# Chương 4 – bổ sung lần 2 (góp ý GVHD, kế hoạch 10/11/2026, mục 2 và 5)

Trạng thái (10/11/2026): **Giai đoạn 1 đã chạy đầy đủ**, gồm E-T, E7, E-G, E-S (kể cả ALS, chạy sau khi được duyệt), E-B, E-C, E-D và E-P. Giai đoạn 2 viết lại Chương 2–4 trong bản báo cáo v19. Kết quả đã khóa trong `outputs/chinh_thuc_cloud_20261026/` và `docs/results/chinh_thuc_cloud_20261026/{test,m2,bo_sung}` không bị ghi đè.

Kết quả thô nằm ở `outputs/chuong_4_bo_sung_2/` (Git bỏ qua theo `.gitignore`). Bản sao các tệp nhỏ dùng cho báo cáo nằm ở `docs/results/chinh_thuc_cloud_20261026/bo_sung_2/<thực nghiệm>/`. Các đường dẫn `outputs/...` dưới đây có bản sao cùng tên trong thư mục đó.

## Tóm tắt các kết luận bị ảnh hưởng

- **RQ1 – E7 làm đổi kết luận.** Khi UserCF và ItemCF chấm điểm theo kiểu top-N (cộng dồn, không chia), cả hai cao hơn PureSVD có ý nghĩa trên test. UserCF: 0,193668 so với 0,182780, Holm p = 0,00233. ItemCF: 0,193973, Holm p = 0,000832. Cả hai cao hơn Popularity rất xa. Các câu "PureSVD cao nhất trong sáu mô hình đối sánh" và "UserCF, ItemCF thấp hơn Popularity" chỉ còn đúng với **cách chấm trung bình có trọng số** đã khóa. Implicit ALS (0,217453) vẫn cao hơn cả hai. Đây là phân tích bổ sung sau khi khóa cấu hình, không thay mô hình đã khóa.
- **M2 – E-G làm đổi kết luận.** Với tập đích Given-N (mọi nghệ sĩ còn lại của người dùng, trung bình 39,47 nghệ sĩ trong danh mục ở N = 3), M2 cao hơn Popularity có ý nghĩa ở so sánh chính N = 3 (+0,063028, Holm p = 0,0011) và ở N = 5. Trong giao thức cũ (chỉ cặp test), M2 thấp hơn Popularity và không có ý nghĩa.
- **M1 – E-B cho thấy cấu hình khóa nằm ở biên lưới β.** Nếu áp dụng cùng quy tắc chọn trên lưới mở rộng thì cấu hình được chọn sẽ là λ = 0,75, β = 0,75 thay vì β = 0,5. TOST (E-T) xác nhận M1 tương đương PureSVD trên test ở biên ±5%.

Máy chạy (mọi lần chạy dưới đây): Intel Core i5-11300H @ 3,10 GHz, 4 nhân / 8 luồng, RAM 15,7 GB, Windows 11 (10.0.26200); Python 3.11.9, numpy 2.4.6, scipy 1.17.1, pandas 2.3.3, pyarrow 19.0.1; BLAS 1 luồng. Mỗi `metrics.json` trong các thư mục kết quả ghi lại cấu hình máy, phiên bản thư viện, git SHA và git status.

## E-T (BƯỚC 1): thống kê lại với bootstrap dùng chung

### Thay đổi phương pháp

- Trước đây `scripts/test_statistics.py`, `scripts/report_ch4_extras.py`, `scripts/evaluate_m2_test.py` dùng một bộ sinh `rng` chạy tiếp qua từng cặp, nên mỗi cặp có một chuỗi bootstrap riêng (chỉ cặp đầu tiên dùng đúng ma trận của seed 42). Nay mọi cặp trên cùng một tập người dùng dùng **chung một ma trận chỉ số** `resample_indices(n, 1000, 42)` (`musicrec.evaluation.inference`). Ma trận này trùng với lần rút đầu tiên của cách cũ, nên cặp đầu mỗi bảng giữ nguyên CI.
- Mô-đun mới `src/musicrec/evaluation/paired.py`: chênh lệch trung bình, CI 95% và **CI 90%** bootstrap phân vị, Wilcoxon hai phía (bỏ d = 0), W+, W−, **r_rb = (W+ − W−)/(W+ + W−)** trên cùng các d ≠ 0, và **TOST** theo quy tắc khoảng: tương đương khi CI 90% nằm trọn trong (−δ; δ).
- Chênh lệch trung bình và p Wilcoxon/Holm không phụ thuộc bootstrap: `scripts/compare_statistics.py` kiểm tra chúng **trùng khớp tuyệt đối** với các tệp đã khóa (21/21 cặp) và chỉ CI thay đổi. Dịch chuyển lớn nhất của một cận CI 95% là 0,001270. **Không cặp nào đổi kết luận theo CI 95%** (chứa hay không chứa 0).

