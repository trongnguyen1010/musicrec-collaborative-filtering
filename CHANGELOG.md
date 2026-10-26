# Changelog

Mọi thay đổi đáng chú ý của MusicRec được ghi trong file này theo
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) và Semantic Versioning.

## [Unreleased]

### Changed

- 2026-10-26: Hoàn thành lượt implicit ALS đầu tiên sau Bước 14, đúng một
  cấu hình/seed 42: 32 factors, reg 0.1, c=1+ln(1+raw count), alpha thư viện 1,
  implicit CPU 0.7.3/native CG3/float32/một luồng. Chọn NDCG@10 mỗi vòng,
  tốt nhất vòng 18/dừng 23; 0.1974107044 cao hơn PureSVD nhị phân 26,1997%,
  coverage 4,9682%, ARP giảm/ILD giảm nhẹ. Fit+monitor 176,550137 giây,
  OS peak working set cả tiến trình 178 MiB, model 2.556.337 byte.
  Thêm model/config/CLI, extra als và CI kiểm thử; 73 tests/lint/format/mypy đạt,
  kiểm toán confidence/loss/checkpoint/danh sách/metric độc lập khớp, load không fit.
  Theo yêu cầu mới, đối chiếu nghiên cứu 2022–2026 và ghi rõ preprint/protocol;
  không lấy “accuracy 96%” của bài MICE 2025 làm NDCG held-out.
  Đề xuất xác nhận seed 43/44 trước tuning/đổi nền M1, chưa thực hiện.
  Giữ mọi run cũ/Word và lịch chính; chưa test hoặc BPR/SLIM/M1/M2.

- 2026-10-26: Hoàn thành Bước 14 tổng hợp validation của tám cấu hình thuộc
  sáu họ baseline, kiểm hash/protocol/cohort trên 14 run và phân tích chi phí,
  lịch sử train <40/=40/>40 (41/1.822/2 user hợp lệ). Thêm CLI tổng hợp và
  config cố định, helper nhóm/seed, --model-seed 42/43/44 cho Random/SVD/PureSVD.
  Chạy đúng sáu fit xác nhận seed, không tuning: NDCG@10 mean ± sample std
  PureSVD nhị phân 0.1564272628 ± 0, SVD 0.0576259192 ± 0.0010411842,
  Random 0.0004124977 ± 0.0001408550; Popularity vẫn vượt SVD cả ba seed.
  Giữ kết quả không cải thiện, các cấu hình cũ/11 Word và chưa mở test.
  69 tests/lint/format/mypy đạt. PureSVD nhị phân là ứng viên M1 trong phạm vi
  chưa tuning; chỉ đánh giá điều kiện đề xuất ALS riêng, chưa triển khai mở rộng
  hoặc khóa nền M1. Run/model giữ cục bộ, tài liệu hiện có được đồng bộ.

- 2026-10-26: Hoàn thành Bước 13 so PureSVD nhị phân/log/proxy tại cùng
  32 chiều/seed 42/split/catalog/evaluator. NDCG@10 tương ứng
  0.1564272628/0.1545766607/0.1516922327; nhị phân tăng 3,1215% tương đối
  so proxy nhưng ARP cao hơn/ILD thấp hơn, log phủ nhiều artist Top-10 hơn.
  Thêm hai config và lựa chọn biểu diễn trong model/runner, giữ contract proxy
  1–5 và artifact proxy tương thích. Đối chiếu biểu diễn train trước fit,
  kiểm chứng độc lập bằng eigh toàn danh sách/score/metric, nạp lại và lặp
  mỗi biểu diễn mới 9 tệp trùng hash; proxy cũng khớp 9 tệp Bước 12.
  67 tests/lint/format/mypy đạt; 113 tệp đầu ra cũ/11 Word giữ nguyên.
  Run/model giữ cục bộ, cập nhật tài liệu hiện có; chưa tuning, chốt nền M1,
  tổng hợp Bước 14 hoặc mở test.

