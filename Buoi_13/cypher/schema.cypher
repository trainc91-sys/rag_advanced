// ============================================================
// 1. UNIQUENESS CONSTRAINTS & INDEXES FOR RISK GRAPH NODES
// ============================================================

// Constraint cho Node RuiRo
CREATE CONSTRAINT constraint_ruiro_id IF NOT EXISTS
FOR (r:RuiRo) REQUIRE r.id IS UNIQUE;

// Constraint cho Node KiemSoat
CREATE CONSTRAINT constraint_kiemsoat_id IF NOT EXISTS
FOR (k:KiemSoat) REQUIRE k.id IS UNIQUE;

// Constraint cho Node SuKienRuiRo
CREATE CONSTRAINT constraint_sukienruiro_id IF NOT EXISTS
FOR (s:SuKienRuiRo) REQUIRE s.id IS UNIQUE;

// Fulltext / Range Indexes cho Tra Cứu Tên & Danh Mục
CREATE INDEX index_ruiro_name IF NOT EXISTS
FOR (r:RuiRo) ON (r.name);

CREATE INDEX index_kiemsoat_name IF NOT EXISTS
FOR (k:KiemSoat) ON (k.name);

CREATE INDEX index_sukien_severity IF NOT EXISTS
FOR (s:SuKienRuiRo) ON (s.severity);
