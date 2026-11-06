# Quy tắc viết báo cáo khóa luận MusicRec

Tệp này dùng khi soạn, sửa và rà soát đề cương hoặc báo cáo khóa luận của đề tài 33. Báo cáo Word, đề cương và tài liệu ôn tập có mục đích riêng. Áp dụng phần quy tắc chung cho cả ba và chọn đúng mẫu cho từng loại tài liệu.

## 1. Chọn bản gốc và nguồn đối chiếu

- Đọc yêu cầu mới nhất của nhóm và nhận xét đã được GVHD xác nhận. Xác định trước tài liệu, mục cần sửa và các phần liên quan.
- Lấy bản đánh dấu **hiện hành** trong bảng phiên bản làm gốc khi cập nhật báo cáo. Giữ bố cục, văn phong và tên đề tài của bản đó. Khi cần sửa thông tin sai, đối chiếu với dữ liệu, mã nguồn hoặc nguồn gốc rồi giải thích thay đổi lúc bàn giao. [Bảng phiên bản](README.md)
- Dùng mẫu khoa cho định dạng báo cáo chính thức và hướng dẫn của GVHD cho trình tự nghiên cứu. Dùng đề cương đã chốt để đối chiếu mục tiêu và phạm vi. Nếu mẫu khoa và cách trình bày đang dùng khác nhau, ghi rõ điểm khác và chốt cách áp dụng trước khi đổi hàng loạt. [Mẫu khoa](../huong-dan-gvhd/Mau_bao_cao_KLTN.docx) · [Hướng dẫn GVHD](../huong-dan-gvhd/H%C6%B0%E1%BB%9Bng%20d%E1%BA%ABn%20t%E1%BB%ABng%20b%C6%B0%E1%BB%9Bc%20ho%C3%A0n%20th%C3%A0nh%20kh%C3%B3a%20lu%E1%BA%ADn.docx) · [Đề cương V2](../de-cuong/DeCuongChiTiet_KLTN_CaoTrongNguyen_LeKhacGiaKhang_v2_04-10-2026.docx)
- Đối chiếu thông tin triển khai với mã và gói phát hành tương ứng. Đối chiếu số liệu với hồ sơ lần chạy và tệp kết quả. Ghi chú dựng Word và các bản cũ giúp truy lại quyết định trình bày theo từng phiên bản. [Quy tắc dự án](../../DEVELOPMENT_RULES.md) · [Hồ sơ dữ liệu](../data-card.md) · [Hồ sơ kết quả](../results/)

## 2. Văn phong và thuật ngữ

- Viết tiếng Việt là chính, bằng lời của sinh viên đã đọc nguồn và hiểu cách nhóm thực hiện. Mỗi đoạn tập trung vào một ý. Ưu tiên câu có chủ thể, hành động và kết quả cụ thể. Dùng “nhóm” nhất quán trong phần trình bày nghiên cứu.
- Giải thích khái niệm bằng câu dễ đọc trước khi đưa công thức hoặc chi tiết cài đặt. Diễn giải bài báo theo câu hỏi, cách nghiên cứu, kết luận và phần nhóm vận dụng. Giữ nguyên tên tác giả, tên bài báo và các tên riêng cần tra cứu.
- Lần đầu dùng thuật ngữ, viết tiếng Việt trước rồi ghi tên tiếng Anh hoặc chữ viết tắt trong ngoặc khi cần. Những lần sau dùng một cách gọi đã chọn. Giải nghĩa chữ viết tắt trong tóm tắt nếu cần để tóm tắt đọc độc lập. Khi có hơn 10 chữ viết tắt, lập danh mục theo thứ tự chữ cái ở đầu báo cáo theo mẫu khoa.
- Giữ nguyên tên riêng, tên thuật toán và định danh cần đối chiếu với mã, ví dụ Last.fm, PureSVD, FastAPI và `artist_id`. Diễn giải vai trò của chúng bằng tiếng Việt. Trang Abstract và từ khóa tiếng Anh theo mẫu khoa.
- Đưa lịch thực hiện và thời điểm chạy vào hồ sơ kỹ thuật, bảng phiên bản hoặc phần tiến độ của đề cương. Trong nội dung chính, tập trung vào thiết kế, cách làm, bằng chứng và kết quả. Ngày công bố và ngày truy cập tài liệu ghi theo quy cách trích dẫn.
- Chọn động từ theo trạng thái có bằng chứng. Dùng “dự kiến” cho kế hoạch, “đã triển khai” cho chức năng có trong phiên bản được mô tả và “kết quả cho thấy” cho số liệu đã đo. Ghi trạng thái gửi hoặc duyệt của GVHD theo xác nhận của nhóm.

