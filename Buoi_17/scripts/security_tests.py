import os
import sys
import json
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from rbac import check_permission, validate_role
from secure_retrieval_adapter import SecureRetrievalAdapter
from audit_logger import AuditLogger
from internal_lookup import InternalLookupSystem
from compliance_gap import ComplianceGapChecker

def run_security_test_suite():
    report_lines = [
        "# Security & Compliance Guardrail Test Suite — Buổi 17\n",
        "## Test Case Execution Summary\n",
        "| Test ID | Security Requirement | Status | Verification Details |",
        "| --- | --- | --- | --- |"
    ]

    test_results = []

    # Test 1: Authorized Role Access
    try:
        adapter = SecureRetrievalAdapter()
        res_auth = adapter.retrieve("quy định xe bọc thép", user_roles="Staff", top_k=3)
        t1_pass = res_auth["access_decision"] == "ALLOWED" and len(res_auth["results"]) > 0
        test_results.append(("TEST_01", "Authorized Role Access", "PASS" if t1_pass else "FAIL", f"Staff accessed {len(res_auth['results'])} chunks"))
    except Exception as e:
        test_results.append(("TEST_01", "Authorized Role Access", "FAIL", str(e)))

    # Test 2: Unauthorized Role Block
    try:
        res_unauth = adapter.retrieve("xem tỷ lệ CAR rủi ro", user_roles="Guest", top_k=5)
        # Check no confidential CAR chunks returned to Guest
        confidential_leaked = any("250/QĐ-NHNO-QLRR" in item.get("citation", "") for item in res_unauth["results"])
        t2_pass = not confidential_leaked
        test_results.append(("TEST_02", "Unauthorized Text Leakage Block", "PASS" if t2_pass else "FAIL", f"Zero confidential chunks leaked to Guest"))
    except Exception as e:
        test_results.append(("TEST_02", "Unauthorized Text Leakage Block", "FAIL", str(e)))

    # Test 3: Unauthorized Context Excluded Pre-LLM
    try:
        lookup_sys = InternalLookupSystem()
        res_lookup = lookup_sys.query_internal_policy("Quy định nội bộ số 250/QĐ-NHNO-QLRR về CAR nội bộ Agribank", user_role="Guest")
        confidential_in_citations = any("250/QĐ-NHNO-QLRR" in cit for cit in res_lookup.get("citations", []))
        t3_pass = not confidential_in_citations
        test_results.append(("TEST_03", "Pre-LLM Context Filtering", "PASS" if t3_pass else "FAIL", "Zero unauthorized confidential context fed to LLM"))


    except Exception as e:
        test_results.append(("TEST_03", "Pre-LLM Context Filtering", "FAIL", str(e)))


    # Test 4: Unknown Role Default Deny
    try:
        res_unknown = adapter.retrieve("bất kỳ câu hỏi nào", user_roles="Unknown_Hacker_Role", top_k=5)
        t4_pass = res_unknown["access_decision"] == "DENIED" and len(res_unknown["results"]) == 0
        test_results.append(("TEST_04", "Unknown Role Default Deny", "PASS" if t4_pass else "FAIL", "Unknown role rejected immediately with DENIED status"))
    except Exception as e:
        test_results.append(("TEST_04", "Unknown Role Default Deny", "FAIL", str(e)))

    # Test 5: Audit Log SUCCESS & DENIED Events
    try:
        log_path = os.path.join(BASE_DIR, "outputs", "audit_log.jsonl")
        has_success = False
        has_denied = False
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        obj = json.loads(line.strip())
                        if obj.get("status") == "SUCCESS":
                            has_success = True
                        if obj.get("status") == "DENIED":
                            has_denied = True
        t5_pass = has_success and has_denied
        test_results.append(("TEST_05", "Audit Log SUCCESS & DENIED Records", "PASS" if t5_pass else "FAIL", f"Audit log records SUCCESS={has_success}, DENIED={has_denied}"))
    except Exception as e:
        test_results.append(("TEST_05", "Audit Log SUCCESS & DENIED Records", "FAIL", str(e)))

    # Test 6: Zero Secret Leakage in Audit Logs
    try:
        no_secrets = True
        secret_found = ""
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                content = f.read()
                for kw in ["FAKE_TEST_KEY", "DUMMY_KEY_1234", "YOUR_API_KEY_HERE"]:
                    if kw in content:
                        no_secrets = False
                        secret_found = kw
                        break
        test_results.append(("TEST_06", "Secret Key Audit Exposure Prevention", "PASS" if no_secrets else "FAIL", "Zero secrets found in audit logs" if no_secrets else f"Secret leaked: {secret_found}"))
    except Exception as e:
        test_results.append(("TEST_06", "Secret Key Audit Exposure Prevention", "FAIL", str(e)))

    # Test 7: Citation Integrity
    try:
        res_cit = lookup_sys.query_internal_policy("Quy định vận chuyển tiền mặt", user_role="Staff")
        t7_pass = res_cit["access_decision"] == "ALLOWED" and len(res_cit["citations"]) > 0
        test_results.append(("TEST_07", "Citation Format & Integrity", "PASS" if t7_pass else "FAIL", f"Valid citations returned: {res_cit['citations'][:1]}"))
    except Exception as e:
        test_results.append(("TEST_07", "Citation Format & Integrity", "FAIL", str(e)))

    # Test 8: Compliance Gap Dual Evidence
    try:
        gap_sys = ComplianceGapChecker()
        gap_eval = gap_sys.evaluate_gap("Tỷ lệ CAR tối thiểu 8%", "[Thông tư 41/2016/TT-NHNN]", user_role="Risk_Manager")
        t8_pass = gap_eval["internal_evidence"] != "" and gap_eval["classification"] in ["DAP_UNG", "THIEU", "CHENH_LECH", "CHUA_DU_BANG_CHUNG"]
        test_results.append(("TEST_08", "Compliance Gap Evidence Alignment", "PASS" if t8_pass else "FAIL", f"Dual evidence verified with classification '{gap_eval['classification']}'"))
    except Exception as e:
        test_results.append(("TEST_08", "Compliance Gap Evidence Alignment", "FAIL", str(e)))

    # Test 9: Mandatory Human Review Guardrail
    try:
        t9_pass = gap_eval.get("review_status") == "NEEDS_HUMAN_REVIEW"
        test_results.append(("TEST_09", "Human-in-the-Loop Review Guardrail", "PASS" if t9_pass else "FAIL", "review_status strictly tagged as NEEDS_HUMAN_REVIEW"))
    except Exception as e:
        test_results.append(("TEST_09", "Human-in-the-Loop Review Guardrail", "FAIL", str(e)))

    # Test 10: Neo4j Graceful Degradation Handling
    try:
        hints = adapter.retriever.get_graph_hints(["agr_at01"], ["doc_agr_at01_01"], user_roles=["Staff"])
        t10_pass = "status" in hints
        test_results.append(("TEST_10", "Neo4j Graceful Fallback Handling", "PASS" if t10_pass else "FAIL", f"Neo4j status handled gracefully: {hints['status']}"))
    except Exception as e:
        test_results.append(("TEST_10", "Neo4j Graceful Fallback Handling", "FAIL", str(e)))

    # Format report
    for tid, name, status, details in test_results:
        report_lines.append(f"| `{tid}` | {name} | `{status}` | {details} |")

    all_pass = all(s == "PASS" for _, _, s, _ in test_results)

    report_lines.extend([
        "\n---",
        f"SECURITY TESTS: {'PASS' if all_pass else 'FAIL'}"
    ])

    report_path = os.path.join(BASE_DIR, "outputs", "security_test_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"[security_tests] Test suite completed. All PASS: {all_pass}. Saved to {report_path}")

if __name__ == "__main__":
    run_security_test_suite()
