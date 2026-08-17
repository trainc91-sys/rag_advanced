import os
import sys
import json
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def load_secure_kg():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    database = os.getenv("NEO4J_DATABASE", "neo4j")

    print(f"[Neo4j] Connecting to {uri} (Database: {database})...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        print("[Neo4j] Connection SUCCESSful!")
    except Exception as e:
        print(f"[Neo4j] ERROR: Connection failed ({e})")
        sys.exit(1)

    secure_csv = os.path.join(base_dir, "data", "processed", "chunks_secure.csv")
    if not os.path.exists(secure_csv):
        print(f"❌ Error: {secure_csv} does not exist. Run assign_security_tags.py first.")
        sys.exit(1)

    df = pd.read_csv(secure_csv)
    print(f"[Neo4j] Loading allowed_roles into graph for {len(df)} chunks...")

    # Prepare rows with parsed JSON roles as list
    rows_data = []
    doc_roles_map = {}

    for _, row in df.iterrows():
        cid = str(row['chunk_id'])
        did = str(row['document_id'])
        roles_list = json.loads(row['allowed_roles']) if isinstance(row['allowed_roles'], str) else row['allowed_roles']
        
        rows_data.append({
            "chunk_id": cid,
            "document_id": did,
            "allowed_roles": roles_list
        })

        if did not in doc_roles_map:
            doc_roles_map[did] = set()
        doc_roles_map[did].update(roles_list)

    doc_rows = [{"document_id": did, "allowed_roles": sorted(list(roles))} for did, roles in doc_roles_map.items()]

    with driver.session(database=database) as session:
        # Update DieuKhoan nodes
        cypher_dieukhoan = """
        UNWIND $rows AS row
        MERGE (d:DieuKhoan {id: row.chunk_id})
        SET d.allowed_roles = row.allowed_roles,
            d.lab_session_buoi15 = "buoi_15"
        """
        session.run(cypher_dieukhoan, rows=rows_data)

        # Update VanBan nodes
        cypher_vanban = """
        UNWIND $rows AS row
        MERGE (v:VanBan {id: row.document_id})
        SET v.allowed_roles = row.allowed_roles,
            v.lab_session_buoi15 = "buoi_15"
        """
        session.run(cypher_vanban, rows=doc_rows)

        # Verification Query 1: Count nodes with allowed_roles
        cnt_dieukhoan = session.run("MATCH (d:DieuKhoan) WHERE d.allowed_roles IS NOT NULL RETURN count(d) AS cnt").single()["cnt"]
        cnt_vanban = session.run("MATCH (v:VanBan) WHERE v.allowed_roles IS NOT NULL RETURN count(v) AS cnt").single()["cnt"]

        print(f"✅ Updated allowed_roles on {cnt_dieukhoan} DieuKhoan nodes and {cnt_vanban} VanBan nodes.")

        # Verification Query 2: Sample VanBan and linked DieuKhoan nodes
        sample_res = session.run("""
        MATCH (v:VanBan)-[:CONTAINS]->(d:DieuKhoan)
        WHERE v.allowed_roles IS NOT NULL AND d.allowed_roles IS NOT NULL
        RETURN v.id AS doc_id, v.so_ky_hieu AS so_ky_hieu, v.allowed_roles AS v_roles,
               d.id AS chunk_id, d.allowed_roles AS d_roles
        LIMIT 3
        """)

        print("\n--------------------------------------------------------")
        print("GRAPH SECURITY INGESTION VERIFICATION SAMPLES")
        print("--------------------------------------------------------")
        for rec in sample_res:
            print(f"VanBan [{rec['so_ky_hieu']} | ID: {rec['doc_id']}] -> Allowed Roles: {rec['v_roles']}")
            print(f"  └── DieuKhoan [{rec['chunk_id']}] -> Allowed Roles: {rec['d_roles']}")
        print("--------------------------------------------------------")

    driver.close()

if __name__ == "__main__":
    load_secure_kg()
