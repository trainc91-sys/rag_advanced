import os
import sys
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def load_mini_kg():
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
        report_path = os.path.join(base_dir, "outputs", "kg_build_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# MINI KNOWLEDGE GRAPH BUILD REPORT (BUỔI 14)\n\n**Status:** NOT RUN\n**Reason:** Neo4j connection failed: `{e}`\n")
        return

    session = driver.session(database=database)

    # 1. Apply Schema Constraints
    schema_path = os.path.join(base_dir, "cypher", "schema.cypher")
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            cypher_statements = [stmt.strip() for stmt in f.read().split(";") if stmt.strip()]
            for stmt in cypher_statements:
                try:
                    session.run(stmt)
                except Exception as ex:
                    pass

    # 2. Ingest VanBan Nodes
    kb_dir = os.path.abspath(os.path.join(base_dir, "..", "kb+hops"))
    meta_path = os.path.join(kb_dir, "metadata.csv")
    meta_df = pd.read_csv(meta_path)

    print(f"[Neo4j] Ingesting {len(meta_df)} VanBan nodes...")
    cypher_vanban = """
    UNWIND $rows AS row
    MERGE (v:VanBan {id: toString(row.id)})
    SET v.title = coalesce(row.title, ""),
        v.so_ky_hieu = coalesce(row.so_ky_hieu, ""),
        v.loai_van_ban = coalesce(row.loai_van_ban, ""),
        v.status = coalesce(row.tinh_trang_hieu_luc, ""),
        v.lab_session = "buoi_14"
    """
    session.run(cypher_vanban, rows=meta_df.to_dict(orient="records"))

    # 3. Ingest DieuKhoan Nodes & CONTAINS / NEXT Edges
    corpus_path = os.path.join(base_dir, "data", "processed", "chunks_normalized.csv")
    chunks_df = pd.read_csv(corpus_path)

    print(f"[Neo4j] Ingesting {len(chunks_df)} DieuKhoan nodes & structure edges...")
    cypher_dieukhoan = """
    UNWIND $rows AS row
    MERGE (d:DieuKhoan {id: toString(row.chunk_id)})
    SET d.document_id = toString(row.document_id),
        d.text = substring(coalesce(row.text, ""), 0, 1500),
        d.article = coalesce(row.article, ""),
        d.lab_session = "buoi_14"
    WITH d, row
    MATCH (v:VanBan {id: toString(row.document_id)})
    MERGE (v)-[r:CONTAINS]->(d)
    SET r.lab_session = "buoi_14"
    """
    session.run(cypher_dieukhoan, rows=chunks_df.to_dict(orient="records"))

    # Ingest NEXT Edges for sequential chunks within same document
    print("[Neo4j] Ingesting NEXT edges for sequential clauses...")
    grouped = chunks_df.groupby("document_id")
    next_pairs = []
    for doc_id, group in grouped:
        cids = group["chunk_id"].tolist()
        for c1, c2 in zip(cids[:-1], cids[1:]):
            next_pairs.append({"c1": str(c1), "c2": str(c2)})

    cypher_next = """
    UNWIND $pairs AS pair
    MATCH (d1:DieuKhoan {id: pair.c1})
    MATCH (d2:DieuKhoan {id: pair.c2})
    MERGE (d1)-[r:NEXT]->(d2)
    SET r.lab_session = "buoi_14"
    """
    session.run(cypher_next, pairs=next_pairs)

    # 4. Ingest Domain Relationships from relationships.csv
    rel_path = os.path.join(kb_dir, "relationships.csv")
    rel_count = 0
    if os.path.exists(rel_path):
        rel_df = pd.read_csv(rel_path)
        print(f"[Neo4j] Ingesting {len(rel_df)} domain relationships from relationships.csv...")
        
        # Check column names
        cols = rel_df.columns.tolist()
        source_col = "source" if "source" in cols else "doc_id"
        target_col = "target" if "target" in cols else "other_doc_id"
        rel_type_col = "relationship_type" if "relationship_type" in cols else "relationship"

        for _, rrow in rel_df.iterrows():
            src_val = str(rrow[source_col]).strip()
            tgt_val = str(rrow[target_col]).strip()
            r_type = str(rrow[rel_type_col]).strip().replace(" ", "_").upper()
            if not r_type or r_type == "NAN":
                r_type = "RELATED_TO"
            
            evidence = str(rrow.get("evidence", "")) if "evidence" in cols else ""

            cypher_rel = f"""
            MATCH (v1:VanBan {{lab_session: "buoi_14"}})
            WHERE v1.id = $src OR v1.so_ky_hieu = $src
            MATCH (v2:VanBan {{lab_session: "buoi_14"}})
            WHERE v2.id = $tgt OR v2.so_ky_hieu = $tgt
            MERGE (v1)-[r:{r_type}]->(v2)
            SET r.lab_session = "buoi_14", r.evidence = $evidence
            """
            try:
                session.run(cypher_rel, src=src_val, tgt=tgt_val, evidence=evidence)
                rel_count += 1
            except Exception as e:
                pass

    # 5. Graph Inspection & Validation Metrics
    n_vanban = session.run("MATCH (v:VanBan {lab_session: 'buoi_14'}) RETURN count(v) AS cnt").single()["cnt"]
    n_dieukhoan = session.run("MATCH (d:DieuKhoan {lab_session: 'buoi_14'}) RETURN count(d) AS cnt").single()["cnt"]
    n_contains = session.run("MATCH ()-[r:CONTAINS {lab_session: 'buoi_14'}]->() RETURN count(r) AS cnt").single()["cnt"]
    n_next = session.run("MATCH ()-[r:NEXT {lab_session: 'buoi_14'}]->() RETURN count(r) AS cnt").single()["cnt"]
    
    domain_rels_res = session.run("""
    MATCH (v1:VanBan {lab_session: "buoi_14"})-[r]->(v2:VanBan {lab_session: "buoi_14"})
    WHERE type(r) <> 'CONTAINS'
    RETURN type(r) AS rel_type, count(r) AS cnt
    """)
    domain_rel_counts = {record["rel_type"]: record["cnt"] for record in domain_rels_res}

    n_orphans = session.run("""
    MATCH (n {lab_session: "buoi_14"})
    WHERE NOT (n)-[]-()
    RETURN count(n) AS cnt
    """).single()["cnt"]

    session.close()
    driver.close()

    # Generate outputs/kg_build_report.md
    report_path = os.path.join(base_dir, "outputs", "kg_build_report.md")
    report_lines = [
        "# MINI KNOWLEDGE GRAPH BUILD REPORT (BUỔI 14)\n",
        "**Neo4j Status:** CONNECTED & LOADED SUCCESSFUL\n",
        "## 1. Node Counts by Label",
        f"- `:VanBan`: `{n_vanban}`",
        f"- `:DieuKhoan`: `{n_dieukhoan}`",
        f"- **Total Nodes:** `{n_vanban + n_dieukhoan}`\n",
        "## 2. Relationship Counts by Type",
        f"- `:CONTAINS`: `{n_contains}`",
        f"- `:NEXT`: `{n_next}`"
    ]
    for rtype, rcnt in domain_rel_counts.items():
        report_lines.append(f"- `:{rtype}`: `{rcnt}`")

    report_lines.append(f"\n## 3. Data Integrity & Safety Check")
    report_lines.append(f"- **Orphan Nodes Count:** `{n_orphans}`")
    report_lines.append(f"- **Lab Session Scope Tag:** `lab_session = 'buoi_14'` (Preserved past sessions)")
    report_lines.append(f"- **Destructive Delete Used:** NO (`MATCH (n) DETACH DELETE n` was NOT executed)\n")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n--- MINI KNOWLEDGE GRAPH BUILD COMPLETE ---")
    print(f"Nodes loaded: {n_vanban} VanBan, {n_dieukhoan} DieuKhoan")
    print(f"Edges loaded: {n_contains} CONTAINS, {n_next} NEXT, {sum(domain_rel_counts.values())} Domain relations")
    print(f"Orphan nodes: {n_orphans}")
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    load_mini_kg()
