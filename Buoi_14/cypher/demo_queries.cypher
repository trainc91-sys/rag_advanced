// DEMO QUERIES FOR BUỔI 14 MINI KNOWLEDGE GRAPH

// Query A — Xem toàn bộ Subgraph của Buổi 14
MATCH (n {lab_session: "buoi_14"})-[r]->(m {lab_session: "buoi_14"})
RETURN n, r, m
LIMIT 100;

// Query B — Từ văn bản tới các điều khoản thuộc văn bản
MATCH (v:VanBan {lab_session: "buoi_14"})-[r:CONTAINS]->(d:DieuKhoan {lab_session: "buoi_14"})
RETURN v.so_ky_hieu AS VanBan, v.title AS TenVanBan, d.id AS ChunkID, d.article AS DieuKhoan
LIMIT 50;

// Query C — Xem chuỗi điều khoản kế tiếp (NEXT relationship)
MATCH path = (d1:DieuKhoan {lab_session: "buoi_14"})-[:NEXT*1..3]->(d2:DieuKhoan {lab_session: "buoi_14"})
RETURN path
LIMIT 20;

// Query D — Xem quan hệ giữa các văn bản thực tế (ví dụ: SUA_DOI_BO_SUNG, THAM_CHIEU, THAY_THE)
MATCH (v1:VanBan {lab_session: "buoi_14"})-[r]->(v2:VanBan {lab_session: "buoi_14"})
WHERE type(r) <> 'CONTAINS'
RETURN v1.so_ky_hieu AS TuVanBan, type(r) AS LoaiQuanHe, v2.so_ky_hieu AS DenVanBan, r.evidence AS BangChung
LIMIT 50;

// Query E — Kiểm tra các node mồ côi (Orphan nodes)
MATCH (n {lab_session: "buoi_14"})
WHERE NOT (n)-[]-()
RETURN labels(n) AS Label, n.id AS NodeID, n.title AS Title;
