import os
import sys
import json
import torch
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import validate_roles
from src.bm25_retriever import BM25Retriever, custom_tokenizer
from src.dense_retriever import DenseRetriever
from src.hybrid_retriever import HybridRetriever
from src.reranker import NeuralReranker
from src.citation import format_citation

class SecureRetriever:
    def __init__(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        env_corpus = os.getenv("SOURCE_SECURE_CSV", "")
        if env_corpus and os.path.exists(env_corpus):
            corpus_path = env_corpus
        else:
            corpus_path = os.path.join(base_dir, "data", "processed", "chunks_secure.csv")
            if not os.path.exists(corpus_path):
                corpus_path = os.path.join(base_dir, "data", "processed", "chunks_normalized.csv")

        self.full_df = pd.read_csv(corpus_path)

        
        # Ensure allowed_roles column exists as parsed Python lists
        if 'allowed_roles' not in self.full_df.columns:
            self.full_df['allowed_roles'] = [["Admin", "Risk_Manager", "HR", "Staff", "Guest"]] * len(self.full_df)
        else:
            self.full_df['allowed_roles'] = self.full_df['allowed_roles'].apply(
                lambda x: json.loads(x) if isinstance(x, str) else (x if isinstance(x, list) else [])
            )

        print("[SecureRetriever] Pre-building indices for fast secure search...")
        self.bm25 = BM25Retriever(self.full_df)
        self.dense = DenseRetriever(self.full_df)
        self._reranker = None  # Lazy loading

        # Load Neo4j credentials from .env
        env_path = os.path.join(base_dir, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)

        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        self.neo4j_db = os.getenv("NEO4J_DATABASE", "neo4j")

    @property
    def reranker(self):
        if self._reranker is None:
            print("[SecureRetriever] Loading Neural Reranker...")
            self._reranker = NeuralReranker()
        return self._reranker

    def _get_access_mask(self, user_roles):
        validated_roles = validate_roles(user_roles)
        mask = [
            any(role in row_roles for role in validated_roles)
            for row_roles in self.full_df['allowed_roles']
        ]
        accessible_indices = set(i for i, allowed in enumerate(mask) if allowed)
        accessible_cids = set(str(self.full_df.iloc[i]['chunk_id']) for i in accessible_indices)
        filtered_out_count = len(self.full_df) - len(accessible_indices)
        return accessible_indices, accessible_cids, validated_roles, filtered_out_count

    def get_graph_hints(self, doc_ids, chunk_ids, user_roles):
        """Secure Graph Retrieval: filters nodes and edges based on user_roles in Cypher."""
        validated_roles = validate_roles(user_roles)
        hints = {
            "document_ids": list(set(doc_ids)),
            "chunk_ids": list(set(chunk_ids)),
            "relations": [],
            "status": "OFFLINE",
            "user_roles": validated_roles
        }
        try:
            driver = GraphDatabase.driver(self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password))
            driver.verify_connectivity()
            with driver.session(database=self.neo4j_db) as session:
                cypher = """
                MATCH (v1:VanBan)-[r]->(v2:VanBan)
                WHERE (v1.id IN $doc_ids OR v1.so_ky_hieu IN $doc_ids)
                  AND type(r) <> 'CONTAINS'
                  AND (v1.allowed_roles IS NULL OR any(role IN v1.allowed_roles WHERE role IN $user_roles))
                  AND (v2.allowed_roles IS NULL OR any(role IN v2.allowed_roles WHERE role IN $user_roles))
                RETURN v1.so_ky_hieu AS src, type(r) AS rel, v2.so_ky_hieu AS tgt
                LIMIT 10
                """
                res = session.run(cypher, doc_ids=doc_ids, user_roles=validated_roles)
                for rec in res:
                    hints["relations"].append(f"{rec['src']} --[{rec['rel']}]--> {rec['tgt']}")
            driver.close()
            hints["status"] = "CONNECTED"
        except Exception as e:
            hints["status"] = f"UNAVAILABLE ({e})"
        return hints

    def search_bm25(self, query, accessible_indices, top_k=5):
        tokenized_query = custom_tokenizer(query)
        scores = self.bm25.bm25.get_scores(tokenized_query)
        
        valid_pairs = [(i, float(scores[i])) for i in accessible_indices]
        valid_pairs.sort(key=lambda x: x[1], reverse=True)
        ranked_pairs = valid_pairs[:top_k]

        results = []
        for rank, (idx, score) in enumerate(ranked_pairs, start=1):
            row = self.full_df.iloc[idx]
            results.append({
                "rank": rank,
                "chunk_id": str(row['chunk_id']),
                "document_id": str(row['document_id']),
                "text": str(row['text']),
                "retrieval_score": round(score, 4),
                "retrieval_method": "BM25 (Secure)",
                "allowed_roles": row['allowed_roles'],
                "citation": format_citation(row)
            })
        return results

    def search_dense(self, query, accessible_indices, top_k=5):
        query_embedding = self.dense.model.encode(query, convert_to_tensor=True)
        cos_scores = torch.nn.functional.cosine_similarity(query_embedding, self.dense.embeddings, dim=1)

        mask_tensor = torch.zeros(len(self.full_df), dtype=torch.bool, device=cos_scores.device)
        mask_tensor[list(accessible_indices)] = True
        cos_scores[~mask_tensor] = -1e9

        top_results = torch.topk(cos_scores, k=min(top_k, len(accessible_indices)))

        results = []
        for rank, (score, idx) in enumerate(zip(top_results.values, top_results.indices), start=1):
            idx_item = idx.item()
            row = self.full_df.iloc[idx_item]
            results.append({
                "rank": rank,
                "chunk_id": str(row['chunk_id']),
                "document_id": str(row['document_id']),
                "text": str(row['text']),
                "retrieval_score": round(float(score.item()), 4),
                "retrieval_method": "Dense (Secure)",
                "allowed_roles": row['allowed_roles'],
                "citation": format_citation(row)
            })
        return results

    def search_hybrid(self, query, accessible_indices, candidate_k=20, top_k=5, rrf_k=60):
        bm25_res = self.search_bm25(query, accessible_indices, top_k=candidate_k)
        dense_res = self.search_dense(query, accessible_indices, top_k=candidate_k)

        rrf_scores = {}
        bm25_ranks = {}
        dense_ranks = {}

        for item in bm25_res:
            cid = item['chunk_id']
            rank = item['rank']
            bm25_ranks[cid] = rank
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))

        for item in dense_res:
            cid = item['chunk_id']
            rank = item['rank']
            dense_ranks[cid] = rank
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))

        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)[:top_k]

        chunk_map = {str(row['chunk_id']): row for _, row in self.full_df.iterrows()}

        results = []
        for rank, cid in enumerate(sorted_cids, start=1):
            row = chunk_map[cid]
            results.append({
                "final_rank": rank,
                "rank": rank,
                "chunk_id": cid,
                "document_id": str(row['document_id']),
                "bm25_rank": bm25_ranks.get(cid, None),
                "dense_rank": dense_ranks.get(cid, None),
                "rrf_score": round(rrf_scores[cid], 5),
                "retrieval_score": round(rrf_scores[cid], 5),
                "text": str(row['text']),
                "allowed_roles": row['allowed_roles'],
                "retrieval_method": "Hybrid (RRF) (Secure)",
                "citation": format_citation(row)
            })

        return results

    def retrieve(self, question, user_roles, method="hybrid_rerank", top_k=5, candidate_k=20):
        method = method.lower().strip()
        accessible_indices, accessible_cids, validated_roles, filtered_out_count = self._get_access_mask(user_roles)

        if not accessible_indices:
            return {
                "results": [],
                "user_roles": validated_roles,
                "total_chunks_in_corpus": len(self.full_df),
                "accessible_chunks_count": 0,
                "filtered_out_count": filtered_out_count
            }

        if method == "bm25":
            results = self.search_bm25(question, accessible_indices, top_k=top_k)
            for r in results:
                r['score'] = r['retrieval_score']

        elif method == "dense":
            results = self.search_dense(question, accessible_indices, top_k=top_k)
            for r in results:
                r['score'] = r['retrieval_score']

        elif method == "hybrid":
            results = self.search_hybrid(question, accessible_indices, candidate_k=candidate_k, top_k=top_k)
            for r in results:
                r['score'] = r['rrf_score']

        elif method in ["hybrid_rerank", "hybrid+rerank"]:
            candidates = self.search_hybrid(question, accessible_indices, candidate_k=candidate_k, top_k=candidate_k)
            # Cross-Encoder Reranking ONLY on accessible candidates
            raw_results = self.reranker.rerank(question, candidates, top_k=top_k)
            results = [{
                "rank": r['final_rank'],
                "chunk_id": r['chunk_id'],
                "document_id": r['document_id'],
                "hybrid_rank": r.get('hybrid_rank'),
                "hybrid_score": r.get('hybrid_score'),
                "rerank_score": r.get('rerank_score'),
                "text": r['text'],
                "score": r.get('rerank_score', r.get('hybrid_score')),
                "citation": r['citation'],
                "retrieval_method": r['retrieval_method'],
                "allowed_roles": r['allowed_roles']
            } for r in raw_results]
        else:
            raise ValueError(f"Unknown retrieval method: {method}")

        return {
            "results": results,
            "user_roles": validated_roles,
            "total_chunks_in_corpus": len(self.full_df),
            "accessible_chunks_count": len(accessible_indices),
            "filtered_out_count": filtered_out_count
        }
