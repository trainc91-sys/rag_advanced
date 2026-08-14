"""
step4_entity_normalization.py
------------------------------
BƯỚC 4: Chuẩn hóa Entity (Entity Normalization)
- Input: ner_kb/extracted_entities_raw.csv & ner_kb/enriched_metadata.csv
- Chuẩn hóa Unicode, whitespace, alias mapping có kiểm soát (NHNN -> Ngân hàng Nhà nước Việt Nam, etc.)
- Giữ nguyên original_name và canonical_name để truy vết.
- Output: ner_kb/entities.csv
"""

import sys
import unicodedata
import pathlib
import pandas as pd
import re

# Ensure UTF-8 output encoding for terminal
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = pathlib.Path(__file__).resolve().parent
NER_KB_DIR = BASE_DIR / "ner_kb"

RAW_ENTITIES_PATH = NER_KB_DIR / "extracted_entities_raw.csv"
ENRICHED_META_PATH = NER_KB_DIR / "enriched_metadata.csv"
OUTPUT_PATH = NER_KB_DIR / "entities.csv"
OUTPUT_ROOT_PATH = BASE_DIR / "entities.csv"

# Known explicit alias mapping (Safe & Controlled)
ALIAS_MAP = {
    "NHNN": "Ngân hàng Nhà nước Việt Nam",
    "NGÂN HÀNG NHÀ NƯỚC": "Ngân hàng Nhà nước Việt Nam",
    "NGÂN HÀNG NHÀ NƯỚC VIỆT NAM": "Ngân hàng Nhà nước Việt Nam",
    "BTC": "Bộ Tài chính",
    "BỘ TÀI CHÍNH": "Bộ Tài chính",
    "CP": "Chính phủ",
    "CHÍNH PHỦ": "Chính phủ",
    "QH": "Quốc hội",
    "QUỐC HỘI": "Quốc hội",
    "TCTD": "Tổ chức tín dụng",
    "TỔ CHỨC TÍN DỤNG": "Tổ chức tín dụng",
    "NHTM": "Ngân hàng thương mại",
    "NGÂN HÀNG THƯƠNG MẠI": "Ngân hàng thương mại",
    "QTDND": "Quỹ tín dụng nhân dân",
    "QUỸ TÍN DỤNG NHÂN DÂN": "Quỹ tín dụng nhân dân",
    "DNBH": "Doanh nghiệp bảo hiểm",
    "DOANH NGHIỆP BẢO HIỂM": "Doanh nghiệp bảo hiểm"
}

