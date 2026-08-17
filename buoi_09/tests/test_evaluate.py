import json
import tempfile
import unittest
from pathlib import Path

from rag_advanced.buoi_09 import evaluate


class TestBuoi09Evaluate(unittest.TestCase):
    def test_compute_metrics(self):
        predicted = ["c1", "c2", "c3", "c4"]
        relevant = {"c2", "c4"}

        self.assertEqual(evaluate.compute_recall_at_k(predicted, relevant, 2), 0.5)
        self.assertEqual(evaluate.compute_mrr_at_k(predicted, relevant, 4), 1.0 / 2)
        self.assertAlmostEqual(evaluate.compute_ndcg_at_k(predicted, relevant, 4), 0.6509209298071326, places=6)

    def test_build_evaluation_report_aggregates_modes(self):
        questions = [
            {
                "question_id": "Q01",
                "question": "Điều 8 quy định nhu cầu vốn không được cho vay?",
                "relevant_child_ids": ["c2", "c4"],
                "relevant_parent_ids": ["p2"],
                "needs_human_review": False,
            }
        ]
        mode_results = {
            "single_flat": [
                {
                    "question_id": "Q01",
                    "predicted_child_ids": ["c1", "c2"],
                    "predicted_parent_ids": ["p1"],
                    "latency_ms": 150,
                    "context_chars": 1024,
                    "query_count": 1,
                    "child_union_count": 2,
                    "expansion_factor": 1.0,
                    "generation_call_count": 0,
                    "embedding_call_count": 1,
                }
            ],
            "multi_parent": [
                {
                    "question_id": "Q01",
                    "predicted_child_ids": ["c2", "c4"],
                    "predicted_parent_ids": ["p2"],
                    "latency_ms": 320,
                    "context_chars": 6500,
                    "query_count": 3,
                    "child_union_count": 2,
                    "expansion_factor": 3.2,
                    "generation_call_count": 1,
                    "embedding_call_count": 3,
                }
            ],
        }

        report = evaluate.build_evaluation_report(
            questions=questions,
            mode_results=mode_results,
            strategy="hierarchical",
            k=3,
            model_identity="buoi_09-offline",
            corpus_identity="test-corpus",
            hierarchy_identity="test-hierarchy",
        )

        self.assertEqual(report["strategy"], "hierarchical")
        self.assertEqual(report["config"]["k"], 3)
        self.assertIn("single_flat", report["metrics"])
        self.assertIn("multi_parent", report["metrics"])
        self.assertAlmostEqual(report["metrics"]["single_flat"]["recall@k"], 0.5)
        self.assertAlmostEqual(report["metrics"]["multi_parent"]["recall@k"], 1.0)
        self.assertEqual(report["metrics"]["multi_parent"]["context_chars"], 6500.0)
        self.assertEqual(report["questions"], 1)

    def test_write_report_creates_latest(self):
        report = {"created_at": "2026-01-01T00:00:00Z", "metrics": {}, "results": []}
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            path = evaluate.write_report(report, output_dir=output, filename="eval.json")
            self.assertTrue(path.exists())
            self.assertTrue((output / "latest_report.json").exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), report)
            self.assertEqual(json.loads((output / "latest_report.json").read_text(encoding="utf-8")), report)

    def test_load_questions_validates_array(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "questions.json"
            path.write_text(json.dumps([{"question_id": "Q01", "question": "Test"}]), encoding="utf-8")
            loaded = evaluate.load_questions(path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["question_id"], "Q01")

    def test_build_report_raises_when_hierarchy_missing(self):
        questions = [
            {
                "question_id": "Q01",
                "question": "Test",
                "relevant_child_ids": ["c1"],
                "relevant_parent_ids": ["p1"],
            }
        ]
        mode_results = {"single_flat": [{"question_id": "Q01", "predicted_child_ids": ["c1"], "predicted_parent_ids": []}]}
        with self.assertRaises(FileNotFoundError):
            evaluate.build_evaluation_report(
                questions=questions,
                mode_results=mode_results,
                strategy="hierarchical",
                k=1,
                model_identity="buoi_09-offline",
                validate_hierarchy=True,
                hierarchy_dir=Path(tempfile.gettempdir()) / "missing-hierarchy",
            )


if __name__ == "__main__":
    unittest.main()
