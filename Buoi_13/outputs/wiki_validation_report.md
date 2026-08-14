# 📋 BÁO CÁO KIỂM THỬ VẸN TOÀN WIKI RISK GRAPH

**Ngày kiểm thử:** `2026-08-14`
**Hệ thống kiểm thử:** `scripts/validate_wiki.py`
**Thư mục Wiki:** `wiki/`

---

## 1. 📊 THỐNG KÊ TỔNG QUAN

| Tiêu chí | Số lượng | Trạng thái |
| :--- | :--- | :--- |
| **Tổng số file Markdown** | `35` | ✅ Đạt |
| **Tổng số Obsidian Wikilink** | `78` | ✅ Đạt |
| **Số Wikilink bị hỏng (Broken links)** | `0` | ✅ Không có |
| **Trùng lặp mã Entity ID** | `0` | ✅ Không trùng |
| **Trang có ID không trong entities.csv** | `0` | ✅ Khớp 100% |
| **Quan hệ tham chiếu lỗi (Relations)** | `0` | ✅ Khớp 100% |
| **Trang mồ côi (Orphan pages)** | `0` | ✅ Không có |

---

## 2. 🔍 CHI TIẾT PHÁT HIỆN VÀ PHÂN TÍCH LỖI

### 2.1. Kiểm Tra Broken Wikilinks
✅ **0 lỗi.** Tất cả 100% Obsidian wikilinks đều trỏ đúng tới trang Markdown hợp lệ.

### 2.2. Kiểm Tra Rủi Ro Chưa Có Kiểm Soát Giảm Thiểu (Missing Controls)
⚠️ **Phát hiện 2 hồ sơ Rủi ro chưa được gán bất kỳ Kiểm soát nào:**
- 🔴 **[[RR-011]]** — `Nhà cung cấp công nghệ không đáp ứng cam kết` (Phân loại: `Rui ro ben thu ba`)
- 🔴 **[[RR-012]]** — `Xung đột lợi ích trong mua sắm` (Phân loại: `Rui ro dao duc`)

> 💡 **Phân tích:** Đây là **LỖI DỮ LIỆU THỰC TẾ** từ seed CSV (trong `controls_seed.csv` chỉ có KS-001 đến KS-010, thiếu kiểm soát cho RR-011 và RR-012). Không phải lỗi chương trình `build_wiki.py`.

### 2.3. Kiểm Tra Rủi Ro Chưa Có Sự Kiện Ghi Nhận (Missing Events)
✅ **0 lỗi.** 100% hồ sơ rủi ro (12/12) đều đã có sự kiện rủi ro quan sát được tương ứng.

### 2.4. Kiểm Tra Trang Mồ Côi (Orphan Pages)
✅ **0 trang mồ côi.** Tất cả các trang đều có liên kết hai chiều vào mạng lưới Knowledge Graph.

---

## 3. 🎯 KẾT LUẬN VÀ KHUYẾN NGHỊ

1. **Về Mã Nguồn & Code Build Wiki:** Chương trình `build_wiki.py` hoạt động hoàn hảo, tạo đúng **35/35 trang Wiki**, **78/78 wikilinks chuẩn xác**, 0 broken links, 0 trang mồ côi.
2. **Về Chất Lượng Dữ Liệu Seed:** Phát hiện điểm hổng nghiệp vụ: **RR-011** *(Nhà cung cấp công nghệ không đáp ứng cam kết)* và **RR-012** *(Xung đột lợi ích trong mua sắm)* hiện chưa có kiểm soát nào giảm thiểu. Bộ phận quản lý rủi ro cần bổ sung kiểm soát cho 2 hồ sơ rủi ro này.
