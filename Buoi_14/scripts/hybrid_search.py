import os
import sys
import argparse
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.hybrid_retriever import HybridRetriever

def run_hybrid_search(query=None, candidate_k=20, top_k=5):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    corpus_path = os.path.join(base_dir, "data", "processed", "chunks_normalized.csv")
    
    if not os.path.exists(corpus_path):
        raise FileNotFoundError(f"Corpus not found at {corpus_path}. Run prepare_corpus.py first.")

    df = pd.read_csv(corpus_path)
    hybrid = HybridRetriever(df)

    test_queries = [
        ("EXACT_KEYWORD", "Quy định 73/2016/NĐ-CP Điều 115 về hiệu lực thi hành"),
        ("SEMANTIC", "Ai có thẩm quyền phê duyệt hạn mức tín dụng và cấp tiền mặt?"),
        ("MIXED", "Theo Thông tư 01/2014/TT-NHNN việc vận chuyển tài sản quý được quy định như thế nào?")
    ]
    
    queries_to_run = [("USER_QUERY", query)] if query else test_queries

    report_path = os.path.join(base_dir, "outputs", "retrieval_examples.md")
    
    # Read existing report if available
    existing_content = ""
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            existing_content = f.read()
            
    new_lines = []
    
    for q_type, q_text in queries_to_run:
        print(f"\n==========================================")
        print(f"HYBRID SEARCH [{q_type}]: '{q_text}'")
        print(f"==========================================")
        
        results = hybrid.search(q_text, candidate_k=candidate_k, top_k=top_k)
        
        print("\nHYBRID RESULTS:")
        print(f"{'Rank':<5} | {'Chunk ID':<15} | {'BM25 Rank':<10} | {'Dense Rank':<10} | {'RRF Score':<10} | Citation")
        print("-" * 90)
        for r in results:
            bm25_r = str(r['bm25_rank']) if r['bm25_rank'] is not None else "N/A"
            dense_r = str(r['dense_rank']) if r['dense_rank'] is not None else "N/A"
            print(f"{r['rank']:<5} | {r['chunk_id']:<15} | {bm25_r:<10} | {dense_r:<10} | {r['rrf_score']:<10.5f} | {r['citation']}")

        new_lines.append(f"### 3. Hybrid Search (RRF) - Query: `{q_text}`")
        new_lines.append("| Rank | Chunk ID | BM25 Rank | Dense Rank | RRF Score | Citation | Excerpt |")
        new_lines.append("|---|---|---|---|---|---|---|")
        for r in results:
            bm25_r = str(r['bm25_rank']) if r['bm25_rank'] is not None else "N/A"
            dense_r = str(r['dense_rank']) if r['dense_rank'] is not None else "N/A"
            excerpt = r['text'][:100].replace('\n', ' ') + "..."
            new_lines.append(f"| {r['rank']} | `{r['chunk_id']}` | {bm25_r} | {dense_r} | {r['rrf_score']} | {r['citation']} | {excerpt} |")
        new_lines.append("\n---\n")

    if new_lines:
        with open(report_path, "a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(new_lines))
        print(f"\nAppended Hybrid Search results to {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hybrid Search with RRF")
    parser.add_argument("--query", type=str, default=None, help="Search query")
    parser.add_argument("--candidate-k", type=int, default=20, help="Candidate count from each retriever")
    parser.add_argument("--top-k", type=int, default=5, help="Top-k final output")
    args = parser.parse_args()
    
    run_hybrid_search(query=args.query, candidate_k=args.candidate_k, top_k=args.top_k)
