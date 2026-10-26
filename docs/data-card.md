# Data card HetRec 2011 Last.fm 2K

## Trạng thái sau Bước 13 ngày 26/10/2026

Đã hoàn thành Bước 1–13 theo yêu cầu người dùng. **Train có 74.275 cặp; validation và test mỗi tập 9.263 cặp; mapping gồm 1.877 user và 15.398 artist từ train.** Đã có evaluator, lượt chạy đầu của đủ sáu baseline và so PureSVD nhị phân/log/proxy tại 32 chiều/seed 42. NDCG@10 lần lượt 0.1564272628/0.1545766607/0.1516922327; chưa chốt mô hình cuối. Chưa tuning số chiều/CF/MF, học thẻ hoặc đánh giá test. Dừng Bước 13; các phần Bước 1–12 giữ bối cảnh lịch sử, kết quả mới nhất ở mục Bước 13 cuối tệp. Số dòng test ở đây kế thừa Bước 4, không mở lại test trong Bước 13. Word chỉ cập nhật khi người dùng yêu cầu rõ ràng, hiện giữ bản Bước 6.

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

## Bước 5 biểu diễn đầu vào ngày 24/10/2026

Đầu vào là run split_20261024 đã xác minh. [representations.py](../src/musicrec/data/representations.py) giữ logic, [prepare_inputs.py](../scripts/prepare_inputs.py) điều phối CLI; quy tắc nằm trong mục representations của [base.yaml](../configs/base.yaml). Count gốc không bị sửa hoặc cắt ngoại lai. Trên từng cặp quan sát, lưu thêm log_count = log2(1 + listening_count), binary = 1 và proxy_score = 1 + số ngưỡng log-count bị vượt nghiêm ngặt. Điểm đại diện không phải sao thật; ô chưa quan sát không được thêm như phản hồi âm hoặc điểm 1.

| Phân vị trên log-count train | Ngưỡng đầy đủ |
| --- | ---: |
| 20% | 6.392317422778761 |
| 40% | 7.562242424221073 |
| 60% | 8.491853096329674 |
| 80% | 9.579315937580015 |

Nội suy tuyến tính tại vị trí (n − 1) × q trên các log-count train đã sắp tăng. Bằng ngưỡng vẫn thuộc mức thấp hơn; ngưỡng trùng không bị tách tùy ý. Bốn giá trị trong transform.json chỉ học từ 74.275 cặp train; validation/test áp dụng lại nguyên giá trị, không đóng góp vào ước lượng hoặc chọn ngưỡng. Cơ số 2, các phân vị và quy tắc điểm là lựa chọn của nhóm cần kiểm chứng về Top-K, không phải kết luận Hu et al. đã chứng minh tối ưu.

| Tập | Điểm 1 | Điểm 2 | Điểm 3 | Điểm 4 | Điểm 5 | Tổng cặp |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Train | 14.989 | 14.805 | 14.819 | 14.818 | 14.844 | 74.275 |
| Validation | 1.889 | 1.824 | 1.865 | 1.838 | 1.847 | 9.263 |
| Test | 1.867 | 1.836 | 1.861 | 1.846 | 1.853 | 9.263 |

Đây là kiểm tra giá trị biến đổi, không phải kết quả chất lượng hoặc căn cứ tinh chỉnh từ test. Chênh lệch số cặp giữa các mức được giữ nguyên do đồng hạng.

Run [representations_20261024](../outputs/runs/representations_20261024/metrics.json) lưu ba Parquet với đủ cột gốc/chỉ số và ba cột bổ sung; bốn ma trận CSR train_raw_count/train_log_count/train_proxy_score/train_binary ở định dạng NPZ, kích thước 1.877 × 15.398, mỗi ma trận có đúng 74.275 ô quan sát. Raw count là int64, log là float64, proxy/binary là uint8. id_mappings.json sao chép nguyên byte từ Bước 4; transform.json lưu ngưỡng, cách fit, biên và ý nghĩa ô thiếu. Không tạo ma trận validation/test: vẫn giữ toàn bộ 1.121/1.203 đích ngoài catalog với item_index null trong Parquet, không biến chúng thành cột chung hoặc xóa dòng âm thầm.

[Kiểm tra độc lập](../outputs/runs/representations_20261024/verification.json) dùng Arrow records, math.log2, tự nội suy trên danh sách sắp xếp và đối chiếu từng tọa độ/giá trị sparse, không gọi hàm biến đổi production. Xác nhận bảo toàn đủ mọi cặp/count/chỉ số, đúng log/binary/điểm, mapping không đổi, nguồn thô/clean/split giữ nguyên. Chạy lại cho chín tệp dữ liệu/mapping/biến đổi trùng hash; run representations_20261024_final_recheck dùng mã sau kiểm tra kiểu cũng cho cùng chín hash. Run có seed kế thừa 42, config, Git SHA/trạng thái, hash input/output, runtime và snapshot mã; phép biến đổi không phát sinh ngẫu nhiên mới.

Bản [báo cáo Bước 5, V14](reports/V14/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_24-10-2026.docx) kế thừa bản Bước 4, cập nhật mục 3.5.3 và công việc còn lại, giữ công thức và đề cương Chương 4–5. Chưa học popularity, similarity, TF–IDF, xây evaluator hoặc huấn luyện. Bước tiếp theo là Bước 6 kiểm chứng evaluator trên ví dụ tính tay khi được phép.

## Bước 6 kiểm chứng bộ đánh giá ngày 25/10/2026

Đã hoàn thiện [evaluator dùng chung](../src/musicrec/evaluation/ranking.py), [kiểm thử](../tests/unit/test_ranking.py), [cấu hình](../configs/evaluation.yaml) và [CLI kiểm chứng tổng hợp](../scripts/evaluate.py). Dữ liệu đầu vào ví dụ nhỏ được lưu ngay trong run; không đọc Parquet HetRec, chấm baseline hoặc mở chỉ số test thật. Run [evaluator_20261025](../outputs/runs/evaluator_20261025/metrics.json) có đầu vào, kết quả từng user/từng K, đáp án tính tay, cấu hình, seed, Git SHA/diff hash và snapshot mã. Ba JSON dữ liệu/kết quả trùng hash ở run chạy lại `evaluator_20261025_recheck`.

Quy tắc đã kiểm tra: full ranking catalog train trừ lịch sử, hòa điểm theo mapping train; validation lọc train, test lọc train + validation nhưng thống kê/hồ sơ học vẫn chỉ từ train. Đích lấy giao catalog; báo đích ngoài catalog và user không còn đích. Danh sách trùng/seen/ngoài catalog bị từ chối. Precision chia K dù trả thiếu; user còn đích nhưng danh sách rỗng nhận 0 trong macro Precision/Recall/NDCG. IDCG dùng min(K, số đích hợp lệ), không giảm theo số mục thực trả.

Coverage/Gini dùng danh sách của cùng cohort đủ điều kiện; Gini giữ mọi artist kể cả tần suất 0 và không chuẩn hóa thêm theo kích thước hữu hạn. ARP dùng số người nghe phân biệt train; Novelty dùng `-log2((listeners + 1) / sum_catalog(listeners + 1))` theo công thức báo cáo V14. Hai chỉ số lấy trung bình trên các vị trí thực trả. ILD dùng cosine tương tác nhị phân train, lấy trung bình user có ít nhất hai mục. Báo mẫu số, số danh sách thiếu/rỗng, tỷ lệ đủ K và null cho chỉ số không xác định. Không coi đồng nghe là giống âm thanh hoặc thể loại. RMSE tách riêng, chỉ cho dự đoán cùng điểm đại diện 1–5 và không tự cắt dự đoán.

| Kiểm tra tính tay | Kết quả đã đối chiếu |
| --- | --- |
| Đích {A,C}, danh sách [B,A,C], K=3 | Precision 2/3; Recall 1; NDCG 0,6934264036 |
| Đích {A,C}, danh sách [A,B,C], K=5 | Precision 0,4; không chia 3 |
| Danh mục 4 mục, tần suất [2,1,1,0] | Coverage 3/4; Gini 0,375 |
| Ví dụ tổng hợp 4 user, 6 artist, K=3 | 3 user đủ điều kiện; Precision 1/3, Recall 2/3, NDCG 0,6399069297 |
| Cùng ví dụ, 4 vị trí thực trả | Coverage 0,5; Gini 7/12; ARP 1,25; Novelty 2,6611142969 bit; ILD 2/3, 1 user đóng góp |

