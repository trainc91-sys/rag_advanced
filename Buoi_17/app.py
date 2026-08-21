import os
import sys
import json
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from internal_lookup import InternalLookupSystem
from compliance_gap import ComplianceGapChecker

st.set_page_config(
    page_title="Agribank Secure RAG & AI Compliance Gap Checker — Buổi 17",
    page_icon="🏦",
    layout="wide"
)

# Custom CSS for Banking / Enterprise Aesthetic
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #0b4f2c;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 20px;
    }
    .warning-banner {
        background-color: #fff3cd;
        color: #856404;
        padding: 12px 18px;
        border-radius: 8px;
        border-left: 5px solid #ffeba8;
        font-weight: 500;
        margin-bottom: 20px;
    }
    .badge-allowed {
        background-color: #d4edda;
        color: #155724;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-denied {
        background-color: #f8d7da;
        color: #721c24;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .gap-dap-ung { background-color: #28a745; color: white; padding: 4px 8px; border-radius: 4px; }
    .gap-thieu { background-color: #dc3545; color: white; padding: 4px 8px; border-radius: 4px; }
    .gap-chenh-lech { background-color: #ffc107; color: black; padding: 4px 8px; border-radius: 4px; }
    .gap-chua-du { background-color: #6c757d; color: white; padding: 4px 8px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# Initialize Session State systems
@st.cache_resource
def get_lookup_system():
    return InternalLookupSystem()

@st.cache_resource
def get_gap_system():
    return ComplianceGapChecker()

lookup_sys = get_lookup_system()
gap_sys = get_gap_system()

# Sidebar Setup
st.sidebar.title("🔐 Phân quyền & Cấu hình")
user_id_demo = st.sidebar.text_input("User ID Demo", value="usr_demo_01")
user_role = st.sidebar.selectbox(
    "Vai trò người dùng (User Role)",
    options=["Admin", "Risk_Manager", "HR", "Staff", "Guest"],
    index=1
)

st.sidebar.markdown("---")
st.sidebar.subheader("🌐 Neo4j Graph Status")
st.sidebar.success("Neo4j Connected: bolt://localhost:7687")

st.sidebar.markdown("---")
st.sidebar.info("Module 3 RAG Security & Compliance — Buổi 17")

# Page Header
st.markdown('<div class="main-header">🏦 AGRIBANK SECURE RAG & AI COMPLIANCE GAP CHECKER</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Hệ thống tra cứu quy định nội bộ có phân quyền RBAC, Audit Trail và AI Compliance Gap Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="warning-banner">⚠️ <b>Lưu ý quan trọng:</b> Demo đào tạo — kết quả AI cần kiểm toán viên xác minh trước khi sử dụng chính thức. Mọi Gap Analysis đều mang trạng thái <code>NEEDS_HUMAN_REVIEW</code>.</div>', unsafe_allow_html=True)

# Main Navigation Tabs
tab1, tab2, tab3 = st.tabs(["🔍 TRA CỨU QUY ĐỊNH NỘI BỘ", "⚖️ COMPLIANCE GAP CHECKER", "📜 AUDIT TRAIL LOGS"])

# TAB 1: Internal Policy Search
with tab1:
    st.subheader("Tra cứu Quy định Nội bộ Agribank (RBAC Pre-Filtered RAG)")
    
    col_q, col_k = st.columns([4, 1])
    with col_q:
        question = st.text_input(
            "Nhập câu hỏi tra cứu quy định:",
            value="Hạn mức xe bọc thép khi vận chuyển tiền mặt Agribank là bao nhiêu?"
        )
    with col_k:
        top_k = st.slider("Top-k Retrieval", min_value=1, max_value=10, value=3)

    if st.button("🚀 Tra cứu Quy định", type="primary"):
        with st.spinner("Đang truy xuất dữ liệu theo phân quyền RBAC..."):
            res = lookup_sys.query_internal_policy(
                question=question,
                user_role=user_role,
                user_id_demo=user_id_demo,
                top_k=top_k
            )

        col_dec, col_req, col_filt = st.columns(3)
        with col_dec:
            if res["access_decision"] == "ALLOWED":
                st.markdown('Trạng thái truy cập: <span class="badge-allowed">ALLOWED</span>', unsafe_allow_html=True)
            else:
                st.markdown('Trạng thái truy cập: <span class="badge-denied">DENIED</span>', unsafe_allow_html=True)
        with col_req:
            st.metric("Request ID", res["request_id"])
        with col_filt:
            st.metric("RBAC Filtered Chunks", f"{res['filtered_count']} chunks")

        st.markdown("### 💬 Câu trả lời từ AI Generator")
        st.info(res["answer"])

        if res["citations"]:
            st.markdown("### 📚 Danh sách Trích dẫn (Citations)")
            for cit in res["citations"]:
                st.markdown(f"- `{cit}`")

        if res["retrieved_chunks"]:
            with st.expander("🔬 Xem chi tiết Ngữ cảnh Chunk được phép xem"):
                for chunk in res["retrieved_chunks"]:
                    st.markdown(f"**Rank {chunk['rank']}** | Document: `{chunk['document_id']}` | Chunk ID: `{chunk['chunk_id']}`")
                    st.caption(f"Quyền xem chunk: `{chunk['allowed_roles']}` | Citation: `{chunk['citation']}`")
                    st.text_area("Nội dung Chunk", chunk["text"], height=100, key=f"txt_{chunk['chunk_id']}")

# TAB 2: Compliance Gap Checker
with tab2:
    st.subheader("AI Compliance Gap Checker (Đối chiếu Quy định NHNN vs Quy định Nội bộ)")

    sample_reqs = [
        "Ngân hàng Nhà nước quy định công tác vận chuyển tiền mặt có giá trị lớn phải đảm bảo an toàn tuyệt đối và có phương án bảo vệ chuyên trách bằng xe bọc thép chuyên dùng.",
        "Tỷ lệ an toàn vốn tối thiểu (CAR) đối với các tổ chức tín dụng phải đạt tối thiểu 8% theo quy định NHNN.",
        "Tất cả hệ thống CNTT và ứng dụng AI xử lý dữ liệu khách hàng phải lưu trữ nhật ký truy cập (Audit Trail) tối thiểu 24 tháng."
    ]
    
    selected_sample = st.selectbox("Chọn mẫu yêu cầu pháp lý NHNN:", sample_reqs)
    req_input = st.text_area("Hoặc nhập yêu cầu quy định NHNN cần đối chiếu:", value=selected_sample, height=100)

    if st.button("⚖️ Chạy AI Compliance Gap Analysis", type="primary"):
        with st.spinner("Đang tìm kiếm evidence nội bộ và phân tích chênh lệch tuân thủ..."):
            gap_res = gap_sys.evaluate_gap(
                external_req_text=req_input,
                external_citation="[Thông tư NHNN đối chiếu]",
                user_role=user_role
            )

        st.markdown("### 📊 Kết quả Phân tích Compliance Gap")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Gap ID", gap_res["gap_id"])
        with c2:
            cls = gap_res["classification"]
            st.metric("Phân loại Compliance", cls)
        with c3:
            st.metric("Độ tin cậy (Confidence)", f"{gap_res['confidence']*100:.0f}%")
        with c4:
            st.metric("Human Review", gap_res["review_status"])

        st.markdown("---")
        col_ext, col_int = st.columns(2)
        with col_ext:
            st.markdown("#### 🏛️ Yêu cầu Pháp lý NHNN (External Requirement)")
            st.warning(f"**Yêu cầu:** {gap_res['external_requirement']}\n\n**Trích dẫn:** `{gap_res['external_citation']}`")

        with col_int:
            st.markdown("#### 🏢 Quy định Nội bộ Agribank (Internal Evidence)")
            st.success(f"**Bằng chứng:** {gap_res['internal_evidence']}\n\n**Trích dẫn:** `{gap_res['internal_citation']}`")

        st.markdown("#### 💡 Lý do Phân tích của AI (Reasoning)")
        st.info(gap_res["reason"])

# TAB 3: Audit Log Viewer
with tab3:
    st.subheader("📜 Nhật ký Hệ thống (Audit Trail Viewer)")
    st.caption("Truy vết toàn bộ câu hỏi, vai trò, phương thức truy xuất và quyết định phân quyền (JSONL Format)")

    log_file = os.path.join(BASE_DIR, "outputs", "audit_log.jsonl")
    if os.path.exists(log_file):
        lines = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        lines.append(json.loads(line.strip()))
                    except Exception:
                        pass
        
        if lines:
            df_log = pd.DataFrame(lines)
            st.dataframe(df_log, use_container_width=True)

            st.download_button(
                "📥 Tải xuống Audit Log (JSONL)",
                data="\n".join([json.dumps(l, ensure_ascii=False) for l in lines]),
                file_name="audit_log.jsonl",
                mime="application/json"
            )
        else:
            st.info("Chưa có sự kiện audit nào được ghi nhận.")
    else:
        st.info("Tệp audit_log.jsonl chưa khởi tạo.")
