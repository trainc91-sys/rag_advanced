import unittest
from pathlib import Path
import tempfile
import json

from rag_advanced.buoi_09.app import (
    build_query_cards,
    build_query_matrix,
    build_parent_tree_data,
    build_mode_comparison_rows,
    format_citation,
    format_hierarchy_store_status,
    format_status_message,
    load_hierarchy_counts,
)


class TestBuoi09AppHelpers(unittest.TestCase):
    def test_build_query_cards(self):
        query_result = {
            "query_set": {
                "queries": [
                    {"query_id": "Q0", "text": "Câu hỏi gốc", "origin": "original", "focus": "original_intent"},
                    {"query_id": "Q1", "text": "Paraphrase query", "origin": "generated", "focus": "paraphrase"},
                ]
            },
            "trace": {
                "queries": [
                    {"query_id": "Q0", "result_count": 3, "retrieval_latency_ms": 12.3, "error": None},
                    {"query_id": "Q1", "result_count": 1, "retrieval_latency_ms": 22.4, "error": "timeout"},
                ]
            },
        }

        cards = build_query_cards(query_result)
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]["query_id"], "Q0")
        self.assertEqual(cards[0]["result_count"], 3)
        self.assertEqual(cards[1]["origin"], "generated")
        self.assertEqual(cards[1]["error"], "timeout")

    def test_build_query_matrix(self):
        query_result = {
            "query_set": {"queries": [{"query_id": "Q0"}, {"query_id": "Q1"}]},
            "child_hits": [
                {
                    "child_id": "src:1",
                    "source": "DocA",
                    "page_start": 1,
                    "page_end": 2,
                    "support_query_count": 2,
                    "multi_query_rrf_score": 0.85,
                    "per_query_ranks": {"Q0": 1, "Q1": 3},
                },
                {
                    "child_id": "src:2",
                    "source": "DocB",
                    "page_start": 3,
                    "page_end": 3,
                    "support_query_count": 1,
                    "multi_query_rrf_score": 0.42,
                    "per_query_ranks": {"Q0": 2},
                },
            ],
        }

        queries, rows = build_query_matrix(query_result)
        self.assertEqual(queries, ["Q0", "Q1"])
        self.assertEqual(rows[0]["Q0"], 1)
        self.assertEqual(rows[0]["Q1"], 3)
        self.assertEqual(rows[1]["Q1"], "—")
        self.assertEqual(rows[1]["pages"], "3-3")

    def test_build_parent_tree_data_with_anchor_child(self):
        parent_result = {
            "selected_parents": [
                {
                    "parent_id": "P1",
                    "structural_path": {"chapter": "Chương 1", "article": "Điều 2"},
                    "source": "DocA",
                    "page_start": 1,
                    "page_end": 5,
                    "parent_rank": 1,
                    "parent_rerank_rank": 1,
                    "parent_rrf_score": 4.5,
                    "parent_rerank_score": 0.98,
                    "warnings": ["ambiguous_path"],
                    "ambiguous": True,
                    "supporting_child_ids": ["src:1", "src:2"],
                    "anchor_child_id": "src:2",
                    "support_query_ids": ["Q0", "Q1"],
                    "text": "Nội dung parent mở rộng.",
                }
            ]
        }

        tree = build_parent_tree_data(parent_result)
        self.assertEqual(len(tree), 1)
        self.assertIn("Chương 1", tree[0]["path"])
        self.assertTrue(tree[0]["ambiguous"])
        self.assertEqual(tree[0]["supporting_children"][1]["is_anchor"], True)
        self.assertEqual(tree[0]["supporting_children"][1]["child_id"], "src:2")

    def test_build_parent_tree_data_uses_child_specific_query_ids(self):
        parent_result = {
            "selected_parents": [
                {
                    "parent_id": "P1",
                    "structural_path": {"chapter": "Chương 1", "article": "Điều 2"},
                    "source": "DocA",
                    "page_start": 1,
                    "page_end": 5,
                    "supporting_child_ids": ["src:1", "src:2"],
                    "supporting_child_query_ids": {
                        "src:1": ["Q0"],
                        "src:2": ["Q0", "Q1"],
                    },
                    "text": "Nội dung parent mở rộng.",
                }
            ]
        }

        tree = build_parent_tree_data(parent_result)
        self.assertEqual(tree[0]["supporting_children"][0]["query_ids"], ["Q0"])
        self.assertEqual(tree[0]["supporting_children"][1]["query_ids"], ["Q0", "Q1"])

    def test_build_parent_tree_data_falls_back_to_initial_ranking(self):
        parent_result = {
            "selected_parents": [
                {
                    "parent_id": "P1",
                    "structural_path": {"article": "Điều 2"},
                    "source": "DocA",
                    "page_start": 1,
                    "page_end": 5,
                    "parent_rank": 2,
                    "parent_rrf_score": 0.1234,
                    "text": "Nội dung parent mở rộng.",
                }
            ]
        }

        tree = build_parent_tree_data(parent_result)
        self.assertEqual(tree[0]["parent_rerank_rank"], 2)
        self.assertEqual(tree[0]["parent_rerank_score"], 0.1234)

    def test_build_mode_comparison_rows(self):
        compare_result = {
            "modes": [
                {
                    "mode": "single_flat",
                    "raw": {
                        "status": "ready",
                        "accepted_evidence": [
                            {"evidence_id": "src:1", "source": "DocA"},
                            {"evidence_id": "src:2", "source": "DocB"},
                        ],
                        "child_hits": [{}, {}],
                        "trace": {"child_chars": 432, "warnings": ["warning"]},
                        "query_set": {"generation_call_count": 1},
                    },
                },
                {
                    "mode": "single_parent",
                    "raw": {
                        "status": "ready",
                        "accepted_evidence": [
                            {"evidence_id": "P1", "parent_id": "parent:1", "source": "DocA"},
                        ],
                        "child_hits": [{}],
                        "parent_candidates": [{"parent_id": "parent:1"}],
                        "trace": {"parent_chars": 789, "warnings": []},
                        "query_set": {"generation_call_count": 0},
                    },
                },
            ]
        }

        rows = build_mode_comparison_rows(compare_result)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["mode"], "single_flat")
        self.assertEqual(rows[0]["unit_type"], "child")
        self.assertIn("src:1", rows[0]["evidence_ids"])
        self.assertEqual(rows[1]["unit_type"], "parent")
        self.assertEqual(rows[1]["parent_count"], 1)

    def test_build_mode_comparison_rows_accepts_mode_mapping(self):
        compare_result = {
            "modes": {
                "single_flat": {
                    "status": "ready",
                    "raw": {
                        "status": "ready",
                        "accepted_evidence": [{"evidence_id": "src:1", "source": "DocA"}],
                        "child_hits": [{}],
                        "trace": {"child_chars": 100, "warnings": []},
                        "query_set": {"generation_call_count": 1},
                    },
                },
                "single_parent": {
                    "status": "ready",
                    "raw": {
                        "status": "ready",
                        "accepted_evidence": [{"evidence_id": "P1", "parent_id": "parent:1", "source": "DocA"}],
                        "child_hits": [{}],
                        "parent_candidates": [{"parent_id": "parent:1"}],
                        "trace": {"parent_chars": 200, "warnings": []},
                        "query_set": {"generation_call_count": 0},
                    },
                },
            }
        }

        rows = build_mode_comparison_rows(compare_result)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["mode"], "single_flat")
        self.assertEqual(rows[1]["mode"], "single_parent")

    def test_format_citation(self):
        citation = {"evidence_id": "src:1", "parent_id": "P1", "anchor_child_id": "src:2"}
        self.assertEqual(format_citation(citation), "src:1: parent=P1, anchor_child=src:2")

    def test_format_status_message_unknown(self):
        self.assertEqual(format_status_message("unknown_status"), "Trạng thái không xác định. Xin kiểm tra lại.")

    def test_format_hierarchy_store_status_handles_none_reason(self):
        label, reason = format_hierarchy_store_status({"ready": True, "reason": None})
        self.assertEqual(label, "Ready")
        self.assertEqual(reason, "—")

    def test_load_hierarchy_counts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            parent_path = Path(tmpdir) / "parents.json"
            children_path = Path(tmpdir) / "children.json"
            children_path.write_text(json.dumps([
                {"child_id": "src:1", "ambiguous": False},
                {"child_id": "src:2", "ambiguous": True},
            ]), encoding="utf-8")
            parent_path.write_text(json.dumps([
                {"parent_id": "P1", "child_ids": ["src:1"]}
            ]), encoding="utf-8")

            counts = load_hierarchy_counts(Path(tmpdir))
            self.assertEqual(counts["child_count"], 2)
            self.assertEqual(counts["parent_count"], 1)
            self.assertEqual(counts["ambiguous_count"], 1)


if __name__ == "__main__":
    unittest.main()
