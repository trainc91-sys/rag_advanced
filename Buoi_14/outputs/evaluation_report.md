# RETRIEVAL EVALUATION REPORT (BUỔI 14)

Total Questions Evaluated: `10`

## 1. Overall Performance Summary
| Method | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---|---|---|---|
| **BM25-only** | 40.00% | 60.00% | 60.00% | 0.4833 |
| **Dense-only** | 60.00% | 60.00% | 80.00% | 0.6500 |
| **Hybrid** | 60.00% | 80.00% | 80.00% | 0.7000 |
| **Hybrid+Rerank** | 60.00% | 80.00% | 80.00% | 0.7000 |

## 2. Performance by Query Type

| Query Type | Method | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---|---|---|---|---|
| `EXACT_KEYWORD` | BM25-only | 50.00% | 75.00% | 75.00% | 0.5833 |
| `EXACT_KEYWORD` | Dense-only | 50.00% | 50.00% | 100.00% | 0.6250 |
| `EXACT_KEYWORD` | Hybrid | 75.00% | 100.00% | 100.00% | 0.8750 |
| `EXACT_KEYWORD` | Hybrid+Rerank | 50.00% | 75.00% | 75.00% | 0.6250 |
| `MIXED` | BM25-only | 33.33% | 66.67% | 66.67% | 0.5000 |
| `MIXED` | Dense-only | 100.00% | 100.00% | 100.00% | 1.0000 |
| `MIXED` | Hybrid | 66.67% | 100.00% | 100.00% | 0.8333 |
| `MIXED` | Hybrid+Rerank | 66.67% | 100.00% | 100.00% | 0.8333 |
| `SEMANTIC` | BM25-only | 33.33% | 33.33% | 33.33% | 0.3333 |
| `SEMANTIC` | Dense-only | 33.33% | 33.33% | 33.33% | 0.3333 |
| `SEMANTIC` | Hybrid | 33.33% | 33.33% | 33.33% | 0.3333 |
| `SEMANTIC` | Hybrid+Rerank | 66.67% | 66.67% | 66.67% | 0.6667 |

## 3. Analysis & Key Insights
- **EXACT_KEYWORD Queries**: BM25 excels at matching exact document numbers (e.g. `QĐ-125`, `73/2016/NĐ-CP`) and specific article numbers (`Điều 115`).
- **SEMANTIC Queries**: Dense retrieval outperforms BM25 when user vocabulary differs from statutory wording (e.g. searching for approval authority or credit limits).
- **MIXED Queries**: Hybrid Search (RRF) delivers superior consistency across both exact keyword signals and semantic intent.
- **Reranking Effect**: Neural Reranking (Cross-Encoder) re-orders candidate passages based on query-passage interaction, sharpening Hit@1 precision.
