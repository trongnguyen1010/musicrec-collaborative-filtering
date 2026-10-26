# Kết quả Chương 4 (phần validation): tinh chỉnh và M1 trên nền PureSVD

Ngày chạy: 26/10/2026, máy đám mây (cấu hình như [chuong_3.md mục 1](chuong_3.md#1-môi-trường-chạy)). Đây là **lần chạy phát triển**. Bản chạy chính thức, cũng trên máy đám mây theo lựa chọn ngày 26/10, cho đúng các lựa chọn và con số validation dưới đây. Kết quả test nằm ở [chuong_4_test.md](chuong_4_test.md).

Phạm vi: bước 4.1–4.3 trong [ROADMAP](../ROADMAP.md#chương-4-huấn-luyện-và-thực-nghiệm-đánh-giá). Không script nào trong lượt chạy phát triển này đọc `test.parquet`. Bước 4.4–4.6 (khóa cấu hình, test, kiểm định) nằm ở [chuong_4_test.md](chuong_4_test.md).

Quyết định áp dụng (chọn ngày 26/10/2026): Q3 ALS là thực nghiệm mở rộng; Q4 M1 dùng nền PureSVD; Q6 tinh chỉnh đủ ngân sách; Q7 PureSVD dùng biểu diễn nhị phân.

## Tóm tắt

- Chạy đủ **48 cấu hình** theo [configs/tuning.yaml](../../configs/tuning.yaml) (UserCF 12, ItemCF 12, SVD 12, PureSVD 4, ALS 8), cộng seed 43/44 cho ba mô hình có yếu tố ngẫu nhiên. Tổng thời gian **43,8 phút** trên máy đám mây.
- Cấu hình đầu của Random, Popularity, UserCF, ItemCF, SVD và PureSVD cho **đúng số cũ** trong data card. ALS lệch ở chữ số thứ năm do khác máy (mục 5).
- Tinh chỉnh cải thiện UserCF (gấp 2,2 lần), ItemCF (gấp 2,1 lần), SVD (+7,4%) và PureSVD (+6,5%). ALS giữ nguyên cấu hình đầu.
- **UserCF, ItemCF và SVD vẫn thấp hơn Popularity sau tinh chỉnh.** Đây là kết quả thật, cần ghi rõ trong báo cáo.
- M1 trên nền PureSVD k=16 chọn **λ = 0,75, β = 0,5**: NDCG@10 tăng 0,52%, ARP giảm 15,81%, độ bao phủ tăng từ 1,79% lên 2,91%. Cấu hình này qua ngưỡng giảm NDCG tối đa 5%.
- Các điểm cần quyết định ở mục 6 đã được chốt, trừ Q5 (M2).

## 1. Bảng validation sau tinh chỉnh (K = 10, seed 42)

Nguồn: `outputs/chuong_4/tuning_cloud_20261026/<mô hình>/<run>/metrics.json` và `outputs/chuong_4/baselines_cloud_20261026/`. Cả 1.865 người dùng có đích hợp lệ đều được tính.

| Mô hình | Cấu hình chọn | Precision | Recall | NDCG | Coverage | ARP | ILD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Random | seed 42 | 0,000322 | 0,000697 | 0,000372 | 0,7060 | 4,55 | 0,9984 |
| Popularity | | 0,033941 | 0,073190 | 0,062362 | 0,0018 | 351,83 | 0,6648 |
| UserCF | L = 20, shrinkage = 0 | 0,012279 | 0,027248 | 0,017488 | 0,1220 | 50,24 | 0,9531 |
| ItemCF | L = 20, shrinkage = 0 | 0,008204 | 0,019062 | 0,015364 | 0,2461 | 50,96 | 0,8502 |
| SVD có độ lệch | d = 16, η = 0,001925, λreg = 0,01025 | 0,031314 | 0,067927 | 0,060666 | 0,0032 | 323,51 | 0,7111 |
| PureSVD (nhị phân) | k = 16 | 0,085791 | 0,185782 | 0,166611 | 0,0179 | 181,13 | 0,7844 |
| Implicit ALS (mở rộng) | 32 nhân tố, reg = 0,1, a_conf = 1 | 0,100643 | 0,221609 | 0,197433 | 0,0497 | 138,11 | 0,8128 |

RMSE proxy (bảng phụ, không dùng để chọn): UserCF 0,9413; ItemCF 0,9708; SVD 1,2757.

Ba seed (42/43/44) cho cấu hình chọn, NDCG@10 trung bình ± độ lệch chuẩn mẫu:

| Mô hình | Seed 42 | Seed 43 | Seed 44 | Trung bình ± std |
| --- | --- | --- | --- | --- |
| SVD | 0,060666 | 0,058957 | 0,059207 | 0,059610 ± 0,000923 |
| PureSVD k=16 | 0,166611 | 0,166611 | 0,166611 | 0,166611 ± 0 |
| ALS | 0,197433 | 0,197409 | 0,194878 | 0,196574 ± 0,001468 |

PureSVD cho kết quả giống hệt ở cả ba seed. Seed chỉ đổi vector khởi đầu của ARPACK, và ARPACK hội tụ về cùng không gian con.

## 2. Kết quả từng lưới

Bảng đầy đủ có trong `docs/results/chuong_4/tuning_<mô hình>.csv`.

**UserCF** (NDCG@10):

| L \ shrinkage | 0 | 10 | 50 |
| --- | --- | --- | --- |
| 20 | **0,017488** | 0,017045 | 0,017108 |
| 40 | 0,008079 | 0,008158 | 0,008530 |
| 80 | 0,002475 | 0,002539 | 0,002428 |
| 120 | 0,001525 | 0,001077 | 0,001017 |

**ItemCF** (NDCG@10):

| L \ shrinkage | 0 | 10 | 50 |
| --- | --- | --- | --- |
| 20 | **0,015364** | 0,005616 | 0,004718 |
| 40 | 0,007430 | 0,002091 | 0,001463 |
| 80 | 0,003070 | 0,001156 | 0,001207 |
| 120 | 0,002193 | 0,000874 | 0,000599 |

Với cả hai mô hình, NDCG giảm khi L tăng, nên cấu hình tốt nhất nằm ở **biên dưới của lưới** (L = 20). Shrinkage làm ItemCF kém đi rõ rệt.

**PureSVD nhị phân** (NDCG@10): k=16: **0,166611**; k=32: 0,156427; k=64: 0,137042; k=128: 0,114355. Cấu hình tốt nhất cũng ở biên dưới (k = 16).

**Implicit ALS** (NDCG@10, vòng tốt nhất):

| Nhân tố | reg | a_conf | NDCG@10 | Vòng |
| --- | --- | --- | --- | --- |
| 32 | 0,1 | 1 | **0,197433** | 16 |
| 32 | 0,01 | 1 | 0,197368 | 22 |
| 64 | 0,1 | 1 | 0,187241 | 8 |
| 64 | 0,01 | 1 | 0,186649 | 10 |
| 32 | 0,01 | 10 | 0,153926 | 37 |
| 32 | 0,1 | 10 | 0,152641 | 44 |
| 64 | 0,01 | 10 | 0,150670 | 22 |
| 64 | 0,1 | 10 | 0,149469 | 16 |

**SVD có độ lệch.** Lưới gồm cấu hình đầu cộng 11 cấu hình ngẫu nhiên (seed 42): d ∈ {16, 32, 64, 128}, η và λreg lấy theo thang log trong [0,001; 0,02] và [0,001; 0,1], như Bảng 4.3 của bản v01. NDCG@10 nằm trong khoảng 0,048651–0,060666. Vòng tốt nhất luôn là 1–4, và mọi cấu hình dừng sớm trước vòng 10. Hàm mục tiêu của SVD là sai số bình phương trên điểm đại diện. Kết quả này cho thấy giảm sai số đó không kéo theo xếp hạng tốt hơn trên dữ liệu này, đây là một ý có thể đưa vào phần thảo luận.

## 3. M1 trên nền PureSVD k=16

Config: [configs/models/m1_pure_svd.yaml](../../configs/models/m1_pure_svd.yaml). Lưới, ngưỡng 5% và quy tắc chọn giữ nguyên như M1 trên nền ALS: trong các biến thể đầy đủ đạt ngưỡng, chọn ARP thấp nhất, rồi ILD cao nhất, rồi NDCG cao nhất. Nguồn: `outputs/chuong_4/m1_pure_svd_cloud_20261026/`.

Ablation tại K = 10, seed 42 (C = 100):

| Biến thể | λ | β | NDCG | Recall | Coverage | Gini | ARP | Novelty | ILD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Nền | 1 | 0 | 0,166611 | 0,185782 | 0,0179 | 0,9928 | 181,13 | 9,171 | 0,7844 |
| Chỉ đa dạng | 0,75 | 0 | 0,165962 | 0,184799 | 0,0183 | 0,9926 | 177,97 | 9,194 | 0,7966 |
| Chỉ phạt phổ biến | 1 | 0,5 | 0,168459 | 0,187551 | 0,0205 | 0,9911 | 163,25 | 9,357 | 0,7890 |
| **M1 đầy đủ (chọn)** | 0,75 | 0,5 | 0,167477 | 0,187337 | 0,0291 | 0,9897 | 152,50 | 9,477 | 0,8047 |

So với nền, M1 đầy đủ tăng NDCG@10 0,52% (0,166611 → 0,167477), giảm ARP 15,81% (181,13 → 152,50) và tăng ILD từ 0,7844 lên 0,8047. 10/12 tổ hợp λ/β nằm trong ngưỡng giảm 5%. Hai tổ hợp vượt ngưỡng là λ = 0,5 với β = 0,25 (giảm 5,24%) và β = 0,5 (giảm 13,72%). Biến thể λ = 1, β = 0,5 có NDCG cao nhất (0,168459), nhưng quy tắc chọn đặt trước ưu tiên ARP thấp nhất.

Vì PureSVD giống hệt ở ba seed, phần xác nhận ở seed 43/44 **không phải kiểm chứng độc lập**. Báo cáo nên ghi như vậy thay vì gọi là "ổn định qua ba seed". Ngoài ra, các run nền PureSVD không có tệp kiểm tra độc lập `verification.json` như các run ALS cũ. `run_m1.py` ghi rõ điều này trong `base_verification`.

So sánh với M1 trên nền ALS (run cũ, theo data card): NDCG@10 giảm 4,33% và ARP giảm 24,71%. Trên nền PureSVD, M1 giảm ARP ít hơn nhưng không làm giảm NDCG.

## 4. So với kế hoạch và bản viết trước

| Nội dung | Kế hoạch / bản trước | Kết quả lần này |
| --- | --- | --- |
| CF thấp hơn Popularity | Đã thấy ở cấu hình đầu; ROADMAP ghi cần kiểm tra lại sau tinh chỉnh | Vẫn đúng sau tinh chỉnh: Popularity cao hơn UserCF 3,57 lần, ItemCF 4,06 lần, SVD 2,8% (seed 42) |
| PureSVD | Bản v15: điểm đại diện, k chưa chốt | Nhị phân, k = 16 |
| Nền M1 | Đề cương V2: SVD; code: ALS | PureSVD k=16 (Q4) |
| M1 | Kỳ vọng đánh đổi NDCG để giảm ARP | Không mất NDCG, ARP giảm 15,81% |

## 5. Tái lập giữa hai máy

- Random, Popularity, UserCF, ItemCF, SVD, PureSVD: cấu hình đầu cho NDCG@10 trùng tới mọi chữ số đã ghi trong data card.
- ALS (32/0,1/1, seed 42): máy đám mây cho 0,1974331612 ở vòng 16; run cũ cho 0,1974107044 ở vòng 18. Chạy lại trên cùng máy đám mây thì danh sách gợi ý trùng từng byte, nên phần lệch đến từ khác máy hoặc thư viện số (float32, BLAS), không phải do ngẫu nhiên trong lần chạy. Vì vậy bộ số chính thức cần chạy trên một máy duy nhất.

## 6. Cần bạn quyết định

1. **Cấu hình tốt nhất nằm ở biên lưới.** UserCF và ItemCF có L = 20, PureSVD có k = 16, đều là giá trị nhỏ nhất của lưới. Kế hoạch ghi "không tăng lưới sau khi thấy kết quả". **Đã chốt ngày 26/10/2026: giữ nguyên lưới, ghi là hạn chế trong báo cáo** (không thử thêm L ∈ {5, 10} hay k ∈ {4, 8}).
2. **Khóa cấu hình và mở tập test (4.4–4.5).** Đã chốt ngày 26/10/2026: chạy bản chính thức trên máy đám mây. Đã chạy xong, xem [chuong_4_test.md](chuong_4_test.md).
3. **Q5 (M2)** vẫn chờ trả lời trước khi viết lại mục 3.8 và chạy M2 trên 189 người dùng để dành.

## 7. Lệnh chạy lại

```bash
python -B scripts/tune_validation.py --representations-run outputs/chuong_3/<run>/run/representations --output-dir outputs/chuong_4/tuning_<máy>_<ngày>
python -B scripts/run_m1.py --config configs/models/m1_pure_svd.yaml --output-dir outputs/chuong_4/m1_pure_svd_<máy>_<ngày>
python -B scripts/run_random.py --split-run outputs/chuong_3/<run>/run/split --output-dir outputs/chuong_4/baselines_<máy>_<ngày>/random
python -B scripts/run_popularity.py --split-run outputs/chuong_3/<run>/run/split --output-dir outputs/chuong_4/baselines_<máy>_<ngày>/popularity
```

Đường dẫn `base_runs` trong `configs/models/m1_pure_svd.yaml` cần trỏ tới run PureSVD của máy đang chạy.
