# Bài báo SSRC v1 (18/11/2026): ghi chú

Tệp bài báo: [CaoTrongNguyen_LeKhacGiaKhang_KhuyenNghiNgheSi_BaiBao_SSRC_v1_18-11-2026.docx](CaoTrongNguyen_LeKhacGiaKhang_KhuyenNghiNgheSi_BaiBao_SSRC_v1_18-11-2026.docx). Bản PDF kiểm tra có 7 trang, khổ Letter, do Word xuất.

Bản v1 dựng từ bài mẫu của cô ([GopY_GVHD_18-11-2026_BaiBaoMau_SSRC.docx](GopY_GVHD_18-11-2026_BaiBaoMau_SSRC.docx)) bằng script [dung_bai_bao_v1.py](dung_bai_bao_v1.py). Script chỉ thay chữ trong XML nên giữ nguyên định dạng SSRC: hai cột, đề mục La Mã, bảng đánh số La Mã, tài liệu theo IEEE. Tiêu đề, cấu trúc, hình và công thức giữ như bản mẫu. Mỗi phép thay đều được kiểm tra trúng đúng một chỗ.

```
python -X utf8 docs/bai-bao-ssrc/dung_bai_bao_v1.py docs/bai-bao-ssrc/GopY_GVHD_18-11-2026_BaiBaoMau_SSRC.docx docs/bai-bao-ssrc/CaoTrongNguyen_LeKhacGiaKhang_KhuyenNghiNgheSi_BaiBao_SSRC_v1_18-11-2026.docx
python -X utf8 docs/bai-bao-ssrc/doi_chieu_so_lieu.py docs/bai-bao-ssrc/CaoTrongNguyen_LeKhacGiaKhang_KhuyenNghiNgheSi_BaiBao_SSRC_v1_18-11-2026.docx
```

## Cần nhóm xác nhận (tô vàng trong bài)

1. **Câu công bố dùng AI** ở Lời cảm ơn. Đây là câu nháp viết theo Lời cam đoan của khóa luận: Claude và Codex hỗ trợ viết và kiểm thử mã, đối chiếu số liệu, soạn nháp và chỉnh diễn đạt. Nhóm cần sửa lại cho đúng phạm vi đã dùng thật khi viết bài.
2. **Ngày nộp bài** ở chú thích chân trang, hiện ghi "…/…/2026".
3. **Kho mã**: bài ghi đường dẫn https://github.com/trongnguyen1010/musicrec-collaborative-filtering. Nhóm cần tự kiểm kho đã để chế độ công khai chưa, vì tôi không kiểm được từ máy. Kho không chứa tệp dữ liệu `.dat` của GroupLens, chỉ có tệp readme ở `docs/seminar/`.

## Thay đổi so với bản mẫu của cô

