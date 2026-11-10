# Kết quả Chương 5: hệ thống FastAPI và Next.js (bằng chứng cho báo cáo v18)

Ngày chạy: 07/11/2026, máy cá nhân của nhóm (Windows 11, Intel Core i5-11300H 3,10 GHz, 8 luồng logic; Python 3.11.9; FastAPI 0.141.1, uvicorn 0.52.4, numpy 2.4.6, scipy 1.17.1, pandas 2.3.3). Gói mô hình `artifacts/releases/demo-chinh-thuc-20261026` (mô hình đã khóa ở Chương 4). Bản trước: [chuong_5_backend.md](chuong_5_backend.md), [chuong_5_frontend.md](chuong_5_frontend.md).

## Tóm tắt

- **12/12 ca kiểm thử chức năng đạt** trên gói thật, gọi qua HTTP bằng TestClient. Bộ kiểm thử của dự án: **145 passed**.
- **API và đánh giá ngoại tuyến trùng hoàn toàn**: top-10 qua `POST /recommend` so với top-10 tính trực tiếp từ checkpoint gốc trong `outputs/` (không qua gói), 1.877 người dùng × PureSVD, M1, ALS và 189 người để dành × M2 ở N = 1, 3, 5: trùng 100% cả thứ tự, Jaccard 1, chênh điểm 0.
- **Độ trễ** (20 lượt khởi động, 200 lượt đo, HTTP cục bộ): trung vị `POST /recommend` từ 3,78 ms (Popularity) đến 11,46 ms (M1).
- **Nạp gói**: 18 tệp, 10,67 MB; từ khởi động tiến trình tới dịch vụ sẵn sàng 2,75 / 2,22 / 2,12 giây (ba tiến trình mới).
- Giao diện chính là **Next.js** (5 trang); Streamlit giữ làm dự phòng. Báo cáo v18 viết Chương 5 theo hướng này.

## 1. Lệnh

```bash
.venv/Scripts/python.exe -B scripts/check_chuong_5.py --output-dir outputs/demo/chuong_5_20261107
.venv/Scripts/python.exe -m uvicorn musicrec.api.main:app --port 8000
.venv/Scripts/python.exe scripts/measure_latency.py --output-dir outputs/demo/latency_20261107
.venv/Scripts/python.exe scripts/ve_hinh_chuong_5.py --output outputs/demo/chuong_5_20261107/anh/hinh_5_1_cay.png
```

`measure_latency.py` được sửa: thêm `--warmup` (mặc định 20) và `--repeats` (mặc định 200), báo thêm trung bình và độ lệch chuẩn. Lần đo 27/10 dùng 1 lượt khởi động và 50 lượt đo nên số khác.

Ảnh giao diện chụp bằng Edge không giao diện (playwright-core trong thư mục tạm, không cài vào dự án), API cổng 8000 và `next dev` cổng 3000, ẩn nút công cụ phát triển của Next.js.

## 2. Ca kiểm thử

Nguồn: [ca_kiem_thu.csv](chuong_5/bo_sung_20261107/ca_kiem_thu.csv).

| Mã | Nội dung | Kết quả |
| --- | --- | --- |
| T01 | Người dùng 2, PureSVD, K = 10: 10 mục, không trùng, không thuộc lịch sử | Đạt |
| T02 | Lịch sử rỗng → Popularity, `fallback_reason = empty_profile` | Đạt |
| T03 | Một nghệ sĩ trong danh mục M2 → nhánh M2, không dự phòng | Đạt |
| T04 | Chỉ nghệ sĩ ngoài danh mục → dự phòng, liệt kê `ignored_item_ids` | Đạt |
| T05 | K = 100 với ALS → 100 mục khác nhau | Đạt |
| T06 | K = 0, −1, "abc", 101 → 422 | Đạt |
| T07 | M1 với λ = 1, β = 0 trùng thứ tự PureSVD; M1 đã chọn khác PureSVD 3/10 mục | Đạt |
| T08 | Mô hình `svd` → 422 | Đạt |
| T09 | Cùng yêu cầu hai lần → JSON giống hệt | Đạt |
| T10 | Nạp lại gói trong ứng dụng mới → JSON giống hệt | Đạt |
| T11 | Người dùng không tồn tại → 404 (recommend, history) | Đạt |
| T12 | Thiếu cả user_id và history; nghệ sĩ trùng; quá 5; lượt nghe âm; λ ngoài lưới → 422 | Đạt |

Khác thiết kế GVHD: API không có `/models`, `model_version`, `use_m1`; mô hình chọn bằng trường `model`, M1 là một giá trị của `model`. Giao diện không đặt thời gian chờ riêng cho lời gọi API (ghi vào Hạn chế).

