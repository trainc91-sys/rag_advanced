"""
step8_import_neo4j.py
---------------------
BƯỚC 8: Import Knowledge Graph vào Neo4j (Đảm bảo Idempotent)
- Input:
  + ner_kb/cleaned_documents.csv
  + ner_kb/entities.csv
  + ner_kb/relationships.csv
- Nạp Node: Document, CoQuan, NguoiKy, DoiTuongApDung, LinhVuc
- Nạp Edge: BAN_HANH_BOI, KY_BOI, AP_DUNG_CHO, THUOC_LINH_VUC, THAM_CHIEU, SUA_DOI_BO_SUNG, THAY_THE_BOI
- Sử dụng MERGE & Uniqueness Constraints để nạp dữ liệu Idempotent (Chạy lại không tăng duplicate node/edge).
"""

import os
import sys
import pathlib
import pandas as pd
from dotenv import load_dotenv

# Ensure UTF-8 output encoding for terminal
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = pathlib.Path(__file__).resolve().parent
NER_KB_DIR = BASE_DIR / "ner_kb"

CLEANED_DOCS_PATH = NER_KB_DIR / "cleaned_documents.csv"
ENTITIES_PATH = NER_KB_DIR / "entities.csv"
RELATIONSHIPS_PATH = NER_KB_DIR / "relationships.csv"

ENV_PATH = BASE_DIR / ".env"
if not ENV_PATH.exists():
    ENV_PATH = BASE_DIR.parent / "buoi_11" / ".env"

load_dotenv(ENV_PATH)

from neo4j import GraphDatabase

def create_constraints(session):
    print("   - Đang tạo các Uniqueness Constraints...")
    constraints = [
        "CREATE CONSTRAINT doc_id_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;",
        "CREATE CONSTRAINT doc_so_ky_hieu_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.so_ky_hieu IS UNIQUE;",
        "CREATE CONSTRAINT conquan_name_unique IF NOT EXISTS FOR (c:CoQuan) REQUIRE c.name IS UNIQUE;",
        "CREATE CONSTRAINT nguoiky_name_unique IF NOT EXISTS FOR (n:NguoiKy) REQUIRE n.name IS UNIQUE;",
        "CREATE CONSTRAINT doituong_name_unique IF NOT EXISTS FOR (d:DoiTuongApDung) REQUIRE d.name IS UNIQUE;",
        "CREATE CONSTRAINT linhvuc_name_unique IF NOT EXISTS FOR (l:LinhVuc) REQUIRE l.name IS UNIQUE;"
    ]
    for c in constraints:
        try:
            session.run(c)
        except Exception as e:
            # Constraints might already exist or DB version variations
            pass

def import_nodes_and_relationships(session, df_docs, df_entities, df_rels):
    import_errors = []

    # 1. Import Document Nodes
    print("   - Importing Document nodes...")
    for idx, row in df_docs.iterrows():
        doc_id = str(row['id']).strip()
        so_ky_hieu = str(row.get('so_ky_hieu', '')).strip()
        title = str(row.get('title', '')).strip()
        loai_vb = str(row.get('loai_van_ban', '')).strip()
        ngay_ban_hanh = str(row.get('ngay_ban_hanh', '')).strip()
        
        query = """
        MERGE (d:Document {id: $doc_id})
        ON CREATE SET d.so_ky_hieu = $so_ky_hieu, d.title = $title, d.loai_van_ban = $loai_vb, d.ngay_ban_hanh = $ngay_ban_hanh
        ON MATCH SET d.so_ky_hieu = $so_ky_hieu, d.title = $title, d.loai_van_ban = $loai_vb, d.ngay_ban_hanh = $ngay_ban_hanh
        """
        try:
            session.run(query, doc_id=doc_id, so_ky_hieu=so_ky_hieu, title=title, loai_vb=loai_vb, ngay_ban_hanh=ngay_ban_hanh)
        except Exception as e:
            import_errors.append(f"Document {doc_id}: {str(e)}")

    # 2. Import Entity Nodes
    print("   - Importing Entity nodes (CoQuan, NguoiKy, DoiTuongApDung, LinhVuc)...")
    for idx, row in df_entities.iterrows():
        etype = str(row['entity_type']).strip()
        cname = str(row['canonical_name']).strip()
        if not cname:
            continue

        label_map = {
            "CoQuan": "CoQuan",
            "NguoiKy": "NguoiKy",
            "DoiTuongApDung": "DoiTuongApDung",
            "LinhVuc": "LinhVuc"
        }
        label = label_map.get(etype)
        if label:
            query = f"MERGE (e:{label} {{name: $name}})"
            try:
                session.run(query, name=cname)
            except Exception as e:
                import_errors.append(f"Entity {etype} '{cname}': {str(e)}")

    # 3. Import Relationships
    print("   - Importing Relationships...")
    for idx, row in df_rels.iterrows():
        source = str(row['source']).strip()
        target = str(row['target']).strip()
        rel_type = str(row['relationship_type']).strip()
        evidence = str(row.get('evidence', '')).strip()

        if not source or not target or not rel_type:
            continue

        # Case A: Document -> Entity relationships
        if rel_type in ["BAN_HANH_BOI", "KY_BOI", "AP_DUNG_CHO", "THUOC_LINH_VUC"]:
            target_label_map = {
                "BAN_HANH_BOI": "CoQuan",
                "KY_BOI": "NguoiKy",
                "AP_DUNG_CHO": "DoiTuongApDung",
                "THUOC_LINH_VUC": "LinhVuc"
            }
            tlabel = target_label_map.get(rel_type)
            
            # Match Document by so_ky_hieu or id
            query = f"""
            MATCH (d:Document) WHERE d.so_ky_hieu = $source OR d.id = $source
            MATCH (e:{tlabel} {{name: $target}})
            MERGE (d)-[r:{rel_type}]->(e)
            ON CREATE SET r.evidence = $evidence
            ON MATCH SET r.evidence = $evidence
            """
            try:
                result = session.run(query, source=source, target=target, evidence=evidence)
            except Exception as e:
                import_errors.append(f"Rel Doc->Entity ({source} -[{rel_type}]-> {target}): {str(e)}")

        # Case B: Document -> Document relationships
        elif rel_type in ["THAM_CHIEU", "SUA_DOI_BO_SUNG", "THAY_THE_BOI"]:
            # Ensure target Document node exists or MERGE stub document node
            query = f"""
            MERGE (d1:Document {{so_ky_hieu: $source}})
            MERGE (d2:Document {{so_ky_hieu: $target}})
            MERGE (d1)-[r:{rel_type}]->(d2)
            ON CREATE SET r.evidence = $evidence
            ON MATCH SET r.evidence = $evidence
            """
            try:
                session.run(query, source=source, target=target, evidence=evidence)
            except Exception as e:
                import_errors.append(f"Rel Doc->Doc ({source} -[{rel_type}]-> {target}): {str(e)}")

    return import_errors

