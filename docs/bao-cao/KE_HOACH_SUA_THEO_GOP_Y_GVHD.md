# Kế hoạch sửa báo cáo theo góp ý GVHD ngày 06/11/2026

Trạng thái: **bản đề xuất, chờ nhóm duyệt**. Chưa sửa báo cáo, chưa sửa mã, chưa chạy thực nghiệm mới.

Nguồn: [tóm tắt góp ý](GOP_Y_GVHD_06-11-2026.md) (mã G01–G32 trỏ tới từng ý chữ đỏ), [bản gốc của GVHD](GopY_GVHD_06-11-2026_KLTN_TrongNguyen_GiaKhang.docx), [đối chiếu mục tiêu](../results/doi_chieu_muc_tieu.md), [kết quả test chính thức](../results/chuong_4_test.md), [kết quả M2](../results/chuong_4_m2.md), [H1 vòng 1](../results/h1_vong_1.md), [backend](../results/chuong_5_backend.md), [frontend](../results/chuong_5_frontend.md). Mọi việc viết báo cáo theo [quy tắc viết báo cáo](QUY_TAC_VIET_BAO_CAO.md).

## 1. Nhận định chung

GVHD viết sẵn khung Chương 4 với giả định nhóm chưa có kết quả. Thực tế nhóm đã có lần chạy chính thức `chinh_thuc_cloud_20261026`: tập test đã mở đúng một lần sau khi khóa cấu hình trong `lock.json`, có bảng K = 5, 10, 20 cho tám mô hình, có Wilcoxon, Holm và bootstrap cho bốn cặp khai báo trước. Vì vậy:

- **Không chạy lại đánh giá test để chọn mô hình.** Việc “chạy lại toàn bộ đánh giá trên tập kiểm thử” trong lộ trình của GVHD đã xong. Phần nhóm cần làm là điền số đã có vào khung của GVHD, rồi tính thêm các phân tích GVHD yêu cầu từ danh sách gợi ý và kết quả từng người dùng đã lưu.
- Phân tích nào chấm thêm trên test sau khi đã mở test (ví dụ các biến thể ablation của M1, các cặp kiểm định ngoài bốn cặp khai báo trước) phải ghi rõ là **phân tích bổ sung**, không dùng để chọn cấu hình.
- Một số số liệu chữ xanh của GVHD lệch nhẹ so với tệp kết quả và phải sửa theo tệp (mục 3).

Phần lớn việc còn lại là viết báo cáo. Phần tính toán mới đều nhẹ: đọc lại kết quả đã lưu, huấn luyện lại một cấu hình SVD trên validation để ghi đường học, đo lại độ trễ, chụp ảnh giao diện. Không cần đưa thực nghiệm lên server.

## 2. Các quyết định cần nhóm chốt