- 2026-10-26: Hoàn thành Bước 12 PureSVD 32 chiều trên proxy train/seed 42,
  zero-fill không centering/bias, score R V32 V32.T bằng svds/ARPACK thưa.
  Không SGD/dừng sớm/RMSE; cold-start zero profile có reason riêng. NDCG@10
  0.1516922327 cao hơn các cấu hình đầu đã chạy, Coverage@10 362 artist (2.3510%),
  ARP 143.9862/ILD 0.8189; chưa chốt mô hình cuối. Kiểm tra độc lập qua dense
  Gram user–user/eigh, 32 singular values/không gian chiếu và đủ 1.877 danh sách,
  nạp lại không fit/phân rã; 9 tệp chạy lại trùng hash. 63 tests/lint/format/mypy
  đạt; giữ mọi run cũ/Word, chưa tuning/so sánh biểu diễn hoặc mở test.

- 2026-10-26: Hoàn thành Bước 11 SVD có độ lệch: 32 factors, lr=0.005,
  reg=0.02, seed=42; SGD chỉ trên proxy train quan sát với global mean/bias,
  cập nhật đồng thời factors và L2 theo quan sát. Chọn epoch bằng NDCG@10
  validation mỗi epoch, patience=5, dừng 6/100 epoch và khôi phục epoch 1.
  NDCG@10 0.0564899628 chưa vượt Popularity, Coverage@10 82 artist (0.5325%),
  RMSE proxy bổ sung 1.2439097807. Tái hiện độc lập cả 445.650 cập nhật và metric,
  nạp lại không fit khớp 1.877 danh sách; 10 tệp chạy lại trùng hash, có đường học.
  59 tests/lint/format/mypy đạt. Chưa tuning, PureSVD, M1/M2 hoặc mở test;
  giữ mọi run cũ/Word và cập nhật tài liệu làm việc, dừng trước Bước 12.

- 2026-10-26: Hoàn thành Bước 10 ItemCF L=40/shrinkage=0 trên validation:
  cosine toàn cột proxy train, top-L theo artist đích rồi giao lịch sử user,
  trung bình điểm có trọng số và mean fallback có reason. Tính từng khối 256
  artist, lưu CSR/model và nạp lại không fit. NDCG@10 0.0074299548 thấp hơn
  UserCF đầu/Popularity, Coverage@10 22.5029225% gồm 1.217 vị trí fallback;
  RMSE proxy bổ sung 0.9796199383. Kiểm tra độc lập toàn 15.398 bộ láng giềng,
  1.877 danh sách và metric, chín tệp chạy lại trùng hash. 53 tests đạt;
  sửa lỗi style/import/type sẵn có và bỏ môi trường legacy khỏi quét lint để
  ruff/format/mypy toàn dự án đạt. Chưa tuning, MF/PureSVD hoặc mở test;
  giữ run cũ và mọi Word. Đồng bộ tài liệu làm việc, chưa chuyển Bước 11.

- 2026-10-25: Hoàn thành Bước 9 UserCF một cấu hình L=40/shrinkage=0, cosine
  toàn vector proxy train, láng giềng toàn user rồi giao người nghe từng item,
  dự đoán trừ mean quan sát và mean fallback rõ ràng. Thêm proxy_score tùy chọn
  trong Interaction, giữ count gốc riêng. Kiểm tra tay, sửa nhiễu số thực khi
  hòa điểm bằng khóa sắp 12 chữ số; bản run đầu giữ audit, run chốt có hậu tố
  checked. NDCG@10 0.0080787555 thấp hơn Popularity tại cấu hình đầu, Coverage
  10.3065333%; RMSE proxy 0.9326875842. Kiểm tra độc lập và nạp model không fit
  khớp 1.877 user; chạy lại trùng chín tệp. Chưa tuning, ItemCF/MF hoặc mở test;
  giữ mọi Word theo yêu cầu.

- 2026-10-25: Hoàn thành Bước 8 Popularity trên validation: tổng log2(1 + count)
  từng cặp train, tổng ổn định theo thứ tự dòng và hòa điểm theo ID số tăng dần.
  Phân biệt điểm với listener count dùng đo ARP/Novelty, kiểm tra ví dụ tính tay,
  count không hữu hạn, trùng cặp, lọc lịch sử và cold-start. Dùng chung runner
  I/O với Random, giữ hai CLI riêng và mọi run cũ. NDCG@10 0.06236226641020536,
  Coverage@10 28/15.398; kiểm tra độc lập và chạy lại trùng năm hash kết quả.
  Chưa mở test hoặc triển khai UserCF; toàn bộ Word giữ nguyên theo yêu cầu.

