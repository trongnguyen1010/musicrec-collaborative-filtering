# Đối chiếu kết quả với mục tiêu ban đầu của khóa luận

Ngày lập: 06/11/2026.

Mốc đối chiếu: nhánh `research/data-preparation-model-survey` trên GitHub, commit `09a3336`, và báo cáo v16 (26/10). Mục tiêu lấy từ mục 1.3.2 và năm câu hỏi nghiên cứu RQ1–RQ5 của báo cáo. Mọi con số dưới đây chép từ tệp kết quả đã lưu, có ghi nguồn.

## Tóm tắt

- Năm mục tiêu cụ thể (1.3.2): **3 đạt, 2 đạt một phần, 0 chưa làm**.
- Năm câu hỏi nghiên cứu: **4 trả lời được** (RQ4 có kết quả âm), **1 không kết luận được** (RQ2).
- Phần còn thiếu chủ yếu nằm ở **báo cáo**: Chương 5 mới có tiêu đề, mục 4.9.2 (phân tích lỗi từng trường hợp) chưa làm, và demo chưa deploy.

## 1. Năm mục tiêu cụ thể (mục 1.3.2)

| # | Mục tiêu | Trạng thái | Bằng chứng (nguồn) |
| --- | --- | --- | --- |
| 1 | Tiền xử lý, chia tập, biểu diễn dữ liệu | **Đạt** | Chạy lại Chương 3 từ dữ liệu gốc khớp 70/70 con số của báo cáo v15 ([chuong_4_test.md](chuong_4_test.md), lần chạy `chinh_thuc_cloud_20261026`). |
| 2 | Bốn mô hình (UserCF, ItemCF, SVD, PureSVD) và hai mốc Random, Popularity | **Đạt** | Đã tinh chỉnh 48 cấu hình trên validation, khóa `lock.json`, mở test một lần. NDCG@10 test: PureSVD 0,182780; Popularity 0,068775; SVD 0,062650; UserCF 0,018850; ItemCF 0,017502; Random 0,000597 ([test/metrics.csv](chinh_thuc_cloud_20261026/test/metrics.csv)). Lưu ý: SVD, UserCF, ItemCF thấp hơn Popularity. |
| 3 | M1 (giảm thiên lệch phổ biến), M2 (người dùng mới), có ablation | **Đạt một phần** | **M1 đạt**: so với nền PureSVD, ARP@10 giảm 15,69%, NDCG@10 giảm 0,001364 nhưng không có ý nghĩa (p Holm 0,608) ([chuong_4_test.md](chuong_4_test.md)). **M2 xây và đánh giá đúng giao thức nhưng không đạt giả thuyết**: ở N = 3, M2 thấp hơn Popularity 0,008719 NDCG@10, KTC 95% [−0,026749; 0,008436], p Holm 0,857; M2 đa dạng hơn rõ (ARP 294,91 → 129,10) ([chuong_4_m2.md](chuong_4_m2.md)). Ablation: lưới 12 điểm λ, β của M1 và các nhánh nội dung / ItemCF của M2 đều đã có. |
| 4 | Độ đo P/R/NDCG, Coverage, Gini, ARP, Novelty, ILD, RMSE | **Đạt** | Đủ 8 chỉ số xếp hạng ở K = 5/10/20 cho 8 mô hình, kèm Wilcoxon, Holm và bootstrap ([chuong_4_test.md](chuong_4_test.md)). RMSE chỉ là bảng phụ (UserCF 0,9327; ItemCF 0,9610; SVD 1,2713), không dùng để chọn mô hình. |
| 5 | API FastAPI, giao diện, tài liệu, tái lập, xử lý đầu vào lỗi | **Đạt một phần** | **Đã có**: backend FastAPI và frontend Next.js (5 trang) đã push. API qua gói phát hành tái lập đúng kết quả test: 12 dòng người dùng có sẵn và 9 dòng M2, 0 dòng lệch, sai số ≤ 1e-12 ([check_release.json](chuong_5/check_release.json)). Độ trễ trung vị `POST /recommend` 2,8–9,1 ms trên máy cục bộ ([latency.json](chuong_5/latency.json)). Gói nạp kiểm mã băm, từ chối nếu lệch; user không tồn tại trả 404; hồ sơ rỗng chuyển Popularity với `fallback_used = true` ([chuong_5_backend.md](chuong_5_backend.md)). **Còn thiếu**: chưa deploy (cần tạo tài khoản host); báo cáo mục 5.3 vẫn ghi Streamlit là giao diện chính; chưa đối chiếu từng ca kiểm thử T01–T09 của bản viết trước. |