| # | Câu hỏi | Đề xuất | Lý do |
| --- | --- | --- | --- |
| Q-A | Dùng khung Chương 4 của GVHD (4.1–4.12) thay khung v16 (4.1–4.11)? | **Dùng khung GVHD**, chuyển số liệu và bảng đã có của v16 vào. | GVHD đã viết sẵn và sẽ chấm theo khung này. Khung v16 có nhiều mục mô tả thiết kế lặp lại Chương 3. |
| Q-B | Đưa ALS vào bảng so sánh chính (G12, G16)? Quyết định trước đây (Q3) là để ALS ở mục riêng. | **Đưa vào Bảng 4.5, tách bằng dòng kẻ, ghi “mở rộng”.** Giữ mục 4.9 riêng để phân tích. | GVHD yêu cầu rõ. ALS đã đi qua cùng giao thức và cùng `lock.json`, nên đưa vào bảng không làm sai quy trình. |
| Q-C | Mô hình nền của M1 và của ứng dụng: giữ PureSVD hay chuyển sang ALS (G16)? ALS hơn PureSVD 0,034673 NDCG@10, p Holm 3,36e−25. | **Giữ PureSVD, giải thích lý do** trong 4.9 và 4.11: M1 được thiết kế, tinh chỉnh và khóa trên PureSVD trước khi mở test. Nêu chuyển M1 sang ALS là hướng phát triển. Ứng dụng vẫn cho chọn ALS như hiện nay. | Chạy lại M1 trên ALS sau khi đã xem test là chọn hậu kiểm. Kết quả H1 vòng 1 (phạt phổ biến trực tiếp trên ALS, chỉ có validation) có thể dẫn làm bằng chứng gợi ý, ghi rõ chưa có test. |
| Q-D | Đưa H1 vào báo cáo? | **Một đoạn ngắn trong 4.9** (hoặc 5.9) ghi là hướng đã thử, chỉ có validation, không qua cổng. | Kết quả âm có giá trị và liên quan trực tiếp tới câu hỏi Q-C. Không đủ để thành mục riêng. |
| Q-E | Mã thí nghiệm: theo bảng GVHD (E1 tinh chỉnh, E2 so sánh, E3 nhóm lịch sử, E4 M1, E5 ALS, E6 M2) thay mã v16 (E0–E3 so sánh, E4 M1, E5 nhóm lịch sử, E6 M2)? | **Theo bảng GVHD** (G10). E4 và E6 giữ nguyên. Ghi bảng đổi mã trong `docs/results/` để tra ngược. | GVHD đã giữ E4, E6 và đề nghị sửa phần còn lại cho khớp. |
| Q-F | Phụ lục C (ma trận truy vết, kế hoạch, mẫu nhật ký): cập nhật hay bỏ (G32)? | **Bỏ Phụ lục C**. Chuyển những gì còn giá trị (liên hệ yêu cầu và đánh giá) vào Bảng 5.5. | GVHD gọi đây là tài liệu làm việc. Bỏ cũng tránh mâu thuẫn với Chương 3. |
| Q-G | Mục 5.5 Đối chiếu mã nguồn với đề cương V2 (G27). | **Xóa**, đánh số lại 5.6–5.9 thành 5.5–5.8. | GVHD đề nghị rõ. |
| Q-H | Chương 5: giao diện chính là Next.js hay Streamlit? GVHD viết theo Streamlit. | **Next.js là giao diện chính, Streamlit là bản dự phòng**, viết theo mã thật. | Đúng phiên bản đã bàn giao. GVHD cho phép chỉnh theo mã thật (G21). |
| Q-I | Bảng 5.1–5.3 của GVHD có chức năng chưa cài (`GET /models`, `model_version`, `use_m1`, báo số mã nghệ sĩ bị bỏ qua, nạp lại gói). Thêm mã hay ghi hạn chế? | **Viết theo API thật, ghi chức năng chưa có vào Hạn chế.** Chỉ thêm mã khi ca kiểm thử cho thấy lỗi thật. | Tránh mở rộng phạm vi vào cuối kỳ. Danh sách đối chiếu ở mục 4.3. |
| Q-J | Hạn nộp. GVHD giả định 30/11/2026. | Xác nhận với GVHD hoặc khoa. Lịch ở mục 6 dùng giả định này. | Các mốc gửi GVHD (17/11, 23/11, 27/11) phụ thuộc hạn nộp. |
| Q-K | Bảng 4.6 GVHD muốn so mô hình tốt nhất với từng mô hình còn lại. Lock chỉ khai báo bốn cặp. | **Giữ bốn cặp khai báo trước làm kiểm định chính.** Thêm các cặp còn lại trong một họ Holm riêng, ghi “bổ sung”. | Giữ đúng quy trình đã cam kết trước khi mở test, vẫn đáp ứng yêu cầu của GVHD. |

## 3. Số liệu chữ xanh cần sửa theo tệp kết quả

Đã kiểm tra nhanh một số con số GVHD viết sẵn. Danh sách đầy đủ sẽ rà ở bước A1.

