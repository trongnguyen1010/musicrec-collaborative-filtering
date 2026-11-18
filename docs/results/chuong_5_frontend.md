# Kết quả Chương 5 (giai đoạn B): frontend Next.js

Ngày làm: 27/10/2026, trên máy cục bộ. Backend: [chuong_5_backend.md](chuong_5_backend.md). Mã nguồn: [frontend/](../../frontend/README.md).

## 1. Tóm tắt

- Next.js 16.4.3 (App Router, TypeScript, Tailwind CSS 4), React 19.3. Năm trang: giới thiệu, người dùng có sẵn, người dùng mới, luồng hoạt động, kết quả. Giao diện tiếng Việt, theo chế độ sáng/tối của máy, dùng được trên điện thoại (đã kiểm ở bề rộng 375 px: không tràn ngang).
- Mọi gợi ý lấy từ API thật. Mọi số liệu tĩnh (NDCG, ARP, quy mô dữ liệu, độ trễ, kết quả kiểm tra) sinh tự động bằng `scripts/export_frontend_data.py` từ các tệp kết quả đã lưu, không gõ tay.
- `tsc --noEmit`, `npm run lint`, `npm run build` đều đạt; năm trang được dựng tĩnh.
- Đã chạy thử với API thật trên trình duyệt: ba nhánh hoạt động đúng, xem mục 3.
- Chưa deploy lên Vercel và host backend. Việc này cần người dùng cho phép và tạo tài khoản.

## 2. Đáp ứng yêu cầu đã chốt

| Yêu cầu | Cách đáp ứng |
| --- | --- |
| Người dùng có sẵn | `/nguoi-dung`: chọn hoặc chọn ngẫu nhiên trong 1.877 user, lịch sử nghe (đánh dấu nghệ sĩ thuộc validation), K = 5/10/20 |
| So sánh bật/tắt M1 kèm độ phổ biến | Hai danh sách PureSVD và M1 cạnh nhau; mỗi nghệ sĩ có thanh số người nghe trên cùng thang log; số người nghe trung bình của từng danh sách và mức thay đổi; nhãn "M1 thêm" và "M1 bỏ"; nhắc số chính thức trên toàn test |
| Người dùng mới | `/nguoi-moi`: tìm theo tên, chọn tối đa 5, gợi ý M2 cập nhật ngay; hồ sơ rỗng chuyển Popularity kèm thông báo fallback |
| Trung thực về M2 | Ghi rõ dưới kết quả: trên test (N = 3) M2 có NDCG@10 thấp hơn Popularity, khác biệt không có ý nghĩa; M2 đa dạng hơn; demo gán mức nghe trung bình |
| Animation luồng | `/luong`: bảy bước tự chạy, có tạm dừng, đổi theo ba nhánh; mỗi bước kèm số liệu thật |

## 3. Chạy thử

Backend `uvicorn` cổng 8000 với gói `demo-chinh-thuc-20261026`, frontend `next start` cổng 3000.

- User 2, K = 10: PureSVD có số người nghe trung bình 182,6; M1 có 124,1 (giảm 32,0% với riêng user này); 7/10 nghệ sĩ chung. M1 bỏ Michael Jackson, The Killers, Radiohead và thêm Erasure, Keane, Dave Gahan.
- Người dùng mới chọn Lady Gaga: M2 trả 10 nghệ sĩ, cả hai thành phần cộng tác và nội dung đều có; số người nghe trung bình 271,7.
- Chưa chọn nghệ sĩ: nhánh Popularity, `fallback_used = true`.

Ảnh nghệ sĩ dùng link Last.fm năm 2011, phần lớn đã chết; giao diện tự đổi sang ô chữ cái đầu.

## 4. Việc còn lại

- Deploy (P6): chọn host backend, đặt `MUSICREC_CORS_ORIGINS` và `NEXT_PUBLIC_API_URL`. Cần người dùng tạo tài khoản và cho phép.
- Sửa báo cáo mục 5.3 sau khi được duyệt: Next.js là giao diện chính, Streamlit là dự phòng.
- Giai đoạn C: luyện demo, quay video dự phòng.

## 5. Nâng cấp giao diện "Sonic AI Lab" (27/10/2026, theo đề xuất của người dùng)

