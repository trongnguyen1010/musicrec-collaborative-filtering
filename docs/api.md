# API contract (v0)

| Endpoint | Mục đích |
| --- | --- |
| `GET /health` | Trạng thái dịch vụ và `model_version`. |
| `POST /recommend` | Nhận `user_id` hoặc history tạm và `k`; trả recommendation, score, reason, fallback. |
| `GET /users/{user_id}/history` | Lịch sử user đã biết; trả 404 khi không tồn tại. |
| `GET /metrics` | Metric offline của release đang chạy. |

`POST /recommend` phải từ chối request không có `user_id` lẫn history, `k <= 0`,
và history có trọng số không hợp lệ.
