import os
import sys
import pandas as pd

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def build_entities_and_relations():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    output_dir = os.path.join(base_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Read seed CSV files
    risks_df = pd.read_csv(os.path.join(data_dir, "risk_profiles_seed.csv"))
    controls_df = pd.read_csv(os.path.join(data_dir, "controls_seed.csv"))
    events_df = pd.read_csv(os.path.join(data_dir, "risk_events_seed.csv"))
    rels_df = pd.read_csv(os.path.join(data_dir, "relationships_seed.csv"))
    
    # 2. Transform into entities list
    entities = []
    
    # Map RuiRo
    for _, row in risks_df.iterrows():
        entities.append({
            "id": row["id"],
            "type": "RuiRo",
            "name": row["name"],
            "description": row["description"],
            "source_file": "risk_profiles_seed.csv",
            "data_origin": row["data_origin"],
            "verification_status": row["verification_status"],
            # Business attributes
            "category": row.get("category", ""),
            "cause": row.get("cause", ""),
            "event": row.get("event", ""),
            "impact": row.get("impact", ""),
            "inherent_level": row.get("inherent_level", ""),
            "residual_level": row.get("residual_level", ""),
            "owner_unit_id": row.get("owner_unit_id", ""),
            "control_type": "",
            "frequency": "",
            "owner_role_id": "",
            "effectiveness": "",
            "occurred_at": "",
            "discovered_at": "",
            "severity": "",
            "loss_amount_vnd": ""
        })
        
    # Map KiemSoat
    for _, row in controls_df.iterrows():
        entities.append({
            "id": row["id"],
            "type": "KiemSoat",
            "name": row["name"],
            "description": row["name"], # No dedicated description column in controls, use name
            "source_file": "controls_seed.csv",
            "data_origin": row["data_origin"],
            "verification_status": row["verification_status"],
            # Business attributes
            "category": "",
            "cause": "",
            "event": "",
            "impact": "",
            "inherent_level": "",
            "residual_level": "",
            "owner_unit_id": "",
            "control_type": row.get("control_type", ""),
            "frequency": row.get("frequency", ""),
            "owner_role_id": row.get("owner_role_id", ""),
            "effectiveness": row.get("effectiveness", ""),
            "occurred_at": "",
            "discovered_at": "",
            "severity": "",
            "loss_amount_vnd": ""
        })
        
    # Map SuKienRuiRo
    for _, row in events_df.iterrows():
        entities.append({
            "id": row["id"],
            "type": "SuKienRuiRo",
            "name": row["description"], # Description serves as event summary name
            "description": row["description"],
            "source_file": "risk_events_seed.csv",
            "data_origin": row["data_origin"],
            "verification_status": row["verification_status"],
            # Business attributes
            "category": "",
            "cause": "",
            "event": "",
            "impact": "",
            "inherent_level": "",
            "residual_level": "",
            "owner_unit_id": "",
            "control_type": "",
            "frequency": "",
            "owner_role_id": "",
            "effectiveness": "",
            "occurred_at": row.get("occurred_at", ""),
            "discovered_at": row.get("discovered_at", ""),
            "severity": row.get("severity", ""),
            "loss_amount_vnd": row.get("loss_amount_vnd", "")
        })
        
    entities_df = pd.DataFrame(entities)
    entities_path = os.path.join(output_dir, "entities.csv")
    entities_df.to_csv(entities_path, index=False, encoding="utf-8")
    
    # 3. Transform and validate relations
    relations_path = os.path.join(output_dir, "relations.csv")
    rels_df.to_csv(relations_path, index=False, encoding="utf-8")
    
    # 4. Verification & Validation
    entity_ids = set(entities_df["id"])
    sources = set(rels_df["source_id"])
    targets = set(rels_df["target_id"])
    
    missing_sources = sources - entity_ids
    missing_targets = targets - entity_ids
    
    print("=" * 60)
    print("KẾT QUẢ CHUẨN HÓA DỮ LIỆU ENTITIES VÀ RELATIONS")
    print("=" * 60)
    print(f"- Đã lưu file: {entities_path}")
    print(f"- Đã lưu file: {relations_path}")
    print("\n--- THỐNG KÊ CHI TIẾT ENTITIES BY TYPE ---")
    type_counts = entities_df["type"].value_counts()
    for etype, count in type_counts.items():
        print(f"  + {etype}: {count} entities")
    print(f"  Total Entities: {len(entities_df)}")
    
    print("\n--- THỐNG KÊ CHI TIẾT RELATIONS BY TYPE ---")
    rel_counts = rels_df["relationship_type"].value_counts()
    for rtype, count in rel_counts.items():
        print(f"  + {rtype}: {count} relations")
    print(f"  Total Relations: {len(rels_df)}")
    
    print("\n--- KIỂM TRA ORPHAN REFERENCES ---")
    if missing_sources or missing_targets:
        print(f"[ERR] Phát hiện orphan reference!")
        if missing_sources:
            print(f"  - source_id không tồn tại: {missing_sources}")
        if missing_targets:
            print(f"  - target_id không tồn tại: {missing_targets}")
    else:
        print("  -> 100% source_id và target_id đều tồn tại hợp lệ trong entities.csv.")
    print("=" * 60)

if __name__ == "__main__":
    build_entities_and_relations()
