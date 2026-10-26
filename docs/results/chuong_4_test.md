# Kết quả Chương 4: bản chạy chính thức và đánh giá trên tập test

Ngày chạy: 26/10/2026, 14:30–15:18 (giờ máy chủ), trên máy đám mây. Bạn đã chọn chạy bản chính thức trên máy này ngày 26/10/2026. Mọi con số trong tài liệu này đến từ **một lần chạy liên tục, một máy, một commit** (`e1350ce`). Lần chạy bắt đầu từ dữ liệu gốc và đi qua đủ Chương 3 → baseline → tinh chỉnh → M1 → khóa cấu hình → test.

Thư mục kết quả: `outputs/chinh_thuc_cloud_20261026/`. Các tệp nhỏ (khóa cấu hình, bảng chỉ số, kiểm định, môi trường) được chép vào [docs/results/chinh_thuc_cloud_20261026/](chinh_thuc_cloud_20261026/).

## Tóm tắt

- **Tập test đã mở đúng một lần**, sau khi `lock.json` ghi lại toàn bộ cấu hình đã chọn, mã băm checkpoint và các cặp kiểm định. Mã băm của `lock.json` trước và sau khi chấm test trùng nhau. Không mô hình nào được huấn luyện lại; Random và Popularity tính lại từ train vì đó là thống kê xác định.
- Lần chạy chính thức cho **cùng lựa chọn và cùng con số validation** như lần chạy phát triển ([chuong_4.md](chuong_4.md)). Chương 3 chạy lại vẫn khớp 70/70 con số của báo cáo v15.
- Thứ hạng trên test theo NDCG@10: **ALS (mở rộng) > PureSVD > M1 > Popularity > SVD > UserCF > ItemCF > Random**. Thứ tự này giống trên validation, chỉ khác là M1 xếp sau nền của nó.
- **PureSVD cao hơn Popularity** 0,1140 NDCG@10 (CI 95% [0,1064; 0,1219], p Holm < 1e-100).
- **SVD, UserCF và ItemCF vẫn thấp hơn Popularity trên test**, giống validation.
- **M1** so với nền PureSVD: NDCG@10 giảm 0,75%, khác biệt **không có ý nghĩa thống kê** (p Holm = 0,608), trong khi ARP giảm 15,69%, độ bao phủ tăng từ 1,86% lên 2,94%, ILD tăng từ 0,795 lên 0,814.
- **M2 chưa đánh giá trên test** vì còn chờ trả lời Q5.

## 1. Môi trường chạy

| Mục | Giá trị |
| --- | --- |
| Máy | Máy đám mây; Linux-6.18.44-fc-v153-x86_64-with-glibc2.39 |
| CPU / RAM | Intel(R) Xeon(R) Processor @ 2.10GHz, 4 luồng logic / 16.872.804.352 byte |
| Python | 3.11.17 |
| Thư viện chính | numpy 2.4.6, pandas 2.3.3, pyarrow 19.0.1, scipy 1.17.1, scikit-learn 1.9.1, implicit 0.7.3 |
| Commit | `e1350ceee849daf4ab78ef607629996f96ae35ca` |
| Trạng thái Git | Sạch ở mọi bước, trừ hai run Random/Popularity: chúng ghi nhận thêm tệp chưa commit `scripts/test_statistics.py`. Tệp này là script kiểm định viết trong lúc chạy, không được các run đó gọi tới. |

Danh sách đầy đủ gói đã cài: [environment.json](chinh_thuc_cloud_20261026/environment.json).

Thời gian: tinh chỉnh 42,8 phút; chấm test cho 8 mô hình × các seed 1,5 phút; toàn bộ lần chạy khoảng 48 phút.

## 2. Cấu hình đã khóa

Nguồn: [lock.json](chinh_thuc_cloud_20261026/test/lock.json). Mọi cấu hình được chọn theo NDCG@10 trên validation, seed 42.

| Mô hình | Cấu hình | NDCG@10 validation |
| --- | --- | --- |
| UserCF | L = 20, shrinkage = 0 | 0,017488 |
| ItemCF | L = 20, shrinkage = 0 | 0,015364 |
| SVD | d = 16, η = 0,001925, λreg = 0,01025 | 0,060666 |
| PureSVD nhị phân | k = 16 | 0,166611 |
| M1 | nền PureSVD k = 16, C = 100, λ = 0,75, β = 0,5 | 0,167477 |
| Implicit ALS (mở rộng) | 32 nhân tố, reg = 0,1, a_conf = 1 | 0,197433 |

