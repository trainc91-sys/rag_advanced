# RETRIEVAL EXAMPLES & COMPARISON (BUỔI 14)

## Query Type: `EXACT_KEYWORD`
**Query:** `Quy định 73/2016/NĐ-CP Điều 115 về hiệu lực thi hành`

### 1. BM25 Baseline
| Rank | Chunk ID | Score | Citation | Excerpt |
|---|---|---|---|---|
| 1 | `166269_c115` | 28.9016 | Luật Hợp tác xã số 17/2023/QH15 | 17/2023/QH15 | Điều 114. Điều khoản thi hành | 166269_c115 | Điều 114. Điều khoản thi hành 1. Luật này có hiệu lực thi hành từ ngày 01 tháng 7 năm 2024, trừ quy định tại khoản 2 Điề... |
| 2 | `163441_c123` | 28.7155 | Nghị định số 46/2023/NĐ-CP Quy định chi tiết thi hành một số điều của Luật Kinh doanh bảo hiểm | 46/2023/NĐ-CP | Điều 122. Hiệu lực thi hành | 163441_c123 | Điều 122. Hiệu lực thi hành 1. Nghị định này có hiệu lực thi hành kể từ ngày ký, trừ trường hợp quy định tại khoản 2 Điề... |
| 3 | `112025_c116` | 24.5663 | Nghị định số 73/2016/NĐ-CP Quy định chi tiết thi hành Luật kinh doanh bảo hiểm và Luật sửa đổi, bổ sung một số điều của Luật kinh doanh bảo hiểm | 73/2016/NĐ-CP | Điều 115. Hiệu lực thi hành | 112025_c116 | Điều 115. Hiệu lực thi hành 1. Nghị định này có hiệu lực thi hành từ ngày 01 tháng 7 năm 2016. 2. Nghị định số 45/2007/N... |
| 4 | `166269_c116` | 21.0673 | Luật Hợp tác xã số 17/2023/QH15 | 17/2023/QH15 | Điều 115. Quy định chuyển tiếp | 166269_c116 | Điều 115. Quy định chuyển tiếp 1. Hợp tác xã, liên hiệp hợp tác xã được thành lập trước ngày Luật này có hiệu lực thi hà... |
| 5 | `166170_c211` | 20.9793 | Luật Các tổ chức tín dụng số 32/2024/QH15 | 32/2024/QH15 | Điều 210. Quy định chuyển tiếp | 166170_c211 | Điều 210. Quy định chuyển tiếp 1. Tổ chức tín dụng, chi nhánh ngân hàng nước ngoài, văn phòng đại diện nước ngoài đã thà... |

### 2. Dense Baseline
| Rank | Chunk ID | Score | Citation | Excerpt |
|---|---|---|---|---|
| 1 | `112025_c116` | 0.7731 | Nghị định số 73/2016/NĐ-CP Quy định chi tiết thi hành Luật kinh doanh bảo hiểm và Luật sửa đổi, bổ sung một số điều của Luật kinh doanh bảo hiểm | 73/2016/NĐ-CP | Điều 115. Hiệu lực thi hành | 112025_c116 | Điều 115. Hiệu lực thi hành 1. Nghị định này có hiệu lực thi hành từ ngày 01 tháng 7 năm 2016. 2. Nghị định số 45/2007/N... |
| 2 | `143217_c001` | 0.7635 | Thông tư số 66/2020/TT-BTC Ban hành Quy chế mẫu về kiểm toán nội bộ áp dụng cho doanh nghiệp | 66/2020/TT-BTC | 143217_c001 | BỘ TÀI CHÍNH Số: 66/2020/TT-BTC BỘ TÀI CHÍNH Số: 66/2020/TT-BTC CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM Độc lập - Tự do - Hạn... |
| 3 | `44209_c073` | 0.7307 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 72. Hiệu lực thi hành | 44209_c073 | Điều 72. Hiệu lực thi hành 1. Thông tư này có hiệu lực thi hành kể từ ngày 20/02/2014. 2. Kể từ ngày Thông tư này có hiệ... |
| 4 | `166170_c210` | 0.727 | Luật Các tổ chức tín dụng số 32/2024/QH15 | 32/2024/QH15 | Điều 209. Hiệu lực thi hành | 166170_c210 | Điều 209. Hiệu lực thi hành 1. Luật này có hiệu lực thi hành từ ngày 01 tháng 7 năm 2024, trừ quy định tại khoản 2 Điều ... |
| 5 | `f69936f0-6937-11f1-a48d-29bc6b0fd706_c059` | 0.7265 | Văn bản hợp nhất Nghị định số 156/2020/NĐ-CP Quy định xử phạt vi phạm hành chính trong lĩnh vực chứng khoán và thị trường chứng khoán | 17/VBHN-BTC | Điều 52. Hiệu lực thi hành | f69936f0-6937-11f1-a48d-29bc6b0fd706_c059 | Điều 52. Hiệu lực thi hành 1. Nghị định này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2021. 2. Nghị định số 108/2013/... |

