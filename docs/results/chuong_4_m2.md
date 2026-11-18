# Kết quả M2: người dùng mới có ít lịch sử nghe

Ngày chạy: 26/10/2026, máy đám mây (cùng môi trường với lần chạy chính thức, xem [chuong_4_test.md](chuong_4_test.md)). Theo quyết định Q5: giữ phép chia người dùng 1.501 / 187 / 189, chọn cấu hình M2 trên 187 người dùng tinh chỉnh (tập validation), rồi chấm **một lần** trên tập test của 189 người để dành.

## Tóm tắt

- Trên validation, cấu hình được chọn là **α = 0,75, ngưỡng lịch sử = 10**. NDCG@10 trung bình ở N = 1, 3, 5 là 0,045492, cao hơn Popularity ở mọi N > 0.
- Trên test của 189 người để dành, kết quả **đảo ngược**: Popularity có NDCG@10 cao hơn M2 ở cả N = 1, 3 và 5. Ở so sánh chính (N = 3), M2 thấp hơn Popularity 0,008719, khoảng tin cậy 95% là [−0,026749; 0,008436], p sau Holm = 0,857. Không có khác biệt có ý nghĩa thống kê.
- M2 vẫn có ích về độ phủ và độ mới: ở N = 3, coverage@10 tăng từ 0,0009 lên 0,0555, ARP@10 giảm từ 294,9 xuống 129,1. Tuy vậy, M2 không cải thiện độ chính xác so với Popularity trên tập test.
- Kết luận đưa vào báo cáo: M2 **không đạt** giả thuyết "cải thiện độ chính xác cho người dùng mới so với Popularity". Kết quả validation trên 187 người dùng không lặp lại trên 189 người khác. Đây là kết quả âm, và báo cáo cần ghi đúng như vậy.

## 1. Thiết lập

| Mục | Giá trị | Nguồn |
| --- | --- | --- |
| Người dùng học / tinh chỉnh / để dành | 1.501 / 187 / 189 | `validation/metrics.json` |
| Cặp tương tác dùng để học | 59.371 (chỉ train của nhóm học) | `validation/metrics.json` |
| Danh mục nghệ sĩ của nhóm học | 13.210 | như trên |
| Từ vựng thẻ sau lọc df ≥ 2 | 2.316 thẻ; 4.717 nghệ sĩ có thẻ, 8.493 không có | `feature_report` |
| Hồ sơ cung cấp | N = 0, 1, 3, 5 nghệ sĩ lấy từ train của chính người dùng, lồng nhau, xáo theo hạt giống 42 | `run_m2.py` |
| Đích validation / test | Cặp validation (187 người) / cặp test (189 người), chỉ tính đích trong danh mục | |
| Người có đích trong danh mục | 186/187 (validation), 187/189 (test) | `evaluation.json` |
| Tỷ lệ đích ngoài danh mục | 16,63% (validation), 14,59% (test) | như trên |
| Lưới chọn | α ∈ {0,25; 0,5; 0,75} × ngưỡng ∈ {3, 5, 10} | `m2_config.yaml` |
| Quy tắc chọn | NDCG@10 trung bình N = 1/3/5 cao nhất, hòa thì α rồi ngưỡng nhỏ hơn | `select_m2_config` |

Lệnh chạy (từ thư mục gốc, Git `7058883` cho bước chọn, `717d04b` cho bước test):

```bash
python -B scripts/run_m2.py --config outputs/chinh_thuc_cloud_20261026/chuong_4/m2_config.yaml --output-dir outputs/chinh_thuc_cloud_20261026/chuong_4/m2_tuning
python -B scripts/evaluate_m2_test.py --m2-run outputs/chinh_thuc_cloud_20261026/chuong_4/m2_tuning --output-dir outputs/chinh_thuc_cloud_20261026/chuong_4/m2_test
```

