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
  - Đưa ra giả định cốt lõi của lọc cộng tác: *những người dùng từng có quan điểm/hành vi tương đồng trong quá khứ sẽ có xu hướng tiếp tục đồng thuận trong tương lai*.
  - Đề xuất công thức tính độ tương đồng giữa người dùng bằng hệ số tương quan Pearson và mô hình dự đoán đánh giá dựa trên độ lệch có trọng số so với điểm trung bình của từng láng giềng.
  - Thiết kế kiến trúc mở với cơ chế "Better Bit Bureaus" hỗ trợ bảo vệ quyền riêng tư qua định danh giả (pseudonyms).
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 1.1 (Bối cảnh và lý do chọn đề tài):** Căn cứ lý thuyết cho giả định nền tảng của họ thuật toán Lọc cộng tác (CF).
  - **Mục 2.1 (Tổng quan hệ thống khuyến nghị):** Định nghĩa và phân loại nhánh tiếp cận Collaborative Filtering.
  - **Mục 2.3 (Lọc cộng tác dựa trên người dùng - User-based CF):** Cơ sở lý thuyết trực tiếp cho công thức tương quan Pearson (Công thức 2.2) và công thức dự đoán điểm số có trọng số lệch trung bình (Công thức 2.3).
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Đưa vào **Bảng 2.2** (công trình nền tảng khởi nguồn cho User-based CF).
  - **Mục 3.6 & 3.6.1 (Các mô hình đề xuất / Thuật toán User-based CF):** Xây dựng **Thuật toán 3.1** (User-kNN).

---

### 2. Sarwar et al. (2001)
- **Tên bài báo:** *Item-Based Collaborative Filtering Recommendation Algorithms* (WWW 2001)
- **Tập tin tài liệu:** [Sarwar et al. 2001.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Sarwar%20et%20al.%202001.pdf)
- **Đóng góp chính của bài báo:**
  - Đề xuất giải thuật Lọc cộng tác dựa trên sản phẩm (**Item-based Collaborative Filtering**), giải quyết triệt để nút thắt cổ chai về khả năng mở rộng (scalability) và tốc độ phản hồi thời gian thực của User-based CF khi số lượng người dùng tăng đột biến.
  - Đưa ra độ đo tương đồng cosine điều chỉnh (**Adjusted Cosine Similarity**) nhằm loại bỏ sự chênh lệch trong thang đánh giá chủ quan giữa các cá nhân.
  - Chứng minh mối quan hệ giữa các mục (items) ổn định hơn nhiều theo thời gian so với người dùng, cho phép tính toán trước ma trận tương đồng offline và tái sử dụng cho suy luận online với chi phí $O(1)$ thay vì $O(|U|)$ trên mỗi truy vấn.
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
  - Tổng kết có hệ thống các kỹ thuật Phân rã ma trận (**Matrix Factorization - MF**) chứng minh tính vượt trội trong giải thưởng quốc tế Netflix Prize.
  - Mô hình hóa sở thích người dùng và đặc tính sản phẩm vào một không gian nhân tử tiềm ẩn chung (*latent factor space*) thông qua tích vô hướng vector $p_u^T q_i$, đồng thời tích hợp các số hạng thiên lệch hệ thống (*global mean, user bias, item bias*).
  - Thiết lập hàm mất mát bình phương có điều chuẩn $L_2$ và chi tiết hóa phương pháp tối ưu bằng hạ độ dốc ngẫu nhiên (**SGD**) và bình phương tối thiểu luân phiên (**ALS**).
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 1.1 (Bối cảnh và lý do chọn đề tài):** Căn cứ đưa mô hình phân rã ma trận SVD vào danh mục 3 mô hình nền tảng.
  - **Mục 2.5 (Phân rã ma trận và SVD):** Cơ sở lý thuyết cho công thức biểu diễn nhân tử tiềm ẩn kèm bias (Công thức 2.6) và hàm mất mát điều chuẩn (Công thức 2.7).
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Đưa vào **Bảng 2.2** (mô hình Matrix Factorization / SVD-bias).
  - **Mục 3.6 & 3.6.3 (Các mô hình đề xuất / Thuật toán SVD huấn luyện bằng SGD):** Xây dựng **Thuật toán 3.3**, đặc biệt là chi tiết cập nhật đồng thời tham số bằng `p_u_old` để đảm bảo đạo hàm chính xác.
  - **Mục 4.4 & 4.8 (Thiết kế thí nghiệm E3 & So sánh chi tiết theo nhóm mô hình):** Đánh giá baseline cá nhân hóa chính và phân tích lợi ích của vector tiềm ẩn.

---

### 4. Hu, Koren, Volinsky (2008)
- **Tên bài báo:** *Collaborative Filtering for Implicit Feedback Datasets* (ICDM 2008)
- **Tập tin tài liệu:** [Hu, Koren, Volinsky 2008.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Hu,%20Koren,%20Volinsky%202008.pdf)
- **Đóng góp chính của bài báo:**
  - Thiết lập khung lý thuyết chuẩn tắc cho bài toán lọc cộng tác trên dữ liệu phản hồi ngầm (**implicit feedback**).
  - Chỉ ra 3 đặc trưng cốt lõi của phản hồi ngầm: không có phản hồi âm tường minh (*no negative feedback*), dữ liệu chứa nhiều nhiễu (*inherent noise*), và giá trị số quan sát được (như lượt nghe/lượt xem) phản ánh mức độ tin cậy (*confidence*) chứ không tỷ lệ tuyến tính với độ yêu thích.
  - Đề xuất mô hình phân rã ma trận tách biệt biến nhị phân ưu tiên ($p_{ui}$) và trọng số độ tin cậy ($c_{ui} = 1 + \alpha r_{ui}$), cùng thuật toán giải hiệu quả ALS tuyến tính theo kích thước dữ liệu.
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 1.1 & 1.2 (Bối cảnh & Vấn đề cần giải quyết):** Căn cứ nhận diện bản chất dữ liệu `listening count` trong Last.fm HetRec 2011 là phản hồi ngầm một phía.
  - **Mục 2.2 (Dữ liệu tương tác và phản hồi ngầm):** Trích dẫn trực tiếp 3 điểm khác biệt cốt lõi; làm cơ sở cho việc áp dụng phép biến đổi log-transform $y_{ui} = \ln(1 + w_{ui})$ (Công thức 2.1) để nén miền giá trị lượt nghe.
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Đưa vào **Bảng 2.2** (cơ sở xử lý listening count và mô hình hóa phản hồi ngầm).
  - **Mục 3.4 & 3.5 (Thiết kế bộ dữ liệu & Tiền xử lý dữ liệu):** Thiết kế pipeline làm sạch, gộp tương tác trùng và biến đổi log ma trận phản hồi ngầm.

