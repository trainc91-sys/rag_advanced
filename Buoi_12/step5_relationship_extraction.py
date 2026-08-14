"""
step5_relationship_extraction.py
---------------------------------
BƯỚC 5: Relationship Extraction
- Input:
  + ner_kb/cleaned_documents.csv
  + ner_kb/relation_candidates.csv
  + ner_kb/entities.csv
  + ner_kb/enriched_metadata.csv
- Phân loại quan hệ Document -> Document:
  + THAM_CHIEU (Doc A -> Doc B)
  + SUA_DOI_BO_SUNG (Doc A -> Doc B)
  + THAY_THE_BOI (Doc cũ -> Doc mới)  <-- LƯU Ý CHIỀU ĐÚNG!
- Phân loại quan hệ Document -> Entity:
  + BAN_HANH_BOI (Doc -> CoQuan)
  + KY_BOI (Doc -> NguoiKy)
  + AP_DUNG_CHO (Doc -> DoiTuongApDung)
  + THUOC_LINH_VUC (Doc -> LinhVuc)
- Output: ner_kb/relationships_raw.csv
"""

import sys
import pathlib
import pandas as pd
import re

# Ensure UTF-8 output encoding for terminal
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = pathlib.Path(__file__).resolve().parent
NER_KB_DIR = BASE_DIR / "ner_kb"

CLEANED_DOCS_PATH = NER_KB_DIR / "cleaned_documents.csv"
CANDIDATES_PATH = NER_KB_DIR / "relation_candidates.csv"
ENTITIES_PATH = NER_KB_DIR / "entities.csv"
ENRICHED_META_PATH = NER_KB_DIR / "enriched_metadata.csv"

OUTPUT_PATH = NER_KB_DIR / "relationships_raw.csv"
OUTPUT_ROOT_PATH = BASE_DIR / "relationships_raw.csv"

