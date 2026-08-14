"""Evaluation metrics and report generation for Buổi 08 retrieval ranking."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence, Set

BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"


def compute_recall_at_k(predicted: Sequence[int], relevant: Set[int], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be greater than 0.")
    hits = sum(1 for item in predicted[:k] if item in relevant)
    return hits / len(relevant) if relevant else 0.0


def compute_mrr_at_k(predicted: Sequence[int], relevant: Set[int], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be greater than 0.")
    for index, item in enumerate(predicted[:k], start=1):
        if item in relevant:
            return 1.0 / index
    return 0.0


def compute_dcg_at_k(relevances: Sequence[float], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be greater than 0.")
    return sum(
        (2 ** rel - 1) / math.log2(rank + 1)
        for rank, rel in enumerate(relevances[:k], start=1)
    )


def compute_ndcg_at_k(predicted: Sequence[int], relevant: Set[int], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be greater than 0.")
    relevances = [1.0 if item in relevant else 0.0 for item in predicted[:k]]
    dcg = compute_dcg_at_k(relevances, k)
    ideal_relevances = sorted(relevances, reverse=True)
    idcg = compute_dcg_at_k(ideal_relevances, k)
    return dcg / idcg if idcg > 0 else 0.0


def evaluate_run(predicted: Sequence[int], relevant: Set[int], k: int) -> dict[str, float]:
    return {
        "recall_at_k": compute_recall_at_k(predicted, relevant, k),
        "mrr_at_k": compute_mrr_at_k(predicted, relevant, k),
        "ndcg_at_k": compute_ndcg_at_k(predicted, relevant, k),
    }


def _normalize_chunk_id(value: Any) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("c") and stripped[1:].isdigit():
            return int(stripped[1:])
        if stripped.isdigit():
            return int(stripped)
    raise ValueError(f"Unsupported chunk id '{value}'.")


def build_evaluation_report(
    questions: Sequence[dict[str, Any]],
    mode_results: dict[str, Sequence[Sequence[str]]],
    strategy: str,
    k: int,
    model_name: str,
) -> dict[str, Any]:
    metrics: dict[str, dict[str, float]] = {}
    warnings: list[str] = []
    per_query_results: list[dict[str, Any]] = []

    for question in questions:
        relevant_ids = {_normalize_chunk_id(item) for item in question.get("relevant_chunk_ids", [])}
        if question.get("needs_human_review"):
            warnings.append(f"Question {question.get('query_id')} needs_human_review.")
        for mode, ranked_ids in mode_results.items():
            predicted_ids = [str(item) for item in ranked_ids[0]] if isinstance(ranked_ids, list) and ranked_ids else []
            if mode not in metrics:
                metrics[mode] = {"recall_at_k": 0.0, "mrr_at_k": 0.0, "ndcg_at_k": 0.0}
            predicted_numeric_ids = [
                _normalize_chunk_id(item)
                for item in predicted_ids
            ]
            mode_metrics = evaluate_run(predicted_numeric_ids, relevant_ids, k)
            metrics[mode]["recall_at_k"] += mode_metrics["recall_at_k"]
            metrics[mode]["mrr_at_k"] += mode_metrics["mrr_at_k"]
            metrics[mode]["ndcg_at_k"] += mode_metrics["ndcg_at_k"]
            per_query_results.append({
                "query_id": question.get("query_id") or question.get("id"),
                "mode": mode,
                "predicted": predicted_ids,
                "relevant": sorted(str(item) for item in relevant_ids),
                "metrics": mode_metrics,
            })

    if questions:
        for mode in metrics:
            count = len(questions)
            metrics[mode] = {
                "recall_at_k": round(metrics[mode]["recall_at_k"] / count, 4),
                "mrr_at_k": round(metrics[mode]["mrr_at_k"] / count, 4),
                "ndcg_at_k": round(metrics[mode]["ndcg_at_k"] / count, 4),
            }

    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "strategy": strategy,
        "k": k,
        "model_identity": model_name,
        "config": {
            "strategy": strategy,
            "k": k,
            "model_name": model_name,
        },
        "metrics": metrics,
        "warnings": warnings or ["No warnings."],
        "needs_human_review": any(question.get("needs_human_review") for question in questions),
        "winner": None,
        "results": per_query_results,
    }
    return report


def write_report(payload: dict[str, Any], output_dir: Path | str | None = None, filename: str = "evaluation_report.json") -> Path:
    output_dir = Path(output_dir) if output_dir is not None else REPORT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline evaluation for Buổi 08")
    parser.add_argument("--strategy", default="hierarchical")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--input", default=str(BASE_DIR / "eval" / "questions.json"))
    parser.add_argument("--output", default=str(REPORT_DIR / "evaluation_report.json"))
    args = parser.parse_args()

    questions = json.loads(Path(args.input).read_text(encoding="utf-8"))
    mode_results = {
        "bm25": [["c1", "c3"]],
        "semantic": [["c3", "c1"]],
        "hybrid": [["c1", "c2"]],
        "hybrid_rerank": [["c2", "c1"]],
    }
    report = build_evaluation_report(
        questions=questions,
        mode_results=mode_results,
        strategy=args.strategy,
        k=args.k,
        model_name="offline-fixture",
    )
    output_path = write_report(report, output_dir=Path(args.output).parent, filename=Path(args.output).name)
    print(json.dumps({"report_path": str(output_path), "report": report}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
