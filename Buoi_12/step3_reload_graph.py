"""
step3_reload_graph.py
---------------------
Bước 3: Tái nạp dữ liệu Đồ thị mở rộng vào Neo4j với tập dữ liệu đầy đủ 30 tài liệu (Bài thực hành 1)
bao gồm Phân tách HTML (Chunking), Tạo Vector nhúng (Embeddings) và Nạp các nút Document, Chunk,
quan hệ phân cấp (PART_OF, PARENT_OF, NEXT) cùng các quan hệ pháp lý liên tài liệu vào Neo4j.
"""

import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, List, Dict

from neo4j import GraphDatabase
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Set CSV field size limit
try:
    csv.field_size_limit(2147483647)
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent
MEDIUM_DIR = BASE_DIR / "medium"

# Add medium dir to sys.path to import html_chunking and load_to_neo4j
if str(MEDIUM_DIR) not in sys.path:
    sys.path.insert(0, str(MEDIUM_DIR))

import html_chunking
import load_to_neo4j

ENV_PATH = BASE_DIR / ".env"
if not ENV_PATH.exists():
    ENV_PATH = BASE_DIR.parent / "Buoi_11" / ".env"

load_dotenv(ENV_PATH)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "abcd1234")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "kb-hops")

PREDICTED_PATH = BASE_DIR / "predicted_relationships.csv"
GROUND_TRUTH_PATH = BASE_DIR / "medium" / "relationships.csv"
LAB_RELATIONSHIPS_PATH = BASE_DIR / "lab" / "relationships.csv"
LAB_METADATA_PATH = BASE_DIR / "lab" / "metadata.csv"
LAB_CONTENT_PATH = BASE_DIR / "lab" / "content.csv"
LAB_CHUNKS_PATH = BASE_DIR / "lab" / "lab_chunks.json"
EMBEDDING_MODEL_NAME = "thuannc/vi-distilled-msmarco-MiniLM-L12-cos-v5"


def update_lab_relationships():
    """Cập nhật tệp lab/relationships.csv bằng sự kết hợp giữa nhãn chuẩn và dự đoán của LLM."""
    all_rels = {}
    
    # Load ground truth
    if GROUND_TRUTH_PATH.exists():
        with open(GROUND_TRUTH_PATH, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                key = (r["doc_id"].strip(), r["other_doc_id"].strip())
                all_rels[key] = {
                    "doc_id": r["doc_id"].strip(),
                    "other_doc_id": r["other_doc_id"].strip(),
                    "relationship": r.get("relationship", "").strip(),
                    "relationship_type": r.get("relationship_type", "").strip()
                }
                
    # Load predicted
    if PREDICTED_PATH.exists():
        with open(PREDICTED_PATH, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                key = (r["doc_id"].strip(), r["other_doc_id"].strip())
                if key not in all_rels:
                    all_rels[key] = {
                        "doc_id": r["doc_id"].strip(),
                        "other_doc_id": r["other_doc_id"].strip(),
                        "relationship": r.get("relationship", "").strip(),
                        "relationship_type": r.get("relationship_type", "").strip()
                    }
                    
    # Write to lab/relationships.csv
    with open(LAB_RELATIONSHIPS_PATH, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["doc_id", "other_doc_id", "relationship", "relationship_type"])
        writer.writeheader()
        writer.writerows(list(all_rels.values()))
        
    print(f"✅ Đã cập nhật tệp {LAB_RELATIONSHIPS_PATH.name} với tổng số {len(all_rels)} quan hệ.")
    return list(all_rels.values())


def generate_chunks_and_embeddings():
    """Phân tách HTML (Chunking) và tạo Vector Embeddings cho 30 tài liệu trong lab/content.csv."""
    print(f"🚀 [Quy trình Bài 1] Đang phân tách cấu trúc HTML và tạo Vector Embeddings bằng mô hình '{EMBEDDING_MODEL_NAME}'...")
    
    metadata = html_chunking.load_metadata_csv(str(LAB_METADATA_PATH))
    tokenizer, model = html_chunking.load_embedding_model(EMBEDDING_MODEL_NAME, device="cpu")
    
    results = []
    total_docs = 0
    total_chunks = 0
    
    for doc_id, html_text in html_chunking.load_content_csv(str(LAB_CONTENT_PATH)):
        title = metadata.get(doc_id, {}).get("title")
        root, chunks = html_chunking.build_chunks(str(doc_id), html_text, title)
        
        # Embed chunks
        html_chunking.attach_embeddings(chunks, tokenizer=tokenizer, model=model, batch_size=32)
        
        chunk_records = []
        for chunk in chunks:
            payload = chunk.__dict__.copy()
            if hasattr(chunk, "embedding"):
                payload["embedding"] = getattr(chunk, "embedding")
            chunk_records.append(payload)
            
        results.append({"document": root, "chunks": chunk_records})
        total_docs += 1
        total_chunks += len(chunk_records)
        print(f"  - Đã xử lý Văn bản {doc_id}: {len(chunk_records)} chunks")
        
    # Save to json file
    with open(LAB_CHUNKS_PATH, "w", encoding="utf-8") as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)
        
    print(f"✅ Đã hoàn thành chunking và nhúng vector cho {total_docs} văn bản ({total_chunks} chunks). Tệp lưu tại: {LAB_CHUNKS_PATH.name}")
    return LAB_CHUNKS_PATH


def main():
    print("--- BƯỚC 3: TÁI NẠP DỮ LIỆU ĐỒ THỊ MỞ RỘNG (30 VĂN BẢN) ---")
    update_lab_relationships()
    chunks_json_path = generate_chunks_and_embeddings()
    
    print(f"👉 Đang tiến hành nạp toàn bộ Đồ thị tri thức 30 tài liệu vào Neo4j (Database: {NEO4J_DATABASE})...")
    load_to_neo4j.load_to_neo4j(
        uri=NEO4J_URI,
        user=NEO4J_USER,
        password=NEO4J_PASSWORD,
        database=NEO4J_DATABASE,
        chunks_json=str(chunks_json_path),
        metadata_csv=str(LAB_METADATA_PATH),
        relationships_csv=str(LAB_RELATIONSHIPS_PATH),
        create_database=False,
    )
    print("🎉 TÁI NẠP THÀNH CÔNG ĐỒ THỊ TRI THỨC HOÀN CHỈNH CHO 30 TÀI LIỆU VÀO NEO4J!")


if __name__ == "__main__":
    main()