---

### 5. Herlocker et al. (2004)
- **Tên bài báo:** *Evaluating Collaborative Filtering Recommender Systems* (ACM TOIS 2004)
- **Tập tin tài liệu:** [Herlocker et al. 2004.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Herlocker%20et%20al.%202004.pdf)
- **Đóng góp chính của bài báo:**
  - Khảo sát kinh điển và toàn diện nhất đặt ra các nguyên tắc, chuẩn mực và phương pháp luận đánh giá hệ thống lọc cộng tác.
  - Phân loại rõ ràng các tác vụ thực tế của người dùng (*Find Good Items, Recommend Sequence, Annotation in Context...*) và tương ứng với từng nhóm độ đo (đo sai số dự đoán điểm như MAE/RMSE so với độ đo xếp hạng và phân loại như Precision, Recall, F-measure, ROC).
  - Nhấn mạnh tầm quan trọng của các tiêu chí ngoài độ chính xác (*novelty, coverage, diversity, serendipity*) và đề xuất kỹ thuật **Significance Weighting** nhằm giảm trọng số của những cặp tương đồng có quá ít tương tác chung.
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 2.3 (Lọc cộng tác dựa trên người dùng - User-based CF):** Áp dụng kỹ thuật Significance Weighting với ngưỡng $\gamma$ (nhân hệ số $\frac{\min(|I_{av}|, \gamma)}{\gamma}$) để ổn định độ tương đồng trên dữ liệu thưa.
  - **Mục 2.7 (Các độ đo đánh giá mô hình):** Cơ sở xây dựng khung đánh giá đa diện, nguyên tắc minh bạch thực nghiệm (báo cáo rõ seed, quy tắc lọc, không chỉ báo cáo trung bình toàn cục).
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Định vị phương pháp luận đánh giá trong **Bảng 2.2**.
  - **Mục 3.6.1 (Thuật toán User-based CF):** Tích hợp tham số $\gamma$ vào Thuật toán 3.1.
  - **Mục 3.9 & 4.5 (Tiêu chí đánh giá & Kiểm định thống kê):** Phân tách phân tích lỗi theo nhóm độ dài lịch sử người dùng để tránh che giấu thất bại có hệ thống.

---

### 6. Cremonesi, Koren, Turrin (2010)
- **Tên bài báo:** *Performance of Recommender Algorithms on Top-N Recommendation Tasks* (ACM RecSys 2010)
- **Tập tin tài liệu:** [Cremonesi et al. 2010.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Cremonesi%20et%20al.%202010.pdf)
- **Đóng góp chính của bài báo:**
  - Phát hiện bước ngoặt: **Tối ưu hóa RMSE không đồng nghĩa với cải thiện chất lượng xếp hạng Top-N** (các mô hình giảm được RMSE thường chỉ làm tốt ở các mục phổ biến, dễ đoán, nhưng lại cho danh sách Top-N nghèo nàn).
  - Chỉ ra hiện tượng các thuật toán không cá nhân hóa (*Popularity baseline*) có thể đánh bại hoặc đạt độ chính xác gần bằng các mô hình phức tạp nếu đánh giá Top-N bị chi phối bởi các mục phổ biến.
  - Đề xuất thuật toán **PureSVD** (phân rã trực tiếp ma trận tương tác nhị phân/chuẩn hóa lấp đầy số 0 bằng SVD đại số tuyến tính) với hiệu năng xếp hạng Top-N vượt trội và đơn giản bất ngờ.
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 1.1 & 1.2 (Bối cảnh & Vấn đề cần giải quyết):** Căn cứ chứng minh việc chỉ đo RMSE là thiếu sót, bắt buộc phải đánh giá xếp hạng Top-K (NDCG@K, Recall@K).
  - **Mục 2.5 (Phân rã ma trận và SVD):** Trình bày biến thể PureSVD dùng phép chiếu đại số ma trận.
  - **Mục 2.7 (Các độ đo đánh giá mô hình):** Phân tích sự bất tương xứng giữa độ đo dự đoán điểm số và độ đo xếp hạng Top-K.
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Đưa vào **Bảng 2.2** (cơ sở lựa chọn độ đo Top-K và biến thể PureSVD).
  - **Mục 3.6 & 3.8 (Các mô hình đề xuất & Baseline):** Đưa PureSVD vào danh mục thử nghiệm; bắt buộc dùng Popularity baseline làm mốc đối chứng tối thiểu.
  - **Mục 4.7 (Kết quả thực nghiệm định lượng):** Làm nguyên tắc diễn giải: nếu RMSE giảm nhưng NDCG@10 giảm thì đây là minh chứng cho luận điểm của Cremonesi.

---

