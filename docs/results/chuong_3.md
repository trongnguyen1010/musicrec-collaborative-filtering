# Kết quả Chương 3: chạy lại dữ liệu và đối chiếu số liệu

Ngày chạy: 26/10/2026. Nhánh `claude/project-thread-n6skg7`. Phạm vi: bước 3.1 và 3.2 trong [ROADMAP](../ROADMAP.md#chương-3-phân-tích-bài-toán-và-phương-pháp-đề-xuất). Bước 3.3 (tài liệu hóa thiết kế 3.6–3.8) đang chờ trả lời câu hỏi Q3–Q7 nên chưa làm.

## Tóm tắt

- Dữ liệu HetRec nhận từ tệp `data.rar` của nhóm. Cả **8/8 mã băm SHA-256** (ZIP và 7 tệp `.dat`/`readme.txt`) trùng với bảng mã băm trong [data card](../data-card.md#mã-băm-sha-256-của-đầu-vào-đã-kiểm-tra).
- Chạy lại Bước 1–6 từ dữ liệu gốc hai lần liên tiếp. Toàn bộ 31 tệp dữ liệu/bảng đầu ra của hai lần **trùng từng byte**, và mã băm đầu ra ghi trong metadata của các bước cũng trùng nhau.
- Đối chiếu **70 con số** trong Chương 3 và Phụ lục B của bản v15 (25-10-2026) với kết quả chạy lại: **70/70 khớp**, không có số nào sai.
- **Không so được với các run cũ** (`outputs/runs/...`), vì các run này không có trong `data.rar` và không có trong repo. Việc đối chiếu vì vậy dựa trên con số đã ghi trong báo cáo và data card, không dựa trên mã băm của run cũ.
- Chương 3 bản v15 **chưa cần sửa số liệu** ở mục 3.4, 3.5, 3.10 và Phụ lục B. Những chỗ cần sửa nằm ở phần mô tả thiết kế 3.6–3.8 (mục 4 bên dưới) và phụ thuộc quyết định Q3–Q7.

## 1. Môi trường chạy

Đây là lần chạy phát triển trên máy đám mây. Theo thỏa thuận, lần chạy lấy số đưa vào báo cáo sẽ chạy lại bằng cùng script trên máy Windows của nhóm, và bảng này sẽ được thay bằng cấu hình máy đó.

| Mục | Giá trị |
| --- | --- |
| Nhãn máy | cloud |
| Hệ điều hành | Linux-6.18.44-fc-v153-x86_64-with-glibc2.39 |
| CPU | Intel(R) Xeon(R) Processor @ 2.10GHz, 4 luồng logic |
| RAM | 16.872.804.352 byte (khoảng 15,7 GiB) |
| Python | 3.11.17 |
| numpy / pandas / pyarrow | 2.4.6 / 2.3.3 / 19.0.1 |
| scipy / scikit-learn | 1.17.1 / 1.9.1 |
| matplotlib / pyyaml | 3.11.2 / 6.0.3 |
| Git SHA lúc chạy | `8d170f9501204238e49b70d3d611e39e7d9105a5`, cây làm việc sạch |

Danh sách đầy đủ 87 gói đã cài nằm trong [environment.json](chuong_3/environment.json).

## 2. Bước 3.1: chạy lại Bước 1–6

Lệnh (chạy từ thư mục gốc repo, dữ liệu ở `data/raw/hetrec2011`):

```bash
python -B scripts/run_chuong_3.py --label cloud --output-dir outputs/chuong_3/cloud_20261026
python -B scripts/check_chuong_3_report.py --run outputs/chuong_3/cloud_20261026/run --output outputs/chuong_3/cloud_20261026/report_check.json
```

`run_chuong_3.py` gọi lần lượt các script có sẵn (`eda.py`, `preprocess.py`, `split_data.py`, `prepare_inputs.py`, `evaluate.py --toy-check`) vào `run/`, rồi chạy lại toàn bộ vào `recheck/` và so sánh. Script không thay đổi thuật toán của bước nào.

Thời gian chạy (giây, đồng hồ thực) trên máy đám mây, nguồn [summary.json](chuong_3/summary.json):

| Bước | Lần 1 | Lần 2 | Số tệp so sánh | Khác nhau |
| --- | --- | --- | --- | --- |
| EDA dữ liệu gốc | 4,87 | 5,05 | 6 | 0 |
| Làm sạch | 1,69 | 1,58 | 8 | 0 |
| Chia tập | 1,27 | 1,14 | 5 | 0 |
| Biểu diễn | 1,18 | 1,20 | 9 | 0 |
| Bộ đánh giá (ví dụ tính tay) | 0,10 | 0,09 | 3 | 0 |

Các tệp so sánh gồm Parquet, NPZ, CSV và JSON dữ liệu. Không so `metrics.json` (chứa thời điểm chạy), thư mục `code/` (bản chụp mã), hình PNG và bộ nhớ đệm font của matplotlib.

Mã băm SHA-256 của các tệp chính (lần chạy này):

| Tệp | SHA-256 |
| --- | --- |
| cleaning/interactions.parquet | `e2ddee2f323981cfb8d092db00f78a7cc17f2e9e70962d5032beea1af8db1d65` |
| split/train.parquet | `5232d6b1b7a5bb8354b94bc8ee2e4d27054607915f83ca8d18f8aefdd97cb526` |
| split/validation.parquet | `a456b7306756aed62321196045c2b101451e935e5cc6f878803adededf58972c` |
| split/test.parquet | `c9196bba9fa761db016d1b8eab7d3b76e3bad8a9fc044a5f66e2e42e58685901` |
| split/id_mappings.json | `3da642513b590a9c8fd89111cb91f0fff75c13c2c8a023f7ea4ad970fe31449b` |
| representations/transform.json | `7a7f83ebb6cee61486dba9c2442d816e57fdff05012a0cae110a5c5b15958af4` |
| representations/train_proxy_score.npz | `46558f2a9bd4c0c4a2b974b6679edb29fc2c613eb5b2d6b02a5ffffb98fff73e` |

Lưu ý: tệp Parquet do pyarrow ghi, nên mã băm có thể khác khi chạy với phiên bản pyarrow khác dù nội dung giống nhau. Khi chạy trên máy Windows, nếu mã băm Parquet khác thì cần so nội dung từng dòng trước khi kết luận dữ liệu khác. Mã băm của `id_mappings.json` và `transform.json` không phụ thuộc pyarrow.

## 3. Bước 3.2: đối chiếu số liệu Chương 3 bản v15

Script [check_chuong_3_report.py](../../scripts/check_chuong_3_report.py) ghi sẵn từng con số trong bản v15 cùng vị trí tương ứng trong kết quả chạy, rồi so với sai số làm tròn của cách viết trong báo cáo. Kết quả đầy đủ ở [report_check.json](chuong_3/report_check.json).

| Mục trong bản v15 | Số con số kiểm tra | Khớp |
| --- | --- | --- |
| 3.4.2 Quy mô và độ thưa | 10 | 10 |
| 3.4.3 Khám phá dữ liệu gốc, điều kiện lọc | 12 | 12 |
| 3.5.1 Kiểm tra và chuẩn hóa | 8 | 8 |
| 3.5.2 Chia tập, đích ngoài danh mục | 15 | 15 |
| 3.5.3 Ngưỡng phân vị, phân bố mức 1–5 | 10 | 10 |
| 3.10.2 Tỷ lệ người dùng có đúng 50 nghệ sĩ | 1 | 1 |
| Phụ lục B.1 Ví dụ xếp hạng | 5 | 5 |
| Phụ lục B.2 Độ bao phủ, Gini, ví dụ tổng hợp | 9 | 9 |
| **Tổng** | **70** | **70** |

Một số con số tiêu biểu: 1.892 người dùng, 17.632 nghệ sĩ, 92.834 cặp gốc; sau lọc còn 1.877 người dùng và 92.801 cặp; chia 74.275 / 9.263 / 9.263; đích ngoài danh mục 12,10% (validation) và 12,99% (test); bốn ngưỡng 6,392317 / 7,562242 / 8,491853 / 9,579316.

Riêng giá trị NDCG ≈ 0,61315 ở Phụ lục B.1 (chỉ trả về A khi có hai đích) không được lưu trong run của bộ đánh giá. Script tính độc lập theo định nghĩa 1 / (1 + 1/log2 3) = 0,6131472, khớp với báo cáo.

Ngoài các con số, ba nhận định định tính trong bản v15 cũng được xác nhận:

- Bảng tương tác gốc không có cặp trùng, giá trị thiếu hay lượt nghe không hợp lệ (mục 3.4.3).
- Chạy lại cùng hạt giống cho dữ liệu và ánh xạ trùng mã băm (mục 3.5.2, 3.5.3).
- Kiểm thử tự động có đối chiếu NDCG với `ndcg_score` của scikit-learn trên 20 ví dụ, mỗi ví dụ 4 giá trị K (mục 3.10.3, xem `tests/unit/test_ranking.py`).

## 4. Những điểm Chương 3 cần sửa (chưa làm, chờ quyết định)

Số liệu không sai, nhưng phần mô tả thiết kế ở 3.6–3.8 chưa khớp với những gì code đã làm. Các điểm này đã liệt kê trong [ROADMAP mục 2](../ROADMAP.md) và phụ thuộc câu hỏi Q3–Q7:

| Mục | Bản v15 viết | Code hiện tại | Câu hỏi |
| --- | --- | --- | --- |
| 1.3.2, 3.6 | Sáu mô hình đối sánh | Có thêm implicit ALS | Q3 |
| 3.6.3 | CF không có láng giềng thì chuyển sang M2 | Trong giao thức chính, CF dùng trung bình người dùng/trung bình chung | Q3–Q5 |
| 3.6.4 | PureSVD trên điểm đại diện | Tốt nhất trên validation là biểu diễn nhị phân | Q7 |
| 3.7 | M1 dựa trên mô hình nền (đề cương: SVD) | M1 đang chạy trên nền ALS | Q4 |
| 3.8 | M2 đánh giá trên tập chính | M2 dùng phép chia người dùng riêng 1.501/187/189, catalog 13.210, chỉ ItemCF làm thành phần cộng tác | Q5 |

## 5. Ghi chú về dữ liệu

- `data.rar` có thêm thư mục `interim/aiprobs-source` và `processed/reproduction` từ nhánh tái lập bài báo khác. Hai tệp trong `processed/reproduction/aiprobs-original` giải nén lỗi (`split_11.json`, `split_18.npz`). Các tệp này không được pipeline của khóa luận dùng, nên không ảnh hưởng kết quả trên.
- Dữ liệu được đặt ở `data/raw/hetrec2011/` và `data/raw/hetrec2011-lastfm-2k.zip`, đúng đường dẫn mặc định của các script. Thư mục `data/raw` và `outputs/` không đưa vào Git theo `.gitignore` hiện tại.

## 6. Việc tiếp theo

1. Chạy lại đúng hai lệnh ở mục 2 trên máy Windows với `--label windows` để lấy bộ số chính thức, rồi cập nhật bảng môi trường ở mục 1.
2. Sau khi có trả lời Q3–Q7: làm bước 3.3 (bảng tham số cuối của từng mô hình, công thức M1, giao thức M2) và đề xuất đoạn sửa cho 1.6/1.7, 3.6.3, 3.6.4, 3.7, 3.8.
