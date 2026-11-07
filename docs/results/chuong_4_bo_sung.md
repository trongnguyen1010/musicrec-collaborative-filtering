# Chương 4: phân tích bổ sung theo góp ý GVHD ngày 06/11/2026

Ngày chạy: 07/11/2026, trên máy cá nhân của nhóm (Windows 11, Intel Core i5-11300H 3,10 GHz, 8 luồng logic, 16.856.203.264 byte RAM; Python 3.11.9; numpy 2.4.6, scipy 1.17.1, pandas 2.3.3, pyarrow 19.0.1, implicit 0.7.3, matplotlib 3.11.2; một luồng BLAS). Commit gốc `60b175c`, cây làm việc có các tệp mới chưa commit liệt kê ở mục 7.

Tài liệu này ghi các phân tích GVHD yêu cầu thêm cho Chương 4 ([góp ý](../bao-cao/GOP_Y_GVHD_06-11-2026.md), ý G09–G18). **Không có cấu hình nào được chọn lại.** Mọi mô hình là mô hình đã khóa trong `outputs/chinh_thuc_cloud_20261026/chuong_4/test/lock.json` của lần chạy chính thức ([chuong_4_test.md](chuong_4_test.md)).

## Tóm tắt

- Máy cá nhân chỉ có bảng chỉ số tổng hợp của tập test, không có điểm từng người dùng. Nhóm chấm lại test bằng các mô hình đã khóa: PureSVD, M1, ALS nạp lại từ tệp đã lưu; UserCF, ItemCF, SVD huấn luyện lại với cấu hình đã khóa (NDCG@10 validation trùng tới mọi chữ số với lần chạy chính thức). **24 chỉ số × 8 mô hình khớp bảng chính thức, lệch tối đa 7,1e−15**; bốn cặp kiểm định khai báo trước cho đúng giá trị cũ. Vì vậy dữ liệu từng người dùng dùng được cho hình và bảng mới.
- **Lỗi số liệu cũ**: NDCG@10 của PureSVD log-count (k = 32) ghi ở v16 mục 3.6.4 và bản GVHD Bảng 4.4 là 0,153543, nhưng [data-card.md](../data-card.md) ghi **0,1545766607**. Không tìm thấy nguồn cho 0,153543. Bản v17 sửa thành 0,154577.
- **Số liệu chữ xanh của GVHD cần sửa**: trên train có 1.831 người đúng 40 tương tác, 44 người dưới 40, 2 người trên 40 (GVHD ghi 1.829 và 48). Con số 1.829 là số người có đúng 50 nghệ sĩ trong dữ liệu gốc.
- SVD có độ lệch chạy đủ 100 vòng: NDCG@10 validation đạt đỉnh ở vòng 2 rồi giảm, trong khi RMSE train và validation tiếp tục giảm. Xem mục 2.
- Theo mức ưa chuộng nghệ sĩ phổ biến (ba nhóm bằng nhau), mọi mô hình kém hẳn ở nhóm thấp. Ở nhóm thấp, ItemCF vượt Popularity và M1 vượt PureSVD.
- M1: ILD theo thẻ (thước đo không nằm trong hàm lựa chọn) chỉ tăng 0,0107, nhỏ hơn mức tăng ILD theo người nghe (0,0187).
- M2: ở N = 1, 22,75% yêu cầu chuyển hẳn về Popularity, đúng bằng tỷ lệ người dùng có nghệ sĩ duy nhất nằm ngoài ánh xạ (43/189).

## 1. Chấm lại test và đối chiếu

Lệnh (từ thư mục gốc, venv dự án):

```bash
.venv/Scripts/python.exe -B scripts/rebuild_locked_runs.py --representations-run outputs/chinh_thuc_cloud_20261026/chuong_3/run/representations --tuning-summary docs/results/chinh_thuc_cloud_20261026/tuning_summary.json --output-dir outputs/chinh_thuc_cloud_20261026/chuong_4_bo_sung/tuning
.venv/Scripts/python.exe -B scripts/preprocess.py --output-dir outputs/chinh_thuc_cloud_20261026/chuong_4_bo_sung/cleaning
.venv/Scripts/python.exe -B scripts/report_ch4_extras.py
```

