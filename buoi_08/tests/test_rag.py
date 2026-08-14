"""Unit tests for Buổi 08 Advanced RAG."""

from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from rag_foundation.buoi_08 import advanced_rag, evaluate, rag


def _write_fixture_file(path: Path) -> None:
    path.write_text(
        """[
  {
    "chunk_id": "c1",
    "strategy": "hierarchical",
    "source": "Văn bản A",
    "page_start": 1,
    "page_end": 1,
    "text": "Nội dung điều 1."
  },
  {
    "chunk_id": "c2",
    "strategy": "hierarchical",
    "source": "Văn bản A",
    "page_start": 2,
    "page_end": 2,
    "text": "Nội dung điều 2."
  },
  {
    "chunk_id": "c3",
    "strategy": "semantic",
    "source": "Văn bản B",
    "page_start": 1,
    "page_end": 1,
    "text": "Thông tin tổng quát."
  }
]""",
        encoding="utf-8",
    )


class TestAdvancedRAG(unittest.TestCase):
    def test_rag_module_imports(self):
        self.assertTrue(hasattr(rag, "run_query"))
        self.assertTrue(hasattr(advanced_rag, "load_chunks"))

    def test_cli_parser_supports_bm25_command(self):
        parser = advanced_rag._build_cli_parser()
        args = parser.parse_args(["bm25", "--strategy", "hierarchical", "--question", "Điều 7"])
        self.assertEqual(args.command, "bm25")
        self.assertEqual(args.strategy, "hierarchical")
        self.assertEqual(args.question, "Điều 7")

    def test_load_chunks_filters_strategy(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fixture_path = temp_path / "chunks_advanced_sample.json"
            _write_fixture_file(fixture_path)

            chunks = advanced_rag.load_chunks(temp_path, strategy="hierarchical")
            self.assertEqual(len(chunks), 2)
            self.assertTrue(all(chunk["strategy"] == "hierarchical" for chunk in chunks))
            self.assertEqual(chunks[0]["chunk_id"], "c1")
            self.assertEqual(chunks[1]["chunk_id"], "c2")

    def test_fuse_rrf_combines_ranked_results(self):
        bm25_results = [
            {
                "chunk_id": "c1",
                "text": "Doc 1",
                "source": "A",
                "page_start": 1,
                "page_end": 1,
                "bm25_rank": 1,
                "bm25_score": 2.0,
            },
            {
                "chunk_id": "c2",
                "text": "Doc 2",
                "source": "A",
                "page_start": 1,
                "page_end": 1,
                "bm25_rank": 2,
                "bm25_score": 1.0,
            },
        ]
        semantic_results = [
            {
                "chunk_id": "c2",
                "text": "Doc 2",
                "source": "A",
                "page_start": 1,
                "page_end": 1,
                "semantic_rank": 1,
                "semantic_distance": 0.9,
            },
            {
                "chunk_id": "c3",
                "text": "Doc 3",
                "source": "A",
                "page_start": 1,
                "page_end": 1,
                "semantic_rank": 2,
                "semantic_distance": 0.8,
            },
        ]
        fused = advanced_rag._fuse_rrf(
            bm25_results,
            semantic_results,
            rrf_k=10,
            bm25_weight=1.0,
            semantic_weight=1.0,
        )
        self.assertEqual([item["chunk_id"] for item in fused], ["c2", "c1", "c3"])
        self.assertTrue(fused[0]["rrf_score"] > fused[1]["rrf_score"])
        self.assertEqual(fused[0]["matched_by"], ["bm25", "semantic"])

    def test_evaluation_metrics(self):
        predicted = [3, 1, 2, 4]
        relevant = {1, 2}
        self.assertEqual(evaluate.compute_recall_at_k(predicted, relevant, 2), 0.5)
        self.assertAlmostEqual(evaluate.compute_mrr_at_k(predicted, relevant, 4), 0.5)
        self.assertAlmostEqual(evaluate.compute_ndcg_at_k(predicted, relevant, 4), 0.6934264036172708, places=6)

    @patch("rag_foundation.buoi_08.advanced_rag._query_bm25")
    @patch("rag_foundation.buoi_08.advanced_rag._query_semantic")
    @patch("rag_foundation.buoi_08.advanced_rag._generate_answer")
    def test_run_query_hybrid(self, mock_generate, mock_semantic, mock_bm25):
        mock_bm25.return_value = [
            {
                "chunk_id": "c1",
                "text": "Nội dung 1",
                "source": "A",
                "page_start": 1,
                "page_end": 1,
                "bm25_rank": 1,
                "bm25_score": 1.0,
            }
        ]
        mock_semantic.return_value = [
            {
                "chunk_id": "c1",
                "text": "Nội dung 1",
                "source": "A",
                "page_start": 1,
                "page_end": 1,
                "semantic_rank": 1,
                "semantic_distance": 0.3,
            }
        ]
        mock_generate.return_value = "Trả lời giả lập."

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fixture_path = temp_path / "chunks_advanced_sample.json"
            _write_fixture_file(fixture_path)

            result = advanced_rag.run_query(
                question="Nội dung nào liên quan?",
                top_k=1,
                strategy="hierarchical",
                mode="hybrid",
                input_dir=temp_path,
            )

        self.assertEqual(result["status"], "answered")
        self.assertEqual(result["mode"], "hybrid")
        self.assertEqual(result["top_k"], 1)
        self.assertEqual(result["answer"], "Trả lời giả lập.")
        self.assertEqual(len(result["evidence"]), 1)
        self.assertIn("retrieval_ms", result["timings"])

    def test_get_status_is_read_only(self):
        fake_client = MagicMock()
        fake_client.get_collection.return_value = None
        with patch.object(advanced_rag, "_create_chroma_client", return_value=fake_client):
            with patch.object(advanced_rag, "load_chunks", return_value=[]):
                status = advanced_rag.get_status("hierarchical")
        self.assertFalse(status["collection_exists"])
        self.assertIsNone(status["collection_compatible"])
        self.assertEqual(status["record_count"], 0)
        self.assertFalse(status["details"]["bm25_ready"])

    def test_run_hybrid_returns_trace_and_results(self):
        mock_bm25 = [
            {
                "chunk_id": "c1",
                "text": "Nội dung 1",
                "source": "Văn bản A",
                "page_start": 1,
                "page_end": 1,
                "bm25_rank": 1,
                "bm25_score": 2.0,
            }
        ]
        mock_semantic = [
            {
                "chunk_id": "c2",
                "text": "Nội dung 2",
                "source": "Văn bản B",
                "page_start": 2,
                "page_end": 2,
                "semantic_rank": 1,
                "semantic_distance": 0.1,
            }
        ]
        with patch.object(advanced_rag, "_query_bm25", return_value=mock_bm25) as patch_bm25:
            with patch.object(advanced_rag, "_query_semantic", return_value=mock_semantic) as patch_semantic:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    fixture_path = temp_path / "chunks_advanced_sample.json"
                    _write_fixture_file(fixture_path)

                    result = advanced_rag.run_hybrid(
                        question="Câu hỏi hybrid?",
                        candidate_k=2,
                        strategy="hierarchical",
                        input_dir=temp_path,
                    )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["candidate_k"], 2)
        self.assertEqual(result["bm25_candidate_count"], 1)
        self.assertEqual(result["semantic_candidate_count"], 1)
        self.assertEqual(result["union_count"], 2)
        self.assertEqual(result["overlap_count"], 0)
        self.assertEqual(result["fused_count"], 2)
        self.assertIn("fusion_ms", result["latency_ms"])
        patch_bm25.assert_called_once()
        patch_semantic.assert_called_once()

    def test_query_semantic_uses_chromadb_compatible_include(self):
        class FakeCollection:
            metadata = {
                "strategy": "hierarchical",
                "embedding_model": advanced_rag.DEFAULT_CONFIG["gemini_embedding_model"],
                "embedding_dim": advanced_rag.DEFAULT_CONFIG["gemini_embedding_dim"],
                "distance_metric": "cosine",
                "schema_version": "1",
            }
            configuration = {"hnsw": {"space": "cosine"}}

            def __init__(self):
                self.last_include = None

            def query(self, query_embeddings, n_results, include):
                self.last_include = include
                return {
                    "ids": [["c1"]],
                    "metadatas": [[{"source": "A", "page_start": 1, "page_end": 1}]],
                    "documents": [["Nội dung 1"]],
                    "distances": [[0.1]],
                }

        fake_collection = FakeCollection()
        fake_client = MagicMock()
        fake_client.get_collection.return_value = fake_collection

        with patch.object(advanced_rag, "_create_chroma_client", return_value=fake_client):
            with patch.object(advanced_rag, "_create_query_embedding", return_value=[0.1]):
                result = advanced_rag._query_semantic("test", "collection", "hierarchical", 1)

        self.assertEqual(result[0]["chunk_id"], "c1")
        self.assertNotIn("ids", fake_collection.last_include)

    def test_rerank_is_lazy_loaded_only_for_hybrid_rerank(self):
        candidate = {
            "document_index": 0,
            "chunk_id": "c1",
            "text": "Nội dung 1",
            "source": "A",
            "page_start": 1,
            "page_end": 1,
            "bm25_rank": 1,
            "semantic_rank": 1,
            "fused_rank": 1,
        }
        with patch.object(advanced_rag, "_load_reranker", side_effect=RuntimeError("should not load")) as mock_load:
            result = advanced_rag._select_mode_candidates(
                question="test",
                corpus=["Nội dung 1"],
                strategy="hierarchical",
                mode="bm25",
                top_k=1,
            )
        self.assertEqual(result[0]["document_index"], 0)
        mock_load.assert_not_called()

        with patch.object(advanced_rag, "_query_bm25", return_value=[candidate]):
            with patch.object(advanced_rag, "_query_semantic", return_value=[candidate]):
                with patch.object(advanced_rag, "_load_reranker", return_value=(None, None, "cpu")) as mock_load:
                    with patch.object(advanced_rag, "_rerank", return_value=[{**candidate, "rerank_score": 0.9, "rerank_rank": 1, "rank_change": 0}]) as mock_rerank:
                        _ = advanced_rag._select_mode_candidates(
                            question="test",
                            corpus=["Nội dung 1"],
                            strategy="hierarchical",
                            mode="hybrid_rerank",
                            top_k=1,
                        )
        mock_rerank.assert_called_once()

    def test_rerank_injection_and_ranking(self):
        candidates = [
            {"document_index": 0, "chunk_id": "c1", "fused_rank": 1},
            {"document_index": 1, "chunk_id": "c2", "fused_rank": 2},
        ]
        corpus = ["A", "B"]

        def fake_reranker(question, candidates_arg, corpus_arg):
            self.assertEqual(question, "query")
            self.assertEqual(corpus_arg, corpus)
            self.assertEqual(len(candidates_arg), 2)
            return [
                {"rerank_raw_score": 1.0},
                {"rerank_raw_score": 2.0},
            ]

        reranked = advanced_rag._rerank("query", candidates, corpus, reranker=fake_reranker)
        self.assertEqual(reranked[0]["chunk_id"], "c2")
        self.assertEqual(reranked[0]["rerank_rank"], 1)
        self.assertEqual(reranked[0]["rank_change"], 1.0)
        self.assertAlmostEqual(reranked[0]["rerank_score"], 1.0 / (1.0 + math.exp(-2.0)))
        self.assertEqual(len(reranked), advanced_rag.CONFIG["final_top_k"] if advanced_rag.CONFIG["final_top_k"] < 2 else 2)

    def test_reranker_unavailable_returns_status(self):
        candidate = {
            "document_index": 0,
            "chunk_id": "c1",
            "text": "Nội dung 1",
            "source": "A",
            "page_start": 1,
            "page_end": 1,
            "bm25_rank": 1,
            "semantic_rank": 1,
            "fused_rank": 1,
        }
        with patch.object(advanced_rag, "_query_bm25", return_value=[candidate]):
            with patch.object(advanced_rag, "_query_semantic", return_value=[candidate]):
                with patch.object(advanced_rag, "_rerank", side_effect=advanced_rag.RerankerUnavailableError("download failed")):
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir)
                        fixture_path = temp_path / "chunks_advanced_sample.json"
                        _write_fixture_file(fixture_path)

                        result = advanced_rag.run_query(
                            question="Câu hỏi?",
                            top_k=1,
                            strategy="hierarchical",
                            mode="hybrid_rerank",
                            input_dir=temp_path,
                        )
        self.assertEqual(result["status"], "reranker_unavailable")
        self.assertEqual(result["answer"], "")
        self.assertEqual(result["evidence"], [])
        self.assertIn("warnings", result)

    def test_fuse_rrf_metadata_mismatch_raises(self):
        bm25_results = [
            {
                "chunk_id": "c1",
                "text": "Nội dung A",
                "source": "Văn bản A",
                "page_start": 1,
                "page_end": 1,
                "bm25_rank": 1,
                "bm25_score": 2.0,
            }
        ]
        semantic_results = [
            {
                "chunk_id": "c1",
                "text": "Nội dung khác",
                "source": "Văn bản B",
                "page_start": 1,
                "page_end": 1,
                "semantic_rank": 1,
                "semantic_distance": 0.1,
            }
        ]
        with self.assertRaises(ValueError):
            advanced_rag._fuse_rrf(
                bm25_results,
                semantic_results,
                rrf_k=60,
                bm25_weight=1.0,
                semantic_weight=1.0,
            )

    def test_prepare_semantic_requires_api_key(self):
        original_key = advanced_rag.DEFAULT_CONFIG["gemini_api_key"]
        advanced_rag.DEFAULT_CONFIG["gemini_api_key"] = None
        try:
            with self.assertRaises(RuntimeError):
                advanced_rag.prepare_semantic("hierarchical")
        finally:
            advanced_rag.DEFAULT_CONFIG["gemini_api_key"] = original_key

    @patch("rag_foundation.buoi_08.advanced_rag._generate_answer")
    @patch("rag_foundation.buoi_08.advanced_rag._run_retrieval_mode")
    @patch("rag_foundation.buoi_08.advanced_rag.load_chunks")
    def test_compare_does_not_call_generation(self, mock_load_chunks, mock_run_retrieval, mock_generate):
        mock_load_chunks.return_value = [
            {
                "chunk_id": "c1",
                "strategy": "hierarchical",
                "source": "A",
                "page_start": 1,
                "page_end": 1,
                "text": "Nội dung test.",
            }
        ]

        def stage_for_mode(question, chunks, strategy, mode, top_k):
            return {
                "mode": mode,
                "candidates": [
                    {
                        "chunk_id": "c1",
                        "bm25_rank": 1,
                        "semantic_rank": 1,
                        "fused_rank": 1,
                        "rerank_rank": 1,
                        "rank_change": 0,
                    }
                ],
                "bm25_latency_ms": 1.0,
                "semantic_latency_ms": 1.0,
                "fusion_latency_ms": 0.0,
                "rerank_latency_ms": 0.0,
                "latency_ms": 2.0,
            }

        mock_run_retrieval.side_effect = stage_for_mode
        result = advanced_rag._compare_modes("Câu hỏi?", 1, "hierarchical", input_dir=Path("."))

        mock_generate.assert_not_called()
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["modes"]), 4)
        self.assertTrue(result["comparison_table"])

    def test_run_semantic_returns_candidates(self):
        expected_results = [
            {
                "chunk_id": "c1",
                "text": "Sample text 1.",
                "source": "Doc A",
                "page_start": 1,
                "page_end": 1,
                "semantic_rank": 1,
                "semantic_distance": 0.1,
            }
        ]
        with patch.object(advanced_rag, "_query_semantic", return_value=expected_results):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                fixture_path = temp_path / "chunks_advanced_sample.json"
                _write_fixture_file(fixture_path)

                result = advanced_rag.run_semantic(
                    question="Câu hỏi kiểm thử",
                    candidate_k=1,
                    strategy="hierarchical",
                    input_dir=temp_path,
                )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["strategy"], "hierarchical")
        self.assertEqual(result["candidate_k"], 1)
        self.assertEqual(result["results"], expected_results)

    def test_run_bm25_accepted_candidates_use_semantic_gate(self):
        mock_bm25 = [
            {
                "chunk_id": "c1",
                "text": "Nội dung 1",
                "source": "A",
                "page_start": 1,
                "page_end": 1,
                "bm25_rank": 1,
                "bm25_score": 1.0,
            }
        ]
        mock_semantic = [
            {
                "chunk_id": "c1",
                "text": "Nội dung 1",
                "source": "A",
                "page_start": 1,
                "page_end": 1,
                "semantic_rank": 1,
                "semantic_distance": 0.3,
            }
        ]
        with patch.object(advanced_rag, "_query_bm25", return_value=mock_bm25):
            with patch.object(advanced_rag, "_query_semantic", return_value=mock_semantic):
                with patch.object(advanced_rag, "_generate_answer", return_value="Trả lời giả lập."):
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir)
                        fixture_path = temp_path / "chunks_advanced_sample.json"
                        _write_fixture_file(fixture_path)

                        result = advanced_rag.run_query(
                            question="Câu hỏi?",
                            top_k=1,
                            strategy="hierarchical",
                            mode="bm25",
                            input_dir=temp_path,
                        )

        self.assertEqual(result["status"], "answered")
        self.assertEqual(len(result["evidence"]), 1)
        self.assertTrue(result["evidence"][0]["accepted"])


if __name__ == "__main__":
    unittest.main()
