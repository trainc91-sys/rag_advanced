import re
import pandas as pd
from rank_bm25 import BM25Okapi
from src.citation import format_citation

def custom_tokenizer(text):
    if not isinstance(text, str):
        return []
    # Tokenize preserving legal document codes, slashes, numbers, and words
    text = text.lower()
    # Match document codes like 73/2016/NĐ-CP, numbers, or words
    tokens = re.findall(r'[a-z0-9àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\/\-]+', text)
    return [t for t in tokens if len(t) > 1 or t.isdigit()]

class BM25Retriever:
    def __init__(self, chunks_df):
        self.df = chunks_df.copy().reset_index(drop=True)
        self.corpus = self.df['text'].tolist()
        self.tokenized_corpus = [custom_tokenizer(doc) for doc in self.corpus]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(self, query, top_k=5):
        tokenized_query = custom_tokenizer(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Rank indices by score descending
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for rank, idx in enumerate(ranked_indices, start=1):
            row = self.df.iloc[idx]
            score = float(scores[idx])
            results.append({
                "rank": rank,
                "chunk_id": str(row['chunk_id']),
                "document_id": str(row['document_id']),
                "text": str(row['text']),
                "retrieval_score": round(score, 4),
                "retrieval_method": "BM25",
                "citation": format_citation(row)
            })
        return results
