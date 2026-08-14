"""
config.py
---------
Cấu hình tập trung cho hệ thống Multihop Graph RAG (Bài thực hành 2 - Buổi 11).

Tất cả các giá trị nhạy cảm (mật khẩu, API key) nên được đặt qua biến môi trường
hoặc file .env thay vì hard-code trực tiếp trong mã nguồn.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # nạp các biến từ file .env nếu có

# ---------------------------------------------------------------------------
# 1. Kết nối Neo4j (được thiết lập từ Bài thực hành 1)
# ---------------------------------------------------------------------------
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "kb-hops")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "abcd1234")

# ---------------------------------------------------------------------------
# 2. Mô hình embedding tiếng Việt (huấn luyện trên MS MARCO / tương đương)
#    Đây là mô hình bi-encoder tiếng Việt phổ biến, cùng họ với mô hình dùng ở
#    Bài thực hành 1. Nếu ở lab1 bạn đã dùng một checkpoint khác, hãy đổi tên
#    tại đây để đảm bảo vector nhúng tương thích với dữ liệu đã lưu trong Neo4j.
# ---------------------------------------------------------------------------
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "bkai-foundation-models/vietnamese-bi-encoder"
)

# Tên của vector index đã tạo trong Neo4j ở Bài thực hành 1
VECTOR_INDEX_NAME = os.getenv("VECTOR_INDEX_NAME", "chunk_embedding_index")

# Nhãn (label) của node chứa đoạn văn bản (chunk) và thuộc tính chứa vector/text
CHUNK_NODE_LABEL = os.getenv("CHUNK_NODE_LABEL", "Chunk")
CHUNK_TEXT_PROPERTY = os.getenv("CHUNK_TEXT_PROPERTY", "text")
CHUNK_EMBEDDING_PROPERTY = os.getenv("CHUNK_EMBEDDING_PROPERTY", "embedding")

# Nhãn của node văn bản luật (document) mà mỗi Chunk thuộc về, và tên quan hệ
# nối Chunk -> Document (chỉnh lại cho khớp với schema thực tế của bạn)
DOCUMENT_NODE_LABEL = os.getenv("DOCUMENT_NODE_LABEL", "Document")
DOCUMENT_TITLE_PROPERTY = os.getenv("DOCUMENT_TITLE_PROPERTY", "title")
BELONGS_TO_REL = os.getenv("BELONGS_TO_REL", "PART_OF")

# ---------------------------------------------------------------------------
# 3. Các mối quan hệ đa bước giữa các văn bản luật (dùng cho multi-hop)
# ---------------------------------------------------------------------------
MULTIHOP_RELATIONSHIPS = [
    "CAN_CU",     # văn bản A căn cứ vào văn bản B
    "THAY_THE",   # văn bản A thay thế văn bản B
    "HOP_NHAT",   # văn bản hợp nhất được hợp nhất từ các văn bản khác
    "SUA_DOI_BO_SUNG",  # văn bản A sửa đổi, bổ sung văn bản B
]

# ---------------------------------------------------------------------------
# 4. Gemini API
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-flash-latest")

# ---------------------------------------------------------------------------
# 5. Tham số truy hồi mặc định
# ---------------------------------------------------------------------------
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))
DEFAULT_HOPS = int(os.getenv("DEFAULT_HOPS", "1"))
MAX_CONTEXT_CHUNKS_PER_HOP = int(os.getenv("MAX_CONTEXT_CHUNKS_PER_HOP", "5"))
