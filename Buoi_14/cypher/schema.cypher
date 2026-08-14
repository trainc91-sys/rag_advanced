// Schema Constraints & Indexes for Buổi 14 Mini Knowledge Graph

CREATE CONSTRAINT vanban_id_unique IF NOT EXISTS
FOR (v:VanBan) REQUIRE v.id IS UNIQUE;

CREATE CONSTRAINT dieukhoan_id_unique IF NOT EXISTS
FOR (d:DieuKhoan) REQUIRE d.id IS UNIQUE;

CREATE INDEX vanban_lab_session_idx IF NOT EXISTS
FOR (v:VanBan) ON (v.lab_session);

CREATE INDEX dieukhoan_lab_session_idx IF NOT EXISTS
FOR (d:DieuKhoan) ON (d.lab_session);