- 2026-10-25: Hoàn thành Bước 7 Random seed 42 trên validation, RNG cục bộ theo
  user, xáo trộn full catalog train và lọc lịch sử. Giữ giao diện fit/predict/
  recommend, điểm thứ hạng và reason/cold-start rõ ràng; không học lượt nghe.
  CLI đọc run Bước 4 có hash, không mở test hoặc ghi đè. Lưu danh sách, chỉ số
  từng user/từng K, trạng thái catalog/config và thời gian; đối chiếu độc lập
  NumPy/ma trận thưa và chạy lại trùng năm hash kết quả. NDCG@10 validation
  0.0003721497084376631, 1.865 user đủ điều kiện. Chưa chạy Popularity.
  Theo yêu cầu mới nhất, chỉ sửa Word khi người dùng yêu cầu rõ ràng, không tự
  cập nhật sau mỗi bước hoặc sau khi chạy hết mô hình; mọi bản Word giữ nguyên.

- 2026-10-25: Hoàn thành Bước 6 kiểm chứng evaluator trên ví dụ tổng hợp: sửa
  Precision chia K khi trả thiếu, thêm NDCG, full ranking/hòa điểm theo mapping,
  lọc lịch sử đúng từng split và từ chối trùng/seen/ngoài catalog. Báo đích ngoài
  catalog, user không còn đích và danh sách rỗng/thiếu; thêm Coverage/Gini/ARP/
  Novelty/ILD cùng mẫu số và RMSE riêng cho điểm đại diện. Giữ Novelty cộng một
  theo V14, ILD nhị phân train; kiểm tra tay và đối chiếu NDCG độc lập. CLI toy
  không đọc HetRec, lưu run mới có hash/snapshot, chạy lại trùng ba JSON kết quả.
  Đồng bộ cấu hình, tài liệu và báo cáo đầy đủ kế thừa V14. Chưa chạy mô hình.

- 2026-10-24: Hoàn thành Bước 5: giữ count gốc, tạo log2(1 + count), nhị phân
  và điểm đại diện 1–5; phân vị 20/40/60/80% nội suy tuyến tính chỉ học từ train,
  áp dụng nguyên cho validation/test, bằng ngưỡng ở mức thấp hơn. Lưu ba Parquet
  đầy đủ, bốn CSR train 1.877 × 15.398 với 74.275 ô quan sát và mapping nguyên byte.
  CLI kiểm tra hash và không ghi đè; kiểm tra độc lập từng giá trị/tọa độ và chạy lại
  chín tệp trùng hash. Đồng bộ docs và bản khóa luận đầy đủ V14 kế thừa Bước 4,
  giữ mọi Word cũ. Chưa xây evaluator, học thẻ/similarity hoặc huấn luyện.

- 2026-10-24: Hoàn thành Bước 4 chia tập/ánh xạ: 74.275 cặp train, 9.263 validation,
  9.263 test, seed 42; giữ đủ 1.877 user, catalog train 15.398 artist. Thay split
  hard-code leave-one-out bằng CLI đọc run làm sạch có hash và config, chỉ ghi run mới.
  Giữ mọi cặp/count holdout ngoài catalog với item_index null; báo đích và user đủ điều kiện.
  Kiểm tra độc lập bảo toàn, phân tách, mapping và chạy lại trùng hash; cập nhật tài liệu
  và bản Word đầy đủ ngày 24/10 kế thừa V13. Chưa biến đổi, học đặc trưng hoặc huấn luyện.

- 2026-10-24: Khảo sát nhánh mở rộng sau sáu baseline: ưu tiên implicit ALS và BPR-MF,
  dự phòng SLIM; đối chiếu Lesota 2021, LFGCF 2022, BoxGNN 2024 cùng phương pháp gốc.
  Bổ sung thiết kế lượt đầu, trần 8/8/4 cấu hình, kiểm tra seed và điều kiện trước khóa
  test; bảo vệ M1/M2 cùng các mốc 15/11, 22/11, 27/11. Đồng bộ tài liệu làm việc,
  quy tắc và câu hỏi seminar; chưa sửa báo cáo Word, code/config, cài thư viện hoặc train.
  Khi cần dành chỗ trong báo cáo, rút diễn giải/phụ lục và giữ bảng kết quả mọi mô hình.