### 7. Kowald, Schedl, Lex (2020)
- **Tên bài báo:** *The Unfairness of Popularity Bias in Music Recommendation: A Reproducibility Study* (ECIR 2020)
- **Tập tin tài liệu:** [Kowald, Schedl, Lex 2020.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Kowald,%20Schedl,%20Lex%202020.pdf)
- **Đóng góp chính của bài báo:**
  - Tái lập và kiểm chứng hiện tượng thiên lệch phổ biến (**Popularity Bias**) và sự đối xử bất công thuật toán trong **miền âm nhạc** trên tập dữ liệu Last.fm quy mô lớn (LFM-1b).
  - Phân nhóm người dùng theo mức độ thị hiếu chính thống (*mainstreaminess*) thành 3 nhóm: *low-mainstream*, *medium-mainstream*, và *high-mainstream*.
  - Chứng minh thực nghiệm rằng các thuật toán lọc cộng tác hiện đại thiên vị nặng nề cho các nghệ sĩ phổ biến và phục vụ kém nhất (độ chính xác khuyến nghị thấp nhất một cách có ý nghĩa thống kê) đối với nhóm người dùng thích nghe nhạc ngách (*low-mainstream*).
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 1.1 & 1.2 (Bối cảnh & Vấn đề cần giải quyết):** Căn cứ thực tiễn chứng minh thiên lệch phổ biến là vấn đề nghiêm trọng trên dữ liệu Last.fm.
  - **Mục 1.9.1 (Ý nghĩa khoa học):** Định vị đóng góp của đề tài trong việc kiểm chứng định lượng giải pháp giảm thiên lệch trong miền âm nhạc.
  - **Mục 2.6 (Sparsity, cold-start và popularity bias):** Cơ sở lý thuyết về sự bất công của thiên lệch phổ biến đối với các nhóm người dùng khác nhau.
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Đưa vào **Bảng 2.2** (động lực trực tiếp cho đề tài).
  - **Mục 3.7.1 (Mô-đun cải tiến M1):** Động lực trực tiếp để thiết kế thuật toán tái xếp hạng tham lam (MMR có phạt độ phổ biến) nhằm bảo vệ nhóm nghệ sĩ đuôi dài (long-tail).
  - **Mục 4.4 & 4.9 (Thí nghiệm E4, E5 & Đánh giá độ đa dạng, thiên lệch):** Đo lường ARP, Gini, Coverage và phân tích hiệu năng theo các nhóm người dùng.

---

### 8. Ji et al. (2023)
- **Tên bài báo:** *A Critical Study on Data Leakage in Recommender System Offline Evaluation* (ACM TOIS 2023)
- **Tập tin tài liệu:** [Ji et al. 2023.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Ji%20et%20al.%202023.pdf)
- **Đóng góp chính của bài báo:**
  - Nghiên cứu phản biện sâu sắc và toàn diện về hiểm họa **rò rỉ dữ liệu (data leakage)** trong quy trình đánh giá ngoại tuyến (offline evaluation) của hệ thống khuyến nghị.
  - Chỉ ra rằng các chiến lược chia tập không tuân thủ dòng thời gian toàn cục (*global timeline*) – chẳng hạn như chia ngẫu nhiên hoặc leave-last-one-out không neo thời gian – khiến mô hình vô tình học trước các tương tác trong tương lai, làm sai lệch thứ hạng tương đối giữa các mô hình và giảm độ tin cậy của kết quả benchmark.
  - Đề xuất khung đánh giá tuân thủ timeline (*timeline evaluation scheme*) và kêu gọi xem xét lại các kết luận vượt trội của nhiều mô hình học sâu.
- **Đối chiếu áp dụng vào Đề cương chi tiết:**
  - **Mục 1.2 (Vấn đề cần giải quyết):** Cảnh báo nguy cơ rò rỉ dữ liệu khi chia tập huấn luyện/kiểm thử.
  - **Mục 1.9.1 (Ý nghĩa khoa học):** Thiết lập quy trình so sánh có kiểm soát, minh bạch và chặt chẽ.
  - **Mục 2.8 (Rủi ro rò rỉ dữ liệu và thực hành đánh giá tin cậy):** Trích dẫn trực tiếp luận điểm của Ji et al. để thừa nhận giới hạn khách quan của bộ dữ liệu Last.fm HetRec 2011 (do không có timestamp ở mức tương tác), từ đó giải trình minh bạch việc sử dụng giao thức Given-N / random per-user split.
  - **Mục 2.9 (Tổng quan các nghiên cứu liên quan):** Đưa vào **Bảng 2.2** (cơ sở thiết kế phân chia tập dữ liệu).
  - **Mục 3.5 (Tiền xử lý và chiến lược chia tập dữ liệu):** Cố định seed, chỉ tinh chỉnh siêu tham số trên validation và chạy trên tập test đúng 1 lần duy nhất để tránh rò rỉ thông tin ngược từ tập test.
  - **Mục 5.7 (Giới hạn của đề tài):** Ghi nhận giới hạn về timeline split do đặc thù bộ dữ liệu tĩnh.

---

## PHẦN 2: NHÓM TÀI LIỆU KHẢO SÁT VÀ TỔNG QUAN (9 TÀI LIỆU)
*(Đã loại bỏ bài số 4: Kleć & Wieczorkowska, 2021 theo đúng yêu cầu)*

---

### 1. Song, Dixon, Pearce (2012)
**Tên bài báo:** *A Survey of Music Recommendation Systems and Future Perspectives* (CMMR 2012)  
**Tập tin tài liệu:** [A_Survey_of_Music_Recommendation_Systems_and_Future_Perspectives.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/A_Survey_of_Music_Recommendation_Systems_and_Future_Perspectives.pdf)

