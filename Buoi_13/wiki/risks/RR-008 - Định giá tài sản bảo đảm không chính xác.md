---
id: RR-008
title: "RR-008 - Định giá tài sản bảo đảm không chính xác"
aliases:
  - "RR-008 - Định giá tài sản bảo đảm không chính xác"
  - "Định giá tài sản bảo đảm không chính xác"
  - "RR-008"
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---

# RR-008 - Định giá tài sản bảo đảm không chính xác

## 1. Thông Tin Chung
- **Mã Rủi Ro:** `RR-008`
- **Tên Rủi Ro:** Định giá tài sản bảo đảm không chính xác
- **Danh Mục (Category):** Rui ro tin dung
- **Mô Tả:** Dữ liệu định giá không độc lập hoặc hết hạn
- **Đơn Vị Phụ Trách (Owner Unit ID):** `DV-CREDIT`

## 2. Diễn Giải Rủi Ro (Cause -> Event -> Impact)
- **Nguyên Nhân (Cause):** Thiếu rà soát lại giá trị tài sản
- **Sự Kiện (Event):** Tài sản bảo đảm được định giá cao hơn thực tế
- **Tác Động (Impact):** Tăng tổn thất khi xử lý nợ

## 3. Mức Độ Rủi Ro
- **Mức Rủi Ro Cố Hữu (Inherent Level):** `Cao`
- **Mức Rủi Ro Còn Lại (Residual Level):** `Trung binh`

## 4. Kiểm Soát Giảm Thiểu (MITIGATES)
- [[KS-008 - Rà soát độc lập định giá tài sản bảo đảm]]
  - *Quan hệ:* `MITIGATES` | *Xác minh:* `VERIFIED`
  - *Bằng chứng:* "Dữ liệu mô phỏng: rà soát độc lập giảm sai định giá"

## 5. Sự Kiện Rủi Ro Quan Sát Được (OBSERVED_AS)
- [[SK-008 - Rà soát phát hiện giá trị tài sản bảo đảm đã hết hiệu lực]]
  - *Quan hệ:* `OBSERVED_AS` | *Xác minh:* `VERIFIED`
  - *Bằng chứng:* "Dữ liệu mô phỏng: sự kiện sai định giá tài sản"
