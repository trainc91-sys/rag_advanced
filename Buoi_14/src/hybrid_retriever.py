import pandas as pd
from src.bm25_retriever import BM25Retriever
from src.dense_retriever import DenseRetriever
from src.citation import format_citation

class HybridRetriever:
    def __init__(self, chunks_df, bm25_retriever=None, dense_retriever=None):
        self.df = chunks_df.copy().reset_index(drop=True)
        self.bm25 = bm25_retriever if bm25_retriever is not None else BM25Retriever(self.df)
        self.dense = dense_retriever if dense_retriever is not None else DenseRetriever(self.df)
        
        # Build map for fast chunk lookup
        self.chunk_map = {str(row['chunk_id']): row for _, row in self.df.iterrows()}

    def search(self, query, candidate_k=20, top_k=5, rrf_k=60):
        # 1. Retrieve candidates from both systems
        bm25_results = self.bm25.search(query, top_k=candidate_k)
        dense_results = self.dense.search(query, top_k=candidate_k)

        # 2. Combine ranks using Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        bm25_ranks = {}
        dense_ranks = {}

        for item in bm25_results:
            cid = item['chunk_id']
            rank = item['rank']
            bm25_ranks[cid] = rank
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))

        for item in dense_results:
            cid = item['chunk_id']
            rank = item['rank']
            dense_ranks[cid] = rank
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))

        # 3. Sort by RRF score descending
        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)[:top_k]

        results = []
        for rank, cid in enumerate(sorted_cids, start=1):
            row = self.chunk_map[cid]
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
                "retrieval_method": "Hybrid (RRF)",
                "citation": format_citation(row)
            })

        return results
