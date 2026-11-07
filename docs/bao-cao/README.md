# Phiên bản báo cáo khóa luận

Xem [Quy tắc viết báo cáo khóa luận](QUY_TAC_VIET_BAO_CAO.md) trước khi soạn, cập nhật hoặc rà soát báo cáo.

Tên tệp: `33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_vNN_DD-MM-YYYY.docx`. Mỗi lần cập nhật báo cáo thì tăng số phiên bản và thêm một dòng vào bảng dưới đây (quy tắc ở [DEVELOPMENT_RULES.md](../../DEVELOPMENT_RULES.md#lưu-phiên-bản-báo-cáo-khóa-luận)).

## Góp ý của GVHD

| Ngày | Tệp gốc | Tóm tắt | Kế hoạch xử lý |
| --- | --- | --- | --- |
| 06/11/2026 | [GopY_GVHD_06-11-2026](GopY_GVHD_06-11-2026_KLTN_TrongNguyen_GiaKhang.docx) | [GOP_Y_GVHD_06-11-2026.md](GOP_Y_GVHD_06-11-2026.md) | [KE_HOACH_SUA_THEO_GOP_Y_GVHD.md](KE_HOACH_SUA_THEO_GOP_Y_GVHD.md) (chờ nhóm duyệt) |

## Các bản đang giữ

| Phiên bản | Ngày | Tệp | Nội dung | Gửi GVHD |
| --- | --- | --- | --- | --- |
| **v18 (hiện hành)** | 07/11/2026 | [v18](33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_v18_07-11-2026.docx) | Kế thừa v17, dựng lại từ bản góp ý GVHD bằng [nguon_v17/dung_v18.ps1](nguon_v17/dung_v18.ps1). Viết Chương 5 theo hệ thống thật FastAPI + Next.js (7 bảng, 5 hình; 12/12 ca kiểm thử, API trùng 100% với đánh giá ngoại tuyến), bỏ mục 5.5 cũ; sửa Chương 1 (RQ2 Given-N, 1.2.1, đổi số 1.6/1.7, câu kiểm định, mục tiêu 5), Chương 2 (implicit ALS, M1 kế thừa MMR và Abdollahpouri), 3.7.3; thêm Abstract; bỏ Phụ lục C; thêm tài liệu [31]–[38]. Còn chờ: mục nghiên cứu liên quan ở Chương 2, khối nhận xét tổng quát của GVHD. Chi tiết: [chuong_5.md](../results/chuong_5.md). | Chưa |
| v17 | 07/11/2026 | [v17](33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_v17_07-11-2026.docx) | Dựng từ [bản góp ý GVHD 06/11](GopY_GVHD_06-11-2026_KLTN_TrongNguyen_GiaKhang.docx). Viết lại toàn bộ Chương 4 theo khung 4.1–4.12 của GVHD bằng số liệu lần chạy chính thức 26/10 và phân tích bổ sung 07/11 ([chuong_4_bo_sung.md](../results/chuong_4_bo_sung.md)): 16 bảng, 7 hình, thêm ALS vào bảng chính (tách dòng), đường học SVD 100 vòng, phân nhóm ưa phổ biến, ILD theo thẻ, đường xử lý M2. Sửa NDCG@10 log-count ở 3.6.4 từ 0,153543 (không có nguồn) thành 0,154577. Các chương khác còn nguyên chữ đỏ, chữ xanh của GVHD. Nguồn dựng: [nguon_v17/](nguon_v17/). | Chưa |
| v16 | 26/10/2026 | [v16](33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_v16_26-10-2026.docx) | Kế thừa v15. Viết đầy đủ Chương 4 từ lần chạy chính thức 26/10 (tinh chỉnh, kiểm thử, kiểm định, M1, M2, ALS mở rộng, 15 bảng). Sửa 1.3.2, 3.6.3, 3.6.4, Bảng 3.3, 3.7, 3.8 theo thiết kế đã chốt; thêm tài liệu [27]–[30]; sửa cỡ chữ số thứ tự trong chú thích bảng/hình. Chương 5 vẫn chỉ có tiêu đề. | Chưa |
| v15 | 25/10/2026 | [v15](33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_v15_25-10-2026.docx) | Kế thừa v14; cập nhật mục 2.2.9, 3.10 (bộ đánh giá, Bước 6), Phụ lục B/C, thêm tài liệu [26]. Ch1–Ch3 có nội dung, Ch4–Ch5 chỉ có tiêu đề. | Chưa |
| v14 | 24/10/2026 | [v14](33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_v14_24-10-2026.docx) | Bổ sung chia tập, ánh xạ, bốn biểu diễn và ngưỡng train (Bước 4–5). Trước đây nằm ở `docs/reports/V14/`. | **Đã gửi** |
| v01 | 04/10/2026 | [v01](33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_v01_04-10-2026.docx) | Bản đầu tiên, cấu trúc cũ (Ch2 có 13 mục, Ch4–Ch5 viết dạng dự kiến). Trước đây là `BaoCao_KLTN_CaoTrongNguyen_LeKhacGiaKhang_V1.docx`. | Đã nộp trước đây |

## Các bản trung gian đã gỡ khỏi thư mục (ngày 26/10/2026)

Các bản này vẫn còn trong lịch sử Git tại commit `2615c35`; bấm liên kết để tải lại.

| Ngày | Tệp cũ | Ghi chú |
| --- | --- | --- |
| 04/10/2026 | [33_..._04-10-2026.docx](https://github.com/trongnguyen1010/musicrec-collaborative-filtering/blob/2615c35/docs/reports/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_04-10-2026.docx) | Trùng mã băm với v01. |
| 19/10/2026 | [33_..._19-10-2026.docx](https://github.com/trongnguyen1010/musicrec-collaborative-filtering/blob/2615c35/docs/reports/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_19-10-2026.docx) | Thêm kết quả EDA, cấu trúc cũ. |
| 20/10/2026 | [33_..._20-10-2026.docx](https://github.com/trongnguyen1010/musicrec-collaborative-filtering/blob/2615c35/docs/reports/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_20-10-2026.docx) | Bản cuối còn nội dung dự kiến Ch4–Ch5 (thiết kế E0–E6, lưới tham số, kiểm thử T01–T09); tóm tắt trong [ROADMAP](https://github.com/trongnguyen1010/musicrec-collaborative-filtering/blob/claude/project-thread-n6skg7/docs/ROADMAP.md). |
| 20/10/2026 | [V12/33_..._20-10-2026.docx](https://github.com/trongnguyen1010/musicrec-collaborative-filtering/blob/2615c35/docs/reports/V12/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_20-10-2026.docx) | Cấu trúc mới: Ch2 hai mục, Ch4–Ch5 chỉ tiêu đề. |
| 21/10/2026 | [33_..._21-10-2026.docx](https://github.com/trongnguyen1010/musicrec-collaborative-filtering/blob/2615c35/docs/reports/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_21-10-2026.docx) | Kết quả làm sạch (Bước 3). |
| 21/10/2026 | [V13/33_..._21-10-2026.docx](https://github.com/trongnguyen1010/musicrec-collaborative-filtering/blob/2615c35/docs/reports/V13/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_21-10-2026.docx) | Bản thứ hai trong ngày. |
| 24/10/2026 | [33_..._24-10-2026.docx](https://github.com/trongnguyen1010/musicrec-collaborative-filtering/blob/2615c35/docs/reports/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_24-10-2026.docx) | Bước 4, bản đầu trong ngày (trước v14). |
