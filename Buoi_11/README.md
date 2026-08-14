# Bài thực hành 2 — Multihop Graph RAG (Buổi 11)

Hệ thống Graph RAG truy vấn Neo4j (đồ thị `kb-hops` từ Bài thực hành 1), thực hiện
tìm kiếm vector + mở rộng đa bước (multi-hop) qua các quan hệ giữa văn bản luật
(`CAN_CU`, `THAY_THE`, `HOP_NHAT`, `SUA_DOI_BO_SUNG`), rồi sinh câu trả lời bằng
Gemini API (`gemini-flash-latest`).

## Cấu trúc dự án

```
graph_rag_lab11/
├── config.py               # Cấu hình Neo4j, embedding, Gemini (đọc từ .env)
├── embeddings.py            # Nhúng câu hỏi bằng mô hình tiếng Việt (MSMARCO bi-encoder)
├── graph_rag.py              # Bước 1 + 2: kết nối Neo4j, vector search, multi-hop expansion
├── gemini_qa.py               # Bước 3: system prompt + gọi Gemini API
├── ask.py                       # CLI hỏi nhanh 1 câu
├── run_qa_comparison.py          # Bước 4: chạy 5 câu hỏi x (0/1/2 bước nhảy) -> qa_comparison.md
├── requirements.txt
└── .env.example
```

## Cài đặt

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Mở .env và điền:
#   - Thông tin Neo4j (nếu khác mặc định của Bài thực hành 1)
#   - GEMINI_API_KEY (lấy tại https://aistudio.google.com/apikey)
#   - EMBEDDING_MODEL_NAME đúng với checkpoint đã dùng ở Bài thực hành 1
```

> **Lưu ý quan trọng về schema:** file `config.py` giả định:
> - Node đoạn văn bản có label `Chunk`, thuộc tính text `text`, vector `embedding`.
> - Node văn bản luật có label `Document`, thuộc tính tên `title`.
> - Quan hệ `Chunk -[PART_OF]-> Document`.
> - Vector index tên `chunk_embedding_index`.
>
> Nếu schema thực tế ở Bài thực hành 1 của bạn đặt tên khác, hãy sửa các biến tương
> ứng trong `.env` (không cần sửa code) cho khớp.

## Chạy thử nhanh 1 câu hỏi

```bash
python ask.py "Nghị định 46/2023/NĐ-CP thay thế cho nghị định nào?" --hops 1
```

## Chạy kiểm thử & đánh giá đầy đủ (Bước 4)

```bash
python run_qa_comparison.py
```

Script sẽ:
1. Chạy 5 câu hỏi kiểm thử (đã cho trong đề bài) qua pipeline với `hops = 0, 1, 2`.
2. So sánh số đoạn ngữ cảnh lấy được và câu trả lời tương ứng ở mỗi mức hop.
3. Ghi toàn bộ kết quả (bảng so sánh + ngữ cảnh chi tiết + nhận xét) vào
   `qa_comparison.md`.

## Ý tưởng thiết kế chính

- **Vector search (Bước 2)**: dùng `db.index.vector.queryNodes` trên vector index đã
  tạo ở Bài thực hành 1 để tìm các `Chunk` gần nhất với câu hỏi (đã nhúng bằng cùng
  họ mô hình MSMARCO tiếng Việt).
- **Multi-hop expansion (Bước 2)**: từ `Document` chứa các `Chunk` khớp trực tiếp,
  duyệt đồ thị theo các quan hệ pháp lý (`CAN_CU`, `THAY_THE`, `HOP_NHAT`,
  `SUA_DOI_BO_SUNG`) tối đa `hops` bước, lấy thêm các `Chunk` thuộc các `Document`
  liên quan — đúng với các câu hỏi kiểm thử dạng "văn bản X thay thế/căn cứ/hợp nhất
  văn bản nào, và nội dung của văn bản đó là gì?".
- **Prompt hệ thống (Bước 3)**: mô tả rõ schema đồ thị, cấu trúc văn bản luật Việt
  Nam, và yêu cầu Gemini chỉ trả lời dựa trên ngữ cảnh, nêu rõ khi thiếu thông tin
  thay vì suy đoán.
- **Đánh giá (Bước 4)**: so sánh trực tiếp câu trả lời ở `hops = 0` (chỉ có văn bản
  khớp gốc) với `hops = 1, 2` (có thêm văn bản liên quan) để cho thấy hiệu quả của
  ngữ cảnh đa bước — đặc biệt với các câu hỏi cần thông tin từ hai văn bản trở lên.
