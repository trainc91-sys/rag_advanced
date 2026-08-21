import os
import sys
from cryptography.fernet import Fernet

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KEY_PATH = os.path.join(BASE_DIR, "outputs", "secret.key")
LOG_PATH = os.path.join(BASE_DIR, "outputs", "audit_log.jsonl")
ENC_PATH = os.path.join(BASE_DIR, "outputs", "audit_log.jsonl.enc")
REPORT_PATH = os.path.join(BASE_DIR, "outputs", "encryption_demo_report.md")

def get_or_create_key():
    os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
        print(f"[encryption_demo] Generated new key at {KEY_PATH}")
    else:
        with open(KEY_PATH, "rb") as f:
            key = f.read()
    return key

def run_encryption_demo():
    key = get_or_create_key()
    fernet = Fernet(key)

    if not os.path.exists(LOG_PATH):
        print(f"[encryption_demo] Creating sample log file at {LOG_PATH}")
        from audit_logger import run_audit_demo
        run_audit_demo()

    with open(LOG_PATH, "rb") as f:
        original_data = f.read()

    # Encrypt
    encrypted_data = fernet.encrypt(original_data)
    with open(ENC_PATH, "wb") as f:
        f.write(encrypted_data)

    # Decrypt
    with open(ENC_PATH, "rb") as f:
        read_encrypted = f.read()
    decrypted_data = fernet.decrypt(read_encrypted)

    is_match = original_data == decrypted_data

    # Generate Report
    report_lines = [
        "# Local Audit Log Encryption Demo Report — Buổi 17\n",
        "## 1. Overview & Security Disclaimer",
        "> [!IMPORTANT]",
        "> This encryption script demonstrates data **at-rest protection** using AES-128/Fernet.",
        "> **Note**: This is a local training demo. Production deployment requires hardware security modules (HSM), key rotation, KMS, and TLS for in-transit encryption.\n",
        "## 2. Encryption Results",
        f"- **Source File**: `{LOG_PATH}`",
        f"- **Original Size**: {len(original_data)} bytes",
        f"- **Encrypted File**: `{ENC_PATH}`",
        f"- **Encrypted Size**: {len(encrypted_data)} bytes",
        f"- **Key Storage**: `{KEY_PATH}` (Excluded in `.gitignore`)",
        f"- **Decryption Integrity Match**: {'PASS' if is_match else 'FAIL'}\n",
        "---",
        f"ENCRYPT: {'PASS' if os.path.exists(ENC_PATH) else 'FAIL'}",
        f"DECRYPT MATCH: {'PASS' if is_match else 'FAIL'}",
        "PRODUCTION READY: NO"
    ]

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"[encryption_demo] Demo complete. Match: {is_match}. Saved to {REPORT_PATH}")

if __name__ == "__main__":
    run_encryption_demo()
