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
10. Quyết định ảnh hưởng dataset, split, metric, model interface hoặc API contract phải được giải thích trong cuộc trò chuyện và ghi trong cấu hình thực nghiệm. Chỉ cập nhật báo cáo Word khi người dùng yêu cầu rõ ràng; không tự cập nhật theo bước hoặc sau khi chạy hết mô hình. Không bắt buộc tạo ADR hoặc tài liệu mới.

## Quy ước mã nguồn

- Python 3.11+, type hints cho hàm public, docstring cho module/class public.
- Logic reusable nằm trong `src/`; script chỉ điều phối I/O và CLI.
- Không dùng notebook làm nguồn chân lý cho pipeline hoặc kết quả báo cáo.
- Tên config và artifact phải ổn định, dùng `snake_case`; model release dùng `vMAJOR.MINOR.PATCH`.
- Lỗi API trả schema rõ ràng, không để stack trace lộ ra client.

## Dữ liệu và báo cáo

- Ghi nguồn, ngày tải, license, checksum và schema trong `docs/data-card.md`.
- Mọi bảng/hình báo cáo phải truy xuất được về một run có cấu hình, seed, phiên bản mã, mã băm dữ liệu và kết quả thật; không bắt buộc bổ sung MLflow hoặc công cụ quản lý thí nghiệm khác.
- Không kết luận mô hình “tốt hơn” chỉ dựa vào một metric: báo cáo cả accuracy, coverage/diversity và chi phí suy luận.

## Vận dụng hướng dẫn của GVHD

- Nguồn hướng dẫn là [Hướng dẫn từng bước hoàn thành khóa luận](docs/huong-dan-gvhd/H%C6%B0%E1%BB%9Bng%20d%E1%BA%ABn%20t%E1%BB%ABng%20b%C6%B0%E1%BB%9Bc%20ho%C3%A0n%20th%C3%A0nh%20kh%C3%B3a%20lu%E1%BA%ADn.docx). Lộ trình hiện hành nằm trong [kế hoạch từng bước](docs/WEEKLY_IMPLEMENTATION_PLAN.md): hạn demo cuối tháng 11/2026, mốc lập kế hoạch 30/11 khi chưa có ngày/giờ cụ thể, hoàn thành nội bộ 27/11 và dự phòng 28–30/11. Khung 16 tuần của hướng dẫn chỉ giữ trình tự; không dùng làm lịch mới hoặc quyền thực hiện bước tiếp theo.
- Giữ nguyên tắc hiểu trước khi làm, EDA trước mô hình, kiểm tra evaluator bằng ví dụ tính tay, baseline trước cải tiến, validation trước test và cập nhật báo cáo theo bằng chứng thật.
- Theo yêu cầu ngày 26/10/2026, ưu tiên nghiên cứu gần đây khi đối chiếu thực nghiệm và đề xuất đổi kế hoạch: tìm nguồn gốc giai đoạn 2022–2026, ưu tiên bài 2024–2026 phù hợp bài toán, kiểm tra ngày/phiên bản và ghi rõ preprint. Không lấy tài liệu quá cũ làm căn cứ thực nghiệm chính cho quyết định mới hoặc chọn bài chỉ vì năm mới; phải kiểm tra dữ liệu, protocol, định nghĩa metric và khả năng tái lập. Các trích dẫn lịch sử đã có giữ nguyên; không tự sửa Word.
- Hướng dẫn không buộc sao chép đủ mọi mô hình/tham số/công cụ. Sáu baseline hiện hành là Random, Popularity, UserCF, ItemCF, SVD có độ lệch và PureSVD. Khảo sát ngày 24/10/2026 xác định implicit ALS và BPR-MF là hai ứng viên mở rộng ưu tiên, SLIM là dự phòng; chưa bổ sung vào nhóm baseline bắt buộc. Chỉ triển khai sau sáu baseline, trước khi chốt nền M1/test nếu còn thời gian và được người dùng cho phép từng bước; thiếu thời gian thì chuyển sau demo. Deep learning và dataset khác vẫn ngoài phạm vi mặc định.
- Phân biệt MF học bằng SGD với PureSVD/TruncatedSVD. Thư viện chỉ là công cụ hiện thực, không làm hai mô hình thành tương đương. Trước khi cài CF, giải thích được một ví dụ tính tay và cách chuyển công thức sang dữ liệu của nhóm.
- Biểu diễn, lọc và split chỉ là thiết kế cho đến khi được kiểm tra ở bước tương ứng. Không coi YAML cũ, số liệu seminar, hoặc kết quả nhánh độc lập là kết quả đã xác minh của quy trình mới.
- Bổ sung thí nghiệm phải nêu câu hỏi, căn cứ, đối chứng, ngân sách và tiêu chí chọn trước khi chạy; chỉ làm sau điểm dừng được người dùng cho phép. Không mở rộng phạm vi chỉ vì hướng dẫn hoặc một bài báo có nhiều mô hình hơn.
- Nhánh ALS/BPR-MF/SLIM dùng chung split/catalog/evaluator, chọn bằng validation và giữ giao diện fit/predict/recommend; chi tiết ở mục thực nghiệm bổ sung của kế hoạch hiện hành. Nếu đổi nền M1 thì đánh giá lại M1 và các đối chứng liên quan; không tự thay ItemCF của M2. Khi test đã mở, không dùng đợt mở rộng để chọn lại mô hình của đợt đã khóa.
- Khảo sát hoặc thiết kế nhánh mở rộng chưa làm phát sinh bản báo cáo Word mới. Chỉ cân nhắc đưa mô hình vào phần trình bày chính khi có kết quả ổn định và test xác nhận sau khóa cấu hình. Nếu cần dành chỗ, rút gọn diễn giải hoặc chuyển chi tiết xuống phụ lục; giữ bảng kết quả đầy đủ của các mô hình đã chạy, kể cả kết quả không cải thiện.
- Thống kê, ngưỡng, similarity, popularity và đặc trưng nội dung phải tuân thủ dữ liệu học được phép của từng protocol. Riêng M2 không dùng đóng góp tương tác/thẻ của user đánh giá để học thành phần chung.
- Ghi quyết định và giải thích trong chat, cấu hình và run thực tế; không tạo NHATKY.md, ADR mới hoặc báo cáo tiến độ song song. DVC/MLflow/GitHub Projects không phải điều kiện bắt buộc để làm nghiên cứu đúng.
- Chuẩn bị nội dung trao đổi với cô theo nhịp người dùng thống nhất; không tự gửi tin, xuất báo cáo gửi cô hoặc tạo lịch nhắc khi chưa được yêu cầu. Không ghi GVHD đã duyệt nếu chưa có xác nhận.
- Thay đổi chỉ Markdown phải kiểm tra nội dung, liên kết và diff; không chạy xử lý dữ liệu, huấn luyện hoặc mở kết quả test để xác minh tài liệu. Lượt cập nhật ngày 19/10/2026 chỉ thuộc phạm vi này.
- Bảo vệ mốc chọn mô hình 15/11 và demo chạy đủ luồng 22/11. Không kéo tuning hoặc tính năng mới vào 23–27/11; khi có nguy cơ trễ phải trình bày phương án thu hẹp phạm vi để người dùng chốt, không tự bỏ kiểm chứng, bước giải thích hoặc mục tiêu M1/M2.

