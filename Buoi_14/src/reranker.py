import os
import pandas as pd
from sentence_transformers import CrossEncoder
from src.citation import format_citation

class NeuralReranker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.use_fallback = False
        try:
            print(f"[NeuralReranker] Loading CrossEncoder model: {model_name}...")
            self.model = CrossEncoder(model_name)
            print(f"[NeuralReranker] Model {model_name} loaded successfully.")
        except Exception as e:
            print(f"[NeuralReranker] WARNING: Failed to load {model_name} ({e}). Using FALLBACK reranker.")
            self.model = None
            self.use_fallback = True

    def rerank(self, query, candidates, top_k=5):
        """
        Rerank top-N candidates from Hybrid search.
        candidates: List of dicts returned by HybridRetriever
        """
        if not candidates:
            return []

        if self.use_fallback or self.model is None:
            # Fallback: keep existing hybrid ranking
            results = []
            for rank, item in enumerate(candidates[:top_k], start=1):
                item_copy = dict(item)
                item_copy['final_rank'] = rank
                item_copy['rank'] = rank
                item_copy['hybrid_rank'] = item.get('rank', rank)
                item_copy['hybrid_score'] = item.get('rrf_score', 0.0)
                item_copy['rerank_score'] = item.get('rrf_score', 0.0)
                item_copy['retrieval_method'] = "Hybrid + Rerank (FALLBACK)"
                results.append(item_copy)
            return results

        # Construct (query, text) pairs for CrossEncoder
        pairs = [[query, str(c['text'])[:1000]] for c in candidates]
        scores = self.model.predict(pairs)

        # Pair candidates with cross-encoder scores
        scored_candidates = []
        for idx, (cand, score) in enumerate(zip(candidates, scores)):
            cand_copy = dict(cand)
            cand_copy['hybrid_rank'] = cand.get('rank', idx + 1)
            cand_copy['hybrid_score'] = cand.get('rrf_score', 0.0)
            cand_copy['rerank_score'] = round(float(score), 4)
            scored_candidates.append(cand_copy)

        # Sort descending by rerank_score
        sorted_candidates = sorted(scored_candidates, key=lambda x: x['rerank_score'], reverse=True)[:top_k]

        results = []
        for rank, item in enumerate(sorted_candidates, start=1):
            item['final_rank'] = rank
            item['rank'] = rank
            item['retrieval_method'] = f"Hybrid + NeuralRerank ({self.model_name})"
            results.append(item)

        return results
