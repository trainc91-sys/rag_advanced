"""
step1_clean_data.py
-------------------
BƯỚC 1: Kiểm tra dữ liệu và làm sạch HTML
- Đọc ner_kb/metadata.csv & ner_kb/content.csv
- Kiểm tra trùng lặp ID, thiếu ID, missing values
- Làm sạch content_html bằng BeautifulSoup tạo content_clean
- Lưu kết quả ra ner_kb/cleaned_documents.csv
"""

import sys
import pathlib
import pandas as pd
from bs4 import BeautifulSoup
import re

# Ensure UTF-8 output encoding for terminal
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = pathlib.Path(__file__).resolve().parent
NER_KB_DIR = BASE_DIR / "ner_kb"

META_PATH = NER_KB_DIR / "metadata.csv"
CONTENT_PATH = NER_KB_DIR / "content.csv"
OUTPUT_PATH = NER_KB_DIR / "cleaned_documents.csv"
OUTPUT_ROOT_PATH = BASE_DIR / "cleaned_documents.csv"

def clean_html_content(html_str: str) -> str:
    if not isinstance(html_str, str) or not html_str.strip():
        return ""
    
    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_str, "html.parser")
    
    # Extract plain text
    text = soup.get_text(separator=" ")
    
    # Normalize whitespace (multiple spaces/tabs/newlines -> single space)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def main():
    print("==========================================================")
    print("🚀 BẮT ĐẦU BƯỚC 1: KIỂM TRA DỮ LIỆU VÀ LÀM SẠCH HTML")
    print("==========================================================\n")
    
    # 1. Read files with pandas
    print("1️⃣ Đọc hai file dữ liệu đầu vào...")
    df_meta = pd.read_csv(META_PATH)
    df_content = pd.read_csv(CONTENT_PATH)
    
    # 2. Check rows & columns
    meta_rows, meta_cols = df_meta.shape
    content_rows, content_cols = df_content.shape
    print(f"   - metadata.csv: {meta_rows} dòng, {meta_cols} cột")
    print(f"   - content.csv:  {content_rows} dòng, {content_cols} cột")
    
    # 3. Check duplicate IDs
    meta_dup = df_meta['id'].duplicated().sum()
    content_dup = df_content['id'].duplicated().sum()
    print(f"\n2️⃣ Kiểm tra ID trùng lặp (Duplicate IDs):")
    print(f"   - Số duplicate ID trong metadata.csv: {meta_dup}")
    print(f"   - Số duplicate ID trong content.csv:  {content_dup}")
    
    # 4. Check ID mismatches
    meta_ids = set(df_meta['id'].dropna())
    content_ids = set(df_content['id'].dropna())
    only_in_meta = meta_ids - content_ids
    only_in_content = content_ids - meta_ids
    id_mismatch_count = len(only_in_meta) + len(only_in_content)
    
    print(f"\n3️⃣ Kiểm tra ID lệch giữa 2 file (ID mismatches):")
    print(f"   - Số ID chỉ có trong metadata.csv: {len(only_in_meta)}")
    print(f"   - Số ID chỉ có trong content.csv:  {len(only_in_content)}")
    print(f"   - Tổng số ID mismatch:             {id_mismatch_count}")
    
    # 5. Merge by id
    print(f"\n4️⃣ Ghép dữ liệu (Merge) theo 'id'...")
    df_merged = pd.merge(df_meta, df_content, on='id', how='inner')
    total_docs = len(df_merged)
    print(f"   - Tổng số document sau ghép (inner join): {total_docs}")
    
    # 6. Missing values & invalid values check
    print(f"\n5️⃣ Thống kê Missing values & Giá trị chưa chuẩn (NULL, rỗng, 'Chưa phân loại'):")
    missing_summary = {}
    for col in df_merged.columns:
        null_cnt = df_merged[col].isnull().sum()
        empty_cnt = (df_merged[col] == "").sum() if df_merged[col].dtype == 'object' else 0
        unclassified_cnt = (df_merged[col] == "Chưa phân loại").sum() if df_merged[col].dtype == 'object' else 0
        
        missing_summary[col] = {
            "null": int(null_cnt),
            "empty": int(empty_cnt),
            "unclassified": int(unclassified_cnt)
        }
        if null_cnt > 0 or empty_cnt > 0 or unclassified_cnt > 0:
            print(f"   - Cột '{col:<22}': NULL={null_cnt}, Rỗng={empty_cnt}, 'Chưa phân loại'={unclassified_cnt}")
    
    # 7. Clean HTML
    print(f"\n6️⃣ Tiến hành làm sạch HTML bằng BeautifulSoup (Tạo cột 'content_clean')...")
    df_merged['content_clean'] = df_merged['content_html'].apply(clean_html_content)
    
    # 8. Print 2 samples of content_html vs content_clean
    print(f"\n7️⃣ Mẫu so sánh content_html vs content_clean (2 mẫu đầu tiên):")
    for idx in range(min(2, total_docs)):
        doc_id = df_merged.iloc[idx]['id']
        raw_html = str(df_merged.iloc[idx]['content_html'])[:180] + "..."
        clean_txt = str(df_merged.iloc[idx]['content_clean'])[:180] + "..."
        print(f"\n   📄 [Mẫu {idx+1}] ID: {doc_id}")
        print(f"   - [RAW HTML]     : {raw_html}")
        print(f"   - [CONTENT CLEAN]: {clean_txt}")
        
    # 9. Save output to ner_kb/cleaned_documents.csv & root cleaned_documents.csv
    print(f"\n8️⃣ Lưu file kết quả...")
    df_merged.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    df_merged.to_csv(OUTPUT_ROOT_PATH, index=False, encoding='utf-8-sig')
    print(f"   - [OK] Đã lưu ra: {OUTPUT_PATH}")
    print(f"   - [OK] Đã lưu ra: {OUTPUT_ROOT_PATH}")
    
    # Verification condition check
    output_exists = OUTPUT_PATH.exists() and OUTPUT_PATH.stat().st_size > 0
    print("\n==========================================================")
    if output_exists and total_docs > 0:
        print("🎯 KẾT QUẢ BƯỚC 1: [PASS]")
        print(f"   - File cleaned_documents.csv tồn tại ({OUTPUT_PATH.stat().st_size / 1024:.2f} KB)")
        print(f"   - Tổng số document đã xử lý sạch: {total_docs}")
    else:
        print("❌ KẾT QUẢ BƯỚC 1: [FAIL]")
    print("==========================================================")

if __name__ == "__main__":
    main()
