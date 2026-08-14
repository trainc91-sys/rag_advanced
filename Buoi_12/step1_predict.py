"""
step1_predict.py
----------------
Bước 1: Phân tích Dữ liệu và Dự đoán Mối quan hệ giữa các Văn bản bằng LLM (Gemini API).

Đọc 30 tài liệu từ lab/metadata.csv & lab/content.csv, phân tích trích xuất quan hệ
pháp lý giữa các cặp tài liệu (CAN_CU, THAY_THE, SUA_DOI_BO_SUNG, HOP_NHAT, VAN_BAN_BO_SUNG).
"""

import csv
import sys
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any

# Increase CSV field size limit for large content.csv fields
csv.field_size_limit(2147483647)

import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
if not ENV_PATH.exists():
    ENV_PATH = BASE_DIR.parent / "Buoi_11" / ".env"

load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    # Try reading from Buoi_11 .env
    alt_env = BASE_DIR.parent / "Buoi_11" / ".env"
    if alt_env.exists():
        load_dotenv(alt_env)
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3.5-flash-lite")

LAB_METADATA_PATH = BASE_DIR / "lab" / "metadata.csv"
LAB_CONTENT_PATH = BASE_DIR / "lab" / "content.csv"
PREDICTED_OUTPUT_PATH = BASE_DIR / "predicted_relationships.csv"


def load_metadata(filepath: Path) -> List[Dict[str, str]]:
    documents = []
    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            documents.append(row)
    return documents


def load_content_preambles(filepath: Path, max_length: int = 25000) -> Dict[str, str]:
    preambles = {}
    if not filepath.exists():
        return preambles
    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc_id = row.get("id") or row.get("doc_id")
            content = row.get("content", "") or row.get("html", "")
            # Clean basic HTML tags
            clean_text = re.sub(r"<[^>]+>", " ", content)
            clean_text = " ".join(clean_text.split())
            preambles[doc_id] = clean_text[:max_length]
    return preambles


def extract_potential_references(docs: List[Dict[str, str]], preambles: Dict[str, str] = None) -> List[Dict[str, Any]]:
    """Phát hiện các cặp tài liệu tiềm năng thông qua việc trích xuất số hiệu, năm ban hành và cụm từ tham chiếu."""
    if preambles is None:
        preambles = {}
    doc_map = {d["id"]: d for d in docs}
    
    # Map so_ky_hieu and extracted number patterns to doc_id
    patterns = {}
    for d in docs:
        doc_id = d["id"]
        skh = d.get("so_ky_hieu", "").strip().lower()
        if skh:
            patterns[skh] = doc_id
            # Extract number pattern like 73/2016, 46/2010, 135/2015, 17/2023
            match = re.search(r"\d{1,4}/\d{4}", skh)
            if match:
                patterns[match.group(0)] = doc_id
                
        title = d.get("title", "").lower()
        # Extract legal document names
        if "ngân hàng nhà nước" in title and ("luật" in title or "46/2010" in title):
            patterns["ngân hàng nhà nước"] = doc_id
            patterns["46/2010"] = doc_id
        if "hợp tác xã" in title and ("luật" in title or "17/2023" in title):
            patterns["hợp tác xã"] = doc_id
            patterns["17/2023"] = doc_id
        if "kinh doanh bảo hiểm" in title and "73/2016" in title:
            patterns["73/2016"] = doc_id
        if "135/2015" in title:
            patterns["135/2015"] = doc_id
        if "56/2024" in title:
            patterns["56/2024"] = doc_id
        if "63/2025" in title:
            patterns["63/2025"] = doc_id
        if "01/2014" in title:
            patterns["01/2014"] = doc_id
        if "41/2016" in title:
            patterns["41/2016"] = doc_id
            
    pairs = []
    
    for d in docs:
        doc_id = d["id"]
        title = d.get("title", "")
        text = preambles.get(doc_id, "").lower()
        full_doc_str = (title + " " + text).lower()
        
        for key_pattern, other_id in patterns.items():
            if doc_id == other_id:
                continue
            if key_pattern in full_doc_str:
                pairs.append({
                    "source_id": doc_id,
                    "target_id": other_id,
                    "source_title": title,
                    "target_title": doc_map[other_id].get("title", ""),
                    "reason": f"Từ khóa/Mã số '{key_pattern}' xuất hiện trong văn bản."
                })
    return pairs