---

## Query Type: `SEMANTIC`
**Query:** `Ai có thẩm quyền phê duyệt hạn mức tín dụng và cấp tiền mặt?`

### 1. BM25 Baseline
| Rank | Chunk ID | Score | Citation | Excerpt |
|---|---|---|---|---|
| 1 | `186888_c018` | 20.3704 | Thông tư số 62/2025/TT-NHNN Quy định về hệ thống kiểm soát nội bộ của tổ chức tín dụng là hợp tác xã, tổ chức tài chính vi mô | 62/2025/TT-NHNN | Điều 17. Hoạt động kiểm soát đối với hoạt động cấp tín dụng | 186888_c018 | Điều 17. Hoạt động kiểm soát đối với hoạt động cấp tín dụng 1. Hoạt động kiểm soát đối với hoạt động cấp tín dụng của tổ... |
| 2 | `38128_c007` | 20.1542 | Thông tư số 37/2014/TT-NHNN Quy định việc thiết kế mẫu tiền, chế bản và quản lý in, đúc tiền Việt Nam | 37/2014/TT-NHNN | Điều 6. Trình duyệt mẫu thiết kế đồng tiền | 38128_c007 | Điều 6. Trình duyệt mẫu thiết kế đồng tiền 1. Sau khi hoàn thành việc thiết kế mẫu tiền theo Đề án đã được phê duyệt, Cụ... |
| 3 | `166170_c075` | 18.6333 | Luật Các tổ chức tín dụng số 32/2024/QH15 | 32/2024/QH15 | Điều 74. Nhiệm vụ, quyền hạn của Hội đồng thành viên của tổ chức tín dụng là công ty trách nhiệm hữu hạn một thành viên | 166170_c075 | Điều 74. Nhiệm vụ, quyền hạn của Hội đồng thành viên của tổ chức tín dụng là công ty trách nhiệm hữu hạn một thành viên ... |
| 4 | `169221_c002` | 18.5119 | Thông tư số 43/2024/TT-NHNN sửa đổi, bổ sung một số điều của Thông tư số 01/2014/TT-NHNN ngày 10 tháng 12 năm 2014 của Thống đốc Ngân hàng Nhà nước Việt Nam hướng dẫn việc tổ chức thực hiện hoạt đọng quản lý dự trữ ngoại hối nhà nước. | 43/2024/TT-NHNN | Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 01/2014/TT-NHNN | 169221_c002 | Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 01/2014/TT-NHNN 1. Sửa đổi, bổ sung một số điểm, khoản của Điều 3 n... |
| 5 | `186888_c028` | 18.4681 | Thông tư số 62/2025/TT-NHNN Quy định về hệ thống kiểm soát nội bộ của tổ chức tín dụng là hợp tác xã, tổ chức tài chính vi mô | 62/2025/TT-NHNN | Điều 27. Yêu cầu, chiến lược quản lý rủi ro tín dụng | 186888_c028 | Điều 27. Yêu cầu, chiến lược quản lý rủi ro tín dụng 1. Quản lý rủi ro tín dụng được thực hiện trong suốt quá trình xem ... |

