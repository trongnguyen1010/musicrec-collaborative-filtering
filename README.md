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
- Đề tài **33**: [báo cáo mới nhất, ngày 21/10/2026](docs/reports/V13/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_21-10-2026.docx). Tên báo cáo theo mẫu `33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_DD-MM-YYYY.docx`.
- [Data card](docs/data-card.md): thông tin nguồn và các mục còn chờ xác minh.
- [Ôn tập và câu hỏi bảo vệ](docs/SEMINAR_CHUONG_1_2.md).
- [Phối hợp và theo dõi](docs/PROGRESS_TRACKING_GUIDE.md), [cấu trúc dự kiến](PROJECT_STRUCTURE.md), [lịch sử thay đổi](CHANGELOG.md).

Nguồn đối chiếu chính là [hướng dẫn của GVHD](docs/Hướng%20dẫn%20từng%20bước%20hoàn%20thành%20khóa%20luận.docx) và bản báo cáo mới nhất trong docs/reports/. Ngày 19/10/2026 đã kiểm tra nguồn và EDA; ngày 21/10/2026 hoàn thành Bước 3 làm sạch, xem [data card](docs/data-card.md). Đang dừng giải thích Bước 3; chưa chia tập, tạo mapping, biến đổi đầu vào hoặc huấn luyện. Dữ liệu gốc và bản Word V12 đã bàn giao được giữ nguyên.

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

`dvc.yaml`, `validate_data.py` và các bước split/train còn là khung cũ, chưa được nối thành pipeline của quy trình mới. Lệnh Bước 3 trên đọc trực tiếp nguồn đã xác minh; không dùng `dvc repro` hoặc lệnh preprocess cũ không có `--output-dir` để chạy toàn bộ nghiên cứu.
