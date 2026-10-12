# Data card: HetRec 2011 Last.fm 2K

| Thuộc tính | Giá trị |
|---|---|
| Nguồn | https://files.grouplens.org/datasets/hetrec2011/hetrec2011-lastfm-2k.zip |
| Ngày tải UTC | 2026-10-12T07:39:38.991656+00:00 |
| Phiên bản | 1.0, May 2011 |
| SHA-256 | `6738f48195667ff03caaab4d32ca9a3133d8cc026b7c3cdaf6ce1010e913c59c` |
| Kích thước ZIP | 2589075 byte |
| Đơn vị | user–artist; weight là số lượt nghe, phản hồi ngầm |
| Quy mô | 1.892 user; 17.632 artist; 92.834 cặp |
| Giấy phép | Phi thương mại; liên hệ Last.fm nếu dùng thương mại |
| Trích dẫn | Last.fm; Cantador, Brusilovsky, Kuflik, HetRec 2011 |
| Encoding | tags.dat CP1252; các bảng còn lại UTF-8 |

Schema raw: `userID`, `artistID`, `weight`. Giữ nguyên ZIP và số lượt nghe. Tái hiện dùng binary/no-filter và 30 split tác giả; giao thức khóa luận tách riêng.

Metadata có 444 pictureURL thiếu và 390 ID artist chỉ xuất hiện trong tag. Timestamp của tag không phải lịch sử nghe. Xem [nghiên cứu dữ liệu](research/dataset-study.md) và manifest/MLflow cục bộ để truy vết.
