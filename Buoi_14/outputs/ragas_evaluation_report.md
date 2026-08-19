# BÁO CÁO ĐÁNH GIÁ HIỆU NĂNG HỆ THỐNG RAG (RAG EVALUATION REPORT)
**Thư viện sử dụng**: Ragas Evaluation Framework  
**Mô hình Pipeline (Generator)**: `Qwen/Qwen3.6-35B-A3B:deepinfra` (hoặc Gemini-3.6-Flash)  
**Mô hình Judger (Evaluator)**: `deepseek-ai/DeepSeek-V4-Flash-0731:deepinfra` (hoặc Gemini-3.6-Flash, LLM-as-a-judge)  
**Ngày thực hiện**: 2026-08-19 20:48:39  

---

## 1. TỔNG QUAN ĐIỂM SỐ RAGAS (OVERALL METRICS SUMMARY)

| Chỉ số Đánh giá (Metric) | Điểm Trung Bình | Ngưỡng Kỳ Vọng (Benchmark) | Đánh Giá Trạng Thái |
| :--- | :---: | :---: | :---: |
| **Context Recall (Độ phủ ngữ cảnh)** | **0.8600** | ≥ 0.70 | PASSED |
| **Context Precision (Độ chuẩn xác ngữ cảnh)** | **0.8975** | ≥ 0.70 | PASSED |
| **Faithfulness (Độ trung thực / Không ảo tưởng)** | **0.9100** | ≥ 0.80 | PASSED |
| **Answer Relevancy (Độ phù hợp câu trả lời)** | **0.9000** | ≥ 0.80 | PASSED |
| **RAGAS OVERALL SCORE (Tổng hợp)** | **0.8919** | **≥ 0.75** | **TUYỆT VỜI** |

---

## 2. ĐÁNH GIÁ CHI TIẾT THEO VAI TRÒ VÀ ĐỘ KHÓ

### 2.1. Điểm số theo Loại Nghiệp vụ (Usecase)
| usecase   |   context_precision |   context_recall |   faithfulness |   answer_relevancy |
|:----------|--------------------:|-----------------:|---------------:|-------------------:|
| Common    |            0.9      |         0.846667 |       0.91     |           0.9      |
| HR        |            0.892857 |         0.851429 |       0.905714 |           0.895714 |
| Risk      |            0.9      |         0.88     |       0.914286 |           0.904286 |

### 2.2. Điểm số theo Độ khó Câu hỏi (Difficulty)
| difficulty   |   context_precision |   context_recall |   faithfulness |   answer_relevancy |
|:-------------|--------------------:|-----------------:|---------------:|-------------------:|
| easy         |            0.875    |         0.846667 |       0.91     |           0.885    |
| hard         |            0.921429 |         0.857143 |       0.914286 |           0.891429 |
| medium       |            0.892857 |         0.874286 |       0.905714 |           0.921429 |

---

## 3. PHÂN TÍCH LỖI VÀ CÁC CÂU HỎI ĐIỂM THẤP (< 0.7)

 Không ghi nhận câu hỏi nào có điểm số dưới ngưỡng 0.7. Hệ thống RAG đạt hiệu năng ổn định trên toàn bộ bộ dữ liệu thử nghiệm.


---

## 4. BẢNG NGUYÊN NHÂN VÀ ĐỀ XUẤT GIẢI PHÁP TỐI ƯU KỸ THUẬT

| Triệu chứng (Chỉ số thấp) | Nguyên nhân phổ biến | Giải pháp kỹ thuật đề xuất áp dụng |
| :--- | :--- | :--- |
| **Context Recall thấp** (< 0.7) | - Truy vấn BM25 bỏ lỡ các từ đồng nghĩa.<br>- Dense search gặp vấn đề với từ viết tắt ngành ngân hàng.<br>- Tham số `top_k` quá nhỏ không chứa đủ ngữ cảnh. | - Tăng giá trị `top_k` từ 5 lên 8.<br>- Tích hợp Mở rộng truy vấn bằng LLM (Query Expansion).<br>- Khai thác liên kết đồ thị Neo4j (`NEXT`, `CONTAINS`) để lấy thêm node lân cận. |
| **Context Precision thấp** (< 0.7) | - Chunk nhiễu có điểm tương đồng vector cao và đứng đầu.<br>- Cấu hình Hybrid RRF chưa tối ưu giữa từ khóa và ngữ nghĩa. | - Cấu hình lại trọng số tham số $k$ trong RRF.<br>- Áp dụng mô hình Cross-Encoder Reranker mạnh hơn (`bge-reranker-large`). |
| **Faithfulness thấp** (< 0.8) | - Generator tự ý bổ sung kiến thức ngoại lai (hallucination).<br>- Ngữ cảnh quá dài gây nhiễu LLM. | - Tắt chế độ reasoning của LLM, thắt chặt prompt hệ thống.<br>- Áp dụng kỹ thuật sinh từng bước (Chain of Thought).<br>- Lọc bớt nhiễu bằng Context Compression trước khi gửi sang Generator. |
| **Answer Relevancy thấp** (< 0.8) | - LLM trả lời quá dài dòng hoặc không tập trung vào câu hỏi. | - Điều chỉnh prompt Generator yêu cầu câu trả lời ngắn gọn.<br>- Bổ sung ví dụ mẫu Few-shot trong Prompt. |

---

## 5. KẾT LUẬN VÀ HƯỚNG MỞ RỘNG

1. **Kiến trúc 2 mô hình độc lập (Pipeline vs Judger)** giúp đánh giá hoàn toàn khách quan, loại bỏ hiện tượng *Self-preference bias*.
2. **Quy trình kiểm thử tự động với Ragas** tạo tiền đề cho việc liên tục giám sát (CI/CD Quality Gate) chất lượng hệ thống RAG trước khi release sản phẩm thực tế.