| Kiểm tra | Kết quả | Nguồn |
| --- | --- | --- |
| UserCF, ItemCF, SVD huấn luyện lại, NDCG@10 validation | 0,017488321672763516; 0,015364109803005505; 0,060665866476874455; trùng tuning_summary.json | `chuong_4_bo_sung/tuning/rebuild_report.json` |
| Làm sạch chạy lại | `interactions.parquet` SHA-256 `e2ddee2f…1d65`, trùng [chuong_3.md](chuong_3.md) | `chuong_4_bo_sung/cleaning/` |
| 8 chỉ số × K = 5, 10, 20 × 8 mô hình so với test/metrics.csv | lệch tối đa 7,1e−15 (UserCF, ItemCF), các mô hình khác ≤ 1,8e−15 | `phan_tich/doi_chieu_chinh_thuc.json` |
| 4 cặp kiểm định khai báo trước | trùng statistics_ndcg_at_10.json | `phan_tich/kiem_dinh_bo_sung.json` |
| M1 đầy đủ fit lại từ PureSVD đã khóa | danh sách trùng hoàn toàn checkpoint M1 đã khóa (script dừng nếu khác) | `report_ch4_extras.py` |

Đường dẫn trong bảng tính từ `outputs/chinh_thuc_cloud_20261026/`.

## 2. Đường học SVD 100 vòng (Hình 4.3)

Cấu hình đã khóa (d = 16, η = 0,001925, λreg = 0,01025, seed 42), chạy đủ 100 vòng với patience = 100, chỉ đọc validation. Hàm `svd_curve` trong `scripts/rebuild_locked_runs.py` dùng đúng callback NDCG@10 của `run_baseline.py` và thêm RMSE trên 8.142 cặp validation có nghệ sĩ trong danh mục. Bảy vòng đầu trùng từng chữ số với lần chạy có dừng sớm (chênh lệch tuyệt đối lớn nhất 0,0). Thời gian chạy khoảng 30 phút. Nguồn: `chuong_4_bo_sung/tuning/svd_curve/learning_curve.csv` (bản sao trong `bo_sung/learning_curve.csv`).

| Vòng | RMSE train | RMSE validation | NDCG@10 validation |
| --- | --- | --- | --- |
| 1 | 1,3361 | 1,3377 | 0,059015 |
| **2 (chọn)** | 1,2700 | 1,2757 | **0,060666** |
| 7 | 1,0426 | 1,0683 | 0,052424 |
| 20 | 0,8341 | 0,8909 | 0,040210 |
| 51 (RMSE validation thấp nhất) | 0,7588 | 0,8601 | 0,033594 |
| 100 | 0,6465 | 0,8750 | 0,029199 |

Kết luận: đường thực tế khớp đoạn diễn giải GVHD viết sẵn ở mục 4.4. Sai số bình phương (kể cả trên validation, tới vòng 51) giảm trong khi NDCG@10 giảm gần một nửa. Báo cáo dùng hai biểu đồ xếp chồng chung trục vòng (không dùng hai trục tung).

## 3. Kiểm định bổ sung và khoảng tin cậy

Bootstrap 1.000 lần theo người dùng, seed 42; Wilcoxon hai phía, bỏ chênh lệch 0. Họ bổ sung (PureSVD so với 5 mô hình đối sánh còn lại) hiệu chỉnh Holm riêng. Nguồn: `phan_tich/kiem_dinh_bo_sung.json`.

| PureSVD − B | Chênh lệch | KTC 95% | p Holm (họ bổ sung) |
| --- | --- | --- | --- |
| Random | +0,182183 | [0,172935; 0,192010] | 1,92e−169 |
| Popularity | +0,114005 | [0,105569; 0,121757] | 4,73e−121 |
| UserCF | +0,163930 | [0,154577; 0,173102] | 5,74e−157 |
| ItemCF | +0,165278 | [0,155392; 0,174882] | 3,76e−146 |
| SVD có độ lệch | +0,120130 | [0,111992; 0,128248] | 1,52e−127 |

KTC của Popularity và SVD trong họ bổ sung khác chút với họ khai báo trước vì chuỗi bootstrap khác; p Wilcoxon không đổi.

| Mô hình | NDCG@10 | KTC 95% |
| --- | --- | --- |
| Random | 0,000597 | [0,000212; 0,001083] |
| Popularity | 0,068775 | [0,063152; 0,075062] |
| UserCF | 0,018850 | [0,016238; 0,021421] |
| ItemCF | 0,017502 | [0,014666; 0,020507] |
| SVD có độ lệch | 0,062650 | [0,056686; 0,068990] |
| PureSVD | 0,182780 | [0,172556; 0,192735] |
| M1 | 0,181416 | [0,171183; 0,191158] |
| ALS (mở rộng) | 0,217453 | [0,206797; 0,227539] |

## 4. Phân tích theo người dùng

PureSVD − Popularity trên 1.855 người: 925 tăng (49,9%), 791 bằng (42,6%, trong đó 765 người bằng 0 ở cả hai), 139 giảm (7,5%). Nguồn: `phan_tich/chenh_lech_puresvd_popularity.json`.

