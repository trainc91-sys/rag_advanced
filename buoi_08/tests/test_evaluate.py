import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from buoi_08 import evaluate


class TestEvaluationReport(unittest.TestCase):
    def test_build_evaluation_report_marks_human_review_and_omits_winner(self):
        questions = [
            {
                "query_id": "Q01",
                "question": "Điều 7 quy định như thế nào?",
                "relevant_chunk_ids": ["c1", "c2"],
                "scope": "in_scope",
                "needs_human_review": True,
            }
        ]
        mode_results = {
            "bm25": [["c1", "c3"]],
            "semantic": [["c3", "c1"]],
            "hybrid": [["c1", "c2"]],
            "hybrid_rerank": [["c2", "c1"]],
        }

        report = evaluate.build_evaluation_report(
            questions=questions,
            mode_results=mode_results,
            strategy="hierarchical",
            k=2,
            model_name="mock-model",
        )

        self.assertIn("metrics", report)
        self.assertIn("bm25", report["metrics"])
        self.assertTrue(report["needs_human_review"])
        self.assertIn("needs_human_review", report["warnings"][0].lower())
        self.assertIsNone(report["winner"])
        self.assertEqual(report["config"]["strategy"], "hierarchical")
        self.assertEqual(report["config"]["k"], 2)

    def test_write_report_writes_json_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "report.json"
            payload = {"metrics": {}, "warnings": []}
            written_path = evaluate.write_report(payload, output_dir=Path(temp_dir), filename="report.json")

            self.assertEqual(written_path, output_path)
            self.assertTrue(output_path.exists())
            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8")), payload)
