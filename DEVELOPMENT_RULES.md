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

## Lưu phiên bản kế hoạch và báo cáo

1. Giữ `khang-dev` làm nhánh nền; lưu thử nghiệm hiện tại trên `codex/musicrec-experiments-18-10-2026`, chỉ đưa về nhánh nền khi người dùng yêu cầu. Giữ thử nghiệm `lastfm-reproduction` độc lập.
2. Không bắt buộc tạo kế hoạch, báo cáo tiến độ hoặc cặp DOCX/Markdown sau mỗi mốc. Ghi tiến độ và kiểm tra trong cuộc trò chuyện; kết quả kỹ thuật nằm trong run riêng.
3. Khi phương pháp, số liệu hoặc hiện trạng code làm báo cáo không còn phù hợp, xuất một bản khóa luận đầy đủ mới ở `docs/reports/`. Giữ văn phong và cấu trúc của báo cáo đang nộp, đồng bộ các chương liên quan; không bắt buộc xuất Markdown.
4. Giữ nguyên bản đã phát hành, kể cả file chưa commit. Không ghi đè, đổi tên hoặc di chuyển. Chỉ xóa những đầu ra được người dùng yêu cầu xóa rõ ràng.
5. Tên mới dùng phiên bản tăng dần, thứ và ngày thực tế tại Việt Nam: `BaoCao_KLTN_CaoTrongNguyen_LeKhacGiaKhang_V2_ChuNhat_18-10-2026.docx`. Kiểm tra trùng tên, tạo file độc quyền; nếu trùng chọn phiên bản tiếp theo.
6. Phân biệt thiết kế, phần đã triển khai và kết quả đã kiểm chứng; không ghi GVHD đã duyệt khi chưa có xác nhận. Không chuyển mục tiêu kỳ vọng thành kết quả đo.
7. Render và kiểm tra tất cả các trang của Word trước bàn giao; giữ bản nháp và ảnh QA ngoài thư mục báo cáo đã phát hành. Xác minh checksum bản nguồn không đổi.
