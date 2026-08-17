import os
import sys
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.config import VALID_ROLES
from src.secure_retriever import SecureRetriever

st.set_page_config(
    page_title="RAG Secure Retrieval & RBAC — Buổi 15",
    page_icon="🛡️",
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
        padding: 2.2rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
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

    .result-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #4338ca;
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    .citation-badge {
        display: inline-block;
        background-color: #eff6ff;
        color: #1d4ed8;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        border: 1px solid #bfdbfe;
        margin-bottom: 0.75rem;
    }

    .role-badge {
        display: inline-block;
        background-color: #fef2f2;
        color: #991b1b;
        font-weight: 700;
        font-size: 0.8rem;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        border: 1px solid #fecaca;
        margin-left: 0.5rem;
    }

    .score-badge {
        display: inline-block;
        background-color: #f0fdf4;
        color: #15803d;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        border: 1px solid #bbf7d0;
        margin-left: 0.5rem;
    }

    .security-alert-box {
        background-color: #fffbebf5;
        border: 1px solid #fcd34d;
        color: #92400e;
        padding: 1rem 1.25rem;
        border-radius: 10px;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }

    .graph-hint-box {
        background-color: #0f172a;
        color: #38bdf8;
        padding: 1.25rem;
        border-radius: 12px;
        font-family: monospace;
        font-size: 0.9rem;
        border: 1px solid #1e293b;
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_secure_retriever():
    return SecureRetriever()

with st.spinner("Đang khởi tạo Secure Retrieval Pipeline (Pre-indexing & RBAC Rules)..."):
    retriever = load_secure_retriever()

# Header Banner
st.markdown("""
<div class="main-header">
    <h1>🛡️ Secure RAG Retrieval & Role-Based Access Control (RBAC)</h1>
    <p>Hệ thống RAG bảo mật lọc quyền truy cập trực tiếp ở tầng dữ liệu, Vector Metadata, Cypher Neo4j và Cross-Encoder Reranking</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.header("🔐 Phân quyền & Tra cứu")

user_roles_selected = st.sidebar.multiselect(
    "👤 Vai trò của bạn (Your Roles):",
    options=VALID_ROLES,
    default=["Guest"],
    help="Chọn một hoặc nhiều vai trò để đóng vai (impersonate) khi thực hiện tìm kiếm."
)

if not user_roles_selected:
    user_roles_selected = ["Guest"]
    st.sidebar.warning("⚠️ Chưa chọn vai trò nào, tự động gán mặc định: Guest")

st.sidebar.markdown("---")
st.sidebar.header("🔍 Cấu hình Retrieval")

query_input = st.sidebar.text_area(
    "Nhập câu hỏi tra cứu:",
    value="Theo Thông tư 01/2014/TT-NHNN việc vận chuyển tài sản quý được quy định như thế nào?",
    height=110
)

method_option = st.sidebar.selectbox(
    "Phương pháp Retrieval:",
    options=["Hybrid + Rerank", "Hybrid (RRF)", "BM25 (Lexical)", "Dense (Embedding)"],
    index=0
)

top_k = st.sidebar.slider("Top-k Kết quả:", min_value=1, max_value=15, value=5)
candidate_k = st.sidebar.slider("Số lượng Ứng viên (Candidate-N):", min_value=5, max_value=30, value=20)

search_button = st.sidebar.button("🚀 Tìm kiếm an toàn", type="primary", use_container_width=True)

# Main Query Execution
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

    # Security Alert / Filtering Notice
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
st.caption("AI Coding Agent — Buổi 15 RAG Advanced Security & RBAC | Data-Level & Retrieval Pipeline Security")