| Cách gọi ưu tiên | Tiếng Anh hoặc ký hiệu khi cần đối chiếu |
| --- | --- |
| Hệ thống khuyến nghị, lọc cộng tác | recommender system, collaborative filtering (CF) |
| Lọc cộng tác theo người dùng, theo nghệ sĩ | user-based CF (UserCF), item-based CF (ItemCF) |
| Phản hồi ngầm, phản hồi tường minh, số lượt nghe | implicit feedback, explicit feedback, listening count |
| Dữ liệu thưa, khởi động nguội, thiên lệch phổ biến | data sparsity, cold-start, popularity bias |
| Mô hình đối sánh, tập ứng viên, xếp hạng top-K | baseline, candidate set, top-K ranking |
| Tập huấn luyện, tập xác thực, tập kiểm thử | training set, validation set, test set |
| Tập nghệ sĩ liên quan dùng để đánh giá, lấy mẫu âm | ground truth, negative sampling |
| Tái xếp hạng, phân tích loại bỏ thành phần có kiểm soát | re-ranking, controlled ablation |
| Cơ chế dự phòng, bản mẫu, đầu vào và đầu ra | fallback, prototype, input và output |
| Độ bao phủ, độ mới, độ đa dạng trong danh sách | coverage, novelty, intra-list diversity (ILD) |
| Độ phổ biến trung bình của danh sách khuyến nghị | average recommendation popularity (ARP) |

## 3. Nội dung theo loại tài liệu và theo chương

- **Đề cương.** Nêu câu hỏi nghiên cứu, phương pháp dự kiến, tiêu chí đánh giá, phạm vi, sản phẩm và tiến độ. Giữ mẫu đề cương của GVHD nếu được chọn làm bản gốc. Phân biệt dữ liệu đã kiểm tra, thiết kế đã chốt và phần đang đề xuất.
- **Tóm tắt báo cáo.** Trình bày bài toán, dữ liệu, phương pháp, kết quả chính đã xác minh và kết luận trong phạm vi nghiên cứu. Đồng bộ số liệu, thuật ngữ và kết luận giữa hai bản tiếng Việt và tiếng Anh.
- **Chương 1.** Nêu bối cảnh, lý do chọn đề tài, vấn đề cần giải quyết, mục tiêu, câu hỏi nghiên cứu và phạm vi. Xác định đầu vào, đầu ra và đơn vị khuyến nghị. Giữ các tuyên bố về đóng góp tương ứng với những gì báo cáo chứng minh.
- **Chương 2.** Mỗi mục giải thích một khái niệm hoặc một nhóm phương pháp. Nêu công thức và giả định khi cần. Với bài liên quan, giải thích bài dùng dữ liệu nào, tìm thấy gì và nhóm vận dụng phần nào. Chi tiết quy trình riêng của MusicRec đặt ở chương phương pháp.
- **Chương 3.** Trình bày dữ liệu, tiền xử lý, cách chia tập, biểu diễn đầu vào, mô hình và giao thức đánh giá. Mô tả đủ để lần theo cách cài đặt hoặc chạy lại. Nêu cách chọn ngưỡng, tham số, tập ứng viên và quy tắc loại nghệ sĩ đã nghe. Phân biệt các bước học từ dữ liệu và các bước dùng để đánh giá.
- **Chương 4.** Mô tả môi trường, cấu hình, đối chứng và tiêu chí chọn mô hình. Trình bày kết quả theo câu hỏi nghiên cứu, giải thích độ lớn chênh lệch, sự đánh đổi và giới hạn. Đưa các bảng đầy đủ, cấu hình dài và kiểm tra bổ sung xuống phụ lục khi phù hợp.
- **Chương 5.** Mô tả kiến trúc và luồng sử dụng của phiên bản hệ thống được bàn giao. Nêu giao diện, API, cách nạp mô hình, xử lý đầu vào và kết quả kiểm thử theo bằng chứng thực tế. Chốt mức đạt của từng mục tiêu, hạn chế và hướng phát triển. Dùng ảnh đúng phiên bản và ghi điều kiện đo nếu báo cáo thời gian phản hồi.
- **Tài liệu ôn tập và seminar.** Giữ số tham chiếu theo phiên bản báo cáo đang dùng để tra cứu. Có thể thêm ví dụ tính tay, câu hỏi bảo vệ và gợi ý trả lời. Ghi tên phiên bản nguồn để tránh nhầm khi thứ tự trích dẫn thay đổi.

