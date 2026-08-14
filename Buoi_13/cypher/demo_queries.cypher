// ============================================================
// WIKI RISK GRAPH — DEMO CYPHER QUERIES FOR NEO4J
// ============================================================

// ------------------------------------------------------------
// A. Xem toàn bộ graph (Nodes & Edges)
// ------------------------------------------------------------
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 100;

// ------------------------------------------------------------
// B. Tìm kiểm soát giảm thiểu một rủi ro cụ thể (vd: RR-001)
// ------------------------------------------------------------
MATCH (k:KiemSoat)-[r:MITIGATES]->(r_risk:RuiRo {id: 'RR-001'})
RETURN k.id AS MaKiemSoat, k.name AS TenKiemSoat, k.effectiveness AS HieuQua, 
       r.evidence_quote AS BangChung, r.verification_status AS TrangThaiXacMinh;

// ------------------------------------------------------------
// C. Tìm tất cả sự kiện rủi ro đã ghi nhận của một rủi ro (vd: RR-001)
// ------------------------------------------------------------
MATCH (r_risk:RuiRo {id: 'RR-001'})-[r:OBSERVED_AS]->(s:SuKienRuiRo)
RETURN s.id AS MaSuKien, s.description AS MoTaSuKien, s.severity AS MucDoNghiemTrong, 
       s.loss_amount_vnd AS TonThatVND, s.occurred_at AS NgayXayRa;

// ------------------------------------------------------------
// D. Tìm đường đi 3 chặng: KiemSoat -> RuiRo -> SuKienRuiRo
// ------------------------------------------------------------
MATCH path = (k:KiemSoat)-[:MITIGATES]->(r:RuiRo)-[:OBSERVED_AS]->(s:SuKienRuiRo)
RETURN k.name AS ControlName, r.name AS RiskName, s.description AS EventDescription, path
LIMIT 20;

// ------------------------------------------------------------
// E. Tìm rủi ro không có kiểm soát giảm thiểu (Orphan Risks)
// ------------------------------------------------------------
MATCH (r:RuiRo)
WHERE NOT (:KiemSoat)-[:MITIGATES]->(r)
RETURN r.id AS MaRuiRo, r.name AS TenRuiRo, r.category AS DanhMuc, r.residual_level AS MucDoConLai;

// ------------------------------------------------------------
// F. Tìm các quan hệ (edges) chưa được VERIFIED (vd: PROPOSED hoặc PENDING)
// ------------------------------------------------------------
MATCH (source)-[r]->(target)
WHERE r.verification_status <> 'VERIFIED'
RETURN source.id AS SourceID, type(r) AS RelationshipType, target.id AS TargetID, 
       r.verification_status AS Status, r.evidence_quote AS Evidence;
