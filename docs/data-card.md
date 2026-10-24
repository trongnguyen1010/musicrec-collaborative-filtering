# Data card HetRec 2011 Last.fm 2K

## Trạng thái sau Bước 4 ngày 24/10/2026

Đã hoàn thành kiểm tra nguồn, EDA, làm sạch và Bước 4 chia tập/ánh xạ theo yêu cầu người dùng. **Train có 74.275 cặp; validation và test mỗi tập 9.263 cặp; mapping gồm 1.877 user và 15.398 artist từ train.** Chưa biến đổi count, học đặc trưng, huấn luyện hoặc tính chỉ số chất lượng trên test. Đang dừng giải thích Bước 4; các phần Bước 1–3 giữ bối cảnh lịch sử, kết quả mới nhất ở mục Bước 4 cuối tệp.

Bằng chứng máy đọc được: [source_audit.json](../outputs/runs/source_audit_20261019_162917_245445/source_audit.json). Tệp ghi thời điểm, phiên bản mã, tình trạng thay đổi chưa commit, cách đọc, từng kiểm tra và mã băm. Dùng Python standard library để đọc/kiểm tra trực tiếp, không thêm pipeline hoặc thư viện mới. Không có thao tác ngẫu nhiên nên seed không áp dụng.

## Nguồn và phạm vi xác minh