- 2026-10-21: Bước 3 làm sạch riêng: count và ID hợp lệ, phát hiện cặp count mâu thuẫn,
  giữ user ≥ 5 artist, không lọc tần suất artist hoặc biến đổi count. Còn 1.877 user,
  17.617 artist có tương tác và 92.801 cặp; danh mục giữ đủ 17.632 artist.
  Tách 1.538 gán thẻ ngoài danh mục; đọc tags bằng Latin-1, giữ userID cho protocol M2.
  Tải lại ZIP chính thức và xác minh trùng byte; kiểm tra đầu ra độc lập, nguồn giữ nguyên.
  Thay preprocess cũ bằng CLI có output-dir riêng, thêm logic trong src và regression tests;
  đồng bộ config/data card/README. Chưa chia tập, mapping, TF–IDF hoặc huấn luyện.
  Báo cáo mới kế thừa V12, giữ nguyên bản đã bàn giao và đề cương Chương 4–5.

- 2026-10-20: Đổi tên hai bản Word theo yêu cầu mới của GVHD và số đề tài 33:
  `33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_DD-MM-YYYY.docx`.
  V1 dùng ngày lưu sửa trong metadata Word 04/10/2026; V2 dùng 19/10/2026.
  Giữ nguyên nội dung và mã băm; đồng bộ quy tắc đặt tên và các liên kết Markdown.

- 2026-10-19: Bước 2 EDA dữ liệu gốc: thêm một script phân tích và kiểm tra nhỏ,
  extra analysis cho Matplotlib; lưu bảng, năm biểu đồ, mã băm và bản chụp mã.
  Kiểm tra chéo bằng standard library và chạy lại cho cùng thống kê; nguồn không đổi.
  Chưa làm sạch, chia tập, biến đổi đầu vào mô hình hoặc huấn luyện.
  Xuất bản khóa luận đầy đủ V2 ngày 19/10/2026: bổ sung kết quả EDA,
  đồng bộ trạng thái và kế hoạch; cập nhật mục lục và kiểm tra 97 trang.
  Giữ nguyên báo cáo V1; người dùng tự đọc và gửi GVHD.

- 2026-10-19: Bước 1 xác minh ZIP/tệp giải nén, schema, kiểu số và khóa nối; lưu
  bằng chứng kiểm tra, bổ sung encoding không đồng nhất và mã nghệ sĩ gán thẻ
  ngoài danh mục vào data card. Chưa EDA, làm sạch, sửa cấu hình hay huấn luyện.

- 2026-10-19: Cập nhật hạn demo cuối tháng 11 thành lịch 19/10–30/11: chọn mô hình
  15/11, demo đủ luồng 22/11, hoàn thành nội bộ 27/11 và dự phòng 28–30/11. Thêm
  điều kiện nghiệm thu demo và phương án xử lý trễ, giữ các điểm dừng từng bước.
- 2026-10-19: Đồng bộ các tài liệu Markdown với hướng dẫn GVHD và cách làm từng
  bước: sáu baseline, M1/M2 sau baseline, kiểm tra kiến thức và bằng chứng cuối bước.
- Thay lịch 12 tuần cố định bằng bốn giai đoạn 16 tuần tham khảo; đơn giản hóa theo
  dõi tiến độ, ghi rõ các phần chưa được kiểm chứng và quy tắc lưu phiên bản Word.
- Lượt này chỉ sửa tài liệu, không thay mã/cấu hình, chạy xử lý dữ liệu hay mô hình.

### Planned

- Thêm pipeline xử lý HetRec/Last.fm và data validation.
- Cài đặt lần lượt Random, Popularity, User-based CF, Item-based CF, SVD có độ lệch,
  PureSVD rồi kiểm chứng M1/M2 theo các điểm dừng được cho phép.
- Đóng gói mô hình và API/UI sau lựa chọn thực nghiệm; DVC remote/MLflow chỉ thêm
  khi thực sự cần.

## [0.1.0] - 2026-08-25

### Added

- Khởi tạo modular monorepo, package `musicrec`, test layout và GitHub Actions CI.
- Thêm khung DVC/MLflow, cấu hình model, API contract và tài liệu vận hành.
- Thêm quy tắc phát triển, changelog và mô tả kiến trúc.
