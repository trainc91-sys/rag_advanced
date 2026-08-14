# Báo cáo Đánh giá Kết quả Dự đoán Mối quan hệ Pháp lý bằng LLM

**Số lượng quan hệ dự đoán**: 4
**Số lượng quan hệ chuẩn**: 8

## Chỉ số Đánh giá (Evaluation Metrics)

| Chỉ số | Giá trị | Phần trăm |
|---|---|---|
| **Precision** | 0.5000 | 50.00% |
| **Recall** | 0.2500 | 25.00% |
| **F1-Score** | 0.3333 | 33.33% |

## Chi tiết Kết quả Đối sánh

### ✅ True Positives (Khớp chính xác)
- `doc_id`: 168220 -> `other_doc_id`: 166269 [CAN_CU]
- `doc_id`: 169221 -> `other_doc_id`: 44209 [SUA_DOI_BO_SUNG]

### ❌ False Positives (Dự đoán dư thừa / sai)
- `doc_id`: 164719 -> `other_doc_id`: 117310 [SUA_DOI_BO_SUNG]
- `doc_id`: f69936f0-6937-11f1-a48d-29bc6b0fd706 -> `other_doc_id`: 146468 [HOP_NHAT]

### ⚠️ False Negatives (Bỏ sót)
- `doc_id`: 6e689cd0-6f81-11f1-94d6-fd5d6d5ff793 -> `other_doc_id`: 173695 [HOP_NHAT]
- `doc_id`: 117310 -> `other_doc_id`: 25692 [CAN_CU]
- `doc_id`: 174218 -> `other_doc_id`: 25692 [CAN_CU]
- `doc_id`: 112924 -> `other_doc_id`: 95652 [CAN_CU]
- `doc_id`: 163441 -> `other_doc_id`: 112025 [THAY_THE]
- `doc_id`: 177271 -> `other_doc_id`: 185630 [VAN_BAN_BO_SUNG]