`m2_config.yaml` là bản sao của `configs/models/m2.yaml`, chỉ đổi `split_run` và `clean_run` sang run chính thức của Chương 3. Bước chọn có cơ chế chặn mọi thao tác mở `test.parquet`. Bước test ghi `lock.json` (cấu hình đã chọn, mã băm mô hình, các cặp so sánh định trước) trước khi đọc test; mô hình được nạp lại, không học lại. Cả hai lần chạy có cây làm việc Git sạch.

## 2. Chọn cấu hình trên validation (187 người)

NDCG@10 theo N. Nguồn: [validation/metrics.csv](chinh_thuc_cloud_20261026/m2/validation/metrics.csv), [selection.json](chinh_thuc_cloud_20261026/m2/validation/selection.json).

| Phương pháp | N = 0 | N = 1 | N = 3 | N = 5 |
| --- | --- | --- | --- | --- |
| Popularity | 0,027627 | 0,027801 | 0,028957 | 0,029728 |
| Nội dung (thẻ) | 0,027627 | 0,030250 | 0,037268 | 0,048444 |
| ItemCF (L = 40) | 0,027627 | 0,025011 | 0,021822 | 0,021939 |
| **M2 (α = 0,75, ngưỡng 10)** | 0,027627 | **0,039662** | **0,045693** | **0,051121** |

Ở N = 0, mọi nhánh đều trả đúng thứ tự Popularity (script kiểm tra điều này). Cấu hình được chọn nằm ở **góc lưới** (α lớn nhất, ngưỡng lớn nhất), tức là gần như dựa vào nội dung thẻ và gần như không dùng ItemCF ở N ≤ 5 (trọng số CF = N/10). Đây là hạn chế giống trường hợp UserCF, ItemCF và PureSVD ở Chương 4: lưới không được mở rộng sau khi thấy kết quả.

## 3. Kết quả test (189 người để dành, chấm một lần)

K = 10, 187 người có đích trong danh mục. Nguồn: [test/metrics.csv](chinh_thuc_cloud_20261026/m2/test/metrics.csv).

| N | Phương pháp | Precision | Recall | NDCG | Coverage | ARP | Novelty | ILD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Mọi phương pháp (= Popularity) | 0,030481 | 0,065508 | 0,056508 | 0,000757 | 295,70 | 7,944 | 0,6447 |
| 1 | Popularity | 0,030481 | 0,065508 | **0,056508** | 0,000833 | 295,52 | 7,945 | 0,6441 |
| 1 | Nội dung | 0,013904 | 0,031551 | 0,021481 | 0,059576 | 126,04 | 10,902 | 0,8032 |
| 1 | ItemCF | 0,026203 | 0,058556 | 0,046035 | 0,026268 | 231,25 | 9,052 | 0,7061 |
| 1 | M2 | 0,024599 | 0,054635 | 0,043317 | 0,047994 | 167,27 | 10,066 | 0,7490 |
| 3 | Popularity | 0,032086 | 0,068984 | **0,058572** | 0,000908 | 294,91 | 7,947 | 0,6449 |
| 3 | Nội dung | 0,020856 | 0,048485 | 0,040181 | 0,063437 | 83,56 | 11,510 | 0,8402 |
| 3 | ItemCF | 0,020856 | 0,046346 | 0,034894 | 0,039213 | 177,19 | 9,934 | 0,7638 |
| 3 | M2 | 0,027807 | 0,062834 | 0,049854 | 0,055488 | 129,10 | 10,598 | 0,7821 |
| 5 | Popularity | 0,032620 | 0,071658 | **0,059750** | 0,000984 | 294,33 | 7,950 | 0,6475 |
| 5 | Nội dung | 0,025134 | 0,055971 | 0,047301 | 0,063588 | 67,19 | 11,727 | 0,8665 |
| 5 | ItemCF | 0,017112 | 0,037611 | 0,027847 | 0,041559 | 153,82 | 10,253 | 0,7975 |
| 5 | M2 | 0,029412 | 0,065508 | 0,049562 | 0,065026 | 97,54 | 11,139 | 0,8249 |

## 4. Kiểm định thống kê trên test

