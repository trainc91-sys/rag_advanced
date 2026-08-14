import os
import sys
import argparse
import pandas as pd
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.bm25_retriever import BM25Retriever
from src.dense_retriever import DenseRetriever
from src.hybrid_retriever import HybridRetriever
from src.reranker import NeuralReranker

class UnifiedRetrievalPipeline:
    def __init__(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        corpus_path = os.path.join(base_dir, "data", "processed", "chunks_normalized.csv")
        
        if not os.path.exists(corpus_path):
            raise FileNotFoundError(f"Normalized corpus missing at {corpus_path}. Run prepare_corpus.py.")
            
        self.chunks_df = pd.read_csv(corpus_path)
        self.bm25 = BM25Retriever(self.chunks_df)
        self.dense = DenseRetriever(self.chunks_df)
        self.hybrid = HybridRetriever(self.chunks_df, bm25_retriever=self.bm25, dense_retriever=self.dense)
        self.reranker = NeuralReranker()
        
        # Load Neo4j helper if credentials exist
        env_path = os.path.join(base_dir, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        self.neo4j_db = os.getenv("NEO4J_DATABASE", "neo4j")

    def get_graph_hints(self, doc_ids, chunk_ids):
        hints = {"document_ids": list(set(doc_ids)), "chunk_ids": list(set(chunk_ids)), "relations": [], "status": "OFFLINE"}
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password))
            driver.verify_connectivity()
            with driver.session(database=self.neo4j_db) as session:
                cypher = """
                MATCH (v1:VanBan {lab_session: "buoi_14"})-[r]->(v2:VanBan {lab_session: "buoi_14"})
                WHERE (v1.id IN $doc_ids OR v1.so_ky_hieu IN $doc_ids)
                  AND type(r) <> 'CONTAINS'
                RETURN v1.so_ky_hieu AS src, type(r) AS rel, v2.so_ky_hieu AS tgt
                LIMIT 10
                """
                res = session.run(cypher, doc_ids=doc_ids)
                for rec in res:
                    hints["relations"].append(f"{rec['src']} --[{rec['rel']}]--> {rec['tgt']}")
            driver.close()
            hints["status"] = "CONNECTED"
        except Exception as e:
            hints["status"] = f"UNAVAILABLE ({e})"
        return hints

    def retrieve(self, question, method="hybrid_rerank", top_k=5):
        method = method.lower().strip()
        if method == "bm25":
            raw_results = self.bm25.search(question, top_k=top_k)
            results = [{
                "rank": r['rank'],
                "chunk_id": r['chunk_id'],
                "document_id": r['document_id'],
                "text": r['text'],
                "score": r['retrieval_score'],
                "citation": r['citation'],
                "retrieval_method": "BM25"
            } for r in raw_results]

        elif method == "dense":
            raw_results = self.dense.search(question, top_k=top_k)
            results = [{
                "rank": r['rank'],
                "chunk_id": r['chunk_id'],
                "document_id": r['document_id'],
                "text": r['text'],
                "score": r['retrieval_score'],
                "citation": r['citation'],
                "retrieval_method": "Dense"
            } for r in raw_results]

        elif method == "hybrid":
            raw_results = self.hybrid.search(question, candidate_k=20, top_k=top_k)
            results = [{
                "rank": r['rank'],
                "chunk_id": r['chunk_id'],
                "document_id": r['document_id'],
                "bm25_rank": r.get('bm25_rank'),
                "dense_rank": r.get('dense_rank'),
                "text": r['text'],
                "score": r['rrf_score'],
                "citation": r['citation'],
                "retrieval_method": "Hybrid (RRF)"
            } for r in raw_results]

        elif method in ["hybrid_rerank", "hybrid+rerank"]:
            candidates = self.hybrid.search(question, candidate_k=20, top_k=20)
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
                "retrieval_method": r['retrieval_method']
            } for r in raw_results]
        else:
            raise ValueError(f"Unknown retrieval method: {method}. Choose from: bm25, dense, hybrid, hybrid_rerank")

        return results

def main():
    parser = argparse.ArgumentParser(description="Unified Retrieval Query Demo (Buổi 14)")
    parser.add_argument("--query", type=str, required=True, help="Search question")
    parser.add_argument("--method", type=str, default="hybrid_rerank", choices=["bm25", "dense", "hybrid", "hybrid_rerank"], help="Retrieval method")
    parser.add_argument("--top-k", type=int, default=5, help="Number of items to retrieve")
    args = parser.parse_args()

    pipeline = UnifiedRetrievalPipeline()
    results = pipeline.retrieve(args.query, method=args.method, top_k=args.top_k)

    print(f"\n========================================================")
    print(f"QUERY: '{args.query}' | METHOD: {args.method.upper()} | TOP-K: {args.top_k}")
    print(f"========================================================")

    doc_ids = [r['document_id'] for r in results]
    chunk_ids = [r['chunk_id'] for r in results]

    for r in results:
        print(f"\n[Rank {r['rank']}] Score: {r['score']} | Chunk: {r['chunk_id']} | Doc: {r['document_id']}")
        print(f"Citation: {r['citation']}")
        if "hybrid_rank" in r:
            print(f" (Hybrid Rank: {r['hybrid_rank']} -> Rerank Score: {r['rerank_score']})")
        print(f"Text snippet: {r['text'][:150].replace('\n', ' ')}...")

    # Print Graph Hints
    hints = pipeline.get_graph_hints(doc_ids, chunk_ids)
    print(f"\n--------------------------------------------------------")
    print(f"GRAPH HINTS (Neo4j Status: {hints['status']})")
    print(f"--------------------------------------------------------")
    print(f"Retrieved Documents: {hints['document_ids']}")
    print(f"Retrieved Chunks: {hints['chunk_ids']}")
    if hints['relations']:
        print("Direct Graph Relationships:")
        for rel in hints['relations']:
            print(f"  - {rel}")
    else:
        print("Direct Graph Relationships: None found for these documents.")
    print("--------------------------------------------------------")

if __name__ == "__main__":
    main()