### 2. Dense Baseline
| Rank | Chunk ID | Score | Citation | Excerpt |
|---|---|---|---|---|
| 1 | `166170_c137` | 0.7062 | Luật Các tổ chức tín dụng số 32/2024/QH15 | 32/2024/QH15 | Điều 136. Giới hạn cấp tín dụng | 166170_c137 | Điều 136. Giới hạn cấp tín dụng 1. Tổng mức dư nợ cấp tín dụng đối với một khách hàng, một khách hàng và người có liên q... |
| 2 | `177271_c019` | 0.6854 | Thông tư số 01/2025/TT-NHNN Quy định về cấp Giấy phép lần đầu, cấp đổi Giấy phép của quỹ tín dụng nhân dân | 01/2025/TT-NHNN | Điều 18. Trách nhiệm của Ngân hàng Nhà nước Khu vực | 177271_c019 | Điều 18. Trách nhiệm của Ngân hàng Nhà nước Khu vực 1. Thẩm định tính đầy đủ, hợp lệ của hồ sơ đề nghị cấp Giấy phép quỹ... |
| 3 | `f69936f0-6937-11f1-a48d-29bc6b0fd706_c052` | 0.6818 | Văn bản hợp nhất Nghị định số 156/2020/NĐ-CP Quy định xử phạt vi phạm hành chính trong lĩnh vực chứng khoán và thị trường chứng khoán | 17/VBHN-BTC | Điều 47. Thẩm quyền xử phạt vi phạm hành chính | f69936f0-6937-11f1-a48d-29bc6b0fd706_c052 | Điều 47. Thẩm quyền xử phạt vi phạm hành chính 1. [158] Giám đốc Sở Tài chính, Chánh Thanh tra Chứng khoán Nhà nước, Trư... |
| 4 | `27257_c040` | 0.6742 | Thông tư số 44/2011/TT-NHNN Quy định về hệ thống kiểm soát nội bộ và kiểm toán nội bộ của tổ chức tín dụng, chi nhánh ngân hàng nước ngoài | 44/2011/TT-NHNN | Điều 39. Hiệu lực thi hành | 27257_c040 | Điều 39. Hiệu lực thi hành 1. Thông tư này có hiệu lực thi hành kể từ ngày 12 tháng 02 năm 2012. 2. Quyết định số 36/200... |
| 5 | `166170_c194` | 0.6685 | Luật Các tổ chức tín dụng số 32/2024/QH15 | 32/2024/QH15 | Điều 193. Thẩm quyền quyết định cho vay, lãi suất và tài sản bảo đảm của khoản vay đặc biệt | 166170_c194 | Điều 193. Thẩm quyền quyết định cho vay, lãi suất và tài sản bảo đảm của khoản vay đặc biệt 1. Ngân hàng Nhà nước quyết ... |

---

## Query Type: `MIXED`
**Query:** `Theo Thông tư 01/2014/TT-NHNN việc vận chuyển tài sản quý được quy định như thế nào?`

### 1. BM25 Baseline
| Rank | Chunk ID | Score | Citation | Excerpt |
|---|---|---|---|---|
| 1 | `44209_c001` | 31.3504 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | 44209_c001 | NGÂN HÀNG NHÀ NƯỚC VIỆT NAM ------- CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM Độc lập - Tự do - Hạnh phúc --------------- Số: 0... |
| 2 | `44209_c051` | 28.2461 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 50. Phương tiện vận chuyển | 44209_c051 | Điều 50. Phương tiện vận chuyển 1. Vận chuyển tiền mặt, tài sản quý, giấy tờ có giá phải sử dụng xe chuyên dùng và các p... |
| 3 | `44209_c056` | 27.5505 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 55. Lực lượng tham gia vận chuyển và trách nhiệm của người áp tải | 44209_c056 | Điều 55. Lực lượng tham gia vận chuyển và trách nhiệm của người áp tải 1. Khi vận chuyển tiền mặt, tài sản quý, giấy tờ ... |
| 4 | `44209_c052` | 27.411 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 51. Đảm bảo bí mật thông tin vận chuyển | 44209_c052 | Điều 51. Đảm bảo bí mật thông tin vận chuyển 1. Những người tổ chức và tham gia vận chuyển tiền mặt, tài sản quý, giấy t... |
| 5 | `44209_c049` | 26.8316 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 48. Trách nhiệm tổ chức vận chuyển | 44209_c049 | Điều 48. Trách nhiệm tổ chức vận chuyển 1. Cục Phát hành và Kho quỹ có nhiệm vụ tổ chức vận chuyển tiền mặt, tài sản quý... |