## 4. Trích dẫn và liêm chính học thuật

- Đặt trích dẫn sát nhận định cần nguồn. Mở bài gốc hoặc tài liệu chính thức và kiểm tra tác giả, năm, tiêu đề, nơi công bố, DOI hoặc URL. Ghi rõ bản thảo công bố trước (preprint) nếu đang dùng bản đó.
- Với lý thuyết nền tảng, giữ nguồn gốc phù hợp. Với so sánh thực nghiệm hoặc quyết định mới, ưu tiên công trình gần đây có dữ liệu, giao thức và chỉ số phù hợp. Khi dẫn kết quả từ công trình khác, ghi rõ dữ liệu, nhiệm vụ và điều kiện so sánh.
- Tách đóng góp của tác giả bài báo khỏi cách nhóm hiện thực hoặc điều chỉnh. Ghi nguồn dưới hình, bảng hoặc sơ đồ lấy từ nguồn khác hoặc được vẽ lại từ nguồn đó. Giữ nguyên tên tài liệu trong ngôn ngữ gốc ở danh mục.
- Kiểm tra trích dẫn hai chiều. Mọi số trong thân bài phải trỏ đến đúng tài liệu. Mỗi mục trong danh mục phải có chỗ sử dụng hoặc lý do xuất hiện theo yêu cầu của khoa. Rà lại liên kết và đánh số sau khi thêm, bỏ hoặc di chuyển nguồn.
- Khi cập nhật cục bộ, giữ hệ `[n]` và thứ tự của bản hiện hành. Cách sắp xếp danh mục cho bản nộp chính thức được theo dõi ở mục 8.

## 5. Công thức, dữ liệu và kết quả thực nghiệm

