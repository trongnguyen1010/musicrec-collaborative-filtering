# Báo cáo v23: các thay đổi theo góp ý GVHD ngày 18/11/2026

Bản v23 (`docs/bao-cao/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_v23_18-11-2026.docx`) kế thừa v22. Nhóm dựng lại bản này bằng `docs/bao-cao/nguon_v23/dung_v23.ps1` từ bản góp ý ngày 10/11, có mã SHA-256 `31ef177d…88d9f` và không đổi so với commit trước. Phần nội dung được sửa trực tiếp trong `nguon_v19/ch3_v19.py`, `nguon_v19/ch4_v19.py` và `nguon_v20/edits_v20.py`, giống cách làm của v22. Tệp `nguon_v23/edits_v23.py` chạy cuối và sửa những chỗ các script trên không với tới. Hình 3.3 được vẽ lại bằng `nguon_v23/ve_hinh_v23.py`. Nhóm không chạy thêm thực nghiệm mới, chỉ chạy một script chẩn đoán chỉ đọc ở điểm 5. Bản PDF kiểm tra có 168 trang, theo cả Word lẫn pdfinfo (v22 có 165 trang).

| # | Góp ý | Chỗ sửa trong v23 | Nguồn số liệu |
| --- | --- | --- | --- |
| 1 | Kết quả hậu kiểm phải ghi "phân tích sau khi khóa cấu hình". Thay "vượt có ý nghĩa" bằng cách nói về cỡ hiệu ứng | Tóm tắt, Abstract, 1.7 (ý thứ hai, ba, tư), 4.5, 4.6, RQ3 ở 4.7, 4.11.1, 4.11.3, 4.12, 4.13, Bảng 6.1 (dòng 3b), 6.2, Bảng 6.2 (RQ1, RQ3, RQ4) | E7: ⟦r_rb⟧ 0,10397 và 0,12309; Holm p 0,00233 và 0,00083 (`outputs/chuong_4_bo_sung_2/e7/test/statistics_ndcg_at_10.json`, bản sao ở `docs/results/chinh_thuc_cloud_20261026/bo_sung_2/e7/`) |
| 2 | Ghi điều kiện "cách tổng hợp trung bình có trọng số và lưới đã khóa". Nêu UserCF L = 5 | 4.5 (hai đoạn và câu trả lời RQ1), ghi chú dưới Bảng 4.3, đoạn sau Bảng 4.19 (4.11.2) | UserCF L = 5, co rút 10: 0,065160 (`outputs/chuong_4_bo_sung_2/e_s/baselines_validation.csv`). Popularity: 0,062362 (`e_p/popularity_validation.csv`, dòng log_count_sum). ItemCF L = 5, co rút 0: 0,056458, vẫn thấp hơn Popularity |
| 3 | Mọi kết quả dựa trên một lần chia (hạt giống 42). Chênh lệch top-N nhỏ | 4.1.1 (đoạn cuối), câu trả lời RQ1 ở 4.5, 4.11.1 (thêm KTC 95%), 4.12 (tính hợp lệ nội tại), 6.3 (ý thứ năm) | Chênh lệch so với PureSVD: 0,010888 và 0,011193. KTC 95% của NDCG@10: UserCF top-N [0,184070; 0,203222], ItemCF top-N [0,184401; 0,203577] (`mean_ndcg10_ci` trong cùng tệp). PureSVD [0,173448; 0,192598] (Bảng 4.7) |
| 4 | Trình bày M2 là kết quả sơ bộ, nêu cả hai định nghĩa tập đích, hướng kiểm định chéo theo người dùng | Đoạn mới đầu 4.8; câu trả lời RQ4; 4.11.3; 6.3 (ý thứ tám); 6.4 | Popularity trên nhóm tinh chỉnh từ 0,027627 đến 0,029728 (186 người có đích, `docs/results/chinh_thuc_cloud_20261026/m2/validation/metrics.csv`, K = 10). Trên nhóm để dành từ 0,056508 đến 0,059750 (Bảng 4.13) |
| 5 | Giải thích Popularity bằng nhau ở N = 0 và N = 1 | Đoạn mới sau Bảng 4.13. Các số được đọc từ tệp kết quả lúc dựng, không gõ tay | Script `scripts/diagnose_m2_popularity_n0_n1.py` chạy ngày 18/11/2026, xem mục dưới |
| 6 | Giải thích 8,06 ms và 4,90 ms | Đoạn mới cuối 5.4.4. Câu "sau một lượt khởi động" được sửa thành "50 yêu cầu khởi động không tính" | `outputs/demo/latency_20261107/latency.json`: 20 lượt khởi động, 200 lần lặp, người dùng 2, trung vị 8,059. `docs/results/chuong_5/load_test.json`: `--warmup 50 --requests 1000`, xoay vòng 200 người dùng, trung vị 4,903, tạo lúc 10/11 17:06 UTC. `outputs/demo/latency_20261027/latency.json`: 50 lần lặp, trung vị 5,233. Cả `scripts/measure_latency.py` và `scripts/load_test.py` đều dùng `requests.Session` |
| 7 | δ tính từ NDCG@10 xác thực | Câu mới sau (4.1). Mục 3.7.3 có thêm một câu dẫn tới đây | NDCG@10 xác thực của mô hình nền (λ = 1, β = 0) là 0,166611 (`m1_metrics.csv`), nên δ = 0,00833. KTC 90% [−0,003641; 0,000888] (`thong_ke/kiem_dinh_bo_sung.json`). Script dựng có `assert` kiểm tra khoảng này nằm trong biên |
| 8 | Vẽ lại Hình 3.3 với Next.js ở lớp trên cùng | `ve_hinh_v23.py` sinh `hinh_bao_cao/kien_truc_v23.png`, thêm một câu ở 3.3 | Hình vẽ theo mã. Streamlit (`src/musicrec/ui/app.py`) gọi REST API, nên mũi tên dự phòng trỏ tới lớp API |
| 9 | Bảng 3.5 ở 3.4.1 cần đổi thành 3.3. Sửa văn bản thay thế. Rà tham chiếu | `edits_v23.py`. Sáu hình được sửa văn bản thay thế (Hình 3.6, 5.1, 5.4, 5.7–5.9); Hình 3.3 là hình mới. Rà toàn bộ tham chiếu bằng script | 119 lần dẫn Bảng/Hình, mọi lần dẫn mục và công thức đều có đích. Nhóm đã đọc lại ngữ cảnh từng lần dẫn. Mục lục và danh mục khớp số trang ở 153 mục một dòng |
| 10 | Kiểm số IFPI và Spotify ở 1.1 | Không sửa | Tệp PDF GMR2026_SOTI không đọc được (vượt 10 MB). Thông cáo báo chí IFPI ngày 18/03/2026, tức tài liệu [1] của báo cáo, xác nhận 69,6% và 837 triệu "users of paid streaming subscription accounts". Trang Spotify ngày 30/06/2025, tức tài liệu [4], xác nhận "more than 56 million new artist discoveries" mỗi tuần, 77% "from emerging artists" |