## Làm việc theo từng bước

1. Dùng `khang-dev` tại `e80cfbf` làm nền cho kế hoạch làm lại. Nhánh `codex/musicrec-experiments-18-10-2026` chỉ giữ lịch sử đợt cũ; không tự đưa lại mã hoặc kết quả đó vào bản đang làm. Giữ `lastfm-reproduction` và đầu ra của nó độc lập.
2. Chỉ thực hiện bước người dùng đang cho phép. Đồng ý kế hoạch tổng thể không đồng nghĩa cho phép chạy toàn bộ kế hoạch. Hoàn thành một bước phải giải thích kết quả rồi dừng, chờ người dùng cho chuyển bước.
3. Tách riêng kiểm tra nguồn, EDA, làm sạch, chia tập, biểu diễn đầu vào, bộ đánh giá và từng mô hình. Không huấn luyện trong bước dữ liệu hoặc tự chạy test set trong lúc tinh chỉnh.
4. Với UserCF, ItemCF, SVD có độ lệch và PureSVD, chạy một cấu hình và tinh chỉnh là hai điểm dừng riêng. Chỉ làm M1/M2 sau các mô hình nền; trình bày thiết kế từng mô-đun trước khi chạy.
5. Cuối mỗi bước, giải thích: việc đã làm và tệp đã đổi; kết quả thật; bài báo làm căn cứ và lựa chọn riêng của nhóm; ý nghĩa và giới hạn; hai hoặc ba câu hỏi bảo vệ kèm câu trả lời ngắn. Ghi rõ nội dung mới đang lưu trong run/tài liệu làm việc; chỉ sửa Word khi người dùng yêu cầu rõ ràng. Bước quản lý mã nguồn không cần gán một bài báo làm căn cứ.
6. Giải thích đủ để người dùng hiểu đầu vào, đầu ra, lý do lựa chọn, cách kiểm chứng và giới hạn kết luận; không bắt buộc trình bày đầy đủ phép suy diễn toán học. Nêu rõ cả kết quả không cải thiện.
7. Không tạo thêm tài liệu kế hoạch hoặc báo cáo tiến độ Word/Markdown. Trao đổi nằm trong chat; kết quả kỹ thuật nằm trong run riêng và không ghi đè run cũ.

