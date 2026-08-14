import os
import sys
import pandas as pd

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def inspect_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    files = {
        "risk_profiles": "risk_profiles_seed.csv",
        "controls": "controls_seed.csv",
        "risk_events": "risk_events_seed.csv",
        "relationships": "relationships_seed.csv"
    }
    
    dfs = {}
    print("=" * 60)
    print("1. THỐNG KÊ CHI TIẾT TỪNG FILE CSV")
    print("=" * 60)
    
    for key, filename in files.items():
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            print(f"File không tồn tại: {filepath}")
            continue
            
        df = pd.read_csv(filepath)
        dfs[key] = df
        
        print(f"\n--- FILE: {filename} ---")
        print(f"- Số dòng (rows): {len(df)}")
        print(f"- Số cột (columns): {len(df.columns)}")
        print(f"- Tên các cột: {list(df.columns)}")
        print(f"- Giá trị NULL theo cột:\n{df.isnull().sum()[df.isnull().sum() > 0] if df.isnull().sum().sum() > 0 else '  Không có giá trị NULL'}")
        
        if "id" in df.columns:
            dups = df["id"].duplicated().sum()
            print(f"- Trùng lặp khóa chính 'id': {dups}")
        elif key == "relationships":
            dups = df.duplicated().sum()
            print(f"- Trùng lặp dòng quan hệ: {dups}")
            print(f"- Các loại relationship_type: {df['relationship_type'].value_counts().to_dict()}")

    print("\n" + "=" * 60)
    print("2. KIỂM TRA TÍNH TOÀN VẸN VÀ THAM CHIẾU (FOREIGN KEYS)")
    print("=" * 60)
    
    risk_ids = set(dfs["risk_profiles"]["id"]) if "risk_profiles" in dfs else set()
    control_ids = set(dfs["controls"]["id"]) if "controls" in dfs else set()
    event_ids = set(dfs["risk_events"]["id"]) if "risk_events" in dfs else set()
    all_entity_ids = risk_ids.union(control_ids).union(event_ids)
    
    # Check risk_events foreign key: risk_id -> risk_profiles.id
    if "risk_events" in dfs:
        event_risk_refs = set(dfs["risk_events"]["risk_id"])
        missing_risks_in_events = event_risk_refs - risk_ids
        print(f"- Risk IDs trong risk_events không tồn tại ở risk_profiles: {missing_risks_in_events if missing_risks_in_events else 'Không có (100% hợp lệ)'}")
        
    # Check relationships foreign keys: source_id, target_id -> all_entity_ids
    if "relationships" in dfs:
        rel_df = dfs["relationships"]
        sources = set(rel_df["source_id"])
        targets = set(rel_df["target_id"])
        
        missing_sources = sources - all_entity_ids
        missing_targets = targets - all_entity_ids
        
        print(f"- source_id trong relationships không tồn tại trong entities: {missing_sources if missing_sources else 'Không có (100% hợp lệ)'}")
        print(f"- target_id trong relationships không tồn tại trong entities: {missing_targets if missing_targets else 'Không có (100% hợp lệ)'}")

    print("\n" + "=" * 60)
    print("3. PHÂN TÍCH PHẠM VI MÃ THAM CHIẾU VÀ DỮ LIỆU THIẾU MASTER DATA")
    print("=" * 60)
    
    if "risk_profiles" in dfs and "owner_unit_id" in dfs["risk_profiles"].columns:
        units = sorted(dfs["risk_profiles"]["owner_unit_id"].dropna().unique().tolist())
        print(f"- Danh sách mã đơn vị (owner_unit_id): {units}")
        print("  -> LƯU Ý: Chưa có bảng master mô tả tên đơn vị đầy đủ (DV-OPS, DV-CREDIT, v.v.). Không tự bịa tên!")

    if "controls" in dfs and "owner_role_id" in dfs["controls"].columns:
        roles = sorted(dfs["controls"]["owner_role_id"].dropna().unique().tolist())
        print(f"- Danh sách mã vai trò (owner_role_id): {roles}")
        print("  -> LƯU Ý: Chưa có bảng master mô tả tên vai trò đầy đủ (VT-OPS-CONTROL, v.v.). Không tự bịa tên!")
        
    print("\n" + "=" * 60)
    print("4. KIẾN TRÚC NODE VÀ EDGE CHO PHIÊN BẢN MVP")
    print("=" * 60)
    print("- Node types:")
    print(f"  + RuiRo ({len(risk_ids)} nodes)")
    print(f"  + KiemSoat ({len(control_ids)} nodes)")
    print(f"  + SuKienRuiRo ({len(event_ids)} nodes)")
    print("- Edge types:")
    if "relationships" in dfs:
        for rtype, count in dfs["relationships"]["relationship_type"].value_counts().items():
            print(f"  + {rtype}: {count} edges")
    print("=" * 60)

if __name__ == "__main__":
    inspect_data()