- **Phương pháp:**
  - Khảo sát hệ thống hóa khung làm việc chung của hệ khuyến nghị âm nhạc với 3 thành phần chính: Mô hình hóa người dùng (*User Modelling*), Hồ sơ hóa sản phẩm (*Item Profiling*), và Thuật toán khớp nối (*Match Algorithms*).
  - Khảo sát 6 lớp mô hình: (1) Truy hồi siêu dữ liệu biên tập/nhân khẩu học (Metadata IR); (2) Lọc cộng tác (Memory-based kNN, Model-based Bayesian/Latent Factor, Hybrid CF); (3) Mô hình dựa trên nội dung âm thanh (Content-based Audio - MFCC, nhịp điệu, cao độ); (4) Mô hình dựa trên cảm xúc (Emotion-based theo mô hình vòng tròn cảm xúc Thayer/Russell); (5) Mô hình theo ngữ cảnh (Context-based: thời gian, địa điểm, hoạt động); (6) Mô hình lai (Hybrid).
  - Đề xuất mô hình khái niệm mới: *Motivation-based model* kết hợp tâm lý học âm nhạc và hành vi con người.
- **Bộ dữ liệu thực nghiệm:**
  - Khảo sát và tổng hợp các nguồn dữ liệu từ chiến dịch đánh giá MIREX (Music Information Retrieval Evaluation eXchange), nền tảng Last.fm (scrobbling logs, social tags), Allmusic, Pandora (Music Genome Project), Shazam, và Musicovery.
- **Kết quả đạt được:**
  - Khẳng định Lọc cộng tác (CF) và Mô hình nội dung âm thanh (CBM) là hai hướng tiếp cận hoạt động hiệu quả nhất trong thực tế thương mại.
  - Nhận định CF cho kết quả tốt trên các nghệ sĩ/bài hát phổ biến nhưng bộc lộ giới hạn nghiêm trọng ở phần đuôi dài (long-tail) do thiên lệch phổ biến.
  - Khảo sát các tiêu chuẩn đánh giá từ độ đo kỹ thuật (Precision, Recall, F-measure, ROC, MAP) đến trải nghiệm người dùng chủ quan (Novelty, Serendipity, User Satisfaction).
- **Ưu và nhược điểm:**
  - *Ưu điểm:* Cung cấp bức tranh toàn cảnh, đa chiều về việc chuyển dịch từ mô hình kỹ thuật thuần túy sang các mô hình lấy người nghe làm trung tâm (cảm xúc, ngữ cảnh, động cơ nghe nhạc).
  - *Nhược điểm:* Chưa có thực nghiệm benchmark định lượng độc lập trên một bộ dữ liệu thống nhất; mô hình đề xuất dựa trên động cơ (motivation-based) mới dừng ở mức định hướng lý thuyết, khó thu thập dữ liệu sinh lý/tâm lý thời gian thực.

---

### 2. Schedl, Zamani, Chen, Deldjoo, Elahi (2018)
**Tên bài báo:** *Current Challenges and Visions in Music Recommender Systems Research* (International Journal of Multimedia Information Retrieval - IJMIR 2018)  
**Tập tin tài liệu:** [Current_Challenges_and_Visions_in_Music_Recommender_Systems_Research.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Current_Challenges_and_Visions_in_Music_Recommender_Systems_Research.pdf)

- **Phương pháp:**
  - Khảo sát chuyên sâu phân tích những đặc thù riêng biệt của lĩnh vực âm nhạc so với các lĩnh vực khuyến nghị khác (e-commerce, phim ảnh): vật phẩm có thời lượng tiêu thụ ngắn (3-5 phút), tần suất nghe lặp lại cao (*repeat consumption*), người dùng tiêu thụ theo chuỗi/danh sách (*playlists/sessions*), và trải nghiệm âm nhạc mang tính cảm xúc và thụ động (*lean-back mode*).
  - Phân tích 3 Thách thức lớn (**Grand Challenges**): (1) Vấn đề khởi đầu lạnh (Cold-start); (2) Tự động tiếp nối danh sách phát (Automatic Playlist Continuation - APC); (3) Phương pháp luận đánh giá hệ thống khuyến nghị âm nhạc.
  - Đề xuất 3 Tầm nhìn tương lai (**Future Visions**): Khuyến nghị âm nhạc lấy cảm hứng từ tâm lý học (*Psychologically inspired*), Khuyến nghị nhận biết tình huống (*Situation-aware*), và Khuyến nghị nhận biết văn hóa (*Culture-aware*).
- **Bộ dữ liệu thực nghiệm:**
  - Khảo sát và so sánh các tập dữ liệu chuẩn: LFM-1b (hơn 1 tỷ lượt nghe), Million Song Dataset (MSD), Spotify RecSys Challenge 2018 (1 triệu playlists cho tác vụ APC), Last.fm 360K/1K, 30Music, và Art of the Mix (AotM).
- **Kết quả đạt được:**
  - Chỉ ra rằng đánh giá ngoại tuyến chỉ bằng RMSE hoặc Accuracy truyền thống là không đầy đủ và dễ gây ngộ nhận trong âm nhạc; cần đánh giá qua tính gắn kết chuỗi, độ đa dạng, độ mới và sự phù hợp ngữ cảnh.
  - Định hình bài toán APC như một tác vụ trung tâm thúc đẩy các thuật toán học sâu và học tuần tự (sequential models).
- **Ưu và nhược điểm:**
  - *Ưu điểm:* Là tài liệu định hướng nghiên cứu (roadmap) có tầm ảnh hưởng sâu sắc, chỉ rõ các khoảng trống nghiên cứu then chốt mà các mô hình truyền thống bỏ quên.
  - *Nhược điểm:* Là bài báo khảo sát và định hướng lý thuyết, không trực tiếp cài đặt mô hình giải thuật mới hoặc báo cáo bảng chỉ số thực nghiệm so sánh riêng.

---

