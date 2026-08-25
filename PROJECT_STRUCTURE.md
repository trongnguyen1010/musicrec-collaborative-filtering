# Bộ khung và cấu trúc dự án MusicRec

## Mục tiêu kiến trúc

Đây là modular monorepo Python. Pipeline offline xử lý dữ liệu, huấn luyện, đánh giá
và phát hành artifact; API/UI online chỉ nạp artifact đã phát hành để suy luận. Không
được huấn luyện lại model trong HTTP request.

```text
src/musicrec/
  data/          dữ liệu, kiểm tra schema, preprocessing, split, mapping
  recommenders/  Popularity, User-CF, Item-CF, SVD và reranker
  evaluation/    RMSE, Precision@K, Recall@K, coverage, diversity, bias
  artifacts/     manifest và kiểm tra tương thích artifact
  serving/       candidate generation, filtering và cold-start fallback
  api/           FastAPI router, schema và xử lý lỗi
  ui/            Streamlit demo; chỉ gọi REST API
```

## Cấu trúc thư mục

| Đường dẫn | Trách nhiệm |
| --- | --- |
| `configs/` | Cấu hình có version cho dataset, model, split và đánh giá. |
| `data/` | Nội dung dữ liệu do DVC quản lý; Git chỉ giữ `README.md` và metadata DVC. |
| `artifacts/releases/` | Model đã duyệt để demo, mapping, metadata, metrics, manifest; do DVC quản lý. |
| `notebooks/` | EDA/phân tích. Logic tái sử dụng phải chuyển vào `src/` hoặc `scripts/`. |
| `reports/` | Hình/bảng sinh cho báo cáo. |
| `scripts/` | Entry point CLI cho từng stage của pipeline. |
| `tests/` | Unit, integration và contract test. |
| `docs/adr/` | Architecture Decision Records; mỗi quyết định quan trọng có lý do và hậu quả. |

## Luồng tái lập

```text
data/raw → validate → preprocess → split → train → evaluate → export_release
                             ↑                      ↓
                       params.yaml             MLflow run
```

`dvc.yaml` mô tả stage, dependency và output. `params.yaml` chứa các tham số có
thể thay đổi giữa experiment. MLflow lưu run-level metrics, biểu đồ và artifact tạm.
Chỉ artifact được chọn cho demo mới export vào `artifacts/releases/<model_version>/`.

Mỗi release bắt buộc có `manifest.json` với: `model_version`, Git SHA, DVC data
hash/phiên bản, MLflow run ID, seed, config hash, metrics và ngày tạo.

## Quy trình Git

- `main` luôn chạy được, không push trực tiếp.
- Nhánh ngắn hạn: `feat/`, `fix/`, `research/`, `docs/`, `chore/`.
- Mọi PR cần CI xanh và ít nhất một review của thành viên còn lại.
- Commit theo Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `chore:`.
- Release demo theo tag Semantic Versioning, ví dụ `v0.1.0`.

## Definition of Done

Một thay đổi được xem là hoàn thành khi: code đã format/lint, test phù hợp đã pass,
config/seed/metric được ghi lại, README hoặc ADR được cập nhật nếu cần, và không có
dataset, model lớn hoặc secret bị commit vào Git.
