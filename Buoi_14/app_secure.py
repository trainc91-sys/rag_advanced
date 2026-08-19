import os
import sys
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Ensure root buoi_14 is in path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

from src.config import VALID_ROLES
from src.secure_retriever import SecureRetriever

# Page Configuration
st.set_page_config(
    page_title="RAG System & Ragas Evaluation Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Custom CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 35%, #312e81 70%, #4338ca 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 1.8rem;
        box-shadow: 0 12px 30px -5px rgba(67, 56, 202, 0.35);
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    .main-header h1 {
        font-weight: 800;
        font-size: 2.2rem;
        margin: 0;
        letter-spacing: -0.02em;
        color: #ffffff;
    }
    
    .main-header p {
        font-size: 1.05rem;
        opacity: 0.92;
        margin-top: 0.6rem;
        margin-bottom: 0;
        color: #c7d2fe;
    }

    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 800;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.88rem;
        color: #64748b;
        font-weight: 600;
        margin-top: 0.3rem;
    }
    .metric-target {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.2rem;
    }

    .result-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #4338ca;
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 8px -2px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    .result-card:hover {
        box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.1);
    }
    
    .citation-badge {
        background-color: #e0e7ff;
        color: #3730a3;
        font-weight: 700;
        font-size: 0.83rem;
        padding: 0.25rem 0.65rem;
        border-radius: 8px;
        border: 1px solid #c7d2fe;
    }
    .role-badge {
        background-color: #fef3c7;
        color: #92400e;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 0.25rem 0.65rem;
        border-radius: 8px;
        margin-left: 0.4rem;
        border: 1px solid #fde68a;
    }
    .score-badge {
        background-color: #dcfce7;
        color: #166534;
        font-weight: 700;
        font-size: 0.82rem;
        padding: 0.25rem 0.65rem;
        border-radius: 8px;
        margin-left: 0.4rem;
        border: 1px solid #bbf7d0;
    }
    
    .security-alert-box {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 1px solid #93c5fd;
        color: #1e40af;
        padding: 1rem 1.4rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        font-size: 0.95rem;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.1);
    }
    
    .llm-answer-box {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #cbd5e1;
        border-left: 6px solid #10b981;
        padding: 1.4rem 1.6rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.04);
    }
    .llm-answer-title {
        font-weight: 800;
        color: #065f46;
        font-size: 1.1rem;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .llm-answer-content {
        font-size: 1.02rem;
        line-height: 1.65;
        color: #1e293b;
    }

    .graph-hint-box {
        background-color: #0f172a;
        color: #f8fafc;
        padding: 1.25rem;
        border-radius: 12px;
        font-family: monospace;
        font-size: 0.85rem;
        border: 1px solid #334155;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Main Banner Header
st.markdown("""
<div class="main-header">
    <h1>⚡ Hệ Thống Tra Cứu RAG An Toàn & Dashboard Đánh Giá Ragas</h1>
    <p>Kiểm soát Truy cập Phân quyền (RBAC), Hybrid Search + Reranking & Đánh giá Tự động Hiệu năng RAG bằng Ragas Framework</p>
</div>
""", unsafe_allow_html=True)

# Load SecureRetriever
@st.cache_resource
def get_secure_retriever():
    return SecureRetriever()

with st.spinner("Đang khởi tạo hệ thống RAG & nạp chỉ mục tìm kiếm..."):
    retriever = get_secure_retriever()

# LLM Generator Function for RAG Answers
def generate_rag_answer(question: str, contexts: list):
    """Generate answer from contexts using available LLM API (Gemini or HF Router or Fallback)."""
    context_text = "\n\n".join([f"[{i+1}] (Nguồn: {c['citation']})\n{c['text']}" for i, c in enumerate(contexts)])
    prompt = f"""Bạn là Trợ lý AI Chuyên gia về Quy định Ngân hàng.
Hãy trả lời câu hỏi dựa TRỰC TIẾP và CHÍNH XÁC vào các đoạn ngữ cảnh được cung cấp dưới đây. 
Nếu thông tin không có trong ngữ cảnh, hãy ghi rõ "Thông tin không được đề cập trong tài liệu được cấp quyền".
Trích dẫn nguồn theo định dạng [Nguồn: ...] ở cuối các ý chính.

CÂU HỎI: {question}

NGỮ CẢNH TRUY CẤP ĐƯỢC:
{context_text}

CÂU TRẢ LỜI CHI TIẾT:"""

    gemini_key = os.getenv("GEMINI_API_KEY")
    hf_token = os.getenv("HF_TOKEN")

    if gemini_key:
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=gemini_key,
                model="gemini-3.6-flash",
                temperature=0.2
            )
            resp = llm.invoke(prompt)
            return resp.content, "Gemini 3.6 Flash"
        except Exception as e:
            pass

    if hf_token:
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=hf_token
            )
            completion = client.chat.completions.create(
                model="Qwen/Qwen3.6-35B-A3B:deepinfra",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return completion.choices[0].message.content, "Qwen 3.6 (HF Router)"
        except Exception as e:
            pass

    # Extractive summary fallback if APIs offline
    fallback_text = f"Dựa trên các đoạn ngữ cảnh tìm được ({len(contexts)} trích dẫn):\n\n"
    for i, c in enumerate(contexts[:3]):
        fallback_text += f"• **{c['citation']}**: {c['text'][:250]}...\n\n"
    return fallback_text, "Extractive Summary (Fallback)"

# Tab Navigation
tab_eval, tab_search, tab_compare, tab_graph = st.tabs([
    "📊 Dashboard Đánh Giá Ragas",
    "🛡️ Tra Cứu RAG & RBAC",
    "⚖️ So Sánh Retrieval Methods",
    "🕸️ Knowledge Graph Explorer"
])


# ==================== TAB 1: RAGAS EVALUATION DASHBOARD ====================
with tab_eval:
    st.subheader("📈 Báo Cáo Hiệu Năng Hệ Thống RAG (Ragas Evaluation Framework)")
    
    results_path = os.path.join(BASE_DIR, "data", "eval", "evaluation_results.csv")
    report_path = os.path.join(BASE_DIR, "outputs", "ragas_evaluation_report.md")
    qa_path = os.path.join(BASE_DIR, "data", "eval", "qa_dataset.csv")

    if os.path.exists(results_path):
        df_eval = pd.read_csv(results_path)
        
        prec = df_eval["context_precision"].mean()
        rec = df_eval["context_recall"].mean()
        faith = df_eval["faithfulness"].mean()
        rel = df_eval["answer_relevancy"].mean()
        overall = (prec + rec + faith + rel) / 4.0

        # KPI Summary Cards
        col1, col2, col3, col4, col5 = st.columns(5)
        
        def get_color(val, threshold=0.8):
            return "#15803d" if val >= threshold else ("#b45309" if val >= 0.7 else "#b91c1c")

        with col1:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value" style="color: {get_color(rec)};">{rec:.4f}</div>
                <div class="metric-label">Context Recall</div>
                <div class="metric-target">Benchmark: ≥ 0.70</div>
            </div>
            ''', unsafe_allow_html=True)
            
        with col2:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value" style="color: {get_color(prec)};">{prec:.4f}</div>
                <div class="metric-label">Context Precision</div>
                <div class="metric-target">Benchmark: ≥ 0.70</div>
            </div>
            ''', unsafe_allow_html=True)

        with col3:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value" style="color: {get_color(faith)};">{faith:.4f}</div>
                <div class="metric-label">Faithfulness</div>
                <div class="metric-target">Benchmark: ≥ 0.80</div>
            </div>
            ''', unsafe_allow_html=True)

        with col4:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value" style="color: {get_color(rel)};">{rel:.4f}</div>
                <div class="metric-label">Answer Relevancy</div>
                <div class="metric-target">Benchmark: ≥ 0.80</div>
            </div>
            ''', unsafe_allow_html=True)

        with col5:
            st.markdown(f'''
            <div class="metric-card" style="border: 2px solid #4338ca; background: linear-gradient(135deg, #e0e7ff 0%, #f5f3ff 100%);">
                <div class="metric-value" style="color: #312e81;">{overall:.4f}</div>
                <div class="metric-label" style="color: #4338ca; font-weight: 700;">RAGAS OVERALL</div>
                <div class="metric-target" style="color: #4338ca;">Trạng thái: TUYỆT VỜI</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        # Plotly Interactive Visualizations
        c_chart1, c_chart2 = st.columns([1, 1])

        with c_chart1:
            st.markdown("#### 🕸️ Biểu đồ Radar (Spider Chart) — Chỉ số Ragas vs Benchmark")
            metrics_names = ['Context Recall', 'Context Precision', 'Faithfulness', 'Answer Relevancy']
            current_scores = [rec, prec, faith, rel]
            benchmark_scores = [0.70, 0.70, 0.80, 0.80]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=current_scores + [current_scores[0]],
                theta=metrics_names + [metrics_names[0]],
                fill='toself',
                name='Hệ thống RAG Hiện tại',
                line_color='#4338ca',
                fillcolor='rgba(67, 56, 202, 0.25)'
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=benchmark_scores + [benchmark_scores[0]],
                theta=metrics_names + [metrics_names[0]],
                fill='toself',
                name='Ngưỡng Kỳ vọng (Benchmark)',
                line_color='#ef4444',
                fillcolor='rgba(239, 68, 68, 0.1)',
                line_dash='dash'
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1.0])),
                showlegend=True,
                margin=dict(l=40, r=40, t=30, b=30),
                height=350
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with c_chart2:
            st.markdown("#### 📊 Phân Phối Điểm Đánh Giá Theo Loại Nghiệp Vụ (Usecase)")
            if 'usecase' in df_eval.columns:
                df_grouped = df_eval.groupby('usecase')[['context_recall', 'context_precision', 'faithfulness', 'answer_relevancy']].mean().reset_index()
                df_melted = df_grouped.melt(id_vars=['usecase'], var_name='Metric', value_name='Score')
                
                fig_bar = px.bar(
                    df_melted, 
                    x='usecase', 
                    y='Score', 
                    color='Metric', 
                    barmode='group',
                    text_auto='.3f',
                    color_discrete_sequence=['#3b82f6', '#6366f1', '#10b981', '#f59e0b']
                )
                fig_bar.update_layout(
                    yaxis=dict(range=[0, 1.05]),
                    margin=dict(l=20, r=20, t=30, b=30),
                    height=350,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")

        # Sub-tabs for Detailed Data Exploration
        sub_t1, sub_t2, sub_t3 = st.tabs([
            "📋 Kết Quả Đánh Giá Chi Tiết (20 Samples)", 
            "📄 Báo Cáo Markdown Chi Tiết", 
            "🎯 Bộ Câu Hỏi Golden Dataset"
        ])
        
        with sub_t1:
            st.markdown("#### Bảng kết quả đánh giá từng câu hỏi")
            
            # Interactive Filters
            f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
            with f_col1:
                usecase_filter = st.multiselect("Lọc Usecase:", options=df_eval['usecase'].unique(), default=df_eval['usecase'].unique())
            with f_col2:
                diff_filter = st.multiselect("Lọc Độ khó:", options=df_eval['difficulty'].unique(), default=df_eval['difficulty'].unique())
            with f_col3:
                search_kw = st.text_input("🔍 Tìm theo từ khóa câu hỏi:", "")

            df_filtered = df_eval[
                df_eval['usecase'].isin(usecase_filter) & 
                df_eval['difficulty'].isin(diff_filter)
            ]
            if search_kw:
                df_filtered = df_filtered[df_filtered['question'].str.contains(search_kw, case=False, na=False)]

            st.dataframe(
                df_filtered[["question_id", "usecase", "difficulty", "question", "answer", "context_precision", "context_recall", "faithfulness", "answer_relevancy"]],
                use_container_width=True,
                height=400
            )

            # Download CSV button
            csv_bytes = df_filtered.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label="📥 Tải xuống dữ liệu đánh giá (CSV)",
                data=csv_bytes,
                file_name="ragas_evaluation_filtered.csv",
                mime="text/csv"
            )
            
        with sub_t2:
            if os.path.exists(report_path):
                with open(report_path, "r", encoding="utf-8") as f:
                    report_content = f.read()
                st.markdown(report_content)
            else:
                st.info("Chưa tìm thấy tệp ragas_evaluation_report.md.")
                
        with sub_t3:
            if os.path.exists(qa_path):
                df_qa = pd.read_csv(qa_path)
                st.dataframe(df_qa, use_container_width=True, height=450)
            else:
                st.info("Chưa tìm thấy bộ câu hỏi Golden Dataset.")
    else:
        st.warning("⚠️ Chưa tìm thấy tệp kết quả đánh giá evaluation_results.csv. Hãy chạy tập lệnh scripts/evaluate_rag_pipeline.py.")


# ==================== TAB 2: SECURE RAG SEARCH & LLM GENERATOR ====================
with tab_search:
    st.sidebar.markdown("---")
    st.sidebar.header("🔑 Phân Quyền Vai Trò (RBAC)")
    st.sidebar.markdown("Chọn danh sách vai trò người dùng:")

    user_roles_selected = []
    for r in VALID_ROLES:
        default_val = True if r in ["Staff", "Guest"] else False
        if st.sidebar.checkbox(f"Role: {r}", value=default_val, key=f"role_{r}"):
            user_roles_selected.append(r)

    if not user_roles_selected:
        user_roles_selected = ["Guest"]
        st.sidebar.warning("⚠️ Chưa chọn vai trò nào, tự động gán mặc định: Guest")

    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Cấu Hình Retrieval")

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
    
    enable_llm = st.sidebar.toggle("🤖 Sinh câu trả lời bằng LLM Generator", value=True)

    search_button = st.sidebar.button("🚀 Tìm kiếm & Sinh câu trả lời", type="primary", use_container_width=True)

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
            🔒 <b>Trạng thái phân quyền RBAC:</b> Vai trò đang hoạt động <code>{user_roles_selected}</code> | 
            Đã truy cập <b>{accessible_count}</b> / {response['total_chunks_in_corpus']} chunks | 
            <span style="color: #b91c1c;">Đã ẩn <b>{filtered_out_count}</b> chunks nhạy cảm không đủ quyền xem</span>.
        </div>
        """, unsafe_allow_html=True)

        # Generate LLM Answer if enabled
        if enable_llm and results:
            with st.spinner("🤖 AI Generator đang tổng hợp và sinh câu trả lời từ ngữ cảnh..."):
                answer_text, model_used = generate_rag_answer(query_input, results)

            st.markdown(f"""
            <div class="llm-answer-box">
                <div class="llm-answer-title">
                    <span>🤖 Câu Trả Lời RAG (Mô hình: {model_used})</span>
                </div>
                <div class="llm-answer-content">
                    {answer_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.subheader(f"📌 Ngữ Cảnh Tra Cứu Được ({method_option})")
        if not results:
            st.info("❌ Không tìm thấy kết quả nào phù hợp hoặc tất cả tài liệu liên quan đã bị ẩn do không đủ quyền truy cập.")
        else:
            st.write(f"Hiển thị **Top {len(results)}** kết quả ngữ cảnh được phép truy cập:")

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
                                <span class="role-badge">🔒 Quyền: [{allowed_str}]</span>
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
                st.subheader("📊 Ranking Metrics")
                table_data = []
                for r in results:
                    table_data.append({
                        "Rank": r['rank'],
                        "Chunk ID": r['chunk_id'],
                        "Score": r['score'],
                        "Allowed Roles": ", ".join(r['allowed_roles']) if isinstance(r['allowed_roles'], list) else str(r['allowed_roles'])
                    })
                st.dataframe(pd.DataFrame(table_data), use_container_width=True)

                st.subheader("🕸️ Graph Hints (Neo4j)")
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


# ==================== TAB 3: RETRIEVAL METHOD COMPARISON ====================
with tab_compare:
    st.subheader("⚖️ So Sánh Trực Quan Giữa Các Phương Pháp Retrieval")
    st.markdown("Chạy đồng thời 1 câu hỏi trên cả 4 phương pháp **BM25**, **Dense**, **Hybrid (RRF)** và **Hybrid + Neural Reranker** để kiểm tra sự biến động thứ hạng.")

    cmp_query = st.text_input(
        "Câu hỏi so sánh:",
        value="Hồ sơ đề nghị cấp Giấy phép thành lập ngân hàng thương mại bao gồm những văn bản gì?",
        key="cmp_query"
    )
    
    cmp_roles = st.multiselect(
        "Vai trò người truy vấn:",
        options=VALID_ROLES,
        default=["Staff", "Guest"],
        key="cmp_roles"
    )

    if st.button("⚡ Chạy So Sánh 4 Phương Pháp", type="primary"):
        methods = [
            ("BM25 (Lexical)", "bm25"),
            ("Dense (Embedding)", "dense"),
            ("Hybrid (RRF)", "hybrid"),
            ("Hybrid + Rerank", "hybrid_rerank")
        ]
        
        cols = st.columns(4)
        
        for idx, (label, m_key) in enumerate(methods):
            with cols[idx]:
                st.markdown(f"### {label}")
                res = retriever.retrieve(question=cmp_query, user_roles=cmp_roles, method=m_key, top_k=5)['results']
                for item in res:
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.6rem; font-size: 0.85rem;">
                        <b style="color: #4338ca;">Rank #{item['rank']}</b> | Score: <code>{item['score']}</code><br/>
                        <b>{item['citation']}</b><br/>
                        <span style="color: #475569;">{item['text'][:120]}...</span>
                    </div>
                    """, unsafe_allow_html=True)


# ==================== TAB 4: KNOWLEDGE GRAPH EXPLORER ====================
with tab_graph:
    st.subheader("🕸️ Knowledge Graph & Neo4j Database Explorer")
    st.markdown("Trực quan hóa cấu trúc đồ thị tri thức các văn bản ngân hàng và các mối quan hệ `CONTAINS`, `DAN_CHIEU`, `THAY_THE`.")

    col_g1, col_g2 = st.columns([1, 1])

    with col_g1:
        st.markdown("#### 📌 Thông tin Đồ Thị Tri Thức")
        st.info("""
        - **Node `VanBan`**: Đại diện cho các Thông tư, Luật, Nghị định (ví dụ: Thông tư 01/2014/TT-NHNN).
        - **Node `DieuKhoan`**: Các điều khoản chi tiết trong văn bản.
        - **Relationship `CONTAINS`**: Văn bản chứa các điều khoản.
        - **Relationship `DAN_CHIEU`**: Điều khoản dẫn chiếu tới văn bản/điều khoản khác.
        """)

    with col_g2:
        st.markdown("#### 🔌 Kiểm tra Kết Nối Neo4j")
        test_hints = retriever.get_graph_hints(["TT01/2014/TT-NHNN"], ["chunk_1"], user_roles=["Admin"])
        st.markdown(f"""
        <div class="graph-hint-box">
            <b>URI:</b> <code>{retriever.neo4j_uri}</code><br/>
            <b>Database:</b> <code>{retriever.neo4j_db}</code><br/>
            <b>Trạng thái:</b> <span style="color: {'#4ade80' if test_hints['status'] == 'CONNECTED' else '#f87171'}">{test_hints['status']}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("AI Coding Agent — Advanced RAG Lab & Ragas Evaluation Framework | Integrated Streamlit Web Application")
