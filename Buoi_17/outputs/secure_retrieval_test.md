# Secure Retrieval Adapter Test Report — Buổi 17

**Test Query**: `Hạn mức vận chuyển tiền mặt bằng xe bọc thép Agribank là bao nhiêu?`
**Total Corpus Chunks**: 811

## 1. Multi-Role Retrieval Isolation Test

### Role: `Admin`
- **Access Decision**: `ALLOWED`
- **Accessible Scope**: 811 chunks
- **Filtered Out Pre-retrieval**: 0 chunks
- **Top-k Retrieved**: 3 chunks
- **Retrieved Citations**:
  - Rank 1: `Quy định nội bộ số 180/QĐ-NHNO-BH về Mua bảo hiểm rủi ro nghiệp vụ và tài sản Agribank | 180/QĐ-NHNO-BH | Điều 5. Mua bảo hiểm BBB cho tiền mặt kho vận | doc_agr_bh06_01` (Allowed: `['Admin', 'Risk_Manager', 'Staff']`)
  - Rank 2: `Quy định nội bộ số 100/QĐ-NHNO-AT về Giao nhận, bảo quản, vận chuyển tiền mặt và tài sản quý Agribank | 100/QĐ-NHNO-AT | Điều 12. Xe bọc thép và phương án bảo vệ | doc_agr_at01_02` (Allowed: `['Admin', 'Risk_Manager', 'Staff']`)
  - Rank 3: `Quy định nội bộ số 100/QĐ-NHNO-AT về Giao nhận, bảo quản, vận chuyển tiền mặt và tài sản quý Agribank | 100/QĐ-NHNO-AT | Điều 1. Phạm vi và đối tượng tuân thủ | doc_agr_at01_01` (Allowed: `['Admin', 'Risk_Manager', 'Staff']`)

### Role: `Staff`
- **Access Decision**: `ALLOWED`
- **Accessible Scope**: 418 chunks
- **Filtered Out Pre-retrieval**: 393 chunks
- **Top-k Retrieved**: 3 chunks
- **Retrieved Citations**:
  - Rank 1: `Quy định nội bộ số 180/QĐ-NHNO-BH về Mua bảo hiểm rủi ro nghiệp vụ và tài sản Agribank | 180/QĐ-NHNO-BH | Điều 5. Mua bảo hiểm BBB cho tiền mặt kho vận | doc_agr_bh06_01` (Allowed: `['Admin', 'Risk_Manager', 'Staff']`)
  - Rank 2: `Quy định nội bộ số 100/QĐ-NHNO-AT về Giao nhận, bảo quản, vận chuyển tiền mặt và tài sản quý Agribank | 100/QĐ-NHNO-AT | Điều 12. Xe bọc thép và phương án bảo vệ | doc_agr_at01_02` (Allowed: `['Admin', 'Risk_Manager', 'Staff']`)
  - Rank 3: `Quy định nội bộ số 100/QĐ-NHNO-AT về Giao nhận, bảo quản, vận chuyển tiền mặt và tài sản quý Agribank | 100/QĐ-NHNO-AT | Điều 1. Phạm vi và đối tượng tuân thủ | doc_agr_at01_01` (Allowed: `['Admin', 'Risk_Manager', 'Staff']`)

### Role: `Guest`
- **Access Decision**: `ALLOWED`
- **Accessible Scope**: 162 chunks
- **Filtered Out Pre-retrieval**: 649 chunks
- **Top-k Retrieved**: 3 chunks
- **Retrieved Citations**:
  - Rank 1: `Ngân hàng Nhà nước Việt Nam | 46/2010/QH12 | Điều 16. Đơn vị tiền | doc_25692_điều_16__đơn_vị_tiền_16` (Allowed: `['Admin', 'HR', 'Risk_Manager', 'Staff', 'Guest']`)
  - Rank 2: `Luật Hợp tác xã số 17/2023/QH15 | 17/2023/QH15 | Điều 76. Chuyển giao tài sản góp vốn | doc_166269_điều_76__chuyển_giao_tài_sản_góp_vốn_76` (Allowed: `['Admin', 'HR', 'Risk_Manager', 'Staff', 'Guest']`)
  - Rank 3: `Luật Hợp tác xã số 17/2023/QH15 | 17/2023/QH15 | Điều 73. Tài sản góp vốn | doc_166269_điều_73__tài_sản_góp_vốn_73` (Allowed: `['Admin', 'HR', 'Risk_Manager', 'Staff', 'Guest']`)

### Role: `Unknown_User`
- **Access Decision**: `DENIED`
- **Accessible Scope**: 0 chunks
- **Filtered Out Pre-retrieval**: 811 chunks
- **Top-k Retrieved**: 0 chunks
- **Retrieved Citations**: None (Filtered or Access Denied)

## 2. Verification Checklist
- **Authorized Role Access**: PASS
- **Unauthorized Context Leakage**: PASS (Zero unauthorized chunks present in returned context)
- **Citation & ID Preservation**: PASS (`chunk_id`, `document_id`, `citation` preserved)

---
SECURE RETRIEVAL REUSE: PASS
NO UNAUTHORIZED CONTEXT: PASS
CITATION PRESERVED: PASS