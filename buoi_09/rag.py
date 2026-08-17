"""Buổi 09 CLI entrypoint and Baseline snapshot loader.

This module is independent of Buổi 08 runtime and uses the copied Buổi 08
baseline implementation from `advanced_rag.py`.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    from .advanced_rag import (
        DEFAULT_CONFIG,
        VALID_STRATEGIES,
        _safe_print_json,
        get_status,
        load_chunks,
        run_query,
        run_bm25,
        run_semantic,
        run_hybrid,
        prepare_semantic,
        _compare_modes,
    )
except ImportError:
    from advanced_rag import (
        DEFAULT_CONFIG,
        VALID_STRATEGIES,
        _safe_print_json,
        get_status,
        load_chunks,
        run_query,
        run_bm25,
        run_semantic,
        run_hybrid,
        prepare_semantic,
        _compare_modes,
    )


def compare(question: str, top_k: int, strategy: str, input_dir: Path | str | None = None) -> dict[str, Any]:
    return _compare_modes(question, top_k, strategy, input_dir=input_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Buoi 09 Advanced RAG CLI")
    subparsers = parser.add_subparsers(dest="command")

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--strategy", choices=sorted(VALID_STRATEGIES), default="hierarchical")

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("--question", required=True)
    query_parser.add_argument("--top-k", type=int, default=DEFAULT_CONFIG["default_top_k"])
    query_parser.add_argument("--strategy", choices=sorted(VALID_STRATEGIES), default="hierarchical")
    query_parser.add_argument("--mode", choices=["bm25", "semantic", "hybrid", "hybrid_rerank"], default="hybrid")

    bm25_parser = subparsers.add_parser("bm25")
    bm25_parser.add_argument("--question", required=True)
    bm25_parser.add_argument("--candidate-k", type=int, default=DEFAULT_CONFIG["default_top_k"])
    bm25_parser.add_argument("--strategy", choices=sorted(VALID_STRATEGIES), default="hierarchical")

    semantic_parser = subparsers.add_parser("semantic")
    semantic_parser.add_argument("--question", required=True)
    semantic_parser.add_argument("--candidate-k", type=int, default=DEFAULT_CONFIG["default_top_k"])
    semantic_parser.add_argument("--strategy", choices=sorted(VALID_STRATEGIES), default="hierarchical")

    hybrid_parser = subparsers.add_parser("hybrid")
    hybrid_parser.add_argument("--question", required=True)
    hybrid_parser.add_argument("--candidate-k", type=int, default=DEFAULT_CONFIG["default_top_k"])
    hybrid_parser.add_argument("--strategy", choices=sorted(VALID_STRATEGIES), default="hierarchical")

    prepare_parser = subparsers.add_parser("prepare-semantic")
    prepare_parser.add_argument("--strategy", choices=sorted(VALID_STRATEGIES), default="hierarchical")
    prepare_parser.add_argument("--input-dir", default=None)

    rerank_parser = subparsers.add_parser("rerank")
    rerank_parser.add_argument("--question", required=True)
    rerank_parser.add_argument("--top-k", type=int, default=DEFAULT_CONFIG["default_top_k"])
    rerank_parser.add_argument("--strategy", choices=sorted(VALID_STRATEGIES), default="hierarchical")
    rerank_parser.add_argument("--input-dir", default=None)

    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--question", required=True)
    compare_parser.add_argument("--top-k", type=int, default=DEFAULT_CONFIG["default_top_k"])
    compare_parser.add_argument("--strategy", choices=sorted(VALID_STRATEGIES), default="hierarchical")
    compare_parser.add_argument("--input-dir", default=None)

    args = parser.parse_args()
    if args.command == "status":
        _safe_print_json(get_status(args.strategy))
    elif args.command == "query":
        _safe_print_json(run_query(args.question, args.top_k, args.strategy, args.mode))
    elif args.command == "rerank":
        _safe_print_json(run_query(args.question, args.top_k, args.strategy, "hybrid_rerank", input_dir=args.input_dir))
    elif args.command == "compare":
        _safe_print_json(_compare_modes(args.question, args.top_k, args.strategy, input_dir=args.input_dir))
    elif args.command == "bm25":
        _safe_print_json(run_bm25(args.question, args.candidate_k, args.strategy))
    elif args.command == "semantic":
        _safe_print_json(run_semantic(args.question, args.candidate_k, args.strategy))
    elif args.command == "hybrid":
        _safe_print_json(run_hybrid(args.question, args.candidate_k, args.strategy))
    elif args.command == "prepare-semantic":
        _safe_print_json(prepare_semantic(args.strategy, args.input_dir))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
