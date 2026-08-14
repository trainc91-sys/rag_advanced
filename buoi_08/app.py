"""Streamlit dashboard cho Buổi 08 Advanced RAG."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from rag_foundation.buoi_08 import advanced_rag, rag

REPORT_DIR = Path(__file__).resolve().parent / "reports"
MODES = ["bm25", "semantic", "hybrid", "hybrid_rerank"]


def _get_effective_reranker_device() -> str:
    configured = advanced_rag.CONFIG["rerank_device"]
    if configured != "auto":
        return configured

    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


@st.cache_data(show_spinner=False)
def load_status(strategy: str) -> dict[str, Any]:
    return rag.get_status(strategy)


@st.cache_data(show_spinner=False)
def load_corpus(strategy: str) -> list[dict[str, Any]]:
    return advanced_rag.load_chunks(advanced_rag.DEFAULT_INPUT_DIR, strategy)


@st.cache_data(show_spinner=False)
def load_evaluation_report() -> tuple[dict[str, Any] | None, str | None]:
    paths = sorted(REPORT_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not paths:
        return None, None
    latest = paths[0]
    try:
        with latest.open("r", encoding="utf-8") as handle:
            return json.load(handle), latest.name
    except Exception:
        return None, latest.name


def _format_status_item(value: Any) -> str:
    if isinstance(value, bool):
        return "Có" if value else "Không"
    if value is None:
        return "Không sẵn sàng"
    return str(value)


def _safe_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _display_evidence_card(evidence: dict[str, Any], index: int) -> None:
    title = f"Bằng chứng {index} — chunk_id={evidence.get('chunk_id')}"
    with st.expander(title, expanded=False):
        st.markdown(f"**Được chấp nhận:** {'✅' if evidence.get('accepted') else '❌'}")
        st.markdown(f"**Hạng:** {evidence.get('rank')}")
        st.markdown(f"**BM25:** {evidence.get('bm25_rank')} / {evidence.get('bm25_score')}")
        st.markdown(f"**Semantic:** {evidence.get('semantic_rank')} / {evidence.get('semantic_distance')}")
        st.markdown(f"**RRF:** {evidence.get('fused_rank')} / {evidence.get('rrf_score')}")
        st.markdown(f"**Rerank:** {evidence.get('rerank_rank')} / {evidence.get('rerank_score')} ({evidence.get('rerank_raw_score')})")
        st.markdown(f"**Thay đổi hạng:** {evidence.get('rank_change')}")
        st.markdown(f"**Nguồn:** {evidence.get('source')}")
        st.markdown(f"**Trang:** {evidence.get('page_start')}-{evidence.get('page_end')}")
        st.write(evidence.get("text", ""))


def _build_comparison_rows(comparison: dict[str, Any]) -> list[dict[str, Any]]:
    if not comparison or comparison.get("status") != "success":
        return []

    mode_lookup = {item.get("mode"): item for item in comparison.get("modes", []) if isinstance(item, dict)}
    rows: list[dict[str, Any]] = []
    for row in comparison.get("comparison_table", []):
        chunk_id = row.get("chunk_id")
        row_data: dict[str, Any] = {"chunk_id": chunk_id, "final_modes": ", ".join(row.get("modes", []))}
        for mode in MODES:
            mode_result = mode_lookup.get(mode, {})
            candidate = next(
                (
                    item
                    for item in mode_result.get("candidates", [])
                    if str(item.get("chunk_id")) == str(chunk_id)
                ),
                None,
            )
            if not candidate:
                continue
            if mode == "bm25":
                row_data["bm25_rank"] = candidate.get("bm25_rank") if candidate.get("bm25_rank") is not None else candidate.get("rank")
            elif mode == "semantic":
                row_data["semantic_rank"] = candidate.get("semantic_rank") if candidate.get("semantic_rank") is not None else candidate.get("rank")
            elif mode == "hybrid":
                row_data["fused_rank"] = candidate.get("fused_rank") if candidate.get("fused_rank") is not None else candidate.get("rank")
            elif mode == "hybrid_rerank":
                row_data["rerank_rank"] = candidate.get("rerank_rank") if candidate.get("rerank_rank") is not None else candidate.get("rank")
                row_data["rank_change"] = candidate.get("rank_change")
        rows.append(row_data)
    return rows


def _render_comparison_panels(comparison: dict[str, Any]) -> None:
    if not comparison or comparison.get("status") != "success":
        st.info("Chưa có dữ liệu so sánh. Vui lòng chạy lại với một câu hỏi hợp lệ.")
        return

    st.subheader("Bảng so sánh hạng chung")
    rows = _build_comparison_rows(comparison)
    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("Không có hàng dữ liệu để hiển thị.")

    st.subheader("Top-k từng chế độ")
    cols = st.columns(4)
    mode_titles = {
        "bm25": "BM25",
        "semantic": "Semantic",
        "hybrid": "Hybrid RRF",
        "hybrid_rerank": "Hybrid + Rerank",
    }
    for idx, mode in enumerate(MODES):
        with cols[idx]:
            st.markdown(f"### {mode_titles.get(mode, mode)}")
            mode_data = next((item for item in comparison.get("modes", []) if item.get("mode") == mode), None)
            if not mode_data:
                st.write("Không có dữ liệu")
                continue
            for item in mode_data.get("candidates", [])[:10]:
                label = f"{item.get('chunk_id')}"
                rank = item.get("rank")
                st.markdown(f"- **{label}**: hạng={rank}")
                if mode == "hybrid_rerank" and item.get("rank_change") is not None:
                    st.caption(f"thay đổi hạng={item.get('rank_change')}")


def _render_trace(query_result: dict[str, Any] | None) -> None:
    st.subheader("Dòng chảy xử lý")
    if not query_result:
        st.info("Chưa có kết quả truy vấn. Chạy tab 'Hỏi đáp Advanced RAG' trước để xem dòng chảy xử lý.")
        return

    trace = query_result.get("trace", {})
    counts = [
        ("Ứng viên BM25", trace.get("bm25_candidates", 0)),
        ("Ứng viên Semantic", trace.get("semantic_candidates", 0)),
        ("Hợp nhất / chồng lấp", trace.get("overlap", 0)),
        ("Đã rerank", trace.get("reranked", 0)),
        ("Được chấp nhận", trace.get("accepted", 0)),
    ]
    cols = st.columns(5)
    for idx, (label, value) in enumerate(counts):
        cols[idx].metric(label, value)

    st.markdown("**Độ trễ từng bước**")
    latencies = trace.get("latency_ms", {})
    latency_cols = st.columns(4)
    latency_cols[0].metric("BM25 (ms)", f"{latencies.get('bm25', 0.0):.1f}")
    latency_cols[1].metric("Semantic (ms)", f"{latencies.get('semantic', 0.0):.1f}")
    latency_cols[2].metric("RRF / hợp nhất (ms)", f"{latencies.get('fusion', 0.0):.1f}")
    latency_cols[3].metric("Rerank (ms)", f"{latencies.get('rerank', 0.0):.1f}")
    st.metric("Tổng (ms)", f"{latencies.get('total', 0.0):.1f}")

    st.markdown(
        """
        - Điểm số BM25 cao hơn là tốt hơn.
        - Khoảng cách cosine thấp hơn là tốt hơn.
        - Điểm số RRF / rerank cao hơn là tốt hơn.
        - Điểm score rerank không phải xác suất.
        """
    )


def _render_evaluation(report: dict[str, Any] | None, filename: str | None) -> None:
    st.subheader("Đánh giá")
    if report is None:
        if filename:
            st.error(f"Không thể đọc báo cáo JSON: {filename}")
        else:
            st.info("Chưa tìm thấy báo cáo JSON trong thư mục reports/.")
        return

    st.markdown(f"**Báo cáo:** {filename}")
    st.json(report)

    metrics = report.get("metrics") or report.get("results") or report.get("evaluation")
    if isinstance(metrics, dict):
        st.markdown("**Bảng metrics**")
        rows = []
        for mode, values in metrics.items():
            if not isinstance(values, dict):
                continue
            rows.append(
                {
                    "mode": mode,
                    "recall@k": values.get("recall_at_k"),
                    "mrr@k": values.get("mrr_at_k"),
                    "ndcg@k": values.get("ndcg_at_k"),
                    "latency_mean_ms": values.get("latency_mean_ms") or values.get("latency_mean"),
                    "latency_p50_ms": values.get("latency_p50_ms") or values.get("latency_p50"),
                }
            )
        if rows:
            st.dataframe(rows, use_container_width=True)

    if report.get("needs_human_review"):
        st.warning("Có gold labels vẫn đánh dấu needs_human_review=true.")

    if report.get("winner") is None:
        st.info("Không kết luận winner khi report chưa xác thực hoặc chưa có report hợp lệ.")


def main() -> None:
    st.set_page_config(page_title="Buổi 08 — RAG nâng cao", layout="wide")
    st.title("Buổi 08 — RAG nâng cao")

    with st.sidebar.expander("Cấu hình truy vấn", expanded=True):
        strategy = st.selectbox("Chiến lược", sorted(rag.VALID_STRATEGIES), index=2)
        mode = st.selectbox("Chế độ truy xuất", MODES, index=3)
        top_k = st.slider("Top-k cuối cùng", 1, 20, 5)
        question = st.text_area("Câu hỏi", st.session_state.get("question", ""))

    status = load_status(strategy)
    details = status.get("details", {})
    corpus = load_corpus(strategy)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Chẩn đoán**")
    st.sidebar.write(
        {
            "Chiến lược": strategy,
            "Chế độ truy xuất": mode,
            "Top-k cuối cùng": top_k,
            "Ứng viên BM25": advanced_rag.CONFIG["bm25_candidates"],
            "Ứng viên Semantic": advanced_rag.CONFIG["semantic_candidates"],
            "RRF k": advanced_rag.CONFIG["rrf_k"],
            "Trọng số BM25 trong RRF": advanced_rag.CONFIG["rrf_bm25_weight"],
            "Trọng số Semantic trong RRF": advanced_rag.CONFIG["rrf_semantic_weight"],
            "Mô hình reranker": advanced_rag.CONFIG["reranker_model"],
            "Thiết bị reranker": _get_effective_reranker_device(),
            "Cache reranker có sẵn": _format_status_item(details.get("reranker_cache_present")),
            "K ứng viên rerank": advanced_rag.CONFIG["rerank_candidates"],
            "Điểm tối thiểu rerank": advanced_rag.CONFIG["rerank_min_score"],
            "Bộ sưu tập Semantic tồn tại": _format_status_item(status.get("collection_exists")),
            "Số bản ghi Semantic": status.get("record_count"),
            "API key": _format_status_item(details.get("api_key_present")),
            "Kích thước corpus BM25": len(corpus),
        }
    )
    st.sidebar.caption("Không hiển thị secret. Không tự index hoặc tải model khi mở app.")

    if not status.get("collection_exists"):
        st.sidebar.info("Semantic index chưa sẵn sàng. Vui lòng chạy prepare-semantic khi cần đánh giá semantic hoặc hybrid_rerank thật.")
    if not details.get("reranker_cache_present"):
        st.sidebar.info("Cache reranker chưa có. Hybrid + rerank sẽ báo reranker_unavailable nếu được gọi mà chưa tải model.")

    tab_answer, tab_compare, tab_trace, tab_eval = st.tabs(
        ["Hỏi đáp Advanced RAG", "So sánh Retrieval", "Pipeline Trace", "Đánh giá"]
    )

    with tab_answer:
        st.header("Hỏi đáp Advanced RAG")
        run_answer = st.button("Chạy câu trả lời")
        if run_answer:
            st.session_state["question"] = question
            if not question.strip():
                st.warning("Vui lòng nhập câu hỏi.")
            else:
                with st.spinner("Đang chạy query..."):
                    try:
                        result = rag.run_query(question, top_k, strategy, mode)
                        st.session_state["answer_result"] = result
                    except Exception as exc:
                        st.session_state["answer_result"] = None
                        st.error(_safe_text(exc))

        answer_result = st.session_state.get("answer_result")
        if answer_result:
            status_value = answer_result.get("status")
            status_map = {
                "answered": "Đã trả lời",
                "insufficient_evidence": "Thiếu bằng chứng",
                "retrieval_only": "Chỉ truy xuất",
                "reranker_unavailable": "Reranker không khả dụng",
            }
            st.markdown(f"**Trạng thái:** {status_map.get(status_value, status_value)}")
            st.markdown(f"**Chế độ:** {answer_result.get('mode')}")
            st.markdown(f"**Bộ sưu tập:** {answer_result.get('collection_name')}")
            if answer_result.get("warnings"):
                st.warning("\n".join(answer_result.get("warnings", [])))
            if answer_result.get("status") == "reranker_unavailable":
                st.error(
                    "Reranker chưa sẵn sàng. Vui lòng chạy lại lệnh CLI prepare-semantic và kiểm tra cache model, hoặc chọn mode khác."
                )
            if answer_result.get("answer"):
                st.subheader("Câu trả lời")
                st.write(answer_result.get("answer"))
            if answer_result.get("citations"):
                st.subheader("Chú thích")
                st.table(answer_result.get("citations"))
            st.subheader("Bằng chứng")
            for idx, evidence in enumerate(answer_result.get("evidence", []), start=1):
                _display_evidence_card(evidence, idx)

    with tab_compare:
        st.header("So sánh Retrieval")
        run_compare = st.button("Chạy so sánh")
        if run_compare:
            st.session_state["question"] = question
            if not question.strip():
                st.warning("Vui lòng nhập câu hỏi.")
            else:
                with st.spinner("Đang chạy compare retrieval..."):
                    try:
                        compare_result = rag.compare(question, top_k, strategy)
                        st.session_state["compare_result"] = compare_result
                    except Exception as exc:
                        st.session_state["compare_result"] = None
                        st.error(_safe_text(exc))
        compare_result = st.session_state.get("compare_result")
        _render_comparison_panels(compare_result)

    with tab_trace:
        st.header("Pipeline Trace")
        _render_trace(st.session_state.get("answer_result"))

    with tab_eval:
        st.header("Đánh giá")
        report, filename = load_evaluation_report()
        _render_evaluation(report, filename)


if __name__ == "__main__":
    main()
