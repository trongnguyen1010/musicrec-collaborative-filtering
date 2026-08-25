# Quy tắc phát triển MusicRec

## Bắt buộc

1. Không commit dataset, model lớn, `mlruns/`, file `.env`, API key hoặc dữ liệu cá nhân vào Git.
2. Mọi experiment phải ghi seed, config, dataset version/hash, Git SHA và metric.
3. Mọi model phải dùng chung giao diện `fit`, `predict`, `recommend`; đánh giá dùng cùng split và evaluator.
4. Chỉ validation được chọn hyperparameter; test set chỉ chạy sau khi chốt cấu hình.
5. `recommend()` phải loại item user đã nghe, trả metadata/reason khi có, và xử lý cold-start rõ ràng.
6. API không được fit model trong request; chỉ nạp artifact release có `manifest.json` hợp lệ.
7. Thay đổi code phải có test tương ứng. Sửa bug phải có regression test khi khả thi.
8. Trước PR: chạy `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, `uv run pytest`.
9. Không merge trực tiếp vào `main`; PR cần CI xanh và review chéo.
10. Quyết định ảnh hưởng dataset, split, metric, model interface hoặc API contract phải có ADR trong `docs/adr/`.

## Quy ước mã nguồn

- Python 3.11+, type hints cho hàm public, docstring cho module/class public.
- Logic reusable nằm trong `src/`; script chỉ điều phối I/O và CLI.
- Không dùng notebook làm nguồn chân lý cho pipeline hoặc kết quả báo cáo.
- Tên config và artifact phải ổn định, dùng `snake_case`; model release dùng `vMAJOR.MINOR.PATCH`.
- Lỗi API trả schema rõ ràng, không để stack trace lộ ra client.

## Dữ liệu và báo cáo

- Ghi nguồn, ngày tải, license, checksum và schema trong `docs/data-card.md`.
- Mọi bảng/hình báo cáo phải truy xuất được về một MLflow run hoặc release manifest.
- Không kết luận mô hình “tốt hơn” chỉ dựa vào một metric: báo cáo cả accuracy, coverage/diversity và chi phí suy luận.
