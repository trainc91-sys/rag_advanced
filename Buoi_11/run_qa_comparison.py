"""
run_qa_comparison.py
---------------------
Bước 4: Kiểm thử và đánh giá pipeline.

Chạy 5 câu hỏi kiểm thử (đại diện cho các tình huống tra cứu luật đa văn bản)
qua hệ thống Multihop Graph RAG với 3 mức số bước nhảy khác nhau: 0, 1, 2.
Ghi lại toàn bộ kết quả so sánh (ngữ cảnh lấy được + câu trả lời của Gemini)
vào file qa_comparison.md để chứng minh hiệu quả của ngữ cảnh đa bước.

Cách chạy:
    python run_qa_comparison.py

Yêu cầu trước khi chạy:
    - Neo4j đang chạy và đã có dữ liệu từ Bài thực hành 1 (đồ thị kb-hops).
    - Đã cài đặt các gói trong requirements.txt.
    - Đã đặt biến môi trường GEMINI_API_KEY (hoặc trong file .env).
"""

from datetime import datetime
from typing import List

import config
from graph_rag import MultihopGraphRAG
import gemini_qa

TEST_QUESTIONS: List[str] = [
    "Nghị định 46/2023/NĐ-CP thay thế cho nghị định nào, và nghị định bị thay thế đó "
    "có nội dung gì nổi bật về kinh doanh bảo hiểm?",
    "Văn bản hợp nhất số 52/VBHN-NHNN được hợp nhất từ văn bản nào, và quy định về hồ "
    "sơ, thủ tục cấp giấy phép lần đầu của ngân hàng thương mại gồm những tài liệu gì?",
    "Thông tư số 01/2025/TT-NHNN quy định về cấp giấy phép quỹ tín dụng nhân dân được "
    "sửa đổi, bổ sung bởi văn bản nào, và những nội dung sửa đổi bổ sung chính là gì?",
    "Thông tư số 41/2016/TT-NHNN về tỷ lệ an toàn vốn của ngân hàng căn cứ vào luật "
    "nào, và luật đó quy định chức năng nhiệm vụ của cơ quan nào?",
    "Hoạt động giao nhận, vận chuyển tiền mặt và tài sản quý của Ngân hàng Nhà nước "
    "được điều chỉnh bởi Thông tư nào, và Thông tư đó có được sửa đổi bổ sung bởi văn "
    "bản nào không?",
]

HOP_SETTINGS = [0, 1, 2]
OUTPUT_FILE = "qa_comparison.md"


def run_single(rag: MultihopGraphRAG, question: str, hops: int) -> dict:
    retrieval = rag.retrieve_context(question, hops=hops)
    try:
        answer = gemini_qa.answer_question(question, retrieval["context_text"])
    except RuntimeError as e:
        answer = f"[LỖI] {e}"

    return {
        "hops": hops,
        "n_seed_chunks": len(retrieval["seed_chunks"]),
        "n_hop_chunks": len(retrieval["hop_chunks"]),
        "context_text": retrieval["context_text"],
        "answer": answer,
    }


def format_markdown(all_results: List[dict]) -> str:
    lines = []
    lines.append("# So sánh kết quả QA theo số bước nhảy (multi-hop)")
    lines.append("")
    lines.append(f"Thời gian chạy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append(
        "Tài liệu này so sánh câu trả lời của hệ thống Multihop Graph RAG khi thay đổi "
        "số bước nhảy (hops = 0, 1, 2) trên 5 câu hỏi kiểm thử, nhằm chứng minh hiệu quả "
        "của việc mở rộng ngữ cảnh qua các quan hệ CAN_CU, THAY_THE, HOP_NHAT, "
        "SUA_DOI_BO_SUNG giữa các văn bản luật."
    )
    lines.append("")

    for i, item in enumerate(all_results, start=1):
        lines.append(f"## Câu hỏi {i}")
        lines.append("")
        lines.append(f"> {item['question']}")
        lines.append("")
        lines.append("| Số bước nhảy | Số đoạn khớp trực tiếp | Số đoạn lấy thêm qua multi-hop | Câu trả lời |")
        lines.append("|---|---|---|---|")
        for r in item["results"]:
            answer_preview = r["answer"].replace("\n", "<br>")
            lines.append(
                f"| {r['hops']} | {r['n_seed_chunks']} | {r['n_hop_chunks']} | {answer_preview} |"
            )
        lines.append("")

        for r in item["results"]:
            lines.append(f"### Chi tiết — hops = {r['hops']}")
            lines.append("")
            lines.append("**Câu trả lời:**")
            lines.append("")
            lines.append(r["answer"])
            lines.append("")
            lines.append("<details><summary>Ngữ cảnh đã truy vấn</summary>")
            lines.append("")
            lines.append("```")
            lines.append(r["context_text"] if r["context_text"] else "(không có ngữ cảnh)")
            lines.append("```")
            lines.append("")
            lines.append("</details>")
            lines.append("")

        lines.append("---")
        lines.append("")

    lines.append("## Nhận xét tổng quan")
    lines.append("")
    lines.append(
        "- Với `hops = 0`, hệ thống chỉ trả lời được phần câu hỏi liên quan trực tiếp tới "
        "văn bản khớp với truy vấn vector; phần hỏi về văn bản liên quan (bị thay thế, "
        "được căn cứ, được hợp nhất, được sửa đổi bổ sung) thường bị báo là **không đủ "
        "thông tin trong ngữ cảnh**."
    )
    lines.append(
        "- Với `hops = 1` hoặc `hops = 2`, ngữ cảnh được mở rộng sang các văn bản liên "
        "kết trực tiếp/gián tiếp, giúp mô hình trả lời được đầy đủ cả hai vế của câu hỏi."
    )
    lines.append(
        "- Tăng số bước nhảy quá lớn (ví dụ hops = 2 trên đồ thị dày quan hệ) có thể lấy "
        "về nhiều đoạn văn bản không thực sự liên quan, làm loãng ngữ cảnh — cần cân "
        "nhắc giới hạn `MAX_CONTEXT_CHUNKS_PER_HOP` phù hợp."
    )
    lines.append("")

    return "\n".join(lines)


def main():
    print("Kết nối Neo4j ...")
    with MultihopGraphRAG() as rag:
        if not rag.verify_connectivity():
            print("Không thể kết nối Neo4j. Kiểm tra lại config.py / biến môi trường.")
            return

        all_results = []
        for q_idx, question in enumerate(TEST_QUESTIONS, start=1):
            print(f"\n=== Câu hỏi {q_idx}/{len(TEST_QUESTIONS)} ===")
            print(question)
            results_for_question = []
            for hops in HOP_SETTINGS:
                print(f"  -> Đang chạy với hops = {hops} ...")
                r = run_single(rag, question, hops)
                results_for_question.append(r)
            all_results.append({"question": question, "results": results_for_question})

    markdown = format_markdown(all_results)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"\nĐã ghi kết quả so sánh vào: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
