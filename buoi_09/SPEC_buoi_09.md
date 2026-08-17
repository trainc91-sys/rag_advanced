# SPEC Buổi 09 — Hierarchical Multi-query RAG

## 1. Mục tiêu và khác biệt Buổi 08/09

Buổi 09 kế thừa Buổi 08 nhưng mở rộng để xử lý retrieval văn bản pháp luật theo parent–child:

- Buổi 08: một câu hỏi duy nhất, candidate là chunk phẳng, rerank chunk.
- Buổi 09: một câu hỏi gốc Q0 + query variants, candidate child sau đó mở rộng sang parent.

> Buổi 09 không import runtime Buổi 08. Mọi baseline Buổi 08 được sao chép vào
> cùng thư mục Buổi 09 và sử dụng như một snapshot tham chiếu.

Buổi 09 giải quyết:

- Một biểu đạt chưa đủ để bao phủ nội dung pháp luật.
- Chunk nhỏ có thể thiếu context Điều/Khoản xung quanh.
- Cần giữ parent context khi trả lời.

## 2. Kiến trúc pipeline

```
Question
  ├─ Q0: câu hỏi gốc
  ├─ Q1: variant 1
  ├─ Q2: variant 2
  └─ Q3: variant 3
        ↓
Per-query hybrid retrieval
        ↓
Cross-query RRF fusion
        ↓
Child hit selection
        ↓
Child → Parent mapping
        ↓
Parent aggregation
        ↓
Parent rerank bằng Q0
        ↓
Gemini answer generation
```

## 2.1 Hai tầng fusion

Buổi 09 có hai tầng fusion riêng biệt:

- Tầng 1: fusion child-level giữa các truy vấn. Mỗi truy vấn variant trả về các
  hit chunk, sau đó `cross-query RRF` hợp nhất các rank child nhằm xác định bộ
  child candidate mạnh nhất.
- Tầng 2: parent aggregation và parent rerank. Child hit được map lên parent
  document bằng hierarchy registry; mỗi parent candidate tổng hợp evidence từ
  các child anchors và được rerank bằng câu hỏi gốc Q0.

## 2.2 Parent expansion

Parent expansion là quá trình mở rộng evidence từ chunk nhỏ sang parent context:

- Mỗi child hit có thể nằm trong một parent document chứa chapter/article/clause.
- Parent document giữ toàn bộ context parent, không chỉ snippet child.
- Evidence trả về phải bao gồm cả `parent_id` và `child_chunk_ids` để đảm bảo
  traceability.
- Parent expansion không phải là tóm tắt nội dung; nó là ghép và mở rộng context
  từ hierarchy registry.

## 3. Bốn mode

- `single_flat`: chỉ Q0, evidence là child chunk, rerank child.
- `multi_flat`: Q0 + variants, evidence là child chunk sau cross-query fusion, rerank child.
- `single_parent`: chỉ Q0, evidence là parent mở rộng từ child hit, rerank parent.
- `multi_parent`: Q0 + variants, evidence là parent mở rộng từ fused child hits, rerank parent.

`multi_parent` là mode mặc định của Buổi 09.

## 4. QueryVariant schema và validation

```json
{
  "query_id": "Q1",
  "query_text": "Nội dung diễn đạt khác",
  "source_type": "original|variant",
  "weight": 1.0,
  "cooldown": 0
}
```

Validation:

- `query_id`: non-empty string.
- `query_text`: non-empty string, độ dài <= `MULTI_QUERY_MAX_CHARS`.
- `source_type`: chỉ `original` hoặc `variant`.
- `weight`: float >= 0.
- `Q0` phải luôn có `source_type=original`.

## 5. Hierarchy registry schema