- Dùng Equation của Word ở định dạng chỉnh sửa được (OMML). Dùng cấu trúc toán học thật cho phân số, căn, tổng, véc-tơ, ma trận, chỉ số trên/dưới và chuyển vị. Công thức hiển thị đúng ký hiệu trong Word và trong bản xuất để kiểm tra. LaTeX có thể dùng làm đầu vào soạn thảo, sau đó chuyển thành công thức Word.
- Định nghĩa biến, tập chỉ số và ý nghĩa của điểm số ở gần công thức. Khi đổi ký hiệu, cập nhật đồng thời phương trình, bảng ký hiệu, nội dung giải thích và chỗ dẫn lại. Với PureSVD, dùng `R` cho ma trận và `r_u` cho hàng tương tác của người dùng `u` theo quy ước hiện hành.
- Giữ đúng đơn vị phân tích. Một bản ghi người dùng–nghệ sĩ trong bảng tương tác chứa số lượt nghe tổng hợp của cặp đó. Phân biệt số bản ghi, số lượt nghe và số nghệ sĩ. Trường hợp chưa quan sát là thiếu bằng chứng về sở thích. Nếu thuật toán gán 0 hoặc lấy mẫu âm, nêu rõ đây là quy ước trong giao thức.
- Phân biệt SVD có độ lệch học bằng SGD, PureSVD và ALS cho phản hồi ngầm. Nêu thang và nguồn của điểm khi báo cáo RMSE. Điểm đại diện suy ra từ lượt nghe cần ghi rõ cách tạo và dữ liệu dùng để xác định ngưỡng.
- Mỗi kết quả thực nghiệm phải truy được đến lần chạy, mã hoặc commit, mã băm dữ liệu, cấu hình, seed, giao thức và tệp kết quả. Ghi “chưa đo” hoặc “chưa có số liệu” nếu chưa có phép đo được xác minh. Ví dụ giả lập ghi rõ “minh họa”. [Quy tắc truy vết](../../DEVELOPMENT_RULES.md#dữ-liệu-và-báo-cáo) · [Hồ sơ kết quả](../results/)
- Dùng tập xác thực để chọn cấu hình và khóa cấu hình trước khi chấm tập kiểm thử. So sánh mô hình trên cùng phép chia, tập ứng viên và bộ đánh giá trong từng giao thức. Ghi rõ điều kiện khác biệt khi trình bày các giao thức riêng hoặc lần chạy mở rộng.
- Khi đọc một bảng, người đọc cần biết chỉ số, giá trị K nếu có, tập dữ liệu, nhóm người dùng, số mẫu thực sự được tính, đối chứng và chiều diễn giải. Phân biệt tỷ lệ thay đổi tương đối với chênh lệch theo điểm phần trăm. Tính chênh lệch từ giá trị gốc rồi làm tròn khi trình bày.
- Báo cáo cả độ chính xác xếp hạng, độ bao phủ, độ đa dạng, mức phổ biến và chi phí suy luận khi chúng liên quan đến câu hỏi nghiên cứu. Nêu chênh lệch, khoảng tin cậy và phép kiểm định khi có. Giữ các kết quả âm và phân biệt ý nghĩa thống kê với ý nghĩa thực tiễn. Kết luận về mức phổ biến hoặc độ đa dạng cần phù hợp với phạm vi của chỉ số đã đo.

## 6. Định dạng và kiểm tra Word

- Báo cáo chính thức gồm bìa, các trang đầu, nội dung, tài liệu tham khảo và phụ lục trong một tệp `.docx`. Giữ các thành phần, logo, đầu trang, chân trang và cách đánh số trang theo mẫu được chọn. Dùng số Ả Rập từ trang 1 của phần nội dung. Phụ lục theo mẫu khoa không hiển thị số trang.
- Báo cáo theo mẫu khoa dùng A4, lề trên và dưới 3 cm, trái 3,5 cm, phải 2 cm. Thân bài Times New Roman 13 pt, căn đều, giãn dòng 1,5, khoảng cách trước đoạn 10 pt và sau đoạn 0 pt. Tên chương 14 pt, in hoa và đậm. Các cấp tiểu mục dùng kiểu Heading tương ứng của mẫu. Mục lục hiển thị đến cấp ba. Đề cương V2 dùng mẫu riêng với lề trái 3 cm, ba lề còn lại 2 cm. [Mẫu khoa](../huong-dan-gvhd/Mau_bao_cao_KLTN.docx) · [Đề cương V2](../de-cuong/DeCuongChiTiet_KLTN_CaoTrongNguyen_LeKhacGiaKhang_v2_04-10-2026.docx)
- Dùng chú thích tự động của Word cho bảng và hình. Tên bảng đặt phía trên và tên hình phía dưới, căn giữa, cùng cỡ chữ với thân bài theo mẫu khoa. Kiểm tra cả chữ và số do trường tự động sinh ra. Đánh số theo chương. Số công thức đặt trong ngoặc và căn phải theo mẫu.
- Dẫn mỗi bảng và hình trong đoạn văn liên quan. Ghi đơn vị, tên trục, ý nghĩa ký hiệu và nguồn khi cần. Giữ hình cùng chú thích. Bảng dài qua trang lặp hàng tiêu đề. Điều chỉnh độ rộng cột hoặc cách trình bày để số, ký hiệu và văn bản đọc được.
- Cập nhật toàn bộ trường Word sau khi chốt nội dung. So tiêu đề và số trang trong mục lục với thân bài, so danh mục với chú thích thực tế, rồi kiểm tra tham chiếu chéo và số thứ tự. Xuất bản kiểm tra và xem đủ các trang để phát hiện bảng tràn, hình mờ, mất ký hiệu, ngắt trang hoặc đầu/chân trang sai.

## 7. Quản lý phiên bản và bàn giao

1. Cập nhật Word khi nhóm yêu cầu rõ ràng. Mở bản hiện hành trong [bảng phiên bản](README.md), kiểm tra phạm vi và đối chiếu bằng chứng trước khi sửa. Khi có số liệu mới, lưu bằng chứng trong hồ sơ kết quả theo [quy tắc dự án](../../DEVELOPMENT_RULES.md#lưu-phiên-bản-báo-cáo-khóa-luận).
2. Xuất một bản báo cáo đầy đủ mới trong thư mục này. Dùng tên `33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_vNN_DD-MM-YYYY.docx`, tăng `vNN` lên 1 và dùng ngày tạo theo giờ Việt Nam như quy ước dự án. Hai bản cùng ngày được phân biệt bằng số phiên bản.
3. Giữ các bản trước và tệp nguồn. Để bản nháp, PDF kiểm tra và ảnh kiểm tra ngoài thư mục bàn giao. Kiểm tra mã băm bản nguồn sau khi xuất bản mới.
4. Thêm một dòng vào README với phiên bản, ngày, tệp, người sửa, nội dung thay đổi và trạng thái gửi GVHD. Cập nhật dấu **hiện hành**. Khi chưa có xác nhận về người sửa của một bản cũ, để trống hoặc ghi “chưa ghi nhận”.
5. Bàn giao liên kết đến bản Word mới trong chat, tóm tắt nội dung đã sửa và nêu phần cần bổ sung hoặc xác nhận. Nhóm quyết định lúc gửi báo cáo cho GVHD.

### Danh sách kiểm tra trước bàn giao

- [ ] Đúng bản gốc, đúng yêu cầu, đúng mẫu và đúng phạm vi thay đổi.
- [ ] Tóm tắt, mục tiêu, tên mô hình, phương pháp, kết quả và kết luận nhất quán giữa các chương liên quan.
- [ ] Số liệu, cỡ mẫu, chỉ số và kết luận kiểm định khớp tệp nguồn. Phần chưa đo và ví dụ minh họa có nhãn rõ ràng.
- [ ] Trích dẫn, danh mục, hình, bảng, công thức và phụ lục được đối chiếu hai chiều.
- [ ] Mục lục và các trường Word đã làm mới. Đã xem các trang sau khi xuất để kiểm tra định dạng.
- [ ] Tên tệp, mã băm bản nguồn và lịch sử phiên bản đã được kiểm tra.

## 8. Bổ sung và sửa quy tắc về sau

Khi nhóm hoặc GVHD chốt quy tắc mới, cập nhật mục liên quan trong tệp này và ghi một dòng ở lịch sử bên dưới. Ghi ngày, quyết định, phạm vi áp dụng và nguồn hoặc lý do. Nếu quyết định ảnh hưởng các bản đã giao, ghi phiên bản bắt đầu áp dụng và xác định phần cần đồng bộ. Dùng mục chờ chốt cho những lựa chọn đang thảo luận.

| Điểm chờ chốt | Cách xử lý trong lúc chờ |
| --- | --- |
| Sắp xếp danh mục bản nộp theo thứ tự xuất hiện hay theo nhóm ngôn ngữ và tên tác giả như mẫu khoa | Giữ thứ tự hiện hành khi sửa cục bộ. Khi có quyết định, đồng bộ danh mục và số `[n]` trong thân bài. |
| Dấu thập phân và số chữ số theo từng chỉ số | Theo cách trình bày của bản hiện hành trong từng nhóm bảng. Giữ đủ độ chính xác để thấy chênh lệch có ý nghĩa và ghi cách làm tròn nếu cần. |

### Lịch sử quy tắc

| Ngày | Thay đổi | Phạm vi và căn cứ |
| --- | --- | --- |
| 06/11/2026 | Tập hợp quy tắc văn phong, thuật ngữ, công thức, trích dẫn, thực nghiệm, định dạng và bàn giao. Thêm danh sách kiểm tra và mục chờ chốt. | Đề cương V2, lịch sử báo cáo v01–v16, mẫu khoa, hướng dẫn GVHD, ghi chú dựng các bản ngày 04/10 và quy tắc dự án. |