| Vị trí | GVHD viết | Tệp kết quả | Nguồn |
| --- | --- | --- | --- |
| 4.2, 4.6 | 1.829 người có đúng 40 tương tác huấn luyện, chỉ 48 người có lịch sử ngắn hơn | Trên train: 1.831 người có đúng 40, 44 người dưới 40, 2 người trên 40. Trên test (1.855 người có đích hợp lệ): 37 / 1.816 / 2. Con số 1.829 là số người có đúng 50 nghệ sĩ trong dữ liệu gốc (1.829/1.892). | `outputs/chinh_thuc_cloud_20261026/chuong_3/run/split/train.parquet`; [history_groups.csv](../results/chinh_thuc_cloud_20261026/test/history_groups.csv); [data-card.md](../data-card.md) |
| Bảng 4.7 | Hai nhóm “Dưới 40” và “Đúng 40” | Có thêm nhóm “Trên 40” (2 người). Đề xuất gộp vào bảng với ghi chú hoặc nêu trong lời văn. | như trên |
| 4.4, 4.9 | ALS vòng tốt nhất là 16 | Khớp ở seed 42. Seed 43 có best_epoch 32. | `chuong_4/tuning/implicit_als/.../metrics.json`; [tuning_summary.json](../results/chinh_thuc_cloud_20261026/tuning_summary.json) |
| 4.4 | SVD chọn vòng 2 | Khớp (seed 42 và 43). | như trên |
| 4.1.1 | Máy cá nhân | Lần chạy chính thức chạy trên máy đám mây (Xeon 2,10 GHz, 4 luồng). Độ trễ demo đo trên máy cục bộ (i5-11300H). Phải ghi rõ lần chạy nào ở đâu (G07). | [environment.json](../results/chinh_thuc_cloud_20261026/environment.json); [latency.json](../results/chuong_5/latency.json) |
| 4.1.2 | Số lần bootstrap, mức ý nghĩa | Bootstrap phân vị 1.000 lần theo người dùng, seed 42; α = 0,05; Wilcoxon và Holm từ SciPy. Cần đối chiếu câu chữ (G08). | [statistics_ndcg_at_10.json](../results/chinh_thuc_cloud_20261026/test/statistics_ndcg_at_10.json) |

## 4. Kế hoạch theo từng góp ý

Ký hiệu trạng thái dữ liệu: **Có** (đã có số trong tệp kết quả), **Tính thêm** (tính từ kết quả đã lưu, không huấn luyện lại), **Chạy mới** (cần chạy mã), **Viết** (chỉ viết hoặc tra nguồn).

### 4.1 Chương 1–3 và tài liệu tham khảo