### 3. Schedl, Knees, McFee, Bogdanov, Kaminskas (2015)
**Tên bài báo:** *Music Recommender Systems* (Chương 13, Recommender Systems Handbook, 2nd Edition, Springer, 2015)  
**Tập tin tài liệu:** [RecSysHandbook2015_ch13_musicrec.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/RecSysHandbook2015_ch13_musicrec.pdf)

- **Phương pháp:**
  - Chuyên khảo chuẩn mực toàn diện nhất về mặt kỹ thuật cho hệ thống khuyến nghị âm nhạc, bao quát:
    + Phương pháp dựa trên nội dung: trích xuất đặc trưng âm thanh (âm sắc - timbre/MFCC, nhịp điệu - rhythm, hòa âm - pitch/harmony), khai phá siêu dữ liệu web và social tags.
    + Phương pháp nhận biết ngữ cảnh: lọc trước (pre-filtering), lọc sau (post-filtering), và mô hình hóa ngữ cảnh trực tiếp (contextual modeling).
    + Phương pháp lai (Hybrid): kết hợp có trọng số (weighted), chuyển mạch (switching), xếp tầng (cascade), và kết hợp đặc trưng.
    + Tự động tạo danh sách phát (Automatic Playlist Generation - APG): mô hình Markov Chains, đồ thị tương đồng, và tối ưu hóa thỏa mãn ràng buộc.
    + Khung phương pháp luận đánh giá: offline evaluation, user studies, và online A/B testing.
- **Bộ dữ liệu thực nghiệm:**
  - Bảng thống kê chi tiết các bộ dữ liệu công khai lớn nhất lúc bấy giờ: Yahoo! Music (624k items, 1M users, 262M ratings), Million Song Dataset - MSD (1M bài hát, 48M tương tác), Last.fm 360K, Last.fm 1K, MusicMicro, MMTD, và AotM-2011 (85k playlists).
- **Kết quả đạt được:**
  - Khẳng định lọc cộng tác cho độ chính xác cao nhất khi có mật độ tương tác lớn nhưng hoàn toàn bất lực trước vật phẩm mới (cold-start bài hát mới).
  - Phân tích hiện tượng "trần kính" (*glass ceiling*) của độ tương đồng âm thanh: các đặc trưng âm sắc thấp (timbre) chỉ giúp phân biệt bài hát ở mức tương đối nhưng không thể phản ánh trọn vẹn ngữ nghĩa cao cấp của gu âm nhạc.
  - Đưa ra kết luận rằng việc tạo danh sách phát (playlist) đòi hỏi tính chuyển tiếp mượt mà (*smooth transition*) và sự đồng nhất nội tại hơn là chỉ tối ưu độ chính xác của từng mục độc lập.
- **Ưu và nhược điểm:**
  - *Ưu điểm:* Là cuốn cẩm nang kinh điển, hệ thống hóa chặt chẽ các công thức toán học, thuật toán MIR, quy trình xử lý tín hiệu và các tiêu chí đánh giá chuẩn tắc.
  - *Nhược điểm:* Xuất bản năm 2015 nên chưa cập nhật các bước tiến đột phá gần đây của mạng nơ-ron đồ thị (GNN) và mô hình ngôn ngữ lớn (LLM).

---

### 4. Deldjoo, Schedl, Knees (2021)
**Tên bài báo:** *Content-driven Music Recommendation: Evolution, State of the Art, and Challenges* (arXiv 2021)  
**Tập tin tài liệu:** [Content-driven_Music_Recommendation_Evolution_State_of_the_Art_and_Challenges.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Content-driven_Music_Recommendation_Evolution_State_of_the_Art_and_Challenges.pdf)

- **Phương pháp:**
  - Khảo sát sự tiến hóa của các hệ thống khuyến nghị âm nhạc dựa trên nội dung hiện đại, cấu trúc theo **Mô hình củ hành (Onion Model)** gồm 5 tầng thông tin:
    + *Tầng 1 (Tín hiệu âm thanh):* Từ đặc trưng thủ công (MFCC, spectrograms) đến học biểu diễn sâu (deep audio embeddings qua CNN, VGGish, MusicNN).
    + *Tầng 2 (Dạng biểu diễn ký hiệu):* File MIDI, bản phổ âm nhạc (sheet music).
    + *Tầng 3 (Dữ liệu văn bản):* Lời bài hát (lyrics), thể loại, tags, bài đánh giá phê bình, tiểu sử nghệ sĩ.
    + *Tầng 4 (Dữ liệu thị giác/video):* Ảnh bìa album (album art), video âm nhạc (MV).
    + *Tầng 5 (Ngữ cảnh người dùng):* Tín hiệu sinh lý, cảm xúc, vị trí.
  - Dành riêng một phần trọng tâm khảo sát **các phương pháp dựa trên đồ thị (Graph-based methods)**: xây dựng Đồ thị tri thức (Knowledge Graphs) và Mạng nơ-ron đồ thị (**Graph Neural Networks - GNN**) để học biểu diễn nút kết hợp cấu trúc liên kết và nội dung đa phương thức.
- **Bộ dữ liệu thực nghiệm:**
  - Khảo sát các bộ dữ liệu đa phương thức: Million Song Dataset (MSD), Spotify Million Playlist Dataset (MPD), Free Music Archive (FMA), Jamendo, Last.fm (LFM-1b, HetRec), và Deezer.
- **Kết quả đạt được:**
  - Chứng minh sự trỗi dậy của học sâu (deep learning) đã phá vỡ "trần kính" cũ của các đặc trưng âm thanh truyền thống.
  - Kết luận rằng các mô hình dung hợp đa phương thức (*multimodal fusion*) – đặc biệt là đồ thị kết hợp GNN tích hợp tín hiệu cộng tác lẫn nội dung âm thanh/lời bài hát – luôn đạt hiệu năng vượt trội so với các mô hình đơn phương thức.
