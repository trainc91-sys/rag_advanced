"""
ask.py
------
Script tiện ích: hỏi nhanh một câu qua hệ thống Multihop Graph RAG từ dòng lệnh.

Cách dùng:
    python ask.py "Câu hỏi của bạn" --hops 1 --top_k 5
"""

import argparse

from graph_rag import MultihopGraphRAG
import gemini_qa


def main():
    parser = argparse.ArgumentParser(description="Hỏi đáp qua Multihop Graph RAG")
    parser.add_argument("question", type=str, help="Câu hỏi cần trả lời")
    parser.add_argument("--hops", type=int, default=1, help="Số bước nhảy multi-hop (0, 1, 2, ...)")
    parser.add_argument("--top_k", type=int, default=5, help="Số đoạn khớp trực tiếp lấy về")
    args = parser.parse_args()

    with MultihopGraphRAG() as rag:
        if not rag.verify_connectivity():
            print("Không thể kết nối Neo4j.")
            return
        retrieval = rag.retrieve_context(args.question, top_k=args.top_k, hops=args.hops)

    print("\n=== NGỮ CẢNH ĐÃ TRUY VẤN ===")
    print(retrieval["context_text"] or "(không có ngữ cảnh)")

    print("\n=== ĐANG GỌI GEMINI ===")
    answer = gemini_qa.answer_question(args.question, retrieval["context_text"])
    print("\n=== CÂU TRẢ LỜI ===")
    print(answer)


if __name__ == "__main__":
    main()