| Ý | Việc | Dữ liệu | Ghi chú |
| --- | --- | --- | --- |
| G01 | Mở nguồn [1] IFPI và [4] Spotify, đối chiếu 69,6%, 837 triệu, 56 triệu, 77%, ghi đúng năm số liệu. | Viết | Cần truy cập web. Nếu không khớp thì sửa số hoặc bỏ. |
| G02 | Viết lại câu về phân nhóm theo độ dài lịch sử theo câu GVHD gợi ý, trỏ tới 4.8 Given-N. | Viết | |
| G03 | Sửa RQ2 thành câu hỏi Given-N (N = 0, 1, 3, 5), bằng chứng E6. | Viết | Đồng bộ Bảng 1.1, 4.2, 4.11, 5.5. |
| G04 | Đổi số 1.6 Phương pháp thực hiện, 1.7 Cấu trúc báo cáo; thêm một câu về Wilcoxon, Holm, bootstrap. Sửa câu về EDA nếu Chương 1 nói EDA thuộc Chương 4 (G09). | Viết | Cập nhật Mục lục. |
| G05 | Chương 2: thêm đoạn implicit ALS [8]; thêm mục “Các nghiên cứu liên quan” (5–6 công trình dùng Last.fm HetRec 2011, kèm giao thức và chỉ số); nêu M1 kế thừa gì từ MMR [18] và Abdollahpouri [19]. | Viết | Mục nghiên cứu liên quan cần tra bài gốc, có thể dùng [9], [24], [25] và [khảo sát hướng mới](../tai-lieu-tham-khao/khao-sat-huong-moi/KHAO_SAT_HUONG_MOI_2021_2025.md) đã có. Việc tra cứu nhiều nhất trong phần viết. |
| G06 | 3.7.3: thêm câu trỏ tới lưu ý tính vòng tròn ở 4.7. | Viết | |
| — | 3.6.4: thay “data card, Bước 13” bằng tham chiếu Bảng 4.3/4.4; giữ cụm chữ xanh “(chi tiết ở Bảng 4.4)”. | Viết | Lỗi hình thức trong nhận xét tổng quát. |
| — | Kiểm tra câu chữ readme của HetRec về giới hạn nghệ sĩ nghe nhiều nhất và trích dẫn [7]. | Viết | Readme có sẵn trong `data/raw/hetrec2011/readme.txt`. |
| G31 | Tài liệu tham khảo: thêm SciPy, FastAPI, Streamlit, Next.js, pandas, scikit-learn nếu nhắc; thêm nguồn cho LFM-1K, LFM-2b, BPR, EASE, LightGCN nếu giữ ở 5.9; [27]–[29] được trích ở 4.1.2; rà hai chiều mọi tài liệu. | Viết | Giữ hệ `[n]` theo thứ tự hiện hành (quy tắc mục 4). |

### 4.2 Chương 4

Kết quả tính thêm lưu vào `outputs/chinh_thuc_cloud_20261026/chuong_4_bo_sung/`, bản sao nhỏ vào `docs/results/chinh_thuc_cloud_20261026/bo_sung/`, tổng hợp trong `docs/results/chuong_4_bo_sung.md`. Hình xuất PNG 300 dpi kèm CSV dữ liệu vẽ.

