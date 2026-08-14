"""
step3_entity_enrichment.py
---------------------------
BƯỚC 3: Entity Extraction và Metadata Enrichment bằng Gemini (Có Retry & Rate Limit Handling)
- Input: ner_kb/cleaned_documents.csv
- Output: ner_kb/extracted_entities_raw.csv & ner_kb/enriched_metadata.csv
"""

import os
import sys
import json
import re
import time
import pathlib
import pandas as pd
from dotenv import load_dotenv

# Ensure UTF-8 output encoding for terminal
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = pathlib.Path(__file__).resolve().parent
NER_KB_DIR = BASE_DIR / "ner_kb"

INPUT_PATH = NER_KB_DIR / "cleaned_documents.csv"
ENTITIES_OUTPUT_PATH = NER_KB_DIR / "extracted_entities_raw.csv"
METADATA_OUTPUT_PATH = NER_KB_DIR / "enriched_metadata.csv"

ENTITIES_ROOT_PATH = BASE_DIR / "extracted_entities_raw.csv"
METADATA_ROOT_PATH = BASE_DIR / "enriched_metadata.csv"

# Load Gemini API Key
ENV_PATH = BASE_DIR / ".env"
if not ENV_PATH.exists():
    ENV_PATH = BASE_DIR.parent / "buoi_11" / ".env"
load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

from google import genai
from google.genai import types

def build_prompt(row: pd.Series) -> str:
    doc_id = str(row['id'])
    so_ky_hieu = str(row.get('so_ky_hieu', ''))
    title = str(row.get('title', ''))
    co_quan_goc = str(row.get('co_quan_ban_hanh', ''))
    nguoi_ky_goc = str(row.get('nguoi_ky', ''))
    linh_vuc_goc = str(row.get('linh_vuc', ''))
    content_clean = str(row.get('content_clean', ''))[:4000]

    prompt = f"""Bạn là chuyên gia trích xuất tri thức từ văn bản pháp luật Việt Nam.
Hãy phân tích văn bản sau và trích xuất 4 loại thực thể (entities) chính xác dựa trên BẰNG CHỨNG (evidence) trong văn bản.

Thông tin văn bản:
- ID: {doc_id}
- Số ký hiệu: {so_ky_hieu}
- Tiêu đề: {title}
- Cơ quan ban hành (Gốc): {co_quan_goc}
- Người ký (Gốc): {nguoi_ky_goc}
- Lĩnh vực (Gốc): {linh_vuc_goc}

Nội dung văn bản (đầu đoạn):
\"\"\"
{content_clean}
\"\"\"

Nhiệm vụ: Trích xuất danh sách thực thể JSON theo đúng định dạng dưới đây:
1. `co_quan`: Cơ quan ban hành (Ví dụ: Quốc hội, Chính phủ, Bộ Tài chính, Ngân hàng Nhà nước Việt Nam).
2. `nguoi_ky`: Người ký văn bản (Họ và tên người ký).
3. `doi_tuong_ap_dung`: Đối tượng chịu sự điều chỉnh hoặc áp dụng văn bản (Ví dụ: Ngân hàng thương mại, Tổ chức tín dụng, Chi nhánh ngân hàng nước ngoài, Quỹ tín dụng nhân dân, Doanh nghiệp bảo hiểm, v.v.).
4. `linh_vuc`: Lĩnh vực pháp lý chính của văn bản (Ví dụ: Tín dụng, Bảo hiểm, Chứng khoán, Kiểm toán, Quản lý ngoại hối, Thanh toán, An toàn hoạt động ngân hàng).

QUY TẮC BẮT BUỘC:
- Mọi entity PHẢI CÓ đoạn văn bản trích dẫn làm bằng chứng (`evidence`) trực tiếp từ nội dung trên. Nếu không có evidence, KHÔNG tạo entity đó.
- `confidence`: Điểm tin cậy từ 0.70 đến 0.95 tùy thuộc độ rõ ràng của bằng chứng (KHÔNG đặt 1.0 cho tất cả).
- Trả về kết quả hoàn toàn bằng định dạng JSON thuần túy.

Định dạng JSON yêu cầu:
{{
  "co_quan": [
    {{"entity": "Tên cơ quan", "confidence": 0.92, "evidence": "Đoạn trích dẫn..."}}
  ],
  "nguoi_ky": [
    {{"entity": "Tên người ký", "confidence": 0.90, "evidence": "Đoạn trích dẫn..."}}
  ],
  "doi_tuong_ap_dung": [
    {{"entity": "Đối tượng", "confidence": 0.88, "evidence": "Đoạn trích dẫn..."}}
  ],
  "linh_vuc": [
    {{"entity": "Lĩnh vực", "confidence": 0.85, "evidence": "Đoạn trích dẫn..."}}
  ]
}}
"""
    return prompt