### Cách tạo lại

```
.venv/Scripts/python.exe scripts/evaluate_m2_test.py --m2-run outputs/chinh_thuc_cloud_20261026/chuong_4/m2_tuning --output-dir outputs/chuong_4_bo_sung_2/thong_ke/m2_test
.venv/Scripts/python.exe scripts/report_ch4_extras.py --output-dir outputs/chuong_4_bo_sung_2/thong_ke/phan_tich
.venv/Scripts/python.exe scripts/compare_statistics.py
```

Kiểm tra tái lập: chấm lại M2 khớp `docs/results/chinh_thuc_cloud_20261026/m2/test/metrics.csv` 48/48 dòng, sai khác 0; chấm lại tám mô hình test khớp `test/metrics.csv` với sai khác lớn nhất 7,1e-15 (`phan_tich/doi_chieu_chinh_thuc.json`); `predeclared_equal_official = true`. Thời gian: M2 45 s, `report_ch4_extras.py` 2 phút 18 s.

### TOST M1 − PureSVD (NDCG@10, tập kiểm thử, 1.855 người dùng)

Nguồn: `outputs/chuong_4_bo_sung_2/thong_ke/phan_tich/kiem_dinh_bo_sung.json`, khóa `m1_pure_svd_equivalence`.

| Đại lượng | Giá trị |
|---|---|
| NDCG@10 nền PureSVD | 0,182780 (đúng như bản nháp ghi 0,182780) |
| δ = 0,05 × 0,182780 | 0,009139 |
| Chênh lệch M1 − PureSVD | −0,001364 |
| CI 90% (bootstrap dùng chung) | [−0,003641; 0,000888] |
| CI 95% | [−0,004052; 0,001258] (cũ: [−0,004124; 0,001244]) |
| r_rb | −0,0215 (755 cặp d ≠ 0) |
| p Holm (họ khai báo trước) | 0,608 |
| Kết luận TOST | **Tương đương** ở biên ±5%: CI 90% nằm trọn trong (−0,009139; 0,009139) |

### Bảng 4.8 (kiểm định NDCG@10 test) – mới so với cũ

Nguồn mới: `outputs/chuong_4_bo_sung_2/thong_ke/doi_chieu_thong_ke.csv` (cột `_cu` lấy từ `docs/results/chinh_thuc_cloud_20261026/test/statistics_ndcg_at_10.json` và `bo_sung/kiem_dinh_bo_sung.json`).

| Cặp (A − B) | Họ | Chênh lệch | CI 95% cũ | CI 95% mới | CI 90% mới | r_rb | p Holm |
|---|---|---|---|---|---|---|---|
| PureSVD − Popularity | Khai báo trước | 0,114005 | [0,106354; 0,121929] | [0,106354; 0,121929] | [0,107272; 0,120525] | 0,8280 | 1,42e-120 |
| SVD − PureSVD | Khai báo trước | −0,120130 | [−0,128123; −0,111630] | [−0,128123; −0,112136] | [−0,126908; −0,113326] | −0,8533 | 3,04e-127 |
| M1 − PureSVD | Khai báo trước | −0,001364 | [−0,004124; 0,001244] | [−0,004052; 0,001258] | [−0,003641; 0,000888] | −0,0215 | 0,608 |
| ALS − PureSVD | Khai báo trước | 0,034673 | [0,027812; 0,041257] | [0,027694; 0,041325] | [0,029047; 0,040104] | 0,3509 | 3,36e-25 |
| PureSVD − Random | Bổ sung | 0,182183 | [0,172935; 0,192010] | [0,172935; 0,192010] | [0,174318; 0,190376] | 0,9976 | 1,92e-169 |
| PureSVD − Popularity | Bổ sung | 0,114005 | [0,105569; 0,121757] | [0,106354; 0,121929] | [0,107272; 0,120525] | 0,8280 | 4,73e-121 |
| PureSVD − UserCF | Bổ sung | 0,163930 | [0,154577; 0,173102] | [0,154661; 0,173102] | [0,156389; 0,172017] | 0,9487 | 5,74e-157 |
| PureSVD − ItemCF | Bổ sung | 0,165278 | [0,155392; 0,174882] | [0,155348; 0,175501] | [0,157214; 0,173942] | 0,9032 | 3,76e-146 |
| PureSVD − SVD | Bổ sung | 0,120130 | [0,111992; 0,128248] | [0,112136; 0,128123] | [0,113326; 0,126908] | 0,8533 | 1,52e-127 |

