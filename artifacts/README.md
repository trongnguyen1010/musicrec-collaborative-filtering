# Release artifacts

Thư mục `releases/` dành cho mô hình đã được chọn để demo sau thực nghiệm; chưa
xuất release trong bước cập nhật tài liệu hoặc các bước dữ liệu. Mỗi release dự
kiến có model, ID mapping, biến đổi đầu vào, metadata, metrics, config và
`manifest.json` để tái lập. DVC là lựa chọn quản lý tệp, không phải điều kiện bắt
buộc; không commit model lớn vào Git.

Các lần thử trước khi chọn mô hình lưu trong run riêng, không ghi đè. Chỉ thực hiện
đóng gói khi đến bước prototype theo [kế hoạch hiện hành](../docs/WEEKLY_IMPLEMENTATION_PLAN.md).

## Gói demo trong Git

`releases/demo-chinh-thuc-20261026/` (khoảng 11 MB) được đưa vào Git theo yêu cầu của nhóm ngày
27/10/2026, để ai pull về cũng chạy được demo mà không cần checkpoint gốc. Gói được dựng bằng
`python scripts/export_release.py --version demo-chinh-thuc-20261026` và tự kiểm mã băm từng
tệp khi API nạp. `.gitattributes` tắt đổi xuống dòng cho thư mục này để mã băm không lệch trên
Windows. Các release khác vẫn không commit.