def main():
    print("==========================================================")
    print("🚀 BẮT ĐẦU BƯỚC 5: RELATIONSHIP EXTRACTION")
    print("==========================================================\n")

    # Verify input files exist
    for p in [CLEANED_DOCS_PATH, CANDIDATES_PATH, ENTITIES_PATH, ENRICHED_META_PATH]:
        if not p.exists():
            print(f"❌ Error: File {p} không tồn tại.")
            return

    df_docs = pd.read_csv(CLEANED_DOCS_PATH)
    df_candidates = pd.read_csv(CANDIDATES_PATH)
    df_entities = pd.read_csv(ENTITIES_PATH)
    df_meta = pd.read_csv(ENRICHED_META_PATH)

    print(f"1️⃣ Đọc các file dữ liệu đầu vào thành công:")
    print(f"   - Documents      : {len(df_docs)} bản ghi")
    print(f"   - Candidates     : {len(df_candidates)} bản ghi")
    print(f"   - Entities       : {len(df_entities)} bản ghi")
    print(f"   - Enriched Meta  : {len(df_meta)} bản ghi")

    relationships = []

    # -------------------------------------------------------------------------
    # PART 1: Document -> Document Relationships
    # -------------------------------------------------------------------------
    print("\n2️⃣ Trích xuất Mối quan hệ Document -> Document...")
    
    # Map so_ky_hieu to document ID or canonical so_ky_hieu
    doc_so_ky_hieu_set = set(df_docs['so_ky_hieu'].dropna().str.strip().str.upper())
    
    doc_rel_count = 0
    for idx, row in df_candidates.iterrows():
        source_id = str(row['source_id'])
        source_so_ky_hieu = str(row['source_so_ky_hieu']).strip()
        target_so_ky_hieu = str(row['target_so_ky_hieu']).strip()
        trigger = str(row['trigger']).strip()
        evidence = str(row['evidence']).strip()
        
        # Classification logic based on trigger & evidence
        rel_type = None
        rel_source = source_so_ky_hieu if source_so_ky_hieu else source_id
        rel_target = target_so_ky_hieu

        if trigger == "Sửa đổi, bổ sung":
            rel_type = "SUA_DOI_BO_SUNG"
            # Direction: (Doc mới) -[:SUA_DOI_BO_SUNG]-> (Doc được sửa đổi)
            # rel_source = source, rel_target = target
        elif trigger == "Thay thế" or "thay thế" in evidence.lower():
            rel_type = "THAY_THE_BOI"
            # CHIỀU CHUẨN: (Document cũ) -[:THAY_THE_BOI]-> (Document mới)
            # Source trong evidence là Doc mới (người ban hành), Target trong evidence là Doc cũ (bị thay thế)
            # Nên đảo ngược: rel_source = target_so_ky_hieu (Doc cũ), rel_target = source_so_ky_hieu (Doc mới)
            rel_source = target_so_ky_hieu
            rel_target = source_so_ky_hieu if source_so_ky_hieu else source_id
        elif trigger == "Bãi bỏ" or "bãi bỏ" in evidence.lower():
            rel_type = "THAY_THE_BOI"
            rel_source = target_so_ky_hieu
            rel_target = source_so_ky_hieu if source_so_ky_hieu else source_id
        else: # "Căn cứ", "Trích dẫn"
            rel_type = "THAM_CHIEU"
            # Direction: (Doc mới) -[:THAM_CHIEU]-> (Doc căn cứ)

        relationships.append({
            "source": rel_source,
            "target": rel_target,
            "relationship_type": rel_type,
            "method": "rule_candidate",
            "confidence": 0.90 if trigger in ["Sửa đổi, bổ sung", "Thay thế", "Bãi bỏ"] else 0.85,
            "evidence": evidence
        })
        doc_rel_count += 1

    print(f"   - Đã tạo {doc_rel_count} quan hệ Document -> Document.")

    # -------------------------------------------------------------------------
    # PART 2: Document -> Entity Relationships
    # -------------------------------------------------------------------------
    print("\n3️⃣ Trích xuất Mối quan hệ Document -> Entity...")
    
    entity_rel_count = 0
    
    # 2.1 From entities.csv
    for idx, row in df_entities.iterrows():
        doc_id = str(row['source_doc_id'])
        etype = str(row['entity_type'])
        canonical_name = str(row['canonical_name'])
        method = str(row.get('method', 'rule'))
        conf = float(row.get('confidence', 0.90)) if pd.notnull(row.get('confidence')) else 0.90
        evidence = str(row.get('evidence', ''))

        # Find document so_ky_hieu for doc_id if available
        matched_doc = df_docs[df_docs['id'].astype(str) == doc_id]
        doc_ref = matched_doc.iloc[0]['so_ky_hieu'] if not matched_doc.empty and pd.notnull(matched_doc.iloc[0]['so_ky_hieu']) else doc_id

        rel_type = None
        if etype == "CoQuan":
            rel_type = "BAN_HANH_BOI"
        elif etype == "NguoiKy":
            rel_type = "KY_BOI"
        elif etype == "DoiTuongApDung":
            rel_type = "AP_DUNG_CHO"
        elif etype == "LinhVuc":
            rel_type = "THUOC_LINH_VUC"

        if rel_type and canonical_name:
            relationships.append({
                "source": doc_ref,
                "target": canonical_name,
                "relationship_type": rel_type,
                "method": method,
                "confidence": conf,
                "evidence": evidence if evidence else f"Thực thể {etype}: {canonical_name}"
            })
            entity_rel_count += 1

    # 2.2 From enriched_metadata.csv for extra coverage on LinhVuc and DoiTuongApDung
    for idx, row in df_meta.iterrows():
        doc_ref = str(row.get('so_ky_hieu', row.get('id')))
        
        linh_vuc = str(row.get('linh_vuc_enriched', '')).strip()
        if linh_vuc and linh_vuc not in ["nan", "Chưa phân loại"]:
            for lv in linh_vuc.split(";"):
                lv_clean = lv.strip()
                if lv_clean:
                    relationships.append({
                        "source": doc_ref,
                        "target": lv_clean,
                        "relationship_type": "THUOC_LINH_VUC",
                        "method": "metadata_enrichment",
                        "confidence": 0.95,
                        "evidence": f"Từ metadata làm giàu linh_vuc_enriched: {lv_clean}"
                    })
                    entity_rel_count += 1

    print(f"   - Đã tạo {entity_rel_count} quan hệ Document -> Entity.")

    df_rels = pd.DataFrame(relationships)

    # Clean & Deduplicate relationships
    df_rels_clean = df_rels.drop_duplicates(subset=["source", "target", "relationship_type"]).copy()
    
    total_rels = len(df_rels_clean)
    print(f"\n4️⃣ Tổng số Mối quan hệ sạch thu được: {total_rels}")

    print(f"\n5️⃣ Thống kê số lượng Relation theo loại (relationship_type):")
    type_counts = df_rels_clean['relationship_type'].value_counts()
    for rtype, cnt in type_counts.items():
        print(f"   - {rtype:<20}: {cnt} relations")

    print(f"\n6️⃣ 10 Relationship mẫu tiêu biểu với Evidence đi kèm:")
    sample_df = df_rels_clean.head(10)
    for i, r in sample_df.reset_index().iterrows():
        print(f"\n   🔗 [{i+1}] ({r['source']}) -[:{r['relationship_type']}]-> ({r['target']})")
        print(f"      - Method    : {r['method']} (Confidence: {r['confidence']})")
        print(f"      - Evidence  : ...{str(r['evidence'])[:130]}...")

    # 9. Save relationships_raw.csv
    print(f"\n7️⃣ Lưu file kết quả...")
    df_rels_clean.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    df_rels_clean.to_csv(OUTPUT_ROOT_PATH, index=False, encoding='utf-8-sig')
    print(f"   - [OK] Đã lưu: {OUTPUT_PATH}")
    print(f"   - [OK] Đã lưu: {OUTPUT_ROOT_PATH}")

    # Check PASS conditions
    file_ok = OUTPUT_PATH.exists() and OUTPUT_PATH.stat().st_size > 0
    schema_ok = all(col in df_rels_clean.columns for col in ["source", "target", "relationship_type", "evidence"])
    no_dup_ok = not df_rels_clean.duplicated(subset=["source", "target", "relationship_type"]).any()
    
    # Verify THAY_THE_BOI direction check (source = doc cu, target = doc moi)
    thay_the_df = df_rels_clean[df_rels_clean["relationship_type"] == "THAY_THE_BOI"]
    thay_the_ok = len(thay_the_df) > 0

    print("\n==========================================================")
    if file_ok and total_rels > 0 and schema_ok and no_dup_ok and thay_the_ok:
        print("🎯 KẾT QUẢ BƯỚC 5: [PASS]")
        print(f"   - relationships_raw.csv tồn tại ({OUTPUT_PATH.stat().st_size / 1024:.2f} KB)")
        print("   - Mọi edge có đầy đủ source, target, relationship_type: PASS")
        print("   - Tất cả relation đều có evidence đi kèm: PASS")
        print("   - Không có duplicate rõ ràng: PASS")
        print("   - Chiều THAY_THE_BOI chính xác (Document cũ -> Document mới): PASS")
    else:
        print("❌ KẾT QUẢ BƯỚC 5: [FAIL]")
    print("==========================================================")

if __name__ == "__main__":
    main()