Họ Holm (`kiem_dinh_bo_sung.json`, khóa `holm_families`): họ **khai báo trước 4 cặp**, họ **bổ sung 5 cặp**, hiệu chỉnh Holm riêng trong từng họ. **Hai cặp bị lặp giữa hai phần**: PureSVD − Popularity (cùng chiều) và SVD − PureSVD / PureSVD − SVD (ngược dấu). Cùng p thô, nhưng p Holm khác nhau vì thuộc họ khác. Trong bảng cũ, PureSVD − Popularity có hai CI 95% khác nhau ([0,106354; 0,121929] và [0,105569; 0,121757]), và hai CI của cặp SVD/PureSVD không đối xứng nhau. Lý do là mỗi lần lặp lại rút một bootstrap mới. Với ma trận dùng chung, hai dòng lặp nay có CI trùng nhau (hoặc đối xứng đúng). Bảng chỉ còn 7 cặp khác nhau.

**Phương án đã chọn (người dùng duyệt ngày 10/11/2026), chưa sửa Word:** Bảng 4.8 mới giữ 4 dòng khai báo trước. Phần bổ sung chỉ còn 3 dòng: PureSVD − Random, PureSVD − UserCF, PureSVD − ItemCF. Hai dòng PureSVD − Popularity và PureSVD − SVD bị bỏ vì trùng với dòng khai báo trước (SVD − PureSVD là cùng cặp, ngược dấu). Bảng có 7 dòng, kèm ghi chú: "Hiệu chỉnh Holm của họ bổ sung vẫn tính trên đủ 5 cặp PureSVD − {Random, Popularity, UserCF, ItemCF, SVD}; hai cặp trùng với phần khai báo trước không in lại, p Holm của chúng trong họ bổ sung lần lượt là 4,73e-121 và 1,52e-127." Số liệu ba dòng còn lại lấy từ bảng trên (cột "mới").

### CI của NDCG@10 trung bình (Bảng 4.7), M1 biến thể (Bảng 4.11), M2 (Bảng 4.15)

- Bảng 4.7: `outputs/chuong_4_bo_sung_2/thong_ke/doi_chieu_ci_trung_binh.csv`. Ví dụ PureSVD 0,182780, CI 95% cũ [0,172556; 0,192735] → mới [0,173448; 0,192598]; CI 90% [0,174855; 0,190941].
- Bảng 4.11 (`phan_tich/m1_kiem_dinh_bien_the.json`): chỉ đa dạng − nền −0,001306, CI 95% [−0,002610; −0,000068] (không đổi, là cặp đầu), r_rb −0,0956, Holm 0,238; chỉ phạt phổ biến − nền 0,000391, CI [−0,001568; 0,002309], r_rb 0,0310; M1 đầy đủ − nền như dòng M1 − PureSVD ở trên.
- Bảng 4.15 (`thong_ke/m2_test/statistics_ndcg_at_10.json`, 187 người): so sánh chính N = 3, M2 − Popularity −0,008719, CI 95% cũ [−0,026749; 0,008436] → mới [−0,026619; 0,008400], CI 90% [−0,023997; 0,005806], r_rb −0,2158, Holm 0,857. Các kết luận về CI 95% không đổi. Toàn bộ 9 cặp có trong `doi_chieu_thong_ke.csv`.

