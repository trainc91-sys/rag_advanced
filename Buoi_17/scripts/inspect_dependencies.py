import os
import sys
import json
import pandas as pd
from dotenv import load_dotenv

def inspect_environment():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)

    # 1. Primary secure CSV
    secure_csv_rel = os.getenv("SOURCE_SECURE_CSV", "data/chunks_combined_secure.csv")
    secure_csv_path = os.path.join(base_dir, secure_csv_rel)
    if not os.path.exists(secure_csv_path):
        secure_csv_path = os.path.abspath(os.path.join(base_dir, "..", "Buoi_14", "data", "processed", "chunks_secure.csv"))

    # 2. Normalized CSV
    norm_csv_rel = os.getenv("SOURCE_NORMALIZED_CSV", "../Buoi_14/data/processed/chunks_normalized.csv")
    norm_csv_path = os.path.join(base_dir, norm_csv_rel)
    if not os.path.exists(norm_csv_path):
        norm_csv_path = os.path.abspath(os.path.join(base_dir, "..", "Buoi_14", "data", "processed", "chunks_normalized.csv"))

    report_lines = []
    report_lines.append("# Dependency & Source Data Inspection Report — Buổi 17\n")
    report_lines.append(f"**Base Directory**: `{base_dir}`\n")

    # Inspect Secure CSV
    secure_exists = os.path.exists(secure_csv_path)
    secure_cols = []
    secure_rows = 0
    has_allowed_roles = False

    if secure_exists:
        df_sec = pd.read_csv(secure_csv_path)
        secure_rows = len(df_sec)
        secure_cols = list(df_sec.columns)
        has_allowed_roles = "allowed_roles" in secure_cols
        report_lines.append("## 1. Secure CSV Status")
        report_lines.append(f"- **Path**: `{secure_csv_path}`")
        report_lines.append(f"- **Exists**: YES")
        report_lines.append(f"- **Total Rows**: {secure_rows}")
        report_lines.append(f"- **Total Columns**: {len(secure_cols)}")
        report_lines.append(f"- **Columns**: `{', '.join(secure_cols)}`")
        report_lines.append(f"- **Has `allowed_roles`**: {'YES' if has_allowed_roles else 'NO'}\n")
    else:
        report_lines.append("## 1. Secure CSV Status")
        report_lines.append(f"- **Path**: `{secure_csv_path}`")
        report_lines.append("- **Exists**: NO\n")

    # Inspect Normalized CSV
    norm_exists = os.path.exists(norm_csv_path)
    norm_cols = []
    norm_rows = 0

    if norm_exists:
        df_norm = pd.read_csv(norm_csv_path)
        norm_rows = len(df_norm)
        norm_cols = list(df_norm.columns)
        report_lines.append("## 2. Normalized CSV Status")
        report_lines.append(f"- **Path**: `{norm_csv_path}`")
        report_lines.append(f"- **Exists**: YES")
        report_lines.append(f"- **Total Rows**: {norm_rows}")
        report_lines.append(f"- **Total Columns**: {len(norm_cols)}")
        report_lines.append(f"- **Columns**: `{', '.join(norm_cols)}`\n")
    else:
        report_lines.append("## 2. Normalized CSV Status")
        report_lines.append(f"- **Path**: `{norm_csv_path}`")
        report_lines.append("- **Exists**: NO\n")

    # Python Packages
    report_lines.append("## 3. Package & Environment Status")
    for pkg in ["pandas", "torch", "sentence_transformers", "google.genai", "neo4j", "cryptography"]:
        try:
            __import__(pkg)
            report_lines.append(f"- `{pkg}`: INSTALLED")
        except ImportError:
            report_lines.append(f"- `{pkg}`: MISSING")

    # Check SecureRetriever reusability
    b14_src = os.path.abspath(os.path.join(base_dir, "..", "Buoi_14"))
    sys.path.insert(0, b14_src)
    retriever_found = False
    try:
        from src.secure_retriever import SecureRetriever
        retriever_found = True
        report_lines.append("\n## 4. SecureRetriever Status")
        report_lines.append("- **Module**: `src.secure_retriever.SecureRetriever`")
        report_lines.append("- **Reusable**: YES")
        report_lines.append("- **Filtering Method**: Pre-retrieval filtering in `_get_access_mask`")
    except Exception as e:
        report_lines.append("\n## 4. SecureRetriever Status")
        report_lines.append(f"- **Reusable**: NO ({e})")

    # Summary
    source_ready = secure_exists and has_allowed_roles
    rbac_ready = has_allowed_roles
    reusable = retriever_found

    report_lines.append("\n---")
    report_lines.append(f"SOURCE DATA: {'PASS' if source_ready else 'FAIL'}")
    report_lines.append(f"RBAC DATA AVAILABLE: {'YES' if rbac_ready else 'NO'}")
    report_lines.append(f"SECURE RETRIEVER REUSABLE: {'YES' if reusable else 'NO'}")
    report_lines.append("REUSE PLAN: Use SecureRetriever from Buổi 14 via secure_retrieval_adapter.py with Buổi 17 dataset.\n")

    output_dir = os.path.join(base_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "dependency_report.md")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"[inspect_dependencies] Report written to {report_path}")
    print(f"ENVIRONMENT READY: {'YES' if (source_ready and reusable) else 'NO'}")
    print(f"SOURCE DATA READY: {'YES' if source_ready else 'NO'}")
    print(f"SECURE RETRIEVER FOUND: {'YES' if reusable else 'NO'}")

if __name__ == "__main__":
    inspect_environment()
