import os
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from src.citation import format_citation

class DenseRetriever:
    def __init__(self, chunks_df, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", cache_dir=None):

        self.df = chunks_df.copy().reset_index(drop=True)
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        
        if cache_dir is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            cache_dir = os.path.join(base_dir, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_path = os.path.join(cache_dir, "embeddings.pt")
        
        self.embeddings = self._get_or_create_embeddings()

    def _get_or_create_embeddings(self):
        if os.path.exists(self.cache_path):
            print(f"[DenseRetriever] Loading cached embeddings from {self.cache_path}")
            try:
                cached_data = torch.load(self.cache_path)
                if isinstance(cached_data, dict) and cached_data.get("count") == len(self.df):
                    return cached_data["embeddings"]
            except Exception as e:
                print(f"[DenseRetriever] Cache invalid ({e}), re-encoding...")
                
        print(f"[DenseRetriever] Encoding {len(self.df)} chunks using {self.model_name}...")
        corpus_texts = [str(t)[:1000] for t in self.df['text'].tolist()]
        embeddings = self.model.encode(corpus_texts, batch_size=64, convert_to_tensor=True, show_progress_bar=True)


        
        torch.save({"embeddings": embeddings, "count": len(self.df)}, self.cache_path)
        print(f"[DenseRetriever] Saved embeddings to {self.cache_path}")
        return embeddings

    def search(self, query, top_k=5):
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, self.embeddings)[0]
        
        top_results = torch.topk(cos_scores, k=min(top_k, len(self.df)))
        
        results = []
        for rank, (score, idx) in enumerate(zip(top_results.values, top_results.indices), start=1):
            idx_item = idx.item()
            row = self.df.iloc[idx_item]
            results.append({
                "rank": rank,
                "chunk_id": str(row['chunk_id']),
                "document_id": str(row['document_id']),
                "text": str(row['text']),
                "retrieval_score": round(float(score.item()), 4),
                "retrieval_method": "Dense",
                "citation": format_citation(row)
            })
        return results
