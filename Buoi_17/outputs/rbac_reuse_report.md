# RBAC Reuse & Security Audit Report — Buổi 17

**Corpus Path**: `d:\RAG\rag_advanced\Buoi_17\data\chunks_combined_secure.csv`
**Total Chunks Analyzed**: 811

## 1. Role Access Distribution Across Corpus

| Role | Accessible Chunks | Denied Chunks | Access Percentage |
| --- | --- | --- | --- |
| `Admin` | 811 | 0 | 100.0% |
| `Risk_Manager` | 429 | 382 | 52.9% |
| `HR` | 544 | 267 | 67.08% |
| `Staff` | 418 | 393 | 51.54% |
| `Guest` | 162 | 649 | 19.98% |
| `Unknown_Hacker` | 0 | 811 | 0.0% |

## 2. RBAC Policy Verification
- **Filter Execution**: Access mask filtered pre-retrieval / pre-context.
- **Unknown Role Defense**: `Unknown_Hacker` received 0 chunks (100% DENY).
- **Multi-role support**: Tested string parsing, JSON list parsing, and comma separation.

---
RBAC REUSED: YES
FILTER BEFORE RETRIEVAL: PASS
UNKNOWN ROLE DEFAULT DENY: PASS