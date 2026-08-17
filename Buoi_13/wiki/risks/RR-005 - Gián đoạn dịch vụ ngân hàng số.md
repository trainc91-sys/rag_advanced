---
id: RR-005
title: "RR-005 - Gián đoạn dịch vụ ngân hàng số"
aliases:
  - "RR-005 - Gián đoạn dịch vụ ngân hàng số"
  - "Gián đoạn dịch vụ ngân hàng số"
  - "RR-005"
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---

# RR-005 - Gián đoạn dịch vụ ngân hàng số

## 1. Thông Tin Chung
- **Mã Rủi Ro:** `RR-005`
- **Tên Rủi Ro:** Gián đoạn dịch vụ ngân hàng số
- **Danh Mục (Category):** Rui ro cong nghe thong tin
- **Mô Tả:** Hệ thống thanh toán trực tuyến không sẵn sàng
- **Đơn Vị Phụ Trách (Owner Unit ID):** `DV-IT`

## 2. Diễn Giải Rủi Ro (Cause -> Event -> Impact)
- **Nguyên Nhân (Cause):** Kế hoạch năng lực và dự phòng chưa đầy đủ
- **Sự Kiện (Event):** Dịch vụ ngân hàng số bị gián đoạn
- **Tác Động (Impact):** Mất doanh thu và khiếu nại khách hàng

## 3. Mức Độ Rủi Ro
- **Mức Rủi Ro Cố Hữu (Inherent Level):** `Cao`
- **Mức Rủi Ro Còn Lại (Residual Level):** `Trung binh`

## 4. Kiểm Soát Giảm Thiểu (MITIGATES)
- [[KS-005 - Kiểm thử khả năng chịu tải và chuyển đổi dự phòng]]
  - *Quan hệ:* `MITIGATES` | *Xác minh:* `VERIFIED`
  - *Bằng chứng:* "Dữ liệu mô phỏng: kiểm thử dự phòng giảm gián đoạn dịch vụ"

## 5. Sự Kiện Rủi Ro Quan Sát Được (OBSERVED_AS)
- [[SK-005 - Dịch vụ ngân hàng số gián đoạn trong giờ cao điểm]]
  - *Quan hệ:* `OBSERVED_AS` | *Xác minh:* `VERIFIED`
  - *Bằng chứng:* "Dữ liệu mô phỏng: sự kiện gián đoạn dịch vụ"
