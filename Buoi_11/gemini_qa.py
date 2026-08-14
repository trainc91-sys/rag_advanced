"""
gemini_qa.py
------------
Bước 3: Tích hợp ngữ cảnh đã truy vấn (Graph RAG) vào Gemini API để sinh câu
trả lời tự động.

Thiết kế Prompt hệ thống:
  - Mô tả lược đồ đồ thị (schema): Document -[PART_OF]- Chunk,
    Document -[CAN_CU / THAY_THE / HOP_NHAT / SUA_DOI_BO_SUNG]- Document.
  - Mô tả cấu trúc văn bản luật tiếng Việt (số hiệu, loại văn bản, ngày ban hành,
    cơ quan ban hành, điều/khoản/điểm).
  - Yêu cầu trả lời bám sát ngữ cảnh, trích dẫn văn bản nguồn, và nói rõ
    "không có đủ thông tin trong ngữ cảnh" thay vì tự suy đoán khi không chắc chắn.
"""

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

import config

SYSTEM_PROMPT = """Bạn là một trợ lý AI chuyên tra cứu văn bản pháp luật Việt Nam
(nghị định, thông tư, luật, văn bản hợp nhất...) trong lĩnh vực ngân hàng - tài chính.

## Lược đồ dữ liệu đồ thị (schema) mà ngữ cảnh được trích xuất từ đó:
- Node `Document`: đại diện cho một văn bản luật (nghị định, thông tư, luật, văn bản
  hợp nhất...), có thuộc tính `title` (số hiệu + tên văn bản).
- Node `Chunk`: đại diện cho một đoạn văn bản (điều/khoản/điểm) trích từ một `Document`,
  liên kết với Document cha qua quan hệ `PART_OF`.
- Quan hệ giữa các `Document` với nhau (thể hiện mối liên hệ pháp lý):
  - `CAN_CU`: văn bản A được ban hành CĂN CỨ vào văn bản B (ví dụ: căn cứ Luật NHNN).
  - `THAY_THE`: văn bản A THAY THẾ (bãi bỏ, thay thế hiệu lực) văn bản B.
  - `HOP_NHAT`: văn bản hợp nhất A được HỢP NHẤT từ văn bản gốc và các văn bản sửa đổi.
  - `SUA_DOI_BO_SUNG`: văn bản A SỬA ĐỔI, BỔ SUNG một số điều của văn bản B.

## Cấu trúc văn bản luật tiếng Việt cần lưu ý khi đọc ngữ cảnh:
- Văn bản được định danh bằng số hiệu (ví dụ: 46/2023/NĐ-CP, 41/2016/TT-NHNN,
  52/VBHN-NHNN), trong đó hậu tố cho biết loại văn bản: NĐ-CP (Nghị định Chính phủ),
  TT-NHNN (Thông tư Ngân hàng Nhà nước), VBHN (Văn bản hợp nhất), QH (Luật/Quốc hội)...
- Nội dung được chia theo Chương, Điều, Khoản, Điểm.
- Ngữ cảnh cung cấp cho bạn gồm các đoạn (chunk) được gắn nhãn theo văn bản nguồn và
  cho biết đoạn đó là "khớp trực tiếp" với câu hỏi hay "liên quan qua N bước" (đến từ
  một văn bản có quan hệ CAN_CU/THAY_THE/HOP_NHAT/SUA_DOI_BO_SUNG với văn bản khớp gốc).

## Nguyên tắc trả lời — BẮT BUỘC tuân thủ:
1. CHỈ trả lời dựa trên nội dung có trong phần "NGỮ CẢNH" được cung cấp bên dưới.
   Không tự suy đoán, không dùng kiến thức pháp luật ngoài ngữ cảnh.
2. Nếu câu hỏi có nhiều phần (ví dụ vừa hỏi "văn bản nào" vừa hỏi "nội dung gì"), hãy
   trả lời đầy đủ TỪNG PHẦN, dựa trên các đoạn ngữ cảnh tương ứng (kể cả các đoạn đến
   từ multi-hop).
3. Khi trích dẫn thông tin, hãy nêu rõ đoạn đó thuộc văn bản nào (dùng đúng số hiệu/tên
   văn bản như trong ngữ cảnh).
4. Nếu ngữ cảnh KHÔNG chứa đủ thông tin để trả lời một phần nào đó của câu hỏi, hãy nói
   rõ: "Ngữ cảnh được cung cấp không có đủ thông tin để trả lời phần này" thay vì bịa ra
   câu trả lời.
5. Trả lời ngắn gọn, rõ ràng, đúng trọng tâm, bằng tiếng Việt.
"""

_configured = False


def _ensure_configured():
    global _configured
    if not _configured:
        if not config.GEMINI_API_KEY:
            raise RuntimeError(
                "Thiếu GEMINI_API_KEY. Hãy đặt biến môi trường GEMINI_API_KEY "
                "hoặc thêm vào file .env trước khi gọi Gemini API."
            )
        genai.configure(api_key=config.GEMINI_API_KEY)
        _configured = True


def build_user_prompt(question: str, context_text: str) -> str:
    if not context_text.strip():
        context_text = "(Không tìm thấy đoạn văn bản liên quan nào trong đồ thị.)"
    return f"""NGỮ CẢNH:
{context_text}

CÂU HỎI:
{question}

Hãy trả lời câu hỏi trên dựa đúng vào NGỮ CẢNH ở trên, theo các nguyên tắc đã nêu."""


def answer_question(question: str, context_text: str, model_name: str = config.GEMINI_MODEL_NAME) -> str:
    """Gọi Gemini API để sinh câu trả lời dựa trên ngữ cảnh đã truy vấn từ Graph RAG."""
    _ensure_configured()
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_PROMPT,
    )
    user_prompt = build_user_prompt(question, context_text)

    try:
        response = model.generate_content(user_prompt)
        return (response.text or "").strip()
    except google_exceptions.ResourceExhausted as exc:
        return (
            "[Không thể gọi Gemini do vượt hạn ngạch/quota] "
            f"{exc}. Hãy thử lại sau hoặc đổi sang model khác."
        )
    except Exception as exc:  # pragma: no cover - defensive fallback
        return f"[Không thể gọi Gemini] {exc}"
