import os
import sys
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from scripts.query_demo import UnifiedRetrievalPipeline

st.set_page_config(
    page_title="RAG Hybrid Search & KG Mini — Buổi 14",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern visual design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
    }
    
    .main-header h1 {
        font-weight: 800;
        font-size: 2.2rem;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        font-size: 1.05rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }

    .result-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #3b82f6;
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
def load_pipeline():
    return UnifiedRetrievalPipeline()

with st.spinner("Đang khởi tạo Retrieval Pipeline..."):
    pipeline = load_pipeline()

# Header Banner
st.markdown("""
<div class="main-header">
    <h1>⚡ RAG Hybrid Search + Reranking & Knowledge Graph Mini</h1>
    <p>Hệ thống RAG nâng cao kết hợp Lexical Search (BM25), Dense Vector Embedding, Reciprocal Rank Fusion & Cross-Encoder Reranking</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.header("🔍 Cấu hình Retrieval")

query_input = st.sidebar.text_area(
    "Nhập câu hỏi tra cứu:",
    value="Theo Thông tư 01/2014/TT-NHNN việc vận chuyển tài sản quý được quy định như thế nào?",
    height=120
)

method_option = st.sidebar.selectbox(
    "Phương pháp Retrieval:",
    options=["Hybrid + Rerank", "Hybrid (RRF)", "BM25 (Lexical)", "Dense (Embedding)"],
    index=0
)

top_k = st.sidebar.slider("Top-k Kết quả:", min_value=1, max_value=15, value=5)
candidate_k = st.sidebar.slider("Số lượng Ứng viên (Candidate-N):", min_value=5, max_value=30, value=20)

search_button = st.sidebar.button("🚀 Tìm kiếm", type="primary", use_container_width=True)

# Main Query Execution
if search_button or query_input:
    method_map = {
        "BM25 (Lexical)": "bm25",
        "Dense (Embedding)": "dense",
        "Hybrid (RRF)": "hybrid",
        "Hybrid + Rerank": "hybrid_rerank"
    }
    
    selected_method_key = method_map[method_option]
    
    with st.spinner(f"Đang thực hiện retrieval bằng phương pháp {method_option}..."):
        results = pipeline.retrieve(query_input, method=selected_method_key, top_k=top_k)

    st.subheader(f"📌 Kết quả Tra cứu ({method_option})")
    st.write(f"Hiển thị **Top {len(results)}** kết quả cho câu hỏi: *\"{query_input}\"*")

    doc_ids = [r['document_id'] for r in results]
    chunk_ids = [r['chunk_id'] for r in results]

    col1, col2 = st.columns([2, 1])

    with col1:
        for r in results:
            st.markdown(f"""
            <div class="result-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="citation-badge">📚 {r['citation']}</span>
                    <div>
                        <span class="score-badge">Rank #{r['rank']} | Score: {r['score']}</span>
                    </div>
                </div>
                <div style="margin-top: 0.5rem; color: #334155; line-height: 1.6;">
                    {r['text']}
                </div>
                <div style="margin-top: 0.75rem; font-size: 0.8rem; color: #64748b;">
                    Chunk ID: <code>{r['chunk_id']}</code> | Document ID: <code>{r['document_id']}</code> | Method: <b>{r['retrieval_method']}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.subheader("📊 Ranking Metrics")
        if selected_method_key in ["hybrid_rerank", "hybrid"]:
            table_data = []
            for r in results:
                table_data.append({
                    "Rank": r['rank'],
                    "Chunk ID": r['chunk_id'],
                    "Hybrid Rank": r.get('hybrid_rank', r.get('bm25_rank', '-')),
                    "Score": r['score']
                })
            st.dataframe(pd.DataFrame(table_data), use_container_width=True)

        st.subheader("🕸️ Graph Hints (Neo4j)")
        hints = pipeline.get_graph_hints(doc_ids, chunk_ids)
        
        st.markdown(f"""
        <div class="graph-hint-box">
            <b>Neo4j Status:</b> <span style="color: {'#4ade80' if hints['status'] == 'CONNECTED' else '#f87171'}">{hints['status']}</span><br/><br/>
            <b>Retrieved Documents:</b><br/>
            <code>{hints['document_ids']}</code><br/><br/>
            <b>Retrieved Chunks:</b><br/>
            <code>{hints['chunk_ids']}</code><br/><br/>
            <b>Direct Graph Relations:</b><br/>
            {"<br/>".join(["• " + rel for rel in hints['relations']]) if hints['relations'] else "Không có quan hệ trực tiếp."}
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("AI Coding Agent — Buổi 14 RAG Advanced Lab | Clean Code, Verification & Neo4j Mini Graph")