Các cặp kiểm định khai báo trong `lock.json` trước khi mở test: PureSVD – Popularity, SVD – PureSVD, M1 – PureSVD, ALS – PureSVD. Bốn cặp này là đề xuất Q12 trong ROADMAP, đã điều chỉnh theo quyết định Q3/Q4. Q12 chưa được bạn duyệt riêng, nên nếu muốn đổi cặp thì kiểm định chạy lại được, nhưng phải ghi rõ trong báo cáo là cặp được chọn sau khi xem test.

## 3. Bảng kết quả test chính (K = 10, seed 42)

Nguồn: [test/metrics.csv](chinh_thuc_cloud_20261026/test/metrics.csv). Có 1.855/1.877 người dùng có đích test trong danh mục train; 22 người không còn đích được báo riêng. 1.203/9.263 đích test (12,99%) nằm ngoài danh mục. Danh sách gợi ý trên test che cả lịch sử train và validation.

| Mô hình | Precision | Recall | NDCG | Coverage | Gini | ARP | Novelty | ILD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Random | 0,000431 | 0,001006 | 0,000597 | 0,7032 | 0,4824 | 4,51 | 14,823 | 0,9984 |
| Popularity | 0,035903 | 0,078410 | 0,068775 | 0,0019 | 0,9991 | 348,35 | 8,023 | 0,6659 |
| UserCF | 0,012722 | 0,028679 | 0,018850 | 0,1220 | 0,9489 | 47,93 | 12,212 | 0,9548 |
| ItemCF | 0,009596 | 0,022058 | 0,017502 | 0,2457 | 0,9176 | 50,77 | 12,545 | 0,8493 |
| SVD có độ lệch | 0,031051 | 0,068041 | 0,062650 | 0,0038 | 0,9991 | 319,77 | 8,193 | 0,7135 |
| PureSVD nhị phân | 0,088356 | 0,194205 | 0,182780 | 0,0186 | 0,9923 | 174,21 | 9,230 | 0,7948 |
| **M1** | 0,088248 | 0,193872 | 0,181416 | 0,0294 | 0,9892 | 146,87 | 9,527 | 0,8135 |
| Implicit ALS (mở rộng) | 0,107062 | 0,237493 | 0,217453 | 0,0514 | 0,9812 | 131,97 | 9,846 | 0,8234 |

NDCG tại K = 5 và K = 20 (seed 42):

| Mô hình | NDCG@5 | NDCG@20 | Recall@20 |
| --- | --- | --- | --- |
| Random | 0,000276 | 0,000690 | 0,001222 |
| Popularity | 0,053910 | 0,083739 | 0,114088 |
| UserCF | 0,010779 | 0,033690 | 0,065364 |
| ItemCF | 0,012797 | 0,022138 | 0,033405 |
| SVD | 0,048195 | 0,075275 | 0,098446 |
| PureSVD | 0,153384 | 0,213270 | 0,268535 |
| M1 | 0,150894 | 0,213011 | 0,271033 |
| ALS | 0,179155 | 0,253336 | 0,325499 |

RMSE proxy trên test (bảng phụ, 8.060 cặp test trong danh mục, không dùng để chọn mô hình): UserCF 0,9327; ItemCF 0,9610; SVD 1,2713.

Ba seed (NDCG@10 trên test, trung bình ± độ lệch chuẩn mẫu), nguồn [seed_summary.json](chinh_thuc_cloud_20261026/test/seed_summary.json):

| Mô hình | Trung bình ± std |
| --- | --- |
| Random | 0,000559 ± 0,000033 |
| SVD | 0,063540 ± 0,000782 |
| PureSVD | 0,182780 ± 0 |
| M1 | 0,181416 ± 0 |
| ALS | 0,217211 ± 0,001222 |

## 4. Kiểm định thống kê (4.6)

