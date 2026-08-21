# Buổi 17 — RBAC, Audit Trail và AI Compliance Gap Checker bằng Vibe Coding

## Mục tiêu
Dự án Buổi 17 bổ sung ba năng lực bảo mật và quản trị doanh nghiệp cho hệ thống RAG Agribank:
1. **RBAC (Role-Based Access Control)**: Chỉ truy xuất tài liệu đúng quyền người dùng trước khi đưa vào ngữ cảnh LLM.
2. **Audit Trail**: Nhật ký lưu vết chuẩn JSONL ghi nhận toàn bộ câu hỏi, vai trò, phương thức truy xuất và kết quả.
3. **AI Compliance Gap Checker**: So sánh quy định nội bộ Agribank với Thông tư/Quy định NHNN, đưa ra bằng chứng 2 phía và nhãn phân loại tuân thủ (`DAP_UNG`, `THIEU`, `CHENH_LECH`, `CHUA_DU_BANG_CHUNG`).

## Cấu trúc Thư mục Dự án

```text
Buoi_17/
├── .env                                 # Biến môi trường & cấu hình API Key
├── .gitignore                           # Loại bỏ file nhạy cảm và key
├── README.md                            # Hướng dẫn sử dụng & tài liệu dự án
├── app.py                               # Giao diện Streamlit Demo (3 Tabs)
├── config/
│   └── rbac_policy.json                 # Định nghĩa chính sách phân quyền vai trò
├── scripts/
│   ├── inspect_dependencies.py          # Kiểm tra môi trường & dữ liệu đầu vào
│   ├── rbac.py                          # Module phân quyền RBAC & kiểm tra vai trò
│   ├── secure_retrieval_adapter.py      # Adapter tái sử dụng SecureRetriever Buổi 14
│   ├── audit_logger.py                  # Module ghi nhật ký hệ thống (Audit Logger)
│   ├── encryption_demo.py               # Demo mã hóa dữ liệu tĩnh (At-rest Encryption)
│   ├── internal_lookup.py               # Use Case 1: Tra cứu quy định nội bộ + Citation
│   ├── compliance_gap.py                # Use Case 2: AI Compliance Gap Checker
│   ├── security_tests.py                # Tập lệnh kiểm thử bảo mật & ranh giới dữ liệu
│   └── final_validation.py              # Script kiểm toán toàn bộ sản phẩm đầu ra
└── outputs/
    ├── dependency_report.md
    ├── rbac_reuse_report.md
    ├── secure_retrieval_test.md
    ├── audit_log.jsonl
    ├── encryption_demo_report.md
    ├── internal_lookup_demo.md
    ├── gap_input_catalog.md
    ├── compliance_gap_results.csv
    ├── compliance_gap_report.md
    ├── graph_gap_integration_report.md
    ├── security_test_report.md
    └── final_validation_report.md
```

## Hướng dẫn Chạy ứng dụng & Kiểm thử

### 1. Kiểm tra môi trường & Dữ liệu
```bash
python scripts/inspect_dependencies.py
```

### 2. Chạy kiểm thử Phân quyền RBAC & Secure Retrieval
```bash
python scripts/rbac.py
python scripts/secure_retrieval_adapter.py
```

### 3. Khởi tạo Audit Logger & Demo Mã hóa
```bash
python scripts/audit_logger.py
python scripts/encryption_demo.py
```

### 4. Chạy Use Case 1 (Tra cứu quy định nội bộ) & Use Case 2 (Compliance Gap Checker)
```bash
python scripts/internal_lookup.py
python scripts/compliance_gap.py
```

### 5. Chạy Kiểm thử Bảo mật & Kiểm toán Tổng thể
```bash
python scripts/security_tests.py
python scripts/final_validation.py
```

### 6. Khởi chạy Giao diện Streamlit UI
```bash
streamlit run app.py
```

## Trình tự Demo Bài thực hành
1. **Tra cứu quy định theo Role**: Cùng một câu hỏi tra cứu tỷ lệ an toàn vốn CAR, chọn vai trò `Risk_Manager` (Được phép) và vai trò `Guest` (Bị chặn).
2. **Kiểm tra Audit Log**: Mở Tab **AUDIT TRAIL LOGS** hoặc tệp `outputs/audit_log.jsonl` để kiểm tra vết truy cập.
3. **Phân tích Gap Tuân thủ**: Chuyển sang Tab **COMPLIANCE GAP CHECKER**, chọn yêu cầu NHNN và kiểm tra bằng chứng đối chiếu 2 phía.
4. **Xác minh Human Review**: Kiểm tra nhãn `NEEDS_HUMAN_REVIEW` đảm bảo kết quả AI không thay thế kết luận kiểm toán viên.
