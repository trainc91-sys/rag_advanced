import os
import sys
import pandas as pd

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def load_env(env_path):
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()
    return env_vars

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "outputs")
    entities_path = os.path.join(output_dir, "entities.csv")
    relations_path = os.path.join(output_dir, "relations.csv")
    env_path = os.path.join(base_dir, ".env")
    
    if not os.path.exists(entities_path) or not os.path.exists(relations_path):
        print("[ERR] Chưa có outputs/entities.csv hoặc outputs/relations.csv. Hãy chạy scripts/build_entities.py trước!")
        return

    # Check neo4j python library
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("=" * 70)
        print("[THÔNG BÁO] Chưa cài đặt thư viện python `neo4j`.")
        print("Để chạy nạp dữ liệu tự động vào Neo4j, hãy thực hiện:")
        print("  pip install neo4j python-dotenv")
        print("=" * 70)
        return

    # Load environment variables
    env_vars = load_env(env_path)
    uri = env_vars.get("NEO4J_URI", os.environ.get("NEO4J_URI", "bolt://localhost:7687"))
    user = env_vars.get("NEO4J_USER", os.environ.get("NEO4J_USER", "neo4j"))
    password = env_vars.get("NEO4J_PASSWORD", os.environ.get("NEO4J_PASSWORD", ""))
    database = env_vars.get("NEO4J_DATABASE", os.environ.get("NEO4J_DATABASE", "neo4j"))

    if not password or password == "your_password_here":
        print("=" * 70)
        print("[THÔNG BÁO] Mật khẩu Neo4j chưa được cấu hình hợp lệ trong file .env.")
        print("Hãy tạo file .env từ .env.example và điền NEO4J_PASSWORD chính xác.")
        print("=" * 70)
        return

    print(f"Đang kết nối tới Neo4j tại: {uri} (Database: {database})...")

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session(database=database) as session:
            # 1. Create Schema Constraints
            print("1. Tạo constraints và indexes...")
            session.run("CREATE CONSTRAINT constraint_ruiro_id IF NOT EXISTS FOR (r:RuiRo) REQUIRE r.id IS UNIQUE")
            session.run("CREATE CONSTRAINT constraint_kiemsoat_id IF NOT EXISTS FOR (k:KiemSoat) REQUIRE k.id IS UNIQUE")
            session.run("CREATE CONSTRAINT constraint_sukienruiro_id IF NOT EXISTS FOR (s:SuKienRuiRo) REQUIRE s.id IS UNIQUE")
            
            # 2. Ingest Entities
            entities_df = pd.read_csv(entities_path, keep_default_na=False)
            print(f"2. Nạp {len(entities_df)} Entities vào Neo4j...")
            
            for _, row in entities_df.iterrows():
                etype = row["type"]
                props = row.to_dict()
                
                query = f"""
                MERGE (n:{etype} {{id: $id}})
                SET n += $props
                """
                session.run(query, id=row["id"], props=props)

            # 3. Ingest Relations
            relations_df = pd.read_csv(relations_path, keep_default_na=False)
            print(f"3. Nạp {len(relations_df)} Relations vào Neo4j...")
            
            for _, row in relations_df.iterrows():
                src = row["source_id"]
                tgt = row["target_id"]
                rel_type = row["relationship_type"]
                
                query = f"""
                MATCH (src {{id: $src}})
                MATCH (tgt {{id: $tgt}})
                MERGE (src)-[r:{rel_type}]->(tgt)
                SET r.source = $source,
                    r.evidence_quote = $evidence_quote,
                    r.confidence = toFloat($confidence),
                    r.verification_status = $verification_status,
                    r.data_origin = $data_origin
                """
                session.run(query, 
                            src=src, 
                            tgt=tgt, 
                            source=row["source"], 
                            evidence_quote=row["evidence_quote"], 
                            confidence=row["confidence"], 
                            verification_status=row["verification_status"], 
                            data_origin=row["data_origin"])
                            
        driver.close()
        print("=" * 70)
        print("[THÀNH CÔNG] Đã nạp toàn bộ Knowledge Graph vào Neo4j thành công!")
        print("=" * 70)
        
    except Exception as e:
        print("=" * 70)
        print(f"[CẢNH BÁO] Không thể kết nối tới máy chủ Neo4j: {e}")
        print("Vui lòng kiểm tra:")
        print("1. Máy chủ Neo4j / Docker container Neo4j đã được khởi động chưa.")
        print("2. Thông tin NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD trong file .env đã chính xác chưa.")
        print("Note: Điều này KHÔNG ảnh hưởng tới kết quả Obsidian Wiki đã được tạo thành công.")
        print("=" * 70)

if __name__ == "__main__":
    main()