Ba nhóm ưa chuộng nghệ sĩ phổ biến (số người nghe trung bình trên train của các nghệ sĩ trong lịch sử train; chia theo thứ hạng thành ba nhóm 618/618/619). NDCG@10 test, nguồn `phan_tich/nhom_uu_pho_bien.csv`:

| Mô hình | Thấp (1,1–45,0) | Trung bình (45,0–84,3) | Cao (84,3–262,2) |
| --- | --- | --- | --- |
| Popularity | 0,009850 | 0,035008 | 0,161317 |
| UserCF | 0,007083 | 0,013307 | 0,036132 |
| ItemCF | 0,021650 | 0,016946 | 0,013915 |
| SVD có độ lệch | 0,009252 | 0,029663 | 0,148895 |
| PureSVD | 0,072375 | 0,169222 | 0,306543 |
| M1 | 0,081042 | 0,169183 | 0,293841 |
| ALS (mở rộng) | 0,125206 | 0,202576 | 0,324405 |

Chưa kiểm định theo nhóm; báo cáo ghi là phân tích mô tả.

## 5. M1 và M2

Biến thể M1 trên test (phân tích bổ sung, test đã mở trước đó; không chọn lại). ILD theo thẻ: côsin TF-IDF thẻ theo cách dựng của M2 nhưng trên toàn bộ train (2.778 thẻ, 5.650/15.398 nghệ sĩ có thẻ), chỉ cặp nghệ sĩ đều có thẻ; 1.855/1.855 danh sách đóng góp. Nguồn `phan_tich/m1_bien_the_test.csv`, `m1_kiem_dinh_bien_the.json`.

| Biến thể | NDCG@10 | ARP | Bao phủ | Gini | ILD | ILD theo thẻ | p Holm so với nền (họ 3 cặp) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Nền (λ = 1, β = 0) | 0,182780 | 174,21 | 1,86% | 0,9923 | 0,7948 | 0,6953 | - |
| Chỉ đa dạng (0,75; 0) | 0,181474 | 171,34 | 1,94% | 0,9921 | 0,8064 | 0,7094 | 0,238 |
| Chỉ phạt phổ biến (1; 0,5) | 0,183171 | 156,72 | 2,16% | 0,9905 | 0,7990 | 0,6904 | 1 |
| M1 đầy đủ (0,75; 0,5) | 0,181416 | 146,87 | 2,94% | 0,9892 | 0,8135 | 0,7060 | 1 (họ khai báo trước: 0,608) |

ILD theo thẻ của danh sách Popularity: 0,6177. Ví dụ danh sách trước/sau M1 của người dùng 2, 9 và một người nữa: `phan_tich/m1_vi_du.csv` (lấy ba người đầu tiên theo mã có ít nhất 3 nghệ sĩ khác nhau trong top-10).

Đường xử lý của M2 trên 189 người để dành (cùng hồ sơ với lần chấm chính thức). Nguồn `phan_tich/m2_duong_xu_ly.csv`:

| Thống kê | N = 0 | N = 1 | N = 3 | N = 5 |
| --- | --- | --- | --- | --- |
| Có điểm nội dung (%) | 0 | 66,14 | 89,42 | 97,88 |
| Chuyển hoàn toàn về phổ biến (%) | 100 | 22,75 | 3,70 | 0 |
| Nghệ sĩ đầu vào ngoài ánh xạ | 0 / 0 | 43 / 189 | 111 / 567 | 158 / 945 |

## 6. Tệp và hình

Hình 4.1–4.7 (PNG 300 dpi) và CSV dữ liệu vẽ: `outputs/chinh_thuc_cloud_20261026/chuong_4_bo_sung/phan_tich/hinh/`. Bản sao (1,1 MB, gồm JSON, CSV kết quả và hình) trong [chinh_thuc_cloud_20261026/bo_sung/](chinh_thuc_cloud_20261026/bo_sung/).

Hình 4.3 dùng hai biểu đồ xếp chồng chung trục vòng thay cho một biểu đồ hai trục tung như GVHD gợi ý, để mỗi đại lượng có thang riêng mà không bị đọc nhầm.

## 7. Báo cáo v17 và tệp mới

Báo cáo [v17](../bao-cao/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_v17_07-11-2026.docx) dựng từ bản góp ý của GVHD: thay toàn bộ Chương 4 (16 bảng, 7 hình) theo khung của GVHD, sửa 0,153543 thành 0,154577 ở mục 3.6.4, các chương khác giữ nguyên chữ đỏ, chữ xanh của GVHD để xử lý sau. Trường Word (mục lục, danh mục bảng, hình, số chú thích) đã cập nhật bằng Word; bản xuất PDF kiểm tra 111 trang.

Tệp mới: `scripts/rebuild_locked_runs.py`, `scripts/report_ch4_extras.py`, `docs/bao-cao/nguon_v17/` (dựng báo cáo v17).