## 3. Độ trễ (ms)

Nguồn: [latency.json](chuong_5/bo_sung_20261107/latency.json).

| Cấu hình | Trung bình | Trung vị | Độ lệch chuẩn | P95 |
| --- | --- | --- | --- | --- |
| PureSVD | 8,28 | 8,06 | 1,58 | 11,23 |
| M1 | 11,97 | 11,46 | 4,34 | 18,08 |
| ALS | 8,34 | 7,51 | 3,40 | 13,07 |
| M2 (3 nghệ sĩ) | 11,35 | 10,88 | 2,14 | 15,98 |
| Popularity (lịch sử rỗng) | 3,87 | 3,78 | 0,92 | 5,58 |

Chỉ đo từ phía người gọi; chưa đo riêng thời gian xử lý bên trong dịch vụ.

## 4. Thay đổi trong báo cáo v18

Báo cáo [v18](../bao-cao/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_v18_07-11-2026.docx), dựng lại từ bản góp ý bằng `docs/bao-cao/nguon_v17/dung_v18.ps1`:

- Chương 4 như v17, thêm trích dẫn SciPy [31].
- Chương 5 viết mới: 5.1–5.4 theo hệ thống thật (7 bảng, 5 hình), xóa mục 5.5 cũ, đánh số lại 5.5–5.8; tài liệu [32]–[38] (FastAPI, Next.js, Streamlit, LFM-2b, BPR, EASE, LightGCN; thông tin xuất bản kiểm tra qua tìm kiếm web ngày 07/11).
- Chương 1: RQ2 theo Given-N, 1.2.1 viết lại, đổi số 1.6/1.7, thêm câu kiểm định, mục tiêu 5 và cấu trúc báo cáo đổi sang giao diện web/Next.js. Số liệu IFPI (69,6%, 837 triệu) và Spotify (56 triệu, 77%) khớp nguồn công bố, không đổi.
- Chương 2: thêm đoạn implicit ALS và đoạn M1 kế thừa gì từ MMR [18], Abdollahpouri [19].
- Chương 3: 3.7.3 ghi ngưỡng 5% là ngưỡng đặt trước, trỏ tới lưu ý tính vòng tròn ở 4.7.
- Bỏ Phụ lục C. Thêm trang Abstract tiếng Anh theo mẫu khoa. Sửa câu cuối Lời cảm ơn.

**Còn lại**: mục “Các nghiên cứu liên quan” trên Last.fm HetRec 2011 ở Chương 2 (cần đọc bài gốc để ghi giao thức và chỉ số; chữ đỏ của GVHD tại đầu Chương 2 vẫn giữ), và khối nhận xét tổng quát của GVHD ở đầu báo cáo (sẽ xóa khi xong toàn bộ).

## Kiểm thử tải (11/11/2026, bổ sung theo góp ý GVHD ngày 10/11)

Lệnh: `uvicorn musicrec.api.main:app --port 8010` (một tiến trình) rồi `python scripts/load_test.py --output-dir outputs/demo/load_20261111 --requests 1000 --warmup 50`. Yêu cầu: `POST /recommend`, người dùng có sẵn, PureSVD, K = 10, mã người dùng luân phiên trong 200 người đầu. Máy: Windows 11, Intel Core i5-11300H, 8 luồng logic; Python 3.11.9, FastAPI 0.141.1, uvicorn, requests, numpy, scipy theo phiên bản ghi trong tệp nguồn. Chương trình gửi và dịch vụ chạy trên cùng máy. Mẫu thử 100 yêu cầu ở mức 1 và 8 chạy hết 1,6 giây nên chạy đủ ngay.

| Số yêu cầu đồng thời | Số yêu cầu | Thông lượng (yêu cầu/giây) | Trung vị (ms) | P95 (ms) | Lỗi (%) |
| --- | --- | --- | --- | --- | --- |
| 1 | 1.000 | 197,4 | 4,90 | 6,57 | 0,00 |
| 8 | 1.000 | 347,3 | 22,19 | 33,42 | 0,00 |
| 32 | 1.000 | 331,2 | 90,33 | 146,00 | 0,00 |

Nguồn: [chuong_5/load_test.json](chuong_5/load_test.json). Ví dụ phản hồi thật dùng cho Đoạn mã 5.1 của báo cáo: [chuong_5/vi_du_recommend.json](chuong_5/vi_du_recommend.json) (người dùng mới chọn Lady Gaga, Britney Spears, Christina Aguilera; K = 3; kết quả Madonna, Rihanna, Katy Perry).