| Chỗ | Bản mẫu | v1 | Lý do |
| --- | --- | --- | --- |
| Bốn ghi chú chữ đỏ (ghi chú chung, IFPI, Bảng 4.13, thời gian phản hồi) | Có | Đã xóa | Đã xử lý: IFPI 69,6% xác nhận qua thông cáo báo chí IFPI ngày 18/03/2026; Bảng 4.13 xác nhận bằng script chẩn đoán; thời gian phản hồi giữ số của Bảng 5.6 và giải thích ở khóa luận v23, mục 5.4.4 |
| Bảng III, hai dòng E7 | Không có KTC; ghi chú "khóa luận không báo KTC riêng cho hai mô hình E7" | 0,1937 [0,1841; 0,2032]; 0,1940 [0,1844; 0,2036]; ghi chú sửa thành "…hạt giống 42, trên một lần chia dữ liệu" | Khóa luận v23, mục 4.11.1 |
| Bảng III, SVD có độ lệch | 0,0627 | 0,0626 | Giá trị đủ là 0,0626499. Bản mẫu làm tròn hai lần (0,062650 rồi 0,0627) |
| Bảng VI, Popularity N = 5, và câu ở IV-E | 0,0598; 0,0565–0,0598 | 0,0597; 0,0565–0,0597 | Giá trị đủ là 0,0597496, cùng lỗi làm tròn hai lần |
| Abstract, Tóm tắt (M2) | "but does at N = 3 and N = 5"; "nhưng vượt ở N = 3 và N = 5" | Ghi là phân tích sau khi khóa cấu hình, kết quả sơ bộ trên 189 người | Góp ý 1 và 4; danh sách kiểm tra mục 7 |
| IV-A (E8) | L = 5 cho 0,0652 và 0,0565 | Thêm: 0,0652 của UserCF cao hơn Popularity (0,0624) | Góp ý 2 |
| IV-B | "UserCF, ItemCF và SVD có độ lệch đều thấp hơn Popularity" | Thêm điều kiện "với cách tổng hợp trung bình có trọng số và lưới đã khóa" | Góp ý 2 |
| IV-C (E7) | "vượt Popularity… vượt PureSVD" | "cao hơn…"; thêm câu: chỉ một lần chia, KTC chồng lấn với PureSVD | Góp ý 3 |
| IV-D (theo mức ưa chuộng) | "thực hiện sau khi tập kiểm thử đã mở" | "là phân tích sau khi khóa cấu hình" | Góp ý 1 |
| IV-E (M2) | — | Thêm: cấu hình ở góc lưới, kết quả sơ bộ; giải thích Popularity bằng nhau ở N = 0 và N = 1 (9/189 người); giao thức (5) ghi là phân tích sau khi khóa cấu hình | Góp ý 4, 5 |
| Thảo luận, hạn chế (i) | "trong khi… hai mô hình láng giềng top-N đều vượt rõ"; "một hạt giống" | Ghi rõ phân tích sau khi khóa cấu hình, so với Popularity; "hạt giống 42" | Góp ý 1, 3 |
| Kết luận | "M2 chỉ vượt Popularity khi…" | "chỉ cao hơn… trong phân tích sau khi khóa cấu hình và ở mức sơ bộ"; thêm hướng kiểm định chéo theo người dùng cho M2 | Góp ý 1, 4 |
| III-C, III-D | (3), (4) không được nhắc bằng số | "c_i trong (3)", "(α, n_min) của (4)" | Danh sách kiểm tra: công thức (1)–(5) đều được nhắc |
| Chú thích chân trang | "[CẦN BỔ SUNG: e-mail]"; chú thích không hiện vì không có tham chiếu | Thêm e-mail hai thành viên; gắn tham chiếu ẩn vào tiêu đề như mẫu IEEE, nên chú thích hiện ở trang 1 | Thông tin nhóm cung cấp |
| Lời cảm ơn | "[CẦN BỔ SUNG: câu công bố AI]" | Câu nháp tô vàng | Chờ nhóm xác nhận |

## Đối chiếu số liệu

- **Bảng III–VI**: `doi_chieu_so_lieu.py` đọc trực tiếp các tệp kết quả mà khóa luận v23 dùng khi dựng, làm tròn một lần như quy ước bài báo và so từng ô. Kết quả: 33 dòng, 0 chỗ khác. Các tệp gồm:
  - `docs/results/chinh_thuc_cloud_20261026/test/metrics.csv`
  - `bo_sung_2/thong_ke/kiem_dinh_bo_sung.json`
  - `bo_sung_2/e7/metrics.csv` và `statistics_ndcg_at_10.json`
  - `bo_sung/m1_bien_the_test.csv`
  - `m2/test/metrics.csv` và `bo_sung_2/eg/metrics.csv`
- **Bảng I, II và các số trong văn bản**: đối chiếu theo bảng tra ở Phần 4 của hướng dẫn, với khóa luận v23.

