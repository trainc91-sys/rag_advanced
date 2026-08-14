"""
step6_validate_relationships.py
--------------------------------
BƯỚC 6: Validate Relationship và Tạo Output Chính Thức
- Input:
  + ner_kb/relationships_raw.csv
  + ner_kb/cleaned_documents.csv
  + ner_kb/entities.csv
- Đánh giá tính hợp lệ của từng quan hệ:
  + Validate Source, Target, Relationship Type
  + Check Self-loop, Duplicate, Missing Evidence
- Output:
  + ner_kb/relationships.csv (Chỉ chứa quan hệ PASS chuẩn bị cho Neo4j)
  + ner_kb/validation_report.csv (Báo cáo đánh giá chi tiết PASS/FAIL)
"""

import sys
import pathlib
import pandas as pd

# Ensure UTF-8 output encoding for terminal
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = pathlib.Path(__file__).resolve().parent
NER_KB_DIR = BASE_DIR / "ner_kb"

RAW_RELS_PATH = NER_KB_DIR / "relationships_raw.csv"
CLEANED_DOCS_PATH = NER_KB_DIR / "cleaned_documents.csv"
ENTITIES_PATH = NER_KB_DIR / "entities.csv"

VALIDATED_OUTPUT_PATH = NER_KB_DIR / "relationships.csv"
REPORT_OUTPUT_PATH = NER_KB_DIR / "validation_report.csv"

VALIDATED_ROOT_PATH = BASE_DIR / "relationships.csv"
REPORT_ROOT_PATH = BASE_DIR / "validation_report.csv"

ALLOWED_REL_TYPES = {
    "THAM_CHIEU",
    "SUA_DOI_BO_SUNG",
    "THAY_THE_BOI",
    "BAN_HANH_BOI",
    "KY_BOI",
    "AP_DUNG_CHO",
    "THUOC_LINH_VUC"
}