### 2. Dense Baseline
| Rank | Chunk ID | Score | Citation | Excerpt |
|---|---|---|---|---|
| 1 | `44209_c051` | 0.7445 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 50. Phương tiện vận chuyển | 44209_c051 | Điều 50. Phương tiện vận chuyển 1. Vận chuyển tiền mặt, tài sản quý, giấy tờ có giá phải sử dụng xe chuyên dùng và các p... |
| 2 | `44209_c048` | 0.7315 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 47. Quy trình vận chuyển | 44209_c048 | Điều 47. Quy trình vận chuyển Quy trình vận chuyển tiền mặt, tài sản quý, giấy tờ có giá bắt đầu từ khi nhận, đóng gói n... |
| 3 | `44209_c050` | 0.7256 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 49. Giấy ủy quyền vận chuyển | 44209_c050 | Điều 49. Giấy ủy quyền vận chuyển Khi giao nhận và vận chuyển tiền mặt, tài sản quý, giấy tờ có giá, người áp tải hàng p... |
| 4 | `44209_c049` | 0.7105 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 48. Trách nhiệm tổ chức vận chuyển | 44209_c049 | Điều 48. Trách nhiệm tổ chức vận chuyển 1. Cục Phát hành và Kho quỹ có nhiệm vụ tổ chức vận chuyển tiền mặt, tài sản quý... |
| 5 | `44209_c056` | 0.6926 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 55. Lực lượng tham gia vận chuyển và trách nhiệm của người áp tải | 44209_c056 | Điều 55. Lực lượng tham gia vận chuyển và trách nhiệm của người áp tải 1. Khi vận chuyển tiền mặt, tài sản quý, giấy tờ ... |

---

### 3. Hybrid Search (RRF) - Query: `Quy định 73/2016/NĐ-CP Điều 115 về hiệu lực thi hành`
| Rank | Chunk ID | BM25 Rank | Dense Rank | RRF Score | Citation | Excerpt |
|---|---|---|---|---|---|---|
| 1 | `112025_c116` | 3 | 1 | 0.03227 | Nghị định số 73/2016/NĐ-CP Quy định chi tiết thi hành Luật kinh doanh bảo hiểm và Luật sửa đổi, bổ sung một số điều của Luật kinh doanh bảo hiểm | 73/2016/NĐ-CP | Điều 115. Hiệu lực thi hành | 112025_c116 | Điều 115. Hiệu lực thi hành 1. Nghị định này có hiệu lực thi hành từ ngày 01 tháng 7 năm 2016. 2. Ng... |
| 2 | `163441_c123` | 2 | 8 | 0.03083 | Nghị định số 46/2023/NĐ-CP Quy định chi tiết thi hành một số điều của Luật Kinh doanh bảo hiểm | 46/2023/NĐ-CP | Điều 122. Hiệu lực thi hành | 163441_c123 | Điều 122. Hiệu lực thi hành 1. Nghị định này có hiệu lực thi hành kể từ ngày ký, trừ trường hợp quy ... |
| 3 | `166269_c115` | 1 | 12 | 0.03028 | Luật Hợp tác xã số 17/2023/QH15 | 17/2023/QH15 | Điều 114. Điều khoản thi hành | 166269_c115 | Điều 114. Điều khoản thi hành 1. Luật này có hiệu lực thi hành từ ngày 01 tháng 7 năm 2024, trừ quy ... |
| 4 | `166170_c210` | 9 | 4 | 0.03012 | Luật Các tổ chức tín dụng số 32/2024/QH15 | 32/2024/QH15 | Điều 209. Hiệu lực thi hành | 166170_c210 | Điều 209. Hiệu lực thi hành 1. Luật này có hiệu lực thi hành từ ngày 01 tháng 7 năm 2024, trừ quy đị... |
| 5 | `146468_c053` | 12 | 5 | 0.02927 | Nghị định số 156/2020/NĐ-CP Quy định xử phạt vi phạm hành chính trong lĩnh vực chứng khoán và thị trường chứng khoán | 156/2020/NĐ-CP | Điều 52. Hiệu lực thi hành | 146468_c053 | Điều 52. Hiệu lực thi hành 1. Nghị định này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2021. 2. Ng... |

