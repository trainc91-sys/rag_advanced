import os
import sys
import argparse
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.secure_retriever import SecureRetriever

def main():
    parser = argparse.ArgumentParser(description="Secure Retrieval Pipeline CLI Demo (Buổi 15 RBAC)")
    parser.add_argument("--query", type=str, required=True, help="Search question")
    parser.add_argument("--roles", type=str, nargs="+", default=["Guest"], help="User active roles (e.g. --roles Guest or --roles HR Admin)")
    parser.add_argument("--method", type=str, default="hybrid_rerank", choices=["bm25", "dense", "hybrid", "hybrid_rerank"], help="Retrieval method")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to retrieve")
    args = parser.parse_args()

    print("\n--------------------------------------------------------")
    print(f"SECURE SEARCH DEMO — BUỔI 15 RBAC")
    print(f"Query: '{args.query}'")
    print(f"User Impersonated Roles: {args.roles}")
    print(f"Method: {args.method.upper()} | Top-k: {args.top_k}")
    print("--------------------------------------------------------")

    retriever = SecureRetriever()
    response = retriever.retrieve(args.query, user_roles=args.roles, method=args.method, top_k=args.top_k)

    results = response['results']
    print(f"\n📊 CORPUS ACCESS STATS:")
    print(f"  - Total Corpus Chunks: {response['total_chunks_in_corpus']}")
    print(f"  - Accessible Chunks for {response['user_roles']}: {response['accessible_chunks_count']}")
    print(f"  - Security Filtered Out Chunks: {response['filtered_out_count']}")

    print(f"\n📌 RETRIEVED TOP-{len(results)} RESULTS:")
    doc_ids = [r['document_id'] for r in results]
    chunk_ids = [r['chunk_id'] for r in results]

    for r in results:
        print(f"\n[Rank #{r['rank']}] Score: {r['score']} | Chunk: {r['chunk_id']} | Doc: {r['document_id']}")
        print(f"  Citation: {r['citation']}")
        print(f"  Allowed Roles on Document: {r['allowed_roles']}")
        print(f"  Text snippet: {r['text'][:140].replace('\n', ' ')}...")

    # Graph hints validation
    hints = retriever.get_graph_hints(doc_ids, chunk_ids, user_roles=args.roles)
    print(f"\n🕸️ SECURE GRAPH HINTS (Neo4j Status: {hints['status']})")
    print(f"  - Accessible Documents: {hints['document_ids']}")
    print(f"  - Direct Graph Relations Filtered by Roles:")
    if hints['relations']:
        for rel in hints['relations']:
            print(f"    • {rel}")
    else:
        print("    • None found or restricted by user roles.")
    print("--------------------------------------------------------\n")

if __name__ == "__main__":
    main()