- **Ưu và nhược điểm:**
  - *Ưu điểm:* Phân loại cực kỳ chi tiết, hiện đại; là cầu nối lý thuyết xuất sắc giữa lĩnh vực xử lý tín hiệu âm nhạc (MIR), học biểu diễn sâu và hệ thống khuyến nghị.
  - *Nhược điểm:* Việc trích xuất và lưu trữ đặc trưng đa phương thức (audio, video, lyrics) đòi hỏi chi phí tính toán và hạ tầng phần cứng rất lớn, khó khả thi cho các nền tảng vừa và nhỏ.

---

### 5. Lacic et al. (2024)
**Tên bài báo:** *Hybrid music recommendation with graph neural networks* (User Modeling and User-Adapted Interaction - UMAI 2024)  
**Tập tin tài liệu:** [Hybrid_music_recommendation_with_graph_neural_networks.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Hybrid_music_recommendation_with_graph_neural_networks.pdf)

- **Phương pháp:**
  - Đề xuất hệ thống khuyến nghị lai dựa trên mạng nơ-ron đồ thị **PinSage** (Graph Convolutional Neural Networks trên đồ thị quy mô lớn) cho tác vụ gợi ý bài hát liên quan (*Related Song Recommendation*).
  - Thuật toán kết hợp cấu trúc đồ thị tương tác danh sách phát - bài hát (Playlist-Song bipartite graph) thông qua bước ngẫu nhiên cục bộ (Personalized PageRank - PPR) với các đặc trưng nội dung nạp vào nút (node features) trích xuất từ mô hình học sâu âm thanh hiện đại (**L3-Net, VGGish, MusicNN**).
  - So sánh với các nhóm baseline: Lọc cộng tác truyền thống (Item-based CF), Lọc cộng tác đồ thị (PPR, Random Walks), và Phương pháp thuần nội dung (Cosine similarity trên audio embeddings).
- **Bộ dữ liệu thực nghiệm:**
  - Bộ dữ liệu mới được thu thập từ **Spotify**: gồm **10.000 playlists** công khai chứa hơn **277.000 bài hát duy nhất**, đi kèm đoạn trích âm thanh (30s audio previews), lời bài hát và các chỉ số âm thanh của Spotify. Chia tập thực nghiệm theo tỷ lệ 70% huấn luyện - 30% kiểm thử trên các cặp đồng xuất hiện (co-occurrences).
- **Kết quả đạt được:**
  - Mô hình PinSage kết hợp cấu trúc đồ thị với embedding âm thanh (L3-Net hoặc MusicNN) đạt kết quả vượt trội rõ rệt trên các độ đo xếp hạng: **Hit Ratio@K**, **NDCG@K** và **MRR**.
  - Ví dụ: PinSage đạt điểm NDCG@10 và Hit Ratio@10 cao hơn đáng kể so với việc chỉ dùng PPR đơn thuần (chỉ dùng đồ thị) hoặc chỉ dùng VGGish/MusicNN đơn thuần (chỉ dùng âm thanh), chứng minh tính ưu việt của mô hình nơ-ron đồ thị lai trong việc giải bài toán cold-start cho bài hát mới chưa có tương tác.
- **Ưu và nhược điểm:**
  - *Ưu điểm:* Giải quyết đồng thời cả bài toán biểu diễn cấu trúc lẫn bài toán khởi đầu lạnh nhờ tính quy nạp (*inductive learning*) của PinSage; kiểm nghiệm thực tế trên dữ liệu Spotify hiện đại.
  - *Nhược điểm:* Chi phí huấn luyện đồ thị và trích xuất embedding âm thanh sâu rất nặng; đồ thị playlist có thể bị nhiễu do thói quen tạo playlist chủ quan, tùy tiện của người dùng.

---

### 6. Ziaoddini et al. (2025)
**Tên bài báo:** *Socially Aware Music Recommendation: A Multi-Modal Graph Neural Networks for Collaborative Music Consumption and Community-Based Engagement* (arXiv 2025)  
**Tập tin tài liệu:** [Socially_Aware_Music_Recommendation_A_Multi-Modal_Graph_Neural_Networks_for_Collaborative_Music_Consumption_and_Community-Based_Engagement.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Socially_Aware_Music_Recommendation_A_Multi-Modal_Graph_Neural_Networks_for_Collaborative_Music_Consumption_and_Community-Based_Engagement.pdf)

- **Phương pháp:**
  - Đề xuất mô hình **MM-GNN (Multi-Modal Graph Neural Network)** khai thác thông tin xã hội và tương tác đa phương thức trong tiêu thụ âm nhạc.
  - Xây dựng đồ thị thông tin dị thể (*heterogeneous graph*) bao gồm cả tương tác người dùng - bài hát và mạng lưới liên kết xã hội giữa người dùng với nhau (bạn bè, cộng đồng).
  - Tích hợp biểu diễn đa phương thức từ 3 nguồn: đặc trưng âm thanh, lời bài hát (lyrics) và hình ảnh bìa album, kết hợp cơ chế học tương hỗ sâu (*deep mutual learning*) và embedding nhận biết cảm xúc (*emotion-aware embeddings*).
  - Tối ưu hóa bằng hàm mất mát Bayesian Personalized Ranking (BPR) mở rộng trên đồ thị.
- **Bộ dữ liệu thực nghiệm:**
  - Thử nghiệm trên 2 bộ dữ liệu: **MSD-A** (tập con của Million Song Dataset với 25.000 người dùng, 328.821 bài hát, hơn 1,2 triệu tương tác) và bộ dữ liệu **Last.fm** (có đồ thị quan hệ bạn bè xã hội).