---

### 3. Hybrid Search (RRF) - Query: `Ai có thẩm quyền phê duyệt hạn mức tín dụng và cấp tiền mặt?`
| Rank | Chunk ID | BM25 Rank | Dense Rank | RRF Score | Citation | Excerpt |
|---|---|---|---|---|---|---|
| 1 | `186888_c018` | 1 | N/A | 0.01639 | Thông tư số 62/2025/TT-NHNN Quy định về hệ thống kiểm soát nội bộ của tổ chức tín dụng là hợp tác xã, tổ chức tài chính vi mô | 62/2025/TT-NHNN | Điều 17. Hoạt động kiểm soát đối với hoạt động cấp tín dụng | 186888_c018 | Điều 17. Hoạt động kiểm soát đối với hoạt động cấp tín dụng 1. Hoạt động kiểm soát đối với hoạt động... |
| 2 | `166170_c137` | N/A | 1 | 0.01639 | Luật Các tổ chức tín dụng số 32/2024/QH15 | 32/2024/QH15 | Điều 136. Giới hạn cấp tín dụng | 166170_c137 | Điều 136. Giới hạn cấp tín dụng 1. Tổng mức dư nợ cấp tín dụng đối với một khách hàng, một khách hàn... |
| 3 | `38128_c007` | 2 | N/A | 0.01613 | Thông tư số 37/2014/TT-NHNN Quy định việc thiết kế mẫu tiền, chế bản và quản lý in, đúc tiền Việt Nam | 37/2014/TT-NHNN | Điều 6. Trình duyệt mẫu thiết kế đồng tiền | 38128_c007 | Điều 6. Trình duyệt mẫu thiết kế đồng tiền 1. Sau khi hoàn thành việc thiết kế mẫu tiền theo Đề án đ... |
| 4 | `177271_c019` | N/A | 2 | 0.01613 | Thông tư số 01/2025/TT-NHNN Quy định về cấp Giấy phép lần đầu, cấp đổi Giấy phép của quỹ tín dụng nhân dân | 01/2025/TT-NHNN | Điều 18. Trách nhiệm của Ngân hàng Nhà nước Khu vực | 177271_c019 | Điều 18. Trách nhiệm của Ngân hàng Nhà nước Khu vực 1. Thẩm định tính đầy đủ, hợp lệ của hồ sơ đề ng... |
| 5 | `166170_c075` | 3 | N/A | 0.01587 | Luật Các tổ chức tín dụng số 32/2024/QH15 | 32/2024/QH15 | Điều 74. Nhiệm vụ, quyền hạn của Hội đồng thành viên của tổ chức tín dụng là công ty trách nhiệm hữu hạn một thành viên | 166170_c075 | Điều 74. Nhiệm vụ, quyền hạn của Hội đồng thành viên của tổ chức tín dụng là công ty trách nhiệm hữu... |

---

### 3. Hybrid Search (RRF) - Query: `Theo Thông tư 01/2014/TT-NHNN việc vận chuyển tài sản quý được quy định như thế nào?`
| Rank | Chunk ID | BM25 Rank | Dense Rank | RRF Score | Citation | Excerpt |
|---|---|---|---|---|---|---|
| 1 | `44209_c051` | 2 | 1 | 0.03252 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 50. Phương tiện vận chuyển | 44209_c051 | Điều 50. Phương tiện vận chuyển 1. Vận chuyển tiền mặt, tài sản quý, giấy tờ có giá phải sử dụng xe ... |
| 2 | `44209_c056` | 3 | 5 | 0.03126 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 55. Lực lượng tham gia vận chuyển và trách nhiệm của người áp tải | 44209_c056 | Điều 55. Lực lượng tham gia vận chuyển và trách nhiệm của người áp tải 1. Khi vận chuyển tiền mặt, t... |
| 3 | `44209_c049` | 5 | 4 | 0.03101 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 48. Trách nhiệm tổ chức vận chuyển | 44209_c049 | Điều 48. Trách nhiệm tổ chức vận chuyển 1. Cục Phát hành và Kho quỹ có nhiệm vụ tổ chức vận chuyển t... |
| 4 | `44209_c050` | 11 | 3 | 0.02996 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 49. Giấy ủy quyền vận chuyển | 44209_c050 | Điều 49. Giấy ủy quyền vận chuyển Khi giao nhận và vận chuyển tiền mặt, tài sản quý, giấy tờ có giá,... |
| 5 | `44209_c052` | 4 | 11 | 0.02971 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 51. Đảm bảo bí mật thông tin vận chuyển | 44209_c052 | Điều 51. Đảm bảo bí mật thông tin vận chuyển 1. Những người tổ chức và tham gia vận chuyển tiền mặt,... |

