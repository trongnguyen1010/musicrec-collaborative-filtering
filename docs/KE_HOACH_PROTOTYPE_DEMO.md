# Kế hoạch prototype demo: backend FastAPI, Streamlit dự phòng, frontend Next.js

Ngày lập: 27/10/2026, cập nhật P1, P4, A2, A3 cùng ngày. Trạng thái: **đã duyệt 27/10/2026**. Giai đoạn A xong ngày 27/10/2026, kết quả ở [chuong_5_backend.md](results/chuong_5_backend.md). Giai đoạn B (trừ deploy) xong cùng ngày, kết quả ở [chuong_5_frontend.md](results/chuong_5_frontend.md).

Hướng đã được người dùng đồng ý ngày 27/10/2026: frontend Next.js deploy lên Vercel; backend FastAPI chạy riêng ở một host Python hoặc chạy cục bộ; giữ một trang Streamlit tối giản làm bản dự phòng. Mốc lấy từ [kế hoạch hiện hành](WEEKLY_IMPLEMENTATION_PLAN.md): chốt mô hình 15/11, bản tích hợp đầu 20/11, demo đủ luồng 22/11, sẵn sàng nội bộ 27/11, dự phòng 28–30/11.

## 1. Hiện trạng (đã đọc code ngày 27/10/2026)

| Thành phần | Hiện trạng |
| --- | --- |
| API | [main.py](../src/musicrec/api/main.py): `GET /health`, `POST /recommend`; Popularity dựng từ 2 tương tác mẫu, không nạp mô hình thật |
| Schema | [schemas.py](../src/musicrec/api/schemas.py): nhận `user_id` hoặc `history`, `k` từ 1 đến 100; trả `model_version`, `fallback_used`, `recommendations` gồm `item_id`, `score`, `reason` |
| Service | [service.py](../src/musicrec/serving/service.py): bọc một recommender; `fallback_used` luôn là false |
| UI | [app.py](../src/musicrec/ui/app.py): Streamlit 24 dòng, gọi API, hiện JSON thô |
| Export | [export_release.py](../scripts/export_release.py): ném `NotImplementedError` |
| Artifact có trên máy | `outputs/chinh_thuc_cloud_20261026/`: representations seed 42 và ba checkpoint ALS, đã khớp `SHA256SUMS` và lock |
| Artifact chưa có trên máy | PureSVD, M1, M2 của lần chạy chính thức (lock có mã băm, máy đám mây của thread lộ trình còn giữ bản gốc) |
| Tên nghệ sĩ | `data/raw/hetrec2011/artists.dat` (id, name, url, pictureURL) |

## 2. Quyết định cần duyệt trước khi viết code

| Mã | Câu hỏi | Đề xuất của Claude |
| --- | --- | --- |
| P1 | Mô hình cho user đã có lịch sử | **PureSVD k=16 với công tắc M1** (bật = M1 λ=0,75, β=0,5 trên chính PureSVD đó). M1 chính thức đặt trên PureSVD (Q4, [chuong_4.md](results/chuong_4.md) mục 3), nên so bật/tắt M1 phải là PureSVD với M1(PureSVD), không phải ALS. **ALS seed 42** chỉ là lựa chọn phụ "mô hình NDCG test cao nhất", không có công tắc M1. Phạm vi chốt trước đó ghi "ALS (bật/tắt M1)" nên cần người dùng xác nhận sửa |
| P2 | Mô hình cho user mới nhập vài nghệ sĩ | **M2** (α = 0,75, ngưỡng 10), đúng mô hình đã chấm. Giao diện phải ghi trung thực: trên test, M2 không hơn Popularity về NDCG@10 nhưng đa dạng hơn |
| P3 | Hồ sơ rỗng | Popularity, `fallback_used = true` |
| P4 | Cách có artifact M2, PureSVD, M1 | **Chép bản gốc** từ máy đám mây (thread lộ trình còn giữ `outputs/chinh_thuc_cloud_20261026`): đóng zip PureSVD, M1, M2 kèm `SHA256SUMS`, người dùng tải về và giải nén vào đúng thư mục; script kiểm từng tệp khớp mã băm trong lock trước khi dùng. Không fit lại. Fit lại cục bộ chỉ là phương án dự phòng nếu máy đám mây không còn |
| P5 | Phạm vi "đã nghe" khi demo user có sẵn | Che train + validation của user, như giao thức test |
| P6 | Host backend | Hugging Face Spaces, Render hoặc Railway; người dùng tự tạo tài khoản. Luôn có phương án chạy cục bộ |
| P7 | Kết quả tính sẵn cho Vercel | Không bắt buộc ở vòng đầu; chỉ làm nếu host backend gặp vấn đề |