- **Kết quả đạt được:**
  - Đánh giá trên các độ đo xếp hạng **Recall@50** và **NDCG@50**:
    + Trên MSD-A: MM-GNN đạt **Recall@50 = 0.075**, **NDCG@50 = 0.043** (vượt trội hoàn toàn so với các baseline: BPR đạt 0.045 / 0.026, VBPR đạt 0.052 / 0.030, NGCF đạt 0.061 / 0.035).
    + Trên Last.fm: MM-GNN đạt **Recall@50 = 0.065**, **NDCG@50 = 0.037** (vượt trội so với NGCF: 0.051 / 0.029, VBPR: 0.043 / 0.024, BPR: 0.038 / 0.021).
  - Cải thiện vượt bậc độ chính xác trong kịch bản người dùng mới và bài hát mới (cold-start).
- **Ưu và nhược điểm:**
  - *Ưu điểm:* Tận dụng tối đa sức mạnh của quan hệ xã hội kết hợp với dữ liệu đa phương thức; khắc phục tốt vấn đề dữ liệu thưa và khởi đầu lạnh.
  - *Nhược điểm:* Kiến trúc mô hình rất phức tạp với nhiều nhánh mạng nơ-ron chạy đồng thời; trong thực tế, đa số nền tảng nghe nhạc trực tuyến không có sẵn mạng xã hội mở giữa người dùng (người dùng thường nghe nhạc cá nhân).

---

### 7. Ferraro et al. (2022)
**Tên bài báo:** *Fairness in Music Recommender Systems: A Stakeholder-Centered Mini Review* (Frontiers in Big Data 2022)  
**Tập tin tài liệu:** [Fairness_in_Music_Recommender_Systems_A_Stakeholder-Centered_Mini_Review.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Fairness_in_Music_Recommender_Systems_A_Stakeholder-Centered_Mini_Review.pdf)

- **Phương pháp:**
  - Tổng quan có hệ thống về vấn đề **Tính công bằng (Fairness)** trong hệ thống khuyến nghị âm nhạc dưới góc nhìn **Đa bên liên quan (Multi-stakeholder perspective)**:
    + *Bên người tiêu dùng (Consumers/Users):* Công bằng nhân khẩu học (giới tính, độ tuổi), công bằng giữa nhóm người dùng thích nhạc chính thống vs. nhạc ngách (mainstream vs. low-mainstream).
    + *Bên nhà cung cấp (Providers/Artists/Labels):* Thiên lệch phổ biến (popularity bias), công bằng về mức độ phơi bày (exposure fairness) cho nghệ sĩ độc lập/ít tên tuổi, thiên lệch giới tính của nghệ sĩ.
    + *Bên nền tảng và xã hội (Platform & Society).*
  - Phân loại các nghiên cứu thành 2 nhóm: Nghiên cứu phân tích hiện trạng (*Observational/Analysis studies*) và Nghiên cứu giải pháp can thiệp/cải thiện (*Mitigation/Improvement studies*).
- **Bộ dữ liệu thực nghiệm:**
  - Khảo sát các bộ dữ liệu thường dùng trong nghiên cứu công bằng: LFM-1b, Last.fm 360K/1K, Million Song Dataset (MSD), Celma's Last.fm, và Spotify playlists.
- **Kết quả đạt được:**
  - Rút ra phát hiện then chốt: **Đại đa số các công trình hiện nay (>80%) chỉ dừng lại ở việc phân tích và chỉ ra hiện trạng bất công** bằng các mô hình và tập dữ liệu sẵn có; rất ít nghiên cứu đề xuất các thuật toán can thiệp hay mô hình cải thiện khả thi.
  - Nhận định thiên lệch giới tính và thiên lệch phổ biến là hai biểu hiện bất công thuật toán phổ biến nhất trong khuyến nghị âm nhạc.
  - Chỉ ra nghiên cứu công bằng đa bên (cân bằng lợi ích giữa người nghe và nghệ sĩ) đang là khoảng trống nghiên cứu cực lớn.
- **Ưu và nhược điểm:**
  - *Ưu điểm:* Cung cấp khung phân loại lý luận chặt chẽ, đa chiều về khái niệm công bằng thuật toán; định vị chuẩn xác khoảng trống nghiên cứu cho cộng đồng.
  - *Nhược điểm:* Là bài báo tổng quan mini-review nên không đề xuất một giải thuật toán học cụ thể để khử thiên lệch; khái niệm công bằng mang tính chuẩn tắc (normative) và ngữ cảnh xã hội, khó đo lường bằng một công thức duy nhất.

---

### 8. Shakespeare et al. (2020)
**Tên bài báo:** *Exploring Artist Gender Bias in Music Recommendation* (2020)  
**Tập tin tài liệu:** [Exploring_Artist_Gender_Bias_in_Music_Recommendation.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/Exploring_Artist_Gender_Bias_in_Music_Recommendation.pdf)

- **Phương pháp:**
  - Nghiên cứu thực nghiệm định lượng về **thiên lệch giới tính của nghệ sĩ (Artist Gender Bias)** trong các thuật toán Lọc cộng tác (CF).
  - Thiết lập mô hình đo lường sự chênh lệch thiên lệch (**Bias Disparity**): so sánh tỷ lệ ưu tiên đầu vào trong lịch sử người dùng (*Input Preference Ratio*) với tỷ lệ đầu ra trong danh sách khuyến nghị (*Output Preference Ratio*) giữa nghệ sĩ nam và nữ.
  - Đánh giá trên 4 thuật toán: Most Popular (không cá nhân hóa), UserItem Avg, UserKNN (k-láng giềng), và NMF (Non-negative Matrix Factorization).
