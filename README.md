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
- Đề tài **33**: [báo cáo mới nhất sau Bước 5, ngày 24/10/2026](docs/reports/V14/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_24-10-2026.docx), kế thừa bản Bước 4 và giữ mọi bản cũ. Tên báo cáo theo mẫu `33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_DD-MM-YYYY.docx`.
- [Data card](docs/data-card.md): thông tin nguồn và các mục còn chờ xác minh.
- [Ôn tập và câu hỏi bảo vệ](docs/SEMINAR_CHUONG_1_2.md).
- [Phối hợp và theo dõi](docs/PROGRESS_TRACKING_GUIDE.md), [cấu trúc dự kiến](PROJECT_STRUCTURE.md), [lịch sử thay đổi](CHANGELOG.md).

Nguồn đối chiếu chính là [hướng dẫn của GVHD](docs/Hướng%20dẫn%20từng%20bước%20hoàn%20thành%20khóa%20luận.docx) và bản báo cáo mới nhất trong docs/reports/. Đã hoàn thành Bước 1–5: kiểm tra nguồn, EDA, làm sạch, chia tập/ánh xạ và biểu diễn đầu vào, xem [data card](docs/data-card.md). Dừng giải thích Bước 5; chưa xây evaluator, học đặc trưng thẻ/similarity hoặc huấn luyện. Dữ liệu gốc, các run trước và mọi bản Word đã bàn giao giữ nguyên.

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

`dvc.yaml`, `validate_data.py` và bước train còn là khung cũ, chưa được nối với các CLI Bước 3–5 hiện hành. Không dùng `dvc repro` hoặc lệnh preprocess/split thiếu các tham số bắt buộc để chạy toàn bộ nghiên cứu. Bước tiếp theo cần cho phép riêng là Bước 6 kiểm chứng evaluator bằng ví dụ tính tay.
