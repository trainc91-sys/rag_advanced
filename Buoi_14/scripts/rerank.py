import os
import sys
import argparse
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.hybrid_retriever import HybridRetriever
from src.reranker import NeuralReranker

def run_rerank(query=None, candidate_k=20, top_k=5):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    corpus_path = os.path.join(base_dir, "data", "processed", "chunks_normalized.csv")
    
    if not os.path.exists(corpus_path):
        raise FileNotFoundError(f"Corpus not found at {corpus_path}. Run prepare_corpus.py first.")

    df = pd.read_csv(corpus_path)
    hybrid = HybridRetriever(df)
    reranker = NeuralReranker()

    test_queries = [
        ("EXACT_KEYWORD", "Quy định 73/2016/NĐ-CP Điều 115 về hiệu lực thi hành"),
        ("SEMANTIC", "Ai có thẩm quyền phê duyệt hạn mức tín dụng và cấp tiền mặt?"),
        ("MIXED", "Theo Thông tư 01/2014/TT-NHNN việc vận chuyển tài sản quý được quy định như thế nào?")
    ]
    
    queries_to_run = [("USER_QUERY", query)] if query else test_queries

    report_path = os.path.join(base_dir, "outputs", "retrieval_examples.md")
    new_lines = []

    for q_type, q_text in queries_to_run:
        print(f"\n==========================================")
        print(f"RERANKING [{q_type}]: '{q_text}'")
        print(f"==========================================")
        
        candidates = hybrid.search(q_text, candidate_k=candidate_k, top_k=candidate_k)
        reranked_results = reranker.rerank(q_text, candidates, top_k=top_k)

        print("\n--- BEFORE RERANK (Hybrid Top-5 Candidates) ---")
        print(f"{'Hybrid Rank':<12} | {'Chunk ID':<15} | {'RRF Score':<10} | Citation")
        print("-" * 75)
        for c in candidates[:top_k]:
            print(f"{c['rank']:<12} | {c['chunk_id']:<15} | {c['rrf_score']:<10.5f} | {c['citation']}")

        print("\n--- AFTER RERANK (Neural Rerank Top-5) ---")
        print(f"{'Final Rank':<10} | {'Hybrid Rank':<12} | {'Chunk ID':<15} | {'Rerank Score':<12} | Citation")
        print("-" * 85)
        for r in reranked_results:
            print(f"{r['final_rank']:<10} | {r['hybrid_rank']:<12} | {r['chunk_id']:<15} | {r['rerank_score']:<12.4f} | {r['citation']}")

        new_lines.append(f"### 4. Hybrid + Neural Reranking - Query: `{q_text}`")
        new_lines.append("\n**BEFORE RERANK vs AFTER RERANK Comparison:**")
        new_lines.append("| Final Rank | Original Hybrid Rank | Chunk ID | Hybrid RRF Score | Rerank Score | Citation | Excerpt |")
        new_lines.append("|---|---|---|---|---|---|---|")
        for r in reranked_results:
            excerpt = r['text'][:100].replace('\n', ' ') + "..."
            new_lines.append(f"| {r['final_rank']} | {r['hybrid_rank']} | `{r['chunk_id']}` | {r['hybrid_score']} | {r['rerank_score']} | {r['citation']} | {excerpt} |")
        new_lines.append("\n---\n")

    if new_lines:
        with open(report_path, "a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(new_lines))
        print(f"\nAppended Reranking results to {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Neural Reranking after Hybrid Search")
    parser.add_argument("--query", type=str, default=None, help="Search query")
    parser.add_argument("--candidate-k", type=int, default=20, help="Candidate count from Hybrid Search")
    parser.add_argument("--top-k", type=int, default=5, help="Top-k items to return after reranking")
    args = parser.parse_args()
    
    run_rerank(query=args.query, candidate_k=args.candidate_k, top_k=args.top_k)
