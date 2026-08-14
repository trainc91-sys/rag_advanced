# Buổi 08 — Advanced RAG

## Mục tiêu

Buổi 08 mở rộng Buổi 07 theo hướng Advanced RAG cho tài liệu pháp lý:

- BM25 lexical retrieval cho số Điều/Khoản và cụm từ chính xác.
- Semantic retrieval bằng Gemini như Buổi 07.
- Hợp nhất bằng Reciprocal Rank Fusion (RRF).
- Rerank bằng cross-encoder multilingual.
- So sánh các retrieval mode: `bm25`, `semantic`, `hybrid`, `hybrid_rerank`.
- Hiển thị thứ hạng, score, latency và phân tích rank movement.
- Đánh giá bằng Recall@K, MRR@K và nDCG@K.

## Cấu trúc project

- `rag.py` — backend Advanced RAG logic và CLI.
- `app.py` — giao diện Streamlit so sánh retrieval mode.
- `SPEC_buoi_08.md` — đặc tả kỹ thuật và tiêu chí nghiệm thu.
- `requirements.txt` — package Buổi 08.
- `tests/` — unit test offline, không gọi Gemini thật, không tải reranker khi import.
- `tests/fixtures/` — dữ liệu mẫu cho kiểm thử.

## Cài đặt

Sử dụng Python interpreter của Buổi 05:

```powershell
cd d:\RAG
.\rag_foundation\buoi_05\.venv\Scripts\python.exe -m pip install -r rag_foundation\buoi_08\requirements.txt
```

## Chạy test

```powershell
.\rag_foundation\buoi_05\.venv\Scripts\python.exe -m unittest discover -s rag_foundation\buoi_08\tests -v
```

## Chạy ứng dụng Streamlit

```powershell
.\rag_foundation\buoi_05\.venv\Scripts\python.exe -m streamlit run rag_foundation\buoi_08\app.py
```

## Đánh giá và báo cáo

- Chạy đánh giá offline với câu hỏi mẫu trong `eval/questions.json`:

```powershell
.
ag_foundationuoi_05\.venv\Scripts\python.exe rag_foundation\buoi_08\evaluate.py --input rag_foundation\buoi_08\eval\questions.json --output rag_foundation\buoi_08\reports\evaluation_report.json
```

- Kết quả được lưu tại `rag_foundation/buoi_08/reports/evaluation_report.json` và chứa `metrics`, `warnings`, `needs_human_review`, `winner`.
- Mục tiêu Prompt 10 là có thể chạy đánh giá offline, xuất báo cáo JSON và ghi lại trạng thái cần human review khi dữ liệu đánh giá yêu cầu.

## Note

- Chỉ được sửa và ghi trong `rag_foundation/buoi_08/`.
- Không thay đổi Buổi 05–07.
- Không commit `.env`, cache Hugging Face hay storage hiện có của Buổi 05–07.
