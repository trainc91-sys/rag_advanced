import os
import sys
import json
import pandas as pd

# Set UTF-8 stdout encoding for Windows compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import ROLE_CATEGORIES

def categorize_chunk(row):
    title = str(row.get('title', '')).lower()
    so_ky_hieu = str(row.get('so_ky_hieu', '')).lower()
    text = str(row.get('text', '')).lower()

    # 1. HR & Licensing / Personnel / Internal Organization Docs
    hr_docs = ['01/2025/tt-nhnn', '57/2024/tt-nhnn', '62/2024/tt-nhnn', '69/2025/tt-nhnn']
    hr_keywords = ['tuyển dụng', 'bổ nhiệm', 'bỏ nhiệm', 'nhân sự', 'tổ chức lại', 'cấp phép lần đầu', 'lương', 'kỷ luật']
    if any(doc in so_ky_hieu for doc in hr_docs) or any(kw in text for kw in hr_keywords):
        return ROLE_CATEGORIES["HR"]

    # 2. Risk Management / Capital Adequacy / Internal Audit / Foreign Reserves / Securities Penalties
    risk_docs = [
        '41/2016/tt-nhnn', '22/2023/tt-nhnn', '44/2011/tt-nhnn', 
        '62/2025/tt-nhnn', '43/2024/tt-nhnn', '156/2020/nđ-cp', 
        '17/vbhn-btc', '105/2016/tt-btc', '67/2011/qh12'
    ]
    risk_keywords = [
        'an toàn vốn', 'tỷ lệ an toàn', 'quản trị rủi ro', 'hạn mức', 
        'phê duyệt vay', 'nợ xấu', 'dự trữ ngoại hối', 'xử phạt vi phạm', 'chứng khoán'
    ]
    if any(doc in so_ky_hieu for doc in risk_docs) or any(kw in text for kw in risk_keywords):
        return ROLE_CATEGORIES["RISK"]

    # 3. General Public & Staff Regulations
    return ROLE_CATEGORIES["GENERAL"]

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_csv = os.path.join(base_dir, "data", "processed", "chunks_normalized.csv")
    output_csv = os.path.join(base_dir, "data", "processed", "chunks_secure.csv")

    if not os.path.exists(input_csv):
        print(f"❌ Error: {input_csv} does not exist.")
        sys.exit(1)

    print(f"📖 Reading normalized corpus from {input_csv}...")
    df = pd.read_csv(input_csv)

    print(f"🏷️ Assigning security tags (allowed_roles) to {len(df)} chunks...")
    roles_list = []
    for _, row in df.iterrows():
        assigned = categorize_chunk(row)
        roles_list.append(json.dumps(assigned, ensure_ascii=False))

    df['allowed_roles'] = roles_list

    # Verification: check nulls
    null_count = df['allowed_roles'].isnull().sum()
    empty_count = sum(1 for r in df['allowed_roles'] if not json.loads(r))
    assert null_count == 0 and empty_count == 0, "❌ Error: Found chunks with empty allowed_roles!"

    # Save secure dataset
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"✅ Successfully saved security-tagged corpus to {output_csv}")

    # Statistics
    print("\n--------------------------------------------------------")
    print("SECURITY TAGGING STATISTICS & SUMMARY")
    print("--------------------------------------------------------")
    counts = {}
    for r in df['allowed_roles']:
        r_str = str(sorted(json.loads(r)))
        counts[r_str] = counts.get(r_str, 0) + 1

    for key, count in counts.items():
        print(f"  - Security Group {key}: {count} chunks ({count/len(df)*100:.1f}%)")

    print("\n--------------------------------------------------------")
    print("REPRESENTATIVE SAMPLE CHUNKS FOR 3 SECURITY LEVELS")
    print("--------------------------------------------------------")
    
    # Representative samples
    sample_hr = df[df['allowed_roles'].str.contains('"HR"') & ~df['allowed_roles'].str.contains('"Guest"')].head(1)
    sample_risk = df[df['allowed_roles'].str.contains('"Risk_Manager"') & ~df['allowed_roles'].str.contains('"Guest"')].head(1)
    sample_guest = df[df['allowed_roles'].str.contains('"Guest"')].head(1)

    samples = [("1. HR / Restricted Level (Admin, HR)", sample_hr),
               ("2. Risk / Internal Operations Level (Admin, Risk_Manager, Staff)", sample_risk),
               ("3. General / Public Level (All Roles)", sample_guest)]

    for label, sample_df in samples:
        print(f"\n[{label}]")
        if not sample_df.empty:
            row = sample_df.iloc[0]
            print(f"  Chunk ID: {row['chunk_id']} | Doc: {row['so_ky_hieu']} ({row['document_id']})")
            print(f"  Allowed Roles: {row['allowed_roles']}")
            print(f"  Text snippet: {str(row['text'])[:120].replace('\n', ' ')}...")
        else:
            print("  No sample found.")
    print("--------------------------------------------------------")

if __name__ == "__main__":
    main()