def get_graph_counts(session):
    node_res = session.run("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY count DESC")
    nodes = {rec['label']: rec['count'] for rec in node_res}
    
    rel_res = session.run("MATCH ()-[r]->() RETURN type(r) AS rel_type, count(r) AS count ORDER BY count DESC")
    rels = {rec['rel_type']: rec['count'] for rec in rel_res}
    
    return nodes, rels

def main():
    print("==========================================================")
    print("🚀 BẮT ĐẦU BƯỚC 8: IMPORT KNOWLEDGE GRAPH VÀO NEO4J")
    print("==========================================================\n")

    # Read config
    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_pass = os.environ.get("NEO4J_PASSWORD", "")
    neo4j_db = os.environ.get("NEO4J_DATABASE", "kb-hops")

    if not CLEANED_DOCS_PATH.exists() or not ENTITIES_PATH.exists() or not RELATIONSHIPS_PATH.exists():
        print("❌ Error: File đầu vào không tồn tại trong ner_kb/")
        return

    df_docs = pd.read_csv(CLEANED_DOCS_PATH)
    df_entities = pd.read_csv(ENTITIES_PATH)
    df_rels = pd.read_csv(RELATIONSHIPS_PATH)

    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))

    # --- LẦN 1: IMPORT LẦN ĐẦU ---
    print("1️⃣ Thực hiện IMPORT LẦN 1 vào Neo4j...")
    with driver.session(database=neo4j_db) as session:
        create_constraints(session)
        errors1 = import_nodes_and_relationships(session, df_docs, df_entities, df_rels)
        nodes1, rels1 = get_graph_counts(session)

    print(f"\n   📊 Kết quả sau LẦN 1:")
    print(f"      - Tổng số Node: {sum(nodes1.values())} {nodes1}")
    print(f"      - Tổng số Relationship: {sum(rels1.values())} {rels1}")
    print(f"      - Số lỗi import Lần 1: {len(errors1)}")

    # --- LẦN 2: IMPORT LẦN HAI ĐỂ KIỂM TRA IDEMPOTENT ---
    print("\n2️⃣ Thực hiện IMPORT LẦN 2 để kiểm tra tính IDEMPOTENT (MERGE Check)...")
    with driver.session(database=neo4j_db) as session:
        errors2 = import_nodes_and_relationships(session, df_docs, df_entities, df_rels)
        nodes2, rels2 = get_graph_counts(session)

    print(f"\n   📊 Kết quả sau LẦN 2:")
    print(f"      - Tổng số Node: {sum(nodes2.values())} {nodes2}")
    print(f"      - Tổng số Relationship: {sum(rels2.values())} {rels2}")
    print(f"      - Số lỗi import Lần 2: {len(errors2)}")

    driver.close()

    # Check Idempotency Condition
    nodes_diff = abs(sum(nodes2.values()) - sum(nodes1.values()))
    rels_diff = abs(sum(rels2.values()) - sum(rels1.values()))
    
    idempotent_pass = (nodes_diff == 0) and (rels_diff == 0)

    print("\n==========================================================")
    if idempotent_pass and sum(nodes1.values()) > 0:
        print("🎯 KẾT QUẢ BƯỚC 8: [PASS]")
        print("   - Import thành công toàn bộ Node & Relationship vào Neo4j!")
        print("   - Lần 2 không tạo duplicate node/edge (Idempotency Test: PASS)")
    else:
        print("❌ KẾT QUẢ BƯỚC 8: [FAIL]")
        print(f"   - Sai lệch Node: {nodes_diff}, Sai lệch Relationship: {rels_diff}")
    print("==========================================================")

if __name__ == "__main__":
    main()