def predict_relationship_with_llm(doc_a: Dict[str, str], doc_b: Dict[str, str], text_a: str = "", text_b: str = "") -> Dict[str, Any]:
    prompt = f"""Bạn là một chuyên gia phân tích pháp lý Việt Nam.
Hãy xác định xem giữa Văn bản A và Văn bản B dưới đây có mối quan hệ pháp lý nào trực tiếp không.

VĂN BẢN A:
- ID: {doc_a.get('id')}
- Tiêu đề: {doc_a.get('title')}
- Số ký hiệu: {doc_a.get('so_ky_hieu')}
- Loại văn bản: {doc_a.get('loai_van_ban')}
- Đoạn mở đầu: {text_a[:500]}

VĂN BẢN B:
- ID: {doc_b.get('id')}
- Tiêu đề: {doc_b.get('title')}
- Số ký hiệu: {doc_b.get('so_ky_hieu')}
- Loại văn bản: {doc_b.get('loai_van_ban')}
- Đoạn mở đầu: {text_b[:500]}

Các loại mối quan hệ có thể có:
1. CAN_CU (Căn cứ): Văn bản A ban hành dựa trên căn cứ của Văn bản B (hoặc ngược lại).
2. THAY_THE (Thay thế): Văn bản A thay thế, bãi bỏ Văn bản B.
3. SUA_DOI_BO_SUNG (Sửa đổi, bổ sung): Văn bản A sửa đổi, bổ sung cho Văn bản B.
4. HOP_NHAT (Hợp nhất): Văn bản hợp nhất A được hợp nhất từ/với Văn bản B.
5. VAN_BAN_BO_SUNG (Văn bản bổ sung): Văn bản A là văn bản bổ sung cho Văn bản B.
6. NONE: Không có quan hệ trực tiếp.

Hãy trả về kết quả dưới định dạng JSON duy nhất như sau (không kèm markdown):
{{
  "has_relationship": true / false,
  "source_doc_id": "{doc_a.get('id')}",
  "target_doc_id": "{doc_b.get('id')}",
  "relationship_vietnamese": "Sửa đổi, bổ sung" / "Căn cứ" / "Thay thế" / "Hợp nhất" / "Văn bản bổ sung" / "Không",
  "relationship_type": "SUA_DOI_BO_SUNG" / "CAN_CU" / "THAY_THE" / "HOP_NHAT" / "VAN_BAN_BO_SUNG" / "NONE"
}}
"""
    try:
        res = model.generate_content(prompt)
        text = res.text.strip()
        # Parse JSON
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except Exception as e:
        print(f"Lỗi khi gọi LLM cho cặp ({doc_a.get('id')}, {doc_b.get('id')}): {e}")
        return {"has_relationship": False, "relationship_type": "NONE"}


def main():
    print("--- BƯỚC 1: DỰ ĐOÁN MỐI QUAN HỆ BẰNG LLM ---")
    docs = load_metadata(LAB_METADATA_PATH)
    preambles = load_content_preambles(LAB_CONTENT_PATH)
    print(f"Đã tải {len(docs)} tài liệu từ {LAB_METADATA_PATH.name}")
    
    doc_map = {d["id"]: d for d in docs}
    
    # 1. Trích xuất ứng viên bằng tham chiếu chéo
    pairs = extract_potential_references(docs, preambles)
    print(f"Phát hiện {len(pairs)} cặp tài liệu ứng viên tiềm năng có tham chiếu số hiệu.")
    
    predictions = []
    
    # 2. Duyệt qua các cặp tài liệu và gọi LLM phân tích
    seen_pairs = set()
    for p in pairs:
        pair_key = (p["source_id"], p["target_id"])
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)
        
        doc_a = doc_map[p["source_id"]]
        doc_b = doc_map[p["target_id"]]
        
        result = predict_relationship_with_llm(
            doc_a, doc_b, 
            text_a=preambles.get(p["source_id"], ""), 
            text_b=preambles.get(p["target_id"], "")
        )
        
        if result.get("has_relationship") and result.get("relationship_type") != "NONE":
            print(f"✅ Phát hiện: {p['source_id']} -> {p['target_id']} [{result.get('relationship_type')}] ({result.get('relationship_vietnamese')})")
            predictions.append({
                "doc_id": result.get("source_doc_id", p["source_id"]),
                "other_doc_id": result.get("target_doc_id", p["target_id"]),
                "relationship": result.get("relationship_vietnamese", ""),
                "relationship_type": result.get("relationship_type", "")
            })

    # Ghi file kết quả dự đoán
    with open(PREDICTED_OUTPUT_PATH, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["doc_id", "other_doc_id", "relationship", "relationship_type"])
        writer.writeheader()
        writer.writerows(predictions)
        
    print(f"\nĐã lưu {len(predictions)} quan hệ dự đoán vào: {PREDICTED_OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