| Ý | Mục | Việc | Dữ liệu |
| --- | --- | --- | --- |
| A1 | Toàn chương | Rà mọi con số chữ xanh với tệp kết quả, sửa các điểm ở mục 3. | Có |
| G07 | 4.1.1 | Điền môi trường từ `environment.json`; ghi lần chạy chính thức trên máy đám mây, demo và đo độ trễ trên máy cục bộ. | Có |
| G08 | 4.1.2 | Đối chiếu câu chữ với `scripts/test_statistics.py` (1.000 lần bootstrap, α = 0,05). | Có |
| G09 | 4.2 | Bảng 4.1 khớp Chương 3 (đã có). **Hình 4.1** phân bố số người nghe của nghệ sĩ trên train (trục log); **Hình 4.2** phân bố tổng lượt nghe theo người dùng. | Tính thêm |
| G10 | 4.3 | Bảng 4.2 theo mã E1–E6 của GVHD (Q-E). | Viết |
| G11 | 4.4 | Bảng 4.3 đủ lưới tham số và NDCG@10 xác thực tốt nhất (UserCF 12, ItemCF 12, SVD 12, PureSVD 4, ALS 8 cấu hình). **Hình 4.3** NDCG@10 xác thực và RMSE theo vòng của SVD (hai trục tung). Có thể thêm NDCG@10 theo L và theo k. | Có (lưới, trong `tuning_summary.json` và thư mục tuning). Hình 4.3 là **Chạy mới**: huấn luyện lại cấu hình SVD đã chọn trên validation, ghi NDCG@10 và RMSE từng vòng tới 100 vòng, khoảng 1–2 phút. Thư mục tuning của SVD, UserCF, ItemCF chưa có trên máy cục bộ, cần lấy từ gói `chinh_thuc_cloud_20261026.zip` của project hoặc chạy lại. |
| G12 | 4.5 | Bảng 4.5 (K = 10, có ALS tách dòng), bảng K = 5, 20 xuống phụ lục. Bảng 4.6 khoảng tin cậy và p Holm (Q-K). Viết phân tích khoảng 1 trang theo năm ý GVHD, trả lời RQ1. | Có; cặp bổ sung là Tính thêm |
| G13 | 4.6 | Bảng 4.7 nhóm lịch sử (37 / 1.816 / 2), chỉ mô tả. **Hình 4.4** boxplot NDCG@10 theo người dùng. **Hình 4.5** phân bố hiệu NDCG@10 giữa PureSVD và Popularity (tỷ lệ tăng, bằng, giảm). Phân nhóm ba mức “ưa chuộng nghệ sĩ phổ biến” theo phân vị như Kowald và cộng sự [9]. | Tính thêm từ `evaluation.json` từng người dùng |
| G14 | 4.7 | Bảng 4.8 bốn biến thể M1 trên test (nền, chỉ đa dạng, chỉ phạt phổ biến, đầy đủ) thêm cột **ILD theo thẻ** (côsin TF-IDF thẻ của M2, chỉ cặp đều có thẻ, ghi số danh sách đóng góp). **Hình 4.6** NDCG@10 theo ARP cho 12 điểm λ × β trên validation, đánh dấu điểm chọn và ngưỡng giảm 5%. Wilcoxon nền và M1 (đã có, p Holm 0,608). Hai đến ba ví dụ danh sách trước và sau M1. Trả lời RQ3 bằng % giảm ARP và % đổi NDCG@10. | Bảng 12 điểm validation: Có (`m1_metrics.csv`). Biến thể trên test và ILD theo thẻ: Tính thêm, ghi “bổ sung”. |
| G15 | 4.8 | Bảng 4.9 Given-N (có). Bảng 4.10 tần suất đường xử lý của M2 theo N. Khoảng tin cậy bootstrap M2 so Popularity ở N = 1, 3, 5. **Hình 4.7** NDCG@10 theo N. Kiểm tra N = 0 cho M2 trùng Popularity (đã có). Trả lời RQ4 (kết quả âm) và phần RQ2. | Bảng 4.9: Có. Bảng 4.10, CI cho N = 1, 5: Tính thêm (cần kiểm tra M2 đã ghi đường xử lý hay phải chạy lại phần dự đoán của M2 trên test với cấu hình đã khóa). |
| G16 | 4.9 | Viết ALS so PureSVD theo Q-C, kèm đoạn H1 theo Q-D. | Có |
| — | 4.10 | Bảng 4.11 chi phí (đã có trong `cost.csv`, đo trên máy đám mây, một luồng BLAS). Đổi kích thước sang MB. | Có |
| G17 | 4.11 | Thảo luận 1–1,5 trang: trả lời RQ1–RQ4, đối chiếu công trình cùng dữ liệu (phụ thuộc G05), giới hạn, lý do chọn mô hình cho Chương 5. | Viết |
| G18 | 4.12 | Kết luận chương bằng số thật, viết trung thực M2 không vượt Popularity. | Có |
| — | Phụ lục | Bảng K = 5, 20; bảng ba seed. | Có |

### 4.3 Chương 5

Bằng chứng mới lưu trong `outputs/demo/` và `docs/results/chuong_5/`, tổng hợp vào `docs/results/chuong_5.md` (gộp `chuong_5_backend.md` và `chuong_5_frontend.md`).

