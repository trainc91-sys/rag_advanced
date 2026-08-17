import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest

import rag_advanced.buoi_09.advanced_rag as advanced_rag
import rag_advanced.buoi_09.hierarchical_rag as hierarchical_rag
from rag_advanced.buoi_09.hierarchical_rag import (
    DEFAULT_INPUT_DIR,
    HIERARCHY_DIR,
    QUERY_GENERATION_CACHE,
    build_hierarchy,
    build_parents,
    build_query_set,
    hierarchy_audit,
    hierarchy_status,
    load_raw_chunks,
    load_config,
    multi_child_retrieve,
    parent_retrieve,
    query,
    compare,
    resolve_children,
)


class TestHierarchicalRag(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.input_dir = self.temp_dir / "input"
        self.output_dir = self.temp_dir / "hierarchy"
        self.input_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        for child in self.temp_dir.rglob("*"):
            try:
                if child.is_file():
                    child.unlink()
            except OSError:
                pass
        try:
            self.temp_dir.rmdir()
        except OSError:
            pass

    def _write_fixture(self, name: str, payload: dict) -> None:
        path = self.input_dir / name
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def test_metadata_precedence(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {
                        "chunk_id": "src:1",
                        "strategy": "hierarchical",
                        "source": "DocA",
                        "page_start": 1,
                        "page_end": 1,
                        "text": "Nội dung văn bản.",
                        "structure": {"article": "Điều 1"},
                    }
                ]
            },
        )
        children = resolve_children(load_raw_chunks(self.input_dir))
        self.assertEqual(children[0]["article_label"], "Điều 1")
        self.assertEqual(children[0]["resolution_method"], "metadata")
        self.assertFalse(children[0]["ambiguous"])

    def test_heading_inferred_at_start(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {
                        "chunk_id": "src:1",
                        "strategy": "hierarchical",
                        "source": "DocA",
                        "page_start": 1,
                        "page_end": 1,
                        "text": "Điều 2. Đây là nội dung.",
                    }
                ]
            },
        )
        children = resolve_children(load_raw_chunks(self.input_dir))
        self.assertEqual(children[0]["article_label"], "Điều 2")
        self.assertEqual(children[0]["resolution_method"], "heading_inferred")

    def test_carry_forward_within_same_source(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {
                        "chunk_id": "src:1",
                        "strategy": "hierarchical",
                        "source": "DocA",
                        "page_start": 1,
                        "page_end": 1,
                        "text": "Điều 1. Nội dung 1.",
                    },
                    {
                        "chunk_id": "src:2",
                        "strategy": "hierarchical",
                        "source": "DocA",
                        "page_start": 2,
                        "page_end": 2,
                        "text": "Nội dung 2.",
                    },
                ]
            },
        )
        children = resolve_children(load_raw_chunks(self.input_dir))
        self.assertEqual(children[1]["article_label"], "Điều 1")
        self.assertEqual(children[1]["resolution_method"], "carried_forward")

    def test_no_carry_forward_across_source(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {
                        "chunk_id": "docA:1",
                        "strategy": "hierarchical",
                        "source": "DocA",
                        "page_start": 1,
                        "page_end": 1,
                        "text": "Điều 1. Nội dung 1.",
                    },
                    {
                        "chunk_id": "docB:1",
                        "strategy": "hierarchical",
                        "source": "DocB",
                        "page_start": 1,
                        "page_end": 1,
                        "text": "Nội dung 2.",
                    },
                ]
            },
        )
        children = resolve_children(load_raw_chunks(self.input_dir))
        self.assertEqual(children[0]["article_label"], "Điều 1")
        self.assertEqual(children[1]["resolution_method"], "document_fallback")

    def test_inline_dieu_not_heading(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {
                        "chunk_id": "src:1",
                        "strategy": "hierarchical",
                        "source": "DocA",
                        "page_start": 1,
                        "page_end": 1,
                        "text": "Nội dung trích dẫn Điều 3 trong văn bản.",
                    }
                ]
            },
        )
        children = resolve_children(load_raw_chunks(self.input_dir))
        self.assertEqual(children[0]["resolution_method"], "document_fallback")

    def test_conflict_sets_ambiguous_warning(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {
                        "chunk_id": "src:1",
                        "strategy": "hierarchical",
                        "source": "DocA",
                        "page_start": 1,
                        "page_end": 1,
                        "text": "Điều 2. Nội dung.",
                        "structure": {"article": "Điều 1"},
                    }
                ]
            },
        )
        children = resolve_children(load_raw_chunks(self.input_dir))
        self.assertTrue(children[0]["ambiguous"])
        self.assertIn("metadata_heading_conflict", children[0]["warnings"])

    def test_numeric_chunk_ordering(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:2", "strategy": "hierarchical", "source": "DocA", "page_start": 2, "page_end": 2, "text": "Nội dung 2."},
                    {"chunk_id": "src:10", "strategy": "hierarchical", "source": "DocA", "page_start": 10, "page_end": 10, "text": "Nội dung 10."},
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Nội dung 1."},
                ]
            },
        )
        children = resolve_children(load_raw_chunks(self.input_dir))
        self.assertEqual([child["child_id"] for child in children], ["src:1", "src:2", "src:10"])

    def test_stable_parent_id(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Điều 1. Nội dung 1."},
                    {"chunk_id": "src:2", "strategy": "hierarchical", "source": "DocA", "page_start": 2, "page_end": 2, "text": "Nội dung 2."},
                ]
            },
        )
        children = resolve_children(load_raw_chunks(self.input_dir))
        result1 = build_hierarchy(self.input_dir, self.output_dir)
        result2 = build_hierarchy(self.input_dir, self.output_dir)
        self.assertEqual(result1["manifest"]["config_digest"], result2["manifest"]["config_digest"])
        self.assertEqual(result1["child_count"], result2["child_count"])

    def test_parent_split_at_child_boundary(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Điều 1. Nội dung 1."},
                    {"chunk_id": "src:2", "strategy": "hierarchical", "source": "DocA", "page_start": 2, "page_end": 2, "text": "Nội dung 2."},
                    {"chunk_id": "src:3", "strategy": "hierarchical", "source": "DocA", "page_start": 3, "page_end": 3, "text": "Nội dung 3."},
                ]
            },
        )
        config = load_config()
        config["parent_max_chars"] = 25
        result = build_hierarchy(self.input_dir, self.output_dir, config)
        self.assertGreater(result["parent_count"], 1)
        parents = json.loads((self.output_dir / "parents.json").read_text(encoding="utf-8"))
        child_ids = [child_id for parent in parents for child_id in parent["child_ids"]]
        self.assertEqual(child_ids, ["src:1", "src:2", "src:3"])

    def test_build_hierarchy_preserves_structural_path_on_parent(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {
                        "chunk_id": "src:1",
                        "strategy": "hierarchical",
                        "source": "DocA",
                        "page_start": 1,
                        "page_end": 1,
                        "text": "Điều 2. Nội dung 1.",
                        "structure": {"chapter": "Chương 1", "article": "Điều 2"},
                    }
                ]
            },
        )
        build_hierarchy(self.input_dir, self.output_dir)
        parents = json.loads((self.output_dir / "parents.json").read_text(encoding="utf-8"))
        self.assertEqual(parents[0]["structural_path"], {"chapter": "Chương 1", "article": "Điều 2"})

    def test_oversized_child_warning(self):
        long_text = "Điều 1. " + "nội dung " * 1000
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": long_text},
                ]
            },
        )
        result = build_hierarchy(self.input_dir, self.output_dir)
        self.assertEqual(result["child_count"], 1)
        self.assertEqual(result["parent_count"], 1)
        parents = json.loads((self.output_dir / "parents.json").read_text(encoding="utf-8"))
        self.assertTrue(any("oversized_single_child" in parent.get("warnings", []) for parent in parents))

    def test_each_child_has_one_parent(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Điều 1. Nội dung 1."},
                ]
            },
        )
        result = build_hierarchy(self.input_dir, self.output_dir)
        children = json.loads((self.output_dir / "children.json").read_text(encoding="utf-8"))
        self.assertEqual(len(children), 1)
        self.assertIn("parent_id", children[0])
        self.assertEqual(len({child["child_id"] for child in children}), 1)

    def test_build_query_set_preserves_original_query_first(self):
        QUERY_GENERATION_CACHE.clear()

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": "Có phải Điều 10 áp dụng?", "focus": "exact_legal_terms"},
                    {"text": "Điều 10 nghĩa là gì?", "focus": "paraphrase"},
                ]
            }

        result = build_query_set("Nội dung về Điều 10", query_generator_fn=fake_generator)
        self.assertEqual(result["queries"][0]["query_id"], "Q0")
        self.assertEqual(result["queries"][0]["text"], "Nội dung về Điều 10")
        self.assertEqual(result["queries"][0]["origin"], "original")
        self.assertEqual(result["queries"][1]["query_id"], "Q1")
        self.assertEqual(result["queries"][1]["origin"], "generated")
        self.assertEqual(result["status"], "ready")
        self.assertFalse(result["cache_hit"])

    def test_build_query_set_validates_generated_schema_and_drops_invalid(self):
        QUERY_GENERATION_CACHE.clear()

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": "  ", "focus": "exact_legal_terms"},
                    {"text": "Query 1", "focus": "invalid_focus"},
                    {"text": "Query 2", "focus": "paraphrase"},
                ]
            }

        result = build_query_set("Câu hỏi pháp lý", query_generator_fn=fake_generator)
        self.assertEqual(len(result["queries"]), 2)
        self.assertEqual(result["invalid_query_count"], 2)
        self.assertEqual(result["dropped_duplicate_count"], 0)
        self.assertEqual(result["queries"][1]["text"], "Query 2")

    def test_build_query_set_deduplicates_generated_queries(self):
        QUERY_GENERATION_CACHE.clear()

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": "Điều 10 áp dụng", "focus": "exact_legal_terms"},
                    {"text": "điều 10 áp dụng", "focus": "paraphrase"},
                    {"text": "Điều 10 áp dụng?", "focus": "missing_aspect"},
                ]
            }

        result = build_query_set("Vấn đề Điều 10", query_generator_fn=fake_generator)
        self.assertEqual(len(result["queries"]), 2)
        self.assertEqual(result["dropped_duplicate_count"], 2)
        self.assertEqual(result["invalid_query_count"], 0)

    def test_build_query_set_requires_legal_reference_if_question_contains_reference(self):
        QUERY_GENERATION_CACHE.clear()

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": "Phân tích nội dung chung", "focus": "paraphrase"},
                ]
            }

        result = build_query_set("Liên quan đến Điều 5", query_generator_fn=fake_generator)
        self.assertEqual(result["status"], "query_generation_unavailable")
        self.assertEqual(result["queries"], [{"query_id": "Q0", "text": "Liên quan đến Điều 5", "origin": "original", "focus": "original_intent"}])

    def test_build_query_set_uses_cache_hit_and_single_generator_invocation(self):
        QUERY_GENERATION_CACHE.clear()
        call_count = {"value": 0}

        def fake_generator(question, config):
            call_count["value"] += 1
            return {"queries": [{"text": "Query A", "focus": "exact_legal_terms"}]}

        first = build_query_set("Câu hỏi cache", query_generator_fn=fake_generator)
        second = build_query_set("Câu hỏi cache", query_generator_fn=fake_generator)
        self.assertEqual(call_count["value"], 1)
        self.assertTrue(second["cache_hit"])
        self.assertEqual(first["queries"], second["queries"])

    def test_build_query_set_handles_generator_exception_as_unavailable(self):
        QUERY_GENERATION_CACHE.clear()

        def fake_generator(question, config):
            raise RuntimeError("API not available")

        result = build_query_set("Câu hỏi lỗi", query_generator_fn=fake_generator)
        self.assertEqual(result["status"], "query_generation_unavailable")
        self.assertIn("API not available", result["error"])
        self.assertEqual(result["queries"], [{"query_id": "Q0", "text": "Câu hỏi lỗi", "origin": "original", "focus": "original_intent"}])

    def test_query_single_flat_returns_reranked_children_and_evidence(self):
        QUERY_GENERATION_CACHE.clear()

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": question, "focus": "original_intent", "query_id": "Q0", "origin": "original"},
                ]
            }

        def fake_hybrid(query_id, query_text, config, query):
            return {
                "hits": [
                    {"child_id": "c1", "text": "Nội dung 1", "source": "DocA", "page_start": 1, "page_end": 1, "bm25_rank": 1, "semantic_rank": 1, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 1}},
                    {"child_id": "c2", "text": "Nội dung 2", "source": "DocA", "page_start": 2, "page_end": 2, "bm25_rank": 2, "semantic_rank": 2, "inner_rrf_rank": 2, "per_query_trace": {"bm25": 2, "semantic": 2}},
                ]
            }

        def fake_reranker(question, candidates, corpus):
            return [
                {"child_rerank_raw_score": 1.0},
                {"child_rerank_raw_score": 0.0},
            ]

        result = query(
            "Câu hỏi kiểm tra",
            "single_flat",
            query_generator_fn=fake_generator,
            hybrid_search_fn=fake_hybrid,
            reranker_fn=fake_reranker,
        )

        self.assertEqual(result["status"], "single_flat_ready")
        self.assertEqual(len(result["child_hits"]), 2)
        self.assertEqual(len(result["selected_children"]), 2)
        self.assertEqual(result["accepted_evidence"][0]["evidence_id"], "P1")
        self.assertEqual(result["answer"], "")

    def test_query_single_parent_generates_answer_and_citations(self):
        QUERY_GENERATION_CACHE.clear()
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Điều 1. Nội dung 1."},
                ]
            },
        )
        build_hierarchy(self.input_dir, self.output_dir)

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": question, "focus": "original_intent", "query_id": "Q0", "origin": "original"},
                ]
            }

        def fake_hybrid(query_id, query_text, config, query):
            return {
                "hits": [
                    {"child_id": "src:1", "text": "Điều 1. Nội dung 1.", "source": "DocA", "page_start": 1, "page_end": 1, "bm25_rank": 1, "semantic_rank": 1, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 1}},
                ]
            }

        def fake_reranker(question, candidates, corpus):
            return [{"parent_rerank_raw_score": 1.0}]

        with patch("rag_advanced.buoi_09.hierarchical_rag._generate_answer", return_value="Trả lời dựa trên evidence [P1]."):
            result = query(
                "Xin vay",
                "single_parent",
                query_generator_fn=fake_generator,
                hybrid_search_fn=fake_hybrid,
                reranker_fn=fake_reranker,
                input_dir=self.input_dir,
                output_dir=self.output_dir,
            )

        self.assertEqual(result["status"], "parent_ready")
        self.assertEqual(result["answer"], "Trả lời dựa trên evidence [P1].")
        self.assertEqual(result["citations"][0]["evidence_id"], "P1")
        self.assertEqual(result["citations"][0]["parent_id"], result["accepted_evidence"][0]["parent_id"])

    def test_compare_returns_retrieval_only_for_parent_and_flat_modes(self):
        QUERY_GENERATION_CACHE.clear()

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": question, "focus": "original_intent", "query_id": "Q0", "origin": "original"},
                ]
            }

        def fake_hybrid(query_id, query_text, config, query):
            return {
                "hits": [
                    {"child_id": "c1", "text": "Nội dung 1", "source": "DocA", "page_start": 1, "page_end": 1, "bm25_rank": 1, "semantic_rank": 1, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 1}},
                ]
            }

        def fake_reranker(question, candidates, corpus):
            return [{"child_rerank_raw_score": 1.0}]

        result = compare(
            "So sánh",
            query_generator_fn=fake_generator,
            hybrid_search_fn=fake_hybrid,
            reranker_fn=fake_reranker,
            input_dir=self.input_dir,
            output_dir=self.output_dir,
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("single_flat", result["modes"])
        self.assertIn("single_parent", result["modes"])
        self.assertEqual(result["modes"]["single_flat"]["raw"]["answer"], "")
        self.assertEqual(result["modes"]["single_parent"]["raw"]["answer"], "")
        self.assertEqual(result["modes"]["single_parent"]["raw"]["selected_parents"], [])

    def test_multi_child_retrieve_merges_query_hits_with_mq_rrf(self):
        QUERY_GENERATION_CACHE.clear()

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": question, "focus": "original_intent", "query_id": "Q0", "origin": "original"},
                    {"text": "Liên quan đến khoản vay", "focus": "paraphrase", "query_id": "Q1", "origin": "generated"},
                ]
            }

        def fake_hybrid(query_id, query_text, config, query):
            if query_id == "Q0":
                return {
                    "hits": [
                        {"child_id": "c1", "text": "Nội dung 1", "source": "DocA", "page_start": 1, "page_end": 1, "bm25_rank": 1, "semantic_rank": 2, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 2}},
                        {"child_id": "c2", "text": "Nội dung 2", "source": "DocA", "page_start": 2, "page_end": 2, "bm25_rank": 2, "semantic_rank": 1, "inner_rrf_rank": 2, "per_query_trace": {"bm25": 2, "semantic": 1}},
                    ],
                    "semantic_embedding_call_count": 1,
                }
            return {
                "hits": [
                    {"child_id": "c2", "text": "Nội dung 2", "source": "DocA", "page_start": 2, "page_end": 2, "bm25_rank": 1, "semantic_rank": 2, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 2}},
                    {"child_id": "c3", "text": "Nội dung 3", "source": "DocA", "page_start": 3, "page_end": 3, "bm25_rank": 2, "semantic_rank": 1, "inner_rrf_rank": 2, "per_query_trace": {"bm25": 2, "semantic": 1}},
                ],
                "semantic_embedding_call_count": 1,
            }

        result = multi_child_retrieve(
            "Điều kiện vay vốn?",
            query_generator_fn=fake_generator,
            hybrid_search_fn=fake_hybrid,
        )

        self.assertEqual(result["status"], "multi_query_ready")
        self.assertEqual(result["trace"]["query_count_requested"], 2)
        self.assertEqual(result["trace"]["query_count_failed"], 0)
        self.assertEqual(result["trace"]["union_child_count"], 3)
        self.assertEqual(result["trace"]["semantic_embedding_call_count"], 2)

    def test_default_hybrid_search_prefers_semantic_search(self):
        config = load_config()
        query = {"query_id": "Q0", "text": "Test question", "origin": "original", "focus": "original_intent"}
        semantic_candidates = [
            {
                "chunk_id": "src:1",
                "text": "Nội dung tham khảo.",
                "source": "DocA",
                "page_start": 1,
                "page_end": 1,
            }
        ]

        with patch("rag_advanced.buoi_09.advanced_rag._query_semantic", return_value=semantic_candidates) as fake_semantic:
            result = hierarchical_rag._default_hybrid_search(query["query_id"], query["text"], config, query)

        self.assertEqual(result["semantic_embedding_call_count"], 1)
        self.assertEqual(len(result["hits"]), 1)
        self.assertEqual(result["hits"][0]["child_id"], "src:1")
        self.assertEqual(result["hits"][0]["semantic_rank"], 1)
        fake_semantic.assert_called_once_with(
            query["text"],
            advanced_rag._collection_name_for_strategy(hierarchical_rag.DEFAULT_STRATEGY),
            hierarchical_rag.DEFAULT_STRATEGY,
            int(config.get("per_query_candidates", 12)),
        )

    def test_default_hybrid_search_falls_back_to_bm25_when_semantic_returns_no_hits(self):
        config = load_config()
        query = {"query_id": "Q0", "text": "Test fallback", "origin": "original", "focus": "original_intent"}
        records = [
            {
                "chunk_id": "src:1",
                "source": "DocA",
                "page_start": 1,
                "page_end": 1,
                "text": "Nội dung fallback test.",
            }
        ]

        class FakeBM25:
            def __init__(self, corpus):
                self._corpus = corpus

            def get_scores(self, query_tokens):
                return [1.0]

        with patch("rag_advanced.buoi_09.advanced_rag._query_semantic", return_value=[]), patch(
            "rag_advanced.buoi_09.hierarchical_rag.load_raw_chunks", return_value=records
        ), patch("rag_advanced.buoi_09.hierarchical_rag.BM25Okapi", FakeBM25):
            result = hierarchical_rag._default_hybrid_search(query["query_id"], query["text"], config, query)

        self.assertEqual(result["semantic_embedding_call_count"], 1)
        self.assertEqual(len(result["hits"]), 1)
        self.assertEqual(result["hits"][0]["child_id"], "src:1")
        self.assertEqual(result["hits"][0]["bm25_rank"], 1)
        self.assertEqual(result["hits"][0]["semantic_rank"], 1)

    def test_multi_child_retrieve_partial_when_generated_query_fails(self):
        QUERY_GENERATION_CACHE.clear()

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": question, "focus": "original_intent", "query_id": "Q0", "origin": "original"},
                    {"text": "Sai query", "focus": "paraphrase", "query_id": "Q1", "origin": "generated"},
                ]
            }

        def fake_hybrid(query_id, query_text, config, query):
            if query_id == "Q0":
                return {"hits": [{"child_id": "c1", "text": "Nội dung 1", "source": "DocA", "page_start": 1, "page_end": 1, "bm25_rank": 1, "semantic_rank": 1, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 1}}]}
            raise RuntimeError("Hybrid failure")

        result = multi_child_retrieve(
            "Vay vốn",
            query_generator_fn=fake_generator,
            hybrid_search_fn=fake_hybrid,
        )

        self.assertEqual(result["status"], "multi_query_partial")
        self.assertEqual(result["trace"]["query_count_failed"], 1)
        self.assertEqual(result["trace"]["union_child_count"], 1)
        self.assertEqual(result["merged_child_hits"][0]["child_id"], "c1")
        self.assertEqual(result["merged_child_hits"][0]["support_query_ids"], ["Q0"])

    def test_multi_child_retrieve_fails_when_q0_fails(self):
        QUERY_GENERATION_CACHE.clear()

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": question, "focus": "original_intent", "query_id": "Q0", "origin": "original"},
                    {"text": "Liên quan", "focus": "missing_aspect", "query_id": "Q1", "origin": "generated"},
                ]
            }

        def fake_hybrid(query_id, query_text, config, query):
            if query_id == "Q0":
                raise RuntimeError("Q0 unavailable")
            return {"hits": []}

        result = multi_child_retrieve(
            "Xin vay",
            query_generator_fn=fake_generator,
            hybrid_search_fn=fake_hybrid,
        )

        self.assertEqual(result["status"], "multi_query_failed")
        self.assertEqual(result["trace"]["query_count_failed"], 1)
        self.assertEqual(result["merged_child_hits"], [])

    def test_parent_retrieve_returns_hierarchy_not_ready_when_store_missing(self):
        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": question, "focus": "original_intent", "query_id": "Q0", "origin": "original"},
                ]
            }

        def fake_hybrid(query_id, query_text, config, query):
            return {"hits": []}

        result = parent_retrieve(
            "Xin vay",
            mode="multi_parent",
            query_generator_fn=fake_generator,
            hybrid_search_fn=fake_hybrid,
            input_dir=self.input_dir,
            output_dir=self.output_dir,
        )

        self.assertEqual(result["status"], "hierarchy_not_ready")
        self.assertTrue("not_ready" in result["error"] or "missing" in result["error"])
        self.assertEqual(result["parent_candidates"], [])
        self.assertEqual(result["selected_parents"], [])

    def test_parent_retrieve_maps_children_to_parent_and_aggregates_score(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Điều 1. Nội dung 1."},
                    {"chunk_id": "src:2", "strategy": "hierarchical", "source": "DocA", "page_start": 2, "page_end": 2, "text": "Nội dung 2."},
                ]
            },
        )
        build_hierarchy(self.input_dir, self.output_dir)

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": question, "focus": "original_intent", "query_id": "Q0", "origin": "original"},
                    {"text": "Vay vốn", "focus": "paraphrase", "query_id": "Q1", "origin": "generated"},
                ]
            }

        def fake_hybrid(query_id, query_text, config, query):
            if query_id == "Q0":
                return {
                    "hits": [
                        {"child_id": "src:1", "text": "Điều 1. Nội dung 1.", "source": "DocA", "page_start": 1, "page_end": 1, "bm25_rank": 1, "semantic_rank": 1, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 1}},
                    ]
                }
            return {
                "hits": [
                    {"child_id": "src:2", "text": "Nội dung 2.", "source": "DocA", "page_start": 2, "page_end": 2, "bm25_rank": 1, "semantic_rank": 1, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 1}},
                ]
            }

        def fake_reranker(question, candidates, corpus):
            return [{"parent_rerank_raw_score": 1.0}]

        result = parent_retrieve(
            "Xin vay",
            mode="multi_parent",
            query_generator_fn=fake_generator,
            hybrid_search_fn=fake_hybrid,
            reranker_fn=fake_reranker,
            input_dir=self.input_dir,
            output_dir=self.output_dir,
        )

        self.assertEqual(result["status"], "parent_ready")
        self.assertEqual(len(result["selected_parents"]), 1)
        parent = result["selected_parents"][0]
        self.assertEqual(parent["supporting_child_ids"], ["src:1", "src:2"])
        self.assertEqual(parent["scoring_child_ids"], ["src:1", "src:2"])
        self.assertEqual(parent["support_query_ids"], ["Q0", "Q1"])
        self.assertEqual(parent["best_child_rank"], 1)
        self.assertEqual(parent["anchor_child_id"], "src:1")
        self.assertGreater(parent["parent_rrf_score"], 0)
        self.assertEqual(len(result["trace"]["child_to_parent"]), 2)
        self.assertEqual(result["trace"]["unique_parent_count"], 1)

    def test_parent_retrieve_reranks_parents_using_q0_and_applies_threshold(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Điều 1. Nội dung 1."},
                    {"chunk_id": "src:2", "strategy": "hierarchical", "source": "DocA", "page_start": 2, "page_end": 2, "text": "Điều 2. Nội dung 2."},
                ]
            },
        )
        build_hierarchy(self.input_dir, self.output_dir)

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": question, "focus": "original_intent", "query_id": "Q0", "origin": "original"},
                    {"text": "Điều 2", "focus": "paraphrase", "query_id": "Q1", "origin": "generated"},
                ]
            }

        def fake_hybrid(query_id, query_text, config, query):
            if query_id == "Q0":
                return {
                    "hits": [
                        {"child_id": "src:1", "text": "Điều 1. Nội dung 1.", "source": "DocA", "page_start": 1, "page_end": 1, "bm25_rank": 1, "semantic_rank": 1, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 1}},
                    ]
                }
            return {
                "hits": [
                    {"child_id": "src:2", "text": "Điều 2. Nội dung 2.", "source": "DocA", "page_start": 2, "page_end": 2, "bm25_rank": 1, "semantic_rank": 1, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 1}},
                ]
            }

        def fake_reranker(question, candidates, corpus):
            return [
                {"parent_rerank_raw_score": 0.0},
                {"parent_rerank_raw_score": 1.0},
            ]

        config = load_config()
        config["final_parent_top_k"] = 1
        result = parent_retrieve(
            "Xin vay",
            mode="multi_parent",
            config=config,
            query_generator_fn=fake_generator,
            hybrid_search_fn=fake_hybrid,
            reranker_fn=fake_reranker,
            input_dir=self.input_dir,
            output_dir=self.output_dir,
        )

        self.assertEqual(result["status"], "parent_ready")
        self.assertEqual(result["parent_candidates"][0]["parent_rerank_score"], 0.7310585786300049)
        self.assertEqual(result["parent_candidates"][1]["parent_rerank_score"], 0.5)
        self.assertEqual(result["parent_candidates"][0]["parent_rank_change"], result["parent_candidates"][0]["parent_rank"] - 1)
        self.assertEqual(len(result["accepted_evidence"]), 1)
        self.assertEqual(result["accepted_evidence"][0]["evidence_id"], "P1")

    def test_parent_reranker_uses_original_question(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Điều 1. Nội dung 1."},
                ]
            },
        )
        build_hierarchy(self.input_dir, self.output_dir)

        observed_questions: list[str] = []

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": question, "focus": "original_intent", "query_id": "Q0", "origin": "original"},
                    {"text": "Về Điều 1", "focus": "paraphrase", "query_id": "Q1", "origin": "generated"},
                ]
            }

        def fake_hybrid(query_id, query_text, config, query):
            return {
                "hits": [
                    {"child_id": "src:1", "text": "Điều 1. Nội dung 1.", "source": "DocA", "page_start": 1, "page_end": 1, "bm25_rank": 1, "semantic_rank": 1, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 1}},
                ]
            }

        def fake_reranker(question, candidates, corpus):
            observed_questions.append(question)
            return [{"parent_rerank_raw_score": 1.0}]

        result = parent_retrieve(
            "Xin vay",
            mode="multi_parent",
            query_generator_fn=fake_generator,
            hybrid_search_fn=fake_hybrid,
            reranker_fn=fake_reranker,
            input_dir=self.input_dir,
            output_dir=self.output_dir,
        )

        self.assertEqual(result["status"], "parent_ready")
        self.assertEqual(observed_questions, ["Xin vay"])

    def test_parent_answer_context_preserves_anchor_child_citation(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Điều 1. Nội dung 1."},
                ]
            },
        )
        build_hierarchy(self.input_dir, self.output_dir)

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": question, "focus": "original_intent", "query_id": "Q0", "origin": "original"},
                ]
            }

        def fake_hybrid(query_id, query_text, config, query):
            return {
                "hits": [
                    {"child_id": "src:1", "text": "Điều 1. Nội dung 1.", "source": "DocA", "page_start": 1, "page_end": 1, "bm25_rank": 1, "semantic_rank": 1, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 1}},
                ]
            }

        def fake_reranker(question, candidates, corpus):
            return [{"parent_rerank_raw_score": 1.0}]

        with patch("rag_advanced.buoi_09.hierarchical_rag._generate_answer", return_value="Trả lời dựa trên evidence [P1]."):
            result = parent_retrieve(
                "Xin vay",
                mode="single_parent",
                query_generator_fn=fake_generator,
                hybrid_search_fn=fake_hybrid,
                reranker_fn=fake_reranker,
                input_dir=self.input_dir,
                output_dir=self.output_dir,
            )

        self.assertEqual(result["status"], "parent_ready")
        self.assertEqual(result["accepted_evidence"][0]["anchor_child_id"], "src:1")
        self.assertEqual(result["citations"][0]["anchor_child_id"], "src:1")
        self.assertEqual(result["citations"][0]["parent_id"], result["accepted_evidence"][0]["parent_id"])

    def test_multi_mode_query_generation_is_cached_across_flat_and_parent(self):
        QUERY_GENERATION_CACHE.clear()
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Điều 1. Nội dung 1."},
                ]
            },
        )
        build_hierarchy(self.input_dir, self.output_dir)

        call_count = {"count": 0}

        def fake_generator(question, config):
            call_count["count"] += 1
            return {
                "queries": [
                    {"text": question, "focus": "original_intent", "query_id": "Q0", "origin": "original"},
                    {"text": "Về Điều 1", "focus": "paraphrase", "query_id": "Q1", "origin": "generated"},
                ]
            }

        def fake_hybrid(query_id, query_text, config, query):
            return {
                "hits": [
                    {"child_id": "src:1", "text": "Điều 1. Nội dung 1.", "source": "DocA", "page_start": 1, "page_end": 1, "bm25_rank": 1, "semantic_rank": 1, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 1}},
                ]
            }

        def fake_reranker(question, candidates, corpus):
            return [{"parent_rerank_raw_score": 1.0}]

        result = compare(
            "Xin vay",
            query_generator_fn=fake_generator,
            hybrid_search_fn=fake_hybrid,
            reranker_fn=fake_reranker,
            input_dir=self.input_dir,
            output_dir=self.output_dir,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(call_count["count"], 1)
        self.assertEqual(result["modes"]["multi_parent"]["raw"]["query_set"]["generation_call_count"], 1)
        self.assertTrue(result["modes"]["multi_parent"]["raw"]["query_set"]["cache_hit"])

    def test_parent_retrieve_returns_insufficient_evidence_when_no_parent_meets_threshold(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Điều 1. Nội dung 1."},
                ]
            },
        )
        build_hierarchy(self.input_dir, self.output_dir)

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": question, "focus": "original_intent", "query_id": "Q0", "origin": "original"},
                ]
            }

        def fake_hybrid(query_id, query_text, config, query):
            return {
                "hits": [
                    {"child_id": "src:1", "text": "Điều 1. Nội dung 1.", "source": "DocA", "page_start": 1, "page_end": 1, "bm25_rank": 1, "semantic_rank": 1, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 1}},
                ]
            }

        def fake_reranker(question, candidates, corpus):
            return [{"parent_rerank_raw_score": -10.0}]

        result = parent_retrieve(
            "Xin vay",
            mode="single_parent",
            query_generator_fn=fake_generator,
            hybrid_search_fn=fake_hybrid,
            reranker_fn=fake_reranker,
            input_dir=self.input_dir,
            output_dir=self.output_dir,
        )

        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertEqual(result["accepted_evidence"], [])
        self.assertEqual(result["answer"], "")

    def test_parent_retrieve_generates_answer_and_citations_with_fake_generator(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Điều 1. Nội dung 1."},
                ]
            },
        )
        build_hierarchy(self.input_dir, self.output_dir)

        def fake_generator(question, config):
            return {
                "queries": [
                    {"text": question, "focus": "original_intent", "query_id": "Q0", "origin": "original"},
                ]
            }

        def fake_hybrid(query_id, query_text, config, query):
            return {
                "hits": [
                    {"child_id": "src:1", "text": "Điều 1. Nội dung 1.", "source": "DocA", "page_start": 1, "page_end": 1, "bm25_rank": 1, "semantic_rank": 1, "inner_rrf_rank": 1, "per_query_trace": {"bm25": 1, "semantic": 1}},
                ]
            }

        def fake_reranker(question, candidates, corpus):
            return [{"parent_rerank_raw_score": 1.0}]

        with patch("rag_advanced.buoi_09.hierarchical_rag._generate_answer", return_value="Trả lời dựa trên evidence [P1]."):
            result = parent_retrieve(
                "Xin vay",
                mode="single_parent",
                query_generator_fn=fake_generator,
                hybrid_search_fn=fake_hybrid,
                reranker_fn=fake_reranker,
                input_dir=self.input_dir,
                output_dir=self.output_dir,
            )

        self.assertEqual(result["status"], "parent_ready")
        self.assertEqual(result["answer"], "Trả lời dựa trên evidence [P1].")
        self.assertEqual(result["citations"][0]["evidence_id"], "P1")
        self.assertEqual(result["citations"][0]["parent_id"], result["accepted_evidence"][0]["parent_id"])

    def test_parent_text_uses_raw_child_content(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Nội dung 1."},
                    {"chunk_id": "src:2", "strategy": "hierarchical", "source": "DocA", "page_start": 2, "page_end": 2, "text": "Nội dung 2."},
                ]
            },
        )
        build_hierarchy(self.input_dir, self.output_dir)
        parents = json.loads((self.output_dir / "parents.json").read_text(encoding="utf-8"))
        self.assertEqual(parents[0]["text"], "Nội dung 1.\n\nNội dung 2.")

    def test_hierarchy_audit_reports_warnings_for_uncertain_resolution(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {
                        "chunk_id": "src:1",
                        "strategy": "hierarchical",
                        "source": "DocA",
                        "page_start": 1,
                        "page_end": 1,
                        "text": "Điều 2. Nội dung.",
                        "structure": {"article": "Điều 1"},
                    }
                ]
            },
        )
        audit = hierarchy_audit(self.input_dir)
        self.assertEqual(audit["warning_count"], 1)
        self.assertIn("metadata_heading_conflict", audit["warnings"])

    def test_atomic_manifest_write(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Điều 1. Nội dung 1."},
                ]
            },
        )
        build_hierarchy(self.input_dir, self.output_dir)
        self.assertTrue((self.output_dir / "manifest.json").exists())

    def test_status_does_not_modify_files(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {"chunk_id": "src:1", "strategy": "hierarchical", "source": "DocA", "page_start": 1, "page_end": 1, "text": "Điều 1. Nội dung 1."},
                ]
            },
        )
        status = hierarchy_status(self.input_dir, self.output_dir)
        self.assertEqual(status["status"], "missing")
        self.assertFalse((self.output_dir / "children.json").exists())

    def test_heuristic_rerank_prioritizes_legal_prohibition_context(self):
        question = "Điều kiện cho vay và trường hợp không được cho vay cho khách hàng"
        candidate = {"text": "Điều kiện cho vay: khách hàng không được cho vay khi chưa đủ hồ sơ."}
        generic = {"text": "Văn bản tổng hợp về hoạt động ngân hàng."}

        candidate_score = hierarchical_rag._heuristic_rerank_score(question, candidate, load_config())
        generic_score = hierarchical_rag._heuristic_rerank_score(question, generic, load_config())

        self.assertGreater(candidate_score, generic_score)
        self.assertGreater(candidate_score, 0.8)

    def test_parent_retrieve_falls_back_when_reranker_cannot_load(self):
        self._write_fixture(
            "a.json",
            {
                "chunks": [
                    {
                        "chunk_id": "src:1",
                        "strategy": "hierarchical",
                        "source": "DocA",
                        "page_start": 1,
                        "page_end": 1,
                        "text": "Điều kiện cho vay: khách hàng không được cho vay khi chưa đủ hồ sơ.",
                    }
                ]
            },
        )
        build_hierarchy(self.input_dir, self.output_dir)

        def fake_generator(question, config):
            return {"original_question": question, "queries": [{"query_id": "Q0", "text": question, "origin": "original", "focus": "original_intent"}], "status": "ready", "generation_call_count": 0}

        def fake_hybrid(question, query_text, config, query_meta):
            return {
                "hits": [
                    {
                        "chunk_id": "src:1",
                        "child_id": "src:1",
                        "text": "Điều kiện cho vay: khách hàng không được cho vay khi chưa đủ hồ sơ.",
                        "source": "DocA",
                        "page_start": 1,
                        "page_end": 1,
                        "bm25_rank": 1,
                        "semantic_rank": 1,
                        "inner_rrf_rank": 1,
                        "per_query_trace": {"Q0": {"rank": 1}},
                        "multi_query_rank": 1,
                        "support_query_ids": ["Q0"],
                        "per_query_ranks": {"Q0": 1},
                    }
                ],
                "query_id": "Q0",
                "latency_ms": 10.0,
                "semantic_embedding_call_count": 1,
            }

        with patch("rag_advanced.buoi_09.hierarchical_rag._load_reranker", side_effect=RuntimeError("simulated reranker failure")):
            with patch("rag_advanced.buoi_09.hierarchical_rag._generate_answer", return_value="Trả lời dựa trên điều kiện cho vay."):
                result = parent_retrieve(
                    "Điều kiện cho vay và trường hợp không được cho vay",
                    mode="single_parent",
                    query_generator_fn=fake_generator,
                    hybrid_search_fn=fake_hybrid,
                    input_dir=self.input_dir,
                    output_dir=self.output_dir,
                )

        self.assertEqual(result["status"], "parent_ready")
        self.assertTrue(result["accepted_evidence"])
        self.assertIn("cho vay", result["answer"].lower())


if __name__ == "__main__":
    unittest.main()
