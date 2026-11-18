# Kết quả Chương 5 (giai đoạn A): backend demo FastAPI và Streamlit dự phòng

Ngày chạy: 27/10/2026, trên máy cục bộ của người dùng. Kế hoạch: [KE_HOACH_PROTOTYPE_DEMO.md](../KE_HOACH_PROTOTYPE_DEMO.md) (đã duyệt, P1 PureSVD kèm công tắc M1, P4 chép bản gốc).

## 1. Tóm tắt

- Gói phát hành `demo-chinh-thuc-20261026` chép nguyên checkpoint chính thức (PureSVD k=16, M1 trên PureSVD, ALS seed 42, M2), **không fit lại**. Mọi tệp checkpoint khớp mã băm trong hai lock chính thức trước khi chép. Gói có 17 tệp, 11 MB.
- API đi qua gói này **tái lập đúng kết quả test chính thức**: 12 dòng (Popularity, PureSVD, M1, ALS × K = 5/10/20) và 9 dòng M2 (N = 1/3/5 × K) khớp từng chỉ số với `metrics.csv` chính thức, sai khác không quá 1e-12. Nguồn: [check_release.json](chuong_5/check_release.json).
- Độ trễ HTTP trung vị của `POST /recommend` từ 2,8 ms (Popularity) đến 9,1 ms (M2, 3 nghệ sĩ) trên máy cục bộ. Nguồn: [latency.json](chuong_5/latency.json).
- ruff, ruff format, mypy (strict, 37 tệp) đạt; pytest **139 passed** (gồm cả test của H1 đang có trong cây làm việc).

## 2. Gói phát hành

Lệnh: `python scripts/export_release.py --version demo-chinh-thuc-20261026`. Nguồn từ [release_manifest.json](chuong_5/release_manifest.json).

| Thành phần | Nguồn | Kiểm tra |
| --- | --- | --- |
| PureSVD k=16, seed 42 | `chuong_4/tuning/pure_svd/pure_svd_lat16/model` | Khớp `model_sha256` trong `chuong_4/test/lock.json` |
| M1 (λ = 0,75, β = 0,5, C = 100) | `chuong_4/m1_pure_svd/seed_42/selected_model` | Khớp lock test |
| ALS (32 nhân tố, reg 0,1, a = 1), seed 42 | `chuong_4/tuning/implicit_als/implicit_als_lat32_reg0.1_con1/model` | Khớp lock test |
| M2 (α = 0,75, ngưỡng 10) | `chuong_4/m2_tuning/model` | Khớp `chuong_4/m2_test/lock.json` |
| train, validation | `chuong_3/run/representations` | Khớp `output_sha256` của run biểu diễn |
| Tên nghệ sĩ | `data/raw/hetrec2011/artists.dat` | Lưu mã băm trong manifest |
| Popularity | Fit lại trên train của gói | Giống test chính thức (thống kê xác định) |

Gói checkpoint tải từ máy đám mây (245 tệp) đã khớp toàn bộ `SHA256SUMS_checkpoints_demo.txt`. Khi nạp, API kiểm lại đủ tập tệp và mã băm của từng tệp; thiếu, thừa hoặc lệch đều từ chối khởi động.

## 3. Định tuyến

| Đầu vào | Nhánh | Mô hình | `fallback_used` |
| --- | --- | --- | --- |
| `user_id` có trong train | `existing_user` | `pure_svd` (mặc định), `m1` hoặc `implicit_als`; che train + validation như giao thức test | false |
| `user_id` không có | lỗi 404 | | |
| `history` 1–5 nghệ sĩ | `new_user` | M2 với đúng các nghệ sĩ đã chọn | false; true nếu không nghệ sĩ nào nằm trong danh mục M2 (khi đó M2 chỉ còn thành phần phổ biến) |
| `history` rỗng | `popularity` | Popularity | true, `empty_profile` |

Hai điểm cần ghi vào báo cáo:

1. **Số lượt nghe của người dùng mới.** Người dùng demo chỉ chọn nghệ sĩ, không nhập số lượt nghe. Khi thiếu, API gán số lượt nghe ứng với mức proxy giữa (log2(1 + c) nằm giữa ngưỡng 40% và 60% mà M2 học trên train). Trên test chính thức, M2 dùng số lượt nghe thật. Đây là giả định của giao diện demo, không phải của mô hình. Phép kiểm tra ở mục 4 truyền số lượt nghe thật nên vẫn khớp.
2. **Nghệ sĩ ngoài danh mục M2** vẫn được tính vào kích thước hồ sơ, giống test chính thức, và được trả về trong `ignored_item_ids`.

