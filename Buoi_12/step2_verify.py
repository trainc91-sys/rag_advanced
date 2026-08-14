"""
step2_verify.py
---------------
Bước 2: Đối sánh và Xác minh Kết quả do LLM dự đoán với bộ nhãn kiểm thử chuẩn.
Tính toán các chỉ số Precision, Recall, F1-Score.
"""

import csv
from pathlib import Path
from typing import List, Dict, Set, Tuple

BASE_DIR = Path(__file__).resolve().parent
PREDICTED_PATH = BASE_DIR / "predicted_relationships.csv"
GROUND_TRUTH_PATH = BASE_DIR / "medium" / "relationships.csv"
EVALUATION_REPORT_PATH = BASE_DIR / "evaluation_report.md"


def load_relationships(filepath: Path) -> Set[Tuple[str, str, str]]:
    rels = set()
    if not filepath.exists():
        return rels
    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc_id = (row.get("doc_id") or "").strip()
            other_doc_id = (row.get("other_doc_id") or "").strip()
            rel_type = (row.get("relationship_type") or "").strip()
            if doc_id and other_doc_id and rel_type:
                rels.add((doc_id, other_doc_id, rel_type))
    return rels


def calculate_metrics(tp: int, fp: int, fn: int) -> Dict[str, float]:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }


def main():
    print("--- BƯỚC 2: ĐỐI SÁNH VÀ XÁC MINH KẾT QUẢ ---")
    
    pred_rels = load_relationships(PREDICTED_PATH)
    gt_rels = load_relationships(GROUND_TRUTH_PATH)
    
    print(f"Tổng số quan hệ dự đoán: {len(pred_rels)}")
    print(f"Tổng số quan hệ chuẩn (Ground Truth): {len(gt_rels)}")
    
    tp_set = pred_rels.intersection(gt_rels)
    fp_set = pred_rels - gt_rels
    fn_set = gt_rels - pred_rels
    
    tp = len(tp_set)
    fp = len(fp_set)
    fn = len(fn_set)
    
    metrics = calculate_metrics(tp, fp, fn)
    
    print("\n=== KẾT QUẢ ĐÁNH GIÁ (EVALUATION METRICS) ===")
    print(f"True Positives (TP)  : {tp}")
    print(f"False Positives (FP) : {fp}")
    print(f"False Negatives (FN) : {fn}")
    print(f"Precision            : {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
    print(f"Recall               : {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
    print(f"F1-Score             : {metrics['f1_score']:.4f} ({metrics['f1_score']*100:.2f}%)")
    
    # Save markdown report
    report_lines = [
        "# Báo cáo Đánh giá Kết quả Dự đoán Mối quan hệ Pháp lý bằng LLM",
        "",
        f"**Số lượng quan hệ dự đoán**: {len(pred_rels)}",
        f"**Số lượng quan hệ chuẩn**: {len(gt_rels)}",
        "",
        "## Chỉ số Đánh giá (Evaluation Metrics)",
        "",
        "| Chỉ số | Giá trị | Phần trăm |",
        "|---|---|---|",
        f"| **Precision** | {metrics['precision']:.4f} | {metrics['precision']*100:.2f}% |",
        f"| **Recall** | {metrics['recall']:.4f} | {metrics['recall']*100:.2f}% |",
        f"| **F1-Score** | {metrics['f1_score']:.4f} | {metrics['f1_score']*100:.2f}% |",
        "",
        "## Chi tiết Kết quả Đối sánh",
        "",
        "### ✅ True Positives (Khớp chính xác)",
    ]
    for rel in tp_set:
        report_lines.append(f"- `doc_id`: {rel[0]} -> `other_doc_id`: {rel[1]} [{rel[2]}]")
        
    report_lines.append("\n### ❌ False Positives (Dự đoán dư thừa / sai)")
    if fp_set:
        for rel in fp_set:
            report_lines.append(f"- `doc_id`: {rel[0]} -> `other_doc_id`: {rel[1]} [{rel[2]}]")
    else:
        report_lines.append("- (Không có)")
        
    report_lines.append("\n### ⚠️ False Negatives (Bỏ sót)")
    if fn_set:
        for rel in fn_set:
            report_lines.append(f"- `doc_id`: {rel[0]} -> `other_doc_id`: {rel[1]} [{rel[2]}]")
    else:
        report_lines.append("- (Không có)")
        
    EVALUATION_REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"\nĐã xuất báo cáo chi tiết ra tệp: {EVALUATION_REPORT_PATH.name}")


if __name__ == "__main__":
    main()
