import os
import sys
import re
import pandas as pd
from bs4 import BeautifulSoup

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Normalize whitespaces
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n', text)
    return text.strip()

def extract_article_number(header):
    match = re.search(r'Điều\s+(\d+)', header, re.IGNORECASE)
    if match:
        return f"Điều {match.group(1)}"
    return ""

def process_document(doc_id, html_content, metadata_dict):
    if pd.isna(html_content):
        return []

    soup = BeautifulSoup(str(html_content), 'html.parser')
    raw_text = soup.get_text('\n')
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

    # Splitting logic into articles
    chunks = []
    current_article = "Preamble"
    current_lines = []
    chunk_index = 0

    article_pattern = re.compile(r'^(Điều\s+\d+[\.\:\s\-]?.*)', re.IGNORECASE)

    for line in lines:
        match = article_pattern.match(line)
        if match:
            # Save previous chunk
            if current_lines:
                chunk_text = clean_text('\n'.join(current_lines))
                if len(chunk_text) > 20:
                    chunk_index += 1
                    art_num = extract_article_number(current_article)
                    chunks.append({
                        "chunk_id": f"{doc_id}_c{chunk_index:03d}",
                        "document_id": str(doc_id),
                        "text": chunk_text,
                        "source_file": "content.csv",
                        "title": metadata_dict.get("title", ""),
                        "so_ky_hieu": metadata_dict.get("so_ky_hieu", ""),
                        "document_type": metadata_dict.get("loai_van_ban", ""),
                        "chapter": "",
                        "section": "",
                        "article": current_article if current_article != "Preamble" else "",
                        "clause": "",
                        "effective_date": metadata_dict.get("ngay_co_hieu_luc", ""),
                        "status": metadata_dict.get("tinh_trang_hieu_luc", "")
                    })
            current_article = line
            current_lines = [line]
        else:
            current_lines.append(line)

    # Save last chunk
    if current_lines:
        chunk_text = clean_text('\n'.join(current_lines))
        if len(chunk_text) > 20:
            chunk_index += 1
            art_num = extract_article_number(current_article)
            chunks.append({
                "chunk_id": f"{doc_id}_c{chunk_index:03d}",
                "document_id": str(doc_id),
                "text": chunk_text,
                "source_file": "content.csv",
                "title": metadata_dict.get("title", ""),
                "so_ky_hieu": metadata_dict.get("so_ky_hieu", ""),
                "document_type": metadata_dict.get("loai_van_ban", ""),
                "chapter": "",
                "section": "",
                "article": current_article if current_article != "Preamble" else "",
                "clause": "",
                "effective_date": metadata_dict.get("ngay_co_hieu_luc", ""),
                "status": metadata_dict.get("tinh_trang_hieu_luc", "")
            })

    return chunks

def prepare_corpus():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    kb_dir = os.path.abspath(os.path.join(base_dir, "..", "kb+hops"))
    
    content_path = os.path.join(kb_dir, "content.csv")
    meta_path = os.path.join(kb_dir, "metadata.csv")
    
    if not os.path.exists(content_path) or not os.path.exists(meta_path):
        raise FileNotFoundError(f"Source files missing in {kb_dir}")

    content_df = pd.read_csv(content_path)
    meta_df = pd.read_csv(meta_path)
    
    # Map metadata by string ID
    meta_map = {}
    for _, row in meta_df.iterrows():
        meta_map[str(row['id'])] = row.to_dict()

    all_chunks = []
    for _, row in content_df.iterrows():
        doc_id = str(row['id'])
        meta_dict = meta_map.get(doc_id, {})
        doc_chunks = process_document(doc_id, row['content_html'], meta_dict)
        all_chunks.extend(doc_chunks)

    df_out = pd.DataFrame(all_chunks)
    
    # Save to data/processed/chunks_normalized.csv
    out_dir = os.path.join(base_dir, "data", "processed")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "chunks_normalized.csv")
    
    df_out.to_csv(out_path, index=False, encoding="utf-8-sig")
    
    # Validation metrics
    total_chunks = len(df_out)
    unique_docs = df_out['document_id'].nunique()
    missing_text = df_out['text'].isna().sum()
    duplicate_chunks = df_out['chunk_id'].duplicated().sum()
    
    print(f"--- CORPUS PREPARATION COMPLETE ---")
    print(f"Output File: {out_path}")
    print(f"Total chunks: {total_chunks}")
    print(f"Total documents: {unique_docs}")
    print(f"Missing text count: {missing_text}")
    print(f"Duplicate chunk_id count: {duplicate_chunks}")
    print("\nSample records (first 3):")
    print(df_out[['chunk_id', 'document_id', 'so_ky_hieu', 'article', 'text']].head(3).to_string())

if __name__ == "__main__":
    prepare_corpus()
