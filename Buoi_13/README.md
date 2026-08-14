# 🛡️ Wiki Risk Graph — Hướng Dẫn Dự Án (Vibe Coding)

Dự án này xây dựng **Wiki Tri Thức Rủi Ro dạng Đồ Thị (Wiki Risk Graph)** từ dữ liệu rủi ro mô phỏng, phục vụ tra cứu hồ sơ rủi ro, kiểm soát giảm thiểu, sự kiện rủi ro, trực quan hóa trên **Obsidian Graph View** và truy vấn đồ thị bằng **Neo4j Cypher**.

---

## 📁 Cấu Trúc Thư Mục Dự Án

```text
d:\RAG\rag_advanced\Buoi_13\
│
├── data/                             # Dữ liệu hạt giống đầu vào (CSV seed)
│   ├── risk_profiles_seed.csv        # Hồ sơ rủi ro (RuiRo)
│   ├── controls_seed.csv             # Kiểm soát rủi ro (KiemSoat)
│   ├── risk_events_seed.csv          # Sự kiện rủi ro đã phát hiện (SuKienRuiRo)
│   └── relationships_seed.csv        # Mạng lưới quan hệ (Edges)
│
├── scripts/                          # Mã nguồn Python xử lý và kiểm thử
│   ├── inspect_data.py               # Bước 1: Kiểm tra vẹn toàn CSV đầu vào
│   ├── build_entities.py             # Bước 2: Chuẩn hóa thành Entities & Relations
│   ├── build_wiki.py                 # Bước 3: Sinh các trang Wiki Markdown & Wikilinks
│   ├── validate_wiki.py              # Bước 4: Kiểm thử toàn vẹn Wiki & xuất báo cáo
│   └── load_neo4j.py                 # Bước 6: Script nạp tự động vào Neo4j Graph DB
│
├── outputs/                          # Kết quả đầu ra sau chuẩn hóa
│   ├── entities.csv                  # Danh sách 34 entities chuẩn (Nodes)
│   ├── relations.csv                 # Danh sách 22 relations chuẩn (Edges)
│   └── wiki_validation_report.md     # Báo cáo kiểm thử chất lượng Wiki
│
├── wiki/                             # Obsidian Knowledge Vault
│   ├── Home.md                       # Trang chủ tổng quan & chỉ mục Wiki
│   ├── risks/                        # 12 trang hồ sơ rủi ro (RR-001 -> RR-012)
│   ├── controls/                     # 10 trang kiểm soát rủi ro (KS-001 -> KS-010)
│   └── events/                       # 12 trang sự kiện rủi ro (SK-001 -> SK-012)
│
├── cypher/                           # Truy vấn đồ thị cho Neo4j
│   ├── schema.cypher                 # Constraints & Indexes schema
│   └── demo_queries.cypher           # Các truy vấn Cypher demo (A -> F)
│
├── .env.example                      # Mẫu cấu hình môi trường Neo4j
└── README.md                         # Tài liệu hướng dẫn thực thi dự án
```

---

## 🚀 Thứ Tự Chạy Các Lệnh Dự Án (Step-by-Step Execution)

### Bước 1: Kiểm Tra Dữ Liệu Nguồn CSV
Kiểm tra số dòng, tên cột, khóa chính, các loại `relationship_type` và tính toàn vẹn tham chiếu.
```bash
python scripts/inspect_data.py
```

### Bước 2: Chuẩn Hóa Dữ Liệu Thành Entities & Relations
Tạo `outputs/entities.csv` (34 nodes) và `outputs/relations.csv` (22 edges).
```bash
python scripts/build_entities.py
```

### Bước 3: Sinh Wiki Markdown Cho Obsidian
Tạo 35 trang Markdown với đầy đủ YAML frontmatter và Obsidian `[[wikilink]]` liên kết 2 chiều.
```bash
python scripts/build_wiki.py
```

### Bước 4: Kiểm Thử Toàn Vẹn Wiki (Validation)
Kiểm tra broken links, orphan pages, duplicate IDs và phát hiện điểm hổng dữ liệu.
```bash
python scripts/validate_wiki.py
```
*Kết quả báo cáo được lưu tại:* `outputs/wiki_validation_report.md`

---

## 🌐 Bước 5: Mở Thư Mục Wiki Trong Obsidian Graph View

1. Mở phần mềm **Obsidian**.
2. Chọn **Open folder as vault**.
3. Duyệt và chọn thư mục: `d:\RAG\rag_advanced\Buoi_13\wiki`.
4. Mở trang `Home.md` để tra cứu các hồ sơ rủi ro, kiểm soát và sự kiện.
5. Mở tính năng **Graph View** (Phím tắt: `Ctrl + G`) để quan sát đồ thị liên kết:
   ```text
   KiemSoat (Xanh)  ──[MITIGATES]──>  RuiRo (Đỏ)  ──[OBSERVED_AS]──>  SuKienRuiRo (Vàng)
   ```

---

## 📊 Bước 6: Nạp Dữ Liệu Vào Neo4j & Truy Vấn Cypher

### 1. Cấu hình file `.env`
Tạo file `.env` từ `.env.example`:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
NEO4J_DATABASE=neo4j
```

### 2. Nạp dữ liệu tự động bằng Python
```bash
python scripts/load_neo4j.py
```

### 3. Thực thi Cypher Demo Queries
Mở **Neo4j Browser** và chạy các câu lệnh trong `cypher/demo_queries.cypher`:
- **Đường đi 3 chặng:**
  ```cypher
  MATCH path = (k:KiemSoat)-[:MITIGATES]->(r:RuiRo)-[:OBSERVED_AS]->(s:SuKienRuiRo)
  RETURN path LIMIT 20;
  ```
- **Phát hiện Rủi ro chưa có Kiểm soát:**
  ```cypher
  MATCH (r:RuiRo)
  WHERE NOT (:KiemSoat)-[:MITIGATES]->(r)
  RETURN r.id, r.name, r.category;
  ```

---

## 🛑 Quy Tắc Xử Lý Dữ Liệu Nghiêm Ngặt

1. **Owner Unit & Role Codes:** `owner_unit_id` (ví dụ `DV-OPS`) và `owner_role_id` (ví dụ `VT-OPS-CONTROL`) chỉ là mã tham chiếu, **tuyệt đối không tự suy luận hoặc bịa tên đơn vị/vai trò đầy đủ** khi chưa có master data.
2. **Nguyên Trạng Xác Minh:** Không tự chuyển đổi trạng thái `verification_status` từ `PROPOSED` sang `VERIFIED`.
3. **Phát Hiện Điểm Hổng Dữ Liệu:** Hai hồ sơ rủi ro `RR-011` *(Nhà cung cấp công nghệ không đáp ứng cam kết)* và `RR-012` *(Xung đột lợi ích trong mua sắm)* chưa có Kiểm soát giảm thiểu trong dữ liệu seed — đây là phát hiện nghiệp vụ thực tế qua công cụ Validation report.
