# MusicRec frontend (Next.js)

Giao diện demo chính của khóa luận. Chỉ gọi REST API của backend FastAPI; không chứa mô hình.

## Trang

| Đường dẫn | Nội dung |
| --- | --- |
| `/` | Giới thiệu, ba số liệu chính |
| `/nguoi-dung` | Người dùng có sẵn: lịch sử nghe, so sánh PureSVD và M1 cạnh nhau (số người nghe từng nghệ sĩ, trung bình, nghệ sĩ M1 thêm/bỏ), Implicit ALS |
| `/nguoi-moi` | Người dùng mới: tìm và chọn 1–5 nghệ sĩ, gợi ý bằng M2; hồ sơ rỗng dùng Popularity và báo fallback |
| `/luong` | Luồng hoạt động có hoạt ảnh, theo ba nhánh định tuyến |
| `/ket-qua` | Bảng kết quả test chính thức |

Số liệu tĩnh trong `src/data/results.json` do `python scripts/export_frontend_data.py` (ở thư mục gốc) sinh ra từ các tệp kết quả đã lưu. Không sửa tay tệp này.

## Chạy cục bộ

Gói mô hình `artifacts/releases/demo-chinh-thuc-20261026` đã có sẵn trong repo, nên pull về là chạy được. Lần đầu cài thư viện Python ở thư mục gốc: `pip install -e ".[dev]"`.

```bash
# Thư mục gốc: backend
uvicorn musicrec.api.main:app --port 8000
```

```bash
# Thư mục frontend/
npm install
npm run dev
```

Mở http://localhost:3000. Backend mặc định cho phép CORS từ `localhost` và `127.0.0.1` ở mọi cổng.

## Biến môi trường

| Biến | Nơi đặt | Ý nghĩa |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | Frontend (Vercel) | URL backend, mặc định `http://127.0.0.1:8000` |
| `MUSICREC_CORS_ORIGINS` | Backend | Origin ngoài máy cục bộ, cách nhau bằng dấu phẩy (domain Vercel khi deploy) |
| `MUSICREC_RELEASE_DIR` | Backend | Thư mục gói release, mặc định `artifacts/releases/demo-chinh-thuc-20261026` |

## Deploy (chưa thực hiện, cần người dùng cho phép)

Vercel: Root Directory là `frontend`, đặt `NEXT_PUBLIC_API_URL` trỏ tới backend. Backend chạy ở host Python, kèm gói release và `MUSICREC_CORS_ORIGINS` chứa domain Vercel.

## Kiểm tra

```bash
npm run lint
```

```bash
npm run build
```