## E7 – láng giềng top-N (chạy đầy đủ; phân tích bổ sung sau khi khóa cấu hình)

**Mã.** `UserCFRecommender` và `ItemCFRecommender` có thêm hai tham số:
- `aggregation`: "mean" (mặc định, đúng mô hình đã khóa) hoặc "sum".
- `representation`: "proxy" cho mean; "binary" hoặc "log_count" = log2(1 + lượt nghe) cho sum.

Ở chế độ sum, cùng biểu diễn x được dùng cho cả cosine lẫn điểm:
- UserCF: s_ui = Σ_{v∈N_L(u)} sim(u,v)·x_vi.
- ItemCF: s_ui = Σ_{j∈H_u∩N_L(i)} sim(i,j)·x_uj.
- Ứng viên không có hỗ trợ được điểm 0.

`state.json` của chế độ mặc định không đổi. Lưới riêng nằm ở `configs/e7_topn_neighbors.yaml` (40 cấu hình); `configs/tuning.yaml` không đổi.

**Cách tạo lại:** `scripts/run_e7_topn.py validation|select|test|stats --output-dir outputs/chuong_4_bo_sung_2/e7`. Lưới validation mất 5 phút 42 giây, chấm test 18 giây.

**Validation** (`e7/validation_summary.csv`, seed 42, 1.865 người có đích). NDCG@10 nằm trong khoảng 0,152677–0,173886 với UserCF và 0,142857–0,174212 với ItemCF. Mô hình mean đã khóa chỉ đạt 0,017488 (UserCF) và 0,015364 (ItemCF). Cấu hình thắng (`e7/selection.json`):
- UserCF: log_count, L = 20, γ = 10, NDCG@10 = 0,173886.
- ItemCF: log_count, L = 100, γ = 10, NDCG@10 = 0,174212.

**Test**, chấm một lần sau khi khóa (`e7/test/lock.json`, `e7/test/metrics.csv`, K = 10):

| Mô hình | NDCG@10 | Precision | Recall | Bao phủ | Gini | ARP | ILD |
|---|---|---|---|---|---|---|---|
| UserCF top-N | 0,193668 | 0,092776 | 0,207242 | 0,068061 | 0,986021 | 169,37 | 0,765391 |
| ItemCF top-N | 0,193973 | 0,090782 | 0,201752 | 0,063515 | 0,989977 | 183,24 | 0,720604 |

**Kiểm định** (`e7/test/statistics_ndcg_at_10.json`): 1.855 người dùng, bootstrap dùng chung chỉ số, Holm trong họ E7 gồm 4 cặp; CI 90% có trong tệp.

| Cặp | Chênh lệch | CI 95% | r_rb | p Holm |
|---|---|---|---|---|
| UserCF top-N − Popularity | 0,124893 | [0,117195; 0,132430] | 0,8800 | 2,39e-143 |
| UserCF top-N − PureSVD | 0,010888 | [0,004898; 0,017272] | 0,1040 | 0,00233 |
| ItemCF top-N − Popularity | 0,125198 | [0,117513; 0,133264] | 0,8849 | 2,44e-141 |
| ItemCF top-N − PureSVD | 0,011193 | [0,005394; 0,017109] | 0,1231 | 0,000832 |

CI 95% của NDCG@10 trung bình: UserCF top-N [0,184070; 0,203222], ItemCF top-N [0,184401; 0,203577]. Để so sánh, Implicit ALS đã khóa đạt 0,217453 trên test.

**Kết luận RQ1 thay đổi** (xem phần tóm tắt). Đề xuất cho báo cáo: giữ bảng chính với cấu hình đã khóa và thêm một mục "phân tích bổ sung sau khi khóa cấu hình" cho E7. Mục này cần nêu rõ: kết quả kém của UserCF/ItemCF ở Chương 4 đến từ cách chấm trung bình có trọng số (đó là dự đoán điểm, không phải xếp hạng top-N), không phải do bản chất phương pháp láng giềng.

## E-G – Given-N theo tập đích (chạy đầy đủ)