Căn cứ: công thức mục 2.2 và ví dụ Phụ lục B của V14; đối chiếu [Recommenders evaluation](https://recommenders-team.github.io/recommenders/evaluation.html) và [scikit-learn NDCG](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html). Bộ kiểm thử so NDCG với scikit-learn trên 20 ví dụ seed 42 × 4 cutoff. Chính sách catalog, lọc lịch sử, cohort và làm trơn Novelty là lựa chọn đã chốt của nhóm; không khẳng định tái hiện chính xác toàn bộ evaluator của thư viện hay bài báo nào.

[Báo cáo mới ngày 25/10](reports/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_25-10-2026.docx) kế thừa đầy đủ V14, cập nhật mục 2.2.9, 3.10, Phụ lục B/C và giữ đề cương Chương 4–5. Các số minh họa chỉ xác nhận logic evaluator; chưa có kết quả chất lượng mô hình. Bước tiếp theo là Bước 7 Random seed 42 trên validation, cần cho phép riêng.

## Bước 7 Random trên validation ngày 25/10/2026

Run [random_validation_20261025](../outputs/runs/random_validation_20261025/metrics.json) đọc train/validation/mapping có hash từ Bước 4; không mở `test.parquet` kể cả để băm. [RandomRecommender](../src/musicrec/recommenders/random.py) giữ giao diện fit/predict/recommend; [CLI](../scripts/run_random.py) điều phối, [cấu hình](../configs/models/random.yaml) cố định seed 42. Fit chỉ ghi catalog và user đã biết, không dùng count hoặc sở thích học được. Danh mục gồm 15.398 artist theo ID số tăng dần; mỗi user có RNG mới từ chuỗi `musicrec-random-v1:42:{user_id}`. Xáo trộn toàn catalog, lọc train rồi lấy tối đa 20; K=5/10 lấy prefix cùng thứ tự. Score là hạng hoán vị giảm dần, không phải rating hoặc xác suất. User mới nhận cùng baseline với reason cold-start riêng.

Đây là baseline Random theo kế hoạch/báo cáo hiện hành; cách gắn seed theo user và quy tắc score là lựa chọn hiện thực của nhóm, không khẳng định tái hiện đúng generator của một bài báo. Kết quả độc lập thứ tự train, thứ tự yêu cầu và count; runtime Python ghi trong run để tái lập. Không chọn seed tốt nhất sau khi xem kết quả.

Cả 1.877 user nhận đủ 20 mục, tổng 37.540 dòng; không trùng, chứa lịch sử hoặc ngoài catalog. Đánh giá dùng đúng evaluator Bước 6 trên 1.865 user có 8.142 đích hợp lệ. Báo riêng 1.121/9.263 đích ngoài catalog và 12 user không còn đích; các danh sách của 12 user này không tham gia chỉ số. Không có danh sách thiếu/rỗng trong cohort đủ điều kiện; tỷ lệ đủ K bằng 1 tại cả ba cutoff.

| K | Precision | Recall | NDCG | Coverage | Gini | ARP (listener) | Novelty (bit) | ILD |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 0.0001072386 | 0.0001072386 | 0.0000909277 | 0.4543447201 | 0.6330935566 | 4.5358713137 | 14.8222849311 | 0.9984875796 |
| 10 | 0.0003217158 | 0.0006970509 | 0.0003721497 | 0.7060007793 | 0.4807439704 | 4.5472922252 | 14.8212885902 | 0.9984051271 |
| 20 | 0.0001876676 | 0.0008042895 | 0.0004212940 | 0.9102480842 | 0.3548336001 | 4.6212064343 | 14.8231095788 | 0.9983697832 |

Tổng lượt tìm trúng tại K=5/10/20 lần lượt là 1/6/7. Đây là một seed validation làm mốc ngẫu nhiên, chưa phải kết luận chọn mô hình hoặc kết quả test. Coverage/ILD cao đi cùng khả năng tìm lại đích rất thấp; không suy ra chất lượng cá nhân hóa chỉ từ đa dạng/bao phủ. Không tính RMSE cho điểm thứ hạng Random.

Lần chạy đầu: fit 0,018829 giây (chỉ thu catalog/user ID); recommend toàn bộ 9,631595 giây, trung bình 5,131377 ms/user và phân vị 95% 6,167540 ms; evaluator 1,307155 giây. Đây là số đo riêng lần chạy trên môi trường hiện tại, không phải cam kết độ trễ API hoặc đo hiệu năng tổng quát. Chi phí đọc dữ liệu, ghi tệp và provenance không nằm trong thời gian fit/recommend.

Run lưu `recommendations.csv` gồm ID/thứ hạng/score/reason, `evaluation.json` từng user và cohort, `metrics.csv`, `model.json` catalog/config/user, mapping nguyên byte, config, thời gian, hash input/output, Git SHA/trạng thái/diff và snapshot mã. [Kiểm tra độc lập](../outputs/runs/random_validation_20261025/verification.json) tái dựng toàn bộ hoán vị/score từ trạng thái đã lưu mà không gọi class production; tính lại P/R/NDCG bằng vector chiết khấu NumPy, ILD bằng Gram của ma trận nhị phân thưa, Gini/ARP/Novelty bằng tần suất. Tất cả khớp với sai số tối đa 1e-12. Run `random_validation_20261025_recheck` cho năm tệp dự đoán/chỉ số/trạng thái/mapping trùng hash. Kiểm thử còn xác nhận không đọc test, không ghi đè, phát hiện hash sai và thư mục output nằm trong input.

Theo yêu cầu mới nhất của người dùng, **chỉ sửa Word khi được yêu cầu rõ ràng**, không tự sửa sau mỗi bước hoặc khi chạy hết mô hình. Đã giữ nguyên mọi bản Word; bản gần nhất vẫn phản ánh Bước 6, chưa có các số liệu Random này. Bước tiếp theo là Bước 8 Popularity tổng log-count train, cần cho phép riêng.

## Bước 8 Popularity tổng log-count trên validation ngày 25/10/2026

Run [popularity_validation_20261025](../outputs/runs/popularity_validation_20261025/metrics.json) dùng đúng train/validation/mapping và evaluator của Random; hash đầu vào và cấu hình đánh giá giống nhau. [PopularityRecommender](../src/musicrec/recommenders/popularity.py) nhận count gốc từ 74.275 cặp train, tính riêng log2(1 + count) của từng cặp rồi cộng theo artist. Tổng dùng fsum trên các giá trị đã sắp để không phụ thuộc thứ tự dòng; không biến đổi log lần hai. [Cấu hình](../configs/models/popularity.yaml) ghi rõ công thức, fit train-only và hòa điểm theo ID số tăng dần. Model xác định, seed 42 chỉ truy vết split, không tạo ba seed giả lập hoặc chọn cấu hình mới sau kết quả.

Căn cứ là biến thể Popularity theo cường độ nghe đã chốt ở công thức (3.3) của báo cáo và kế hoạch hiện hành. Tổng log-count là lựa chọn của nhóm, không tuyên bố tái hiện đúng một bài báo hoặc xem Popularity theo listener count là cùng phương pháp. **Score Popularity khác listener count**: ARP/Novelty vẫn đếm số user phân biệt trên train bằng evaluator dùng chung; không lấy tổng log-count làm mức phổ biến trong hai chỉ số này.

Ví dụ kiểm tra: artist 2 có count 3 từ hai user, điểm bằng log2(4) + log2(4) = 4; artist 10 có một user count 15, điểm cũng bằng 4. Hai artist hòa điểm nên 2 đứng trước 10; listener count tương ứng là 2 và 1. Nếu cộng count rồi lấy log, artist 2 chỉ nhận log2(7), sai quy tắc đã chọn. Kiểm thử xác nhận thứ tự/predict/recommend nhất quán, không trùng/seen, prefix giữa các K, lạnh user có reason riêng, giữ fallback thứ tự từ vựng cho ID chữ ở khung API cũ, từ chối count không hữu hạn và trùng cặp.

[CLI Popularity](../scripts/run_popularity.py) và CLI Random dùng chung [runner I/O](../scripts/run_baseline.py); không sao chép logic kiểm tra nguồn hoặc đổi evaluator. Mỗi lệnh chỉ chạy một model và một cấu hình được phép. Run mới nằm ngoài input, không ghi đè; chỉ đọc train/validation/mapping, không mở test kể cả để băm. Fit sắp toàn catalog một lần, recommend lọc lịch sử rồi lấy prefix. `model.json` lưu score của đủ 15.398 artist, catalog, config và user đã biết; điểm toàn cục không phải sao thật hoặc xác suất thích.

Đủ 1.877 user nhận 20 mục, tổng 37.540 dòng; evaluator dùng đúng 1.865 user với 8.142 đích hợp lệ như Random. Báo riêng 1.121 đích ngoài catalog và 12 user không còn đích. Không có mục trùng/seen/ngoài catalog, danh sách thiếu hoặc rỗng; tỷ lệ đủ K bằng 1.

| K | Precision | Recall | NDCG | Coverage | Gini | ARP (listener) | Novelty (bit) | ILD |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 0.0408579088 | 0.0439142091 | 0.0470971045 | 0.0012339265 | 0.9995396289 | 385.9477747989 | 7.8666909028 | 0.5972177835 |
| 10 | 0.0339410188 | 0.0731903485 | 0.0623622664 | 0.0018184180 | 0.9991467922 | 351.8289544236 | 8.0066170799 | 0.6647826606 |
| 20 | 0.0259785523 | 0.1113583557 | 0.0784329643 | 0.0027276270 | 0.9984083968 | 297.1026541555 | 8.2728787595 | 0.7220508006 |

Tìm trúng tổng cộng 381/633/969 cặp đích tại K=5/10/20, so với 1/6/7 của Random seed 42. NDCG@10 tăng từ 0.0003721497 lên 0.0623622664 trên validation hiện tại; không xem đây là kiểm định thống kê, kết quả test hoặc bằng chứng mô hình tốt nhất. Coverage@5/10/20 chỉ gồm 19/28/42 artist; Coverage@10 bằng 28/15.398 ≈ 0,1818418%, trong khi Random phủ 70,6000779%. ARP@10 tăng từ 4,5473 lên 351,8290, ILD giảm từ 0,9984051 xuống 0,6647827. Baseline này tìm lại đích tốt hơn trong phép thử nhưng tập trung mạnh vào artist nhiều người nghe. Không tính RMSE trên điểm xếp hạng hoặc tự chạy đối chứng Popularity listener count.

Lần chạy đầu: fit 0,063455 giây, recommend tổng 0,015147 giây, trung bình 0,008070 ms/user, phân vị 95% 0,009100 ms; evaluator 6,445057 giây. Fit gồm tổng hợp và sắp trước catalog; recommend là phép lọc/lấy prefix từ trạng thái trong RAM. Số đo không gồm đọc/ghi dữ liệu hoặc provenance, không phải cam kết độ trễ API hay benchmark môi trường kiểm soát.

[Kiểm tra độc lập](../outputs/runs/popularity_validation_20261025/verification.json) dùng NumPy log2 + bincount trên train, sai khác lớn nhất của điểm so với fsum là 2.7284841053e-12 do số thực. Tái dựng mọi danh sách và score từ model.json mà không gọi class production; tính lại từng user và mọi chỉ số bằng vector chiết khấu, tần suất và Gram của ma trận nhị phân thưa, khớp trong 1e-12. Run `popularity_validation_20261025_recheck` trùng hash năm tệp dự đoán/chỉ số/trạng thái/mapping. Toàn bộ kiểm thử gồm cả hồi quy CLI Random đều đạt; dữ liệu, run cũ và 11 bản Word giữ nguyên.

Word chưa cập nhật các kết quả Bước 7–8 theo yêu cầu người dùng. Bước tiếp theo là Bước 9 UserCF tại một cấu hình L=40, shrinkage=0; cần cho phép riêng, chưa chạy lưới tinh chỉnh.

## Bước 9 UserCF một cấu hình L bằng 40 và shrinkage bằng 0

Run chốt: [user_cf_l40_s0_validation_20261025_checked](../outputs/runs/user_cf_l40_s0_validation_20261025_checked/metrics.json). [UserCFRecommender](../src/musicrec/recommenders/user_cf.py) dùng train proxy_score đã lưu ở Bước 5, không học lại phân vị hoặc dùng count thay điểm. [Interaction](../src/musicrec/data/contracts.py) có thêm trường proxy_score tùy chọn để giữ riêng count gốc; Random/Popularity vẫn dùng hợp đồng cũ với giá trị mặc định None. [CLI](../scripts/run_user_cf.py) dùng chung runner, chỉ đọc train/validation/mapping/transform có hash; không mở test kể cả để băm. So với Bước 7–8, từng cặp/count/chỉ số và cohort giữ nguyên.

Cosine lấy tích vô hướng trên toàn vector proxy và chuẩn toàn vector, vị trí thiếu bằng 0 khi tính tương đồng; không coi vị trí thiếu là điểm 0 quan sát thật khi tính mean hoặc dự đoán. Bỏ chính user, giữ tương đồng dương với ít nhất một artist chung; co rút định nghĩa là cosine × n_common/(n_common + shrinkage), ở lượt này shrinkage=0. Chọn tối đa L=40 láng giềng toàn user trước, rồi từng item chỉ nhận đóng góp từ các láng giềng đã nghe item. Không đổi thành chọn top-40 riêng trong nhóm người nghe từng artist.

Dự đoán bằng mean của các quan sát train của user cộng trung bình có trọng số các độ lệch r_vi − mean_v. Thiếu đóng góp dùng mean user; user chưa có trong train dùng mean chung và reason riêng, chưa phải M2 hoặc bằng chứng đã xử lý tốt cold-start. Predict/recommend không cắt điểm về 1–5; artist ngoài catalog bị từ chối. Recommend loại cả lịch sử train đã biết và lịch sử bổ sung, full ranking cùng catalog với các baseline. Khóa sắp láng giềng và item làm tròn 12 chữ số rồi theo mapping số để ổn định hòa điểm; trọng số và dự đoán gốc vẫn dùng để tính score/RMSE.

Thiết kế theo công thức UserCF trừ mean trong báo cáo hiện hành. Đối chiếu công thức dự đoán và mean fallback với [Surprise KNNWithMeans](https://surprise.readthedocs.io/en/stable/knn_inspired.html); không tuyên bố tái hiện thư viện. [Cosine của Surprise](https://surprise.readthedocs.io/en/stable/similarities.html) chỉ tính chuẩn trên phần đồng quan sát, khác chuẩn toàn vector mà nhóm đã chốt. Biểu diễn proxy, chọn láng giềng toàn cục, co rút và quy tắc số học là lựa chọn hiện thực của nhóm.

Ví dụ tay: user 1 có {artist 1:3, 2:5}, mean=4; user 2 có {1:1, 2:3, 3:5}, mean=3; user 3 có {1:5, 2:3, 4:1}, mean=3; user 4 chỉ có {5:2}. Cosine user 1 với user 2 và 3 lần lượt là 18/sqrt(34×35) và 30/sqrt(34×35). Dự đoán artist 3 là 4+(5−3)=6, artist 4 là 4+(1−3)=2, artist 5 là fallback 4. L=1 chỉ chọn user 3 nên artist 3 trở về 4, không tự thay bằng user 2. Các kiểm thử L=1/shrinkage=10 chỉ là ví dụ nhỏ kiểm tra logic, không phải lượt tinh chỉnh trên dữ liệu thật.

Run ban đầu `user_cf_l40_s0_validation_20261025` được giữ cùng audit.json, không dùng báo cáo: kiểm tra độc lập phát hiện 12 user có lựa chọn ở ngưỡng L bị nhiễu cosine khoảng 3,33e-16, làm tie không luôn theo ID. Đã bổ sung kiểm thử hồi quy với hai cosine cùng bằng 0,15 và ổn định khóa sort ở 12 chữ số. Run checked và run recheck cùng L=40/shrinkage=0 là kết quả sau sửa lỗi; không chọn hyperparameter hoặc đổi seed từ chất lượng validation. Precision/Recall/NDCG không đổi qua sửa lỗi; một số chỉ số tần suất thay đổi nhỏ do ID được chọn khi hòa.

Đủ 1.877 user nhận 20 mục, tổng 37.540 dòng; đánh giá trên cùng 1.865 user, 8.142 đích hợp lệ, báo riêng 1.121 đích ngoài catalog và 12 user không còn đích. Không có mục trùng/seen/ngoài catalog hoặc danh sách thiếu/rỗng.

| K | Precision | Recall | NDCG | Coverage | Gini | ARP (listener) | Novelty (bit) | ILD |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 0.0028954424 | 0.0032171582 | 0.0031049848 | 0.0689050526 | 0.9730097952 | 30.2454691689 | 12.8677122201 | 0.9583425993 |
| 10 | 0.0057372654 | 0.0129490617 | 0.0080787555 | 0.1030653332 | 0.9587138401 | 31.3817694370 | 12.8405979410 | 0.9669347051 |
| 20 | 0.0076943700 | 0.0338069705 | 0.0166469445 | 0.1486556696 | 0.9385312392 | 33.5601608579 | 12.7778560535 | 0.9722169032 |

Tìm trúng 27/107/287 cặp tại K=5/10/20. Cấu hình UserCF đầu có NDCG@10 0.0080787555 cao hơn Random 0.0003721497, thấp hơn Popularity 0.0623622664. Coverage@10 10,3065% cao hơn Popularity 0,1818%; ARP thấp hơn và ILD cao hơn. Chưa kết luận UserCF nói chung kém hơn, hoặc chọn mô hình cuối: đây mới là một cấu hình validation, chưa kiểm định hay mở test.

RMSE bổ sung của proxy = 0.9326875842 trên 8.142 cặp, không dùng chọn ranking. Có 1.840 cặp đích dùng mean fallback và 707 dự đoán held-out nằm ngoài 1–5 được giữ nguyên. Mỗi user có từ 2 đến 40 láng giềng; không user nào hoàn toàn thiếu láng giềng. Trên 28.827.771 ứng viên chưa nghe của toàn bộ user, 27.616.017 không nhận đóng góp trực tiếp từ top-L; tuy vậy, không vị trí Top-5/10/20 nào của cohort đánh giá dùng fallback. Vì thế, không thể chỉ từ lượng fallback mà kết luận nguyên nhân của chất lượng ranking thấp.

Lần chạy checked: fit 0,299661 giây, recommend tổng 4,873055 giây, trung bình 2,596194 ms/user, phân vị 95% 3,403740 ms; evaluator 1,410670 giây. RMSE riêng 3,913492 giây; nạp/đối chiếu mọi danh sách 5,553119 giây. Số đo chỉ của môi trường/lần chạy hiện tại, không gồm đọc/ghi nguồn trong thời gian fit/recommend và không phải cam kết độ trễ API. Predict từng cặp hiện tính cả catalog để dùng chung logic; chưa tối ưu batch do bước này ưu tiên kiểm chứng.

Artifact gồm CSR proxy và láng giềng trong model/ratings.npz, model/neighbors.npz; model/state.json giữ ID/mean/tham số/hash. Load kiểm tra checksum, kích thước, giá trị và mapping, khôi phục láng giềng đã lưu mà không fit hoặc tính similarity mới. Đã nạp lại và khớp đủ 1.877 danh sách/score/reason; chín tệp dữ liệu/model/transform trùng hash trong run recheck. Mỗi run lưu config, seed nguồn split, hash đầu vào/đầu ra, Git SHA/trạng thái/diff và snapshot mã.

[Kiểm tra độc lập](../outputs/runs/user_cf_l40_s0_validation_20261025_checked/verification.json) không gọi model/evaluator production: dựng Gram của CSR proxy từ train, kiểm tra top-40 của mọi user, cộng đóng góp bằng dictionary theo từng láng giềng, tái dựng mọi danh sách/score/reason; tính lại RMSE, từng metric user, Coverage/Gini/ARP/Novelty và ILD nhị phân train. Score tái dựng trùng hoàn toàn; chỉ số khớp trong 1e-12. candidate_diagnostics.csv lưu số láng giềng và mức fallback. **47 tests đạt**, gồm hồi quy hai CLI trước, kiểm tra save/load không gọi fit và checksum sai; lint/format/mypy phần mới đạt. Mọi artifact baseline cũ và 11 Word giữ nguyên.

Đây là bằng chứng riêng Bước 9; kết quả ItemCF nằm ở mục Bước 10 bên dưới. Tinh chỉnh UserCF vẫn là điểm dừng riêng, chưa chạy lưới 12 cấu hình. Word giữ ở Bước 6.

## Bước 10 ItemCF một cấu hình ngày 26/10/2026

Run chốt: [item_cf_l40_s0_validation_20261026](../outputs/runs/item_cf_l40_s0_validation_20261026/metrics.json). [ItemCFRecommender](../src/musicrec/recommenders/item_cf.py), [CLI](../scripts/run_item_cf.py) và [cấu hình](../configs/models/item_cf.yaml) dùng train proxy_score từ Bước 5, không học lại ngưỡng hay dùng count thay điểm. Runner chung chỉ đọc train/validation/mapping/transform có hash, không mở test kể cả để băm; guard kiểm toán của lượt chạy và kiểm tra độc lập sẽ báo lỗi nếu có thao tác mở test.parquet. Không chạy tuning, MF/PureSVD hoặc M1/M2.

Căn cứ là họ ItemCF và dự đoán trung bình có trọng số trong [Sarwar et al. (2001), Item-based collaborative filtering recommendation algorithms](https://experts.umn.edu/en/publications/item-based-collaborative-filtering-recommendation-algorithms/) và công thức ItemCF trong [tài liệu ôn tập](SEMINAR_CHUONG_1_2.md#34-item-based-cf). Không tuyên bố tái hiện nguyên bài báo: proxy 1–5, cosine thường trên toàn cột, L=40/shrinkage=0, chọn top-L toàn cục, fallback và khóa số học là lựa chọn của nhóm trên protocol hiện hành. Không gọi cosine này là adjusted cosine hoặc suy ra hai artist giống âm thanh/thể loại từ đồng nghe.

Cosine lấy toàn cột proxy train, ô thiếu bằng 0 chỉ trong phép tính tương đồng. Giữ tương đồng dương, bỏ self, ít nhất một user chung; co rút khi dùng là cosine × n_common/(n_common + shrinkage), lượt này shrinkage=0. Với mỗi artist đích i, chọn tối đa 40 láng giềng toàn catalog trước, rồi giao với lịch sử user. Dự đoán = tổng sim(i,j) × r_uj chia tổng sim(i,j) trên phần giao; không trừ mean, không lấy tổng không chuẩn hóa, không thay bằng top-40 riêng trong lịch sử user. W có chiều target × neighbor; pruning có thể làm W không đối xứng. Tính theo khối 256 artist và chỉ lưu CSR top-L, không tạo toàn Gram item–item đặc hoặc thưa.

Mẫu số bằng 0 dùng mean điểm quan sát train của user; user mới dùng mean chung và reason riêng, chưa phải M2. Artist ngoài catalog bị từ chối; recommend lọc cả train history và lịch sử truyền thêm. Khóa sort cosine/score làm tròn 12 chữ số rồi theo mapping ID số; score/trọng số gốc không clip, không dùng khóa đã làm tròn tính RMSE. Ô chưa nghe không trở thành điểm 0 thật trong trung bình dự đoán.

Ví dụ tay dùng cùng bảng nhỏ Bước 9: cột artist 1 là [3,1,5,0], artist 2 là [5,3,3,0], artist 3 là [0,5,0,0]. sim(3,1)=1/sqrt(35), sim(3,2)=3/sqrt(43). User 1 có điểm 3 và 5 nên dự đoán artist 3 bằng (3/sqrt(35)+15/sqrt(43))/(1/sqrt(35)+3/sqrt(43)); artist 5 không có đóng góp nên dùng mean=4. Với L=1, artist 3 chỉ giữ artist 2 nên dự đoán là 5. Nếu user chỉ biết artist 1 và artist 5, không được thay láng giềng artist 2 bằng artist 1 sau khi giao lịch sử. Các kiểm thử L=1/shrinkage=10 và 259 artist chỉ xác minh logic, tie, ranh giới khối; không phải tuning dữ liệu thật.

Đủ 1.877 user nhận 20 mục, tổng 37.540 dòng; evaluator dùng cùng 1.865 user/8.142 đích hợp lệ, báo riêng 12 user không còn đích và 1.121 đích ngoài catalog. Không có danh sách thiếu/rỗng hoặc mục trùng/đã nghe/ngoài catalog.

| K | Precision | Recall | NDCG | Coverage | Gini | ARP (listener) | Novelty (bit) | ILD |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 0.0046112601 | 0.0052010724 | 0.0053934554 | 0.1239771399 | 0.9609361127 | 36.0707774799 | 13.1875241660 | 0.8310732406 |
| 10 | 0.0040214477 | 0.0091331546 | 0.0074299548 | 0.2250292246 | 0.9307386879 | 34.4053083110 | 13.2675603621 | 0.8328794020 |
| 20 | 0.0032707775 | 0.0151027703 | 0.0097793148 | 0.3970645538 | 0.8793262591 | 29.3433512064 | 13.5249495852 | 0.8578593222 |

Tìm trúng 43/75/122 đích tại K=5/10/20. NDCG@10 0.0074299548 cao hơn Random 0.0003721497, thấp hơn UserCF cấu hình đầu 0.0080787555 và Popularity 0.0623622664. Coverage@10 có 3.465 artist (22,5029%), cao hơn UserCF 10,3065% và Popularity 0,1818%; ILD thấp hơn UserCF (0,8328794 so 0,9669347), ARP cao hơn UserCF (34,4053 so 31,3818). Không kết luận ItemCF nói chung kém hơn hoặc chọn nền cuối từ một cấu hình validation; chưa kiểm định hay đánh giá test.

RMSE proxy bổ sung = 0.9796199383 trên 8.142 cặp, trong đó 2.262 cặp dùng mean fallback; không dùng RMSE chọn ranking. Mỗi artist có 2–40 láng giềng, không artist nào hoàn toàn thiếu láng giềng; giao với lịch sử vẫn có thể rỗng. Trong 28.827.771 ứng viên chưa nghe của toàn user, 21.281.596 dùng mean fallback. Top-5/10/20 trên cohort đánh giá có 579/1.217/2.497 vị trí fallback; vì vậy, coverage bao gồm cả artist xếp theo mean và quy tắc hòa ID, không chứng minh toàn bộ độ phủ là gợi ý cá nhân hóa từ đồng nghe.

Lần chạy đầu: fit 0,622397 giây; recommend tổng 5,739155 giây, trung bình 3,057621 ms/user, phân vị 95% 3,883440 ms; evaluator 1,480314 giây. RMSE riêng 6,638479 giây; nạp/đối chiếu đủ 1.877 danh sách 6,509215 giây. Ba tệp model chiếm 2.303.559 byte trên đĩa; không phải bộ nhớ đỉnh. Số đo không gồm I/O nguồn trong fit/recommend, chưa phải benchmark kiểm soát hoặc độ trễ API. Predict từng cặp hiện dùng lại logic chấm catalog, chưa tối ưu batch.

Artifact gồm recommendations.csv có score/reason, metric tổng/từng user, config/seed/hash/Git SHA/trạng thái/diff, snapshot mã, mapping/transform và ba tệp model CSR/state. Load kiểm tra checksum/mapping/kích thước/giá trị, không fit hoặc tính similarity mới; khớp đủ 1.877 danh sách/score/reason. Run `_recheck` trùng hash **chín tệp** dự đoán/chỉ số/model/mapping/transform.

[Kiểm tra độc lập](../outputs/runs/item_cf_l40_s0_validation_20261026/verification.json) không nhập recommender/evaluator production: dựng cosine từ tích vô hướng cột gốc chia chuẩn (khác cách chuẩn hóa trước trong model), kiểm tra cả 15.398 bộ top-40; tính lại điểm từ ma trận lịch sử × láng giềng để tái dựng mọi danh sách/score/reason, RMSE, từng metric user và mọi chỉ số tổng bằng NumPy/CSR. Sai khác trọng số tối đa 1,22125e-15, score 2,66454e-15; các chỉ số khớp trong 1e-12. Mã kiểm tra và guard được lưu cùng audit của run. **53 tests đạt; ruff check, ruff format --check và mypy toàn mã nguồn đạt** sau sửa nhỏ lỗi style/import/type đã có; .venv-legacy được bỏ khỏi quét qua .gitignore. Các sửa này không triển khai luồng prototype mới. Đối chiếu hash 36 tệp xác nhận mọi đầu ra baseline trước và cả 11 Word giữ nguyên.

Đây là bằng chứng riêng Bước 10; kết quả SVD có độ lệch nằm ở mục Bước 11 bên dưới. GitHub chỉ nhận mã/cấu hình/tài liệu; dataset, model và run vẫn giữ cục bộ trong các đường dẫn bị ignore. Word giữ Bước 6; tinh chỉnh UserCF/ItemCF vẫn là các điểm dừng riêng, chưa chạy lưới.

## Bước 11 SVD có độ lệch một cấu hình ngày 26/10/2026

Run chốt: [svd_k32_validation_20261026](../outputs/runs/svd_k32_validation_20261026/metrics.json). [SVDRecommender](../src/musicrec/recommenders/svd.py), [CLI](../scripts/run_svd.py) và [cấu hình](../configs/models/svd.yaml) học proxy_score từ Bước 5. Tham số theo kế hoạch hiện hành: 32 nhân tố, learning rate 0.005, regularization 0.02, seed 42, tối đa 100 epoch, patience 5 theo NDCG@10 validation. YAML khung cũ 64 nhân tố/30 vòng được thay bằng cấu hình này trước chạy. Chỉ một cấu hình/seed; chưa tuning hoặc thử seed bổ sung.

Căn cứ phương pháp là [Koren, Bell và Volinsky (2009), Matrix Factorization Techniques for Recommender Systems](https://doi.org/10.1109/MC.2009.263), đối chiếu trực tiếp [toàn văn, công thức 4–5 và phần SGD](https://homepages.math.uic.edu/~lreyzin/s15_mcs590/koren09.pdf). Mô hình dự đoán mu + b_u + b_i + p_u dot q_i, với mu là mean proxy train cố định, hai bias và hai vector học từ quan sát. Đây là MF có bias thường gọi SVD trong recommender, không gọi TruncatedSVD/PureSVD, implicit ALS, BPR hoặc SVD++. Chuyển lượt nghe thành proxy 1–5, số nhân tố, khởi tạo, seed, fallback và cách chọn epoch là lựa chọn của nhóm; không tuyên bố tái hiện kết quả Netflix hoặc xem proxy là sao thật.

Loss ghi trong learning curve là 1/2 × tổng trên từng cặp quan sát [(r_ui − dự đoán)^2 + lambda × (b_u^2 + b_i^2 + norm(p_u)^2 + norm(q_i)^2)]. L2 được áp mỗi quan sát nên khi tổng hợp tương đương trọng số tần suất quan sát cho norm từng user/item; không mô tả nhầm là một lần phạt toàn bộ tham số độc lập tần suất. SGD chỉ qua 74.275 cặp train, không điền ô thiếu thành nhãn 0 và không sinh negative. Bias khởi tạo 0; factor float64 lấy normal(0,0.1) bằng Generator(PCG64(42)); sắp các cặp theo mapping user/item số trước khi xáo trộn mỗi epoch bằng cùng RNG sau khởi tạo. Các gradient dùng error và factor trước bước học; p mới không được dùng để cập nhật q trong cùng bước.

Ví dụ minh họa: mu=3, b_u=0.2, b_i=−0.3, p=[0.1,0.9], q=[0.2,0.8] cho dự đoán 3.64. Nếu target proxy=5, error=1.36; một bước lr=0.005/reg=0.02 cho b_u mới=0.20678, b_i mới=−0.29317, p mới=[0.10135,0.90535], q mới=[0.20066,0.80604]. Ví dụ kiểm tra SGD bằng số vô hướng trong test dùng bảng quan sát nhỏ và trạng thái khởi tạo thật, kiểm cả objective sau epoch; không phải cấu hình thực nghiệm thứ hai.

Từ epoch 1 tính full-ranking NDCG@10 trên đúng cohort validation sau mỗi epoch. Chỉ tăng nghiêm ngặt mới cải thiện, hòa giữ epoch sớm nhất; sau 5 epoch liên tiếp không cải thiện thì dừng, hoặc đạt trần 100. Sao chép đủ bias/factor ở checkpoint tốt nhất và khôi phục trước khi xuất model/đánh giá cuối. Validation chỉ chọn epoch, không cung cấp target gradient, không học lại phân vị, mean hoặc mapping. RMSE không điều khiển dừng sớm. Run và kiểm tra độc lập có guard báo lỗi nếu mở test.parquet, kể cả để băm; không đọc test hoặc refit train+validation.

User mới dùng mu + bias artist, không có bias/vector user; reason là svd_item_bias_cold_start. Đây là đường không cá nhân hóa, chưa phải M2. Predict từ chối artist ngoài catalog. Recommend loại lịch sử train đã biết và lịch sử truyền thêm; đủ full catalog chưa nghe, không lấy mẫu ứng viên. Score/gradient không clip hoặc làm tròn; riêng khóa sort làm tròn 12 chữ số rồi theo mapping số. CLI đặt OPENBLAS/MKL/OMP/BLIS một luồng trước import NumPy để kiểm tra tái lập; runtime lưu môi trường luồng và phiên bản thư viện.

Run chạy **6 epoch**, chọn/khôi phục **epoch 1**. [learning_curve.csv](../outputs/runs/svd_k32_validation_20261026/learning_curve.csv) và [hình đường học](../outputs/runs/svd_k32_validation_20261026/audit/learning_curve.png) giữ cả sáu epoch; tham số model và kết quả dưới đây thuộc epoch 1, không thuộc epoch cuối.

| Epoch | Train proxy RMSE | NDCG@10 validation | Checkpoint |
| ---: | ---: | ---: | --- |
| 1 | 1.2331161636 | 0.0564899628 | Tốt nhất, được xuất |
| 2 | 1.1059182031 | 0.0543261867 | Không cải thiện |
| 3 | 1.0136200681 | 0.0504302904 | Không cải thiện |
| 4 | 0.9469206037 | 0.0478624503 | Không cải thiện |
| 5 | 0.8989960759 | 0.0436939184 | Không cải thiện |
| 6 | 0.8645013737 | 0.0431400553 | Đủ patience 5, dừng |

Đủ 1.877 user nhận 20 mục (37.540 dòng); evaluator dùng cùng 1.865 user và 8.142 đích hợp lệ như bốn baseline trước. Báo riêng 12 user không còn đích và 1.121 đích ngoài catalog. Không có mục trùng/đã nghe/ngoài catalog hoặc danh sách thiếu/rỗng. Tất cả user trong phép thử chính đã có tham số học từ train; không dùng chất lượng này làm bằng chứng cold-start.

| K | Precision | Recall | NDCG | Coverage | Gini | ARP (listener) | Novelty (bit) | ILD |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 0.0345308311 | 0.0373369080 | 0.0415643226 | 0.0020132485 | 0.9994811415 | 361.1347989276 | 7.9934939147 | 0.6176560312 |
| 10 | 0.0301876676 | 0.0657283289 | 0.0564899628 | 0.0053253669 | 0.9990620627 | 317.0871849866 | 8.2154873533 | 0.7211056802 |
| 20 | 0.0205630027 | 0.0889008043 | 0.0662684929 | 0.0422132745 | 0.9972423667 | 254.3220375335 | 8.7180984374 | 0.7974723635 |

Tìm trúng 322/563/767 cặp tại K=5/10/20, phủ 31/82/650 artist tương ứng. NDCG@10 0.0564899628 dưới Popularity 0.0623622664, cao hơn UserCF 0.0080787555, ItemCF 0.0074299548 và Random 0.0003721497. Coverage@10 0,5325% cao hơn Popularity 0,1818% nhưng vẫn rất thấp so hai CF; ARP 317,0872 thấp hơn Popularity 351,8290 nhưng vẫn tập trung artist nhiều người nghe, ILD 0,7211 cao hơn Popularity 0,6648 và thấp hơn hai CF. Chưa kết luận về họ mô hình hoặc chọn nền cuối từ một cấu hình/seed validation.

RMSE proxy bổ sung của checkpoint = **1.2439097807** trên 8.142 cặp, không có dự đoán held-out ngoài 1–5 ở run này; code vẫn không clip. RMSE này cao hơn hai CF dù ranking tốt hơn chúng. Train RMSE/objective giảm đều trong khi NDCG validation giảm qua sáu epoch: việc khớp tốt hơn điểm train chưa bảo đảm thứ hạng đích ẩn tốt hơn. Chỉ đây chưa đủ xác định nguyên nhân hoặc kết luận tác dụng của tuning; không tự đổi objective, patience, seed hay chọn thêm cấu hình sau kết quả.

Lần chạy đầu: fit phần SGD/chuẩn bị/đo loss 8,732634 giây, theo dõi validation 45,015899 giây, tổng fit có theo dõi 53,748533 giây. Recommend tổng 7,550701 giây, trung bình 4,022749 ms/user, phân vị 95% 4,435320 ms; evaluator 6,034926 giây. RMSE riêng 0,066220 giây; nạp và đối chiếu 1.877 danh sách 7,795826 giây. Ba tệp model chiếm **4.766.544 byte trên đĩa**, không phải bộ nhớ đỉnh. Thời gian chỉ thuộc lần chạy/môi trường này, không gồm I/O nguồn trong fit/recommend, không phải độ trễ API hoặc benchmark kiểm soát so với các model chạy thời điểm khác.

Artifact gồm CSR proxy trong model/ratings.npz, bốn mảng bias/factor trong model/parameters.npz, state giữ ID/mean/config/best_epoch/đường học/hash, learning_curve.csv, recommendations có score/reason, metrics tổng/từng user, mapping/transform, seed/version/Git SHA/trạng thái/diff và snapshot mã. Load dùng dữ liệu số không pickle, kiểm checksum/mapping/kích thước/giá trị/lịch sử rồi nạp checkpoint, không fit hoặc chạy chọn epoch. Đã nạp lại và khớp đủ 1.877 danh sách/score/reason; run `_recheck` trùng hash **10 tệp** dự đoán/chỉ số/model/mapping/transform/learning curve.

[Kiểm tra độc lập](../outputs/runs/svd_k32_validation_20261026/verification.json) không nhập model/evaluator production. Mã Python số vô hướng và fsum tái hiện đủ **445.650 cập nhật SGD** qua sáu epoch từ cùng train/khởi tạo/thứ tự RNG; đối chiếu train RMSE/objective và full-ranking NDCG mỗi epoch, quy tắc patience và checkpoint. Sai khác tham số tối đa **1,11023e-16**. Từ checkpoint độc lập tính lại mọi danh sách/score/reason, RMSE, từng metric user/K và Coverage/Gini/ARP/Novelty/ILD bằng NumPy/CSR; sai khác score tối đa 1,77636e-15, các chỉ số khớp trong 1e-12. Mã audit/guard và mã vẽ được giữ trong audit của run. **59 tests đạt; ruff check, ruff format --check và mypy toàn mã nguồn đạt**. Đối chiếu hash **47 tệp** xác nhận các đầu ra baseline trước và cả 11 Word giữ nguyên.

Đây là bằng chứng riêng Bước 11; kết quả PureSVD nằm ở mục Bước 12 bên dưới. GitHub chỉ nhận mã/cấu hình/tài liệu; dataset, model, run và hình giữ cục bộ theo .gitignore. Word giữ Bước 6; tinh chỉnh CF/MF vẫn là các lần cho phép riêng. Chưa học thẻ, M1/M2 hoặc đánh giá test.

## Bước 12 PureSVD 32 chiều trên proxy train ngày 26/10/2026

Run chốt: [pure_svd_k32_proxy_validation_20261026](../outputs/runs/pure_svd_k32_proxy_validation_20261026/metrics.json). [PureSVDRecommender](../src/musicrec/recommenders/pure_svd.py), [CLI](../scripts/run_pure_svd.py) và [cấu hình](../configs/models/pure_svd.yaml) dùng **32 chiều, seed 42**, biểu diễn proxy_score 1–5 đã học ngưỡng ở Bước 5. Đây là lượt đầu theo kế hoạch, không thử 16/64/128 chiều hoặc nhị phân/log trong bước này. Chỉ đọc train/validation/mapping/transform có hash; không mở test kể cả để băm, không học lại ngưỡng và không dùng validation chọn epoch.

Căn cứ là **Cremonesi, Koren, Turrin (2010), Performance of Recommender Algorithms on Top-N Recommendation Tasks**, [DOI](https://doi.org/10.1145/1864708.1864721), đối chiếu mục 3.3.1/công thức 4–6 ở trang PDF 4 của [bản gốc lưu trong dự án](TLTK/Cremonesi%20et%20al.%202010.pdf). Bài báo dựng ma trận zero-fill và viết R_hat=U_k Sigma_k V_k.T, P=R V_k. Nhóm chuyển sang proxy lượt nghe và full-ranking protocol hiện hành; 32 chiều, seed/vector bắt đầu, thư viện, tolerance, xử lý tie/cold-start là lựa chọn của nhóm. Không sao chép protocol lọc head items hoặc số đo MovieLens/Netflix của bài báo sang kết quả HetRec.

R là CSR float64 user × artist, quan sát nhận đúng proxy train; ô thiếu bằng 0 của bài toán phân rã. Không trừ mean, chuẩn hóa user/item, thêm bias hoặc confidence. PureSVD xấp xỉ ma trận gồm cả các ô 0, khác SGD chỉ qua cặp quan sát ở Bước 11; giá trị 0 đại số không biến thành bằng chứng user đã không thích artist. Score = (R V32) V32.T; với các singular vectors tương ứng, bằng U32 Sigma32 V32.T. Không nhân Sigma lần nữa sau khi đã lấy R V32, không gọi đây là MF có bias hoặc implicit ALS/BPR/SVD++.

Dùng scipy.sparse.linalg.svds với solver=arpack, which=LM, tolerance=1e-10, maxiter=10000, ncv mặc định SciPy. Vector v0 do Generator(PCG64(42)) lấy normal chuẩn có độ dài min(shape); không dựa RNG toàn cục. Sắp singular values giảm dần, quy ước phần tử có trị tuyệt đối lớn nhất mỗi right singular vector mang dấu dương rồi mới tính hồ sơ R V32. CLI giới hạn OPENBLAS/MKL/OMP/BLIS một luồng trước import NumPy. Fit không dựng toàn R đặc hoặc ma trận item–item đặc; chỉ giữ train CSR và các mảng 32 chiều. Không có SGD, learning rate, epoch/dừng sớm hoặc loss trên validation.

Score là mức liên hệ, không được hiệu chuẩn thành điểm proxy hoặc xác suất. Giữ cả score âm/lớn hơn 5, không clip; không tính RMSE theo quy tắc đánh giá hiện hành. Khóa sort làm tròn 12 chữ số rồi theo mapping số; score gốc vẫn lưu. Recommend loại lịch sử train đã biết và lịch sử truyền thêm, rank toàn catalog chưa nghe. Predict từ chối artist ngoài catalog. User mới chưa có hồ sơ cho score 0, reason pure_svd_zero_profile_cold_start và thứ tự ID cố định sau lọc seen; chưa cá nhân hóa và chưa phải M2/fold-in từ hồ sơ mới.

Ví dụ kiểm tra trên ma trận nhỏ dùng cùng các quan sát Bước 9, với artist cuối mang ID 10: NumPy SVD đặc và PureSVD rank 2 cùng cho score user 1–artist 3 khoảng 0.4925372, user 1–artist 4 khoảng 0.4877902; user 3–artist 3 khoảng −0.4379825 được giữ nguyên. Hai singular values đầu khoảng 8.7619541 và 4.8101650. Ví dụ đối chiếu score cho cả 20 ô kiểm được zero-fill, không bias và không nhân Sigma hai lần; đây là kiểm tra số học, không phải tuning rank 2 trên dữ liệu thật.

Run trả đủ 20 mục cho 1.877 user (37.540 dòng), cùng catalog 15.398 artist và cohort 1.865 user/8.142 đích hợp lệ như năm baseline trước. Báo riêng 12 user không còn đích và 1.121 đích ngoài catalog. Không có mục trùng/đã nghe/ngoài catalog, danh sách thiếu/rỗng. Phép thử chính chỉ có user đã xuất hiện trong train, không xác nhận chất lượng cold-start.

| K | Precision | Recall | NDCG | Coverage | Gini | ARP (listener) | Novelty (bit) | ILD |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 0.1053083110 | 0.1147363718 | 0.1228661940 | 0.0175996883 | 0.9924219747 | 160.7062734584 | 9.3263286074 | 0.7829309336 |
| 10 | 0.0780160858 | 0.1694459339 | 0.1516922327 | 0.0235095467 | 0.9896366681 | 143.9861662198 | 9.5238269876 | 0.8189157312 |
| 20 | 0.0571313673 | 0.2492850760 | 0.1844239434 | 0.0340953371 | 0.9857275883 | 126.3793029491 | 9.7564753725 | 0.8554517654 |

Tìm trúng 982/1.455/2.131 cặp đích và phủ 271/362/525 artist tại K=5/10/20. NDCG@10 **0.1516922327** cao hơn Popularity 0.0623622664, SVD có độ lệch 0.0564899628, UserCF 0.0080787555, ItemCF 0.0074299548 và Random 0.0003721497 ở các lượt đầu hiện có. Không gọi đây là xác nhận test, kiểm định thống kê, kết quả qua nhiều seed hoặc cấu hình cuối. Sáu baseline đã có lượt đầu, chưa hoàn thành tuning/so sánh biểu diễn/tổng hợp validation Bước 14.

Coverage@10 **362/15.398 = 2,3509547%** cao hơn Popularity 0,1818% và SVD có bias 0,5325%, thấp hơn hai CF. ARP 143,9862 thấp hơn Popularity 351,8290/SVD có bias 317,0872, nhưng cao hơn hai CF; ILD 0,8189 cao hơn Popularity 0,6648 và SVD có bias 0,7211, thấp hơn UserCF 0,9669/ItemCF 0,8329. Danh sách vẫn tập trung vào một phần nhỏ catalog; không suy ra thắng mọi tiêu chí, giảm bias cho mọi nhóm hoặc chốt nền M1 từ một cấu hình.

Sai số trực giao tối đa của các right singular vectors là 7,32747e-15; residual tương đối của R.T R V − V Sigma^2 là 7,54508e-15. 32 chiều giữ khoảng **25,4974% năng lượng Frobenius** của R zero-fill; đây là kiểm tra phân rã, không phải độ chính xác ranking hoặc tiêu chí chọn lại rank. Qua toàn ứng viên chưa nghe, score độc lập nằm khoảng −2,35707 đến 5,69842; giữ nguyên và không diễn giải như sao thật. Không tính RMSE ngay cả khi đầu vào dùng proxy 1–5.

Lần chạy đầu: fit 0,128760 giây, recommend tổng 5,882082 giây, trung bình 3,133768 ms/user, phân vị 95% 4,265300 ms; evaluator 3,302471 giây. Nạp/đối chiếu đủ 1.877 danh sách 6,991761 giây. Ba tệp model chiếm **3.203.557 byte trên đĩa**, không phải bộ nhớ đỉnh. Số đo thuộc lần chạy/môi trường hiện tại, không gồm I/O nguồn trong fit/recommend và không phải benchmark kiểm soát/độ trễ API.

Artifact gồm train CSR trong model/ratings.npz; components V32.T, user_embeddings R V32 và singular_values trong model/projection.npz; state giữ ID/config/diagnostics/hash. Load kiểm checksum/mapping/kích thước/giá trị, thứ tự singular values, tính trực giao và nhất quán hồ sơ đã lưu; không fit hoặc phân rã lại. Nạp lại khớp 1.877 danh sách/score/reason. recommendations.csv, metric tổng/từng user, mapping/transform, seed/runtime/Git SHA/trạng thái/diff và snapshot mã được giữ cùng run. Run `_recheck` trùng hash **9 tệp** kết quả/model/mapping/transform.

[Kiểm tra độc lập](../outputs/runs/pure_svd_k32_proxy_validation_20261026/verification.json) không nhập model/evaluator production hoặc gọi svds/ARPACK: dựng Gram user–user 1.877 × 1.877 rồi dùng scipy.linalg.eigh, suy ra leading singular values và right subspace, tái dựng score theo U32 Sigma32 V32.T. Gram kiểm toán chiếm 28.185.032 byte, không phải cấu trúc fit của model hoặc bộ nhớ đỉnh. Sai khác singular values tối đa **8,81073e-13**, subspace alignment 7,99361e-15, score toàn catalog 1,54876e-13 và score đã xuất 1,26121e-13. Mọi danh sách/score/reason và metric từng user/K, Coverage/Gini/ARP/Novelty/ILD khớp; chỉ số trong 1e-12, score trong 1e-10. Mã audit và guard chặn mở test.parquet được lưu trong audit của run; có hash PDF nguồn.

**63 tests đạt; ruff check, ruff format --check và mypy toàn mã nguồn đạt**. Kiểm thử dùng SVD đặc trên toy, kiểm score âm/không clip/masking/tie/cold-start, đảo thứ tự dòng/đổi count gốc không đổi kết quả, save/load không gọi fit hoặc svds, CLI 32 chiều không tính RMSE, hash và chống ghi đè/nguồn bị sửa. Hash **59 tệp** xác nhận các đầu ra năm baseline trước và cả 11 Word giữ nguyên. Dataset/model/run giữ cục bộ theo .gitignore; GitHub chỉ nhận mã/cấu hình/tài liệu. Word chưa chứa Bước 7–12, vẫn là bản Bước 6.

Dừng giải thích Bước 12 trước khi người dùng cho tiếp tục. Kết quả Bước 13 so sánh nhị phân/log/proxy nằm bên dưới; tuning số chiều vẫn cần cho phép riêng. Chưa học thẻ, M1/M2 hoặc đánh giá test.

## Bước 13 so sánh biểu diễn PureSVD ngày 26/10/2026

Câu hỏi thực nghiệm: thay giá trị các cặp đã nghe bằng nhị phân, log hoặc proxy ảnh hưởng thế nào đến ranking validation tại **cùng 32 chiều, seed 42**? Đối chứng là [run proxy Bước 12](../outputs/runs/pure_svd_k32_proxy_validation_20261026/metrics.json); hai run mới là [nhị phân](../outputs/runs/pure_svd_k32_binary_validation_step13_20261026/metrics.json) và [log](../outputs/runs/pure_svd_k32_log_validation_step13_20261026/metrics.json). Ghi trước câu hỏi, đối chứng, ngân sách và tiêu chí trong experiment.json thuộc audit cục bộ. Ngân sách gồm hai biểu diễn mới, một lần lặp mỗi biểu diễn và một lần lặp proxy: năm fit cố định, không tìm rank/seed/hyperparameter. Chỉ đo độ nhạy, chưa khóa lựa chọn cuối hoặc dùng test xác nhận.

Căn cứ phép phân rã vẫn là Cremonesi, Koren, Turrin (2010), [DOI](https://doi.org/10.1145/1864708.1864721), mục 3.3.1/công thức 4–6 của [bản PDF](TLTK/Cremonesi%20et%20al.%202010.pdf). Việc so ba biểu diễn trên HetRec, ngưỡng proxy và cấu hình cố định là thiết kế của nhóm; không nói bài gốc chứng minh nhị phân tối ưu hoặc đang tái hiện nguyên protocol của bài báo.

Giữ cùng 74.275 vị trí quan sát, split/mapping/catalog/evaluator, solver ARPACK/tolerance=1e-10/maxiter=10000, vector đầu PCG64(42), BLAS một luồng, không bias/centering/normalization. Chỉ đổi giá trị R: binary=1 cho mọi cặp; log=log2(1 + count), miền train 1 đến 18.42807796; proxy_score là 1–5 đã học ngưỡng trên train ở Bước 5. Runner đối chiếu chính xác cột binary/log đã chuẩn bị với phép biến đổi trước fit; model dùng cùng phép biến đổi cố định từ count gốc, không nhét giá trị log vào trường proxy hoặc nới contract điểm 1–5. Không học lại ngưỡng, không chuyển ô thiếu thành phản hồi tiêu cực và không dùng log làm confidence ALS.

Các config [nhị phân](../configs/models/pure_svd_binary.yaml), [log](../configs/models/pure_svd_log.yaml) và [proxy](../configs/models/pure_svd.yaml) chỉ khác representation; CLI vẫn khóa 32 chiều/seed 42. Score R V32 V32.T không clip/hiệu chuẩn thành rating hoặc xác suất, không tính RMSE. ILD luôn dùng cosine hồ sơ nghe **nhị phân train**, ARP luôn dùng số user train đã nghe artist, relevance held-out vẫn nhị phân; không đổi thước đo theo biểu diễn model. Cả ba trả 20 mục cho 1.877 user và cùng cohort 1.865 user/8.142 đích hợp lệ, loại và báo riêng 12 user không có đích trong catalog/1.121 đích ngoài catalog. Không có duplicate/seen/unknown hoặc danh sách thiếu/rỗng.

| Biểu diễn | K | Precision | Recall | NDCG | Coverage | ARP (listener) | ILD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Nhị phân | 5 | 0.1084182306 | 0.1181501340 | 0.1259680906 | 0.0180542928 | 161.7095978552 | 0.7811167805 |
| Nhị phân | 10 | 0.0809651475 | 0.1758891868 | **0.1564272628** | 0.0238992077 | 145.3087935657 | 0.8172029176 |
| Nhị phân | 20 | 0.0582573727 | 0.2550402145 | 0.1887078641 | 0.0337056761 | 128.2636729223 | 0.8543787909 |
| Log | 5 | 0.1067024129 | 0.1159696157 | 0.1243521267 | 0.0178594623 | 159.7311528150 | 0.7815892562 |
| Log | 10 | 0.0795174263 | 0.1732618409 | 0.1545766607 | 0.0242888687 | 143.4903485255 | 0.8184487864 |
| Log | 20 | 0.0578284182 | 0.2529490617 | 0.1872587832 | 0.0340953371 | 126.1913941019 | 0.8548078003 |
| Proxy 1–5 | 5 | 0.1053083110 | 0.1147363718 | 0.1228661940 | 0.0175996883 | 160.7062734584 | 0.7829309336 |
| Proxy 1–5 | 10 | 0.0780160858 | 0.1694459339 | 0.1516922327 | 0.0235095467 | 143.9861662198 | 0.8189157312 |
| Proxy 1–5 | 20 | 0.0571313673 | 0.2492850760 | 0.1844239434 | 0.0340953371 | 126.3793029491 | 0.8554517654 |

Coverage là tỷ lệ trên 15.398 artist, không phải phần trăm trong bảng. Ở K=10, nhị phân/log/proxy tìm trúng 1.510/1.483/1.455 cặp và phủ 368/374/362 artist (2,3899%/2,4289%/2,3510%). Gini tương ứng 0.9895695447/0.9895790791/0.9896366681; novelty 9.5019819854/9.5217928426/9.5238269876 bit. Bảng CSV/JSON trong run giữ toàn bộ chỉ số và từng user/K.

NDCG@10 nhị phân cao hơn proxy **0.0047350301 tuyệt đối, 3,1215% tương đối**; log cao hơn **0.0028844280 tuyệt đối, 1,9015% tương đối**. Nhị phân cao nhất NDCG ở cả ba K trong phép thử cố định này, nhưng ARP@10 cao hơn và ILD@10 thấp hơn hai biểu diễn còn lại; log phủ nhiều artist Top-10 nhất. So từng user với proxy, nhị phân có 507 tăng/440 giảm/918 hòa NDCG@10; log có 421 tăng/371 giảm/1.073 hòa (ngưỡng so sánh 1e-12). Không phải mọi user cùng cải thiện. Chưa có kiểm định ý nghĩa thống kê, nhiều seed/split, tuning rank hoặc test xác nhận; chưa kết luận một biểu diễn luôn tối ưu, nguyên nhân thắng hay nền M1 cuối. Tỷ lệ năng lượng Frobenius giữ lại (nhị phân 21,2626%, log 24,4498%, proxy 25,4974%) thuộc các ma trận khác nhau, không dùng để xếp hạng chất lượng giữa biểu diễn.

Lần chạy đầu nhị phân: fit 0,128636 giây, recommend tổng 6,361797 giây, trung bình 3,389343 ms/user, p95 4,038860 ms; evaluator 3,407793 giây; ba tệp model 2.895.881 byte. Log: fit 0,129892 giây, recommend tổng 6,643907 giây, trung bình 3,539642 ms/user, p95 4,674000 ms; evaluator 3,178913 giây; model 4.656.213 byte. Các số này không phải benchmark kiểm soát, bộ nhớ đỉnh hoặc độ trễ API; không gồm I/O nguồn trong fit/recommend và không dùng chênh thời gian nhỏ để chọn biểu diễn.

Kiểm tra độc lập [nhị phân](../outputs/runs/pure_svd_k32_binary_validation_step13_20261026/verification.json) và [log](../outputs/runs/pure_svd_k32_log_validation_step13_20261026/verification.json) đọc trực tiếp **cột biểu diễn đã chuẩn bị**, dựng Gram user–user rồi dùng eigh, không gọi model/svds/evaluator production. Đối chiếu đủ 32 singular values/không gian chiếu, mọi score ứng viên, 1.877 danh sách/score/reason và từng chỉ số user/K. Sai khác score toàn catalog tối đa 1,18794e-14 cho binary và 1,29674e-13 cho log; score trong 1e-10, metric trong 1e-12. Guard audit chặn mọi lần mở test.parquet, kể cả băm. Điểm ứng viên có thể âm: binary khoảng −0,52722 đến 1,30517, log −6,82941 đến 12,20125; vẫn giữ nguyên, không gọi là xác suất.

Mỗi biểu diễn mới nạp lại không fit/phân rã và khớp đủ 1.877 danh sách. Mỗi run `_recheck` trùng hash **9 tệp** kết quả/model/mapping/transform. [Lặp đối chứng proxy bằng mã mới](../outputs/runs/pure_svd_k32_proxy_control_validation_step13_20261026/metrics.json) cũng khớp đúng 9 tệp đã ghi ở Bước 12, gồm state/model; artifact proxy cũ vẫn nạp được nhờ giá trị mặc định. Bản chụp mã/config/runtime/Git SHA/trạng thái/diff, experiment.json, mã kiểm tra/guard và hash bảo toàn được giữ trong audit cục bộ. Đối chiếu 113 tệp xác nhận đầu ra các bước trước và 11 Word giữ nguyên. Chưa tổng hợp/chốt validation Bước 14, tuning, học thẻ/M1/M2 hoặc đánh giá test. Word vẫn Bước 6; Git chỉ nhận mã, cấu hình và các tài liệu làm việc hiện có.

[Tổng hợp máy đọc được của phép so Bước 13](../outputs/runs/pure_svd_representations_validation_20261026/metrics.json), [bảng đủ ba K](../outputs/runs/pure_svd_representations_validation_20261026/metrics.csv) và [NDCG@10 từng user theo cặp](../outputs/runs/pure_svd_representations_validation_20261026/paired_ndcg_at_10.csv) giữ liên kết/hash tới từng run, cấu hình và bằng chứng kiểm chứng. **67 tests đạt; ruff check, ruff format --check và mypy toàn mã nguồn đạt**. Kiểm thử mới so phân rã SVD đặc trên toy cho binary/log (log không nguyên và có thể lớn hơn 5), save/load, từ chối count không hữu hạn, CLI ba biểu diễn/khóa rank, sai transform dù hash được cập nhật, checksum và chống ghi đè. Không thêm thư viện hoặc tài liệu tiến độ mới.
