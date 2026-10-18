# Data card: HetRec / Last.fm

| Thuộc tính | Giá trị |
| --- | --- |
| Nguồn | https://files.grouplens.org/datasets/hetrec2011/hetrec2011-lastfm-2k.zip |
| Ngày tải | Chưa xác định |
| Ngày xác minh lại | 18-10-2026 |
| ZIP SHA-256 | `6738f48195667ff03caaab4d32ca9a3133d8cc026b7c3cdaf6ce1010e913c59c` |
| user_artists.dat SHA-256 | `001400dc3c7d2667fca6e4ea6dc6acc31a9dd28ad5cd0f74cea988c019934d3b` |
| Schema nguồn | `userID`, `artistID`, `weight` (count dương, hữu hạn) |
| Schema chuẩn | `user_id`, `item_id`, `listening_count`; đơn vị artist, không phải track |
| Kiểm tra thực tế | 1.892 user, 17.632 artist, 92.834 cặp; 0 cặp trùng, 0 count lỗi |
| Thông tin sử dụng trong README nguồn | Yêu cầu trích Last.fm, có trích dẫn HetRec 2011; không ghi nhận giấy phép chuẩn trong README đi kèm |
| Encoding | Tương tác/artist UTF-8; tên thẻ Latin-1, khai báo trong experiment config |

Không ghi ngày tải khi chưa có bằng chứng. Không có timestamp từng lượt nghe;
split là che giấu tương tác ngẫu nhiên, không đánh giá dự đoán tương lai.
Không áp ngưỡng listener artist; giữ user dưới 5 artist trong train. Mỗi run kiểm tra
checksum nguồn, bảo toàn dữ liệu và ghi cold target riêng. M2 có protocol user
holdout riêng, từ vựng/IDF chỉ học trên cặp reference được phép biết.