## 4. Kiểm tra khớp kết quả offline

Lệnh: `python scripts/check_release.py --release artifacts/releases/demo-chinh-thuc-20261026 --output-dir outputs/demo/check_release_20261027`. Thời gian chạy 40 giây.

- Người dùng có sẵn: 1.877 người, top-20 qua `DemoService`, chấm bằng `evaluate_ranking` với đích test. So 8 chỉ số (precision, recall, NDCG, coverage, Gini, ARP, novelty, ILD) với [test/metrics.csv](chinh_thuc_cloud_20261026/test/metrics.csv) ở seed 42: **0 dòng lệch**.
- Người dùng mới: 189 người để dành có ít nhất 5 tương tác train, cùng hồ sơ N = 1/3/5 như test M2, qua `DemoService.recommend_new`. So với [m2/test/metrics.csv](chinh_thuc_cloud_20261026/m2/test/metrics.csv): **0 dòng lệch**.

Thời gian gợi ý toàn bộ người dùng trong lần kiểm tra (trong tiến trình, không qua HTTP): PureSVD 4,86 s, M1 9,13 s, ALS 5,57 s cho 1.877 người; M2 khoảng 1,0 s cho 189 người ở mỗi N. Nạp gói mất 0,73 s.

## 5. API

| Endpoint | Mục đích |
| --- | --- |
| `GET /health` | Phiên bản gói và cấu hình từng mô hình |
| `GET /users?offset=&limit=` | Danh sách người dùng train kèm số nghệ sĩ đã nghe |
| `GET /users/{id}/history?limit=` | Nghệ sĩ train + validation, xếp theo lượt nghe, có nhãn split |
| `GET /artists?q=&limit=` | Tìm nghệ sĩ trong danh mục M2 theo tên, nhiều người nghe trước |
| `POST /recommend` | `user_id` + `model`, hoặc `history` (0–5 nghệ sĩ, lượt nghe tùy chọn); trả nhánh, mô hình, fallback, tên, ảnh, số người nghe từng nghệ sĩ và trung bình (ARP của một danh sách) |

CORS đọc `MUSICREC_CORS_ORIGINS` (mặc định `localhost:3000`); gói đọc `MUSICREC_RELEASE_DIR`. Ví dụ thật với user 2, K = 5: PureSVD có số người nghe trung bình 178,0, M1 164,8.

## 6. Độ trễ

Đo bằng `scripts/measure_latency.py`, 50 lần mỗi endpoint sau một lần khởi động, uvicorn một tiến trình, gọi từ cùng máy. Máy: Intel Core i5-11300H 3,10 GHz, 8 luồng, 15,7 GB RAM, Windows 11, Python 3.11.9, fastapi 0.141.1, uvicorn 0.52.4, numpy 2.4.6, scipy 1.17.1, pandas 2.3.3.

| Endpoint | Trung vị (ms) |
| --- | --- |
| `GET /health` | 2,2 |
| `GET /users` (2.000) | 10,8 |
| `GET /users/2/history` | 7,0 |
| `GET /artists?q=the` | 15,6 |
| `POST /recommend` PureSVD | 5,2 |
| `POST /recommend` M1 | 7,3 |
| `POST /recommend` ALS | 5,9 |
| `POST /recommend` M2, 3 nghệ sĩ | 9,1 |
| `POST /recommend` Popularity | 2,8 |

p95 và giá trị lớn nhất nằm trong [latency.json](chuong_5/latency.json). Đây là số trên máy cục bộ, chưa phải trên host triển khai.

## 7. Streamlit dự phòng

`streamlit run src/musicrec/ui/app.py` khi API đang chạy. Có hai tab: người dùng có sẵn (lịch sử, chọn mô hình, so PureSVD và M1 cạnh nhau kèm số người nghe trung bình) và người dùng mới (tìm, chọn tối đa 5 nghệ sĩ). Đã chạy thử bằng `streamlit.testing` với API thật: không có lỗi, ba nhánh hiển thị đúng.

## 8. Khác với kế hoạch và việc cần sửa báo cáo

- Kế hoạch ghi `GET /users` là "danh sách mẫu"; bản cài đặt trả toàn bộ 1.877 người dùng có phân trang.
- Báo cáo mục 5.3 đang mô tả Streamlit là giao diện chính. Cần sửa sau khi frontend Next.js xong: Next.js là giao diện chính, Streamlit là bản dự phòng, kèm giả định lượt nghe ở mục 3.
- Chưa triển khai lên host (P6). Gói 11 MB nên vừa với các host miễn phí, nhưng chưa đo bộ nhớ trên host.