## Thay đổi thêm ngoài mười điểm

- **Mục 5.1.1.** Câu cũ ghi "Giao diện Streamlit dùng chung DemoService". Câu mới ghi Streamlit gọi cùng dịch vụ FastAPI qua HTTP, đúng với `src/musicrec/ui/app.py`.
- **Trang đầu không có số trang.** Phần trang đầu đánh số La Mã (Lời cảm ơn, Lời cam đoan, mục lục, danh mục) nay không hiển thị số trang, theo mẫu khoa. Đây cũng là thay đổi nhóm đã tự lưu vào tệp v22 lúc 13:43 ngày 11/11/2026. Thay đổi này chưa commit, và phần chữ của v22 không đổi.
- **Lỗi chữ ở 4.5.** "Nguyên cách tổng hợp điểm" được sửa thành "Cách tổng hợp điểm".
- **Nguyên nhân lỗi "Bảng 3.5" ở 3.4.1.** `edits_v19.py` đổi "Bảng 3.3" thành "Bảng 3.5" từ dòng mục lục của Chương 5 trở đi, nên vô tình sửa cả câu này ở Chương 3. Nhóm không sửa `edits_v19.py` để v19 vẫn dựng lại được như cũ. Lỗi được chữa ở `edits_v23.py`.

## Điểm 5: chẩn đoán Popularity ở N = 0 và N = 1

```
.venv/Scripts/python.exe -B scripts/diagnose_m2_popularity_n0_n1.py --output-dir outputs/chuong_4_bo_sung_3/popularity_n0_n1
```

Script chỉ đọc. Script nạp mô hình M2 đã khóa (`outputs/chinh_thuc_cloud_20261026/chuong_4/m2_tuning/model`), `user_roles.json` và split train/test (có kiểm tra SHA-256). Hồ sơ được tạo bằng `profile_order` với hạt giống 42, rồi dùng `rank_scores(features.popularity)` như `scripts/evaluate_m2_test.py`. Script kiểm tra NDCG@10 tính lại trùng với `outputs/chuong_4_bo_sung_2/thong_ke/m2_test/n_{0,1}/popularity/evaluation.json`. Bản sao kết quả nằm ở `docs/results/chuong_4_bo_sung_3/popularity_n0_n1/`, gồm `summary.json` và `per_user.csv`.

- NDCG@10 bằng 0,056508 ở cả N = 0 và N = 1, trên 187 trong 189 người có đích.
- 9 trên 189 người có nghệ sĩ được cung cấp nằm trong top-10 Popularity. 7 người trong số đó không có đích nào trong top-10.
- Hai người còn lại có đích đứng trước nghệ sĩ bị loại. Người dùng 120 có đích ở vị trí 4, nghệ sĩ bị loại ở vị trí 10. Người dùng 1558 có đích ở vị trí 2, nghệ sĩ bị loại ở vị trí 5.
- Nghệ sĩ hạng 11 được đẩy lên không phải đích của ai.
- Danh sách có đổi: số nghệ sĩ khác nhau tăng từ 10 lên 11, độ bao phủ từ 0,000757 lên 0,000833, ARP từ 295,70 xuống 295,52. NDCG@10 của từng người không đổi ở cả 187 người.
- Máy chạy: Windows 11 (10.0.26200), Intel Core i5-11300H, Python 3.11.9, numpy 2.4.6, scipy 1.17.1, pandas 2.3.3, pyarrow 19.0.1. Script chạy trên commit `5d07022`.