- **Bộ dữ liệu thực nghiệm:**
  - Sử dụng 2 bộ dữ liệu lớn từ Last.fm: **LFM-1b** và **LFM-360K**, được gán nhãn giới tính nghệ sĩ thông qua liên kết định danh với cơ sở dữ liệu MusicBrainz và Wikidata.
- **Kết quả đạt được:**
  - Phát hiện rằng dữ liệu tương tác lịch sử vốn đã có thiên lệch giới tính sẵn có (người dùng nghe khoảng 70-80% nghệ sĩ nam).
  - **Tất cả các thuật toán khuyến nghị được thử nghiệm đều khuếch đại (amplify) thiên lệch này**, làm gia tăng mức độ thiên vị có lợi cho nghệ sĩ nam và giảm sự hiện diện của nghệ sĩ nữ trong danh sách gợi ý so với tỷ lệ lịch sử.
  - Thuật toán *Most Popular* tạo ra mức độ chênh lệch thiên lệch cao nhất. Các thuật toán cá nhân hóa đạt độ chính xác cao (trên LFM-1b, NMF đạt Precision = 0.734, NDCG = 0.880; UserKNN đạt Precision = 0.676, NDCG = 0.793 so với Popularity chỉ đạt Precision = 0.010, NDCG = 0.012) nhưng đều duy trì sự đối xử bất bình đẳng đối với nghệ sĩ nữ trên mọi nhóm nhân khẩu học người dùng.
- **Ưu và nhược điểm:**
  - *Ưu điểm:* Minh chứng thực nghiệm xuất sắc, chặt chẽ với kiểm định giả thuyết thống kê ($p < 0.05$), cung cấp bằng chứng rõ ràng về tác động tiêu cực của thuật toán lọc cộng tác đối với công bằng xã hội.
  - *Nhược điểm:* Giới hạn ở phân loại giới tính nhị phân (nam/nữ), gặp khó khăn khi gán nhãn cho các ban nhạc hỗn hợp giới tính; bài báo mới chỉ đo lường và cảnh báo hiện trạng chứ chưa cài đặt thuật toán tái xếp hạng để khử thiên lệch.

---

### 9. Doh, Choi, Nam (2025)
**Tên bài báo:** *TalkPlay: Multimodal Music Recommendation with Large Language Models* (arXiv 2025)  
**Tập tin tài liệu:** [TalkPlay_Multimodal_Music_Recommendation_with_Large_Language_Models.pdf](file:///c:/Users/Admin/Desktop/musicrec-collaborative-filtering/docs/TLTK/TalkPlay_Multimodal_Music_Recommendation_with_Large_Language_Models.pdf)

- **Phương pháp:**
  - Đề xuất hệ thống **TALKPLAY**, chuyển đổi bài toán khuyến nghị âm nhạc hội thoại thành bài toán **dự đoán token kế tiếp (next-token prediction)** thông qua Mô hình ngôn ngữ lớn (LLM).
  - Thiết kế bộ mã hóa âm nhạc đa phương thức (**Multimodal Music Tokenizer**): lượng tử hóa các biểu diễn âm nhạc không đồng nhất – bao gồm vector đặc trưng âm thanh (CLAP, MERT), lời bài hát, siêu dữ liệu nghệ sĩ/album, thẻ ngữ nghĩa (tags) và mẫu đồng xuất hiện trong danh sách phát – thành các token âm nhạc rời rạc trong cùng không gian từ vựng của LLM.
  - Tinh chỉnh mô hình nền tảng ngôn ngữ (LLaMA-based) để vừa trò chuyện, giải thích lý do, vừa trực tiếp sinh ra mã định danh bài hát được gợi ý theo ngữ cảnh hội thoại tự nhiên của người dùng.
- **Bộ dữ liệu thực nghiệm:**
  - Bộ dữ liệu hội thoại âm nhạc đa phương thức quy mô lớn tổng hợp từ: Million Song Dataset (MSD), Spotify playlists, MusicCaps, Song Describer, cùng tập dữ liệu hội thoại đa lượt (*multi-turn dialogues*) tự động sinh.
- **Kết quả đạt được:**
  - TALKPLAY vượt trội rõ rệt so với cả các baseline zero-shot (BM25, CLAP, NV-Embed-V2) và các mô hình học sâu được tinh chỉnh chuyên biệt trên các độ đo xếp hạng.
  - Đạt **MRR = 0.049** (vượt mốc 0.032 của mô hình tốt nhì NV-Embed-V2) và đặc biệt đạt **Hit@1 = 0.026** (cao gấp hơn **5 lần** so với mô hình tốt kế tiếp là 0.005), chứng minh khả năng dự đoán chính xác tuyệt đối bài hát người dùng muốn nghe ngay ở vị trí đầu tiên.
  - Thực nghiệm phân rã (*ablation study*) khẳng định việc hợp nhất âm thanh, siêu dữ liệu văn bản và đồ thị playlist mang lại hiệu năng cao nhất so với việc chỉ dùng đơn lẻ một loại đặc trưng.
- **Ưu và nhược điểm:**
  - *Ưu điểm:* Mang lại trải nghiệm khuyến nghị hội thoại trực quan, tự nhiên; người dùng có thể yêu cầu bằng ngôn ngữ phức tạp (ví dụ: *"hãy gợi ý một bài indie buồn có tiếng guitar mộc phù hợp nghe lúc trời mưa ban đêm"*); thống nhất bài toán hiểu ngữ nghĩa, truy hồi và sinh lời giải thích trong một mô hình duy nhất.
  - *Nhược điểm:* Độ trễ suy luận (inference latency) rất cao (tính bằng giây thay vì vài phần nghìn giây như SVD/Item-CF); tiêu tốn tài nguyên GPU khổng lồ; tiềm ẩn rủi ro sinh ảo giác (hallucination) về thông tin âm nhạc nếu không có cơ chế ràng buộc chặt chẽ.

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