## 3. Giai đoạn A: backend và Streamlit dự phòng (đến 15/11)

| Bước | Việc | Đầu ra và kiểm tra |
| --- | --- | --- |
| A1 | Export release: `scripts/export_release.py` chép artifact đã ghim vào `artifacts/releases/<version>/`, kèm `manifest.json` (mã băm, lock nguồn, git sha, mapping, bảng tên nghệ sĩ) | Không ghi đè; kiểm mã băm khi nạp. `artifacts/releases/*` đã bị git ignore |
| A2 | Đưa PureSVD, M1, M2 bản gốc về máy (zip từ máy đám mây), `scripts/verify_release_inputs.py` so mã băm từng tệp với lock | Báo cáo khớp/lệch; lệch thì dừng, không dùng |
| A3 | Service định tuyến: user có trong checkpoint → PureSVD, `m1=true` thì qua M1 (hoặc `model=als`); có `history` 1–5 nghệ sĩ mà không có `user_id` → M2; hồ sơ rỗng hoặc mọi nghệ sĩ nhập không có trong catalog → Popularity | `reason` và `fallback_used` đúng cơ chế; không gợi ý lại nghệ sĩ đã có; kết quả kèm số người nghe để hiện độ phổ biến khi bật/tắt M1 |
| A4 | API: `GET /health` (phiên bản từng mô hình), `GET /artists?q=` (tìm tên), `GET /users` (danh sách mẫu), `GET /users/{id}/history`, `POST /recommend` thêm trường `model` và tên nghệ sĩ trong kết quả; bật CORS cho domain Vercel | Giữ tương thích schema cũ khi có thể |
| A5 | Test: contract test cho mọi endpoint; API khớp suy luận offline cho cùng đầu vào (ALS so với `recommendations.csv` đã khóa; M2 so với kết quả `rank_scores` offline); khởi động lại cho kết quả như cũ | ruff, mypy src, pytest đều đạt |
| A6 | Streamlit tối giản: chọn user hoặc chọn nhiều nghệ sĩ theo tên, chọn K và mô hình, bảng kết quả có tên, lý do, số người nghe; khung lịch sử user | Chạy bằng một lệnh, chỉ gọi API |
| A7 | Đo độ trễ từng endpoint trên máy demo, ghi cấu hình máy và phiên bản thư viện | Số đo thật, không ước đoán |

## 4. Giai đoạn B: frontend Next.js (16–22/11)

| Trang | Nội dung |
| --- | --- |
| Gợi ý | Chọn user có sẵn hoặc tìm và chọn nghệ sĩ; chọn K và mô hình; danh sách nghệ sĩ có tên, ảnh nếu còn link, điểm, lý do; báo rõ khi dùng fallback |
| Luồng hoạt động | Animation: dữ liệu Last.fm → làm sạch và chia → học mô hình → gợi ý toàn catalog → tái xếp hạng M1 hoặc nhánh M2 hoặc fallback → kết quả; mỗi bước liên kết với số thật đã đo |
| Kết quả thực nghiệm | Bảng NDCG, coverage, ARP từ `docs/results` (dữ liệu tĩnh), có nhãn bằng chứng |

Deploy: Vercel cho frontend, backend ở host đã chọn ở P6. Trước buổi bảo vệ phải gọi backend cho chạy sẵn. Nếu Next.js chưa xong ngày 22/11 thì demo bằng Streamlit ở giai đoạn A.

## 5. Giai đoạn C: hoàn thiện (23–27/11)

Sửa lỗi; chạy lại trong môi trường sạch theo README; đo thời gian; luyện demo ít nhất ba lần; quay video dự phòng; đồng bộ Chương 3 (kiến trúc demo đổi sang Next.js + FastAPI) và Chương 5 của báo cáo khi người dùng yêu cầu. Báo GVHD việc đổi công nghệ frontend so với phiếu đề tài (Streamlit, Flask hoặc Django).

## 6. Câu hỏi cho người dùng

- Ai trong nhóm quen React/Next.js? Nếu chưa ai quen, Claude viết khung frontend và người trong nhóm chỉnh giao diện.
- Xác nhận P1 (PureSVD + công tắc M1, ALS là lựa chọn phụ) và P4 (chép bản gốc từ máy đám mây).

## 7. Những gì không làm

Không train trong request; không thêm mô hình mới (H2–H4 đưa vào hướng phát triển); không Docker, tracking server hay dashboard trước khi luồng chính ổn; không push hoặc deploy khi chưa được phép.