NDCG@10 theo từng người dùng, 187 người. Chín cặp được khai báo trong `lock.json` trước khi đọc test; so sánh chính là M2 − Popularity ở N = 3. Nguồn: [statistics_ndcg_at_10.json](chinh_thuc_cloud_20261026/m2/test/statistics_ndcg_at_10.json).

| N | Cặp | Chênh lệch | KTC 95% (bootstrap) | p Wilcoxon | p Holm |
| --- | --- | --- | --- | --- | --- |
| 1 | M2 − Popularity | −0,013191 | [−0,028847; 0,002145] | 0,188 | 0,942 |
| 1 | M2 − Nội dung | +0,021837 | [0,012399; 0,033588] | 2,47e−5 | **0,000222** |
| 1 | M2 − ItemCF | −0,002717 | [−0,017874; 0,012338] | 0,622 | 1 |
| **3** | **M2 − Popularity** | **−0,008719** | **[−0,026749; 0,008436]** | **0,143** | **0,857** |
| 3 | M2 − Nội dung | +0,009673 | [−0,003768; 0,021598] | 0,0598 | 0,418 |
| 3 | M2 − ItemCF | +0,014960 | [−0,002363; 0,032974] | 0,203 | 0,942 |
| 5 | M2 − Popularity | −0,010187 | [−0,029915; 0,009178] | 0,333 | 0,999 |
| 5 | M2 − Nội dung | +0,002262 | [−0,013278; 0,017881] | 0,636 | 1 |
| 5 | M2 − ItemCF | +0,021715 | [0,005851; 0,039222] | 0,00744 | 0,0595 |

Chỉ một cặp có ý nghĩa sau hiệu chỉnh Holm: ở N = 1, M2 tốt hơn nội dung thuần. Mọi so sánh với Popularity đều âm nhưng không có ý nghĩa thống kê.

## 5. Diễn giải và đề xuất sửa báo cáo

1. **Không nói M2 cải thiện độ chính xác.** Trên test, Popularity đứng đầu NDCG@10 ở mọi N. Khác biệt không có ý nghĩa, nên kết luận đúng là "không tìm thấy bằng chứng M2 tốt hơn Popularity về độ chính xác".
2. **Validation và test lệch nhau.** Trên validation, Popularity của 187 người tinh chỉnh chỉ đạt 0,0278–0,0297, còn trên test của 189 người để dành đạt 0,0565–0,0598. Hai nhóm người dùng khác nhau, mỗi nhóm chưa tới 200 người, nên độ chính xác của Popularity dao động lớn giữa hai nhóm. Cấu hình M2 chọn trên nhóm đầu không giữ được ưu thế ở nhóm sau. Báo cáo nên nêu đây là hạn chế về cỡ mẫu.
3. **Cái M2 làm được là đa dạng hóa.** Ở N = 3, M2 tăng coverage@10 khoảng 61 lần (0,000908 → 0,055488), giảm ARP@10 56% (294,91 → 129,10), tăng novelty và ILD. Đổi lại, NDCG@10 giảm 0,008719 (không có ý nghĩa). Có thể viết M2 như một phương án đánh đổi: giữ độ chính xác ở mức không khác biệt có ý nghĩa với Popularity nhưng gợi ý đa dạng hơn rõ rệt.
4. **Thành phần cộng tác yếu.** ItemCF với hồ sơ 1–5 nghệ sĩ có NDCG@10 giảm dần khi N tăng (0,046 → 0,028 trên test). Cấu hình chọn (ngưỡng 10) khiến ItemCF chỉ chiếm tối đa 50% trọng số ở N = 5.
5. **Mục 3.8 của báo cáo** cần mô tả đúng giao thức riêng: phép chia người dùng 80/10/10 theo hạt giống 42, danh mục 13.210 nghệ sĩ của nhóm học, hồ sơ N = 0/1/3/5, chọn cấu hình trên 187 người tinh chỉnh, chấm một lần trên 189 người để dành.
