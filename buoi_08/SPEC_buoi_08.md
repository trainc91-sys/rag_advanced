# SPEC Buổi 08 — Advanced RAG

## Tổng quan

Mục tiêu: xây dựng một giải pháp Retrieval-Augmented Generation (RAG) hybrid cho dữ liệu pháp lý, kết hợp lexical BM25, Gemini semantic retrieval, Reciprocal Rank Fusion và cross-encoder reranking.

## Yêu cầu chính

1. BM25 lexical retrieval cho phép tìm kiếm:
   - thuật ngữ chính xác
   - số Điều/Khoản
   - tên văn bản pháp lý

2. Semantic retrieval giữ nguyên từ Buổi 07:
   - Gemini embedding cho query và document
   - persistent ChromaDB collection theo strategy
   - semantic retrieval trả về distance hoặc score tương đương

3. Hợp nhất candidate bằng RRF:
   - không gộp trực tiếp score không đồng nhất
   - dùng rank-based fusion

4. Cross-encoder reranker:
   - sử dụng reranker multilingual offline
   - xếp lại candidate theo cặp query–document
   - không tải model khi import module hoặc chạy status/test đơn giản

5. So sánh retrieval mode:
   - `bm25`
   - `semantic`
   - `hybrid`
   - `hybrid_rerank`

6. Hiển thị rõ:
   - top-k trước và sau rerank
   - score từng tầng
   - latency từng tầng
   - rank movement từ lexical/semantic đến rerank

7. Đánh giá retrieval:
   - Recall@K
   - MRR@K
   - nDCG@K

## Kiến trúc module

- `rag.py`
  - config và loader
  - BM25 index builder
  - semantic candidate search
  - RRF fusion
  - reranker wrapper
  - answer builder
  - status / query / index CLI

- `app.py`
  - Streamlit dashboard so sánh mode
  - input câu hỏi và top-k
  - summary latency / metric
  - bảng evidence và trace

- `tests/`
  - kiểm thử offline
  - mock Gemini embedding và generation
  - mock cross-encoder reranker
  - valid schema, query mode, fusion, evaluation metrics

## Dữ liệu

- Sử dụng dữ liệu Buổi 05 ở `rag_foundation/buoi_05/output/chunks/` khi cần.
- Test offline chỉ dùng fixtures và dummy data trong `rag_foundation/buoi_08/tests/fixtures/`.
- Không viết/đọc storage Buổi 05–07.

## Acceptance criteria

- `rag.py` import không lỗi.
- `app.py` import không lỗi.
- `requirements.txt` liệt kê package Buổi 08.
- `python -m unittest discover -s tests -v` chạy được trong `rag_foundation/buoi_08/`.
- Model reranker chỉ được tải trong hàm gọi rõ ràng, không trong import module.
- Project dùng đúng workspace isolation rules.
