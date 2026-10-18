# MusicRec

Hệ thống khuyến nghị âm nhạc dựa trên Collaborative Filtering cho khóa luận tốt
nghiệp. Repository tổ chức tách biệt pipeline ML offline với API/UI suy luận online.

## Bắt đầu

```powershell
uv sync --all-extras
uv run pre-commit install
uv run pytest
```

Nguồn HetRec hiện có ở `data/raw/hetrec2011/`. `params.yaml` ghép cấu hình dữ liệu,
split, Popularity và evaluator; `configs/experiment.yaml` điều khiển các mô hình,
ngân sách tuning (mặc định 4, tối đa 30 cấu hình mỗi họ), seed, M1 và M2.
Mọi lệnh tạo run mới, không thay kết quả cũ:

```powershell
uv run python scripts/run_pipeline.py --run-id thesis_data
uv run python scripts/run_study.py --data-run outputs/runs/thesis_data --run-id thesis_study
uv run python scripts/run_extensions.py --data-run outputs/runs/thesis_data --study outputs/runs/thesis_study
uv run python scripts/final_evaluation.py --data-run outputs/runs/thesis_data --study outputs/runs/thesis_study
uv run python scripts/export_release.py --data-run outputs/runs/thesis_data --study outputs/runs/thesis_study
uv run uvicorn musicrec.api.main:app --reload
uv run streamlit run src/musicrec/ui/app.py
```

Có thể thay `uv run` bằng `.venv/Scripts/python.exe` (với module, dùng `-m`).
Test chỉ chạy sau khi các mô hình, M1 và M2 đã khóa lựa chọn trên validation;
`test_lock.json` không được ghi đè. Muốn thay phương pháp, tạo study mới.
DVC hiện điều phối pipeline Popularity và ghi con trỏ run; không quản lý/xóa lịch sử run.

Các lệnh cũ validate/preprocess/split/train/evaluate riêng đã được thay bằng
pipeline dùng chung để tránh chạy nhầm split leave-one-out hoặc tổng count.
Run chứa source snapshot, cấu hình hiệu lực, phiên bản thư viện, checksum, split,
model, predictions và metric. Không commit dữ liệu, run hoặc release lớn vào Git.

API mặc định nạp `artifacts/releases/v0.2.0`; có thể đặt `MUSICREC_RELEASE` ở máy chủ.
Thiếu hoặc sai checksum artifact trả 503; không còn artist mẫu. Hồ sơ khách trống
nhận Popularity. User đủ lịch sử dùng mô hình nền và M1; user mới/lịch sử ngắn
hoặc hồ sơ cung cấp dùng M2. Lịch sử trùng hợp nhất bằng count lớn nhất, không cộng
hai lần. K hợp lệ 1–100; trả thiếu nếu catalog đã hết.

Kiểm tra: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`,
`uv run pytest`. Trên sandbox Windows, TestClient có thể cần chạy ngoài sandbox;
có thể dùng `--basetemp=outputs/pytest_<ten_moi>` cho thư mục tạm trong workspace.

Báo cáo V1 và các bản đã phát hành được giữ nguyên. Chỉ xuất bản khóa luận đầy đủ
mới khi cần đồng bộ phương pháp, số liệu hoặc trạng thái code; không tạo báo cáo
tiến độ Word/Markdown bắt buộc sau mỗi mốc.

Xem [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) để biết kiến trúc và quy trình,
[DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md) để biết các quy tắc bắt buộc, và
[CHANGELOG.md](CHANGELOG.md) để theo dõi thay đổi.
