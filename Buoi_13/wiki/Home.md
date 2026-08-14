---
id: HOME-001
type: WikiHome
verification_status: VERIFIED
data_origin: SYNTHETIC
---

# 🛡️ Wiki Risk Graph — Trực Quan Hóa Tri Thức Rủi Ro

Chào mừng bạn đến với **Wiki Risk Graph**, hệ thống tri thức rủi ro dạng đồ thị được xây dựng tự động từ dữ liệu chuẩn hóa.

---

## 📊 Thống Kê Tổng Quan Đồ Thị

- **Tổng số trang Wiki (Nodes):** `35` (Bao gồm Home.md)
  - 🔴 **Hồ sơ Rủi ro (`RuiRo`):** `12`
  - 🟢 **Kiểm soát (`KiemSoat`):** `10`
  - 🟡 **Sự kiện Rủi ro (`SuKienRuiRo`):** `12`
- **Tổng số Liên kết Knowledge Graph (Edges):** `22`
  - 🛡️ `MITIGATES` (KiemSoat -> RuiRo): `10`
  - ⚠️ `OBSERVED_AS` (RuiRo -> SuKienRuiRo): `12`

---

## 🔗 Danh Mục Tri Thức

### 1. 🔴 Danh Sách Hồ Sơ Rủi Ro (`RuiRo`)
- [[RR-001]] — **Giao dịch chuyển tiền bị hạch toán sai** (Mức rủi ro: `Trung binh`)
- [[RR-002]] — **Phê duyệt tín dụng vượt thẩm quyền** (Mức rủi ro: `Trung binh`)
- [[RR-003]] — **Giải ngân thiếu hồ sơ bảo đảm** (Mức rủi ro: `Trung binh`)
- [[RR-004]] — **Lộ thông tin khách hàng** (Mức rủi ro: `Trung binh`)
- [[RR-005]] — **Gián đoạn dịch vụ ngân hàng số** (Mức rủi ro: `Trung binh`)
- [[RR-006]] — **Gian lận giả mạo yêu cầu chuyển tiền** (Mức rủi ro: `Trung binh`)
- [[RR-007]] — **Chậm báo cáo giao dịch đáng ngờ** (Mức rủi ro: `Trung binh`)
- [[RR-008]] — **Định giá tài sản bảo đảm không chính xác** (Mức rủi ro: `Trung binh`)
- [[RR-009]] — **Không phát hiện giao dịch bất thường** (Mức rủi ro: `Trung binh`)
- [[RR-010]] — **Sai lệch số liệu báo cáo quản trị** (Mức rủi ro: `Thap`)
- [[RR-011]] — **Nhà cung cấp công nghệ không đáp ứng cam kết** (Mức rủi ro: `Trung binh`)
- [[RR-012]] — **Xung đột lợi ích trong mua sắm** (Mức rủi ro: `Thap`)

### 2. 🟢 Danh Sách Kiểm Soát (`KiemSoat`)
- [[KS-001]] — **Đối soát tự động giao dịch và sổ cái** (Loại: `Detective`)
- [[KS-002]] — **Kiểm tra hạn mức phê duyệt trên hệ thống** (Loại: `Preventive`)
- [[KS-003]] — **Checklist điều kiện giải ngân bắt buộc** (Loại: `Preventive`)
- [[KS-004]] — **Rà soát quyền truy cập định kỳ** (Loại: `Preventive`)
- [[KS-005]] — **Kiểm thử khả năng chịu tải và chuyển đổi dự phòng** (Loại: `Preventive`)
- [[KS-006]] — **Xác thực hai kênh với lệnh chuyển tiền ngoại lệ** (Loại: `Preventive`)
- [[KS-007]] — **Theo dõi SLA xử lý cảnh báo AML** (Loại: `Detective`)
- [[KS-008]] — **Rà soát độc lập định giá tài sản bảo đảm** (Loại: `Detective`)
- [[KS-009]] — **Hiệu chỉnh luật phát hiện giao dịch gian lận** (Loại: `Preventive`)
- [[KS-010]] — **Đối chiếu dữ liệu nguồn trước khi phát hành báo cáo** (Loại: `Detective`)

### 3. 🟡 Danh Sách Sự Kiện Rủi Ro (`SuKienRuiRo`)
- [[SK-001]] — **Sai lệch trạng thái giao dịch được phát hiện khi đối soát cuối ngày** (Mức độ: `Trung binh`)
- [[SK-002]] — **Hồ sơ tín dụng được phê duyệt vượt hạn mức của người phê duyệt** (Mức độ: `Cao`)
- [[SK-003]] — **Giải ngân trước khi hoàn thiện chứng từ bảo đảm** (Mức độ: `Cao`)
- [[SK-004]] — **Tài khoản có quyền truy cập dữ liệu vượt phạm vi công việc** (Mức độ: `Cao`)
- [[SK-005]] — **Dịch vụ ngân hàng số gián đoạn trong giờ cao điểm** (Mức độ: `Cao`)
- [[SK-006]] — **Yêu cầu chuyển tiền giả mạo được xử lý trước khi bị thu hồi** (Mức độ: `Cao`)
- [[SK-007]] — **Báo cáo giao dịch đáng ngờ nộp quá hạn nội bộ** (Mức độ: `Trung binh`)
- [[SK-008]] — **Rà soát phát hiện giá trị tài sản bảo đảm đã hết hiệu lực** (Mức độ: `Cao`)
- [[SK-009]] — **Giao dịch bất thường chỉ bị phát hiện sau khi khách hàng khiếu nại** (Mức độ: `Cao`)
- [[SK-010]] — **Báo cáo quản trị sử dụng dữ liệu nguồn chưa đối chiếu** (Mức độ: `Trung binh`)
- [[SK-011]] — **Nhà cung cấp chậm khôi phục dịch vụ so với SLA** (Mức độ: `Trung binh`)
- [[SK-012]] — **Kiểm tra sau mua sắm phát hiện thiếu kê khai xung đột lợi ích** (Mức độ: `Trung binh`)

---

## 📍 Đường Đi Chi Tiết Mẫu (Sample Knowledge Path)
`[KS-001: Đối soát tự động giao dịch]` 
   └── 🛡️ *MITIGATES* ──> `[RR-001: Giao dịch chuyển tiền bị hạch toán sai]` 
                              └── ⚠️ *OBSERVED_AS* ──> `[SK-001: Sai lệch trạng thái giao dịch...]`
