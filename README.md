# MusicRec

Khóa luận nghiên cứu **khuyến nghị Top-K nghệ sĩ** từ lịch sử nghe nhạc ngầm, với dữ liệu chính dự kiến là HetRec 2011 Last.fm 2K. So sánh Random, Popularity, UserCF, ItemCF, MF có độ lệch thường gọi SVD và PureSVD; sau đó kiểm chứng M1 về tái xếp hạng và M2 cho hồ sơ ít lịch sử.

Khảo sát ngày 24/10/2026 xác định **implicit ALS và BPR-MF** là hai ứng viên mở rộng, **SLIM** dự phòng; chưa thay sáu baseline hoặc bổ sung vào báo cáo Word. Chỉ cân nhắc thử sau baseline, trước chốt nền M1/test nếu không ảnh hưởng mốc 15/11; thiếu thời gian thì để sau demo. Xem [căn cứ bài báo](docs/TONG_QUAN_TAI_LIEU_THAM_KHAO.md#khao-sat-mo-rong-20261024) và [thiết kế có giới hạn](docs/WEEKLY_IMPLEMENTATION_PLAN.md#thực-nghiệm-bổ-sung-có-giới-hạn). Chưa cài thư viện, tạo config hoặc huấn luyện cho nhánh này.

Repository hiện là bộ khung để triển khai theo từng bước, chưa phải hệ thống thực nghiệm đã hoàn thiện. Không coi cấu hình, bảng minh họa hoặc đầu ra của nhánh thử nghiệm khác là kết quả khóa luận đã được xác nhận.

**Hạn demo: cuối tháng 11/2026.** Kế hoạch đặt mốc chọn mô hình 15/11, demo chạy đủ luồng 22/11, sẵn sàng nội bộ 27/11 và dự phòng 28–30/11. Ngày 30/11 là mốc lập kế hoạch khi chưa có ngày/giờ nộp chính xác; xem lịch và phương án xử lý trễ trong [kế hoạch hiện hành](docs/WEEKLY_IMPLEMENTATION_PLAN.md).

## Bắt đầu

Lệnh cài môi trường và chạy kiểm tra của bộ khung:

```powershell
uv sync --all-extras
uv run pre-commit install
uv run pytest
```

Các lệnh này không thay thế việc kiểm tra nguồn, EDA và xác minh từng bước pipeline. Không tự chạy dvc repro hoặc toàn bộ thí nghiệm khi mới được phép làm một bước.

## Tài liệu làm việc

- [Kế hoạch từng bước](docs/WEEKLY_IMPLEMENTATION_PLAN.md): vận dụng hướng dẫn của cô, lộ trình dữ liệu → EDA → mô hình → thực nghiệm → prototype.
- [Quy tắc phát triển](DEVELOPMENT_RULES.md): phạm vi được phép, giải thích cuối bước và lưu phiên bản báo cáo.
- Đề tài **33**: [báo cáo mới nhất sau Bước 6, ngày 25/10/2026](docs/reports/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_25-10-2026.docx), kế thừa V14 và giữ mọi bản cũ. Tên báo cáo theo mẫu `33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_DD-MM-YYYY.docx`.
  Theo yêu cầu mới nhất, chỉ cập nhật Word khi người dùng yêu cầu rõ ràng, không tự cập nhật sau mỗi bước hoặc khi chạy hết mô hình. Kết quả Bước 7–12 nằm trong run và tài liệu làm việc, chưa đưa vào Word.
- [Data card](docs/data-card.md): thông tin nguồn và các mục còn chờ xác minh.
- [Ôn tập và câu hỏi bảo vệ](docs/SEMINAR_CHUONG_1_2.md).
- [Phối hợp và theo dõi](docs/PROGRESS_TRACKING_GUIDE.md), [cấu trúc dự kiến](PROJECT_STRUCTURE.md), [lịch sử thay đổi](CHANGELOG.md).

Nguồn đối chiếu chính là [hướng dẫn của GVHD](docs/Hướng%20dẫn%20từng%20bước%20hoàn%20thành%20khóa%20luận.docx), kế hoạch và bằng chứng run hiện hành. Đã hoàn thành Bước 1–12: dữ liệu, evaluator và lượt chạy đầu của đủ sáu baseline Random, Popularity, UserCF, ItemCF, SVD có độ lệch, PureSVD. CF/MF/PureSVD mới chạy mỗi mô hình một cấu hình trên validation, xem [data card](docs/data-card.md). Dừng giải thích Bước 12; chưa tinh chỉnh, so sánh biểu diễn, học thẻ hoặc đánh giá test. Dữ liệu gốc, các run trước và mọi bản Word đã bàn giao giữ nguyên.

## Chạy lại EDA dữ liệu gốc

Môi trường cần pandas, NumPy và extra analysis (Matplotlib). Lệnh đã chạy trong môi trường .venv của dự án:

```powershell
.venv/Scripts/python.exe -B scripts/eda.py --raw-dir data/raw/hetrec2011 --output-dir outputs/runs/raw_eda_new
```

Đường dẫn đầu ra phải chưa tồn tại; script không ghi đè run hoặc sửa nguồn. Đầu ra gồm metrics.json, các bảng CSV, năm biểu đồ và bản chụp mã. Không chạy các script preprocess/split/train để tái lập EDA.

## Chạy lại riêng Bước 3 làm sạch

```powershell
.venv/Scripts/python.exe -B scripts/preprocess.py --raw-dir data/raw/hetrec2011 --output-dir outputs/runs/cleaning_new
```

Đường dẫn đầu ra phải chưa tồn tại. Run đã kiểm chứng là `outputs/runs/cleaning_20261021`: 1.877 người dùng, 92.801 tương tác và 17.617 nghệ sĩ có tương tác; danh mục nguồn vẫn đủ 17.632 nghệ sĩ. Sáu bảng Parquet gồm dữ liệu sạch, danh mục/từ điển thẻ và các dòng loại riêng; có bảng trước/sau, cấu hình, hash và bản chụp mã. Gán thẻ vẫn giữ userID để lọc theo protocol M2 sau này, chưa phải đặc trưng học. Không lọc artist theo số người nghe hoặc biến đổi count.

## Chạy lại riêng Bước 4 chia tập và ánh xạ

```powershell
.venv/Scripts/python.exe -B scripts/split_data.py --clean-run outputs/runs/cleaning_20261021 --output-dir outputs/runs/split_new
```

Output phải chưa tồn tại và nằm ngoài run làm sạch. CLI xác minh mã băm đầu vào, đọc mục split trong configs/base.yaml và chỉ chạy Bước 4. Run đã kiểm chứng là `outputs/runs/split_20261024`: 74.275 cặp train, 9.263 validation và 9.263 test, đủ 1.877 user; mapping train có 15.398 artist. Cùng seed 42 cho cùng dữ liệu dù thứ tự dòng nguồn thay đổi. Ba Parquet giữ nguyên mọi cặp/count; các đích ngoài catalog train có item_index rỗng, không bị xóa hoặc thêm vào mapping. Có id_mappings.json, bảng đếm từng user, cấu hình, hash và snapshot mã; xem số đích/người dùng đủ điều kiện trong data card. Chưa học ngưỡng, TF–IDF, similarity hoặc mô hình.

## Chạy lại riêng Bước 5 biểu diễn đầu vào

```powershell
.venv/Scripts/python.exe -B scripts/prepare_inputs.py --split-run outputs/runs/split_20261024 --output-dir outputs/runs/representations_new
```

Output phải chưa tồn tại và nằm ngoài run split. CLI xác minh hash Bước 4, đọc mục representations trong configs/base.yaml và chỉ tạo đầu vào: count gốc, log2(1 + count), điểm đại diện 1–5 và nhị phân. Bốn ngưỡng phân vị 20/40/60/80% học duy nhất trên log-count train, nội suy tuyến tính; điểm = 1 + số ngưỡng bị vượt nghiêm ngặt. Validation/test áp dụng nguyên ngưỡng train; điểm này không phải sao thật.

Run đã kiểm chứng là `outputs/runs/representations_20261024`: ba Parquet bổ sung log_count/proxy_score/binary, bốn ma trận CSR train 1.877 × 15.398 (74.275 ô quan sát mỗi ma trận), mapping sao chép nguyên byte và transform.json lưu đầy đủ ngưỡng/quy tắc. Mọi cặp/count/chỉ số vẫn giữ nguyên; đích ngoài catalog vẫn có item_index null. Không tạo ma trận held-out làm mất các dòng này hoặc thêm ô chưa quan sát thành nhãn không thích. Có metrics, hash, snapshot mã và kiểm tra độc lập; chín tệp dữ liệu/mapping/biến đổi trùng hash khi chạy lại, kể cả với mã đã hoàn tất kiểm tra kiểu.

## Chạy lại riêng Bước 6 kiểm chứng evaluator

```powershell
.venv/Scripts/python.exe -B scripts/evaluate.py --toy-check --output-dir outputs/runs/evaluator_new
```

Output phải chưa tồn tại. CLI chỉ dùng dữ liệu tổng hợp trong mã, không đọc HetRec hoặc chạy mô hình. Run đã kiểm chứng là `outputs/runs/evaluator_20261025`; lưu đầu vào, chỉ số từng user/từng K, đáp án tính tay, cấu hình, hash và snapshot mã. Ba tệp JSON kết quả trùng hash khi chạy lại.

Evaluator dùng full ranking trên catalog train, hòa điểm theo thứ tự mapping; validation lọc train, test lọc train + validation nhưng thống kê vẫn chỉ từ train. Đích ngoài catalog và user không còn đích được báo riêng. Precision chia K kể cả trả thiếu; người còn đích nhưng danh sách rỗng vẫn nhận 0 trong trung bình. Từ chối mục trùng/đã nghe/ngoài catalog. Có Precision/Recall/NDCG tại 5/10/20, Coverage, Gini, ARP, Novelty và ILD; quy tắc tổng hợp và giá trị không xác định nằm trong `configs/evaluation.yaml` và docstring evaluator. Novelty giữ công thức cộng một/chuẩn hóa của báo cáo V14; ILD dùng cosine nhị phân train, không phải similarity đã học cho CF. RMSE tách riêng, chỉ dùng khi dự đoán cùng điểm đại diện.

Ví dụ Phụ lục B: đích {A,C}, danh sách [B,A,C], K=3 cho Precision=2/3, Recall=1, NDCG≈0,693426; Gini của [2,1,1,0] bằng 0,375. Đã đối chiếu NDCG với scikit-learn trên 20 ví dụ × 4 cutoff. Đây là kiểm tra tính đúng, chưa phải kết quả mô hình.

## Chạy lại riêng Bước 7 Random trên validation

```powershell
.venv/Scripts/python.exe -B scripts/run_random.py --split-run outputs/runs/split_20261024 --output-dir outputs/runs/random_validation_new
```

Output phải chưa tồn tại và nằm ngoài run split. CLI xác minh hash train/validation/mapping của Bước 4; không mở `test.parquet`, kể cả để băm. Random chỉ lấy catalog và user train, không học từ lượt nghe. Mỗi user có RNG cục bộ từ `musicrec-random-v1:42:{user_id}`, xáo trộn toàn catalog theo thứ tự ID số rồi lọc train, lấy tối đa 20 mục. Các K dùng prefix cùng danh sách; điểm là thứ hạng hoán vị giảm dần, không phải rating hoặc xác suất. Kết quả độc lập thứ tự dòng train/thứ tự gọi; runtime Python được lưu để chạy lại.

Run `outputs/runs/random_validation_20261025` lưu 37.540 dòng gợi ý cho đủ 1.877 user; evaluator tính trên 1.865 user còn đích trong catalog 15.398 artist, báo riêng 12 user và 1.121 đích ngoài catalog. NDCG@10 validation = **0.0003721497084376631**; Precision@10 = 0.00032171581769437004; Recall@10 = 0.0006970509383378016. Coverage@10 = 0.7060007793, ILD@10 = 0.9984051271; hai chỉ số bổ sung cao không chứng minh danh sách phù hợp. Không có danh sách thiếu/rỗng. Không chọn lại seed hoặc tính RMSE cho Random.

Có `recommendations.csv`, `evaluation.json` từng user, `metrics.csv`, trạng thái catalog/config trong `model.json`, mapping, thời gian fit/recommend/evaluator, hash và snapshot mã. Kiểm tra độc lập tái dựng mọi danh sách/điểm từ trạng thái đã lưu; tính lại chỉ số bằng NumPy/ma trận thưa, không gọi model/evaluator production. Chạy lại cùng seed cho năm tệp dự đoán/chỉ số/trạng thái/mapping trùng hash. Word giữ nguyên. Đây là kết quả riêng của Bước 7; Bước 8 được ghi bên dưới.

## Chạy lại riêng Bước 8 Popularity trên validation

```powershell
.venv/Scripts/python.exe -B scripts/run_popularity.py --split-run outputs/runs/split_20261024 --output-dir outputs/runs/popularity_validation_new
```

Output phải chưa tồn tại và nằm ngoài run split. Hai baseline dùng chung I/O/kiểm tra hash trong `scripts/run_baseline.py`, cùng catalog, masking, cohort và evaluator. Popularity nhận **count gốc**, biến đổi từng cặp đúng một lần rồi cộng `log2(1 + count)` theo artist trên train; không cộng count gốc hoặc log sau khi cộng. Fit lưu toàn bộ điểm và thứ tự, hòa điểm theo ID số tăng dần; recommend chỉ lọc lịch sử rồi lấy prefix. Không dùng điểm Popularity làm listener count cho ARP/Novelty. Seed 42 ghi nguồn split, không điều khiển model xác định này.

Run `outputs/runs/popularity_validation_20261025` trả đủ 20 mục cho 1.877 user, đánh giá cùng 1.865 user như Random. NDCG@10 = **0.06236226641020536**, Precision@10 = 0.03394101876675604, Recall@10 = 0.07319034852546917. Coverage@10 chỉ **28/15.398 = 0.1818417976%**, ARP@10 = 351.8289544 và ILD@10 = 0.6647826606. Chỉ số xếp hạng cao hơn Random trên validation này, đồng thời danh sách tập trung mạnh vào ít artist nhiều người nghe; chưa kết luận mô hình tốt nhất hoặc kết quả test.

Run lưu điểm toàn catalog trong `model.json`, danh sách/score/reason, chỉ số từng user/K, config, mapping, thời gian, hash và snapshot mã. Kiểm tra độc lập tính lại tổng log-count từ train bằng NumPy, tái dựng danh sách từ điểm đã lưu và tính lại evaluator bằng ma trận thưa. Chạy lại cho năm tệp kết quả trùng hash; không đọc tệp test và không sửa Word. Đây là kết quả riêng Bước 8; Bước 9 ở bên dưới.

## Chạy lại riêng Bước 9 UserCF cấu hình đầu

```powershell
.venv/Scripts/python.exe -B scripts/run_user_cf.py --representations-run outputs/runs/representations_20261024 --output-dir outputs/runs/user_cf_new
```

CLI chỉ chấp nhận cấu hình [UserCF hiện hành](configs/models/user_cf.yaml), đọc train/validation/mapping/transform có hash từ Bước 5, không mở test hoặc ghi đè run. `Interaction.proxy_score` tách riêng điểm đại diện 1–5 khỏi count gốc; UserCF không học lại ngưỡng và không dùng count thay điểm. Cosine trên toàn vector proxy train (vị trí thiếu bằng 0 để tính cosine), chọn tối đa 40 user tương đồng dương, bỏ chính user đang chấm; từng item chỉ dùng các láng giềng đã nghe item. Dự đoán = mean quan sát của user + trung bình độ lệch láng giềng có trọng số. Thiếu đóng góp dùng mean user; user mới dùng mean chung với reason riêng, chưa phải M2. Không cắt dự đoán về 1–5. Khóa sắp thứ tự làm tròn 12 chữ số để triệt nhiễu số thực khi hòa điểm, sau đó ưu tiên mapping số; score gốc giữ nguyên.

Run chốt là `outputs/runs/user_cf_l40_s0_validation_20261025_checked`: NDCG@10 **0.008078755530928147**, Precision@10 0.0057372654, Recall@10 0.0129490617 trên cùng 1.865 user như hai baseline trước. Thấp hơn Popularity về ranking ở cấu hình này, nhưng Coverage@10 **10.3065333%**, ILD@10 0.9669347, ARP@10 31.3817694. RMSE bổ sung trên 8.142 đích proxy hợp lệ = **0.9326875842**; không dùng RMSE chọn ranking. Có 1.840 đích dùng mean fallback; 707 dự đoán held-out ngoài 1–5 được giữ nguyên, không cắt.

Lưu CSR proxy, láng giềng và means trong `model/`; nạp lại không fit hoặc tính similarity mới và khớp đủ 1.877 danh sách. Kiểm tra độc lập mọi top-40, điểm, chỉ số và fallback; chín tệp kết quả/model trùng hash ở run `_recheck`. Run không có hậu tố `_checked` là bản kiểm tra ban đầu bị loại vì nhiễu số thực ảnh hưởng hòa láng giềng ở 12 user, có `audit.json` và vẫn giữ nguyên; không dùng làm kết quả báo cáo. L/shrinkage không đổi, chưa tuning. Kết quả Bước 10 nằm ở mục tiếp theo.

## Chạy lại riêng Bước 10 ItemCF cấu hình đầu

```powershell
.venv/Scripts/python.exe -B scripts/run_item_cf.py --representations-run outputs/runs/representations_20261024 --output-dir outputs/runs/item_cf_new
```

Output phải chưa tồn tại và nằm ngoài nguồn Bước 5. CLI dùng chung runner và evaluator, chỉ đọc train/validation/mapping/transform có hash; không mở test. [Cấu hình ItemCF](configs/models/item_cf.yaml) chốt L=40, shrinkage=0, cosine toàn cột proxy train, chỉ tương đồng dương và bỏ chính artist. Chọn top-L toàn catalog cho từng artist đích rồi giao với lịch sử user; dự đoán là trung bình proxy đã nghe có trọng số, không trừ mean như UserCF. Thiếu đóng góp dùng mean user; user mới dùng mean chung và reason riêng, chưa phải M2. Khóa sort làm tròn 12 chữ số rồi theo mapping; score gốc không clip. Tính similarity từng khối 256 artist và chỉ lưu top-L, không tạo toàn ma trận item–item.

Run `outputs/runs/item_cf_l40_s0_validation_20261026` trả đủ 20 mục cho 1.877 user, đánh giá cùng 1.865 user/8.142 đích hợp lệ như ba baseline trước. NDCG@10 **0.0074299548**, Precision@10 0.0040214477, Recall@10 0.0091331546; thấp hơn UserCF cấu hình đầu (0.0080787555) và Popularity (0.0623622664). Coverage@10 **3.465/15.398 = 22.5029225%**, ILD@10 0.8328794, ARP@10 34.4053083. Có 1.217/18.650 vị trí Top-10 dùng mean fallback, nên độ phủ này gồm cả fallback. RMSE proxy bổ sung **0.9796199383** trên 8.142 cặp; không dùng chọn ranking. Chưa tuning hoặc kết luận mô hình cuối.

Nạp lại CSR/model không fit và khớp đủ 1.877 danh sách; kiểm tra độc lập toàn 15.398 bộ láng giềng, mọi danh sách/score/reason, RMSE và metric từng user/K. Chạy lại trùng hash chín tệp kết quả/model; guard kiểm toán chặn mở test.parquet. **53 tests đạt; ruff check, format và mypy toàn mã nguồn đạt** tại Bước 10. Sửa nhỏ lỗi style/type cũ để các kiểm tra này chạy sạch; không triển khai luồng prototype mới. Bằng chứng chi tiết và chi phí trong [data card](docs/data-card.md). Run/model/dataset giữ cục bộ theo .gitignore; Git chỉ lưu mã, cấu hình và tài liệu. Word giữ nguyên Bước 6. Kết quả SVD có độ lệch nằm ở mục Bước 11 tiếp theo.

## Chạy lại riêng Bước 11 SVD có độ lệch cấu hình đầu

```powershell
.venv/Scripts/python.exe -B scripts/run_svd.py --representations-run outputs/runs/representations_20261024 --output-dir outputs/runs/svd_new
```

Output phải chưa tồn tại và nằm ngoài nguồn Bước 5. [Cấu hình](configs/models/svd.yaml) là 32 nhân tố, learning rate 0.005, regularization 0.02, seed 42; không dùng YAML 64 nhân tố/30 vòng của khung cũ. SGD học duy nhất các cặp proxy 1–5 quan sát trong train theo công thức mean + user bias + artist bias + tích vô hướng factor. Mean cố định từ train, bias khởi tạo 0, factor normal(0, 0.1) bằng PCG64; mỗi epoch xáo trộn các cặp đã sắp theo mapping. Hai factor cập nhật từ trạng thái trước bước học; điều chuẩn áp theo từng quan sát. Không dùng ô thiếu làm nhãn 0 hoặc thay MF bằng TruncatedSVD.

CLI giới hạn BLAS một luồng, dùng chung I/O/evaluator/cohort, không mở test. Tối đa 100 epoch; từ epoch 1 tính full-ranking NDCG@10 validation mỗi epoch, dừng sau 5 epoch không tăng nghiêm ngặt, hòa giữ epoch sớm nhất rồi khôi phục checkpoint tốt nhất. Validation không tạo gradient; RMSE chỉ bổ sung. User mới dùng mean + bias artist và reason riêng, chưa phải M2; artist ngoài catalog bị từ chối. Score không clip; khóa sort làm tròn 12 chữ số rồi mapping số.

Run `outputs/runs/svd_k32_validation_20261026` chạy 6 epoch, chọn **epoch 1**. NDCG@10 **0.0564899628**, Precision@10 0.0301876676, Recall@10 0.0657283289 trên cùng 1.865 user/8.142 đích hợp lệ; thấp hơn Popularity 0.0623622664, cao hơn hai CF cấu hình đầu. Coverage@10 **82/15.398 = 0.5325367%**, ARP@10 317.0871850, ILD@10 0.7211057; danh sách vẫn tập trung mạnh. RMSE proxy bổ sung **1.2439097807**, không dùng chọn epoch. Train RMSE giảm 1.233116 → 0.864501 qua sáu epoch nhưng NDCG@10 giảm 0.056490 → 0.043140; [đường học](outputs/runs/svd_k32_validation_20261026/audit/learning_curve.png) minh họa sự khác biệt giữa fit điểm và ranking.

Kiểm tra độc lập bằng số vô hướng tái hiện **445.650 cập nhật SGD** qua cả sáu epoch, train loss/validation NDCG, checkpoint và đủ 1.877 danh sách/score/reason/các chỉ số. Sai khác tham số tối đa 1.11023e-16; nạp lại không fit và chạy lại **10 tệp trùng hash**, gồm learning_curve.csv. **59 tests đạt; lint/format/mypy toàn mã nguồn đạt** tại Bước 11. Kết quả, model và mã audit giữ cục bộ; tài liệu có số đo trong [data card](docs/data-card.md). Word giữ Bước 6; chưa tuning hoặc mở test. Kết quả PureSVD nằm ở mục Bước 12 tiếp theo.

## Chạy lại riêng Bước 12 PureSVD cấu hình đầu

```powershell
.venv/Scripts/python.exe -B scripts/run_pure_svd.py --representations-run outputs/runs/representations_20261024 --output-dir outputs/runs/pure_svd_new
```

Output phải chưa tồn tại và nằm ngoài nguồn Bước 5. [Cấu hình](configs/models/pure_svd.yaml) dùng **32 chiều, proxy_score train, seed 42**. Ma trận thưa R không trừ mean/chuẩn hóa hoặc thêm bias; các ô thiếu là 0 đại số trong bài toán phân rã, không phải quan sát không thích. SciPy svds/ARPACK lấy 32 trị suy biến lớn nhất, tolerance=1e-10, maxiter=10000, ncv mặc định; vector đầu PCG64(42), BLAS một luồng. Score là **R V32 V32.T**, tương đương tái dựng U32 Sigma32 V32.T; không nhân Sigma thêm lần nữa, không học bằng SGD/validation hoặc dừng sớm. User mới có score 0 và reason fallback riêng theo thứ tự ID; chưa phải M2. Score không clip, khóa sort 12 chữ số rồi mapping số.

Run `outputs/runs/pure_svd_k32_proxy_validation_20261026` trả đủ 20 mục cho 1.877 user, đánh giá cùng 1.865 user/8.142 đích hợp lệ như năm baseline trước. NDCG@10 **0.1516922327**, Precision@10 0.0780160858, Recall@10 0.1694459339, cao hơn Popularity 0.0623622664 và SVD có độ lệch 0.0564899628 ở các cấu hình đầu. Coverage@10 **362/15.398 = 2.3509547%**, ARP@10 143.9861662, ILD@10 0.8189157. Chưa chốt mô hình cuối hoặc suy ra ổn định qua seed/dataset; độ phủ vẫn thấp và ILD thấp hơn hai CF. Không tính RMSE vì score là mức liên hệ, không phải dự đoán điểm proxy đã hiệu chuẩn.

Kiểm tra độc lập bằng eigh của Gram user–user, không gọi svds/model/evaluator production: khớp 32 trị suy biến/không gian chiếu và đủ 1.877 danh sách/score/reason/chỉ số; sai khác score toàn catalog tối đa 1.54876e-13. Load không fit/phân rã lại; chạy lại **9 tệp trùng hash**. **63 tests đạt; lint/format/mypy toàn mã nguồn đạt**. Bằng chứng, giới hạn và chi phí ở [data card](docs/data-card.md); dataset/model/run giữ cục bộ, Word giữ Bước 6. Dừng Bước 12; **Bước 13 so sánh biểu diễn nhị phân/log/proxy** hoặc tuning số chiều cần cho phép riêng, chưa chạy.

`dvc.yaml`, `validate_data.py` và `scripts/train.py` còn là khung cũ, chưa nối các CLI hiện hành; `scripts/evaluate.py` chỉ kiểm chứng toy, không thay stage evaluate trong DVC. Không dùng `dvc repro` hoặc `scripts/train.py` để chạy toàn bộ nghiên cứu.
