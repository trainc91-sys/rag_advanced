"""Unit tests for BM25 lexical retrieval in Buổi 08."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rag_foundation.buoi_08 import advanced_rag


class TestBM25(unittest.TestCase):
    def test_tokenize_vi_legal_splits_numbers_and_words(self):
        text = "Điều 1: Thử nghiệm, có dấu câu!"
        tokens = advanced_rag.tokenize_vi_legal(text)

        self.assertEqual(tokens, ["điều", "1", "thử", "nghiệm", "có", "dấu", "câu"])

    def test_tokenize_vi_legal_preserves_dieu_khoan_tokens(self):
        text = "Điều 7, Khoản 2: quy định rõ." 
        tokens = advanced_rag.tokenize_vi_legal(text)

        self.assertEqual(tokens, ["điều", "7", "khoản", "2", "quy", "định", "rõ"])

    def test_tokenize_vi_legal_returns_empty_for_whitespace(self):
        self.assertEqual(advanced_rag.tokenize_vi_legal("   \t\n"), [])

    def test_query_bm25_ranks_relevant_chunk_first(self):
        chunks = [
            {
                "chunk_id": "c1",
                "strategy": "hierarchical",
                "source": "Doc A",
                "page_start": 1,
                "page_end": 1,
                "text": "Nội dung điều 1 và nội dung chung.",
            },
            {
                "chunk_id": "c2",
                "strategy": "hierarchical",
                "source": "Doc A",
                "page_start": 2,
                "page_end": 2,
                "text": "Nội dung điều 2 và quy định khác.",
            },
            {
                "chunk_id": "c3",
                "strategy": "hierarchical",
                "source": "Doc A",
                "page_start": 3,
                "page_end": 3,
                "text": "Thông tin giải thích một số thuật ngữ.",
            },
            {
                "chunk_id": "c4",
                "strategy": "hierarchical",
                "source": "Doc A",
                "page_start": 4,
                "page_end": 4,
                "text": "Các điều khoản không liên quan.",
            },
        ]
        results = advanced_rag._query_bm25("Điều 1 là gì?", chunks, candidate_k=4)

        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]["chunk_id"], "c1")
        self.assertGreaterEqual(results[0]["bm25_score"], results[1]["bm25_score"])
        self.assertGreaterEqual(results[1]["bm25_score"], results[2]["bm25_score"])

    def test_run_bm25_loads_chunks_and_returns_results(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fixture_path = temp_path / "chunks_bm25_sample.json"
            fixture_path.write_text(
                "[\n"
                "  {\n"
                "    \"chunk_id\": \"c1\",\n"
                "    \"strategy\": \"hierarchical\",\n"
                "    \"source\": \"Doc A\",\n"
                "    \"page_start\": 1,\n"
                "    \"page_end\": 1,\n"
                "    \"text\": \"Quy định về điều kiện.\"\n"
                "  },\n"
                "  {\n"
                "    \"chunk_id\": \"c2\",\n"
                "    \"strategy\": \"hierarchical\",\n"
                "    \"source\": \"Doc A\",\n"
                "    \"page_start\": 2,\n"
                "    \"page_end\": 2,\n"
                "    \"text\": \"Giải thích một số thuật ngữ.\"\n"
                "  }\n"
                "]",
                encoding="utf-8",
            )

            result = advanced_rag.run_bm25(
                question="Quy định điều kiện",
                candidate_k=2,
                strategy="hierarchical",
                input_dir=temp_path,
            )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["strategy"], "hierarchical")
        self.assertEqual(result["candidate_k"], 2)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["chunk_id"], "c1")

    def test_run_bm25_raises_for_invalid_strategy(self):
        with self.assertRaises(ValueError):
            advanced_rag.run_bm25("Test", 1, "invalid")


if __name__ == "__main__":
    unittest.main()
