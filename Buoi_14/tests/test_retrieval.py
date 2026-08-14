import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.bm25_retriever import BM25Retriever
from src.dense_retriever import DenseRetriever
from src.hybrid_retriever import HybridRetriever

def test_retriever_pipeline():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    corpus_path = os.path.join(base_dir, "data", "processed", "chunks_normalized.csv")
    
    assert os.path.exists(corpus_path), "Normalized corpus missing!"
    df = pd.read_csv(corpus_path)
    assert len(df) > 0, "Corpus is empty!"
    
    # 1. Test BM25
    bm25 = BM25Retriever(df)
    res_bm25 = bm25.search("Quy định 73/2016/NĐ-CP", top_k=3)
    assert len(res_bm25) == 3, "BM25 retrieval count mismatch!"
    assert "retrieval_score" in res_bm25[0], "BM25 missing retrieval_score!"
    
    # 2. Test Dense
    dense = DenseRetriever(df)
    res_dense = dense.search("Phê duyệt khoản vay", top_k=3)
    assert len(res_dense) == 3, "Dense retrieval count mismatch!"
    
    # 3. Test Hybrid
    hybrid = HybridRetriever(df, bm25_retriever=bm25, dense_retriever=dense)
    res_hybrid = hybrid.search("Vận chuyển tài sản quý", candidate_k=10, top_k=3)
    assert len(res_hybrid) == 3, "Hybrid retrieval count mismatch!"
    assert "rrf_score" in res_hybrid[0], "Hybrid missing rrf_score!"

    print("ALL RETRIEVAL UNIT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_retriever_pipeline()