| Ý | Mục | Việc | Dữ liệu |
| --- | --- | --- | --- |
| G19 | 5.1.1 | Hình 5.1 cây thư mục thật, tên mô-đun theo mã. | Viết |
| G20 | 5.1.2 | Bảng tệp trong gói `demo-chinh-thuc-20261026`, dung lượng, thời gian nạp gói lần đầu. | Dung lượng: Có (`release_manifest.json`). Thời gian nạp: Chạy mới, vài giây. |
| G21 | 5.2.1 | Bảng 5.1 theo API thật: `GET /health`, `GET /users`, `GET /users/{id}/history`, `GET /artists`, `POST /recommend`. Bỏ `/models`, `/artists/search`. | Có |
| G22 | 5.2.2 | Ví dụ JSON chạy thật, đúng tên trường; ảnh trang `/docs` làm Hình 5.2. | Chạy mới |
| G23 | 5.2.3 | Bảng 5.2 theo hành vi thật. Đối chiếu tám trường hợp của GVHD: user không tồn tại → 404 (có); hồ sơ rỗng → Popularity, `fallback_used = true` (có); K sai, lượt nghe sai → kiểm tra mã 422; mã nghệ sĩ ngoài danh mục, nghệ sĩ trùng, gói chưa sẵn sàng → kiểm tra; `model_version` → không có, bỏ dòng. Trường hợp chưa xử lý ghi vào Hạn chế (Q-I). | Chạy mới (kiểm tra), có thể kèm sửa mã nhỏ nếu duyệt |
| G24 | 5.3 | Viết luồng sử dụng Next.js (5 trang) và Streamlit dự phòng. Hình 5.3 chọn người dùng có sẵn, 5.4 tự nhập lịch sử, 5.5 có M1 và không M1 cùng người dùng, 5.6 lịch sử rỗng có thông báo dự phòng. Ghi thời gian chờ thật của lời gọi API. | Chạy mới (chụp ảnh) |
| G25 | 5.4.1 | Bảng 5.3: ánh xạ T01–T10 sang các ca trong `tests/contract/test_api.py` (đang có 7 hàm kiểm thử), bổ sung ca còn thiếu (T05 K lớn hơn số ứng viên, T07 bật tắt M1, T09 tất định, T10 khởi động lại) rồi chạy, ghi Đạt/Không đạt. | Chạy mới (thêm kiểm thử, cần duyệt sửa mã) |
| G26 | 5.4.2 | Đã có đối chiếu cấp chỉ số (0 dòng lệch trên 21 dòng). Thêm đối chiếu **cấp danh sách** theo ba chỉ tiêu của GVHD (trùng hoàn toàn cả thứ tự, Jaccard trung bình, chênh điểm lớn nhất) cho toàn bộ người dùng test, trả lời RQ5. | Chạy mới, dưới 1 phút |
| — | 5.4.3 | Đo lại theo cách GVHD mô tả: 20 lượt khởi động, 200 lượt đo, trung bình, trung vị, độ lệch chuẩn, P95, cho bốn cấu hình của Bảng 5.4, ghi cấu hình máy. Hiện có 50 lượt, trung vị và p95. | Chạy mới, vài phút |
| G27 | 5.5 | Xóa mục, đánh số lại (Q-G). | Viết |
| G28 | 5.6 | Bảng 5.5 mức đạt theo [đối chiếu mục tiêu](../results/doi_chieu_muc_tieu.md): mục tiêu 1, 2, 4 Đạt; 3 Đạt một phần (M2 không đạt giả thuyết); 5 Đạt một phần (chưa triển khai lên host). Đổi “giao diện Streamlit” trong mục tiêu 5 cho khớp Q-H. | Có |
| G29 | 5.7 | Kết luận bằng số thật của Chương 4, 5. | Có |
| — | 5.8 | Hạn chế: thêm các điểm GVHD nêu, M2 không vượt Popularity, chức năng API chưa có (Q-I), chưa triển khai lên host. | Viết |
| G30 | 5.9 | Kiểm tra tên LFM-1K, LFM-2b, BPR, EASE, LightGCN và thêm tài liệu; thêm hướng M1 trên ALS (Q-C). | Viết |

### 4.4 Phụ lục và phần đầu

| Ý | Việc |
| --- | --- |
| G32 | Bỏ Phụ lục C (Q-F), sửa các chỗ dẫn tới C trong thân bài. |
| — | Cập nhật Tóm tắt và Abstract theo kết quả chính, đồng bộ hai bản. |
| — | Danh mục bảng, hình, chữ viết tắt; làm mới mục lục và các trường Word. |
| — | Xóa toàn bộ chữ đỏ, chuyển chữ xanh về đen sau khi điền. |