`scripts/evaluate_m2_test.py --target-mode all_but_profile --output-dir outputs/chuong_4_bo_sung_2/eg`; chạy mất 19 giây.
- Đích: T_u^N = (train ∪ validation ∪ test của u) \ hồ sơ N, giao danh mục nhóm học; chỉ che N nghệ sĩ được cung cấp.
- Giữ nguyên M2 đã khóa (α = 0,75, n_min = 10), bốn phương án và chín cặp so sánh, Holm trên 9 cặp.
- Cả 189 người để dành đều có đích hợp lệ ở mọi N.

**Số đích trung bình mỗi người** (tính từ `eg/n_*/m2/evaluation.json`):

| N | Tổng số đích | Trong danh mục | Trung vị trong danh mục |
|---|---|---|---|
| 0 | 49,43 | 41,88 | 45 |
| 1 | 48,43 | 41,11 | 44 |
| 3 | 46,43 | 39,47 | 42 |
| 5 | 44,43 | 37,71 | 40 |

**NDCG@10** (`eg/metrics.csv`; ở N = 0 mọi phương án đều bằng Popularity):

| Phương án | N = 0 | N = 1 | N = 3 | N = 5 |
|---|---|---|---|---|
| Popularity | 0,252612 | 0,249417 | 0,243800 | 0,234496 |
| Chỉ ItemCF | 0,252612 | 0,209123 | 0,171056 | 0,142708 |
| Chỉ nội dung thẻ | 0,252612 | 0,141835 | 0,222909 | 0,264148 |
| M2 | 0,252612 | 0,236658 | 0,306828 | 0,291191 |

**Kiểm định** (`eg/statistics_ndcg_at_10.json`, 189 người):

| N | Cặp | Chênh lệch | CI 95% | r_rb | p Holm |
|---|---|---|---|---|---|
| 1 | M2 − Popularity | −0,012759 | [−0,045589; 0,018375] | −0,0363 | 0,735 |
| 1 | M2 − Chỉ nội dung | 0,094823 | [0,072042; 0,120739] | 0,9475 | 2,04e-12 |
| 1 | M2 − Chỉ ItemCF | 0,027535 | [−0,009146; 0,063798] | 0,1817 | 0,171 |
| **3** | **M2 − Popularity (chính)** | **0,063028** | **[0,025660; 0,098611]** | **0,3411** | **0,0011** |
| 3 | M2 − Chỉ nội dung | 0,083919 | [0,062107; 0,107632] | 0,6179 | 7,52e-10 |
| 3 | M2 − Chỉ ItemCF | 0,135772 | [0,100150; 0,172312] | 0,6305 | 1,08e-10 |
| 5 | M2 − Popularity | 0,056696 | [0,014418; 0,095239] | 0,2698 | 0,00887 |
| 5 | M2 − Chỉ nội dung | 0,027044 | [−0,002198; 0,056292] | 0,1774 | 0,138 |
| 5 | M2 − Chỉ ItemCF | 0,148484 | [0,116071; 0,178419] | 0,7289 | 1,15e-14 |

**Kết luận về M2 thay đổi.** Với đích là các cặp test (Bảng 4.13–4.15 cũ, khoảng 5 đích mỗi người), M2 không hơn Popularity. Với đích Given-N theo mục 3.14, M2 hơn Popularity có ý nghĩa ở N = 3 và N = 5; ở N = 1 thì không. Hai giao thức đo hai câu hỏi khác nhau, nên báo cáo cần nêu rõ giao thức nào là chính.

## E-S – độ nhạy quanh biên lưới (chỉ validation, seed 42)

Cấu hình `configs/e_s_sensitivity.yaml`; script `scripts/run_e_s_sensitivity.py`. Các mô hình nền chạy qua runner cũ với `--tuning-config` (run_baseline.py có thêm tham số này, mặc định vẫn là tuning.yaml). Kết quả nằm ở `e_s/baselines_validation.csv`, `e_s/m2_validation.csv`, `e_s/m2_mean_n135.csv`. Thời gian chạy 3 phút 40 giây.