## Lưu phiên bản báo cáo khóa luận

1. Số đề tài của nhóm là **33**. Báo cáo lưu trong `docs/bao-cao/`, tên tệp theo mẫu `33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_vNN_DD-MM-YYYY.docx`: `vNN` là số phiên bản hai chữ số, tăng 1 mỗi lần cập nhật; ngày là ngày tạo bản tại Việt Nam (`Asia/Saigon`). Hai họ tên viết không dấu, nối bằng dấu gạch dưới.
   Mỗi phiên bản mới phải có một dòng trong [bảng phiên bản](docs/bao-cao/README.md): số phiên bản, ngày, người sửa, nội dung thay đổi, đã gửi GVHD hay chưa. Đọc bản hiện hành trong bảng trước khi cập nhật; giữ văn phong và cấu trúc hiện có nhưng sửa phương pháp hoặc nội dung sai khi có căn cứ.
   Ngày 26/10/2026, theo yêu cầu người dùng, thư mục báo cáo được dọn lại: chỉ giữ v01, v14 (bản đã gửi cô) và v15 (bản hiện hành). Các bản trung gian lấy lại từ commit `2615c35` (danh sách trong bảng phiên bản).
2. Theo yêu cầu mới nhất ngày 25/10/2026, chỉ cập nhật hoặc tạo bản Word khi người dùng yêu cầu rõ ràng. Không tự sửa Word sau mỗi bước, khi có kết quả mới hoặc khi chạy xong tất cả mô hình. Lưu bằng chứng trong run và cập nhật tài liệu làm việc hiện có; báo cáo Word giữ ở trạng thái lần bàn giao gần nhất cho đến khi được yêu cầu. Khi được yêu cầu, kế thừa bản mới nhất và xuất một bản khóa luận đầy đủ mới trong `docs/bao-cao/` với số phiên bản kế tiếp.
3. Giữ nguyên nội dung các bản trong `docs/bao-cao/`, kể cả tệp chưa commit. Không ghi đè; chỉ đổi tên, di chuyển hoặc xóa đầu ra khi người dùng yêu cầu rõ ràng. Khi đổi tên theo yêu cầu mới, cập nhật liên kết và xác minh mã băm không đổi.
4. Tạo tệp mới, không ghi đè bản cũ. Hai bản cùng ngày phân biệt bằng số phiên bản, không tạo thư mục con theo phiên bản. Không đổi ngày chỉ để tránh trùng tên.
5. Đồng bộ các chương liên quan, tóm tắt, bảng/hình và tài liệu tham khảo. Phân biệt thiết kế, ví dụ minh họa, phần đã triển khai và kết quả đã kiểm chứng; không biến mục tiêu kỳ vọng thành số đo hoặc ghi GVHD đã duyệt khi chưa có xác nhận.
   Văn bản báo cáo chỉ mô tả nhóm đã làm gì, phương pháp và kết quả; không chèn ngày/tháng thực hiện hoặc lịch tiến độ nội bộ vào phần trình bày. Ví dụ dùng “Nhóm đã áp dụng…” thay cho “Ngày DD/MM/YYYY, nhóm đã áp dụng…”. Lịch quản lý và thời điểm chạy giữ trong kế hoạch, run kỹ thuật và tên phiên bản; thông tin xuất bản/truy cập của tài liệu tham khảo vẫn theo quy cách trích dẫn.
6. Render và kiểm tra tất cả các trang Word trước bàn giao, gồm công thức, bảng và mục lục. Giữ bản nháp và ảnh QA ngoài thư mục báo cáo đã bàn giao; xác minh mã băm bản nguồn không đổi.
7. Bàn giao bản Word mới cùng tóm tắt phần đã sửa trong chat để người dùng đọc và tự gửi cô. Không tạo bản Markdown song song hoặc tự gửi báo cáo thay người dùng.