## 5. Trình tự thực hiện

Mỗi giai đoạn dừng chờ duyệt theo quy tắc dự án. Làm tuần tự, không chạy song song nhiều luồng sửa mã.

1. **Giai đoạn 0 – Chốt quyết định.** Nhóm trả lời Q-A đến Q-K.
2. **Giai đoạn 1 – Bổ sung số liệu Chương 4.** Viết script đọc kết quả đã lưu (A1, G09, G11, G13, G14, G15), chạy lại một cấu hình SVD trên validation cho Hình 4.3. Chạy ruff, mypy, pytest. Viết `docs/results/chuong_4_bo_sung.md`. **Dừng chờ duyệt.**
3. **Giai đoạn 2 – Bằng chứng Chương 5.** Bổ sung kiểm thử API (G25), đối chiếu cấp danh sách (G26), đo độ trễ (5.4.3), đo thời gian nạp gói (G20), chụp ảnh giao diện (G22, G24). Chạy ruff, mypy, pytest. Viết `docs/results/chuong_5.md`. **Dừng chờ duyệt.**
4. **Giai đoạn 3 – Tra nguồn.** G01, readme [7], G05 (nghiên cứu liên quan), G30, G31. Lưu ghi chú nguồn trong `docs/bao-cao/`.
5. **Giai đoạn 4 – Viết báo cáo v17.** Lấy bản GVHD làm khung cho Chương 4, 5 và v16 làm gốc cho phần còn lại, theo [quy tắc viết báo cáo](QUY_TAC_VIET_BAO_CAO.md). Có thể gửi GVHD từng chương theo mốc. Thêm dòng v17 vào [README](README.md). **Dừng chờ duyệt.**
6. Commit gom một lượt sau mỗi giai đoạn được duyệt, trên nhánh `research/data-preparation-model-survey`. Không push khi chưa được bảo.

## 6. Lịch dự kiến

Theo mốc của GVHD, giả định hạn nộp 30/11/2026 (Q-J). Thời gian là ước lượng công việc, sẽ báo lại sau khi thử trên mẫu nhỏ.

| Thời gian | Giai đoạn | Mốc |
| --- | --- | --- |
| 07/11 | Giai đoạn 0 | Nhóm chốt Q-A đến Q-K |
| 07/11–11/11 | Giai đoạn 1 | Duyệt số liệu bổ sung Chương 4 |
| 11/11–14/11 | Viết Chương 4 (v17 nháp), song song tra nguồn G05 | 17/11 gửi GVHD Chương 4 |
| 13/11–19/11 | Giai đoạn 2 | Duyệt bằng chứng Chương 5 |
| 19/11–22/11 | Viết Chương 5 | 23/11 gửi GVHD Chương 5 |
| 24/11–27/11 | Chương 1–3, 4.11, 5.5–5.8, Tóm tắt, Abstract, tài liệu, định dạng | 27/11 gửi bản hoàn chỉnh |
| 28/11–30/11 | Sửa theo góp ý cuối | Nộp |

## 7. Rủi ro

- **Thư mục tuning của SVD, UserCF, ItemCF chưa có trên máy cục bộ.** Cần cho Bảng 4.3 đầy đủ và Hình 4.3. Cách xử lý: lấy từ gói `chinh_thuc_cloud_20261026.zip` của project, hoặc chạy lại tinh chỉnh trên validation (khoảng 43 phút cho toàn bộ lưới trên máy đám mây; sẽ thử mẫu nhỏ và báo ước tính trước).
- **M2 có thể chưa ghi đường xử lý từng yêu cầu.** Nếu chưa, cần chạy lại phần dự đoán của M2 với cấu hình đã khóa để đếm, không đổi kết quả chỉ số.
- **Nguồn IFPI, Spotify có thể đã đổi trang.** Nếu không xác minh được, bỏ số liệu khỏi Chương 1.
- **Chụp ảnh giao diện cần frontend và backend chạy cùng lúc trên máy cục bộ.**