```json
{
  "parent_id": "p1",
  "document_title": "Văn bản A",
  "source": "TT 01/2024/NHNN",
  "jurisdiction": "VN",
  "children": ["c1", "c2", "c3"],
  "structure": [
    {"type": "chapter", "label": "Chương I", "start_chunk": "c1", "end_chunk": "c5"},
    {"type": "article", "label": "Điều 1", "start_chunk": "c2", "end_chunk": "c3"}
  ]
}
```

Validation:

- `parent_id` phải unique.
- `children` phải là list chunk_id tồn tại.
- `structure` là list các node có `type`, `label`, `start_chunk`, `end_chunk`.

## 6. ParentDocument schema

```json
{
  "parent_id": "p1",
  "title": "Văn bản A",
  "source": "TT 01/2024/NHNN",
  "text": "Toàn bộ nội dung parent...",
  "page_start": 1,
  "page_end": 20,
  "child_chunk_ids": ["c1", "c2"]
}
```

ParentDocument phải giữ nguyên context đủ để trả lời câu hỏi gốc.

## 7. MultiQueryChildHit và ParentCandidate schema

MultiQueryChildHit:

```json
{
  "query_id": "Q1",
  "chunk_id": "c1",
  "rank": 1,
  "score": 0.87,
  "source": "Văn bản A",
  "page_start": 2,
  "page_end": 2,
  "snippet": "..."
}
```

ParentCandidate:

```json
{
  "parent_id": "p1",
  "score": 2.45,
  "child_hits": ["c1", "c2"],
  "rerank_score": 0.92,
  "rank": 1,
  "text": "Context parent..."
}
```

## 8. Quy tắc hierarchy resolution và ambiguous warning

- Nếu child chunk khớp nhiều parent, cảnh báo `ambiguous_parent`.
- Nếu `structure.article` thiếu hoặc không đủ, dùng fallback bằng `source` + `chunk_id`.
- Nếu registry không đồng nhất, đánh dấu `ambiguous_resolution`.
- Warning phải rõ reason, affected chunk_id và parent_id candidate.

## 9. Công thức cross-query RRF và parent aggregation

- Dùng RRF để hợp nhất `single_flat` và `multi_flat` trên child rank:
  `rrf_score = sum(1/(k + rank))`.
- Với multi-query, mỗi query variant có `weight`.
- Parent aggregation:
  - Parent score = max(child_score) hoặc weighted sum của child hits.
  - Giới hạn child contribution bằng `PARENT_SCORE_CHILD_LIMIT`.
  - Parent rerank dùng câu hỏi gốc Q0.

## 10. Context budget và citation contract

- Tổng context vào Gemini không vượt `TOTAL_CONTEXT_MAX_CHARS`.
- Parent text bị cắt ở `PARENT_MAX_CHARS` nếu cần.
- Citations phải là `parent_id` và `child_chunk_ids`.
- Answer phải bao gồm citation labels rõ ràng và traceability.

## 11. Status/failure contract

- `status` phải trả về một trong:
  - `answered`
  - `insufficient_evidence`
  - `reranker_unavailable`
  - `generation_failed`
- `warnings` phải liệt kê vấn đề không chặn.
- Không tạo collection hoặc tải model khi chỉ gọi `status`.

## 12. Testability/dependency injection

- Mỗi component phải cho mock:
  - query generator
  - retrieval client
  - reranker
  - generation client
- Không gọi Gemini hoặc reranker tại import-time.
- Placeholder được thiết kế để compile nhẹ.

## 13. Evaluation metrics và acceptance criteria

- Recall@K, MRR@K, nDCG@K cho parent candidates.
- Cross-query fusion effectiveness.
- Parent aggregation coverage cho child hits.
- Acceptance:
  - CLI và module Buổi 09 import được.
  - `.py` compile sạch.
  - Placeholder không tải model / không gọi API.
  - README và SPEC mô tả rõ Buổi 09 scope.

## 14. Xác nhận chỉ ghi Buổi 09

Tài liệu và code này chỉ sửa `rag_advanced/buoi_09/`.
Không thay đổi Buổi 05–08.
