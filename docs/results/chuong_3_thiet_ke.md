# Chương 3 bước 3.3: thiết kế đã chốt cho 3.6–3.8 và đề xuất sửa báo cáo

Ngày: 26/10/2026. Đây là bước 3.3 trong [ROADMAP](../ROADMAP.md). Nội dung dựa trên bốn quyết định ngày 26/10 (Q3, Q4, Q6, Q7) và kết quả tinh chỉnh trong [chuong_4.md](chuong_4.md). Mục 3.8 (M2) đã chốt theo Q5.

Các tham số dưới đây lấy từ cấu hình chạy thật, không phải từ kế hoạch. Nguồn: trường `config` trong `metrics.json` của từng run đã chọn.

## 1. Bảng tham số cuối (thay Bảng 3.3 của bản v15)

| Mô hình | Đầu vào | Tham số đã chốt | Xử lý khi không chấm được điểm |
| --- | --- | --- | --- |
| Random | Danh mục train | seed 42, mỗi người một chuỗi sinh riêng `musicrec-random-v1:42:{user_id}` | Người dùng mới nhận cùng cách sinh |
| Popularity | Count gốc của cặp train | Điểm = tổng log2(1 + count) theo nghệ sĩ; hòa điểm sắp theo mã nghệ sĩ tăng dần | Không cần |
| UserCF | Ma trận điểm đại diện 1–5 | L = 20 láng giềng, shrinkage = 0, cosine toàn véc-tơ, tối thiểu 1 nghệ sĩ chung | Trung bình của người dùng; người dùng mới dùng trung bình chung |
| ItemCF | Ma trận điểm đại diện 1–5 | L = 20, shrinkage = 0, cosine toàn cột, tối thiểu 1 người nghe chung | Như UserCF |
| SVD có độ lệch | Cặp quan sát, điểm đại diện | d = 16, η = 0,001925, λreg = 0,01025, tối đa 100 vòng, patience 5, chọn vòng theo NDCG@10 validation (vòng chọn: 2) | Trung bình chung cộng độ lệch nghệ sĩ |
| PureSVD | Ma trận **nhị phân**, ô thiếu = 0 | k = 16, ARPACK (`svds`), tolerance 1e-10, không trừ trung bình, không chuẩn hóa, không độ lệch | Hồ sơ rỗng, sắp theo thứ tự ánh xạ |
| M1 | Top-100 ứng viên của PureSVD k=16 | C = 100, λ = 0,75, β = 0,5 | Khi tập đã chọn rỗng, phần phạt tương đồng bằng 0 |
| Implicit ALS (mở rộng) | Confidence 1 + ln(1 + count) | 32 nhân tố, reg = 0,1, a_conf = 1, tối đa 50 vòng, patience 5 (vòng chọn: 16) | Hồ sơ rỗng |

Quy ước chung cho mọi mô hình: chỉ học từ tập train; điểm không bị cắt; hòa điểm làm tròn 12 chữ số rồi sắp theo thứ tự ánh xạ số; một luồng BLAS.

## 2. Đề xuất sửa từng mục của báo cáo

### 2.1 Mục 1.3.2 và phần mô tả Chương 2 (do Q3)

Giữ nguyên sáu mô hình đối sánh. Implicit ALS **không** đưa vào mục tiêu, cơ sở lý thuyết hay thiết kế, mà trình bày như một thực nghiệm mở rộng trong Chương 4. Cần thêm một câu ở cuối 1.3.2 hoặc 1.7, đại ý:

> Ngoài sáu mô hình đối sánh, khóa luận thực hiện thêm một thực nghiệm mở rộng với mô hình phân rã ma trận cho phản hồi ngầm (implicit ALS). Kết quả của thực nghiệm này được trình bày riêng ở Chương 4 và không thuộc phép so sánh chính.

### 2.2 Mục 3.6.3 (mô hình láng giềng)

Bản v15 viết: khi không có láng giềng hợp lệ hoặc mẫu số bằng 0, "hệ thống chuyển sang M2 hoặc phương án dự phòng đã ghi". Trong giao thức đánh giá chính, code **không** gọi M2. UserCF và ItemCF dùng trung bình điểm quan sát của chính người dùng, còn người dùng chưa có trong ánh xạ dùng trung bình chung. M2 chỉ hoạt động trong giao thức người dùng nguội riêng.

Đề xuất sửa thành:

> Nếu không có láng giềng hợp lệ hoặc mẫu số bằng 0, mô hình dùng trung bình điểm quan sát của người dùng; với người dùng chưa có trong ánh xạ huấn luyện, mô hình dùng trung bình chung của tập huấn luyện. Mô-đun M2 không tham gia giao thức đánh giá chính; M2 được đánh giá riêng theo giao thức người dùng nguội ở mục 3.8.

