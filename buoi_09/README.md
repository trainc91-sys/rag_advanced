# Buổi 09 — Parent-aware Multi-query RAG

## Mục tiêu Buổi 09

Buổi 09 đóng gói một pipeline retrieval có 4 mode so sánh:

- `single_flat`: chỉ dùng truy vấn gốc và trả về child chunks.
- `multi_flat`: sinh nhiều query, lấy child chunks qua hybrid retrieval, rồi hợp nhất bằng multi-query fusion.
- `single_parent`: lấy child từ query gốc, sau đó mở rộng lên parent và rerank parent.
- `multi_parent`: kết hợp multi-query child retrieval với parent expansion và rerank.

Nội dung Buổi 09 tập trung vào:

- Multi-query generation để khai thác các khía cạnh pháp lý khác nhau của câu hỏi.
- Hợp nhất child hits qua Reciprocal Rank Fusion (RRF).
- Mở rộng parent từ child hits và đảm bảo mỗi child chỉ nằm trong một parent.
- Đánh giá quyền truy xuất ở cả cấp child và cấp parent.
- Giữ offline test pass, không phụ thuộc vào khai thác dịch vụ Gemini trong unit test.

## Buổi 09 khác Buổi 08 như thế nào

Buổi 08 hướng vào retrieval phẳng, trọng tâm là lấy child chunk trực tiếp.
Buổi 09 mở rộng bằng cách:

- Sinh nhiều truy vấn phụ cho cùng một câu hỏi gốc.
- So sánh bốn mode chạy được song song trong chế độ so sánh.
- Chuyển từ chỉ child retrieval sang parent-aware retrieval.
- Bổ sung parent expansion và reranking thay vì chỉ dùng child hits.
- Kiểm tra chỉ số parent recall, parent MRR và parent nDCG bên cạnh child metrics.

## Cấu trúc Buổi 09

- `rag.py` — CLI scaffold.
- `advanced_rag.py` — snapshot chức năng Buổi 08, giữ lại baseline để so sánh.
- `hierarchical_rag.py` — logic Buổi 09: query generation, parent/child hierarchy,
  và compare mode.
- `evaluate.py` — offline evaluator cho các mode Buổi 09.
- `app.py` — Streamlit dashboard cho từng mode và bảng so sánh.
- `SPEC_buoi_09.md` — đặc tả kỹ thuật.
- `eval/questions.json` — bộ câu hỏi đánh giá offline.
- `reports/` — output báo cáo evaluation.
- `storage/` — hierarchy store, Chroma, huggingface cache.
- `tests/` — unit test offline, không gọi API thật.

## Offline test và chấp nhận

- Tất cả unit test Buổi 09 phải chạy offline và không gọi mạng.
- `hierarchical_rag.py` phải duy trì invariant: mỗi child chỉ liên kết với một parent.
- `app.py` phải hiển thị rõ 4 mode so sánh, không giấu trạng thái `NOT RUN`.
- `evaluate.py` tạo report JSON với metrics recall@k, MRR@k, nDCG@k, latency,
  context chars, query count, expansion factor.

## Hướng dẫn chạy nhanh

Từ thư mục gốc `RAG`:

```powershell
python -m unittest discover -s rag_advanced/buoi_09/tests -p 'test*.py'
python rag_advanced/buoi_09/evaluate.py --input rag_advanced/buoi_09/eval/questions.json --output rag_advanced/buoi_09/reports/evaluation_report.json --k 3 --strategy hierarchical --model-name buoi_09-offline
```

## Đặc tả mode comparison

App so sánh 4 mode với các trường:

- `mode`
- `status` hoặc `NOT RUN`
- `unit_type` (`child` hoặc `parent`)
- evidence ids
- unique sources
- child hits count
- parent candidates / expanded parent count
- context chars
- expansion factor
- latency_ms
- API/model call counts

## Tài liệu và ghi chú

- `eval/questions.json` chứa câu hỏi đánh giá offline.
- `reports/latest_report.json` luôn trỏ đến báo cáo evaluation mới nhất.
- README này giải thích rõ Buổi 09 là một bước tiến bên trên Buổi 08, không phải bản sao.
