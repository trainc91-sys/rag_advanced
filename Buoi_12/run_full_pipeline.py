"""
run_full_pipeline.py
---------------------
Script chạy toàn bộ quy trình hoàn chỉnh của Bài thực hành 3 (Buổi 12):
  1. Dự đoán mối quan hệ giữa các văn bản bằng Gemini LLM API (step1_predict.py)
  2. Đối sánh kết quả và tính các chỉ số Precision, Recall, F1-Score (step2_verify.py)
  3. Tái nạp toàn bộ dữ liệu 30 tài liệu và quan hệ vào đồ thị Neo4j (step3_reload_graph.py)
"""

import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

import step1_predict
import step2_verify
import step3_reload_graph


def main():
    start_total = time.time()
    print("==================================================================")
    print("🚀 BẮT ĐẦU CHẠY TOÀN BỘ PIPELINE BÀI THỰC HÀNH 3 (BUỔI 12)")
    print("==================================================================\n")
    
    # -------------------------------------------------------------------------
    # BƯỚC 1: Dự đoán Mối quan hệ bằng LLM
    # -------------------------------------------------------------------------
    print("👉 [1/3] Đang thực thi Bước 1: Phân tích Dữ liệu và Dự đoán Mối quan hệ bằng LLM...")
    t0 = time.time()
    try:
        step1_predict.main()
        print(f"⏱️ Bước 1 hoàn thành trong {time.time() - t0:.2f}s\n")
    except Exception as e:
        print(f"❌ Lỗi ở Bước 1: {e}")
        return

    # -------------------------------------------------------------------------
    # BƯỚC 2: Đối sánh và Xác minh Kết quả
    # -------------------------------------------------------------------------
    print("👉 [2/3] Đang thực thi Bước 2: Đối sánh và Tính chỉ số Đánh giá (Precision, Recall, F1)...")
    t0 = time.time()
    try:
        step2_verify.main()
        print(f"⏱️ Bước 2 hoàn thành trong {time.time() - t0:.2f}s\n")
    except Exception as e:
        print(f"❌ Lỗi ở Bước 2: {e}")
        return

    # -------------------------------------------------------------------------
    # BƯỚC 3: Tái nạp dữ liệu Đồ thị mở rộng vào Neo4j
    # -------------------------------------------------------------------------
    print("👉 [3/3] Đang thực thi Bước 3: Tái nạp Dữ liệu Đồ thị 30 Văn bản vào Neo4j...")
    t0 = time.time()
    try:
        step3_reload_graph.main()
        print(f"⏱️ Bước 3 hoàn thành trong {time.time() - t0:.2f}s\n")
    except Exception as e:
        print(f"❌ Lỗi ở Bước 3: {e}")
        return

    total_time = time.time() - start_total
    print("==================================================================")
    print(f"🎉 HOÀN THÀNH TOÀN BỘ CHƯƠNG TRÌNH TRONG {total_time:.2f} GIÂY!")
    print("==================================================================")


if __name__ == "__main__":
    main()
