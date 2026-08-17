---
id: RR-010
title: "RR-010 - Sai lệch số liệu báo cáo quản trị"
aliases:
  - "RR-010 - Sai lệch số liệu báo cáo quản trị"
  - "Sai lệch số liệu báo cáo quản trị"
  - "RR-010"
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---

# RR-010 - Sai lệch số liệu báo cáo quản trị

## 1. Thông Tin Chung
- **Mã Rủi Ro:** `RR-010`
- **Tên Rủi Ro:** Sai lệch số liệu báo cáo quản trị
- **Danh Mục (Category):** Rui ro bao cao
- **Mô Tả:** Dữ liệu nguồn không được đối chiếu
- **Đơn Vị Phụ Trách (Owner Unit ID):** `DV-FINANCE`

## 2. Diễn Giải Rủi Ro (Cause -> Event -> Impact)
- **Nguyên Nhân (Cause):** Thay đổi dữ liệu không có kiểm soát
- **Sự Kiện (Event):** Báo cáo quản trị có số liệu sai
- **Tác Động (Impact):** Quyết định quản trị sai lệch

## 3. Mức Độ Rủi Ro
- **Mức Rủi Ro Cố Hữu (Inherent Level):** `Trung binh`
- **Mức Rủi Ro Còn Lại (Residual Level):** `Thap`

## 4. Kiểm Soát Giảm Thiểu (MITIGATES)
- [[KS-010 - Đối chiếu dữ liệu nguồn trước khi phát hành báo cáo]]
  - *Quan hệ:* `MITIGATES` | *Xác minh:* `VERIFIED`
  - *Bằng chứng:* "Dữ liệu mô phỏng: đối chiếu nguồn giảm sai lệch báo cáo"

## 5. Sự Kiện Rủi Ro Quan Sát Được (OBSERVED_AS)
- [[SK-010 - Báo cáo quản trị sử dụng dữ liệu nguồn chưa đối chiếu]]
  - *Quan hệ:* `OBSERVED_AS` | *Xác minh:* `VERIFIED`
  - *Bằng chứng:* "Dữ liệu mô phỏng: sự kiện sai lệch báo cáo"