## 2. Năm câu hỏi nghiên cứu

| RQ | Câu hỏi | Trạng thái | Câu trả lời ngắn |
| --- | --- | --- | --- |
| RQ1 | So sánh các mô hình | **Trả lời được** | Trong sáu mô hình đối sánh, PureSVD tốt nhất, hơn Popularity 0,1140 NDCG@10 (KTC [0,1064; 0,1219]). Ba mô hình UserCF, ItemCF, SVD thấp hơn Popularity ([chuong_4_test.md](chuong_4_test.md)). |
| RQ2 | Ảnh hưởng của độ dài lịch sử | **Không kết luận được** | Trên test, ba nhóm có 37 / 1.816 / 2 người (dưới / đúng / trên 40 nghệ sĩ), vì gần như mọi người có đúng 40 nghệ sĩ trong train. Hai nhóm nhỏ quá ít người ([history_groups.csv](chinh_thuc_cloud_20261026/test/history_groups.csv)). Báo cáo cần ghi đây là hạn chế của dữ liệu. |
| RQ3 | M1 so với mô hình nền | **Trả lời được** | Giảm thiên lệch phổ biến rõ, độ chính xác không đổi có ý nghĩa. |
| RQ4 | M2 cho người dùng mới | **Trả lời được, kết quả âm** | Không có bằng chứng M2 chính xác hơn Popularity; ưu thế trên validation (187 người) không lặp lại trên 189 người để dành. |
| RQ5 | Ứng dụng có nhất quán với kết quả offline | **Trả lời được** | [check_release.json](chuong_5/check_release.json): 0 dòng lệch trên 21 dòng so sánh. |

## 3. Phần làm thêm ngoài mục tiêu ban đầu

| Hạng mục | Kết quả | Nguồn |
| --- | --- | --- |
| Implicit ALS (thực nghiệm mở rộng) | Cao nhất trên test, NDCG@10 0,217453, hơn PureSVD 0,034673 (p Holm 3,36e−25). Không thuộc phép so sánh chính. | [chuong_4_test.md](chuong_4_test.md) |
| H1 (khử thiên lệch phổ biến bằng phổ, trên ALS) | **Không qua cổng validation ở vòng 1**: 18 cấu hình, seed 42. Phạt phổ biến trực tiếp tốt hơn H1 (β = 0,25: NDCG@10 0,1949, 64,2% nghệ sĩ ngoài nhóm đầu; H1 γ₀ = 0,5: 0,1930 và 61,0%). Chưa chạy seed 43/44 và test; nhóm đã chọn dừng H2–H4. | [h1_vong_1.md](h1_vong_1.md) |
| Giao diện Next.js thay cho Streamlit | Có so sánh PureSVD / M1 cạnh nhau, công tắc M1 trong 12 điểm lưới validation, trang luồng hoạt động và trang kết quả | [chuong_5_frontend.md](chuong_5_frontend.md) |

## 4. Việc còn lại để hoàn tất khóa luận

1. Viết Chương 5 của báo cáo (hiện chỉ có tiêu đề), đổi mục 5.3 sang Next.js.
2. Phân tích lỗi từng trường hợp (mục 4.9.2).
3. Deploy demo, nếu cần trình diễn qua mạng (cần tài khoản host).
4. Ghi kết quả H1 vào báo cáo như một hướng đã thử, hoặc bỏ hẳn (cần nhóm quyết).
5. Thêm `pandas-stubs`, `scipy-stubs`, `types-PyYAML` vào `pyproject.toml` để CI chạy mypy được (đang chờ duyệt).
