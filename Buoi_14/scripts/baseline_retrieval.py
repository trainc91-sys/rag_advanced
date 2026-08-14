import os
import sys
import argparse
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.bm25_retriever import BM25Retriever
from src.dense_retriever import DenseRetriever

def run_baseline(query=None, top_k=5):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    corpus_path = os.path.join(base_dir, "data", "processed", "chunks_normalized.csv")
    
    if not os.path.exists(corpus_path):
        raise FileNotFoundError(f"Corpus not found at {corpus_path}. Run prepare_corpus.py first.")

    df = pd.read_csv(corpus_path)
    
    print(f"Loaded {len(df)} chunks from {corpus_path}")
    
    bm25 = BM25Retriever(df)
    dense = DenseRetriever(df)
    
    test_queries = [
        ("EXACT_KEYWORD", "Quy định 73/2016/NĐ-CP Điều 115 về hiệu lực thi hành"),
        ("SEMANTIC", "Ai có thẩm quyền phê duyệt hạn mức tín dụng và cấp tiền mặt?"),
        ("MIXED", "Theo Thông tư 01/2014/TT-NHNN việc vận chuyển tài sản quý được quy định như thế nào?")
    ]
    
    if query:
        queries_to_run = [("USER_QUERY", query)]
    else:
        queries_to_run = test_queries
        
    outputs_dir = os.path.join(base_dir, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    report_path = os.path.join(outputs_dir, "retrieval_examples.md")
    
    markdown_lines = ["# RETRIEVAL EXAMPLES & COMPARISON (BUỔI 14)\n"]
    
    for q_type, q_text in queries_to_run:
        print(f"\n==========================================")
        print(f"QUERY [{q_type}]: '{q_text}'")
        print(f"==========================================")
        
        bm25_res = bm25.search(q_text, top_k=top_k)
        dense_res = dense.search(q_text, top_k=top_k)
        
        print("\n--- BM25 RESULTS ---")
        for r in bm25_res:
            print(f"Rank {r['rank']} | Score: {r['retrieval_score']} | Chunk: {r['chunk_id']} | Citation: {r['citation']}")
            
        print("\n--- DENSE RESULTS ---")
        for r in dense_res:
            print(f"Rank {r['rank']} | Score: {r['retrieval_score']} | Chunk: {r['chunk_id']} | Citation: {r['citation']}")

        # Append to report markdown
        markdown_lines.append(f"## Query Type: `{q_type}`")
        markdown_lines.append(f"**Query:** `{q_text}`\n")
        
        markdown_lines.append("### 1. BM25 Baseline")
        markdown_lines.append("| Rank | Chunk ID | Score | Citation | Excerpt |")
        markdown_lines.append("|---|---|---|---|---|")
        for r in bm25_res:
            excerpt = r['text'][:120].replace('\n', ' ') + "..."
            markdown_lines.append(f"| {r['rank']} | `{r['chunk_id']}` | {r['retrieval_score']} | {r['citation']} | {excerpt} |")
            
        markdown_lines.append("\n### 2. Dense Baseline")
        markdown_lines.append("| Rank | Chunk ID | Score | Citation | Excerpt |")
        markdown_lines.append("|---|---|---|---|---|")
        for r in dense_res:
            excerpt = r['text'][:120].replace('\n', ' ') + "..."
            markdown_lines.append(f"| {r['rank']} | `{r['chunk_id']}` | {r['retrieval_score']} | {r['citation']} | {excerpt} |")
        markdown_lines.append("\n---\n")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_lines))
        
    print(f"\nReport written to {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Baseline Retrieval (BM25 vs Dense)")
    parser.add_argument("--query", type=str, default=None, help="Search query")
    parser.add_argument("--top-k", type=int, default=5, help="Number of top items to retrieve")
    args = parser.parse_args()
    
    run_baseline(query=args.query, top_k=args.top_k)