Thêm vào 3.6.3 dòng tham số đã chốt: L = 20, shrinkage = 0, tối thiểu một đối tượng chung.

### 2.3 Mục 3.6.4 (PureSVD, do Q7)

Bản v15 mô tả PureSVD dùng "cùng ma trận R" với các mô hình điểm đại diện. Thực tế bảng chính dùng **ma trận nhị phân**. Đề xuất bổ sung:

> PureSVD trong bảng kết quả chính dùng ma trận tương tác nhị phân với k = 16. Khóa luận cũng đã so sánh ba biểu diễn (nhị phân, log-count, điểm đại diện) tại cùng số chiều trên tập xác thực; biểu diễn nhị phân cho NDCG@10 cao nhất và được chọn trước khi mở tập kiểm thử. Hai biểu diễn còn lại được báo cáo trong bảng phụ.

Cũng cần nói rõ RMSE không áp dụng cho PureSVD, vì điểm của nó là điểm liên kết, không phải điểm đại diện đã hiệu chỉnh.

### 2.4 Mục 3.7 (M1, do Q4)

Đề cương V2 ghi nền của M1 là SVD; code trước đây chạy trên ALS. Đã chốt dùng **PureSVD nhị phân k = 16**. Đề xuất bổ sung vào 3.7.1:

> Mô hình nền của M1 là PureSVD với biểu diễn nhị phân và k = 16, tức mô hình cho NDCG@10 cao nhất trong sáu mô hình đối sánh trên tập xác thực. Tập ứng viên gồm C = 100 nghệ sĩ đứng đầu của mô hình nền sau khi loại lịch sử.

Trong 3.7.3, nêu rõ tham số đã chọn (λ = 0,75, β = 0,5) được chọn trên tập xác thực theo quy tắc đặt trước: trong các biến thể đầy đủ có mức giảm NDCG@10 không quá 5%, chọn ARP thấp nhất, rồi ILD cao nhất, rồi NDCG cao nhất.

Một điểm cần ghi trung thực: PureSVD cho kết quả giống hệt ở cả ba hạt giống 42, 43 và 44, vì hạt giống chỉ đổi véc-tơ khởi đầu của ARPACK. Vì vậy phần chạy lại ở hai hạt giống còn lại **không phải là kiểm chứng độc lập**, và báo cáo không nên mô tả nó như bằng chứng về độ ổn định.

### 2.5 Mục 3.8 (M2)

Đã chốt theo Q5 (26/10): giữ phép chia người dùng và chấm 189 người để dành trên tập kiểm thử. Đề xuất viết lại 3.8 như sau:

> M2 được đánh giá theo giao thức người dùng mới riêng. Người dùng của tập train được xáo một lần theo hạt giống 42 rồi chia thành nhóm học (80%, 1.501 người), nhóm tinh chỉnh (10%, 187 người) và nhóm để dành (189 người). Mọi thành phần của M2 (điểm đại diện, ItemCF với L = 40, từ vựng thẻ và IDF, độ phổ biến) chỉ học từ dữ liệu train của nhóm học; danh mục gồm 13.210 nghệ sĩ. Với mỗi người dùng đánh giá, hệ thống chỉ nhận N ∈ {0, 1, 3, 5} nghệ sĩ đầu tiên của một thứ tự xáo cố định trên lịch sử train của họ. Cấu hình (α, ngưỡng lịch sử) được chọn trên tập xác thực của nhóm tinh chỉnh theo NDCG@10 trung bình ở N = 1, 3, 5; nhóm để dành chỉ được chấm một lần trên tập kiểm thử sau khi cấu hình đã khóa.

Thêm vào 3.8 dòng tham số: lưới α ∈ {0,25; 0,5; 0,75}, ngưỡng ∈ {3, 5, 10}; thẻ chỉ giữ nếu xuất hiện ở ít nhất 2 nghệ sĩ. Kết quả ở [chuong_4_m2.md](chuong_4_m2.md).

### 2.6 Mục 4.4 (không gian siêu tham số)

Bảng 4.3 của bản v01 ghi ngân sách "tối đa 30 cấu hình mỗi họ mô hình" bằng tìm kiếm ngẫu nhiên. Ngân sách thực tế nhỏ hơn: UserCF 12, ItemCF 12, SVD 12, PureSVD 4, ALS 8, tổng 48. UserCF, ItemCF và PureSVD quét toàn bộ lưới; chỉ SVD dùng tìm kiếm ngẫu nhiên (cấu hình đầu cộng 11 cấu hình sinh bằng hạt giống 42). Báo cáo cần ghi đúng con số này và ghi thêm hạn chế: cấu hình tốt nhất của UserCF, ItemCF (L = 20) và PureSVD (k = 16) nằm ở biên dưới của lưới, và nhóm giữ nguyên lưới đã định trước thay vì mở rộng sau khi thấy kết quả.