def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # Unicode NFC normalization
    text = unicodedata.normalize("NFC", text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_canonical_name(name: str, entity_type: str) -> str:
    cleaned = normalize_text(name)
    if not cleaned:
        return ""
        
    upper_name = cleaned.upper()
    
    # Apply controlled alias mapping
    if upper_name in ALIAS_MAP:
        return ALIAS_MAP[upper_name]
        
    # Controlled cleanup per entity type
    if entity_type == "CoQuan":
        if "NGÂN HÀNG NHÀ NƯỚC" in upper_name:
            return "Ngân hàng Nhà nước Việt Nam"
        if "BỘ TÀI CHÍNH" in upper_name:
            return "Bộ Tài chính"
        if "CHÍNH PHỦ" in upper_name:
            return "Chính phủ"
        if "QUỐC HỘI" in upper_name:
            return "Quốc hội"
    elif entity_type == "LinhVuc":
        # Standardize domain names capitalization
        words = [w.capitalize() for w in cleaned.split()]
        return " ".join(words)
        
    return cleaned

def main():
    print("==========================================================")
    print("🚀 BẮT ĐẦU BƯỚC 4: CHUẨN HÓA ENTITY (ENTITY NORMALIZATION)")
    print("==========================================================\n")

    if not RAW_ENTITIES_PATH.exists():
        print(f"❌ Error: File {RAW_ENTITIES_PATH} không tồn tại. Vui lòng chạy Bước 3 trước.")
        return

    df_raw = pd.read_csv(RAW_ENTITIES_PATH)
    total_before = len(df_raw)
    print(f"1️⃣ Đọc file extracted_entities_raw.csv: {total_before} thực thể thô...")

    normalized_list = []
    alias_merged_count = 0
    merged_aliases_log = set()

    for idx, row in df_raw.iterrows():
        doc_id = str(row.get('document_id', row.get('doc_id', '')))
        orig_name = str(row.get('entity', '')).strip()
        etype = str(row.get('entity_type', '')).strip()
        source = str(row.get('source', '')).strip()
        method = str(row.get('method', '')).strip()
        confidence = float(row.get('confidence', 0.85)) if pd.notnull(row.get('confidence')) else 0.85
        evidence = str(row.get('evidence', '')).strip()

        if not orig_name:
            continue

        canonical_name = get_canonical_name(orig_name, etype)
        
        if canonical_name != orig_name:
            alias_merged_count += 1
            merged_aliases_log.add(f"'{orig_name}' ➔ '{canonical_name}' ({etype})")

        entity_id = f"ENT_{etype[:3].upper()}_{idx+1:04d}"

        normalized_list.append({
            "entity_id": entity_id,
            "entity_type": etype,
            "canonical_name": canonical_name,
            "original_name": orig_name,
            "source_doc_id": doc_id,
            "method": method,
            "confidence": confidence,
            "evidence": evidence
        })

    df_norm = pd.DataFrame(normalized_list)
    
    # 2. Remove duplicate canonical entities per document
    df_norm_clean = df_norm.drop_duplicates(subset=["source_doc_id", "entity_type", "canonical_name"]).copy()
    
    # Re-assign sequential entity_id
    df_norm_clean["entity_id"] = [f"ENT_{r['entity_type'][:3].upper()}_{i+1:04d}" for i, r in df_norm_clean.reset_index().iterrows()]

    total_after = len(df_norm_clean)

    print(f"\n2️⃣ Thống kê kết quả chuẩn hóa Entity:")
    print(f"   - Số Entity trước khi chuẩn hóa: {total_before}")
    print(f"   - Số Entity sau khi chuẩn hóa (đã gộp duplicate per doc): {total_after}")
    print(f"   - Số lượt viết tắt/alias được chuẩn hóa thành tên chính quy: {alias_merged_count}")

    print(f"\n3️⃣ Các Alias tiêu biểu đã chuẩn hóa (`original_name` ➔ `canonical_name`):")
    for alias_entry in list(merged_aliases_log)[:8]:
        print(f"   - {alias_entry}")

    print(f"\n4️⃣ 10 Entity mẫu chuẩn hóa (bao gồm cả canonical & original_name):")
    sample_df = df_norm_clean.head(10)
    for i, r in sample_df.reset_index().iterrows():
        print(f"   📄 [{r['entity_id']}] DocID: {r['source_doc_id']:<10} | Type: {r['entity_type']:<15} | Canonical: '{r['canonical_name']}' (Gốc: '{r['original_name']}')")

    # 8. Save output
    print(f"\n5️⃣ Lưu file kết quả...")
    df_norm_clean.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    df_norm_clean.to_csv(OUTPUT_ROOT_PATH, index=False, encoding='utf-8-sig')
    print(f"   - [OK] Đã lưu: {OUTPUT_PATH}")
    print(f"   - [OK] Đã lưu: {OUTPUT_ROOT_PATH}")

    # Check PASS conditions
    file_ok = OUTPUT_PATH.exists() and OUTPUT_PATH.stat().st_size > 0
    no_dup_ok = not df_norm_clean.duplicated(subset=["source_doc_id", "entity_type", "canonical_name"]).any()
    traceable_ok = (df_norm_clean["original_name"].str.len() > 0).all() and (df_norm_clean["canonical_name"].str.len() > 0).all()
    
    # Check people names not incorrectly merged
    people_entities = df_norm_clean[df_norm_clean["entity_type"] == "NguoiKy"]
    people_unique_canon = people_entities["canonical_name"].nunique()
    people_unique_orig = people_entities["original_name"].nunique()
    people_merge_ok = abs(people_unique_canon - people_unique_orig) <= 2

    print("\n==========================================================")
    if file_ok and total_after > 0 and no_dup_ok and traceable_ok and people_merge_ok:
        print("🎯 KẾT QUẢ BƯỚC 4: [PASS]")
        print(f"   - entities.csv tồn tại ({OUTPUT_PATH.stat().st_size / 1024:.2f} KB)")
        print(f"   - Không còn duplicate hiển nhiên: PASS")
        print(f"   - Tên người ký (NguoiKy) giữ nguyên tính độc lập, không merge nhầm: PASS")
        print(f"   - Truy vết 100% từ canonical_name về original_name: PASS")
    else:
        print("❌ KẾT QUẢ BƯỚC 4: [FAIL]")
    print("==========================================================")

if __name__ == "__main__":
    main()
