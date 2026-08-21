# Dependency & Source Data Inspection Report — Buổi 17

**Base Directory**: `d:\RAG\rag_advanced\Buoi_17`

## 1. Secure CSV Status
- **Path**: `d:\RAG\rag_advanced\Buoi_17\data/chunks_combined_secure.csv`
- **Exists**: YES
- **Total Rows**: 811
- **Total Columns**: 14
- **Columns**: `chunk_id, document_id, text, source_file, title, so_ky_hieu, loai_van_ban, co_quan_ban_hanh, ngay_ban_hanh, chapter, section, article, citation, allowed_roles`
- **Has `allowed_roles`**: YES

## 2. Normalized CSV Status
- **Path**: `d:\RAG\rag_advanced\Buoi_17\../Buoi_14/data/processed/chunks_normalized.csv`
- **Exists**: YES
- **Total Rows**: 1472
- **Total Columns**: 13
- **Columns**: `chunk_id, document_id, text, source_file, title, so_ky_hieu, document_type, chapter, section, article, clause, effective_date, status`

## 3. Package & Environment Status
- `pandas`: INSTALLED
- `torch`: INSTALLED
- `sentence_transformers`: INSTALLED
- `google.genai`: INSTALLED
- `neo4j`: INSTALLED
- `cryptography`: INSTALLED

## 4. SecureRetriever Status
- **Module**: `src.secure_retriever.SecureRetriever`
- **Reusable**: YES
- **Filtering Method**: Pre-retrieval filtering in `_get_access_mask`

---
SOURCE DATA: PASS
RBAC DATA AVAILABLE: YES
SECURE RETRIEVER REUSABLE: YES
REUSE PLAN: Use SecureRetriever from Buổi 14 via secure_retrieval_adapter.py with Buổi 17 dataset.