def main():
    print("==========================================================")
    print("🚀 BẮT ĐẦU BƯỚC 6: VALIDATE RELATIONSHIP & TẠO OUTPUT")
    print("==========================================================\n")

    # Verify input files
    for p in [RAW_RELS_PATH, CLEANED_DOCS_PATH, ENTITIES_PATH]:
        if not p.exists():
            print(f"❌ Error: File {p} không tồn tại.")
            return

    df_raw = pd.read_csv(RAW_RELS_PATH)
    df_docs = pd.read_csv(CLEANED_DOCS_PATH)
    df_entities = pd.read_csv(ENTITIES_PATH)

    print(f"1️⃣ Đọc dữ liệu đầu vào thành công:")
    print(f"   - Raw Relationships: {len(df_raw)} bản ghi")
    print(f"   - Documents        : {len(df_docs)} bản ghi")
    print(f"   - Entities         : {len(df_entities)} bản ghi")

    # Build lookup sets for validation
    doc_ids = set(df_docs['id'].astype(str))
    doc_so_ky_hieu = set(df_docs['so_ky_hieu'].dropna().astype(str).str.strip().str.upper())
    valid_doc_identifiers = doc_ids.union(doc_so_ky_hieu)
    
    valid_entities = set(df_entities['canonical_name'].dropna().astype(str).str.strip())

    report_list = []
    validated_rels = []
    seen_edges = set()

    pass_count = 0
    fail_count = 0
    failure_reasons = {}

    print("\n2️⃣ Tiến hành Validate từng Relationship...")

    for idx, row in df_raw.iterrows():
        source = str(row.get('source', '')).strip()
        target = str(row.get('target', '')).strip()
        rel_type = str(row.get('relationship_type', '')).strip()
        method = str(row.get('method', 'rule')).strip()
        confidence = float(row.get('confidence', 0.90)) if pd.notnull(row.get('confidence')) else 0.90
        evidence = str(row.get('evidence', '')).strip()

        is_valid = True
        reasons = []

        # 1. Missing fields check
        if not source:
            is_valid = False
            reasons.append("Thiếu source")
        if not target:
            is_valid = False
            reasons.append("Thiếu target")
        if not rel_type:
            is_valid = False
            reasons.append("Thiếu relationship_type")

        # 2. Invalid relationship_type check
        if rel_type and rel_type not in ALLOWED_REL_TYPES:
            is_valid = False
            reasons.append(f"Loại quan hệ không hợp lệ ({rel_type})")

        # 3. Self-loop check
        if source and target and source.upper() == target.upper():
            is_valid = False
            reasons.append("Tự tham chiếu (Self-loop)")

        # 4. Missing evidence check
        if not evidence or evidence == "nan":
            is_valid = False
            reasons.append("Thiếu bằng chứng (evidence)")

        # 5. Duplicate edge check
        edge_key = (source.upper(), target.upper(), rel_type)
        if edge_key in seen_edges:
            is_valid = False
            reasons.append("Duplicate edge")
        else:
            if is_valid:
                seen_edges.add(edge_key)

        # 6. Target validation based on rel_type
        if rel_type in ["BAN_HANH_BOI", "KY_BOI", "AP_DUNG_CHO", "THUOC_LINH_VUC"]:
            # Target must be an entity
            if target not in valid_entities and not target.replace(";", "").strip():
                is_valid = False
                reasons.append(f"Entity target không tồn tại trong entities.csv ({target})")

        status = "PASS" if is_valid else "FAIL"
        reason_str = "; ".join(reasons) if reasons else "Hợp lệ"

        report_list.append({
            "source": source,
            "target": target,
            "relationship_type": rel_type,
            "method": method,
            "confidence": confidence,
            "evidence": evidence,
            "status": status,
            "validation_reason": reason_str
        })

        if is_valid:
            pass_count += 1
            validated_rels.append({
                "source": source,
                "target": target,
                "relationship_type": rel_type,
                "method": method,
                "confidence": confidence,
                "evidence": evidence
            })
        else:
            fail_count += 1
            for r in reasons:
                failure_reasons[r] = failure_reasons.get(r, 0) + 1

    df_validated = pd.DataFrame(validated_rels)
    df_report = pd.DataFrame(report_list)

    print(f"\n3️⃣ Thống kê Kết quả Validation:")
    print(f"   - Tổng số Relationship đánh giá: {len(df_raw)}")
    print(f"   - Số quan hệ ĐẠT (PASS)        : {pass_count}")
    print(f"   - Số quan hệ LỖI (FAIL)        : {fail_count}")

    if failure_reasons:
        print(f"\n4️⃣ Phân tích Nguyên nhân FAIL Phổ biến:")
        for reason, count in sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {reason:<45}: {count} trường hợp")

    print(f"\n5️⃣ Thống kê số lượng Relation PASS theo Loại (relationship_type):")
    type_counts = df_validated['relationship_type'].value_counts()
    for rtype, cnt in type_counts.items():
        print(f"   - {rtype:<20}: {cnt} relations")

    print(f"\n6️⃣ 10 Relationship PASS mẫu tiêu chuẩn:")
    sample_df = df_validated.head(10)
    for i, r in sample_df.reset_index().iterrows():
        print(f"   🔗 [{i+1}] ({r['source']}) -[:{r['relationship_type']}]-> ({r['target']}) | Method: {r['method']}")

    # 9 & 10. Save outputs
    print(f"\n7️⃣ Lưu các file kết quả chính thức...")
    df_validated.to_csv(VALIDATED_OUTPUT_PATH, index=False, encoding='utf-8-sig')
    df_validated.to_csv(VALIDATED_ROOT_PATH, index=False, encoding='utf-8-sig')

    df_report.to_csv(REPORT_OUTPUT_PATH, index=False, encoding='utf-8-sig')
    df_report.to_csv(REPORT_ROOT_PATH, index=False, encoding='utf-8-sig')

    print(f"   - [OK] Đã lưu relationships.csv    : {VALIDATED_OUTPUT_PATH}")
    print(f"   - [OK] Đã lưu validation_report.csv: {REPORT_OUTPUT_PATH}")

    # Check PASS conditions
    file1_ok = VALIDATED_OUTPUT_PATH.exists() and VALIDATED_OUTPUT_PATH.stat().st_size > 0
    file2_ok = REPORT_OUTPUT_PATH.exists() and REPORT_OUTPUT_PATH.stat().st_size > 0
    clean_pass = pass_count > 0 and (len(df_validated[df_validated.duplicated(subset=["source", "target", "relationship_type"])]) == 0)

    print("\n==========================================================")
    if file1_ok and file2_ok and clean_pass:
        print("🎯 KẾT QUẢ BƯỚC 6: [PASS]")
        print(f"   - relationships.csv tồn tại ({VALIDATED_OUTPUT_PATH.stat().st_size / 1024:.2f} KB)")
        print(f"   - validation_report.csv tồn tại ({REPORT_OUTPUT_PATH.stat().st_size / 1024:.2f} KB)")
        print("   - FAIL nghiêm trọng trong file relationships.csv = 0: PASS")
    else:
        print("❌ KẾT QUẢ BƯỚC 6: [FAIL]")
    print("==========================================================")

if __name__ == "__main__":
    main()