Nguồn: [statistics_ndcg_at_10.json](chinh_thuc_cloud_20261026/test/statistics_ndcg_at_10.json), script [test_statistics.py](../../scripts/test_statistics.py). Mỗi cặp dùng NDCG@10 từng người dùng ở seed 42, trên 1.855 người dùng chung. Chênh lệch tính theo A − B. CI 95% là bootstrap phân vị 1.000 lần theo người dùng (seed 42). Kiểm định Wilcoxon dấu-hạng hai phía, bỏ các chênh lệch bằng 0, và hiệu chỉnh Holm trên bốn cặp.

| A − B | Trung bình A | Trung bình B | Chênh lệch | CI 95% | p Wilcoxon | p Holm | Số người khác 0 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PureSVD − Popularity | 0,182780 | 0,068775 | +0,114005 | [0,106354; 0,121929] | 4,73e-121 | 1,42e-120 | 1.064 |
| SVD − PureSVD | 0,062650 | 0,182780 | −0,120130 | [−0,128123; −0,111630] | 7,60e-128 | 3,04e-127 | 1.059 |
| M1 − PureSVD | 0,181416 | 0,182780 | −0,001364 | [−0,004124; 0,001244] | 0,608 | 0,608 | 755 |
| ALS − PureSVD | 0,217453 | 0,182780 | +0,034673 | [0,027812; 0,041257] | 1,68e-25 | 3,36e-25 | 1.179 |

Đọc kết quả:

- PureSVD hơn Popularity và hơn SVD rõ rệt.
- M1 không làm NDCG@10 khác có ý nghĩa so với nền: CI chứa 0, p Holm = 0,608. Lợi ích của M1 nằm ở độ phổ biến và độ đa dạng (mục 5), không nằm ở độ chính xác.
- ALS (mở rộng) hơn PureSVD có ý nghĩa thống kê. Vì ALS là thực nghiệm mở rộng (Q3), kết quả này nên đặt ở mục riêng trong Chương 4, không đưa vào bảng so sánh chính.

## 5. M1 trên test

| Chỉ số @10 | Nền PureSVD | M1 (λ = 0,75, β = 0,5) | Thay đổi |
| --- | --- | --- | --- |
| NDCG | 0,182780 | 0,181416 | −0,75% (không có ý nghĩa thống kê) |
| Recall | 0,194205 | 0,193872 | −0,17% |
| Coverage | 0,0186 | 0,0294 | từ 1,86% lên 2,94% |
| ARP | 174,21 | 146,87 | −15,69% |
| Novelty | 9,230 | 9,527 | +0,297 bit |
| ILD | 0,7948 | 0,8135 | +0,0187 |

Trên validation, M1 tăng NDCG 0,52%; trên test, M1 giảm 0,75%. Cả hai thay đổi đều nhỏ và nằm trong ngưỡng 5% đặt trước. Trên cả hai tập, M1 giảm ARP khoảng 15,7–15,8%. Báo cáo nên viết rằng M1 giảm thiên lệch phổ biến mà không làm giảm có ý nghĩa độ chính xác; **không** nên viết rằng M1 cải thiện độ chính xác.

## 6. So với bản viết trước và kế hoạch

| Nội dung | Bản 20-10 / kế hoạch | Kết quả thật |
| --- | --- | --- |
| Mô hình tốt nhất trong sáu mô hình | Chưa có số | PureSVD nhị phân k = 16, NDCG@10 test 0,1828 |
| CF so với Popularity | Kỳ vọng CF tốt hơn | UserCF, ItemCF, SVD đều thấp hơn Popularity trên cả validation và test |
| M1 | Kỳ vọng đánh đổi một phần NDCG để giảm phổ biến | NDCG không đổi có ý nghĩa; ARP giảm 15,69% |
| M2 | | Chưa đánh giá trên test (chờ Q5) |

## 7. Việc còn lại

1. Trả lời Q5 để chạy M2 trên 189 người dùng để dành, rồi viết lại mục 3.8 và phần M2 ở Chương 4.
2. Bước 4.7 (bảng chi phí: thời gian huấn luyện, gợi ý, bộ nhớ, kích thước mô hình) và 4.8 (phân tích ca lỗi) chưa làm. Số liệu thời gian và bộ nhớ đã có sẵn trong `metrics.json` của từng run.
3. Bản chạy chính thức trên máy Windows không còn cần thiết, trừ khi bạn muốn có thêm bằng chứng tái lập trên máy thứ hai. Khi đó phải ghi rõ trong báo cáo đây là lần chạy lại, không phải lần chọn mô hình mới.
