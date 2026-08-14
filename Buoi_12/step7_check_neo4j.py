"""
step7_check_neo4j.py
---------------------
BƯỚC 7: Kiểm tra cấu hình & kết nối Neo4j trước khi import
- Đọc cấu hình từ .env
- Mở driver, verify connectivity, chạy query đọc thử nghiệm
- Bảo mật: KHÔNG in password ra terminal
- Đóng driver đúng cách, chưa import dữ liệu.
"""

import os
import sys
import pathlib
from dotenv import load_dotenv

# Ensure UTF-8 output encoding for terminal
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = pathlib.Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

if not ENV_PATH.exists():
    ENV_PATH = BASE_DIR.parent / "buoi_11" / ".env"

load_dotenv(ENV_PATH)

def main():
    print("==========================================================")
    print("🚀 BẮT ĐẦU BƯỚC 7: KIỂM TRA KẾT NỐI NEO4J DATABASE")
    print("==========================================================\n")

    # 1. Read configuration from .env
    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_pass = os.environ.get("NEO4J_PASSWORD", "")
    neo4j_db = os.environ.get("NEO4J_DATABASE", "neo4j")

    print(f"1️⃣ Đọc cấu hình từ file .env ({ENV_PATH}):")
    print(f"   - NEO4J_URI     : {neo4j_uri}")
    print(f"   - NEO4J_USER    : {neo4j_user}")
    print(f"   - NEO4J_PASSWORD: {'**** (Đã mã hóa/ẩn)' if neo4j_pass else '❌ Chưa cấu hình'}")
    print(f"   - NEO4J_DATABASE: {neo4j_db}")

    if not neo4j_uri or not neo4j_user or not neo4j_pass:
        print("\n❌ Error: Cấu hình Neo4j chưa đầy đủ trong .env!")
        print("\n==========================================================")
        print("Neo4j connection: FAIL")
        print("==========================================================")
        return

    # 3. Use official neo4j Python driver
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("\n❌ Error: Package 'neo4j' chưa được cài đặt!")
        print("\n==========================================================")
        print("Neo4j connection: FAIL")
        print("==========================================================")
        return

    print("\n2️⃣ Khởi tạo Driver và Xác minh Kết nối (Verify Connectivity)...")
    driver = None
    connection_pass = False
    error_detail = ""

    try:
        # 4. Open driver
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
        
        # 5. Verify connectivity
        driver.verify_connectivity()
        print("   - verify_connectivity(): ✅ Thành công!")

        # 6. Run simple read query to verify database session
        print(f"\n3️⃣ Chạy truy vấn đọc thử nghiệm trên Database '{neo4j_db}'...")
        with driver.session(database=neo4j_db) as session:
            result = session.run("MATCH (n) RETURN count(n) AS total_nodes")
            record = result.single()
            node_count = record["total_nodes"] if record else 0
            print(f"   - Read Query Result: ✅ Database phản hồi tốt! (Hiện có {node_count} nodes)")

        connection_pass = True

    except Exception as e:
        error_detail = str(e)
        print(f"   - Kết nối thất bại: ❌ Lỗi: {error_detail}")

    finally:
        # 7. Close driver cleanly
        if driver:
            driver.close()
            print("\n4️⃣ Đóng Driver Neo4j đúng cách: ✅ Đã đóng.")

    # 8. Report PASS/FAIL
    print("\n==========================================================")
    if connection_pass:
        print("🎯 KẾT QUẢ BƯỚC 7: [PASS]")
        print("Neo4j connection: PASS")
        print(f"   - Database đang sử dụng: {neo4j_db}")
    else:
        print("❌ KẾT QUẢ BƯỚC 7: [FAIL]")
        print("Neo4j connection: FAIL")
        print(f"   - Lỗi chi tiết: {error_detail}")
    print("==========================================================")

if __name__ == "__main__":
    main()
