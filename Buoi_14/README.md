# BUỔI 14 — Nâng cấp RAG với Hybrid Search + Reranking và xây Knowledge Graph mini

Hệ thống RAG nâng cao kết hợp **BM25 Lexical Search**, **Dense Vector Retrieval**, **Reciprocal Rank Fusion (RRF)**, **Neural Cross-Encoder Reranking** và **Neo4j Mini Knowledge Graph**.

---

## 📁 Cấu trúc Thư mục Project

```text
buoi_14/
│
├── data/
│   ├── processed/
│   │   └── chunks_normalized.csv    # Corpus 1472 chunks đã chuẩn hóa
│   └── eval/
│       └── questions.csv            # Bộ câu hỏi benchmark gold evaluation
│
├── src/
│   ├── citation.py                  # Format citation chuẩn
│   ├── bm25_retriever.py            # BM25 Lexical search
│   ├── dense_retriever.py           # Dense vector search & embedding cache
│   ├── hybrid_retriever.py          # Hybrid Fusion (Reciprocal Rank Fusion)
│   └── reranker.py                  # Neural Cross-Encoder Reranker
│
├── scripts/
│   ├── inspect_project.py           # Script pre-check dữ liệu & môi trường
│   ├── prepare_corpus.py            # Chuẩn hóa HTML sang chunks_normalized.csv
│   ├── baseline_retrieval.py        # Benchmark BM25 vs Dense
│   ├── hybrid_search.py             # CLI chạy Hybrid Search (RRF)
│   ├── rerank.py                    # CLI chạy Neural Reranking
│   ├── compare_retrieval.py         # Script đánh giá Hit@k & MRR
│   ├── load_mini_kg.py              # Script nạp Mini Graph vào Neo4j
│   └── query_demo.py                # Unified CLI interface & Graph Hints
│
├── cypher/
│   ├── schema.cypher                # Cypher constraints & indexes
│   └── demo_queries.cypher          # 5 Cypher queries trực quan hóa Neo4j
│
├── outputs/
│   ├── inspection_report.md         # Báo cáo kiểm tra trước khi chạy
│   ├── retrieval_examples.md        # Ví dụ so sánh BM25, Dense, Hybrid, Rerank
│   ├── retrieval_comparison.csv     # Đánh giá chi tiết 10 câu hỏi benchmark
│   ├── evaluation_report.md         # Báo cáo tổng hợp metrics Hit@k & MRR
│   ├── kg_build_report.md           # Báo cáo thống kê nodes/edges Neo4j
│   └── final_validation_report.md   # Báo cáo nghiệm thu sản phẩm Buổi 14
│
├── cache/
│   └── embeddings.pt                # Tensor cache 1472 document embeddings
│
├── app.py                           # Interactive Streamlit Demo App
├── .env                             # Cấu hình Neo4j credentials
├── requirements.txt                 # Các thư viện Python bắt buộc
└── README.md                        # Hướng dẫn chạy và giải thích hệ thống
```

---

## 🚀 Hướng dẫn Chạy Chi tiết

### 1. Chuẩn hóa Corpus
```bash
python scripts/prepare_corpus.py
```
> Trích xuất 1472 chunks từ 30 văn bản trong `content.csv` và `metadata.csv`.

### 2. Chạy Baseline Retrieval (BM25 vs Dense)
```bash
python scripts/baseline_retrieval.py --query "Quy định 73/2016/NĐ-CP Điều 115" --top-k 5
```

### 3. Chạy Hybrid Search (RRF)
```bash
python scripts/hybrid_search.py --query "Ai có thẩm quyền phê duyệt hạn mức tín dụng?" --candidate-k 20 --top-k 5
```

### 4. Chạy Neural Reranking
```bash
python scripts/rerank.py --query "Thông tư 01/2014/TT-NHNN vận chuyển tiền mặt" --candidate-k 20 --top-k 5
```

### 5. Nạp Mini Knowledge Graph vào Neo4j
```bash
python scripts/load_mini_kg.py
```
> Nạp 30 `:VanBan`, 1472 `:DieuKhoan`, 1472 `:CONTAINS`, 1442 `:NEXT`, và 29 quan hệ thực tế (`:THAM_CHIEU`, `:SUA_DOI_BO_SUNG`, `:THAY_THE`, `:CAN_CU`).  
> *Lưu ý: Mọi node/edge được gắn tag `lab_session = "buoi_14"` để không ảnh hưởng dữ liệu các buổi khác.*

### 6. Chạy Đánh giá Benchmark Metrics (Hit@k & MRR)
```bash
python scripts/compare_retrieval.py
```

### 7. Chạy Giao diện Trực quan Streamlit App
```bash
streamlit run app.py
```
> Truy cập giao diện ứng dụng tại URL mà terminal cung cấp (thường là `http://localhost:8501`).

---

## 📈 Kết quả Benchmark Đánh giá (Overall)

| Method | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---|---|---|---|
| **BM25-only** | 40.00% | 60.00% | 60.00% | 0.4833 |
| **Dense-only** | 60.00% | 60.00% | 80.00% | 0.6500 |
| **Hybrid (RRF)** | **60.00%** | **80.00%** | **80.00%** | **0.7000** |
| **Hybrid + Rerank** | **60.00%** | **80.00%** | **80.00%** | **0.7000** |