| Thuộc tính | Kết quả |
| --- | --- |
| Bộ dữ liệu | HetRec 2011 Last.fm 2K; không phải LFM-1b, Last.fm 1K/360K hoặc Music4All-Onion. |
| Trang phát hành | [GroupLens HetRec 2011](https://grouplens.org/datasets/hetrec-2011/), đã mở đối chiếu trong Bước 1. |
| ZIP được trang nguồn liên kết | [hetrec2011-lastfm-2k.zip](https://files.grouplens.org/datasets/hetrec2011/hetrec2011-lastfm-2k.zip). |
| ZIP cục bộ | data/raw/hetrec2011-lastfm-2k.zip; 2.589.075 byte. |
| Phiên bản | README trong ZIP ghi Version 1.0, May 2011. |
| Ngày tải lần đầu | Chưa xác minh; không dùng ngày sửa/tạo tệp hoặc ngày kiểm tra làm ngày tải. |
| Ngày kiểm tra lại | 19/10/2026, múi giờ Việt Nam; thời điểm đầy đủ trong JSON. |
| Điều kiện sử dụng | README cho phép phi thương mại; ghi nhận Last.fm và có thể trích dẫn Cantador, Brusilovsky, Kuflik, HetRec 2011. Không tự gán MIT/CC-BY. |
| Đơn vị quan sát | Một cặp người dùng–nghệ sĩ với số lượt nghe tổng hợp, không phải một lần phát hoặc quan hệ người dùng–bài hát. |

Mã băm ZIP trùng bản ghi seminar đã có; kiểm tra CRC nội bộ ZIP không phát hiện thành viên lỗi. Cả bảy tệp đã giải nén khớp từng byte với thành viên tương ứng trong ZIP. Tám tệp nguồn gồm ZIP và bảy tệp giải nén giữ nguyên sau kiểm tra.

Giới hạn xác minh: không tải lại ZIP từ mạng trong lượt này và chưa đối chiếu SHA-256 do nhà phát hành công bố. Vì vậy, kết quả chứng minh sự nhất quán với ZIP và bản ghi cục bộ trước đây, không phải bằng chứng độc lập rằng nhà phát hành đã xác nhận từng byte.

## Kiểm kê tệp và schema

Các tệp .dat có header, phân cách bằng TAB; kiểm tra từng dòng cho thấy số trường khớp header. Khi kiểm tra dùng tách TAB theo nghĩa đen, không tự coi dấu ngoặc kép trong văn bản là ký hiệu trích dẫn CSV.

| Tệp trong data/raw/hetrec2011/ | Dòng dữ liệu không tính header | Cột | Cách đọc đã kiểm tra |
| --- | ---: | --- | --- |
| artists.dat | 17.632 | id, name, url, pictureURL | UTF-8 strict hợp lệ; 4 trường/dòng. |
| user_artists.dat | 92.834 | userID, artistID, weight | UTF-8 strict hợp lệ; 3 trường/dòng. |
| tags.dat | 11.946 | tagID, tagValue | Không hợp lệ UTF-8 toàn tệp; 2 trường/dòng trong bản đọc bảo toàn byte. |
| user_taggedartists.dat | 186.479 | userID, artistID, tagID, day, month, year | UTF-8 strict hợp lệ; 6 trường/dòng. |
| user_taggedartists-timestamps.dat | 186.479 | userID, artistID, tagID, timestamp | UTF-8 strict hợp lệ; 4 trường/dòng. |
| user_friends.dat | 25.434 | userID, friendID | UTF-8 strict hợp lệ; 2 trường/dòng. |
| readme.txt | Không áp dụng | Mô tả nguồn, phiên bản, schema, giấy phép | Không hợp lệ UTF-8 toàn tệp; đọc bản bảo toàn byte để đối chiếu nội dung. |

Các cột ID, weight và trường thời gian đọc được như số nguyên signed int64 ở mọi dòng; không có lỗi chuyển kiểu trong kiểm tra này. name, url, pictureURL, tagValue là văn bản. Đây là kiểm tra kiểu, **chưa kết luận count đều dương, tên đầy đủ, dữ liệu không trùng hoặc nội dung thẻ đã đúng encoding**; các nội dung đó thuộc EDA.

ID dù ghi bằng số vẫn là nhãn định danh, không phải đại lượng để lấy trung bình hoặc so mức độ yêu thích. Hai bảng danh mục có id nghệ sĩ và tagID duy nhất. Bảng tương tác có 1.892 mã người dùng và 17.632 mã nghệ sĩ phân biệt; số dòng 92.834 khớp README. Chưa kiểm tra trùng cặp người dùng–nghệ sĩ ở Bước 1.

### Encoding cần lưu ý

- artists.dat và bốn tệp quan hệ còn lại đọc được UTF-8 strict.
- tags.dat: lỗi UTF-8 đầu tiên ở byte offset 51.083 (đếm từ 0), dòng 2.815 (đếm từ 1); dòng này có tagID 2863. Bản xem Latin-1 cho chuỗi tropicália.
- readme.txt: lỗi đầu tiên ở byte offset 4.354, trong phần tên tác giả.
- Latin-1 được dùng để ánh xạ byte sang ký tự phục vụ kiểm tra cấu trúc, **không phải khẳng định mọi chuỗi trong tệp đều dùng cùng encoding**.
- Không dùng errors=ignore hoặc errors=replace, không bỏ dòng, ghi lại tệp hay chuẩn hóa thẻ. Cách đọc văn bản phục vụ EDA/M2 phải được kiểm tra riêng; dùng UTF-8 mặc định cho mọi tệp có thể làm bước nạp lỗi.

## Khóa nối và cách dùng bảng

| Quan hệ được kiểm tra | Kết quả | Ý nghĩa |
| --- | --- | --- |
| user_artists.artistID → artists.id | 0 dòng không nối được. | Mọi nghệ sĩ trong tương tác chính có mã trong danh mục. Chưa khẳng định mọi tên/URL đều đầy đủ hoặc hoạt động. |
| user_taggedartists.artistID → artists.id | 1.538 dòng không nối được, thuộc 390 mã. | Gán thẻ có nghệ sĩ ngoài danh mục hiện có; giữ nguyên để EDA và quyết định xử lý sau. |
| user_taggedartists.tagID → tags.tagID | 0 dòng không nối được. | Mã thẻ có trong từ điển; chưa chứng minh chất lượng văn bản thẻ. |
| user_taggedartists.userID → tập userID của user_artists | 0 dòng ngoài tập. | Các user gán thẻ đều có trong bảng tương tác chính. |
| Bản timestamp: artistID, tagID, userID | Kết quả tương ứng giống bản ngày/tháng/năm. | Không phải một tập gán thẻ độc lập. |
| user_friends.userID và friendID → tập userID của user_artists | 0 dòng ngoài tập ở cả hai cột. | Hai đầu quan hệ đều thuộc tập người dùng quan sát. Bảng bạn bè chưa dùng trong baseline. |

Không có tệp users.dat chứa hồ sơ người dùng riêng; phép đối chiếu user ở đây dùng tập ID quan sát trong user_artists.dat, không giả định có bảng danh mục người dùng khác.

Hai bản user_taggedartists có cùng 186.479 dòng và cùng bộ userID–artistID–tagID ở từng vị trí. Dùng một cách biểu diễn cho một mục đích; **không cộng hoặc ghép dọc hai bản thành 372.958 lượt gán thẻ**. Tương tự, không cộng 1.538 dòng không nối được ở hai bản để tuyên bố có 3.076 quan sát khác nhau.

Ví dụ mã nghệ sĩ không nối được: dòng 241 của cả hai bản gán thẻ dùng artistID 14103. Điều này chỉ có nghĩa mã đó không có trong artists.dat đang dùng, không chứng minh nghệ sĩ không tồn tại trên Last.fm. Chưa xóa hoặc tự bổ sung nghệ sĩ.

### Ví dụ đã nối từ dữ liệu thật

- user_artists có dòng 2, 51, 13883. Nối artistID 51 với artists.id được tên Duran Duran: người dùng 2 có số lượt nghe tổng hợp 13.883 đối với nghệ sĩ này.
- Dòng gán thẻ đầu tiên có userID 2, artistID 52, tagID 13, ngày 1/4/2009; nối được Morcheeba và thẻ chillout. Đây là gán thẻ, không phải bằng chứng một lượt nghe vào ngày đó.
- Bản timestamp của cùng dòng chứa 1238536800000. Khi diễn giải như Unix milliseconds, giá trị là 31/03/2009 22:00 UTC, khác ngày lịch trong bản song song. README không chỉ rõ múi giờ; không tự ép ngày về UTC, suy đoán múi giờ nguồn hoặc dựng dòng thời gian nghe từ trường này.

## Mã băm SHA-256 của đầu vào đã kiểm tra

| Tệp | SHA-256 |
| --- | --- |
| hetrec2011-lastfm-2k.zip | 6738f48195667ff03caaab4d32ca9a3133d8cc026b7c3cdaf6ce1010e913c59c |
| artists.dat | c173881362c6b28551368fecb3c0be5a6a30a6cd859e1f5775413dfe46d48648 |
| readme.txt | 6fe5d1e6f67b025fc50cd70883dd1a1ff16c5ff37b5b7abfb33644b83468b209 |
| tags.dat | e95175f259be4c0c47644ae23d66131cd6d5767142a1405000e79f5584691d70 |
| user_artists.dat | 001400dc3c7d2667fca6e4ea6dc6acc31a9dd28ad5cd0f74cea988c019934d3b |
| user_friends.dat | 9a3a8f7fa5f5ec832335e5b58ed69a4cf27c6f6f6afcde62134810eea46445a7 |
| user_taggedartists-timestamps.dat | ec753318e453b15356853674b687da44d9f8c7e1215e1e0ff27aaa5f52e322bd |
| user_taggedartists.dat | d31fe938fcfeed6f0059f37a36b156f63674d073fc2553e5cc9dc1595e365bc7 |

Mã băm giúp nhận ra đầu vào có bị thay đổi giữa các lần chạy hay không. Khớp hash không có nghĩa dữ liệu sạch, đại diện thị trường hiện tại hoặc không có sai sót nội dung.

## Đối chiếu báo cáo sau Bước 1 và cấu hình hiện có

Đã đọc lại các phần 3.4, 3.5, 5.5, 5.7 và 5.8 của báo cáo V1. Báo cáo phân biệt đúng nghệ sĩ, lượt nghe tổng hợp và thời điểm gán thẻ; các kiểm tra EDA/mã không nối được vẫn được trình bày là việc cần làm. Không thấy khẳng định toàn bộ tệp là UTF-8 hoặc mọi gán thẻ đều nối danh mục thành công. Vì chưa đổi phương pháp và chưa có kết quả sau xử lý, **chưa cần xuất một bản Word mới ngay ở Bước 1**. Sẽ bổ sung chi tiết encoding, quan hệ thẻ và số lượng trước/sau khi có bằng chứng EDA/làm sạch cần đồng bộ; không ghi đè V1.

configs/dataset.yaml vẫn còn URL/checksum TODO và min_item_interactions = 5 của bộ khung. Đã ghi nhận nhưng không sửa hoặc chạy cấu hình ở bước kiểm tra nguồn; ngưỡng này không phải quy tắc hiện hành. Trước triển khai làm sạch phải đồng bộ theo kế hoạch, không âm thầm lọc nghệ sĩ đuôi dài.

## Kết quả EDA Bước 2

Bằng chứng chính: [metrics.json](../outputs/runs/raw_eda_20261019_verified/metrics.json), [bảng kết quả](../outputs/runs/raw_eda_20261019_verified/tables/), [năm biểu đồ](../outputs/runs/raw_eda_20261019_verified/figures/) và [kiểm tra chéo](../outputs/runs/raw_eda_20261019_verified/verification.json). Mã chạy lại ở [scripts/eda.py](../scripts/eda.py); một bản chụp mã đúng lần chạy được giữ trong run. Lần chạy ban đầu và lần xác minh cho các thống kê giống nhau; không chọn kết quả theo chất lượng mô hình.

| Nội dung | Kết quả đo trên dữ liệu gốc | Diễn giải |
| --- | --- | --- |
| Tương tác, user, artist | 92.834 cặp; 1.892 user; 17.632 artist | Chưa lọc hay chia tập. |
| Thiếu ID/weight, count không hữu hạn hoặc không dương | 0 | Các kiểm tra chính không phát hiện lỗi; không có nghĩa dữ liệu đại diện mọi hành vi. |
| Dòng trùng, cặp trùng, cặp count mâu thuẫn | 0 / 0 / 0 | Không có cơ sở tự cộng lượt nghe. |
| Độ thưa | 99,7217% trên 33.359.744 vị trí | Dựa trên cặp phân biệt, không phải lấy tổng lượt nghe chia số ô. |
| Tổng lượt nghe | 69.183.975 | Khác 92.834 cặp tương tác. |
| Count: min / trung vị / trung bình / max | 1 / 260 / 745,24 / 352.698 | Trung bình bị kéo lên bởi phần đuôi lớn; chưa cắt ngoại lai. |
| Count: phân vị 95% / 99% | 2.328 / 7.228,01 | Nội suy tuyến tính; không phải các ngưỡng được chọn để lọc. |
| Lịch sử user: min / trung vị / max | 1 / 50 / 50 nghệ sĩ | Nguồn là lịch sử quan sát tổng hợp; không suy ra tổng sở thích ngoài đời. |
| User đúng 50 nghệ sĩ | 1.829/1.892 (96,67%) | Tứ phân vị độ dài lịch sử có thể trùng, cần lưu ý khi phân nhóm sau split. |
| User dưới 5 nghệ sĩ | 15 user, 33 cặp | Tác động dự kiến của ngưỡng user tối thiểu; chưa áp dụng. |
| Artist chỉ có một người nghe | 10.679 (60,57% danh mục) | Khó ước lượng đồng nghe ổn định. |
| Artist dưới 5 người nghe | 14.804 (83,96%), chứa 21.408 cặp (23,06%) | Lọc ngưỡng này sẽ loại phần lớn danh mục đuôi dài; không đề xuất áp dụng. |
| Khoảng 20% artist nhiều người nghe nhất | 3.527 artist, chứa 79,94% cặp | Tập trung theo số người nghe, không phải tổng lượt phát. |
| Artist có / chưa có thẻ | 12.133 (68,81%) / 5.499 (31,19%) | M2 cần đường xử lý thiếu nội dung. |
| Cặp tương tác có artist mang thẻ | 86.608 (93,29%) | Mẫu số khác độ phủ danh mục; nghệ sĩ có thẻ xuất hiện trong nhiều tương tác hơn. |
| Gán thẻ nối / không nối danh mục | 184.941 / 1.538 dòng; phần không nối thuộc 390 mã | Chỉ thống kê bản ngày tháng, không cộng đôi bản timestamp. |
| Thẻ dùng trong danh mục, thẻ chỉ gắn một artist | 9.718 / 5.506 | Thẻ hiếm nhiều; chưa chuẩn hóa từ vựng hoặc tạo TF–IDF. |
| Tên nghệ sĩ trống / URL ảnh trống | 0 / 444 | Ảnh là metadata hiển thị, không tự loại tương tác; chưa thử tải URL. |
| Văn bản thẻ không hợp lệ UTF-8 | 8 giá trị | Chưa đổi encoding hoặc thay ký tự nguồn; các phép nối thẻ dùng ID. |

Các tệp .dat không có dòng trùng hoàn toàn trong kiểm tra đã chạy. Thiếu được định nghĩa là trường rỗng hoặc chỉ có khoảng trắng; giữ nguyên chuỗi văn bản như NA thay vì tự coi là null. Thống kê được thực hiện bằng bản đọc trong bộ nhớ; các phép nhóm/nối chỉ phục vụ chẩn đoán, không xuất một tập tương tác đã làm sạch.

Biểu đồ count dùng trục log để hiển thị dải rộng; chưa biến đổi dữ liệu đưa vào mô hình. Không thể kết luận log là biểu diễn tốt nhất chỉ từ histogram. Độ phủ thẻ hiện dùng toàn snapshot; sau khi chỉ giữ đóng góp được phép của nhóm học M2 phải tính lại, không dùng trực tiếp thống kê này làm đặc trưng train.

### Đề xuất cho Bước 3 chưa thực hiện

Giữ quy tắc xác minh ID/count và trùng đã có, dự kiến giữ user có ít nhất năm nghệ sĩ; không lọc thêm artist theo số người nghe và không cắt count lớn chỉ vì nằm ở đuôi phân bố. Tách gán thẻ không nối danh mục khỏi phần sẽ dùng xây nội dung và ghi rõ số lượng khi đến bước xử lý; giữ nguồn nguyên vẹn. Việc đọc/chuẩn hóa văn bản thẻ cần nêu rõ, không bỏ ký tự lỗi âm thầm. Đây là đề xuất, không xác nhận đã làm sạch.

### Đồng bộ báo cáo sau Bước 2

Đã tạo bản khóa luận đầy đủ [V2 ngày 19/10/2026](reports/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_19-10-2026.docx) để người dùng đọc và tự gửi GVHD. Bổ sung kết quả EDA vào Chương 3–4, một bảng và ba hình; đồng bộ tóm tắt Việt/Anh, trạng thái ở Chương 1 và Chương 5, cùng kế hoạch trong phụ lục. Các bảng chất lượng mô hình vẫn chờ chạy, không điền số dự kiến. Đã cập nhật mục lục, danh mục bảng/hình bằng Word và kiểm tra bản dựng 97 trang. Báo cáo V1 giữ nguyên mã băm; không khẳng định V2 đã được gửi hoặc được GVHD duyệt. Ngày 20/10/2026 chỉ đổi tên hai bản Word theo số đề tài 33 và quy tắc tên mới, không sửa nội dung.

## Điểm dừng và các việc còn lại

- Bước 1 đã được giải thích; người dùng đã cho phép thực hiện Bước 2.
- Bước 2 đã có bảng/hình và kiểm tra chéo; người dùng đã cho phép Bước 3 ngày 21/10/2026.
- Bước 3 đã làm sạch và kiểm tra chéo độc lập; giải thích kết quả trước khi chuyển bước. Không tự cộng count khác nhau của cặp trùng và không lọc artist theo số người nghe.
- Bước 4–5: chỉ sau các bước trước mới tạo split/mapping, biến đổi và ngưỡng học từ train.
- M2: chỉ khi đến bước, xây thẻ theo đóng góp được phép của nhóm học, tránh rò rỉ từ user đánh giá.

Dữ liệu này phục vụ khuyến nghị nghệ sĩ từ phản hồi ngầm. Không coi chưa quan sát là không thích, lượt nghe là sao đánh giá, hoặc timestamp thẻ là timestamp nghe. Kết quả sau này trên benchmark không tự đại diện người nghe Việt Nam hiện nay hoặc chứng minh gợi ý đúng từng bài hát.

## Bước 3: đối chiếu nguồn và làm sạch ngày 21/10/2026

Đã tải lại ZIP qua liên kết GroupLens: trùng từng byte với ZIP đang dùng, cả bảy tệp giải nén cũng khớp. Bản phát hành chính thức có đúng 1.538 dòng thẻ ngoài danh mục và tám giá trị thẻ không hợp lệ UTF-8; không phải lỗi tải/giải nén cục bộ. Bằng chứng: [kiểm tra nguồn](../outputs/runs/source_recheck_20261021_064216_805830/verification.json), [đối chiếu mã tác giả](../outputs/runs/source_recheck_20261021_064216_805830/literature_source_checks.json).

`tags.dat` có 11.938 giá trị ASCII và tám giá trị ngoài ASCII; không có giá trị ngoài ASCII nào hợp lệ UTF-8. Latin-1 cho các chuỗi như español, rock français, tropicália; chọn cách đọc này theo byte thực tế và [notebook CoLaKG](https://github.com/ziqiangcui/CoLaKG-SIGIR25/blob/main/data_preprocess/lastfm-2k.ipynb). Các bảng còn lại đọc UTF-8. Không thay byte nguồn, không bỏ ký tự, không chuẩn hóa từ vựng.

Logic ở [cleaning.py](../src/musicrec/data/cleaning.py), CLI [preprocess.py](../scripts/preprocess.py), quy tắc trong [dataset.yaml](../configs/dataset.yaml). Mã đọc TAB theo nghĩa đen, giữ chuỗi NA, đòi ID nguyên dương và count nguyên dương trong int64. Loại theo thứ tự: ID sai → count sai → artist ngoài danh mục → cùng quan sát lặp → user dưới năm artist phân biệt. Cặp hợp lệ có count mâu thuẫn làm dừng quy trình, không cộng. Chỉ xuất sang thư mục chưa tồn tại; không tạo mapping, log-count, split hoặc đặc trưng M2.

| Đại lượng | Trước | Sau / xử lý |
| --- | ---: | ---: |
| Người dùng có tương tác | 1.892 | 1.877 |
| Cặp tương tác | 92.834 | 92.801 |
| Artist xuất hiện trong tương tác | 17.632 | 17.617 |
| Artist trong danh mục giữ lại | 17.632 | 17.632 |
| Tổng lượt nghe | 69.183.975 | 69.138.727 |
| Count lớn nhất giữ lại | 352.698 | 352.698 |
| ID/count sai, artist không hợp lệ, quan sát trùng | 0 | Không có dòng bị loại bởi các quy tắc này |
| User dưới năm artist | 15 user, 33 cặp | Loại riêng 33 dòng, tổng 45.248 lượt nghe |
| Gán thẻ | 186.479 | 184.941 giữ; 1.538 lưu riêng |
| Từ điển thẻ | 11.946 | 11.946 |
| Artist chưa có thẻ trong danh mục | 5.499 | Giữ toàn bộ; 5.493 còn tương tác sau lọc |

15 artist không còn tương tác chỉ vì toàn bộ tương tác của họ thuộc user bị loại; vẫn giữ metadata của cả 15. Không lọc theo tần suất artist; còn 10.667 artist chỉ có một người nghe. Số artist có tương tác sau làm sạch chưa phải catalog đánh giá, vốn chỉ xác định sau split ở bước sau.

Gán thẻ chỉ dùng bản ngày tháng, không cộng bản timestamp. Bảng hợp lệ giữ userID và toàn bộ nguồn gán, trong đó 202 dòng thuộc user đã bị loại khỏi tập tương tác chính. Đây là metadata nguồn đã kiểm tra khóa nối, **không phải 184.941 dòng được phép dùng ngay cho train M2**. Từ vựng, IDF, đặc trưng và độ phủ hợp lệ phải học/tính lại theo nhóm học được phép ở M2.

Tham khảo [mã PoissonMF-CS 2017](https://github.com/zehsilva/poissonmf_cs/blob/master/scripts/load_convert.py): chỉ lấy thẻ cho artist thuộc bảng tương tác. Quy tắc đó áp lên bản nguồn hiện có giữ 184.941 dòng. Không gán cho bài báo một tuyên bố đích danh về 1.538 dòng; số này do nhóm kiểm tra độc lập. Ngưỡng user ≥ 5 và việc giữ đuôi dài là lựa chọn của khóa luận, không phải kết luận các bài đó đã chứng minh tối ưu.

Run: [metrics.json](../outputs/runs/cleaning_20261021/metrics.json), [verification.json](../outputs/runs/cleaning_20261021/verification.json), [bảng trước/sau](../outputs/runs/cleaning_20261021/before_after.csv). Sáu Parquet lưu tương tác sạch, tương tác loại, danh mục, từ điển thẻ, gán thẻ hợp lệ và gán thẻ loại; bản ghi loại có dòng nguồn/lý do. Run có cấu hình, hash đầu vào/đầu ra, Git SHA/trạng thái thay đổi và snapshot mã. Kiểm tra độc lập bằng csv/Counter xác nhận từng cặp/count giữ lại, từng dòng loại, bảo toàn gán thẻ/danh mục và hash nguồn.

Báo cáo nội dung mới ngày 21/10/2026 kế thừa bản V12 đã bàn giao ngày 20/10, giữ nguyên cấu trúc, công thức và phần đề cương Chương 4–5; cập nhật phần dữ liệu/làm sạch và công việc còn lại. Không ghi nhận đã chia tập hoặc có chất lượng mô hình; bản V12 giữ nguyên.

## Bước 4 chia tập và ánh xạ ngày 24/10/2026

Đầu vào là interactions.parquet thuộc run làm sạch đã kiểm chứng, cùng mã băm các Parquet trong metrics.json Bước 3. [splitting.py](../src/musicrec/data/splitting.py) chứa logic và [split_data.py](../scripts/split_data.py) là CLI ghi run mới; cấu hình split ở [base.yaml](../configs/base.yaml). Tên protocol là per_user_random_holdout, không phải leave-one-out hoặc temporal split. Hạt giống và tỷ lệ là lựa chọn của nhóm đã chốt trước khi chia, không phải giá trị tối ưu được tài liệu chứng minh.

Sắp user và artist theo giá trị số tăng dần, dùng một random.Random(42) lần lượt qua các user. Với mỗi lịch sử n nghệ sĩ, xáo trộn rồi lấy n_val = n_test = max(1, floor(0,1 × n)); lấy validation trước, test tiếp theo và train nhận phần còn lại. Không lọc thêm nghệ sĩ, đổi count, chuyển đích sang train để bảo đảm độ phủ hoặc thử seed khác để chọn catalog đẹp hơn.

| Tập | Cặp tương tác | User | Artist phân biệt trong tập | Tổng lượt nghe |
| --- | ---: | ---: | ---: | ---: |
| Train | 74.275 | 1.877 | 15.398 | 55.418.502 |
| Validation | 9.263 | 1.877 | 3.945 | 6.956.688 |
| Test | 9.263 | 1.877 | 4.054 | 6.763.537 |
| Hợp ba tập | 92.801 | 1.877 | 17.617 | 69.138.727 |

Ba tập không giao cặp user–artist và bảo toàn từng cặp/count nguồn. ID gốc vẫn là chuỗi định danh; user_index và item_index là chỉ số liên tiếp từ 0, theo thứ tự ID số, **chỉ tạo từ train**. Mapping user có 1.877 phần tử (0–1.876), mapping artist có 15.398 phần tử (0–15.397). 2.219 artist có tương tác sạch nhưng không xuất hiện trong train; danh mục metadata nguồn vẫn giữ đủ 17.632 artist.

Toàn bộ holdout được giữ nguyên trong Parquet, kể cả đích ngoài catalog. item_index của artist không có trong train là null, không phải một chỉ số dùng chung hoặc một artist được thêm từ test vào ánh xạ. Chưa tạo điểm đại diện, ma trận đặc trưng, từ vựng/IDF, similarity, popularity hoặc mô hình; M2 chưa chia nhóm user và vẫn là protocol riêng khi đến bước.

| Đích đánh giá theo catalog train | Validation | Test |
| --- | ---: | ---: |
| Tổng đích đã giữ lại | 9.263 | 9.263 |
| Đích thuộc catalog | 8.142 | 8.060 |
| Đích ngoài catalog | 1.121 (12,10%) | 1.203 (12,99%) |
| User có ít nhất một đích thuộc catalog | 1.865 | 1.855 |
| User không còn đích sau giao catalog | 12 | 22 |

Các số này là kiểm tra cấu trúc của protocol, không phải Precision/Recall/NDCG hoặc kết quả mô hình. Khi xây evaluator, lấy giao đích với catalog train và báo rõ mẫu số người dùng/đích đủ điều kiện; không thay split để giữ lại cả 1.877 user trong mọi phép đo. Validation lọc lịch sử train, test lọc train + validation; hồ sơ/học vẫn chỉ dùng train theo kế hoạch hiện hành.

Run [split_20261024](../outputs/runs/split_20261024/metrics.json) lưu ba Parquet, id_mappings.json, user_split_counts.csv, cấu hình, seed, phiên bản mã/trạng thái Git, hash input/output, runtime và snapshot mã. [Kiểm tra độc lập](../outputs/runs/split_20261024/verification.json) dùng Arrow records, tập hợp và từ điển, không gọi hàm chia production: tái dựng từng cặp/count, kiểm tra giao nhau, kích thước từng user, mapping/round-trip, đích ngoài catalog và eligibility. Run chạy lại split_20261024_recheck cho năm tệp dữ liệu/mapping/bảng đếm trùng mã băm. Nguồn thô và run làm sạch không đổi.

Bản [báo cáo ngày 24/10/2026](reports/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_24-10-2026.docx) kế thừa V13, bổ sung phương pháp/kết quả chia tập và công việc còn lại; không thêm mô hình mở rộng hoặc kết quả chất lượng. Dừng sau Bước 4; bước tiếp theo là biểu diễn train ở Bước 5 khi được phép.
