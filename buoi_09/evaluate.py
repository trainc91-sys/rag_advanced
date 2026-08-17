"""Evaluation pipeline for Buổi 09 retrieval ranking.

This module is designed for offline evaluation and report generation without any
live Gemini or semantic service calls. It computes standard retrieval metrics
and writes atomic JSON reports into `reports/`.
"""

from __future__ import annotations

import json
import math
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence, Set

BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"
EVAL_DIR = BASE_DIR / "eval"


def compute_recall_at_k(predicted: Sequence[str], relevant: Set[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be greater than 0.")
    if not relevant:
        return 0.0
    hits = sum(1 for item in predicted[:k] if item in relevant)
    return hits / len(relevant)


def compute_mrr_at_k(predicted: Sequence[str], relevant: Set[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be greater than 0.")
    for rank, item in enumerate(predicted[:k], start=1):
        if item in relevant:
            return 1.0 / rank
    return 0.0


def compute_dcg_at_k(relevances: Sequence[float], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be greater than 0.")
    return sum((2 ** rel - 1) / math.log2(rank + 1) for rank, rel in enumerate(relevances[:k], start=1))


def compute_ndcg_at_k(predicted: Sequence[str], relevant: Set[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be greater than 0.")
    relevances = [1.0 if item in relevant else 0.0 for item in predicted[:k]]
    dcg = compute_dcg_at_k(relevances, k)
    ideal = sorted(relevances, reverse=True)
    idcg = compute_dcg_at_k(ideal, k)
    return dcg / idcg if idcg > 0 else 0.0


def _normalize_id(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_set(values: Iterable[Any]) -> Set[str]:
    return {_normalize_id(value) for value in values if _normalize_id(value)}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_atomic(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), suffix=".tmp", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.flush()
        temp_path = Path(handle.name)
    temp_path.replace(path)


def load_questions(input_path: Path | str | None = None) -> list[dict[str, Any]]:
    path = Path(input_path) if input_path is not None else EVAL_DIR / "questions.json"
    if not path.exists():
        raise FileNotFoundError(f"Evaluation questions not found: {path}")
    payload = _load_json(path)
    if not isinstance(payload, list):
        raise ValueError("Evaluation questions JSON must be an array.")
    return payload


def build_evaluation_report(
    questions: Sequence[dict[str, Any]],
    mode_results: dict[str, Sequence[dict[str, Any]]],
    strategy: str,
    k: int,
    model_identity: str,
    corpus_identity: str | None = None,
    hierarchy_identity: str | None = None,
    validate_hierarchy: bool = False,
    hierarchy_dir: Path | str | None = None,
) -> dict[str, Any]:
    if validate_hierarchy:
        if hierarchy_dir is None:
            raise ValueError("hierarchy_dir is required when validate_hierarchy=True.")
        hierarchy_path = Path(hierarchy_dir)
        if not hierarchy_path.exists():
            raise FileNotFoundError(f"Hierarchy directory not found: {hierarchy_path}")
        children_path = hierarchy_path / "children.json"
        parents_path = hierarchy_path / "parents.json"
        if not children_path.exists() or not parents_path.exists():
            raise FileNotFoundError("Hierarchy store missing children.json or parents.json.")
        children = _load_json(children_path)
        parents = _load_json(parents_path)
        hierarchy_child_ids = {_normalize_id(item.get("child_id")) for item in children if isinstance(item, dict)}
        hierarchy_parent_ids = {_normalize_id(item.get("parent_id")) for item in parents if isinstance(item, dict)}
    else:
        hierarchy_child_ids = set()
        hierarchy_parent_ids = set()

    summary: dict[str, dict[str, float]] = {}
    per_question_results: list[dict[str, Any]] = []
    warnings: list[str] = []

    mode_names = sorted(mode_results.keys())
    for mode in mode_names:
        summary[mode] = {
            "count": 0,
            "recall@k": 0.0,
            "parent_recall@k": 0.0,
            "mrr@k": 0.0,
            "ndcg@k": 0.0,
            "parent_mrr@k": 0.0,
            "parent_ndcg@k": 0.0,
            "latency_ms": 0.0,
            "context_chars": 0.0,
            "query_count": 0.0,
            "child_union_count": 0.0,
            "unique_relevant_parents": 0.0,
        }

    for question in questions:
        question_id = _normalize_id(question.get("question_id") or question.get("id") or "unknown")
        relevant_child_ids = _normalize_set(question.get("relevant_child_ids", []))
        relevant_parent_ids = _normalize_set(question.get("relevant_parent_ids", []))

        if question.get("needs_human_review"):
            warnings.append(f"Question {question_id} marked for human review.")

        for mode, results in mode_results.items():
            result = next(
                (
                    item
                    for item in results
                    if _normalize_id(item.get("question_id") or item.get("id") or "unknown") == question_id
                ),
                {},
            )
            if validate_hierarchy and relevant_child_ids:
                missing_children = sorted(relevant_child_ids - hierarchy_child_ids)
                if missing_children:
                    raise ValueError(f"Relevant child IDs not present in hierarchy store: {missing_children}")
            if validate_hierarchy and relevant_parent_ids:
                missing_parents = sorted(relevant_parent_ids - hierarchy_parent_ids)
                if missing_parents:
                    raise ValueError(f"Relevant parent IDs not present in hierarchy store: {missing_parents}")
            predicted_child_ids = [_normalize_id(item) for item in result.get("predicted_child_ids", [])]
            predicted_parent_ids = [_normalize_id(item) for item in result.get("predicted_parent_ids", [])]
            latency_ms = float(result.get("latency_ms", 0.0))
            context_chars = float(result.get("context_chars", 0.0))
            query_count = int(result.get("query_count", 0))
            child_union_count = int(result.get("child_union_count", 0))
            expansion_factor = float(result.get("expansion_factor", 0.0))
            generation_call_count = int(result.get("generation_call_count", 0))
            embedding_call_count = int(result.get("embedding_call_count", 0))

            child_recall = compute_recall_at_k(predicted_child_ids, relevant_child_ids, k)
            parent_recall = compute_recall_at_k(predicted_parent_ids, relevant_parent_ids, k)
            child_mrr = compute_mrr_at_k(predicted_child_ids, relevant_child_ids, k)
            child_ndcg = compute_ndcg_at_k(predicted_child_ids, relevant_child_ids, k)
            parent_mrr = compute_mrr_at_k(predicted_parent_ids, relevant_parent_ids, k)
            parent_ndcg = compute_ndcg_at_k(predicted_parent_ids, relevant_parent_ids, k)
            unique_relevant_parents = len(set(predicted_parent_ids) & relevant_parent_ids)

            summary[mode]["count"] += 1
            summary[mode]["recall@k"] += child_recall
            summary[mode]["parent_recall@k"] += parent_recall
            summary[mode]["mrr@k"] += child_mrr
            summary[mode]["ndcg@k"] += child_ndcg
            summary[mode]["parent_mrr@k"] += parent_mrr
            summary[mode]["parent_ndcg@k"] += parent_ndcg
            summary[mode]["latency_ms"] += latency_ms
            summary[mode]["context_chars"] += context_chars
            summary[mode]["query_count"] += query_count
            summary[mode]["child_union_count"] += child_union_count
            summary[mode]["unique_relevant_parents"] += unique_relevant_parents

            per_question_results.append(
                {
                    "question_id": question_id,
                    "mode": mode,
                    "question": question.get("question", ""),
                    "predicted_child_ids": predicted_child_ids,
                    "predicted_parent_ids": predicted_parent_ids,
                    "relevant_child_ids": sorted(relevant_child_ids),
                    "relevant_parent_ids": sorted(relevant_parent_ids),
                    "metrics": {
                        "child_recall@k": round(child_recall, 4),
                        "parent_recall@k": round(parent_recall, 4),
                        "mrr@k": round(child_mrr, 4),
                        "ndcg@k": round(child_ndcg, 4),
                        "parent_mrr@k": round(parent_mrr, 4),
                        "parent_ndcg@k": round(parent_ndcg, 4),
                        "unique_relevant_parents": unique_relevant_parents,
                        "query_count": query_count,
                        "child_union_count": child_union_count,
                        "context_chars": context_chars,
                        "expansion_factor": round(expansion_factor, 4),
                        "latency_ms": round(latency_ms, 3),
                        "generation_call_count": generation_call_count,
                        "embedding_call_count": embedding_call_count,
                    },
                }
            )

    aggregated: dict[str, dict[str, float]] = {}
    for mode, totals in summary.items():
        count = totals.pop("count")
        if count == 0:
            aggregated[mode] = {key: 0.0 for key in totals}
        else:
            aggregated[mode] = {
                "recall@k": round(totals["recall@k"] / count, 4),
                "parent_recall@k": round(totals["parent_recall@k"] / count, 4),
                "mrr@k": round(totals["mrr@k"] / count, 4),
                "ndcg@k": round(totals["ndcg@k"] / count, 4),
                "parent_mrr@k": round(totals["parent_mrr@k"] / count, 4),
                "parent_ndcg@k": round(totals["parent_ndcg@k"] / count, 4),
                "latency_ms": round(totals["latency_ms"] / count, 3),
                "context_chars": round(totals["context_chars"] / count, 1),
                "query_count": round(totals["query_count"] / count, 1),
                "child_union_count": round(totals["child_union_count"] / count, 1),
                "unique_relevant_parents": round(totals["unique_relevant_parents"] / count, 1),
            }

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "strategy": strategy,
        "k": k,
        "model_identity": model_identity,
        "corpus_identity": corpus_identity,
        "hierarchy_identity": hierarchy_identity,
        "config": {
            "strategy": strategy,
            "k": k,
            "model_identity": model_identity,
            "corpus_identity": corpus_identity,
            "hierarchy_identity": hierarchy_identity,
        },
        "metrics": aggregated,
        "warnings": warnings or ["No warnings."],
        "questions": len(questions),
        "modes": mode_names,
        "results": per_question_results,
    }


def write_report(payload: dict[str, Any], output_dir: Path | str | None = None, filename: str = "evaluation_report.json") -> Path:
    output_dir = Path(output_dir) if output_dir is not None else REPORT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    _write_atomic(output_path, payload)
    _write_atomic(output_dir / "latest_report.json", payload)
    return output_path