---

### 4. Hybrid + Neural Reranking - Query: `Quy định 73/2016/NĐ-CP Điều 115 về hiệu lực thi hành`

**BEFORE RERANK vs AFTER RERANK Comparison:**
| Final Rank | Original Hybrid Rank | Chunk ID | Hybrid RRF Score | Rerank Score | Citation | Excerpt |
|---|---|---|---|---|---|---|
| 1 | 1 | `112025_c116` | 0.03227 | 7.399 | Nghị định số 73/2016/NĐ-CP Quy định chi tiết thi hành Luật kinh doanh bảo hiểm và Luật sửa đổi, bổ sung một số điều của Luật kinh doanh bảo hiểm | 73/2016/NĐ-CP | Điều 115. Hiệu lực thi hành | 112025_c116 | Điều 115. Hiệu lực thi hành 1. Nghị định này có hiệu lực thi hành từ ngày 01 tháng 7 năm 2016. 2. Ng... |
| 2 | 6 | `f69936f0-6937-11f1-a48d-29bc6b0fd706_c059` | 0.02924 | 7.0539 | Văn bản hợp nhất Nghị định số 156/2020/NĐ-CP Quy định xử phạt vi phạm hành chính trong lĩnh vực chứng khoán và thị trường chứng khoán | 17/VBHN-BTC | Điều 52. Hiệu lực thi hành | f69936f0-6937-11f1-a48d-29bc6b0fd706_c059 | Điều 52. Hiệu lực thi hành 1. Nghị định này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2021. 2. Ng... |
| 3 | 5 | `146468_c053` | 0.02927 | 6.9948 | Nghị định số 156/2020/NĐ-CP Quy định xử phạt vi phạm hành chính trong lĩnh vực chứng khoán và thị trường chứng khoán | 156/2020/NĐ-CP | Điều 52. Hiệu lực thi hành | 146468_c053 | Điều 52. Hiệu lực thi hành 1. Nghị định này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2021. 2. Ng... |
| 4 | 2 | `163441_c123` | 0.03083 | 6.9534 | Nghị định số 46/2023/NĐ-CP Quy định chi tiết thi hành một số điều của Luật Kinh doanh bảo hiểm | 46/2023/NĐ-CP | Điều 122. Hiệu lực thi hành | 163441_c123 | Điều 122. Hiệu lực thi hành 1. Nghị định này có hiệu lực thi hành kể từ ngày ký, trừ trường hợp quy ... |
| 5 | 15 | `112025_c001` | 0.01471 | 6.3876 | Nghị định số 73/2016/NĐ-CP Quy định chi tiết thi hành Luật kinh doanh bảo hiểm và Luật sửa đổi, bổ sung một số điều của Luật kinh doanh bảo hiểm | 73/2016/NĐ-CP | 112025_c001 | CHÍNH PHỦ CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM Độc lập – Tự do – Hạnh phúc Số: 73/2016/NĐ-CP Hà Nội, n... |

---

### 4. Hybrid + Neural Reranking - Query: `Ai có thẩm quyền phê duyệt hạn mức tín dụng và cấp tiền mặt?`