| Nội dung | Giá trị trong bài | Nguồn (khóa luận v23 / tệp) |
| --- | --- | --- |
| IFPI | 69,6% | Mục 1.1; thông cáo IFPI 18/03/2026 |
| Dữ liệu (Bảng I) | 1.892/17.632/92.834; 1.877/17.617/92.801; 0,2783%/0,2804%; 1.829 (96,67%/97,44%); 10.679/10.667 | Bảng 3.4 (`bo_sung_2/e_d/metrics.json`) |
| Phép chia | 74.275/9.263/9.263; 15.398; 12,10%/12,99%; 1.865/1.855 | Bảng 4.1 |
| Bảng II | 0,0004; 0,0624; 0,0175; 0,0154; 0,0607; 0,1666; 0,1974; M1 0,1675; M2 0,0455 | Bảng 4.3; M1 λ = 0,75, β = 0,5 xác thực 0,167477 (`m1_metrics.csv`); M2 0,045492 (`m2/validation/selection.json`) |
| Tinh chỉnh | 0,1564/0,1546/0,1517; 0,0292 ở vòng 100; 0,8601 ở vòng 51 | Bảng 4.4, Hình 4.1 (`bo_sung/learning_curve.csv`) |
| E8 | 0,0652; 0,0565; Popularity 0,0624 | Bảng 4.19 (`bo_sung_2/e_s/baselines_validation.csv`, `e_p/popularity_validation.csv`) |
| E7, xác thực | 0,1739; 0,1742 | Mục 4.11.1 |
| Theo từng người dùng | 925 (49,9%), 791 (42,6%), 765, 139 (7,5%) | Mục 4.6 |
| Ba hạt giống | 0,0635 ± 0,0008; 0,2172 ± 0,0012 | Mục 4.5, 4.9 (`test/seed_summary.json`) |
| TOST | δ = 0,05 × 0,1828 ≈ 0,0091; KTC 90% [−0,0036; 0,0009] | Công thức (4.1) |
| E9 | β = 0,75; 0,1628; 135,42 | Mục 4.7 |
| Theo mức ưa chuộng | 0,0724 / 0,3065; +0,0087 [0,0054; 0,0121]; −0,0127 | Bảng 4.10, mục 4.6 |
| M2 (giao thức đã khóa) | −0,0087 [−0,0266; 0,0084], p 0,857; 43/189, 22,75%; 0,09% → 5,55%; 294,91 → 129,10; 0,0276–0,0297 và 0,0565–0,0597 | Mục 4.8, Bảng 4.14, 4.15; `m2/validation/metrics.csv` |
| Popularity N = 0/1 | 9/189 | Mục 4.8 (`docs/results/chuong_4_bo_sung_3/popularity_n0_n1/summary.json`) |
| M2 (tập đích (5)) | 0,0630 [0,0257; 0,0986], r_rb 0,341, p 0,001; 0,0567, p 0,009; −0,0128, p 0,735 | Bảng 4.21 |
| Hệ thống | 12/12 ca; 1.877 và 189 người, trùng 100%; 3,78–11,46 ms | Bảng 5.4–5.6 |
| Thẻ | 36,69% (5.650/15.398) | Mục 4.7, 4.12 |
| Môi trường | Xeon 2,10 GHz, 4 luồng, 15,7 GiB; 48 phút; sai lệch < 10⁻¹⁴ | Mục 4.1.1 |

## Danh sách kiểm tra (Phần 7 của hướng dẫn)

| Mục | Kết quả |
| --- | --- |
| Mọi [CẦN BỔ SUNG] và chữ đỏ đã xử lý và xóa | Đạt. Script có `assert` bảo đảm không còn màu đỏ và không còn "CẦN BỔ SUNG". Câu AI và ngày nộp tô vàng, chờ nhóm xác nhận |
| Số liệu khớp giữa tóm tắt, thân bài, bảng, kết luận và bảng tra | Đạt (xem mục đối chiếu ở trên) |
| Kết quả hậu kiểm (E7–E10, nhóm người dùng) có cụm "sau khi khóa cấu hình" | Đạt: Abstract, Tóm tắt, III-B, IV-A, Bảng III, IV, IV-C, IV-D, IV-E, Thảo luận, Kết luận |
| M1 dựa trên TOST và nêu ILD theo thẻ; M2 nêu cả hai định nghĩa tập đích | Đạt (IV-D, Bảng V, Bảng VI) |
| Mỗi bảng/hình được nhắc; đánh số liên tục; công thức (1)–(5) được nhắc | Đạt: Bảng I–VI, Hình 1–3 đều được nhắc; (3), (4) nay đã được nhắc |
| Tài liệu được trích và ngược lại; định dạng IEEE | Đạt: 32/32 tài liệu được trích, không có số trích ngoài danh mục |
| Không có cụm khẳng định mạnh hơn số liệu | Đạt: không có "vượt trội", "vượt có ý nghĩa". "Chứng minh" chỉ xuất hiện trong câu "chưa chứng minh hai mô hình tương đương". "Tốt nhất" luôn kèm điều kiện ("trên tập xác thực", "trong sáu mô hình đối sánh") |
| Dài 6–7 trang; tên tác giả, đơn vị, e-mail, tác giả liên hệ | 7 trang. Chú thích chân trang hiện đủ đơn vị và e-mail; tác giả liên hệ giữ như cô ghi |
