"""
Streamlit Application for Buổi 11 — Vietnamese Law GraphRAG Explorer
---------------------------------------------------------------------
Giao diện quản lý & kiểm thử Multihop Graph RAG cho hệ thống văn bản luật Việt Nam.
"""

import time
import streamlit as st

import config
from graph_rag import MultihopGraphRAG
import gemini_qa
from run_qa_comparison import TEST_QUESTIONS

# -----------------------------------------------------------------------------
# Cấu hình trang Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Vietnamese Law GraphRAG Explorer",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Custom CSS để tái tạo chuẩn giao diện như ảnh thiết kế mẫu
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Tổng thể & nền */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Header chính */
    .main-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 12px;
        margin-bottom: 20px;
        border-bottom: 1px solid #E2E8F0;
    }
    
    .main-title {
        font-size: 24px;
        font-weight: 700;
        color: #1E293B;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Metric card kiểu hộp thông tin trong mỗi cột Hops */
    .metric-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .metric-item {
        display: flex;
        align-items: center;
        font-size: 13px;
        color: #475569;
        margin-bottom: 4px;
    }
    
    .metric-item strong {
        color: #0F172A;
        margin-left: 4px;
    }
    
    /* Document preview box */
    .doc-card {
        background-color: #F1F5F9;
        border-left: 4px solid #3B82F6;
        border-radius: 4px;
        padding: 8px 12px;
        margin-bottom: 8px;
        font-size: 13px;
    }

    /* Nút bấm nổi bật */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"
if "qa_cache" not in st.session_state:
    st.session_state.qa_cache = {}

# -----------------------------------------------------------------------------
# Sidebar: Tham số & System Prompt
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📊 Tham số Tìm kiếm")
    
    hops_setting = st.slider(
        "Số bước nhảy mở rộng (N-Hops)",
        min_value=0,
        max_value=3,
        value=1,
        help="Số bước nhảy duyệt đồ thị qua các quan hệ pháp lý CAN_CU, THAY_THE, HOP_NHAT, SUA_DOI_BO_SUNG"
    )
    
    top_k_setting = st.slider(
        "Số lượng phân đoạn (Top-k)",
        min_value=1,
        max_value=15,
        value=4,
        help="Số đoạn văn bản khớp trực tiếp lấy từ bước tìm kiếm ban đầu"
    )
    
    st.markdown("---")
    st.markdown("### 📝 Prompt Hệ thống (System Prompt)")
    st.caption("Tự tùy chỉnh System Instruction")
    
    system_instruction = st.text_area(
        label="System Instruction",
        value="Trả lời dựa trên ngữ cảnh được cung cấp.",
        height=100,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption("💡 **Graph Database**: Neo4j (`kb-hops`)")
    st.caption("🤖 **LLM Model**: Gemini 3.5 Flash / Flash Lite")

# -----------------------------------------------------------------------------
# Main Header
# -----------------------------------------------------------------------------
col_title, col_toggle = st.columns([4, 1])

with col_title:
    st.markdown("<div class='main-title'>🔷 Vietnamese Law GraphRAG Explorer</div>", unsafe_allow_html=True)

with col_toggle:
    st.button("🌙 Tối", use_container_width=True)

# -----------------------------------------------------------------------------
# Tabs Navigation
# -----------------------------------------------------------------------------
tab_qa, tab_compare, tab_graph = st.tabs([
    "💬 Tra cứu & QA", 
    "📊 So sánh N-Hops", 
    "🏛️ Tổng quan Đồ thị"
])

# =============================================================================
# TAB 1: Tra cứu & QA
# =============================================================================
with tab_qa:
    st.subheader("💬 Tra cứu Pháp luật & Hỏi đáp Đa bước (Graph RAG)")
    st.markdown("Nhập câu hỏi liên quan tới các Nghị định, Thông tư, Luật kinh doanh bảo hiểm, ngân hàng...")
    
    user_question = st.text_input(
        "Nhập câu hỏi của bạn:",
        value="Nghị định 46/2023/NĐ-CP thay thế cho nghị định nào, và nghị định bị thay thế đó có nội dung gì nổi bật về kinh doanh bảo hiểm?",
        key="single_question_input"
    )
    
    if st.button("🔍 Truy vấn Graph RAG", type="primary", use_container_width=True):
        if not user_question.strip():
            st.warning("Vui lòng nhập câu hỏi.")
        else:
            with st.spinner("Đang truy vấn đồ thị Neo4j và tổng hợp bằng Gemini..."):
                start_time = time.time()
                try:
                    with MultihopGraphRAG() as rag:
                        if not rag.verify_connectivity():
                            st.error("Không thể kết nối tới cơ sở dữ liệu Neo4j.")
                        else:
                            retrieval = rag.retrieve_context(user_question, top_k=top_k_setting, hops=hops_setting)
                            elapsed = time.time() - start_time
                            
                            answer = gemini_qa.answer_question(user_question, retrieval["context_text"])
                            
                            st.success(f"Thời gian truy vấn & trả lời: **{elapsed:.4f}s**")
                            
                            st.markdown("### 🤖 Câu trả lời từ Gemini")
                            st.info(answer)
                            
                            st.markdown("### 📚 Chi tiết Ngữ cảnh Truy vấn")
                            st.write(f"- **Số đoạn khớp trực tiếp (Seed):** {len(retrieval['seed_chunks'])}")
                            st.write(f"- **Số đoạn lấy thêm qua Multi-hop:** {len(retrieval['hop_chunks'])}")
                            
                            with st.expander("Xem toàn bộ văn bản ngữ cảnh (Context Block)", expanded=False):
                                st.code(retrieval["context_text"] or "(Không có ngữ cảnh)", language="text")
                except Exception as e:
                    st.error(f"Xảy ra lỗi trong quá trình xử lý: {e}")

# =============================================================================
# TAB 2: So sánh N-Hops (Interface matching user uploaded image!)
# =============================================================================
with tab_compare:
    st.markdown("## 📊 So sánh Hiệu quả Đa bước (N-Hops)")
    st.markdown("Chọn một câu hỏi bên dưới để chạy so sánh sự khác biệt của ngữ cảnh và câu trả lời thu được khi số bước nhảy tăng từ **0 đến 2**.")
    
    selected_question = st.selectbox(
        "Chọn câu hỏi để đánh giá:",
        options=TEST_QUESTIONS,
        index=0
    )
    
    run_comparison_btn = st.button("🔍 Chạy So sánh Đánh giá", type="primary", use_container_width=True)
    
    if run_comparison_btn or selected_question:
        with st.spinner("Đang thực hiện truy vấn so sánh qua 3 mức hops (0, 1, 2)..."):
            results_by_hop = {}
            with MultihopGraphRAG() as rag:
                if rag.verify_connectivity():
                    for h in [0, 1, 2]:
                        t0 = time.time()
                        retrieval = rag.retrieve_context(selected_question, top_k=top_k_setting, hops=h)
                        t_elapsed = time.time() - t0
                        
                        try:
                            ans = gemini_qa.answer_question(selected_question, retrieval["context_text"])
                        except Exception as ex:
                            ans = f"[Lỗi Gemini]: {ex}"
                            
                        # Unique documents count & relationships count
                        docs = set(c.document_title for c in retrieval["all_chunks"])
                        rels_count = sum(len(c.path_relationships) for c in retrieval["hop_chunks"])
                        
                        results_by_hop[h] = {
                            "time": t_elapsed,
                            "n_docs": len(docs),
                            "n_links": rels_count,
                            "n_chunks": len(retrieval["all_chunks"]),
                            "n_seed": len(retrieval["seed_chunks"]),
                            "n_hop": len(retrieval["hop_chunks"]),
                            "seed_chunks": retrieval["seed_chunks"],
                            "hop_chunks": retrieval["hop_chunks"],
                            "context_text": retrieval["context_text"],
                            "answer": ans
                        }

            # Render 3 Columns for Hops = 0, Hops = 1, Hops = 2
            col_h0, col_h1, col_h2 = st.columns(3)
            
            hop_cols = [
                (0, col_h0, "📋 Số bước nhảy Hops = 0"),
                (1, col_h1, "📋 Số bước nhảy Hops = 1"),
                (2, col_h2, "📋 Số bước nhảy Hops = 2")
            ]
            
            for h_val, col_obj, col_title_str in hop_cols:
                data = results_by_hop.get(h_val, {})
                with col_obj:
                    st.markdown(f"### {col_title_str}")
                    
                    # Metric Box
                    if data:
                        st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-item">⏱️ Thời gian truy vấn: <strong>{data['time']:.4f}s</strong></div>
                            <div class="metric-item">📜 Tài liệu tìm được: <strong>{data['n_docs']}</strong></div>
                            <div class="metric-item">🔗 Số liên kết: <strong>{data['n_links']}</strong></div>
                            <div class="metric-item">🧩 Số phân đoạn: <strong>{data['n_chunks']}</strong></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("**Các tài liệu tìm thấy:**")
                        seen_titles = []
                        for c in (data["seed_chunks"] + data["hop_chunks"]):
                            if c.document_title not in seen_titles:
                                seen_titles.append(c.document_title)
                                tag_str = "Khớp trực tiếp" if c.hop == 0 else f"Liên quan ({' -> '.join(c.path_relationships)})"
                                st.markdown(f"- **{c.document_title}** *({tag_str})*")
                        
                        st.markdown("---")
                        st.markdown("**Câu trả lời:**")
                        st.write(data["answer"])
                        
                        with st.expander(f"Chi tiết ngữ cảnh (Hops={h_val})"):
                            st.code(data["context_text"] or "(Không có ngữ cảnh)", language="text")

# =============================================================================
# TAB 3: Tổng quan Đồ thị
# =============================================================================
with tab_graph:
    st.subheader("🏛️ Tổng quan Đồ thị Tri thức 法律 (Neo4j Graph Database)")
    st.markdown("Thống kê về các thực thể Document, Chunk và mối quan hệ pháp lý trong đồ thị.")
    
    with MultihopGraphRAG() as rag:
        if not rag.verify_connectivity():
            st.error("Không thể kết nối Neo4j.")
        else:
            with rag._driver.session(database=rag._database) as session:
                # Dem so luong Node Document & Chunk
                n_docs = session.run("MATCH (d:Document) RETURN count(d) AS cnt").single()["cnt"]
                n_chunks = session.run("MATCH (c:Chunk) RETURN count(c) AS cnt").single()["cnt"]
                n_rels = session.run(
                    "MATCH ()-[r:CAN_CU|THAY_THE|HOP_NHAT|SUA_DOI_BO_SUNG]->() RETURN count(r) AS cnt"
                ).single()["cnt"]
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Tổng số Văn bản (Document)", n_docs)
                m2.metric("Tổng số Phân đoạn (Chunk)", n_chunks)
                m3.metric("Tổng số Quan hệ Pháp lý", n_rels)
                
                st.markdown("---")
                st.markdown("### 🕸️ Danh sách các Quan hệ Pháp lý tiêu biểu trong Đồ thị")
                rels_query = """
                MATCH (d1:Document)-[r:CAN_CU|THAY_THE|HOP_NHAT|SUA_DOI_BO_SUNG]->(d2:Document)
                RETURN d1.title AS doc1, type(r) AS rel_type, d2.title AS doc2
                LIMIT 20
                """
                records = session.run(rels_query)
                table_data = [{"Văn bản A": r["doc1"], "Loại quan hệ": r["rel_type"], "Văn bản B": r["doc2"]} for r in records]
                st.table(table_data)