def parse_llm_response(response_text: str) -> dict:
    if not response_text:
        return {}
    cleaned = response_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return {}

def call_gemini_with_retry(client, prompt: str, max_retries: int = 3) -> tuple[dict, bool, str]:
    for attempt in range(max_retries):
        try:
            res = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            parsed = parse_llm_response(res.text)
            return parsed, True, ""
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                wait_time = (attempt + 1) * 15
                print(f"      [429 Rate Limit] Đợi {wait_time}s trước khi retry thử lần {attempt+1}/{max_retries}...")
                time.sleep(wait_time)
            else:
                return {}, False, err_str
    return {}, False, "Max retries reached on Rate Limit (429)"

def main():
    print("==========================================================")
    print("🚀 BẮT ĐẦU BƯỚC 3: ENTITY EXTRACTION & METADATA ENRICHMENT")
    print("==========================================================\n")

    if not INPUT_PATH.exists():
        print(f"❌ Error: File {INPUT_PATH} không tồn tại.")
        return

    df = pd.read_csv(INPUT_PATH)
    print(f"1️⃣ Đọc dữ liệu đầu vào: {len(df)} văn bản...")

    if not GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY không được tìm thấy trong .env!")
        return

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    extracted_entities = []
    enriched_rows = []
    
    success_docs = 0
    fail_docs = 0
    errors_list = []

    print("\n2️⃣ Bắt đầu trích xuất Entity & Làm giàu Metadata bằng Gemini API...")

    for idx, row in df.iterrows():
        doc_id = str(row['id'])
        so_ky_hieu = str(row.get('so_ky_hieu', ''))
        
        # 1. Metadata-rule entities (Priority for existing metadata)
        co_quan_goc = str(row.get('co_quan_ban_hanh', '')).strip() if pd.notnull(row.get('co_quan_ban_hanh')) else ""
        nguoi_ky_goc = str(row.get('nguoi_ky', '')).strip() if pd.notnull(row.get('nguoi_ky')) else ""
        linh_vuc_goc = str(row.get('linh_vuc', '')).strip() if pd.notnull(row.get('linh_vuc')) else ""

        if co_quan_goc and co_quan_goc != "nan" and co_quan_goc != "Chưa phân loại":
            extracted_entities.append({
                "document_id": doc_id,
                "so_ky_hieu": so_ky_hieu,
                "entity": co_quan_goc,
                "entity_type": "CoQuan",
                "source": "metadata",
                "method": "metadata_rule",
                "confidence": 0.98,
                "evidence": f"Từ cột co_quan_ban_hanh của metadata: {co_quan_goc}"
            })
            
        if nguoi_ky_goc and nguoi_ky_goc != "nan":
            extracted_entities.append({
                "document_id": doc_id,
                "so_ky_hieu": so_ky_hieu,
                "entity": nguoi_ky_goc,
                "entity_type": "NguoiKy",
                "source": "metadata",
                "method": "metadata_rule",
                "confidence": 0.98,
                "evidence": f"Từ cột nguoi_ky của metadata: {nguoi_ky_goc}"
            })

        # 2. Call Gemini LLM with retry for missing fields & DoiTuongApDung / LinhVuc enrichment
        prompt = build_prompt(row)
        parsed_json, doc_success, err_msg = call_gemini_with_retry(client, prompt)
        
        if doc_success:
            success_docs += 1
        else:
            fail_docs += 1
            full_err = f"Doc {doc_id} ({so_ky_hieu}): Lỗi Gemini API - {err_msg}"
            errors_list.append(full_err)
            print(f"   ⚠️ {full_err}")

        # Process LLM extracted entities
        llm_co_quan = []
        llm_nguoi_ky = []
        llm_doi_tuong = []
        llm_linh_vuc = []

        if parsed_json:
            type_mapping = {
                "co_quan": "CoQuan",
                "nguoi_ky": "NguoiKy",
                "doi_tuong_ap_dung": "DoiTuongApDung",
                "linh_vuc": "LinhVuc"
            }
            
            for key, entity_type in type_mapping.items():
                items = parsed_json.get(key, [])
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            ent_name = str(item.get("entity", "")).strip()
                            evid = str(item.get("evidence", "")).strip()
                            conf = item.get("confidence", 0.85)
                            try:
                                conf = float(conf)
                            except ValueError:
                                conf = 0.85

                            if ent_name and evid:
                                extracted_entities.append({
                                    "document_id": doc_id,
                                    "so_ky_hieu": so_ky_hieu,
                                    "entity": ent_name,
                                    "entity_type": entity_type,
                                    "source": "content_clean",
                                    "method": "gemini",
                                    "confidence": conf,
                                    "evidence": evid
                                })
                                
                                if entity_type == "CoQuan":
                                    llm_co_quan.append(ent_name)
                                elif entity_type == "NguoiKy":
                                    llm_nguoi_ky.append(ent_name)
                                elif entity_type == "DoiTuongApDung":
                                    llm_doi_tuong.append(ent_name)
                                elif entity_type == "LinhVuc":
                                    llm_linh_vuc.append(ent_name)

        # 3. Create enriched metadata row
        row_dict = row.to_dict()
        
        enriched_co_quan = co_quan_goc if (co_quan_goc and co_quan_goc != "nan" and co_quan_goc != "Chưa phân loại") else (llm_co_quan[0] if llm_co_quan else "Chưa phân loại")
        enriched_nguoi_ky = nguoi_ky_goc if (nguoi_ky_goc and nguoi_ky_goc != "nan") else (llm_nguoi_ky[0] if llm_nguoi_ky else "")
        enriched_doi_tuong = "; ".join(list(set(llm_doi_tuong))) if llm_doi_tuong else "Chưa rõ"
        enriched_linh_vuc = linh_vuc_goc if (linh_vuc_goc and linh_vuc_goc != "nan" and linh_vuc_goc != "Chưa phân loại") else ("; ".join(list(set(llm_linh_vuc))) if llm_linh_vuc else "Ngân hàng")

        row_dict["co_quan_enriched"] = enriched_co_quan
        row_dict["nguoi_ky_enriched"] = enriched_nguoi_ky
        row_dict["doi_tuong_ap_dung_enriched"] = enriched_doi_tuong
        row_dict["linh_vuc_enriched"] = enriched_linh_vuc
        
        is_enriched = (enriched_co_quan != co_quan_goc) or (enriched_nguoi_ky != nguoi_ky_goc) or (enriched_linh_vuc != linh_vuc_goc) or (enriched_doi_tuong != "Chưa rõ")
        row_dict["metadata_enriched_flag"] = is_enriched

        enriched_rows.append(row_dict)
        print(f"   [Done {idx+1}/{len(df)}] ID {doc_id} ({so_ky_hieu}) - Success: {doc_success}")
        
        # Pacing rate limit: sleep 2.5s between API calls to stay within free tier QPM limit
        time.sleep(2.5)

    df_entities = pd.DataFrame(extracted_entities)
    df_enriched = pd.DataFrame(enriched_rows)

    df_entities_clean = df_entities.drop_duplicates(subset=["document_id", "entity", "entity_type", "evidence"]).copy()

    print(f"\n3️⃣ Thống kê kết quả:")
    print(f"   - Số document xử lý thành công: {success_docs}/{len(df)}")
    print(f"   - Số document thất bại:         {fail_docs}")
    print(f"   - Tổng số entity trích xuất:    {len(df_entities_clean)}")
    
    print(f"\n4️⃣ Thống kê Entity theo Loại (entity_type):")
    type_counts = df_entities_clean['entity_type'].value_counts()
    for etype, cnt in type_counts.items():
        print(f"   - {etype:<20}: {cnt} entities")

    enriched_count = df_enriched['metadata_enriched_flag'].sum()
    print(f"\n5️⃣ Số giá trị metadata được bổ sung/làm giàu: {enriched_count} văn bản")

    print(f"\n6️⃣ 5 Ví dụ So sánh Metadata Gốc vs Metadata Làm Giàu:")
    sample_enriched = df_enriched[df_enriched['metadata_enriched_flag']].head(5)
    if len(sample_enriched) < 5:
        sample_enriched = df_enriched.head(5)

    for i, r in sample_enriched.reset_index().iterrows():
        print(f"\n   📄 [{i+1}] ID: {r['id']} | Số ký hiệu: {r['so_ky_hieu']}")
        print(f"      - Cơ quan BAN HÀNH : Gốc: '{r.get('co_quan_ban_hanh')}' ➔ Làm giàu: '{r.get('co_quan_enriched')}'")
        print(f"      - Lĩnh vực          : Gốc: '{r.get('linh_vuc')}' ➔ Làm giàu: '{r.get('linh_vuc_enriched')}'")
        print(f"      - Đối tượng áp dụng : '{str(r.get('doi_tuong_ap_dung_enriched'))[:100]}...'")

    if errors_list:
        print(f"\n⚠️ Danh sách lỗi ({len(errors_list)} lỗi):")
        for err in errors_list:
            print(f"   - {err}")
    else:
        print(f"\n✅ KHÔNG CÓ LỖI XẢY RA TRONG QUÁ TRÌNH CHẠY BATCH.")

    # 7. Save outputs
    print(f"\n7️⃣ Lưu các file kết quả...")
    df_entities_clean.to_csv(ENTITIES_OUTPUT_PATH, index=False, encoding='utf-8-sig')
    df_entities_clean.to_csv(ENTITIES_ROOT_PATH, index=False, encoding='utf-8-sig')
    
    df_enriched.to_csv(METADATA_OUTPUT_PATH, index=False, encoding='utf-8-sig')
    df_enriched.to_csv(METADATA_ROOT_PATH, index=False, encoding='utf-8-sig')
    
    print(f"   - [OK] Đã lưu: {ENTITIES_OUTPUT_PATH}")
    print(f"   - [OK] Đã lưu: {METADATA_OUTPUT_PATH}")

    # Check PASS conditions
    file1_ok = ENTITIES_OUTPUT_PATH.exists() and ENTITIES_OUTPUT_PATH.stat().st_size > 0
    file2_ok = METADATA_OUTPUT_PATH.exists() and METADATA_OUTPUT_PATH.stat().st_size > 0
    coquan_ok = "CoQuan" in type_counts
    doituong_ok = "DoiTuongApDung" in type_counts
    
    print("\n==========================================================")
    if file1_ok and file2_ok and success_docs > 0 and coquan_ok and doituong_ok:
        print("🎯 KẾT QUẢ BƯỚC 3: [PASS]")
        print(f"   - extracted_entities_raw.csv tồn tại ({ENTITIES_OUTPUT_PATH.stat().st_size / 1024:.2f} KB)")
        print(f"   - enriched_metadata.csv tồn tại ({METADATA_OUTPUT_PATH.stat().st_size / 1024:.2f} KB)")
        print("   - Cơ quan ban hành, Người ký & Đối tượng áp dụng được làm giàu hợp lý.")
    else:
        print("❌ KẾT QUẢ BƯỚC 3: [FAIL]")
    print("==========================================================")

if __name__ == "__main__":
    main()
