# Nguồn và giấy phép

- Dataset: [GroupLens HetRec 2011](https://grouplens.org/datasets/hetrec-2011/),
  chỉ sử dụng phi thương mại theo README trong ZIP. Trích dẫn Last.fm; có thể
  trích dẫn Cantador, Brusilovsky, Kuflik, HetRec 2011. Không đưa dataset vào Git.
- AIProbS: Yue Deng / pitteryue, commit
  `051ab349c1bfe493cb5eabd3b6ec1fe0c3a3e0f2`, MIT. LICENSE nguyên bản được tải cùng
  mã và giữ nguyên trong cache nguồn. Chỉ chạy các định nghĩa đã xác minh checksum
  bằng harness; không nhập entrypoint tải dữ liệu/huấn luyện mặc định MovieLens.
- RecBole: RUCAIBox, phiên bản 1.1.1, giấy phép MIT. BPR là implementation của
  framework dựa trên Rendle et al. (2009). Số tham chiếu LastFM lấy từ báo cáo
  RecBole-GNN đã ghi trong tài liệu căn cứ, không lấy từ bài BPR 2009.

Các kernel sparse của dự án là bản cài lại được ghi nguồn Deng (2022); kiểm chứng
gồm ví dụ nhỏ bằng định nghĩa tác giả không đổi và full split bằng adapter cấp
phát đồ thị. Mã/weights/data tải ngoài không được tự động đưa vào package serving.