- Chỉ dùng nền tối `#07080C`, có quầng sáng nền và thẻ glass. Màu mang nghĩa: cyan/indigo cho PureSVD và độ chính xác, xanh ngọc cho M1 và mức đa dạng tăng, hổ phách cho thiên lệch phổ biến. Font Plus Jakarta Sans, số liệu dùng JetBrains Mono. Hiệu ứng dùng thư viện `motion` 12.
- Người dùng có sẵn: hai cột PureSVD và M1 có đường nối từng nghệ sĩ giữa hai thứ hạng, nhãn ▲/▼ đổi hạng, nhãn "mới" cho nghệ sĩ M1 thêm vào. Có công tắc "Áp dụng M1"; tắt công tắc tương đương λ = 1, β = 0, cho đúng thứ tự PureSVD (có test). Chọn λ và β chỉ trong **12 điểm của lưới validation** (λ ∈ {0,5; 0,75; 1}, β ∈ {0; 0,1; 0,25; 0,5}), kèm NDCG@10 và ARP validation của điểm đó; điểm khác cấu hình đã chọn được gắn nhãn rõ. API thêm `m1_lambda`, `m1_beta`, từ chối giá trị ngoài lưới.
- Người dùng mới: 5 ô slot, thẻ nghệ sĩ có hiệu ứng lò xo, banner đổi giữa "Popularity · dự phòng" và "M2 Hybrid", hiện trọng số ItemCF tối đa min(1, n/10).
- Luồng hoạt động: hai tầng OFFLINE (bước 1–3) và ONLINE (bước 4–7), có tia sáng chạy giữa các bước. Mỗi bước có hình minh họa nhỏ: mật độ ma trận, thanh chia tập (tính từ số tương tác), sơ đồ R ≈ U Σ Vᵀ với kích thước thật, công thức M1 và M2 viết đúng theo code.
- Kết quả: scatter ARP–NDCG@10 với biên Pareto tính từ bảng, radar 5 trục (chuẩn hóa min–max giữa 8 mô hình) đổi theo dòng hoặc điểm đang rê chuột, dấu ★ cho giá trị tốt nhất mỗi cột.

Hai điểm khác với đề xuất ban đầu, vì đề xuất không khớp số liệu hoặc code:

1. Công thức M1 trong đề xuất, (1 − λ)·r̂ − λ·Pop^β, không phải công thức đã cài. Đúng là: chọn tham lam i* = argmax [λ·rel(i) − (1 − λ)·max sim(i, j) − β·pop(i)] (configs/models/m1_pure_svd.yaml, src/musicrec/recommenders/m1.py).
2. Trên biên Pareto (test, K = 10) chỉ có Random, UserCF và Implicit ALS. ALS trội hơn cả PureSVD và M1 trên hai trục (NDCG 0,2175 so với 0,1828 và 0,1814; ARP 132,0 so với 174,2 và 146,9), nên M1 **không** nằm trên biên Pareto. Biểu đồ tính biên từ dữ liệu, không vẽ theo mong muốn.

Kiểm tra: tsc, eslint, next build đạt; ruff, mypy, pytest **145 passed**. Đã chạy thử với API thật (user 2: tắt M1 cho 10/10 nghệ sĩ chung và số người nghe trung bình 182,6 như PureSVD; bật M1 ở cấu hình đã chọn cho 124,1).

## 6. Chỉnh theo góp ý của người dùng (27/10/2026)

- Đổi sang tông lạnh pastel: xanh băng (PureSVD, độ chính xác), tím nhạt (M2), xanh bạc hà (M1, mức cải thiện), hồng nhạt (thiên lệch phổ biến). Bỏ tông cam. Cỡ chữ gốc tăng lên 17 px, chữ nhỏ nhất 12 px.
- Sửa lỗi thanh chia tập chỉ có màu ở đoạn Test: trong chế độ dev, Tailwind không sinh lớp `bg-cyan` và `bg-indigo` (trùng tên bảng màu mặc định). Bảng màu mới dùng tên riêng nên không còn xung đột.
- Người dùng có sẵn: thêm chú thích đường nối (nét đứt = nghệ sĩ rời khỏi danh sách khi bật M1) và dòng liệt kê nghệ sĩ bị rời; bỏ đoạn giải thích dài; căn các ô điều khiển cùng chiều cao; lịch sử nghe gọn còn 8 dòng, có "Xem thêm". So sánh hai cột chỉ cho K = 5 hoặc 10 để không quá dài.
- Người dùng mới: tên nghệ sĩ hiện dưới từng ô đã chọn, có nút bỏ chọn hết; kết quả phân trang 5 dòng một trang; phần ghi chú về kết quả M2 thu vào mục mở rộng.
- Luồng hoạt động: nút bằng chữ "Trước", "Tự chạy"/"Dừng tự chạy", "Sau" (mặc định không tự chạy); công thức viết bằng KaTeX kèm giải thích từng ký hiệu; nội dung từng bước viết đầy đủ hơn.

## 7. Chỉnh vòng 2 (27/10/2026)

- Màu chủ đạo xanh dương sáng `#4DA3FF`, nền phẳng `#0B1120`, bỏ gradient nền và gradient thẻ.
- Đường nối giữa hai cột PureSVD và M1 trước đây chỉ hiện đường ngang: các đường cong dùng màu dạng `var(--...)` trong thuộc tính SVG, trình duyệt của người dùng không vẽ. Đã đổi sang mã màu cố định; đường nối không còn hiệu ứng chuyển động.
- Thanh số người nghe trước đây trống trên trình duyệt của người dùng; đã đổi sang thanh một màu, độ dài theo số người nghe.
