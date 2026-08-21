import os
import sys
import json
import uuid
from datetime import datetime, timezone

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_FILE_PATH = os.path.join(BASE_DIR, "outputs", "audit_log.jsonl")

class AuditLogger:
    def __init__(self, log_path=LOG_FILE_PATH):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_event(
        self,
        user_role,
        action,
        query,
        user_id_demo="usr_demo_01",
        retrieval_method="Hybrid_Rerank",
        retrieved_doc_ids=None,
        retrieved_chunk_ids=None,
        citation_ids=None,
        filtered_count=0,
        status="SUCCESS",
        extra_meta=None
    ):
        request_id = f"req_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        event = {
            "timestamp": timestamp,
            "request_id": request_id,
            "user_id_demo": user_id_demo,
            "user_role": user_role,
            "action": action,
            "query": str(query),
            "retrieval_method": retrieval_method,
            "retrieved_doc_ids": retrieved_doc_ids or [],
            "retrieved_chunk_ids": retrieved_chunk_ids or [],
            "citation_ids": citation_ids or [],
            "filtered_count": int(filtered_count),
            "status": status
        }

        if extra_meta and isinstance(extra_meta, dict):
            # Sanitize to make sure no secrets are logged
            sanitized_extra = {}
            for k, v in extra_meta.items():
                if any(secret_kw in k.lower() for secret_kw in ["key", "pass", "token", "secret", "auth"]):
                    sanitized_extra[k] = "[REDACTED]"
                else:
                    sanitized_extra[k] = v
            event["metadata"] = sanitized_extra

        # Append to JSONL file
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        print(f"[AuditLogger] Logged {status} event {request_id} for user '{user_id_demo}' ({user_role})")
        return request_id

def run_audit_demo():
    logger = AuditLogger()
    print("[audit_logger] Running 3 demo audit logging events...")

    # Event 1: Allowed request
    logger.log_event(
        user_role="Staff",
        action="INTERNAL_LOOKUP",
        query="Quy định vận chuyển tiền mặt Agribank",
        user_id_demo="staff_nv01",
        retrieved_doc_ids=["agr_at01"],
        retrieved_chunk_ids=["doc_agr_at01_01", "doc_agr_at01_02"],
        citation_ids=["[100/QĐ-NHNO-AT | Điều 1]", "[100/QĐ-NHNO-AT | Điều 12]"],
        filtered_count=393,
        status="SUCCESS"
    )

    # Event 2: Denied request
    logger.log_event(
        user_role="Guest",
        action="INTERNAL_LOOKUP",
        query="Xem tỷ lệ an toàn vốn CAR rủi ro",
        user_id_demo="guest_anon",
        retrieved_doc_ids=[],
        retrieved_chunk_ids=[],
        citation_ids=[],
        filtered_count=649,
        status="DENIED"
    )

    # Event 3: Compliance Gap Check
    logger.log_event(
        user_role="Risk_Manager",
        action="COMPLIANCE_GAP_CHECK",
        query="Đối chiếu quy định tỷ lệ an toàn vốn CAR với Thông tư NHNN",
        user_id_demo="rm_lead",
        retrieved_doc_ids=["44209", "agr_car02"],
        retrieved_chunk_ids=["doc_44209_0", "doc_agr_car02_01"],
        citation_ids=["[Thông tư 41/2016/TT-NHNN]", "[250/QĐ-NHNO-QLRR | Điều 5]"],
        filtered_count=382,
        status="SUCCESS",
        extra_meta={"classification": "DAP_UNG", "confidence": 0.95}
    )

    print(f"[audit_logger] 3 demo events successfully written to {LOG_FILE_PATH}")

if __name__ == "__main__":
    run_audit_demo()
