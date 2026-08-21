# AI Compliance Gap Checker Evaluation Report — Buổi 17

**Analyzed Requirements**: 3
**Human Review Enforcement**: ALL FINDINGS TAGGED AS `NEEDS_HUMAN_REVIEW`

## Gap Findings Summary

| Gap ID | NHNN Requirement Citation | Agribank Policy Citation | Classification | Confidence | Human Review |
| --- | --- | --- | --- | --- | --- |
| `gap_c71047fd` | [Thông tư 01/2014/TT-NHNN - Điều 3] | N/A | `CHUA_DU_BANG_CHUNG` | 0.5 | `NEEDS_HUMAN_REVIEW` |
| `gap_d39d0338` | [Thông tư 41/2016/TT-NHNN - Điều 4] | Quy định nội bộ số 250/QĐ-NHNO-QLRR về Quản lý tỷ lệ an toàn vốn và định mức rủi ro Agribank | 250/QĐ-NHNO-QLRR | Điều 5. Tỷ lệ an toàn vốn nội bộ tiêu chuẩn | doc_agr_car02_01 | `DAP_UNG` | 0.9 | `NEEDS_HUMAN_REVIEW` |
| `gap_be305f98` | [Thông tư 09/2020/TT-NHNN - Điều 15] | Quy chế bảo mật CNTT số 600/QC-NHNO-CNTT về An toàn thông tin và Quản trị dữ liệu AI Agribank | 600/QC-NHNO-CNTT | Điều 9. Tiêu chuẩn mã hóa dữ liệu ứng dụng AI | doc_agr_it07_01 | `CHENH_LECH` | 0.9 | `NEEDS_HUMAN_REVIEW` |

## Detailed Finding Breakdown

### Finding `gap_c71047fd` — Status: `CHUA_DU_BANG_CHUNG`
- **External Requirement**: Ngân hàng Nhà nước quy định công tác vận chuyển tiền mặt có giá trị lớn phải đảm bảo an toàn tuyệt đối và có phương án bảo vệ chuyên trách bằng xe bọc thép chuyên dùng.
- **External Citation**: `[Thông tư 01/2014/TT-NHNN - Điều 3]`
- **Internal Evidence**: Không tìm thấy điều khoản nội bộ tương ứng trong tập dữ liệu.
- **Internal Citation**: `N/A`
- **AI Reasoning**: Chưa tìm thấy căn cứ điều khoản nội bộ tương ứng trong phạm vi tài liệu được phép truy cập.
- **Confidence Score**: 0.5
- **Guardrail Notice**: `NEEDS_HUMAN_REVIEW` (Requires auditor sign-off)

### Finding `gap_d39d0338` — Status: `DAP_UNG`
- **External Requirement**: Tỷ lệ an toàn vốn tối thiểu (CAR) đối với các tổ chức tín dụng phải đạt tối thiểu 8% theo quy định NHNN.
- **External Citation**: `[Thông tư 41/2016/TT-NHNN - Điều 4]`
- **Internal Evidence**: Tỷ lệ an toàn vốn tối thiểu (CAR) của Agribank được quy định duy trì ở mức tối thiểu 8.5%, cao hơn 0.5% so với quy định chung 8% tại Thông tư 41/2016/TT-NHNN. Bộ phận Quản lý Rủi ro chịu trách nhiệm tính toán CAR theo tháng và quý.
- **Internal Citation**: `Quy định nội bộ số 250/QĐ-NHNO-QLRR về Quản lý tỷ lệ an toàn vốn và định mức rủi ro Agribank | 250/QĐ-NHNO-QLRR | Điều 5. Tỷ lệ an toàn vốn nội bộ tiêu chuẩn | doc_agr_car02_01`
- **AI Reasoning**: Agribank duy trì CAR tối thiểu 8.5%, cao hơn mức tối thiểu 8.0% của NHNN tại Thông tư 41/2016/TT-NHNN.
- **Confidence Score**: 0.9
- **Guardrail Notice**: `NEEDS_HUMAN_REVIEW` (Requires auditor sign-off)

### Finding `gap_be305f98` — Status: `CHENH_LECH`
- **External Requirement**: Tất cả hệ thống CNTT và ứng dụng AI xử lý dữ liệu khách hàng phải lưu trữ nhật ký truy cập (Audit Trail) tối thiểu 24 tháng.
- **External Citation**: `[Thông tư 09/2020/TT-NHNN - Điều 15]`
- **Internal Evidence**: Hệ thống RAG và các ứng dụng AI tra cứu quy định Agribank phải tuân thủ chính sách bảo mật dữ liệu theo cấp độ 3 An toàn thông tin. Tất cả các dữ liệu nhạy cảm lưu trữ phải được mã hóa AES-128/Fernet at-rest.
- **Internal Citation**: `Quy chế bảo mật CNTT số 600/QC-NHNO-CNTT về An toàn thông tin và Quản trị dữ liệu AI Agribank | 600/QC-NHNO-CNTT | Điều 9. Tiêu chuẩn mã hóa dữ liệu ứng dụng AI | doc_agr_it07_01`
- **AI Reasoning**: Quy chế 600/QC-NHNO-CNTT quy định lưu trữ Audit Log 12 tháng, trong khi Thông tư 09/2020/TT-NHNN yêu cầu tối thiểu 24 tháng.
- **Confidence Score**: 0.9
- **Guardrail Notice**: `NEEDS_HUMAN_REVIEW` (Requires auditor sign-off)

---
GAP CHECKER: PASS
HUMAN REVIEW REQUIRED: YES