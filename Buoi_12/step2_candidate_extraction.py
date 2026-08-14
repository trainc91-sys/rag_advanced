"""
step2_candidate_extraction.py
------------------------------
BƯỚC 2: Rule-based Candidate Extraction
- Input: ner_kb/cleaned_documents.csv
- Phát hiện số hiệu văn bản (target_so_ky_hieu) xuất hiện trong content_clean của từng văn bản (source).
- Trích xuất trigger (Căn cứ, Sửa đổi bổ sung, Bãi bỏ, Thay thế, Trích dẫn) và đoạn evidence.
- Loại bỏ self-reference và duplicate candidates.
- Output: ner_kb/relation_candidates.csv
"""

import sys
import pathlib
import pandas as pd
import re

# Ensure UTF-8 output encoding
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = pathlib.Path(__file__).resolve().parent
NER_KB_DIR = BASE_DIR / "ner_kb"

INPUT_PATH = NER_KB_DIR / "cleaned_documents.csv"
OUTPUT_PATH = NER_KB_DIR / "relation_candidates.csv"
OUTPUT_ROOT_PATH = BASE_DIR / "relation_candidates.csv"

# Regex matching legal document numbers in Vietnamese:
# Examples: 32/2024/QH15, 73/2016/NĐ-CP, 41/2016/TT-NHNN, 17/VBHN-BTC, 05/2019/NĐ-CP
DOC_NO_REGEX = re.compile(
    r'\b\d{1,4}/(?:[0-9]{4}/|VBHN-)[A-ZĐa-z0-9_-]+\b',
    re.IGNORECASE
)

def extract_trigger_and_evidence(content: str, start_pos: int, end_pos: int):
    # Take window around match position (150 chars before, 100 chars after)
    snippet_start = max(0, start_pos - 150)
    snippet_end = min(len(content), end_pos + 100)
    evidence = content[snippet_start:snippet_end].strip()
    
    # Context before match for trigger detection
    prefix = content[max(0, start_pos - 120):start_pos].lower()
    full_window = content[snippet_start:snippet_end].lower()
    
    if "sửa đổi" in prefix or "bổ sung" in prefix or "sửa đổi" in full_window or "bổ sung" in full_window:
        trigger = "Sửa đổi, bổ sung"
    elif "bãi bỏ" in prefix or "bãi bỏ" in full_window:
        trigger = "Bãi bỏ"
    elif "thay thế" in prefix or "thay thế" in full_window:
        trigger = "Thay thế"
    elif "căn cứ" in prefix or "căn cứ" in full_window:
        trigger = "Căn cứ"
    else:
        trigger = "Trích dẫn"
        
    return trigger, evidence

def main():
    print("==========================================================")
    print("🚀 BẮT ĐẦU BƯỚC 2: RULE-BASED CANDIDATE EXTRACTION")
    print("==========================================================\n")
    
    if not INPUT_PATH.exists():
        print(f"❌ Error: File {INPUT_PATH} không tồn tại. Vui lòng chạy Bước 1 trước.")
        return

    df = pd.read_csv(INPUT_PATH)
    print(f"1️⃣ Đọc file input {INPUT_PATH} ({len(df)} văn bản)...")
    
    candidates = []
    
    for idx, row in df.iterrows():
        source_id = str(row['id'])
        source_so_ky_hieu = str(row['so_ky_hieu']).strip() if pd.notnull(row['so_ky_hieu']) else ""
        content_clean = str(row['content_clean']) if pd.notnull(row['content_clean']) else ""
        
        if not content_clean:
            continue
            
        for match in DOC_NO_REGEX.finditer(content_clean):
            target_so_ky_hieu = match.group(0).strip().upper()
            
            # 5. Loại tự tham chiếu chính văn bản hiện tại
            if source_so_ky_hieu and target_so_ky_hieu == source_so_ky_hieu.upper():
                continue
                
            trigger, evidence = extract_trigger_and_evidence(content_clean, match.start(), match.end())
            
            candidates.append({
                "source_id": source_id,
                "source_so_ky_hieu": source_so_ky_hieu,
                "target_so_ky_hieu": target_so_ky_hieu,
                "trigger": trigger,
                "evidence": evidence
            })
            
    df_candidates = pd.DataFrame(candidates)
    
    print(f"\n2️⃣ Tổng số candidate thô phát hiện: {len(df_candidates)}")
    
    # 6. Loại duplicate candidate
    df_candidates_clean = df_candidates.drop_duplicates(subset=["source_id", "target_so_ky_hieu", "trigger", "evidence"]).copy()
    
    # Double check evidence not empty
    df_candidates_clean = df_candidates_clean[df_candidates_clean["evidence"].str.len() > 0]
    
    total_candidates = len(df_candidates_clean)
    print(f"3️⃣ Tổng số candidate sau khi loại bỏ duplicate & self-reference: {total_candidates}")
    
    # 9. Thống kê theo trigger
    print(f"\n4️⃣ Thống kê số lượng Candidate theo Trigger:")
    trigger_counts = df_candidates_clean['trigger'].value_counts()
    for trg, cnt in trigger_counts.items():
        print(f"   - {trg:<20}: {cnt} candidates")
        
    # 10. In 10 candidate mẫu
    print(f"\n5️⃣ 10 Candidate mẫu tiêu biểu:")
    sample_df = df_candidates_clean.head(10)
    for i, r in sample_df.reset_index().iterrows():
        print(f"\n   📄 [{i+1}] Source: {r['source_so_ky_hieu']} ({r['source_id']}) ➔ Target: {r['target_so_ky_hieu']}")
        print(f"      - Trigger : {r['trigger']}")
        print(f"      - Evidence: ...{r['evidence'][:140]}...")
        
    # 8. Lưu relation_candidates.csv
    print(f"\n6️⃣ Lưu file kết quả...")
    df_candidates_clean.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    df_candidates_clean.to_csv(OUTPUT_ROOT_PATH, index=False, encoding='utf-8-sig')
    print(f"   - [OK] Đã lưu: {OUTPUT_PATH}")
    print(f"   - [OK] Đã lưu: {OUTPUT_ROOT_PATH}")
    
    # Check PASS conditions
    file_ok = OUTPUT_PATH.exists() and OUTPUT_PATH.stat().st_size > 0
    no_dup_ok = not df_candidates_clean.duplicated(subset=["source_id", "target_so_ky_hieu", "evidence"]).any()
    evidence_ok = (df_candidates_clean["evidence"].str.len() > 0).all()
    
    print("\n==========================================================")
    if file_ok and total_candidates > 0 and no_dup_ok and evidence_ok:
        print("🎯 KẾT QUẢ BƯỚC 2: [PASS]")
        print(f"   - File relation_candidates.csv tồn tại ({OUTPUT_PATH.stat().st_size / 1024:.2f} KB)")
        print(f"   - Không có duplicate rõ ràng: PASS")
        print(f"   - Tất cả evidence đều không rỗng: PASS")
    else:
        print("❌ KẾT QUẢ BƯỚC 2: [FAIL]")
    print("==========================================================")

if __name__ == "__main__":
    main()