| Mô hình | Điểm mới | NDCG@10 val | Giá trị đã khóa |
|---|---|---|---|
| PureSVD | k = 4 / 8 | 0,132651 / 0,153245 | k = 16: 0,166611 (cực đại nằm trong lưới) |
| UserCF (mean) | L = 5, γ = 0 / 10 / 50 | 0,064277 / 0,065160 / 0,064922 | L = 20, γ = 0: 0,017488 |
| UserCF (mean) | L = 10, γ = 0 / 10 / 50 | 0,035878 / 0,037740 / 0,038131 | |
| ItemCF (mean) | L = 5, γ = 0 / 10 / 50 | 0,056458 / 0,027434 / 0,025341 | L = 20, γ = 0: 0,015364 |
| ItemCF (mean) | L = 10, γ = 0 / 10 / 50 | 0,028306 / 0,013582 / 0,013022 | |

Với UserCF và ItemCF (chế độ mean), NDCG@10 vẫn tăng khi L giảm xuống dưới biên cũ (L = 20), tức cực đại nằm ngoài lưới cũ. UserCF L = 5, γ = 10 (0,065160) nhỉnh hơn Popularity (0,062362) trên validation; ItemCF tốt nhất (0,056458) vẫn thấp hơn Popularity. Cả hai đều thấp hơn rất xa PureSVD và E7. Phát hiện này cùng hướng với E7: chế độ mean không phù hợp cho top-N.

**M2** (nhóm tinh chỉnh, NDCG@10 trung bình ở N = 1, 3, 5). Điểm khóa (0,75; 10) tái lập đúng 0,045491914679283825.

| α \ n_min | 10 | 15 | 20 |
|---|---|---|---|
| 0,75 | 0,045492 (khóa) | 0,046643 | 0,047248 |
| 0,9 | 0,040368 | 0,042350 | 0,042374 |
| 1,0 | 0,036115 | 0,036884 | 0,038229 |

Tăng α làm giảm điểm, nên α = 0,75 không nằm ở biên xấu. Tăng n_min cho điểm cao hơn một ít (+0,001756 ở n_min = 20), tức theo hướng n_min cực đại nằm ngoài lưới cũ.

**ALS** (11 điểm; chạy sau khi được duyệt, tổng thời gian các lần chạy 1.269 giây (khoảng 21 phút); `e_s/baselines_validation.csv`, máy và thư viện trong `e_s/metrics_20261110T125523.json`). Cấu hình đã khóa: 32 nhân tố, reg 0,1, a_conf 1, NDCG@10 0,197433.

| Nhân tố | reg | a_conf | NDCG@10 val | Vòng tốt nhất |
|---|---|---|---|---|
| 8 | 1 | 0,1 | 0,156677 | 6 |
| 8 | 1 | 0,5 | 0,165609 | 10 |
| 8 | 10 | 0,1 | 0,155130 | 10 |
| 8 | 10 | 0,5 | 0,164642 | 8 |
| 16 | 1 | 0,1 | 0,175612 | 31 |
| 16 | 1 | 0,5 | 0,184401 | 6 |
| 16 | 10 | 0,1 | 0,174229 | 20 |
| 16 | 10 | 0,5 | 0,184054 | 12 |
| 16 | 0,1 | 1 | 0,189091 | 8 |
| 32 | 1 | 1 | 0,197299 | 17 |
| 32 | 0,1 | 0,5 | 0,196755 | 24 |

**Không điểm ngoài biên nào vượt cấu hình đã khóa** (cao nhất 0,197299, thấp hơn 0,000134). Theo các hướng đã thử (ít nhân tố hơn, a_conf nhỏ hơn, reg lớn hơn), cực đại nằm ở cấu hình đã chọn; giảm số nhân tố làm NDCG@10 giảm rõ. Hướng còn lại (nhiều nhân tố hơn 64, a_conf giữa 1 và 10) không nằm trong phạm vi E-S.

## E-B – M1 với β mở rộng (chỉ validation)

`scripts/run_e_b_m1_beta.py --output-dir outputs/chuong_4_bo_sung_2/e_b`, chạy mất khoảng 2 phút. Điểm đã khóa (0,75; 0,5) tái lập với sai khác 1,8e-15. Ngưỡng 5% = 0,95 × 0,166611 = 0,158281. Kết quả 24 điểm nằm ở `e_b/hinh_4_6.csv`; hình vẽ lại là `e_b/hinh_4_6.png` (điểm rỗng = dưới ngưỡng).

