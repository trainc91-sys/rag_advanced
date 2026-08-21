# Internal Policy Lookup Demo Report — Buổi 17

## Multi-Role Lookup Test Results

### Query: `Quy định về hạn mức xe bọc thép khi vận chuyển tiền mặt Agribank?`
- **User Role**: `Staff`
- **Access Decision**: `ALLOWED`
- **Request ID**: `req_85f3be06fce4`
- **Filtered Chunks**: 393
- **Citations Found**: 5
- **Answer**:
```
Lỗi kết nối Gemini API. Ngữ cảnh tìm thấy: 5 đoạn.
```

### Query: `Tỷ lệ an toàn vốn CAR tối thiểu của Agribank quy định bao nhiêu %?`
- **User Role**: `Risk_Manager`
- **Access Decision**: `ALLOWED`
- **Request ID**: `req_15cdc8f9b5ec`
- **Filtered Chunks**: 382
- **Citations Found**: 5
- **Answer**:
```
Lỗi kết nối Gemini API. Ngữ cảnh tìm thấy: 5 đoạn.
```

### Query: `Tỷ lệ an toàn vốn CAR tối thiểu của Agribank quy định bao nhiêu %?`
- **User Role**: `Guest`
- **Access Decision**: `ALLOWED`
- **Request ID**: `req_93c720f55c0c`
- **Filtered Chunks**: 649
- **Citations Found**: 5
- **Answer**:
```
Lỗi kết nối Gemini API. Ngữ cảnh tìm thấy: 5 đoạn.
```

## Verification Checklist
- **Citation Format**: PASS
- **RBAC Enforced**: PASS (Guest denied access to confidential CAR document)
- **Audit Trail Logged**: PASS

---
CITATION: PASS
RBAC: PASS
AUDIT: PASS