**BEFORE RERANK vs AFTER RERANK Comparison:**
| Final Rank | Original Hybrid Rank | Chunk ID | Hybrid RRF Score | Rerank Score | Citation | Excerpt |
|---|---|---|---|---|---|---|
| 1 | 15 | `38128_c006` | 0.01471 | 5.349 | Thông tư số 37/2014/TT-NHNN Quy định việc thiết kế mẫu tiền, chế bản và quản lý in, đúc tiền Việt Nam | 37/2014/TT-NHNN | Điều 5. Thiết kế mẫu tiền | 38128_c006 | Điều 5. Thiết kế mẫu tiền 1. Cục Phát hành và Kho quỹ có nhiệm vụ xây dựng và triển khai Kế hoạch th... |
| 2 | 11 | `38128_c005` | 0.01515 | 4.7228 | Thông tư số 37/2014/TT-NHNN Quy định việc thiết kế mẫu tiền, chế bản và quản lý in, đúc tiền Việt Nam | 37/2014/TT-NHNN | Điều 4. Xây dựng Đề án thiết kế mẫu tiền | 38128_c005 | Điều 4. Xây dựng Đề án thiết kế mẫu tiền 1. Căn cứ vào chủ trương thiết kế mẫu tiền đã được Thống đố... |
| 3 | 19 | `186888_c006` | 0.01429 | 4.0294 | Thông tư số 62/2025/TT-NHNN Quy định về hệ thống kiểm soát nội bộ của tổ chức tín dụng là hợp tác xã, tổ chức tài chính vi mô | 62/2025/TT-NHNN | Điều 5. Cơ chế, chính sách, quy trình, quy định nội bộ | 186888_c006 | Điều 5. Cơ chế, chính sách, quy trình, quy định nội bộ 1. Yêu cầu đối với cơ chế, chính sách, quy tr... |
| 4 | 16 | `168220_c023` | 0.01471 | 3.4322 | Thông tư số 27/2024/TT-NHNN Quy định về việc ngân hàng hợp tác xã, việc trích nộp, quản lý và sử dụng Quỹ bảo đảm an toàn hệ thống quỹ tín dụng nhân dân | 27/2024/TT-NHNN | Điều 22. Quyền hạn | 168220_c023 | Điều 22. Quyền hạn 1. Được Ngân hàng Nhà nước cung cấp thông tin liên quan đến hoạt động của quỹ tín... |
| 5 | 9 | `186888_c028` | 0.01538 | 3.3456 | Thông tư số 62/2025/TT-NHNN Quy định về hệ thống kiểm soát nội bộ của tổ chức tín dụng là hợp tác xã, tổ chức tài chính vi mô | 62/2025/TT-NHNN | Điều 27. Yêu cầu, chiến lược quản lý rủi ro tín dụng | 186888_c028 | Điều 27. Yêu cầu, chiến lược quản lý rủi ro tín dụng 1. Quản lý rủi ro tín dụng được thực hiện trong... |

---

### 4. Hybrid + Neural Reranking - Query: `Theo Thông tư 01/2014/TT-NHNN việc vận chuyển tài sản quý được quy định như thế nào?`

**BEFORE RERANK vs AFTER RERANK Comparison:**
| Final Rank | Original Hybrid Rank | Chunk ID | Hybrid RRF Score | Rerank Score | Citation | Excerpt |
|---|---|---|---|---|---|---|
| 1 | 17 | `44209_c073` | 0.01449 | 6.3393 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 72. Hiệu lực thi hành | 44209_c073 | Điều 72. Hiệu lực thi hành 1. Thông tư này có hiệu lực thi hành kể từ ngày 20/02/2014. 2. Kể từ ngày... |
| 2 | 10 | `44209_c001` | 0.01639 | 5.8378 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | 44209_c001 | NGÂN HÀNG NHÀ NƯỚC VIỆT NAM ------- CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM Độc lập - Tự do - Hạnh phúc -... |
| 3 | 5 | `44209_c052` | 0.02971 | 4.5627 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 51. Đảm bảo bí mật thông tin vận chuyển | 44209_c052 | Điều 51. Đảm bảo bí mật thông tin vận chuyển 1. Những người tổ chức và tham gia vận chuyển tiền mặt,... |
| 4 | 7 | `44209_c002` | 0.0274 | 3.8238 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 1. Phạm vi điều chỉnh | 44209_c002 | Điều 1. Phạm vi điều chỉnh 1. Thông tư này quy định việc giao nhận, bảo quản, vận chuyển; kiểm tra, ... |
| 5 | 8 | `44209_c058` | 0.02583 | 3.7039 | Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | Điều 57. Trách nhiệm của người điều khiển phương tiện | 44209_c058 | Điều 57. Trách nhiệm của người điều khiển phương tiện Người điều khiển phương tiện chịu trách nhiệm ... |

---