| β \ λ | 0,5 | 0,75 | 1 |
|---|---|---|---|
| 0,75 | 0,123376 (ARP 86,68, dưới ngưỡng) | 0,162849 (ARP 135,42) | 0,167809 (ARP 153,23) |
| 1 | 0,099942 (dưới ngưỡng) | 0,150474 (dưới ngưỡng) | 0,165012 (ARP 141,42) |
| 1,5 | 0,042660 (dưới ngưỡng) | 0,112058 (dưới ngưỡng) | 0,150014 (dưới ngưỡng) |
| 2 | 0,028285 (dưới ngưỡng) | 0,059445 (dưới ngưỡng) | 0,119666 (dưới ngưỡng) |

Áp dụng đúng quy tắc chọn cũ (`select_full_variant`: λ < 1, β > 0, trong ngưỡng, ARP nhỏ nhất) lên 24 điểm thì cấu hình được chọn là **λ = 0,75, β = 0,75**: NDCG@10 0,162849, ARP 135,42, ILD 0,815701. Cấu hình đã khóa β = 0,5 có ARP 152,50. Nghĩa là lưới cũ cắt ngay biên β. Đề xuất cho báo cáo: nêu đây là giới hạn của lưới và giữ M1 đã khóa (test đã mở, không chọn lại).

## E-C – nhóm người dùng (test, NDCG@10)

`scripts/report_e_c_groups.py --output-dir outputs/chuong_4_bo_sung_2/e_c`. Script đọc NDCG@10 từng người dùng của tám mô hình đã khóa; bootstrap 1.000 lần, seed 42.

- **Theo độ dài lịch sử** (`e_c/nhom_lich_su_ci.csv`): nhóm "Dưới 40" có 37 người, nhóm "Từ 40 trở lên" có 1.818 người. Ví dụ PureSVD đạt 0,212681 [0,136022; 0,290018] ở nhóm dưới 40 và 0,182171 [0,171463; 0,193219] ở nhóm còn lại; Popularity đạt 0,153110 [0,068178; 0,249498] và 0,067058 [0,061058; 0,073316]. CI của nhóm 37 người rất rộng, nên chỉ nên dùng để mô tả.
- **Bảng 4.10** (ba nhóm theo mức ưa phổ biến; tái lập đúng số người và trung bình của bảng cũ). CI từng ô nằm trong `e_c/bang_4_10_ci.csv`, ví dụ PureSVD Thấp 0,072375 [0,061513; 0,082361], Cao 0,306543 [0,288074; 0,324046]. Kruskal–Wallis giữa ba nhóm, Holm trên 8 mô hình (`e_c/bang_4_10_kruskal_wallis.csv`): có ý nghĩa với mọi mô hình trừ Random (p Holm 0,881) và ItemCF (0,619). Ví dụ PureSVD có H = 385,43, p Holm 1,21e-83; M1 có H = 324,65, p Holm 1,59e-70.
- **M1 − PureSVD theo nhóm**, Holm trên 3 nhóm (`e_c/metrics.json`):

| Nhóm | Số người | Chênh lệch | CI 95% | r_rb | p Holm |
|---|---|---|---|---|---|
| Thấp | 618 | 0,008667 | [0,005444; 0,012090] | 0,5257 | 1,07e-07 |
| Trung bình | 618 | −0,000039 | [−0,004450; 0,004277] | 0,0342 | 0,644 |
| Cao | 619 | −0,012702 | [−0,018295; −0,006717] | −0,2632 | 2,50e-05 |

M1 hơn PureSVD có ý nghĩa ở nhóm ưa phổ biến thấp và kém hơn có ý nghĩa ở nhóm cao. Hai hiệu ứng ngược chiều này giải thích vì sao trên toàn bộ người dùng M1 tương đương PureSVD (TOST).

## E-D – thống kê mô tả dữ liệu (`scripts/report_e_d_data.py --output-dir outputs/chuong_4_bo_sung_2/e_d`)

Bảng mô tả gốc và sau lọc nằm ở `e_d/thong_ke_mo_ta.csv`:

