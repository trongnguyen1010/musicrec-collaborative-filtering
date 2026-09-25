# BÁO CÁO TRÍCH XUẤT VÀ TỔNG HỢP TÀI LIỆU THAM KHẢO

**Đề tài Khóa luận:** Xây dựng hệ thống khuyến nghị nghệ sĩ âm nhạc dựa trên lọc cộng tác  
*(MusicRec: A Collaborative Filtering-based Music Artist Recommendation System)*  
**Cơ sở đối chiếu:** [DeCuongChiTiet_KLTN_XayDungHeThongKhuyenNghiAmNhac_ThamKhao.docx](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/DeCuongChiTiet_KLTN_XayDungHeThongKhuyenNghiAmNhac_ThamKhao.docx) và [Khao sat TQ.docx](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/Khao%20sat%20TQ.docx) cùng thư mục tài liệu gốc [docs/TLTK/](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/).

---

## MỤC LỤC
1. [Phần 1: Nhóm tài liệu nền tảng (8 tài liệu)](#phần-1-nhóm-tài-liệu-nền-tảng-8-tài-liệu)
   - [1. Resnick et al. (1994)](#1-resnick-et-al-1994)
   - [2. Sarwar et al. (2001)](#2-sarwar-et-al-2001)
   - [3. Koren, Bell, Volinsky (2009)](#3-koren-bell-volinsky-2009)
   - [4. Hu, Koren, Volinsky (2008)](#4-hu-koren-volinsky-2008)
   - [5. Herlocker et al. (2004)](#5-herlocker-et-al-2004)
   - [6. Cremonesi, Koren, Turrin (2010)](#6-cremonesi-koren-turrin-2010)
   - [7. Kowald, Schedl, Lex (2020)](#7-kowald-schedl-lex-2020)
   - [8. Ji et al. (2023)](#8-ji-et-al-2023)
2. [Phần 2: Nhóm tài liệu khảo sát và tổng quan (9 tài liệu)](#phần-2-nhóm-tài-liệu-khảo-sát-và-tổng-quan-9-tài-liệu)
   - [1. Song, Dixon, Pearce (2012)](#1-song-dixon-pearce-2012)
   - [2. Schedl, Zamani, Chen, Deldjoo, Elahi (2018)](#2-schedl-zamani-chen-deldjoo-elahi-2018)
   - [3. Schedl, Knees, McFee, Bogdanov, Kaminskas (2015)](#3-schedl-knees-mcfee-bogdanov-kaminskas-2015)
   - [4. Deldjoo, Schedl, Knees (2021)](#4-deldjoo-schedl-knees-2021)
   - [5. Lacic et al. (2024)](#5-lacic-et-al-2024)
   - [6. Ziaoddini et al. (2025)](#6-ziaoddini-et-al-2025)
   - [7. Ferraro et al. (2022)](#7-ferraro-et-al-2022)
   - [8. Shakespeare et al. (2020)](#8-shakespeare-et-al-2020)
   - [9. Doh, Choi, Nam (2025)](#9-doh-choi-nam-2025)
3. [Bảng tổng hợp đối sánh các công trình khảo sát và tổng quan](#bảng-tổng-hợp-đối-sánh-các-công-trình-khảo-sát-và-tổng-quan)

---

## PHẦN 1: NHÓM TÀI LIỆU NỀN TẢNG (8 TÀI LIỆU)

---

### 1. Resnick et al. (1994)
- **Tên bài báo:** *GroupLens: An Open Architecture for Collaborative Filtering of Netnews* (CSCW 1994)
- **Tập tin tài liệu:** [Resnick et al. 1994 (GroupLens).pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Resnick%20et%20al.%201994%20(GroupLens).pdf)
- **Đóng góp chính của bài báo:**
  - Khởi xướng hệ thống "GroupLens", đặt nền móng lịch sử cho kỹ thuật Lọc cộng tác dựa trên người dùng (**User-based Collaborative Filtering**).
  - Đưa ra giả định cốt lõi: *những người dùng từng có quan điểm/hành vi tương đồng trong quá khứ sẽ có xu hướng tiếp tục đồng thuận trong tương lai*.
  - Đề xuất công thức tính độ tương đồng bằng tương quan Pearson và mô hình dự đoán đánh giá dựa trên độ lệch có trọng số so với điểm trung bình của láng giềng.
- **Cách mô hình hoạt động (Định nghĩa & Ví dụ):**
  - **Định nghĩa:** Thay vì phân tích nội dung bài viết, hệ thống tìm ra những "người bạn cùng gu" (láng giềng gần nhất). Điểm dự đoán một bài viết cho bạn sẽ được tính dựa trên điểm đánh giá của những người bạn cùng gu này.
  - **Ví dụ hoạt động:**
    - *Bước 1 (Tìm bạn cùng gu):* Người dùng A và người dùng B cùng đọc báo tin tức. Cả hai đều chấm 5 sao cho bài viết X và 1 sao cho bài viết Y. Hệ thống xác định B có "gu" rất giống A.
    - *Bước 2 (Tìm bài viết tiềm năng):* Người dùng B vừa đọc một bài viết mới Z và chấm 5 sao, nhưng A chưa đọc bài Z.
    - *Bước 3 (Gợi ý):* Hệ thống dự đoán A cũng sẽ thích bài Z (khoảng 4.8 - 5 sao) và đẩy bài Z lên trang tin cá nhân của A.
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 1.1 (Bối cảnh và lý do chọn đề tài):** Căn cứ lý thuyết cho giả định nền tảng của họ thuật toán Lọc cộng tác.
  - **Mục 2.1 (Tổng quan hệ thống khuyến nghị):** Định nghĩa và phân loại nhánh tiếp cận Collaborative Filtering.
  - **Mục 2.3 (Lọc cộng tác dựa trên người dùng - User-based CF):** Cơ sở lý thuyết trực tiếp cho công thức tương quan Pearson (Công thức 2.2) và công thức dự đoán điểm số lệch trung bình (Công thức 2.3).
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Đưa vào **Bảng 2.2** (công trình nền tảng khởi nguồn cho User-based CF).
  - **Mục 3.6 & 3.6.1 (Các mô hình đề xuất / Thuật toán User-based CF):** Xây dựng **Thuật toán 3.1** (User-kNN).

---

### 2. Sarwar et al. (2001)
- **Tên bài báo:** *Item-Based Collaborative Filtering Recommendation Algorithms* (WWW 2001)
- **Tập tin tài liệu:** [Sarwar et al. 2001.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Sarwar%20et%20al.%202001.pdf)
- **Đóng góp chính của bài báo:**
  - Đề xuất giải thuật Lọc cộng tác dựa trên sản phẩm (**Item-based Collaborative Filtering**), giải quyết triệt để nút thắt cổ chai về khả năng mở rộng (scalability) và tốc độ phản hồi thời gian thực của User-based CF khi số người dùng tăng vọt.
  - Đưa ra độ đo tương đồng cosine điều chỉnh (**Adjusted Cosine Similarity**) trừ đi điểm trung bình của người dùng để triệt tiêu độ lệch thang đo đánh giá chủ quan.
  - Chứng minh mối quan hệ giữa các vật phẩm (items) ổn định hơn nhiều so với người dùng, cho phép tính toán trước ma trận tương đồng offline.
- **Cách mô hình hoạt động (Định nghĩa & Ví dụ):**
  - **Định nghĩa:** Thay vì so sánh người với người, hệ thống so sánh độ tương đồng giữa các sản phẩm dựa trên lịch sử mọi người cùng xem/mua chúng.
  - **Ví dụ hoạt động:**
    - *Bước 1 (Tính trước độ giống nhau giữa các ca sĩ):* Hàng triệu người dùng nghe nhạc trên hệ thống. Dữ liệu cho thấy hễ ai nghe nhiều bài của *Sơn Tùng M-TP* thì cũng thường nghe nhiều bài của *Soobin Hoàng Sơn*. Hệ thống tính ra 2 nghệ sĩ này "giống nhau" 90%.
    - *Bước 2 (Người dùng nghe nhạc):* Bạn mới tạo tài khoản và nghe liên tục 10 bài của *Sơn Tùng M-TP*.
    - *Bước 3 (Gợi ý tức thì):* Hệ thống tra cứu bảng độ giống nhau tính sẵn từ trước và lập tức gợi ý *Soobin Hoàng Sơn* cho bạn mà không cần phải quét qua hàng triệu người dùng khác.
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 1.1 (Bối cảnh và lý do chọn đề tài):** Căn cứ lựa chọn họ thuật toán lọc cộng tác cổ điển có tính khả thi triển khai cao.
  - **Mục 2.4 (Lọc cộng tác dựa trên sản phẩm - Item-based CF):** Cơ sở lý thuyết cho công thức Adjusted Cosine (Công thức 2.4), công thức dự đoán điểm số (Công thức 2.5) và phân tích ưu điểm tính toán trước offline.
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Đưa vào **Bảng 2.2** (công trình nền tảng cho Item-based CF).
  - **Mục 3.6 & 3.6.2 (Các mô hình đề xuất / Thuật toán Item-based CF):** Cài đặt **Thuật toán 3.2** (Item-kNN).
  - **Mục 4.4 & 4.8 (Thiết kế thí nghiệm & So sánh chi tiết theo nhóm mô hình):** Thí nghiệm **E2** và đối chiếu thực nghiệm giữa User-based CF và Item-based CF.

---

### 3. Koren, Bell, Volinsky (2009)
- **Tên bài báo:** *Matrix Factorization Techniques for Recommender Systems* (IEEE Computer 2009)
- **Tập tin tài liệu:** [KorenBellVolinsky2009.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/KorenBellVolinsky2009.pdf)
- **Đóng góp chính của bài báo:**
  - Tổng kết có hệ thống các kỹ thuật Phân rã ma trận (**Matrix Factorization - MF**) giúp đội ngũ chiến thắng giải thưởng 1 triệu USD Netflix Prize.
  - Mô hình hóa sở thích người dùng và đặc tính sản phẩm vào một không gian nhân tử tiềm ẩn chung (*latent factor space*) bằng tích vô hướng vector $p_u^T q_i$, đồng thời tích hợp các số hạng thiên lệch hệ thống (*global mean, user bias, item bias*).
  - Trình bày thuật toán tối ưu tham số bằng hạ độ dốc ngẫu nhiên (**SGD**) và bình phương tối thiểu luân phiên (**ALS**).
- **Cách mô hình hoạt động (Định nghĩa & Ví dụ):**
  - **Định nghĩa:** Tách ma trận đánh giá khổng lồ chứa nhiều ô trống thành hai ma trận nhỏ gọn hơn: một ma trận chứa "đặc điểm tiềm ẩn" của người dùng, một ma trận chứa "thuộc tính tiềm ẩn" của bài hát (ví dụ mức độ sôi động, tính trầm buồn, phong cách acoustic).
  - **Ví dụ hoạt động:**
    - Giả sử ta nén gu nhạc thành 2 yếu tố: [Mức độ sôi động, Mức độ buồn bã].
    - Bạn thích nhạc buồn, ít sôi động $\rightarrow$ Vector của bạn là: $[0.1, 0.9]$.
    - Ca sĩ A chuyên hát ballad nhẹ nhàng, da diết $\rightarrow$ Vector của ca sĩ A là: $[0.2, 0.8]$.
    - Ca sĩ B chuyên hát nhạc sàn, nhạc nhảy sôi động $\rightarrow$ Vector của ca sĩ B là: $[0.9, 0.1]$.
    - Hệ thống nhân vector của bạn với từng ca sĩ: với ca sĩ A được $(0.1 \times 0.2) + (0.9 \times 0.8) = 0.74$ (rất cao); với ca sĩ B được $(0.1 \times 0.9) + (0.9 \times 0.1) = 0.18$ (rất thấp). Hệ thống chọn ca sĩ A để gợi ý cho bạn.
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 1.1 (Bối cảnh và lý do chọn đề tài):** Căn cứ đưa mô hình phân rã ma trận SVD vào danh mục 3 mô hình nền tảng.
  - **Mục 2.5 (Phân rã ma trận và SVD):** Cơ sở lý thuyết cho công thức biểu diễn nhân tử tiềm ẩn kèm bias (Công thức 2.6) và hàm mất mát điều chuẩn (Công thức 2.7).
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Đưa vào **Bảng 2.2** (mô hình Matrix Factorization / SVD-bias).
  - **Mục 3.6 & 3.6.3 (Các mô hình đề xuất / Thuật toán SVD huấn luyện bằng SGD):** Xây dựng **Thuật toán 3.3**, đặc biệt là chi tiết cập nhật đồng thời tham số bằng `p_u_old` để bảo đảm đạo hàm chính xác.
  - **Mục 4.4 & 4.8 (Thiết kế thí nghiệm E3 & So sánh chi tiết theo nhóm mô hình):** Đánh giá baseline cá nhân hóa chính.

---

### 4. Hu, Koren, Volinsky (2008)
- **Tên bài báo:** *Collaborative Filtering for Implicit Feedback Datasets* (ICDM 2008)
- **Tập tin tài liệu:** [Hu, Koren, Volinsky 2008.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Hu,%20Koren,%20Volinsky%202008.pdf)
- **Đóng góp chính của bài báo:**
  - Thiết lập khung lý thuyết chuẩn tắc cho bài toán lọc cộng tác trên dữ liệu phản hồi ngầm (**implicit feedback**).
  - Chỉ ra 3 đặc trưng cốt lõi: không có phản hồi âm rõ ràng, dữ liệu nhiều nhiễu, và số lượt nghe phản ánh độ tin cậy (*confidence*) chứ không tỷ lệ tuyến tính với độ yêu thích.
  - Đề xuất tách hành vi thành biến nhị phân ưu tiên ($p_{ui}$) và trọng số độ tin cậy ($c_{ui} = 1 + \alpha r_{ui}$).
- **Cách mô hình hoạt động (Định nghĩa & Ví dụ):**
  - **Định nghĩa:** Thay vì coi lượt nghe là điểm đánh giá (nghe 100 lần không có nghĩa là thích gấp 100 lần người nghe 1 lần), mô hình coi việc có nghe hay không là một "phỏng đoán ưu tiên", còn số lượt nghe đóng vai trò là "mức độ chắc chắn" của phỏng đoán đó.
  - **Ví dụ hoạt động:**
    - Bạn nghe bài hát của ca sĩ X đúng 1 lần: Hệ thống ghi nhận bạn có quan tâm ($p = 1$), nhưng độ tin cậy còn thấp ($c = 1 + \alpha \times 1$) vì có thể bạn chỉ tình cờ bấm nhầm hoặc nghe thử rồi bỏ qua.
    - Bạn nghe bài hát của ca sĩ Y tới 50 lần: Hệ thống ghi nhận bạn chắc chắn thích ($p = 1$) với độ tin cậy cực kỳ cao ($c = 1 + \alpha \times 50$). Khi huấn luyện, mô hình sẽ ưu tiên thỏa mãn các bài hát có độ tin cậy cao trước.
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 1.1 & 1.2 (Bối cảnh & Vấn đề cần giải quyết):** Nhận diện dữ liệu `listening count` trong Last.fm HetRec 2011 là phản hồi ngầm một phía.
  - **Mục 2.2 (Dữ liệu tương tác và phản hồi ngầm):** Trích dẫn 3 khác biệt cốt lõi; cơ sở áp dụng phép biến đổi log-transform $y_{ui} = \ln(1 + w_{ui})$ (Công thức 2.1) để làm mượt số lượt nghe cực đoan.
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Đưa vào **Bảng 2.2** (xử lý listening count và mô hình hóa phản hồi ngầm).
  - **Mục 3.4 & 3.5 (Thiết kế bộ dữ liệu & Tiền xử lý dữ liệu):** Pipeline làm sạch và chuẩn hóa dữ liệu.

---

### 5. Herlocker et al. (2004)
- **Tên bài báo:** *Evaluating Collaborative Filtering Recommender Systems* (ACM TOIS 2004)
- **Tập tin tài liệu:** [Herlocker et al. 2004.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Herlocker%20et%20al.%202004.pdf)
- **Đóng góp chính của bài báo:**
  - Khảo sát kinh điển và toàn diện nhất đặt ra các nguyên tắc, chuẩn mực và phương pháp luận đánh giá hệ thống lọc cộng tác.
  - Phân loại rõ ràng các tác vụ người dùng và tương ứng với từng nhóm độ đo (đo sai số dự đoán điểm như MAE/RMSE so với độ đo xếp hạng như Precision, Recall, ROC).
  - Đề xuất kỹ thuật **Significance Weighting** nhằm giảm độ tin cậy của các cặp người dùng chỉ có 1-2 bài nghe chung.
- **Cách mô hình hoạt động (Định nghĩa & Ví dụ):**
  - **Định nghĩa (Significance Weighting):** Hai người cùng thích 1 ca sĩ có thể chỉ là sự trùng hợp ngẫu nhiên. Chỉ khi hai người cùng nghe từ 10 - 20 ca sĩ chung trở lên thì sự giống nhau đó mới thực sự đáng tin.
  - **Ví dụ hoạt động:**
    - Bạn và người lạ A cùng nghe 1 bài hát duy nhất của *Đen Vâu*. Nếu tính toán thông thường, hệ thống tưởng hai người giống nhau 100%. Kỹ thuật này sẽ phạt nặng độ tương đồng xuống còn $1/20 = 5\%$ vì quá ít dữ liệu chung.
    - Bạn và người bạn B cùng nghe 25 nghệ sĩ giống nhau. Hệ thống sẽ giữ nguyên 100% độ tin cậy vì đã vượt qua ngưỡng tối thiểu ($\gamma = 20$).
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 2.3 (Lọc cộng tác dựa trên người dùng - User-based CF):** Áp dụng kỹ thuật Significance Weighting với ngưỡng $\gamma$ (nhân hệ số $\frac{\min(|I_{av}|, \gamma)}{\gamma}$).
  - **Mục 2.7 (Các độ đo đánh giá mô hình):** Xây dựng khung đánh giá đa diện, nguyên tắc minh bạch thực nghiệm.
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Định vị phương pháp luận đánh giá trong **Bảng 2.2**.
  - **Mục 3.6.1 (Thuật toán User-based CF):** Tích hợp tham số $\gamma$ vào Thuật toán 3.1.
  - **Mục 3.9 & 4.5 (Tiêu chí đánh giá & Kiểm định thống kê):** Phân tách phân tích lỗi theo nhóm độ dài lịch sử người dùng.

---

### 6. Cremonesi, Koren, Turrin (2010)
- **Tên bài báo:** *Performance of Recommender Algorithms on Top-N Recommendation Tasks* (ACM RecSys 2010)
- **Tập tin tài liệu:** [Cremonesi et al. 2010.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Cremonesi%20et%20al.%202010.pdf)
- **Đóng góp chính của bài báo:**
  - Phát hiện bước ngoặt: **Tối ưu hóa RMSE không đồng nghĩa với cải thiện chất lượng xếp hạng Top-N**.
  - Chỉ ra hiện tượng các thuật toán không cá nhân hóa (*Popularity baseline*) có thể đánh bại hoặc đạt độ chính xác gần bằng các mô hình phức tạp nếu đánh giá Top-N bị chi phối bởi các mục phổ biến.
  - Đề xuất thuật toán **PureSVD** (phân rã đại số trực tiếp ma trận tương tác nhị phân lấp đầy số 0) với hiệu năng xếp hạng Top-N vượt trội.
- **Cách mô hình hoạt động (Định nghĩa & Ví dụ):**
  - **Định nghĩa (Mâu thuẫn giữa RMSE và Top-N):** Đo RMSE giống như yêu cầu học sinh đoán chính xác điểm số của tất cả các bài thi (dễ đoán đúng điểm những bài nổi tiếng). Nhưng người dùng chỉ cần danh sách 10 bài hay nhất để nghe (Top-10), họ không quan tâm bạn đoán sai số của những bài họ không bao giờ nghe.
  - **Ví dụ hoạt động:**
    - Mô hình A cố gắng đoán điểm thật chuẩn: đoán bài hát này 3.2 sao, bài kia 3.5 sao (RMSE rất đẹp). Nhưng khi chọn ra Top-5 để gợi ý, toàn gợi ý các bài trung bình, nhàm chán.
    - Mô hình PureSVD chỉ tập trung tìm xem bài nào có xác suất xuất hiện ở top đầu cao nhất, bỏ qua việc đoán điểm số chi tiết. Kết quả là danh sách Top-5 gợi ý ra trúng ngay gu người dùng, dù điểm RMSE của mô hình rất xấu.
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 1.1 & 1.2 (Bối cảnh & Vấn đề cần giải quyết):** Căn cứ chứng minh việc chỉ đo RMSE là thiếu sót, bắt buộc phải đánh giá xếp hạng Top-K (NDCG@K, Recall@K).
  - **Mục 2.5 (Phân rã ma trận và SVD):** Trình bày biến thể PureSVD dùng phép chiếu đại số ma trận.
  - **Mục 2.7 (Các độ đo đánh giá mô hình):** Phân tích sự bất tương xứng giữa độ đo dự đoán điểm số và độ đo xếp hạng Top-K.
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Đưa vào **Bảng 2.2** (lựa chọn độ đo Top-K và biến thể PureSVD).
  - **Mục 3.6 & 3.8 (Các mô hình đề xuất & Baseline):** Đưa PureSVD vào thử nghiệm; bắt buộc dùng Popularity baseline làm mốc đối chứng.
  - **Mục 4.7 (Kết quả thực nghiệm định lượng):** Làm nguyên tắc diễn giải kết quả thực nghiệm.

---

### 7. Kowald, Schedl, Lex (2020)
- **Tên bài báo:** *The Unfairness of Popularity Bias in Music Recommendation: A Reproducibility Study* (ECIR 2020)
- **Tập tin tài liệu:** [Kowald, Schedl, Lex 2020.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Kowald,%20Schedl,%20Lex%202020.pdf)
- **Đóng góp chính của bài báo:**
  - Tái lập và kiểm chứng hiện tượng thiên lệch phổ biến (**Popularity Bias**) và sự đối xử bất công thuật toán trong **miền âm nhạc** trên tập dữ liệu Last.fm quy mô lớn (LFM-1b).
  - Phân nhóm người dùng theo mức độ thị hiếu chính thống (*mainstreaminess*) thành 3 nhóm: *low-mainstream*, *medium-mainstream*, và *high-mainstream*.
  - Chứng minh thực nghiệm rằng các thuật toán lọc cộng tác hiện đại thiên vị nặng nề cho các nghệ sĩ phổ biến và phục vụ kém nhất (độ chính xác thấp nhất) đối với nhóm người dùng thích nghe nhạc ngách (*low-mainstream*).
- **Cách mô hình hoạt động (Định nghĩa & Ví dụ):**
  - **Định nghĩa:** Hệ thống AI thường có xu hướng "lười biếng", cứ thấy ca sĩ nào đang hot, nhiều người nghe thì đem gợi ý cho tất cả mọi người vì cách này an toàn, dễ ăn điểm. Điều này gây bất công cho những người có gu nghe nhạc độc lạ (indie, underground).
  - **Ví dụ hoạt động:**
    - Bạn là người chuyên nghe nhạc Rock cổ điển thập niên 80 (nhóm *low-mainstream*).
    - Hệ thống lọc cộng tác thông thường thấy bạn nghe nhạc, liền gợi ý các bài hit thịnh hành hiện nay của *Taylor Swift* hay *BTS* (vì hàng triệu người khác đều nghe).
    - Hậu quả: Bạn cảm thấy hệ thống vô dụng vì không hiểu gu của mình; các nghệ sĩ Rock độc lập cũng không bao giờ có cơ hội tiếp cận bạn.
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 1.1 & 1.2 (Bối cảnh & Vấn đề cần giải quyết):** Căn cứ thực tiễn chứng minh thiên lệch phổ biến trên Last.fm.
  - **Mục 1.9.1 (Ý nghĩa khoa học):** Định vị đóng góp kiểm chứng giải pháp giảm thiên lệch trong miền âm nhạc.
  - **Mục 2.6 (Sparsity, cold-start và popularity bias):** Cơ sở lý thuyết về sự bất công của thiên lệch phổ biến.
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Đưa vào **Bảng 2.2** (động lực trực tiếp cho đề tài).
  - **Mục 3.7.1 (Mô-đun cải tiến M1):** Thiết kế thuật toán tái xếp hạng tham lam (MMR có phạt độ phổ biến) để bảo vệ nghệ sĩ đuôi dài.
  - **Mục 4.4 & 4.9 (Thí nghiệm E4, E5 & Đánh giá độ đa dạng, thiên lệch):** Đo lường ARP, Gini, Coverage.

---

### 8. Ji et al. (2023)
- **Tên bài báo:** *A Critical Study on Data Leakage in Recommender System Offline Evaluation* (ACM TOIS 2023)
- **Tập tin tài liệu:** [Ji et al. 2023.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Ji%20et%20al.%202023.pdf)
- **Đóng góp chính của bài báo:**
  - Nghiên cứu phản biện về vấn đề **rò rỉ dữ liệu (data leakage)** trong đánh giá ngoại tuyến (offline evaluation).
  - Chỉ ra rằng các chiến lược chia tập không tuân thủ dòng thời gian toàn cục (*global timeline*) – chẳng hạn chia ngẫu nhiên – khiến mô hình vô tình học trước tương lai, làm sai lệch thứ hạng tương đối giữa các mô hình.
  - Đề xuất khung đánh giá tuân thủ mốc thời gian (*timeline evaluation scheme*).
- **Cách mô hình hoạt động (Định nghĩa & Ví dụ):**
  - **Định nghĩa:** Rò rỉ dữ liệu giống như cho học sinh "biết trước đề thi tương lai" trong lúc đang ôn tập. Nếu bạn lấy dữ liệu nghe nhạc của tuần sau cho mô hình học, rồi bắt mô hình đoán xem người đó nghe gì trong tuần này, mô hình sẽ đạt điểm cao giả tạo nhưng khi đưa vào thực tế thì hoạt động dở tệ.
  - **Ví dụ hoạt động:**
    - Thực tế: Ngày 01/10 ca sĩ A ra album mới. Ngày 05/10 người dùng mới biết và bấm nghe.
    - Nếu chia tập ngẫu nhiên không neo thời gian: Hành vi nghe ngày 05/10 vô tình lọt vào tập huấn luyện (train set). Sau đó ta bắt mô hình dự đoán hành vi ngày 02/10 (test set). Mô hình dễ dàng đoán trúng vì nó "đã nhìn thấy tương lai", tạo ra kết quả đánh giá không trung thực.
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 1.2 (Vấn đề cần giải quyết):** Cảnh báo nguy cơ rò rỉ dữ liệu khi chia tập.
  - **Mục 1.9.1 (Ý nghĩa khoa học):** Thiết lập quy trình so sánh có kiểm soát, minh bạch.
  - **Mục 2.8 (Rủi ro rò rỉ dữ liệu và thực hành đánh giá tin cậy):** Trích dẫn trực tiếp luận điểm của Ji et al. để thừa nhận giới hạn của bộ dữ liệu Last.fm HetRec 2011 (do không có timestamp chi tiết), giải trình minh bạch việc sử dụng giao thức Given-N / random per-user split.
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Đưa vào **Bảng 2.2** (cơ sở thiết kế phân chia tập dữ liệu).
  - **Mục 3.5 (Tiền xử lý và chiến lược chia tập dữ liệu):** Cố định seed, chỉ tinh chỉnh siêu tham số trên validation và chạy trên test đúng 1 lần duy nhất.
  - **Mục 5.7 (Giới hạn của đề tài):** Ghi nhận giới hạn về timeline split do đặc thù bộ dữ liệu tĩnh.

---

## PHẦN 2: NHÓM TÀI LIỆU KHẢO SÁT VÀ TỔNG QUAN (9 TÀI LIỆU)
*(Đã loại bỏ bài số 4: Kleć & Wieczorkowska, 2021 theo đúng yêu cầu)*

---

### 1. Song, Dixon, Pearce (2012)
**Tên bài báo:** *A Survey of Music Recommendation Systems and Future Perspectives* (CMMR 2012)  
**Tập tin tài liệu:** [A_Survey_of_Music_Recommendation_Systems_and_Future_Perspectives.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/A_Survey_of_Music_Recommendation_Systems_and_Future_Perspectives.pdf)

#### a. Phương pháp
- **Định nghĩa trực quan:** Bài báo tổng hợp bức tranh toàn cảnh về cách các cỗ máy nghe nhạc thấu hiểu con người qua 4 góc độ: bạn bè nghe gì (Lọc cộng tác), bài hát nghe như thế nào (Phân tích âm thanh - giai điệu, tiết tấu), người nghe đang ở đâu/làm gì (Ngữ cảnh), và người nghe đang vui hay buồn (Cảm xúc). Tác giả đề xuất mô hình mới dựa trên "Động cơ" (*Motivation-based*): hiểu lý do tại sao người ta bật nhạc (để tập gym, để ngủ, hay để giải tỏa căng thẳng).
- **Ví dụ cách hoạt động:**
  - *Bước 1 (Nhận diện ngữ cảnh & cảm xúc):* Điện thoại nhận biết lúc 6 giờ sáng, bạn đang chạy bộ ở công viên (tốc độ di chuyển nhanh, nhịp tim cao).
  - *Bước 2 (Trích xuất đặc trưng âm thanh):* Hệ thống lọc ra các bài hát có tiết tấu nhanh, dồn dập (trên 130 BPM, năng lượng cao) thay vì các bản ballad chậm rãi.
  - *Bước 3 (Khớp nối sở thích cá nhân):* Trong số các bài nhạc sôi động đó, hệ thống chọn đúng các ca sĩ bạn từng nghe nhiều trên Last.fm để phát vào tai nghe của bạn.

#### b. Bộ dữ liệu thực nghiệm (Schema & Chú thích)
Khảo sát các bộ dữ liệu từ nền tảng **Last.fm** và chiến dịch đánh giá quốc tế **MIREX / Million Song Dataset**:

```
Bảng 1: Lịch sử nghe nhạc (Listening History - Last.fm)
+---------------+---------------+---------------+---------------------+
| user_id       | artist_id     | track_id      | timestamp           |
| (Chuỗi ký tự) | (Chuỗi ký tự) | (Chuỗi ký tự) | (Ngày-giờ ISO)      |
+---------------+---------------+---------------+---------------------+
| u_001         | art_101       | trk_501       | 2012-05-10 08:30:00 |
+---------------+---------------+---------------+---------------------+

Bảng 2: Đặc trưng âm thanh bài hát (Audio Features - MIREX / MSD)
+---------------+-------------+-------------+-------------+---------------------+
| track_id      | tempo (BPM) | loudness    | key         | mfcc_vector         |
| (Chuỗi ký tự) | (Số thực)   | (Decibel dB)| (Số nguyên) | (Mảng 13-20 số thực)|
+---------------+-------------+-------------+-------------+---------------------+
| trk_501       | 128.5       | -5.4        | 7           | [-12.1, 4.5, ...]   |
+---------------+-------------+-------------+-------------+---------------------+
```

- **Chú thích các trường dữ liệu:**
  - `user_id`: Mã định danh duy nhất của người nghe nhạc trên nền tảng.
  - `artist_id` / `track_id`: Mã định danh duy nhất của nghệ sĩ hoặc bài hát cụ thể.
  - `timestamp`: Thời điểm chính xác người dùng nhấn phát bài hát (dùng để xác định ngữ cảnh sáng/tối hoặc ngày làm việc/cuối tuần).
  - `tempo`: Tốc độ nhịp điệu của bài hát (đo bằng số nhịp mỗi phút - BPM; ví dụ trên 120 là nhạc nhanh, sôi động).
  - `loudness`: Độ to trung bình của âm thanh đo bằng Decibel (dB).
  - `mfcc_vector`: Hệ số phổ tần số Mel (MFCC), mô tả "màu sắc" âm thanh và âm sắc của nhạc cụ, giọng hát mà không phụ thuộc vào ca từ.

#### c. Kết quả đạt được
- Lọc cộng tác (CF) và Phân tích nội dung âm thanh (CBM) là hai giải pháp cốt lõi mang lại hiệu quả cao nhất trong thực tế.
- Chỉ ra các độ đo xếp hạng phổ biến gồm: Precision (tỷ lệ bài đúng trong danh sách), Recall (tỷ lệ bài tìm được trên tổng số bài thích), và MAP (độ chính xác trung bình có tính thứ tự ưu tiên).

#### d. Ưu và nhược điểm
- *Ưu điểm:* Cung cấp tư duy liên ngành sâu sắc, kết hợp giữa thuật toán máy tính với tâm lý học âm nhạc và hành vi con người.
- *Nhược điểm:* Chưa có bảng thực nghiệm so sánh định lượng trực tiếp; việc thu thập cảm xúc và động cơ tức thời của người nghe đòi hỏi thiết bị cảm biến phức tạp, khó triển khai đại trà.

---

### 2. Schedl, Zamani, Chen, Deldjoo, Elahi (2018)
**Tên bài báo:** *Current Challenges and Visions in Music Recommender Systems Research* (IJMIR 2018)  
**Tập tin tài liệu:** [Current_Challenges_and_Visions_in_Music_Recommender_Systems_Research.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Current_Challenges_and_Visions_in_Music_Recommender_Systems_Research.pdf)

#### a. Phương pháp
- **Định nghĩa trực quan:** Khảo sát định hình lộ trình phát triển của ngành, chỉ ra âm nhạc rất khác phim ảnh hay mua sắm trực tuyến: một bài hát chỉ kéo dài vài phút, người ta có thói quen nghe đi nghe lại một bài hàng chục lần (*repeat consumption*), và thường nghe liền một danh sách phát (*playlist*). Bài báo tập trung vào bài toán: làm sao để tự động tiếp nối danh sách phát (bạn bật 3 bài đầu, máy tự chọn mượt mà 10 bài tiếp theo).
- **Ví dụ cách hoạt động:**
  - *Bước 1 (Đọc hạt giống ban đầu):* Người dùng tạo một playlist đặt tên là "Học bài khuya" và mới chỉ thêm 3 bài nhạc Lofi không lời.
  - *Bước 2 (Mô hình chuỗi tiếp nối - APC):* Hệ thống không chỉ tìm bài giống về thể loại, mà phải đảm bảo bài thứ 4 có âm lượng, độ êm dịu và nhịp điệu chuyển tiếp mượt mà từ bài thứ 3, không gây giật mình làm đứt đoạn sự tập trung của người học.

#### b. Bộ dữ liệu thực nghiệm (Schema & Chú thích)
Khảo sát bộ dữ liệu nổi tiếng **Spotify RecSys Challenge 2018** (1 triệu playlist) và **LFM-1b**:

```
Bảng: Cấu trúc Playlist (Spotify Million Playlist Dataset)
+---------------+----------------+----------------+-------------------------------------+
| pid (ID)      | name           | num_tracks     | tracks (Danh sách bài hát)          |
| (Số nguyên)   | (Chuỗi ký tự)  | (Số nguyên)    | (Mảng đối tượng JSON)               |
+---------------+----------------+----------------+-------------------------------------+
| 1024          | "Night Study"  | 35             | [{"pos": 0, "uri": "spotify:trk_1"},|
|               |                |                |  {"pos": 1, "uri": "spotify:trk_2"}]|
+---------------+----------------+----------------+-------------------------------------+
```

- **Chú thích các trường dữ liệu:**
  - `pid`: Mã định danh số nguyên của danh sách phát (playlist ID).
  - `name`: Tiêu đề do người dùng tự đặt cho playlist (ví dụ: "Chill", "Running", "Workout"), phản ánh ngữ cảnh và tâm trạng người nghe.
  - `num_tracks`: Tổng số lượng bài hát có trong danh sách phát đó.
  - `tracks`: Danh sách có thứ tự các bài hát:
    - `pos`: Thứ tự phát của bài hát trong playlist (vị trí 0 là bài đầu tiên, vị trí 1 là bài kế tiếp...).
    - `uri`: Đường dẫn định danh duy nhất của bản ghi âm trên máy chủ Spotify.

#### c. Kết quả đạt được
- Định nghĩa bài toán Tự động tiếp nối danh sách phát (APC) trở thành thước đo năng lực của các thuật toán học máy hiện đại.
- Chứng minh rằng việc đánh giá offline bằng các độ đo truyền thống (như đoán điểm số RMSE) hoàn toàn không đo được sự hài lòng của người nghe nhạc trong một phiên nghe liên tục.

#### d. Ưu và nhược điểm
- *Ưu điểm:* Là "kim chỉ nam" học thuật cho toàn bộ cộng đồng nghiên cứu hệ khuyến nghị âm nhạc quốc tế, đặt nền móng cho các bài toán chuỗi thời gian.
- *Nhược điểm:* Đóng vai trò là bài báo tầm nhìn (roadmap/survey), không đưa ra giải thuật toán học độc lập để kiểm chứng số liệu.

---

### 3. Schedl, Knees, McFee, Bogdanov, Kaminskas (2015)
**Tên bài báo:** *Music Recommender Systems* (Chương 13, Recommender Systems Handbook, 2nd Edition, Springer, 2015)  
**Tập tin tài liệu:** [RecSysHandbook2015_ch13_musicrec.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/RecSysHandbook2015_ch13_musicrec.pdf)

#### a. Phương pháp
- **Định nghĩa trực quan:** Cuốn cẩm nang toàn thư về kỹ thuật tạo danh sách nhạc tự động và trích xuất đặc trưng âm thanh. Hệ thống giải quyết bài toán: Khi một bài hát mới phát hành chưa ai nghe (chưa có dữ liệu cộng tác), máy tính sẽ tự "lắng nghe" file âm thanh MP3 để phân tích sóng nhạc (tiếng trống, giọng hát, giai điệu), từ đó biết bài này giống bài nào để gợi ý.
- **Ví dụ cách hoạt động:**
  - *Bước 1 (Xử lý tín hiệu âm thanh):* Một ca sĩ vô danh tải lên một bài hát mới toanh. Máy tính quét qua file âm thanh, chia nhỏ thành các khung thời gian 20 mili-giây, trích xuất phổ tần số âm thanh (MFCC).
  - *Bước 2 (Đo khoảng cách âm học):* Máy tính so sánh vector âm sắc này với kho nhạc sẵn có, phát hiện bài hát mới có cách phối khí acoustic và giọng hát trầm ấm tương tự các bài của ca sĩ *Vũ*.
  - *Bước 3 (Gợi ý phá vỡ cold-start):* Dù bài hát chưa có lượt nghe nào, hệ thống vẫn tự tin gợi ý bài này cho những người thích nghe nhạc của *Vũ*.

#### b. Bộ dữ liệu thực nghiệm (Schema & Chú thích)
Bảng tổng hợp đối sánh các bộ dữ liệu âm nhạc chuẩn thế giới (Yahoo! Music, Million Song Dataset, Last.fm):

```
Bảng 1: Đánh giá tường minh (Yahoo! Music Ratings)
+---------------+---------------+---------------+
| user_id       | song_id       | rating (Điểm) |
| (Số nguyên)   | (Số nguyên)   | (Thang 0-100) |
+---------------+---------------+---------------+
| 85401         | 1029481       | 90            |
+---------------+---------------+---------------+

Bảng 2: Lịch sử phản hồi ngầm (MSD Taste Profile / Last.fm 360K)
+---------------+---------------+-----------------------+
| user_id       | artist_id     | play_count (Lượt nghe)|
| (Chuỗi băm)   | (Chuỗi băm)   | (Số nguyên dương)     |
+---------------+---------------+-----------------------+
| b80344d0635...| AR002UA118... | 47                    |
+---------------+---------------+-----------------------+
```

- **Chú thích các trường dữ liệu:**
  - `user_id`: Định danh người nghe (chuỗi ký tự băm hoặc số nguyên).
  - `song_id` / `artist_id`: Định danh bài hát hoặc nghệ sĩ trong cơ sở dữ liệu bài hát chuẩn của Million Song Dataset.
  - `rating`: Điểm đánh giá tường minh từ 0 đến 100 do người dùng trực tiếp chấm (0: cực ghét, 100: tuyệt phẩm).
  - `play_count`: Số lần người dùng đã nghe bài hát/nghệ sĩ đó (dữ liệu phản hồi ngầm dạng đếm).

#### c. Kết quả đạt được
- So sánh toàn diện giữa dữ liệu đánh giá tường minh (ratings) và phản hồi ngầm (play count).
- Chỉ ra hiện tượng "trần kính" (*glass ceiling*): nếu chỉ dựa vào phân tích sóng âm thanh thuần túy, độ chính xác chỉ đạt một ngưỡng nhất định vì máy tính không thể hiểu được yếu tố văn hóa, danh tiếng của ca sĩ và trào lưu xã hội.

#### d. Ưu và nhược điểm
- *Ưu điểm:* Là tài liệu sách giáo khoa kinh điển, chứa đựng đầy đủ các công thức toán học mẫu mực cho xử lý tín hiệu âm thanh và lọc cộng tác.
- *Nhược điểm:* Xuất bản năm 2015 nên chưa bao hàm các bước tiến của mạng nơ-ron đồ thị (GNN) và mô hình ngôn ngữ lớn (LLM).

---

### 4. Deldjoo, Schedl, Knees (2021)
**Tên bài báo:** *Content-driven Music Recommendation: Evolution, State of the Art, and Challenges* (arXiv 2021)  
**Tập tin tài liệu:** [Content-driven_Music_Recommendation_Evolution_State_of_the_Art_and_Challenges.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Content-driven_Music_Recommendation_Evolution_State_of_the_Art_and_Challenges.pdf)

#### a. Phương pháp
- **Định nghĩa trực quan:** Khảo sát các mô hình khuyến nghị âm nhạc dựa trên nội dung hiện đại, mô hình hóa âm nhạc như một "củ hành" nhiều lớp (**Onion Model**): lớp lõi là sóng âm thanh, lớp thứ hai là bản nhạc MIDI, lớp thứ ba là lời bài hát và thể loại, lớp thứ tư là hình ảnh bìa album, và lớp ngoài cùng là ngữ cảnh người nghe. Khảo sát dành một chương riêng phân tích **Mạng nơ-ron đồ thị (GNN)**: biến toàn bộ bài hát, nghệ sĩ, danh sách phát, và thể loại thành các "nút" trên một mạng nhện khổng lồ để AI học mối quan hệ đan xen.
- **Ví dụ cách hoạt động (Mạng đồ thị GNN):**
  - *Bước 1 (Xây dựng mạng lưới kết nối):* Nút "Ca sĩ A" nối với nút "Bài hát X", bài hát X lại được xếp chung vào playlist với "Bài hát Y", bài hát Y lại có chung thẻ tag "Acoustic" với "Bài hát Z".
  - *Bước 2 (Lan truyền thông tin trên đồ thị):* Mạng nơ-ron đồ thị cho các nút "trò chuyện" với nhau dọc theo các sợi dây kết nối. Sau vài lượt truyền tin, nút "Bài hát X" sẽ thu thập được toàn bộ đặc tính âm thanh và thể loại của các bài hát lân cận.
  - *Bước 3 (Gợi ý đa chiều):* Hệ thống nhận ra bài hát X và bài hát Z có sự liên kết chặt chẽ dù chúng chưa từng được cùng một người nghe qua.

#### b. Bộ dữ liệu thực nghiệm (Schema & Chú thích)
Khảo sát các bộ dữ liệu đa phương thức quy mô lớn gồm **Spotify Million Playlist Dataset**, **Free Music Archive (FMA)** và **LFM-1b**:

```
Bảng: Thuộc tính âm thanh cấp cao trích xuất bằng Deep Learning (Spotify Audio Features API)
+---------------+-------------+----------+---------+--------------+--------------+
| track_id      | acousticness| energy   | valence | danceability | speechiness  |
| (Chuỗi ký tự) | (0.0 - 1.0) |(0.0 - 1.0)|(0.0-1.0)| (0.0 - 1.0)  | (0.0 - 1.0)  |
+---------------+-------------+----------+---------+--------------+--------------+
| 4uLU6hMC...   | 0.82        | 0.25     | 0.18    | 0.35         | 0.04         |
+---------------+-------------+----------+---------+--------------+--------------+
```

- **Chú thích các trường dữ liệu:**
  - `track_id`: Mã nhận dạng duy nhất của bài hát.
  - `acousticness`: Xác suất bài hát sử dụng nhạc cụ mộc tự nhiên (0.0: nhạc điện tử hoàn toàn, 1.0: nhạc mộc acoustic thuần túy).
  - `energy`: Mức độ dồn dập, mạnh mẽ và sôi động của bài hát (nhạc Rock/EDM có energy rất cao gần 1.0).
  - `valence`: Độ tươi vui, lạc quan của bài hát (valence càng cao thể hiện bài hát vui tươi, yêu đời; valence thấp phản ánh bài hát u sầu, buồn rầu).
  - `danceability`: Mức độ phù hợp để nhảy múa dựa trên nhịp phách, sự đều đặn của tiếng trống.
  - `speechiness`: Tỷ lệ giọng nói xuất hiện trong bài hát (rap hoặc podcast có chỉ số này cao).

#### c. Kết quả đạt được
- Mô hình học sâu đa phương thức (kết hợp cả âm thanh, lời bài hát và cấu trúc đồ thị tương tác) luôn vượt trội rõ rệt so với các mô hình chỉ nhìn vào một nguồn tín hiệu đơn lẻ.
- Mạng nơ-ron đồ thị (GNN) được chứng minh là công cụ hiệu quả nhất để dung hợp các tầng dữ liệu của mô hình củ hành.

#### d. Ưu và nhược điểm
- *Ưu điểm:* Phân loại kiến trúc cực kỳ hiện đại, cập nhật chi tiết về các tiến bộ của trí tuệ nhân tạo đồ thị và âm thanh sâu.
- *Nhược điểm:* Việc trích xuất và huấn luyện các mô hình đồ thị kết hợp học sâu âm thanh đòi hỏi cấu hình máy trạm GPU mạnh mẽ và dung lượng bộ nhớ lớn.

---

### 5. Lacic et al. (2024)
**Tên bài báo:** *Hybrid music recommendation with graph neural networks* (User Modeling and User-Adapted Interaction - UMAI 2024)  
**Tập tin tài liệu:** [Hybrid_music_recommendation_with_graph_neural_networks.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Hybrid_music_recommendation_with_graph_neural_networks.pdf)

#### a. Phương pháp
- **Định nghĩa trực quan:** Áp dụng mô hình mạng nơ-ron đồ thị quy mô lớn **PinSage** (thuật toán từng làm nên tên tuổi của mạng xã hội hình ảnh Pinterest) vào việc gợi ý bài hát liên quan trên Spotify. Thuật toán kết hợp cả đồ thị bài hát cùng xuất hiện trong các playlist với các đặc trưng âm thanh được nén bằng mạng nơ-ron sâu (**MusicNN, VGGish, L3-Net**).
- **Ví dụ cách hoạt động:**
  - *Bước 1 (Bước ngẫu nhiên trên đồ thị):* Xuất phát từ một bài hát A, thuật toán thực hiện hàng nghìn "bước đi ngẫu nhiên" (Random Walk - PageRank) qua các playlist để xem bài nào thường được xếp cạnh bài A nhất. Thu được tập các bài hát láng giềng quan trọng.
  - *Bước 2 (Tổng hợp âm thanh từ láng giềng):* Với mỗi láng giềng, thuật toán lấy vector âm thanh trích xuất từ mạng nơ-ron (tiết tấu, âm sắc) và gộp chúng lại bằng phép tích chập đồ thị (Graph Convolution).
  - *Bước 3 (Tạo vector đại diện toàn diện):* Mỗi bài hát lúc này vừa mang thông tin về vị trí của nó trong các playlist, vừa mang bản chất âm thanh thực sự của bài hát. Việc gợi ý bài tiếp theo chỉ đơn giản là tìm bài có vector gần nhất trong không gian toán học.

#### b. Bộ dữ liệu thực nghiệm (Schema & Chú thích)
Bộ dữ liệu thực nghiệm thu thập độc quyền từ **Spotify** gồm **10.000 playlists** và **277.000 bài hát duy nhất**:

```
Bảng 1: Tương tác Danh sách phát - Bài hát (Playlist-Song Interactions)
+---------------+---------------+--------------------+
| playlist_id   | song_id       | track_position     |
| (Chuỗi ký tự) | (Chuỗi ký tự) | (Số nguyên thứ tự) |
+---------------+---------------+--------------------+
| pl_88291      | trk_0912      | 0                  |
| pl_88291      | trk_4431      | 1                  |
+---------------+---------------+--------------------+

Bảng 2: Vector nhúng âm thanh học sâu (Deep Audio Embeddings)
+---------------+---------------------+---------------------------------+
| song_id       | model_name          | embedding_vector                |
| (Chuỗi ký tự) | (Tên mô hình)       | (Mảng số thực nhiều chiều)      |
+---------------+---------------------+---------------------------------+
| trk_0912      | "L3-Net" / "MusicNN"| [0.128, -0.441, 0.092, ... 128D]|
+---------------+---------------------+---------------------------------+
```

- **Chú thích các trường dữ liệu:**
  - `playlist_id`: Mã định danh danh sách phát công khai trên Spotify do người dùng tạo.
  - `song_id`: Mã định danh bản ghi bài hát trên Spotify.
  - `track_position`: Thứ tự xuất hiện của bài hát trong danh sách phát (dùng để xác định các cặp bài hát đứng liền kề nhau).
  - `model_name`: Tên kiến trúc mạng nơ-ron học sâu được dùng để trích xuất đặc trưng âm thanh từ đoạn trích 30 giây (như L3-Net tự giám sát, hoặc MusicNN chuyên về âm nhạc).
  - `embedding_vector`: Vector số học 128 chiều hoặc 512 chiều biểu diễn cô đọng toàn bộ phong cách âm nhạc của bài hát đó.

#### c. Kết quả đạt được
- Mô hình PinSage kết hợp đồ thị với vector âm thanh (L3-Net / MusicNN) vượt trội rõ rệt so với các mô hình baseline đơn lẻ trên các chỉ số xếp hạng: **Hit Ratio@10**, **NDCG@10**, và **MRR**.
- Khi gặp bài hát mới toanh chưa có trong bất kỳ playlist nào, việc có sẵn vector âm thanh nạp vào nút đồ thị giúp mô hình vẫn gợi ý chuẩn xác (giải quyết triệt để cold-start).

#### d. Ưu và nhược điểm
- *Ưu điểm:* Có khả năng mở rộng (scalability) trên đồ thị hàng trăm nghìn bài hát nhờ cơ chế lấy mẫu ngẫu nhiên láng giềng cục bộ thay vì tính toàn bộ đồ thị; mang tính quy nạp (*inductive*) giải quyết tốt bài toán bài hát mới.
- *Nhược điểm:* Đòi hỏi phải có cả đồ thị playlist lẫn file âm thanh thô để trích xuất embedding; quy trình huấn luyện đồ thị nơ-ron nhiều bước tương đối phức tạp.

---

### 6. Ziaoddini et al. (2025)
**Tên bài báo:** *Socially Aware Music Recommendation: A Multi-Modal Graph Neural Networks for Collaborative Music Consumption and Community-Based Engagement* (arXiv 2025)  
**Tập tin tài liệu:** [Socially_Aware_Music_Recommendation_A_Multi-Modal_Graph_Neural_Networks_for_Collaborative_Music_Consumption_and_Community-Based_Engagement.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Socially_Aware_Music_Recommendation_A_Multi-Modal_Graph_Neural_Networks_for_Collaborative_Music_Consumption_and_Community-Based_Engagement.pdf)

#### a. Phương pháp
- **Định nghĩa trực quan:** Đề xuất mô hình **MM-GNN** khai thác sức mạnh của mạng xã hội trong việc nghe nhạc. Chúng ta thường có xu hướng nghe nhạc theo bạn bè hoặc cộng đồng có cùng sở thích. Mô hình dựng nên một mạng đồ thị liên kết: người dùng kết bạn với nhau, người dùng nghe bài hát, và bài hát thì gắn liền với âm thanh, lời bài hát (lyrics) và ảnh bìa album (cover art).
- **Ví dụ cách hoạt động:**
  - *Bước 1 (Kết hợp sở thích bạn bè):* Bạn kết bạn với người dùng B và C trên mạng xã hội âm nhạc. Cả B và C đều đang phát cuồng vì một dòng nhạc mới.
  - *Bước 2 (Dung hợp dữ liệu đa giác quan):* Một bài hát mới xuất hiện có ảnh bìa mang phong cách hoài cổ (thị giác), lời bài hát chứa nhiều tâm sự (văn bản), và giai điệu lo-fi nhẹ nhàng (âm thanh).
  - *Bước 3 (Gợi ý cộng đồng):* Nhận thấy bạn bè trong nhóm của bạn đang nghe nhiều bài có đặc tính đa giác quan tương tự, hệ thống MM-GNN sẽ đẩy bài hát này đến danh sách chờ phát của bạn.

#### b. Bộ dữ liệu thực nghiệm (Schema & Chú thích)
Sử dụng bộ dữ liệu **MSD-A** (25.000 người dùng, 328.821 bài hát, 1,2 triệu tương tác) và **Last.fm Social**:

```
Bảng 1: Đồ thị quan hệ bạn bè xã hội (Social Graph - Last.fm)
+---------------+---------------+---------------------+
| user_id_1     | user_id_2     | friendship_status   |
| (Chuỗi ký tự) | (Chuỗi ký tự) | (1: Bạn bè)         |
+---------------+---------------+---------------------+
| u_1001        | u_2045        | 1                   |
+---------------+---------------+---------------------+

Bảng 2: Dữ liệu đa phương thức của bài hát (Multimodal Song Attributes)
+---------------+-------------------+---------------------+--------------------+
| song_id       | audio_feat (Âm)   | lyrics_feat (Lời)   | cover_feat (Ảnh bìa|
| (Chuỗi ký tự) | (Vector số thực)  | (Vector từ vựng)    | (Vector thị giác)  |
+---------------+-------------------+---------------------+--------------------+
| s_99182       | [0.45, -0.12, ...] | [0.88, 0.05, ...]   | [-0.31, 0.72, ...] |
+---------------+-------------------+---------------------+--------------------+
```

- **Chú thích các trường dữ liệu:**
  - `user_id_1`, `user_id_2`: Cặp mã định danh hai người dùng có kết nối bạn bè trên mạng xã hội.
  - `friendship_status`: Trạng thái quan hệ bạn bè/theo dõi lẫn nhau (mối liên kết xã hội để truyền dẫn ảnh hưởng gu âm nhạc).
  - `audio_feat`: Vector đặc trưng âm học trích xuất từ file nhạc.
  - `lyrics_feat`: Vector ngữ nghĩa của lời bài hát (phân tích cảm xúc bài thơ/ca từ qua mô hình xử lý ngôn ngữ tự nhiên NLP).
  - `cover_feat`: Vector thị giác trích xuất từ ảnh bìa album thông qua mạng nơ-ron thị giác máy tính (ResNet).

#### c. Kết quả đạt được
- Mô hình MM-GNN đạt kết quả dẫn đầu trên cả hai bộ dữ liệu thực nghiệm:
  - Trên **MSD-A**: Đạt **Recall@50 = 0.075**, **NDCG@50 = 0.043** (vượt xa các mô hình danh tiếng như NGCF: 0.061/0.035, VBPR: 0.052/0.030, và BPR: 0.045/0.026).
  - Trên **Last.fm**: Đạt **Recall@50 = 0.065**, **NDCG@50 = 0.037** (vượt NGCF: 0.051/0.029).

#### d. Ưu và nhược điểm
- *Ưu điểm:* Là mô hình toàn diện nhất tích hợp trọn vẹn cả mạng xã hội, âm thanh, ca từ và hình ảnh; cải thiện vượt bậc khả năng đề xuất cho người dùng mới nhờ dựa vào bạn bè.
- *Nhược điểm:* Kiến trúc quá nhiều thành phần khiến việc bảo trì và thời gian huấn luyện rất lâu; phần lớn các ứng dụng nghe nhạc ngày nay không thu thập được đồ thị bạn bè xã hội đầy đủ do chính sách riêng tư.

---

### 7. Ferraro et al. (2022)
**Tên bài báo:** *Fairness in Music Recommender Systems: A Stakeholder-Centered Mini Review* (Frontiers in Big Data 2022)  
**Tập tin tài liệu:** [Fairness_in_Music_Recommender_Systems_A_Stakeholder-Centered_Mini_Review.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Fairness_in_Music_Recommender_Systems_A_Stakeholder-Centered_Mini_Review.pdf)

#### a. Phương pháp
- **Định nghĩa trực quan:** Tổng quan mini-review xem xét tính công bằng của các thuật toán âm nhạc dưới góc nhìn đa bên liên quan: Không chỉ người nghe cần được đối xử công bằng (người thích nhạc ngách cũng phải được gợi ý chuẩn như người thích nhạc thị trường), mà cả người nghệ sĩ cũng cần được đối xử công bằng (các nghệ sĩ nữ, nghệ sĩ trẻ độc lập không bị chèn ép lượt hiển thị so với các ngôi sao lớn).
- **Ví dụ cách hoạt động (Can thiệp tái xếp hạng công bằng):**
  - *Bước 1 (Đầu ra thuật toán gốc):* Thuật toán lọc cộng tác chạy xong và trả về danh sách 10 ca sĩ được điểm cao nhất: trong đó có 9 ca sĩ nam nổi tiếng và chỉ có 1 ca sĩ nữ ít tên tuổi.
  - *Bước 2 (Kiểm tra hạn ngạch công bằng):* Bộ lọc công bằng phát hiện danh sách bị lệch nghiêm trọng về giới tính và độ phổ biến.
  - *Bước 3 (Tái xếp hạng có kiểm soát):* Hệ thống chủ động đẩy thêm 2 ca sĩ nữ có điểm số tiềm năng kế tiếp vào danh sách Top-10 để đảm bảo nghệ sĩ nữ có cơ hội tiếp cận khán giả bình đẳng hơn.

#### b. Bộ dữ liệu thực nghiệm (Schema & Chú thích)
Khảo sát các nguồn dữ liệu có gắn thông tin nhân khẩu học của nghệ sĩ và người nghe (**LFM-1b**, **MusicBrainz**):

```
Bảng: Thuộc tính Nghệ sĩ và Nhóm đối tượng (LFM-1b Artist Metadata)
+---------------+--------------------+------------------+---------------------+
| artist_id     | artist_name        | gender (Giới)    | popularity_tier     |
| (Chuỗi ký tự) | (Tên nghệ sĩ)      | (male/female)    | (top_head/long_tail)|
+---------------+--------------------+------------------+---------------------+
| a_00391       | "Billie Eilish"    | female           | top_head (Sao lớn)  |
| a_99182       | "Indie Artist X"   | female           | long_tail (Nghệ sĩ) |
+---------------+--------------------+------------------+---------------------+
```

- **Chú thích các trường dữ liệu:**
  - `artist_id` / `artist_name`: Định danh và tên gọi của ca sĩ/ban nhạc.
  - `gender`: Giới tính của nghệ sĩ biểu diễn (nam, nữ, nhóm hỗn hợp), được đối chiếu từ bách khoa toàn thư âm nhạc MusicBrainz.
  - `popularity_tier`: Phân tầng mức độ nổi tiếng dựa trên tổng lượt nghe toàn cầu (nhóm đỉnh *top-head* chiếm phần lớn lượt nghe, nhóm đuôi dài *long-tail* là các nghệ sĩ ít người biết).

#### c. Kết quả đạt được
- Rút ra kết luận quan trọng: Hơn 80% các bài báo khoa học hiện nay chỉ dừng lại ở việc phát hiện và chứng minh sự bất công trên dữ liệu có sẵn; có rất ít công trình thực sự đề xuất thuật toán sửa chữa hay cải thiện tính công bằng.
- Xác định nghiên cứu công bằng đa bên liên quan (cân bằng giữa người nghe, nghệ sĩ và nền tảng phát hành) là khoảng trống học thuật lớn cần được lấp đầy.

#### d. Ưu và nhược điểm
- *Ưu điểm:* Cung cấp góc nhìn đạo đức và xã hội sâu sắc cho công nghệ AI; giúp các kỹ sư nhận thức rõ trách nhiệm xã hội khi lập trình thuật toán.
- *Nhược điểm:* Là bài tổng quan định tính, không có mã nguồn giải thuật toán học độc lập để chạy thực nghiệm đo đạc lại.

---

### 8. Shakespeare et al. (2020)
**Tên bài báo:** *Exploring Artist Gender Bias in Music Recommendation* (2020)  
**Tập tin tài liệu:** [Exploring_Artist_Gender_Bias_in_Music_Recommendation.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Exploring_Artist_Gender_Bias_in_Music_Recommendation.pdf)

#### a. Phương pháp
- **Định nghĩa trực quan:** Nghiên cứu thực nghiệm chứng minh rằng các thuật toán lọc cộng tác (CF) đang âm thầm "học thói quen thiên vị giới tính" từ người dùng và khuếch đại sự thiên vị đó lên gấp nhiều lần. Nhóm tác giả so sánh tỷ lệ nghệ sĩ nam/nữ trong lịch sử nghe nhạc thực tế với tỷ lệ nghệ sĩ nam/nữ mà máy tính gợi ý ra.
- **Ví dụ cách hoạt động:**
  - *Bước 1 (Ghi nhận thiên lệch ban đầu):* Trong lịch sử nghe nhạc của bạn, bạn nghe 75% ca sĩ nam và 25% ca sĩ nữ.
  - *Bước 2 (Thuật toán lọc cộng tác xử lý):* Máy tính chạy thuật toán k-láng giềng hoặc phân rã ma trận NMF để tính điểm.
  - *Bước 3 (Khuếch đại thiên lệch ở đầu ra):* Trong danh sách Top-10 bài hát gợi ý cho bạn, máy tính đề xuất tới 9 ca sĩ nam (90%) và chỉ có 1 ca sĩ nữ (10%). Thuật toán đã làm trầm trọng thêm sự lép vế của nghệ sĩ nữ.

#### b. Bộ dữ liệu thực nghiệm (Schema & Chú thích)
Sử dụng tập dữ liệu **LFM-1b** và **LFM-360K** được gán nhãn giới tính nghệ sĩ từ cơ sở dữ liệu mở **MusicBrainz** và **Wikidata**:

```
Bảng 1: Lịch sử người dùng kèm giới tính (User-Artist Interaction)
+---------------+---------------+-----------------------+
| user_id       | artist_id     | play_count            |
| (Chuỗi ký tự) | (Chuỗi ký tự) | (Số lượt nghe lũy kế) |
+---------------+---------------+-----------------------+
| u_8812        | art_991       | 152                   |
+---------------+---------------+-----------------------+

Bảng 2: Thông tin giới tính đối soát (Artist Gender Metadata)
+---------------+--------------------+-----------------------------+
| artist_id     | artist_name        | gender                      |
| (Chuỗi ký tự) | (Tên nghệ sĩ)      | ("m", "f", "mixed", "n/a")  |
+---------------+--------------------+-----------------------------+
| art_991       | "Adele"            | "f" (Nữ)                    |
| art_504       | "Coldplay"         | "mixed" / "group" (Ban nhạc)|
+---------------+--------------------+-----------------------------+
```

- **Chú thích các trường dữ liệu:**
  - `user_id`: Định danh tài khoản người nghe trên Last.fm.
  - `artist_id`: Mã định danh nghệ sĩ tương ứng.
  - `play_count`: Số lượt nghe của người dùng đó đối với nghệ sĩ cụ thể.
  - `gender`: Giới tính của nghệ sĩ được chuẩn hóa thành các nhóm: `m` (nam cá nhân), `f` (nữ cá nhân), `mixed` (ban nhạc có cả nam và nữ), và `n/a` (không rõ hoặc nghệ sĩ ảo).

#### c. Kết quả đạt được
- Thuật toán *Most Popular* (gợi ý theo độ phổ biến) gây ra sự bất bình đẳng giới tính trầm trọng nhất.
- Các thuật toán lọc cộng tác cá nhân hóa đạt độ chính xác rất cao trên LFM-1b (NMF đạt Precision = 0.734, NDCG = 0.880; UserKNN đạt Precision = 0.676, NDCG = 0.793), nhưng cả hai đều khuếch đại khoảng cách giới tính có lợi cho nghệ sĩ nam đối với tất cả các nhóm khán giả.

#### d. Ưu và nhược điểm
- *Ưu điểm:* Phương pháp thực nghiệm định lượng mẫu mực, có kiểm định thống kê tin cậy ($p < 0.05$), đưa ra con số báo động thực tế về sự thiên lệch thuật toán.
- *Nhược điểm:* Chưa đề xuất giải thuật tái sắp xếp để khắc phục hiện tượng thiên lệch giới tính này mà mới dừng lại ở khâu đo lường và cảnh báo.

---

### 9. Doh, Choi, Nam (2025)
**Tên bài báo:** *TalkPlay: Multimodal Music Recommendation with Large Language Models* (arXiv 2025)  
**Tập tin tài liệu:** [TalkPlay_Multimodal_Music_Recommendation_with_Large_Language_Models.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/TalkPlay_Multimodal_Music_Recommendation_with_Large_Language_Models.pdf)

#### a. Phương pháp
- **Định nghĩa trực quan:** Đề xuất hệ thống **TALKPLAY**, biến bài toán khuyến nghị âm nhạc thành một cuộc trò chuyện tự nhiên với Mô hình ngôn ngữ lớn (tương tự như ChatGPT phiên bản chuyên gia âm nhạc). Bài toán được mô hình hóa thành việc **dự đoán từ tiếp theo trong câu nói**: máy tính vừa trò chuyện tâm tình, giải thích lý do, vừa đưa ra đúng mã bài hát phù hợp nhất với yêu cầu bằng lời nói tự nhiên của bạn.
- **Ví dụ cách hoạt động:**
  - *Bước 1 (Người dùng trò chuyện tự nhiên):* Bạn nhắn tin: *"Hôm nay trời mưa to, mình vừa chia tay người yêu, muốn nghe một bài hát indie buồn có tiếng đàn guitar mộc mạc"*.
  - *Bước 2 (Chuyển đổi âm nhạc thành từ ngữ - Tokenizer):* Bộ mã hóa âm nhạc chuyển các thông số kỹ thuật (âm thanh mộc, lời bài hát buồn, thể loại indie) thành các mã số token mà mô hình ngôn ngữ hiểu được.
  - *Bước 3 (Sinh câu trả lời kèm gợi ý):* Mô hình LLM tự động trả lời bằng văn bản thấu hiểu cảm xúc: *"Mình rất tiếc khi nghe chuyện của bạn. Hãy thả lỏng và nghe bài hát này nhé..."* và chèn ngay mã bài hát phù hợp nhất vào trình phát nhạc của bạn.

#### b. Bộ dữ liệu thực nghiệm (Schema & Chú thích)
Bộ dữ liệu hội thoại âm nhạc đa phương thức quy mô lớn kết hợp từ **Million Song Dataset**, **Spotify Playlists**, **MusicCaps**, và tập hội thoại sinh tự động:

```
Bảng 1: Lịch sử hội thoại người dùng - trợ lý ảo (Conversational Dialogues)
+---------------+------------+---------------+-----------------------------------------------+
| dialogue_id   | turn_idx   | speaker       | utterance (Nội dung câu nói)                  |
| (Chuỗi ký tự) | (Số thứ tự)| (user/system) | (Văn bản chứa văn cảnh và token bài hát)      |
+---------------+------------+---------------+-----------------------------------------------+
| dlg_001       | 1          | user          | "Gợi ý cho mình bài nhạc acoustic buồn..."   |
| dlg_001       | 2          | system        | "Bạn thử nghe bài này nhé: [TRACK_ID_9041]"   |
+---------------+------------+---------------+-----------------------------------------------+

Bảng 2: Mã hóa âm nhạc rời rạc (Discrete Music Tokens)
+---------------+-------------------------------------+-------------------------------------+
| track_id      | text_metadata                       | audio_semantic_tokens               |
| (Chuỗi ký tự) | (Tên bài, ca sĩ, thể loại, lời)     | (Chuỗi các token biểu diễn âm thanh)|
+---------------+-------------------------------------+-------------------------------------+
| trk_9041      | "Lạ Lùng | Vũ | Indie Pop | Lời..." | <audio_tok_12> <audio_tok_88> ...   |
+---------------+-------------------------------------+-------------------------------------+
```

- **Chú thích các trường dữ liệu:**
  - `dialogue_id`: Mã phiên trò chuyện giữa người dùng và trợ lý ảo AI.
  - `turn_idx`: Lượt trò chuyện qua lại trong một cuộc đối thoại (turn 1: người dùng hỏi, turn 2: bot trả lời...).
  - `speaker`: Người đang nói (`user`: người nghe nhạc, `system`: trợ lý AI).
  - `utterance`: Nội dung phát ngôn bằng ngôn ngữ tự nhiên. Trong câu trả lời của hệ thống sẽ chứa mã thẻ token đặc biệt `[TRACK_ID_xxxx]` tương ứng với bài hát được gợi ý.
  - `audio_semantic_tokens`: Các mã số nguyên rời rạc nén từ sóng âm thanh (CLAP/MERT) giúp LLM có thể "đọc" được âm thanh như một từ vựng thông thường.

#### c. Kết quả đạt được
- TALKPLAY vượt trội hơn tất cả các mô hình cơ sở: đạt **MRR = 0.049** và đặc biệt đạt **Hit@1 = 0.026** (cao gấp **5 lần** so với mô hình tốt thứ hai). Nghĩa là ngay ở lượt gợi ý đầu tiên, bài hát đề xuất đã trúng phóc ý định của người nghe.
- Chứng minh tính ưu việt của việc kết hợp ngôn ngữ lớn với việc lắng nghe âm thanh đa giác quan.

#### d. Ưu và nhược điểm
- *Ưu điểm:* Mang lại trải nghiệm người dùng tuyệt vời, trực quan, cho phép tìm nhạc bằng các câu miêu tả cảm xúc phức tạp mà các hệ thống cũ không thể làm được.
- *Nhược điểm:* Tốc độ phản hồi chậm (tính bằng giây, không thể phản hồi tức thì vài mili-giây như SVD); đòi hỏi chi phí phần cứng và thẻ đồ họa GPU cực kỳ đắt đỏ; có thể gặp rủi ro "ảo giác" (LLM tự bịa ra bài hát không có thật nếu không được kiểm soát).

---

## BẢNG TỔNG HỢP ĐỐI SÁNH CÁC CÔNG TRÌNH KHẢO SÁT VÀ TỔNG QUAN

| STT | Tài liệu | Hướng tiếp cận chính | Dữ liệu thực nghiệm chính | Độ đo & Kết quả nổi bật | Ưu điểm & Hạn chế chính |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | **Song et al. (2012)** | Khảo sát tổng quan RS âm nhạc (CF, CBM, Emotion, Context, Motivation) | MIREX, Last.fm, Allmusic, Pandora | Precision, Recall, F-measure, MAP; CF và CBM hiệu quả nhất | Toàn diện về lý thuyết người nghe; thiếu benchmark định lượng độc lập |
| **2** | **Schedl et al. (2018)** | Khảo sát 3 thách thức lớn (Cold-start, APC, Evaluation) & 3 tầm nhìn | LFM-1b, MSD, Spotify RecSys Challenge 2018 | Đánh giá ngoài độ chính xác (novelty, diversity, session-coherence) | Bản đồ định hướng nghiên cứu sâu sắc; không có thuật toán cụ thể |
| **3** | **Schedl et al. (2015)** | Chuyên khảo Handbook: MIR audio, tags, playlist, context, hybrid | Yahoo! Music, MSD, Last.fm 360K/1K, AotM | So sánh toàn diện catalog; chỉ ra "trần kính" của độ tương đồng âm thanh | Cẩm nang chuẩn mực, công thức chặt chẽ; chưa có GNN và LLM |
| **4** | **Deldjoo et al. (2021)** | Khảo sát khuyến nghị dựa trên nội dung (Onion Model 5 tầng) & GNN | MSD, Spotify MPD, FMA, Last.fm LFM-1b | Multi-modal fusion và GNN vượt trội đơn phương thức | Cập nhật GNN và Deep Audio; chi phí tính toán trích xuất rất lớn |
| **5** | **Lacic et al. (2024)** | Mô hình nơ-ron đồ thị lai PinSage (Playlist-Song Graph + Audio CNN) | Spotify (10.000 playlists, 277k bài hát) | Hit Ratio@K, NDCG@K, MRR; PinSage vượt trội PPR và Audio-only | Giải quyết cold-start bằng tính quy nạp; huấn luyện đồ thị nặng |
| **6** | **Ziaoddini et al. (2025)**| MM-GNN: Đồ thị dị thể đa phương thức (Audio, Lyrics, Art) + Mạng xã hội | MSD-A (25k users, 328k songs), Last.fm | Recall@50 = 0.075, NDCG@50 = 0.043 trên MSD-A (vượt xa NGCF, VBPR) | Tận dụng quan hệ xã hội và đa phương thức; cấu trúc mô hình rất phức tạp |
| **7** | **Ferraro et al. (2022)** | Khảo sát công bằng đa bên (Consumer, Provider, Platform) | LFM-1b, Last.fm 360K, MSD | >80% nghiên cứu chỉ phân tích hiện trạng, thiếu giải pháp cải thiện | Góc nhìn đa bên liên quan sâu sắc; chưa có giải thuật toán học độc lập |
| **8** | **Shakespeare et al. (2020)**| Phân tích thực nghiệm thiên lệch giới tính nghệ sĩ trong CF (kNN, NMF) | LFM-1b, LFM-360K (gán nhãn MusicBrainz) | Bias Disparity; Popularity và CF đều khuếch đại thiên lệch nghệ sĩ nam | Minh chứng thực nghiệm có kiểm định chặt chẽ; chưa có cơ chế giảm thiên lệch |
| **9** | **Doh et al. (2025)** | TALKPLAY: Khuyến nghị hội thoại đa phương thức bằng LLM (Next-token prediction) | MSD, Spotify playlists, MusicCaps, Song Describer | Hit@1 = 0.026 (gấp 5 lần baseline), MRR = 0.049 | Tương tác tự nhiên, hiểu ngữ nghĩa sâu; độ trễ cao và chi phí GPU lớn |
