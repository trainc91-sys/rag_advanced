"""Streamlit dashboard cho Buổi 09 Advanced RAG.

Giao diện Buổi 09 tập trung vào multi-query, parent–child retrieval,
và so sánh bốn mode. App chỉ thực hiện truy vấn khi người dùng nhấn nút.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import streamlit as st

from rag_advanced.buoi_09.hierarchical_rag import (
    DEFAULT_INPUT_DIR,
    HIERARCHY_DIR,
    build_hierarchy,
    compare,
    hierarchy_status,
    load_config,
    query,
)
from rag_advanced.buoi_09.advanced_rag import prepare_semantic

REPORT_DIR = Path(__file__).resolve().parent / "reports"
MODES = ["single_flat", "multi_flat", "single_parent", "multi_parent"]

STATUS_MESSAGE = {
    "hierarchy_not_ready": "Kho hierarchy chưa sẵn sàng. Hãy chạy Xây dựng hierarchy hoặc kiểm tra storage.",
    "missing": "Kho hierarchy chưa tồn tại.",
    "hierarchy_store_incomplete": "Kho hierarchy thiếu một số tệp. Cần xây dựng lại.",
    "strategy_mismatch": "Kho hierarchy không dùng chiến lược hierarchical.",
    "config_mismatch": "Kho hierarchy đã cũ do cấu hình khác. Cần xây dựng lại.",
    "input_file_mismatch": "Dữ liệu đầu vào đã thay đổi so với manifest của hierarchy.",
    "input_file_changed": "Một hoặc nhiều tệp đầu vào đã thay đổi. Cần xây dựng lại.",
    "query_generation_unavailable": "Mở rộng truy vấn không khả dụng cho câu hỏi hiện tại.",
    "multi_query_partial": "Một số truy vấn đa câu hỏi chưa trả về đủ kết quả.",
    "reranker_unavailable": "Reranker chưa sẵn sàng. Chưa thể dùng rerank trực tiếp.",
    "insufficient_evidence": "Không đủ bằng chứng để trả lời.",
}


def _load_store_status(input_dir: Path, output_dir: Path) -> dict[str, Any]:
    return hierarchy_status(input_dir, output_dir)


@st.cache_data(show_spinner=False)
def get_hierarchy_status(input_dir: Path, output_dir: Path) -> dict[str, Any]:
    return _load_store_status(input_dir, output_dir)


@st.cache_data(show_spinner=False)
def load_hierarchy_counts(output_dir: Path) -> dict[str, int]:
    result = {"child_count": 0, "parent_count": 0, "ambiguous_count": 0}
    children_path = Path(output_dir) / "children.json"
    parents_path = Path(output_dir) / "parents.json"
    if children_path.exists():
        children = json.loads(children_path.read_text(encoding="utf-8"))
        result["child_count"] = len(children)
        result["ambiguous_count"] = sum(1 for child in children if child.get("ambiguous"))
    if parents_path.exists():
        parents = json.loads(parents_path.read_text(encoding="utf-8"))
        result["parent_count"] = len(parents)
    return result


@st.cache_data(show_spinner=False)
def load_latest_report() -> tuple[dict[str, Any] | None, str | None]:
    reports = sorted(REPORT_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not reports:
        return None, None
    latest = reports[0]
    try:
        return json.loads(latest.read_text(encoding="utf-8")), latest.name
    except Exception:
        return None, latest.name


def format_status_message(status: str) -> str:
    return STATUS_MESSAGE.get(status, "Trạng thái không xác định. Xin kiểm tra lại.")


def format_hierarchy_store_status(status: dict[str, Any]) -> tuple[str, str]:
    if status.get("ready"):
        return "Sẵn sàng", "—"
    reason = status.get("reason")
    if reason:
        return "Không sẵn sàng", format_status_message(reason)
    return "Không sẵn sàng", "Kho hierarchy chưa sẵn sàng. Hãy xây dựng lại nếu cần."


def get_runtime_config(
    multi_query_count: int,
    per_query_candidates: int,
    parent_candidates: int,
    final_parent_top_k: int,
    rerank_min_score: float,
    embedding_model: str,
    generation_model: str,
    reranker_model: str,
) -> dict[str, Any]:
    config = load_config()
    config["multi_query_count"] = multi_query_count
    config["per_query_candidates"] = per_query_candidates
    config["parent_candidates"] = parent_candidates
    config["final_parent_top_k"] = final_parent_top_k
    config["rerank_min_score"] = rerank_min_score
    config["gemini_embedding_model"] = embedding_model
    config["gemini_generation_model"] = generation_model
    config["reranker_model"] = reranker_model
    return config


def build_query_cards(query_result: dict[str, Any]) -> list[dict[str, Any]]:
    queries = query_result.get("query_set", {}).get("queries", [])
    trace_queries = {item["query_id"]: item for item in query_result.get("trace", {}).get("queries", [])}
    cards = []
    for query in queries:
        trace = trace_queries.get(query["query_id"], {})
        cards.append(
            {
                "query_id": query["query_id"],
                "text": query["text"],
                "origin": query["origin"],
                "focus": query.get("focus", ""),
                "result_count": trace.get("result_count", 0),
                "retrieval_latency_ms": trace.get("retrieval_latency_ms", 0.0),
                "error": trace.get("error"),
            }
        )
    return cards


def build_query_matrix(query_result: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    queries = [query.get("query_id") for query in query_result.get("query_set", {}).get("queries", [])]
    rows: list[dict[str, Any]] = []
    for child in query_result.get("child_hits", []):
        row = {
            "child_id": child.get("child_id"),
            "source": child.get("source"),
            "pages": f"{child.get('page_start', '')}-{child.get('page_end', '')}",
            "support_query_count": child.get("support_query_count", 0),
            "mq_rrf_score": round(child.get("multi_query_rrf_score", 0.0), 4),
        }
        per_query_ranks = child.get("per_query_ranks", {})
        for query_id in queries:
            row[query_id] = per_query_ranks.get(query_id, "—")
        rows.append(row)
    return queries, rows


def build_parent_tree_data(parent_result: dict[str, Any]) -> list[dict[str, Any]]:
    parents = parent_result.get("selected_parents") or parent_result.get("parent_candidates", [])
    tree: list[dict[str, Any]] = []
    for parent in parents:
        structural_path = parent.get("structural_path", {})
        path_values = [str(value) for value in structural_path.values() if value]
        if not path_values:
            article_key = parent.get("article_key")
            if article_key and article_key != "__document_fallback__":
                path_values = [str(article_key)]
        parent_rank = parent.get("parent_rerank_rank")
        if parent_rank is None:
            parent_rank = parent.get("parent_rank")
        parent_score = parent.get("parent_rerank_score")
        if parent_score is None:
            parent_score = parent.get("parent_rrf_score")
        tree.append(
            {
                "parent_id": parent.get("parent_id"),
                "path": " / ".join(path_values) if path_values else "N/A",
                "source": parent.get("source"),
                "pages": f"{parent.get('page_start', '')}-{parent.get('page_end', '')}",
                "parent_rank": parent.get("parent_rank"),
                "parent_rerank_rank": parent_rank,
                "parent_rrf_score": parent.get("parent_rrf_score"),
                "parent_rerank_score": parent_score,
                "warnings": parent.get("warnings", []),
                "ambiguous": parent.get("ambiguous", False),
                "supporting_children": [
                    {
                        "child_id": child_id,
                        "is_anchor": child_id == parent.get("anchor_child_id"),
                        "query_ids": (
                            parent.get("supporting_child_query_ids", {}).get(child_id, [])
                            if isinstance(parent.get("supporting_child_query_ids"), dict)
                            else parent.get("support_query_ids", [])
                        ),
                        "snippet": parent.get("text", "")[:120].strip(),
                    }
                    for child_id in parent.get("supporting_child_ids", [])
                ],
                "parent_text": parent.get("text", ""),
            }
        )
    return tree


def build_mode_comparison_rows(compare_result: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    modes = compare_result.get("modes", [])
    if isinstance(modes, dict):
        items = []
        for mode_name, mode_payload in modes.items():
            if isinstance(mode_payload, dict):
                payload = dict(mode_payload)
                payload.setdefault("mode", mode_name)
                items.append(payload)
            else:
                items.append({"mode": mode_name, "raw": {}})
    elif isinstance(modes, list):
        items = modes
    else:
        items = []

    for mode_item in items:
        if not isinstance(mode_item, dict):
            continue
        raw = mode_item.get("raw", {})
        if not isinstance(raw, dict):
            raw = {}
        accepted_evidence = raw.get("accepted_evidence", []) or []
        if not isinstance(accepted_evidence, list):
            accepted_evidence = []
        evidence_ids = [item.get("evidence_id") for item in accepted_evidence if isinstance(item, dict) and item.get("evidence_id")]
        sources = sorted({item.get("source") for item in accepted_evidence if isinstance(item, dict) and item.get("source")})
        parent_ids = sorted({item.get("parent_id") for item in accepted_evidence if isinstance(item, dict) and item.get("parent_id")})
        trace = raw.get("trace", {}) or {}
        if not isinstance(trace, dict):
            trace = {}
        query_set = raw.get("query_set", {}) or {}
        if not isinstance(query_set, dict):
            query_set = {}
        mode_name = mode_item.get("mode")
        is_parent_mode = mode_name in {"single_parent", "multi_parent"}
        rows.append(
            {
                "mode": mode_name,
                "status": raw.get("status"),
                "unit_type": "parent" if is_parent_mode else "child",
                "evidence_ids": ", ".join(evidence_ids) or "—",
                "source_pages": ", ".join(sources) or "—",
                "unique_sources": len(sources),
                "retrieved_child_count": len(raw.get("child_hits", [])) if isinstance(raw.get("child_hits"), list) else 0,
                "expanded_parent_count": len(raw.get("parent_candidates", [])) if is_parent_mode and isinstance(raw.get("parent_candidates"), list) else 0,
                "context_chars": trace.get("parent_chars") if is_parent_mode else trace.get("child_chars"),
                "expansion_factor": trace.get("context_expansion_factor"),
                "latency_ms": sum(item.get("retrieval_latency_ms", 0.0) for item in trace.get("queries", []) if isinstance(item, dict)),
                "generation_call_count": query_set.get("generation_call_count", 0),
                "embedding_call_count": trace.get("semantic_embedding_call_count", 0),
                "warnings": trace.get("warnings", []),
                "parent_count": len(parent_ids),
            }
        )
    return rows


def format_citation(citation: dict[str, Any]) -> str:
    label = citation.get("evidence_id") or "?"
    parent_id = citation.get("parent_id") or "—"
    anchor_child_id = citation.get("anchor_child_id") or "—"
    return f"{label}: parent={parent_id}, anchor_child={anchor_child_id}"


def render_sidebar(runtime_config: dict[str, Any]) -> dict[str, Any]:
    st.sidebar.header("Bộ điều khiển Buổi 09")
    strategy = st.sidebar.selectbox("Chiến lược", ["hierarchical"], index=0, disabled=True)
    mode = st.sidebar.selectbox("Chế độ", MODES, index=MODES.index(runtime_config["mode"]))
    multi_query_count = st.sidebar.slider("Số truy vấn đa câu hỏi", 1, 5, runtime_config["multi_query_count"])
    per_query_candidates = st.sidebar.slider("Số ứng viên mỗi truy vấn", 1, 50, runtime_config["per_query_candidates"])
    parent_candidates = st.sidebar.slider("Số ứng viên parent", 1, 50, runtime_config["parent_candidates"])
    final_parent_top_k = st.sidebar.slider(
        "Số parent top-k cuối cùng",
        1,
        parent_candidates,
        min(runtime_config["final_parent_top_k"], parent_candidates),
    )
    rerank_min_score = st.sidebar.slider("Điểm rerank tối thiểu", 0.0, 1.0, runtime_config["rerank_min_score"], step=0.01)
    st.sidebar.markdown("---")
    st.sidebar.subheader("Gemini & mô hình")
    has_key = bool(os.getenv("GEMINI_API_KEY", ""))
    st.sidebar.write("Khóa API Gemini:", "Có" if has_key else "Không")
    embedding_model = st.sidebar.text_input("Mô hình embedding", runtime_config["gemini_embedding_model"])
    generation_model = st.sidebar.text_input("Mô hình sinh câu trả lời", runtime_config["gemini_generation_model"])
    reranker_model = st.sidebar.text_input("Mô hình reranker", runtime_config["reranker_model"])
    st.sidebar.markdown("---")
    status = get_hierarchy_status(DEFAULT_INPUT_DIR, HIERARCHY_DIR)
    counts = load_hierarchy_counts(HIERARCHY_DIR)
    label, reason_text = format_hierarchy_store_status(status)
    st.sidebar.subheader("Kho hierarchy")
    st.sidebar.write("Trạng thái:", label)
    st.sidebar.write("Lý do:", reason_text)
    st.sidebar.write("Số child:", counts["child_count"])
    st.sidebar.write("Số parent:", counts["parent_count"])
    st.sidebar.write("Số child mơ hồ:", counts["ambiguous_count"])
    st.sidebar.markdown("---")
    st.sidebar.subheader("Thao tác")
    if st.sidebar.checkbox("Xác nhận chạy thao tác", key="confirm_actions"):
        if st.sidebar.button("Xây dựng hierarchy"):
            try:
                build_hierarchy(DEFAULT_INPUT_DIR, HIERARCHY_DIR)
                st.sidebar.success("Xây dựng hierarchy đã hoàn tất.")
            except Exception:
                st.sidebar.error("Không thể xây dựng hierarchy. Kiểm tra dữ liệu và thử lại.")
        if st.sidebar.button("Chuẩn bị semantic"):
            try:
                prepare_semantic("hierarchical", input_dir=DEFAULT_INPUT_DIR)
                st.sidebar.success("Chuẩn bị semantic đã hoàn tất.")
            except Exception:
                st.sidebar.error("Không thể chuẩn bị semantic. Kiểm tra môi trường và thử lại.")
    return {
        "mode": mode,
        "multi_query_count": multi_query_count,
        "per_query_candidates": per_query_candidates,
        "parent_candidates": parent_candidates,
        "final_parent_top_k": final_parent_top_k,
        "rerank_min_score": rerank_min_score,
        "gemini_embedding_model": embedding_model,
        "gemini_generation_model": generation_model,
        "reranker_model": reranker_model,
    }


def render_query_cards(cards: list[dict[str, Any]]) -> None:
    if not cards:
        st.info("Chưa có truy vấn nào để hiển thị.")
        return
    for card in cards:
        subtitle = "Gốc" if card["origin"] == "original" else "Tạo tự động"
        with st.container():
            st.markdown(f"**{card['query_id']}** — {subtitle}")
            st.markdown(f"_{card['focus']}_")
            st.write(card["text"])
            st.write(f"Số kết quả: {card['result_count']}")
            st.write(f"Độ trễ: {card['retrieval_latency_ms']} ms")
            if card["error"]:
                st.error(card["error"])


def render_parent_tree(parent_data: list[dict[str, Any]]) -> None:
    if not parent_data:
        st.info("Chưa có parent nào để hiển thị.")
        return
    for parent in parent_data:
        label = f"Parent {parent['parent_id']}"
        if parent["ambiguous"]:
            label += " ⚠️"
        with st.expander(label, expanded=False):
            info_cols = st.columns([2, 1, 1])
            info_cols[0].markdown(f"**Đường dẫn:** {parent['path'] or 'N/A'}")
            info_cols[1].metric("Xếp hạng", f"{parent['parent_rank']} → {parent['parent_rerank_rank']}")
            info_cols[2].metric("Điểm số", f"{parent['parent_rrf_score']} → {parent['parent_rerank_score']}")
            st.caption(f"📄 Nguồn / trang: {parent['source']} / {parent['pages']}")

            if parent["warnings"]:
                st.warning("Cảnh báo: " + ", ".join(str(item) for item in parent["warnings"]))

            if parent["supporting_children"]:
                st.markdown("**Children hỗ trợ**")
                for child in parent["supporting_children"]:
                    badge = "⭐ anchor" if child["is_anchor"] else "•"
                    st.markdown(f"{badge} {child['child_id']}")
                    if child["query_ids"]:
                        st.caption(f"Query ids: {', '.join(child['query_ids'])}")
                    if child["snippet"]:
                        st.caption(f"Đoạn trích: {child['snippet']}")
            else:
                st.caption("Không có child hỗ trợ.")

            parent_text = (parent.get("parent_text") or "").strip()
            if parent_text:
                preview = parent_text[:900]
                if len(parent_text) > 900:
                    preview += "..."
                with st.expander("Xem văn bản parent", expanded=False):
                    st.write(preview)


def render_mode_comparison(compare_result: dict[str, Any]) -> None:
    if not compare_result or compare_result.get("status") != "success":
        st.info("Chưa có kết quả so sánh. Hãy chạy so sánh bằng một câu hỏi hợp lệ.")
        return
    rows = build_mode_comparison_rows(compare_result)
    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("Không có dữ liệu so sánh để hiển thị.")


def render_evaluation(report: dict[str, Any] | None, filename: str | None) -> None:
    if report is None:
        if filename:
            st.error(f"Không thể đọc báo cáo JSON: {filename}")
        else:
            st.info("Chưa có báo cáo evaluation. Hãy chạy lệnh tạo report ở thư mục rag_advanced/buoi_09/reports trước khi mở tab này.")
            st.code("python rag_advanced/buoi_09/evaluate.py --input rag_advanced/buoi_09/eval/questions.json --output rag_advanced/buoi_09/reports/evaluation_report.json --k 3 --strategy hierarchical --model-name buoi_09-offline")
        return
    st.markdown(f"**Báo cáo:** {filename}")
    metrics = report.get("metrics") or report.get("results") or report.get("evaluation")
    if isinstance(metrics, dict):
        rows = []
        for label, values in metrics.items():
            if not isinstance(values, dict):
                continue
            rows.append(
                {
                    "label": label,
                    "recall@k": values.get("recall@k"),
                    "mrr@k": values.get("mrr@k"),
                    "ndcg@k": values.get("ndcg@k"),
                    "latency_ms": values.get("latency_ms"),
                    "context_chars": values.get("context_chars"),
                }
            )
        if rows:
            st.dataframe(rows, use_container_width=True)
    if report.get("needs_human_review"):
        st.warning("Gold labels được đánh dấu needs_human_review=true. Cần đánh giá thủ công.")


def render_answer_tab(question: str, query_result: dict[str, Any] | None) -> None:
    with st.form("ask_form"):
        st.text_area("Câu hỏi", value=question, key="ask_question", height=120)
        run_button = st.form_submit_button("Chạy Advanced RAG")
    if run_button:
        st.session_state["last_query_result"] = None
        if not question.strip():
            st.error("Vui lòng nhập câu hỏi hợp lệ.")
            return
        try:
            query_result = query(
                question,
                st.session_state["runtime_config"]["mode"],
                config=st.session_state["runtime_config"],
                input_dir=DEFAULT_INPUT_DIR,
                output_dir=HIERARCHY_DIR,
            )
            st.session_state["last_query_result"] = query_result
        except NotImplementedError as exc:
            st.error(str(exc))
            return
        except Exception:
            st.error("Đã xảy ra lỗi truy vấn. Vui lòng kiểm tra cấu hình và thử lại.")
            return
    if not query_result:
        st.info("Nhấn nút để chạy truy vấn. Kết quả sẽ được giữ trong phiên làm việc.")
        return

    status = query_result.get("status", "unknown")
    answer_text = query_result.get("answer", "").strip()
    citations = query_result.get("citations", [])
    warnings = query_result.get("trace", {}).get("warnings", [])
    query_set = query_result.get("query_set", {}) or {}
    trace = query_result.get("trace", {}) or {}

    st.subheader("Kết quả trả lời")
    st.markdown(f"**Trạng thái:** `{status}`")
    if query_set.get("status"):
        st.caption(f"Query set: {query_set['status']}")
    if query_set.get("error"):
        st.error(query_set["error"])

    if answer_text:
        st.success("Đã tìm thấy câu trả lời có thể sử dụng.")
        st.markdown(answer_text)
    else:
        st.info("Chưa có câu trả lời đủ điều kiện để hiển thị. Hãy kiểm tra trạng thái và bằng chứng được chọn.")

    if citations:
        st.subheader("Bằng chứng và trích dẫn")
        for citation in citations:
            st.markdown(format_citation(citation))
    else:
        st.caption("Không có trích dẫn nào được ánh xạ từ đáp án.")

    if warnings:
        st.subheader("Cảnh báo")
        for warning in warnings:
            st.warning(warning)

    evidence = query_result.get("accepted_evidence", [])
    if evidence:
        with st.expander("Tóm tắt bằng chứng đã chọn", expanded=False):
            for item in evidence[:5]:
                st.markdown(f"- {item.get('parent_id') or item.get('child_id')}: {item.get('text', '')[:220]}")

    st.markdown("**Thống kê**")
    metrics = trace
    cols = st.columns(3)
    cols[0].metric("Số gọi Gen", query_set.get("generation_call_count", 0))
    cols[1].metric("Số gọi Embedding", metrics.get("semantic_embedding_call_count", 0))
    cols[2].metric("Tổng độ trễ (ms)", sum(item.get("retrieval_latency_ms", 0.0) for item in metrics.get("queries", [])))

    st.subheader("Phân tán truy vấn")
    cards = build_query_cards(query_result)
    render_query_cards(cards)


def main() -> None:
    st.set_page_config(page_title="RAG Foundation — Buổi 09: Truy vấn đa câu hỏi & Truy xuất cha-con", layout="wide")
    st.title("RAG Foundation — Buổi 09: Truy vấn đa câu hỏi & Truy xuất cha-con")
    st.caption("Phân tán truy vấn → Truy xuất lai mỗi truy vấn → RRF chéo truy vấn → Mở rộng parent → Rerank parent")

    if "runtime_config" not in st.session_state:
        config = load_config()
        config["mode"] = "multi_parent"
        st.session_state["runtime_config"] = config
    runtime_config = render_sidebar(st.session_state["runtime_config"])
    st.session_state["runtime_config"].update(runtime_config)

    if "last_query_result" not in st.session_state:
        st.session_state["last_query_result"] = None
    if "last_compare_result" not in st.session_state:
        st.session_state["last_compare_result"] = None

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Nhập câu hỏi",
            "Phân tán truy vấn",
            "Khám phá cha-con",
            "So sánh chế độ",
            "Đánh giá",
        ]
    )

    with tab1:
        st.header("Nhập câu hỏi")
        render_answer_tab(st.session_state.get("ask_question", ""), st.session_state.get("last_query_result"))

    with tab2:
        st.header("Phân tán truy vấn")
        query_result = st.session_state.get("last_query_result")
        if not query_result:
            st.info("Chưa có kết quả truy vấn. Hãy chạy tab ‘Nhập câu hỏi’ trước.")
        else:
            cards = build_query_cards(query_result)
            render_query_cards(cards)
            query_ids, matrix_rows = build_query_matrix(query_result)
            if matrix_rows:
                st.subheader("Query–Child matrix")
                st.dataframe(matrix_rows, use_container_width=True)
            else:
                st.info("Không có child hits để xây ma trận.")

    with tab3:
        st.header("Khám phá cha-con")
        parent_result = st.session_state.get("last_query_result")
        if not parent_result:
            st.info("Chưa có kết quả parent. Hãy chạy tab ‘Nhập câu hỏi’ trước.")
        else:
            tree = build_parent_tree_data(parent_result)
            render_parent_tree(tree)

    with tab4:
        st.header("So sánh chế độ")
        with st.form("compare_form"):
            st.text_area("Câu hỏi so sánh", value=st.session_state.get("compare_question", ""), key="compare_question", height=120)
            compare_button = st.form_submit_button("Chạy so sánh 4 chế độ")
        if compare_button:
            question = st.session_state.get("compare_question", "")
            if not question.strip():
                st.error("Vui lòng nhập câu hỏi so sánh.")
            else:
                try:
                    compare_result = compare(
                        question,
                        config=st.session_state["runtime_config"],
                        input_dir=DEFAULT_INPUT_DIR,
                        output_dir=HIERARCHY_DIR,
                    )
                    st.session_state["last_compare_result"] = compare_result
                except Exception:
                    st.error("So sánh thất bại. Hãy kiểm tra hierarchy và cấu hình.")
        render_mode_comparison(st.session_state.get("last_compare_result") or {})

    with tab5:
        st.header("Đánh giá")
        report, filename = load_latest_report()
        render_evaluation(report, filename)


if __name__ == "__main__":
    main()