| Chỉ số | Gốc | Sau lọc |
|---|---|---|
| Người dùng | 1.892 | 1.877 |
| Nghệ sĩ trong danh mục / có tương tác | 17.632 / 17.632 | 17.632 / 17.617 |
| Tương tác | 92.834 | 92.801 |
| Mật độ (trên danh mục) | 0,2783% | 0,2804% |
| Nghệ sĩ/người: trung bình, trung vị, nhỏ nhất, lớn nhất | 49,07; 50; 1; 50 | 49,44; 50; 5; 50 |
| Người có đúng 50 nghệ sĩ | 1.829 (96,67%) | 1.829 (97,44%) |
| Người nghe/nghệ sĩ: trung bình, trung vị | 5,27; 1 | 5,27; 1 |
| Nghệ sĩ chỉ có 1 người nghe | 10.679 | 10.667 |
| Tổng lượt nghe | 69.183.975 | 69.138.727 |
| Lượt nghe lớn nhất của một cặp | 352.698 | 352.698 |
| Lượt nghe mỗi cặp: trung vị | 260 | 260 |

Thẻ: 186.479 dòng gán thẻ gốc, 184.941 dòng nối được danh mục (1.538 dòng có nghệ sĩ ngoài danh mục). 12.133 nghệ sĩ trong danh mục có thẻ; 5.499 nghệ sĩ chưa có thẻ, trong đó 5.493 nghệ sĩ có tương tác.

**Kiểm tra số trong bản nháp của cô** (`e_d/kiem_tra_so_lieu_ban_nhap.csv`): **17/17 số khớp.** Lưu ý: 69.138.727 là tổng lượt nghe **sau lọc** (gốc là 69.183.975); 49,07 và 0,2783% là số **gốc**. Hình 4.1 và 4.2 đã vẽ lại trên dữ liệu gốc: `e_d/hinh_4_1_goc.png`, `e_d/hinh_4_2_goc.png` (kèm CSV).

**Câu "ILD theo thẻ chỉ tính được trên khoảng một phần ba danh mục có thẻ":** danh mục train có 15.398 nghệ sĩ, trong đó 5.650 nghệ sĩ (36,69%) có vector thẻ. Vector thẻ dùng cặp train và thẻ có df ≥ 2, giống công thức của M2 (`thong_ke/phan_tich/ild_the_mo_hinh.json`). Câu này đúng nếu hiểu là "danh mục huấn luyện có vector thẻ dùng được". Nếu tính mọi thẻ thô thì 68,81% danh mục có thẻ (12.133/17.632), nên câu văn cần ghi rõ cách tính.

## E-P – Popularity theo số người nghe phân biệt c_i (chỉ validation)

`PopularityRecommender(score="listeners")` (mặc định vẫn là tổng log2(1 + lượt nghe)); script `scripts/run_e_p_popularity.py`, kết quả `e_p/popularity_validation.csv`.
- Cách cũ tái lập đúng 0,062362.
- Xếp theo c_i: NDCG@10 0,062900, Precision 0,034102, Recall 0,073262, ARP 352,10, ILD 0,639466.
- Chênh lệch nhỏ (+0,000538), không đổi vị trí của Popularity trong bảng.

## Tệp mã đã thêm hoặc sửa trong Giai đoạn 1

- Mới: `src/musicrec/evaluation/paired.py`; các script `compare_statistics.py`, `run_e7_topn.py`, `run_e_s_sensitivity.py`, `run_e_b_m1_beta.py`, `report_e_c_groups.py`, `report_e_d_data.py`, `run_e_p_popularity.py`; cấu hình `configs/e7_topn_neighbors.yaml`, `configs/e_s_sensitivity.yaml`; test `tests/unit/test_paired.py`, `test_neighborhood_sum.py`, `test_given_n_e7_scripts.py`.
- Sửa (chế độ mặc định giữ nguyên): `user_cf.py`, `item_cf.py` (thêm sum), `popularity.py` (thêm listeners), `run_baseline.py` (thêm `--tuning-config`), `evaluate_m2_test.py` (thêm `--target-mode`, bootstrap dùng chung), `test_statistics.py`, `report_ch4_extras.py` (bootstrap dùng chung, TOST, họ Holm), `tests/unit/test_popularity.py`.

## Kiểm tra mã

ruff check, ruff format --check, mypy src và pytest đều đạt ngay trước khi commit (số test ghi trong thông điệp commit).
