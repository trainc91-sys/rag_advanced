import os
import sys
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.config import VALID_ROLES
from src.secure_retriever import SecureRetriever

st.set_page_config(
    page_title="Hệ Thống RAG & Đánh Giá Ragas — Buổi 16",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern visual design & RBAC badges
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 40%, #312e81 70%, #4338ca 100%);
        padding: 2rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(67, 56, 202, 0.3);
        border: 1px solid #4338ca;
    }
    
    .main-header h1 {
        font-weight: 800;
        font-size: 2.1rem;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        font-size: 1.02rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }

    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #4338ca;
    }
    .metric-label {
        font-size: 0.88rem;
        color: #64748b;
        font-weight: 600;
        margin-top: 0.2rem;
    }

    .result-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #4338ca;
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .citation-badge {
        background-color: #e0e7ff;
        color: #3730a3;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
    }
    .role-badge {
        background-color: #fef3c7;
        color: #92400e;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        margin-left: 0.5rem;
    }
    .score-badge {
        background-color: #dcfce7;
        color: #166534;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        margin-left: 0.5rem;
    }
    .security-alert-box {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e40af;
        padding: 0.8rem 1.2rem;
        border-radius: 10px;
        margin-bottom: 1.2rem;
        font-size: 0.95rem;
    }
    .graph-hint-box {
        background-color: #0f172a;
        color: #f8fafc;
        padding: 1.2rem;
        border-radius: 10px;
        font-family: monospace;
        font-size: 0.85rem;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# Main Banner Header
st.markdown("""
<div class="main-header">
    <h1>🛡️ Hệ Thống Tra Cứu RAG An Toàn & Đánh Giá Tự Động Ragas (Buổi 16)</h1>
    <p>Kiểm soát Truy cập dựa trên Vai trò (RBAC) & Tự động hóa Đánh giá Hiệu năng RAG bằng Ragas Framework</p>
</div>
""", unsafe_allow_html=True)

# Load SecureRetriever
@st.cache_resource
def get_secure_retriever():
    return SecureRetriever()

retriever = get_secure_retriever()

# Tab Navigation
tab_eval, tab_search = st.tabs(["📊 Đánh Giá Ragas (Buổi 16)", "🛡️ Tra Cứu RAG & RBAC (Buổi 15)"])

# ==================== TAB 1: RAGAS EVALUATION ====================
with tab_eval:
    st.subheader("📈 Báo Cáo Hiệu Năng Hệ Thống RAG (Ragas Evaluation)")
    
    results_path = os.path.join("data", "eval", "evaluation_results.csv")
    report_path = os.path.join("outputs", "ragas_evaluation_report.md")
    qa_path = os.path.join("data", "eval", "qa_dataset.csv")

    if os.path.exists(results_path):
        df_eval = pd.read_csv(results_path)
        
        prec = df_eval["context_precision"].mean()
        rec = df_eval["context_recall"].mean()
        faith = df_eval["faithfulness"].mean()
        rel = df_eval["answer_relevancy"].mean()
        overall = (prec + rec + faith + rel) / 4.0

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{rec:.4f}</div><div class="metric-label">Context Recall</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{prec:.4f}</div><div class="metric-label">Context Precision</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{faith:.4f}</div><div class="metric-label">Faithfulness</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{rel:.4f}</div><div class="metric-label">Answer Relevancy</div></div>', unsafe_allow_html=True)
        with col5:
            st.markdown(f'<div class="metric-card" style="border: 2px solid #4338ca;"><div class="metric-value" style="color:#312e81;">{overall:.4f}</div><div class="metric-label">RAGAS OVERALL</div></div>', unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        
        sub_t1, sub_t2, sub_t3 = st.tabs(["📄 Báo Cáo Markdown (Full Report)", "📋 Bảng Kết Quả Chi Tiết (20 Samples)", "🎯 Bộ Câu Hỏi Golden Dataset"])
        
        with sub_t1:
            if os.path.exists(report_path):
                with open(report_path, "r", encoding="utf-8") as f:
                    report_content = f.read()
                st.markdown(report_content)
            else:
                st.info("Chưa tìm thấy tệp ragas_evaluation_report.md.")
                
        with sub_t2:
            st.dataframe(df_eval[["question_id", "usecase", "difficulty", "question", "answer", "context_precision", "context_recall", "faithfulness", "answer_relevancy"]], use_container_width=True)
            
        with sub_t3:
            if os.path.exists(qa_path):
                df_qa = pd.read_csv(qa_path)
                st.dataframe(df_qa, use_container_width=True)
    else:
        st.warning("⚠️ Chưa tìm thấy tệp kết quả đánh giá evaluation_results.csv. Hãy chạy tập lệnh scripts/evaluate_rag_pipeline.py.")

# ==================== TAB 2: SECURE RAG SEARCH ====================
with tab_search:
    st.sidebar.markdown("---")
    st.sidebar.header("🔑 Phân quyền Vai trò (RBAC Role Selector)")
    st.sidebar.markdown("Chọn vai trò đóng vai khi gửi truy vấn:")

    user_roles_selected = []
    for r in VALID_ROLES:
        default_val = True if r in ["Staff", "Guest"] else False
        if st.sidebar.checkbox(f"Role: {r}", value=default_val, key=f"role_{r}"):
            user_roles_selected.append(r)

    if not user_roles_selected:
        user_roles_selected = ["Guest"]
        st.sidebar.warning("⚠️ Chưa chọn vai trò nào, tự động gán mặc định: Guest")

    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Cấu hình Retrieval")

    query_input = st.sidebar.text_area(
        "Nhập câu hỏi tra cứu:",
        value="Theo Thông tư 01/2014/TT-NHNN việc vận chuyển tài sản quý được quy định như thế nào?",
        height=110,
        key="search_query"
    )

    method_option = st.sidebar.selectbox(
        "Phương pháp Retrieval:",
        options=["Hybrid + Rerank", "Hybrid (RRF)", "BM25 (Lexical)", "Dense (Embedding)"],
        index=0,
        key="search_method"
    )

    top_k = st.sidebar.slider("Top-k Kết quả:", min_value=1, max_value=15, value=5, key="top_k")
    candidate_k = st.sidebar.slider("Số lượng Ứng viên (Candidate-N):", min_value=5, max_value=30, value=20, key="candidate_k")

    search_button = st.sidebar.button("🚀 Tìm kiếm an toàn", type="primary", use_container_width=True)

    if search_button or query_input:
        method_map = {
            "BM25 (Lexical)": "bm25",
            "Dense (Embedding)": "dense",
            "Hybrid (RRF)": "hybrid",
            "Hybrid + Rerank": "hybrid_rerank"
        }
        
        selected_method_key = method_map[method_option]
        
        with st.spinner(f"Đang thực hiện retrieval an toàn cho vai trò {user_roles_selected}..."):
            response = retriever.retrieve(
                question=query_input,
                user_roles=user_roles_selected,
                method=selected_method_key,
                top_k=top_k,
                candidate_k=candidate_k
            )

        results = response['results']
        accessible_count = response['accessible_chunks_count']
        filtered_out_count = response['filtered_out_count']

        st.markdown(f"""
        <div class="security-alert-box">
            🔒 <b>Trạng thái phân quyền:</b> Bạn đang đóng vai <code>{user_roles_selected}</code> | 
            Đã truy cập <b>{accessible_count}</b> / {response['total_chunks_in_corpus']} chunks | 
            <span style="color: #b91c1c;">Đã lọc bỏ <b>{filtered_out_count}</b> chunks nhạy cảm không đủ quyền xem</span>.
        </div>
        """, unsafe_allow_html=True)

        st.subheader(f"📌 Kết quả Tra cứu ({method_option})")
        if not results:
            st.info("❌ Không tìm thấy kết quả nào phù hợp hoặc tất cả tài liệu liên quan đã bị ẩn do không đủ quyền truy cập.")
        else:
            st.write(f"Hiển thị **Top {len(results)}** kết quả được phép truy cập cho câu hỏi: *\"{query_input}\"*")

            doc_ids = [r['document_id'] for r in results]
            chunk_ids = [r['chunk_id'] for r in results]

            col1, col2 = st.columns([2, 1])

            with col1:
                for r in results:
                    allowed_str = ", ".join(r['allowed_roles']) if isinstance(r['allowed_roles'], list) else str(r['allowed_roles'])
                    st.markdown(f"""
                    <div class="result-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                            <span class="citation-badge">📚 {r['citation']}</span>
                            <div>
                                <span class="role-badge">🔒 Quyền xem: [{allowed_str}]</span>
                                <span class="score-badge">Rank #{r['rank']} | Score: {r['score']}</span>
                            </div>
                        </div>
                        <div style="margin-top: 0.75rem; color: #334155; line-height: 1.6;">
                            {r['text']}
                        </div>
                        <div style="margin-top: 0.75rem; font-size: 0.8rem; color: #64748b;">
                            Chunk ID: <code>{r['chunk_id']}</code> | Document ID: <code>{r['document_id']}</code> | Method: <b>{r['retrieval_method']}</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                st.subheader("📊 Metrics & Security")
                table_data = []
                for r in results:
                    table_data.append({
                        "Rank": r['rank'],
                        "Chunk ID": r['chunk_id'],
                        "Score": r['score'],
                        "Allowed Roles": ", ".join(r['allowed_roles']) if isinstance(r['allowed_roles'], list) else str(r['allowed_roles'])
                    })
                st.dataframe(pd.DataFrame(table_data), use_container_width=True)

                st.subheader("🕸️ Secure Graph Hints (Neo4j)")
                hints = retriever.get_graph_hints(doc_ids, chunk_ids, user_roles=user_roles_selected)
                
                st.markdown(f"""
                <div class="graph-hint-box">
                    <b>Neo4j Status:</b> <span style="color: {'#4ade80' if hints['status'] == 'CONNECTED' else '#f87171'}">{hints['status']}</span><br/>
                    <b>Active User Roles:</b> <code>{hints['user_roles']}</code><br/><br/>
                    <b>Retrieved Documents:</b><br/>
                    <code>{hints['document_ids']}</code><br/><br/>
                    <b>Direct Graph Relations (Role-Filtered):</b><br/>
                    {"<br/>".join(["• " + rel for rel in hints['relations']]) if hints['relations'] else "Không có quan hệ hoặc bị giới hạn bởi quyền truy cập."}
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")
st.caption("AI Coding Agent — Buổi 16 RAG Evaluation bằng Ragas & Buổi 15 RBAC Secure Retrieval Pipeline")
