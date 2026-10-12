# Chạy nghiên cứu và tái hiện LastFM trên Windows

Phạm vi, metric và các điều chỉnh nằm trong [ADR 0002](../adr/0002-lastfm-reproduction-protocols.md).
Phép toán của từng mô hình được giải thích trong [algorithms](algorithms.md).
Các thống kê và kết quả mới nằm trong [dataset study](dataset-study.md) và
[reproduction report](reproduction-report.md). DOCX nguồn giữ nguyên.

## Dựng môi trường

Chạy tại thư mục gốc repository. Python 3.10 có sẵn dùng cho bridge; uv tải Python
3.11 riêng cho dự án. Không cài RecBole vào môi trường NumPy 2 của ứng dụng.

```powershell
powershell -NoProfile -File scripts/research_setup.ps1
```

Môi trường chính dùng `uv.lock`; môi trường RecBole dùng
`requirements/legacy-reproduction.txt`. PyTorch CPU 2.5.1 ở cả hai môi trường.
Dependency lock là môi trường đã khôi phục, không khẳng định đó là lock gốc năm 2022.

## Chạy toàn bộ, có tiếp tục các lượt đã hoàn tất

```powershell
& '.venv/Scripts/python.exe' scripts/research.py all
```

Lần đầu cần mạng để lấy ZIP và 37 file upstream. Downloader kiểm tra SHA-256 ZIP
và Git blob SHA1 từng file của commit đã ghim. Trên Windows, khi urllib không kết
nối được GroupLens, downloader dùng PowerShell TLS; không tắt xác minh chứng chỉ.
Chỉ converter riêng nạp pickle đã xác minh. Sau đó dùng NPZ với `allow_pickle=False`.

`all` chạy tuần tự: tải -> EDA -> chuyển split -> kiểm tra -> tham chiếu -> 90 lượt
graph -> 30 BPR chung -> 3 BPR benchmark -> đối chiếu evaluator -> báo cáo. BPR có
thể mất nhiều giờ trên CPU; giữ early stopping 50 và trần 5.000 epoch. Không cắt
ngắn lượt chạy để gọi là tái hiện hoàn tất.

## Chạy từng mốc

```powershell
& '.venv/Scripts/python.exe' scripts/research.py download
& '.venv/Scripts/python.exe' scripts/research.py analyze
& '.venv/Scripts/python.exe' scripts/research.py convert
& '.venv/Scripts/python.exe' scripts/research.py benchmark-splits
& '.venv/Scripts/python.exe' scripts/research.py validate-splits
& '.venv/Scripts/python.exe' scripts/research.py verify-reference
& '.venv/Scripts/python.exe' scripts/research.py run --protocol aiprobs-original
& '.venv/Scripts/python.exe' scripts/research.py train-bpr --protocol aiprobs-original
& '.venv/Scripts/python.exe' scripts/research.py run --protocol aiprobs-original --model bpr
& '.venv/Scripts/python.exe' scripts/research.py train-bpr --protocol recbole-bpr-benchmark
& '.venv/Scripts/python.exe' scripts/research.py run --protocol recbole-bpr-benchmark
& '.venv/Scripts/python.exe' scripts/research.py verify-metrics
& '.venv-legacy/Scripts/python.exe' scripts/research_checkpoint_check.py
& '.venv/Scripts/python.exe' scripts/research_repeatability.py
& '.venv/Scripts/python.exe' scripts/research_checks.py
& '.venv/Scripts/python.exe' scripts/research.py report
```

`--split-id` chạy một split; `--seed` ở CLI đánh giá phải đúng giao thức, không
thay split tác giả. `--config` dùng YAML riêng nhưng K=10/binary/no-filter được kiểm
tra. Profile `thesis` được khai báo nhưng chủ động không chạy trong đợt tái hiện.

## Bằng chứng và phục hồi

- `outputs/research/download_manifest.json`: URL, kích thước, checksum, commit upstream.
- `data/processed/reproduction`: 30 split tác giả và 3 split benchmark cùng JSON nguồn.
- `outputs/research/split_validation.json`: conservation, native masks, cold targets.
- `tiny_reference_verification.json`, `full_reference_verification.json` trong outputs:
  sai số số học; patch cấp phát đồ thị riêng. Full reference dùng nhiều RAM hơn kernel
  sparse vì giữ nguyên phép chuẩn hóa/scoring tác giả.
- `outputs/research/runs`: config, source snapshot/checksum, ranking, per-user metrics,
  diagnostics và MLflow run của từng lượt. Tên metric `@10` trong CSV được ghi thành
  `_at_10` trong MLflow do giới hạn tên metric.
- `outputs/research/bpr`: cấu hình có hiệu lực, môi trường, source, checkpoint và factors.
  Checkpoint mới lưu RNG Python/NumPy/Torch/loader. Checkpoint không tương thích bị bỏ
  qua để chạy lại từ đầu; không giả nhận đã khôi phục đúng trạng thái ngẫu nhiên.
- `outputs/research/mlflow.db` + `mlartifacts`: tracking cục bộ. Không dùng dịch vụ cloud.
- CSV tổng hợp giữ riêng giao thức và dẫn về từng MLflow run. Kiểm chứng metric gồm
  vector từng user với RecBole, không chỉ so số trung bình đã làm tròn.
- `acceptance.json` chặn nghiệm thu nếu thiếu một trong 123 lượt, kiểm chứng evaluator
  tương ứng, split/reference, repeatability hoặc chất lượng mã. `repeatability.json`
  kiểm tra fresh fit diffusion và fresh factor load BPR trên split 0; không tự nhận
  đó là bằng chứng huấn luyện BPR lại từ đầu trên cả 30 split.
- `checkpoint_verification.json` so sánh 4 epoch BPR liên tục với 2 epoch + khôi phục
  RNG/checkpoint + 2 epoch. Đây là kiểm tra trạng thái model/Adam, không đưa kết quả
  chạy ngắn vào bảng thực nghiệm khoa học.

Xem MLflow khi cần:

```powershell
& '.venv/Scripts/python.exe' -m mlflow ui --backend-store-uri sqlite:///outputs/research/mlflow.db --host 127.0.0.1
```

## DVC và kiểm tra chất lượng

DVC hiện dùng cache cục bộ, `core.no_scm=true`, sidecar được Git version hóa thủ
công; không tự stage/commit và chưa cấu hình remote. Dataset lớn không nằm trong Git.
ZIP, mã/split upstream và split đã chuyển đổi có `.dvc` riêng. Lệnh DVC trên Windows:

```powershell
$env:DVC_SYSTEM_CONFIG_DIR = Join-Path (Get-Location) '.tools/dvc-system-config'
$env:DVC_GLOBAL_CONFIG_DIR = Join-Path (Get-Location) '.tools/dvc-global-config'
$env:DVC_SITE_CACHE_DIR = Join-Path (Get-Location) '.tools/dvc-site-cache'
& '.venv/Scripts/python.exe' -m dvc status data/raw/hetrec2011-lastfm-2k.zip.dvc data/interim/aiprobs-source.dvc data/processed/reproduction.dvc
& '.venv/Scripts/python.exe' -m ruff check .
& '.venv/Scripts/python.exe' -m ruff format --check .
& '.venv/Scripts/python.exe' -m mypy src
& '.venv/Scripts/python.exe' -m pytest
```

`dvc.yaml` ban đầu vẫn là pipeline scaffold khóa luận; không dùng `dvc repro` toàn
bộ để chạy nghiên cứu này. API/UI và model release cũng chưa thuộc nghiệm thu đợt này.
