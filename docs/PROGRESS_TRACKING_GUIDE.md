# Phối hợp và giải thích tiến độ khóa luận

Cập nhật ngày 19/10/2026 theo [hướng dẫn của GVHD](Hướng%20dẫn%20từng%20bước%20hoàn%20thành%20khóa%20luận.docx), [kế hoạch từng bước](WEEKLY_IMPLEMENTATION_PLAN.md) và [quy tắc phát triển](../DEVELOPMENT_RULES.md). Tài liệu này thay quy trình quản lý 12 tuần có ngày cố định trước đây.

Mục tiêu là biết đã làm gì, kết quả ở đâu và vì sao chọn cách đó, đồng thời bảo đảm cả hai thành viên hiểu để bảo vệ. Không bắt buộc thiết lập GitHub Projects, MLflow, tự động hóa báo cáo hoặc hệ thống chấm điểm tiến độ.

## Theo dõi hạn demo cuối tháng 11

Lịch mục tiêu là 19/10–30/11/2026; ngày/giờ nộp chính xác chờ thông tin thực tế, chưa coi hạn demo là hạn nộp toàn bộ khóa luận. Mốc nội bộ: 25/10 dữ liệu/evaluator và hai baseline; 01/11 UserCF/ItemCF; 08/11 sáu baseline; 15/11 chọn mô hình sau M1/M2 và đánh giá; 22/11 demo đủ luồng; 27/11 sẵn sàng nộp; 28–30/11 dự phòng.

- Cuối mỗi mốc đối chiếu minh chứng ngay trong chat: đã xong gì, còn thiếu gì, ảnh hưởng mốc tiếp theo và đề xuất điều chỉnh. Không ghi phần chưa làm là hoàn thành để giữ lịch.
- Nếu trễ trước 08/11, dừng mở rộng thí nghiệm, ưu tiên correctness và các baseline trong phạm vi đã chốt; việc giảm lưới chưa chạy cần giải thích trước thực hiện.
- Nếu M1/M2 chưa được kiểm chứng trước 15/11, đề xuất người dùng chốt phạm vi demo trên mô hình nền đã kiểm chứng và fallback trung thực. Không tự coi đề xuất là được duyệt hoặc ghi M1/M2 đã hoàn thành.
- Từ 23/11 ưu tiên sửa lỗi, kiểm tra môi trường sạch, hướng dẫn chạy và luyện demo; không thêm tính năng hoặc quay lại chọn siêu tham số bằng test.
- Không tự tạo lịch nhắc, gửi tin cho cô hoặc chuyển bước theo ngày. Các điểm dừng trao đổi vẫn áp dụng; khi chưa được phép tiếp tục thì báo ảnh hưởng lịch thay vì tự chạy.

## Một bước làm việc

Trạng thái sau Bước 14 ngày 26/10/2026: đã tổng hợp tám cấu hình thuộc sáu họ baseline, gồm sáu fit xác nhận seed bổ sung cho Random/SVD/PureSVD nhị phân, giữ split seed 42. NDCG@10 mean ± sample std qua model seed 42/43/44: PureSVD nhị phân 0.1564272628 ± 0, SVD 0.0576259192 ± 0.0010411842, Random 0.0004124977 ± 0.0001408550. Popularity 0.0623622664 vẫn vượt SVD cả ba seed. Nhóm lịch sử train <40/=40/>40 có 41/1.822/2 user hợp lệ, không kết luận rộng từ nhóm chỉ hai user. [Data card](data-card.md) giữ toàn bộ bảng chất lượng/chi phí/nhóm/seed và bằng chứng kiểm chứng; 69 tests/lint/format/mypy đạt. PureSVD nhị phân là ứng viên M1 của các cấu hình hiện có; chưa tuning hoặc khóa nền. Baseline/protocol/lịch hiện đủ điều kiện đề xuất bước ALS riêng trước 15/11, chưa cài/huấn luyện mở rộng. Word giữ Bước 6; dừng Bước 14, chờ quyết định nhánh mở rộng hoặc duyệt thiết kế M1, chưa chạy M1/M2/test.

Cập nhật sau phép riêng của người dùng: lượt ALS đầu tiên (32 factors/reg 0.1/a_conf 1/seed 42) đã hoàn thành, tốt nhất vòng 18/dừng 23, NDCG@10 0.1974107044 so PureSVD nhị phân 0.1564272628; coverage tăng, ARP giảm, ILD giảm nhẹ. Đã đo fit/monitor/recommend, OS peak working set và artifact; 73 tests/lint/format/mypy cùng kiểm toán độc lập đạt. Nguồn thực nghiệm mới ưu tiên 2022–2026 theo yêu cầu, có kiểm định nghĩa metric/nhãn preprint. Đề xuất ưu tiên xác nhận hai seed còn lại trước tuning hoặc M1; chưa chạy 43/44 hoặc đổi nền, chưa BPR/SLIM/M1/M2/test. Kế hoạch mốc chính giữ nguyên; Word vẫn Bước 6.

Trạng thái sau điều chỉnh đã được cho phép: xác nhận ALS seed 43/44 xong, tổng hợp lại 17 run cùng cohort/catalog/protocol. ALS NDCG@10 **0.1965852193 ± 0.0014783714** qua ba seed, thắng đối chứng PureSVD nhị phân **3/3 seed**, tăng mean 25,6720%; qua điều kiện giữ đã chốt. Cập nhật ứng viên nền M1 sang ALS cùng cấu hình, seed 42 tham chiếu, không chọn seed đẹp nhất. **76 tests/lint/format/mypy đạt**; kiểm toán độc lập, bốn CSV tổng hợp trùng hash, 219 tệp cũ/11 Word giữ nguyên. Tuning tiếp tục hoãn; chưa BPR/SLIM/M1/M2/test. Việc kế tiếp là duyệt thiết kế Bước 15 M1; chưa triển khai reranker hoặc khóa mô hình cuối.

1. Xác nhận bước được phép, mục tiêu, đầu vào, đầu ra và những việc chưa thuộc bước đó.
2. Trước khi thực hiện, giải thích căn cứ tài liệu và lựa chọn riêng; chỉ cần kiến thức đủ để hiểu công việc sắp làm.
3. Khi đến bước code/thực nghiệm, kiểm tra logic trên ví dụ nhỏ trước; lưu kết quả thật cùng cấu hình.
4. Cuối bước trình bày minh chứng, giới hạn và câu hỏi tự kiểm tra.
5. Dừng chờ người dùng cho chuyển bước. Có kế hoạch đầy đủ không phải quyền chạy liên tục.

Với UserCF, ItemCF, SVD có độ lệch và PureSVD, cấu hình đầu và tinh chỉnh là các lần làm riêng. M1/M2 có lần trao đổi thiết kế trước khi chạy.

### Nhánh khảo sát mở rộng ngày 24/10/2026

- Đã khảo sát implicit ALS và BPR-MF là hai ứng viên ưu tiên, SLIM là dự phòng; chưa có kết quả mô hình hoặc thay đổi sáu baseline chính. Thiết kế lượt đầu, trần 8/8/4 cấu hình và tiêu chí giữ nằm trong [kế hoạch hiện hành](WEEKLY_IMPLEMENTATION_PLAN.md#thực-nghiệm-bổ-sung-có-giới-hạn); nguồn ở [khảo sát tài liệu](TONG_QUAN_TAI_LIEU_THAM_KHAO.md#khao-sat-mo-rong-20261024).
- Chỉ xét thử sau khi sáu baseline có validation hợp lệ, trước chốt nền M1 và khóa test, nếu không ảnh hưởng M1/M2 hoặc mốc 15/11. Trễ mốc baseline 08/11 hoặc thiếu thời gian thì chuyển nhánh phụ sau demo; giữ mốc 22/11, 27/11 và quỹ dự phòng.
- Với từng ứng viên, tách cho phép triển khai/lượt chạy đầu → giải thích số đo và chi phí → cho phép tinh chỉnh → kiểm tra cấu hình được chọn. Đồng ý khảo sát không cho phép tự cài thư viện, tạo config hoặc train.
- Đổi nền M1 cần đánh giá lại M1 cùng ablation; M2 vẫn dùng ItemCF theo thiết kế riêng. Test đã mở không dùng để chọn lại mô hình của đợt đã khóa.
- Chưa sửa báo cáo Word ở bước khảo sát. Khi kết quả đủ căn cứ, rút gọn diễn giải hoặc chuyển chi tiết xuống phụ lục để dành chỗ; giữ bảng kết quả của mọi mô hình đã chạy, kể cả không cải thiện.

## Nội dung giải thích cuối bước

Không tạo tệp nhật ký hoặc Word tiến độ mới. Trình bày trong chat theo sáu mục:

1. **Việc đã làm:** tệp thay đổi, lý do và phạm vi đã hoàn thành.
2. **Bằng chứng:** bảng/hình/ví dụ hoặc kết quả kiểm tra thực tế. Chưa chạy thì ghi chưa có số liệu.
3. **Căn cứ:** bài báo/README nào được dùng; lựa chọn nào của nhóm; có phải tái hiện chính xác không.
4. **Diễn giải:** kết quả có nghĩa gì, chưa chứng minh điều gì, có lỗi hoặc kết quả không cải thiện không.
5. **Tự kiểm tra:** 2–3 câu hỏi bảo vệ cùng trả lời ngắn; nếu chưa hiểu, giải thích lại trước chuyển bước.
6. **Báo cáo Word:** chỉ sửa hoặc xuất bản mới khi người dùng yêu cầu rõ ràng, theo yêu cầu mới nhất ngày 25/10/2026. Không tự cập nhật sau từng bước hoặc khi chạy hết mô hình; kết quả mới vẫn lưu ngay trong run và tài liệu làm việc hiện có.

Bước quản lý hoặc chỉ sửa tài liệu dùng chính tài liệu nguồn làm căn cứ; không đòi có bài báo hay metric mới.

## Phân công hai thành viên

| Trách nhiệm tham khảo | Người phụ trách chính | Người đọc chéo |
| --- | --- | --- |
| Dữ liệu, EDA, evaluator và phân tích | Cao Trọng Nguyên | Lê Khắc Gia Khang |
| Mô hình và prototype khi đến bước | Lê Khắc Gia Khang | Cao Trọng Nguyên |
| Lựa chọn phương pháp, kết luận và báo cáo | Cả hai cùng hiểu và thống nhất | Cả hai |

Một người phụ trách một việc tại một thời điểm; giao diện chung có một người sửa chính. Không phân công theo kiểu mỗi người chỉ biết một nửa khóa luận. Không tự nhắn cho thành viên khác hoặc GVHD.

## Dùng Git và công cụ hiện có

- Dùng Git ghi nhận thay đổi với mục tiêu rõ; không tự commit/push thay người dùng nếu chưa được yêu cầu.
- Khi chuẩn bị PR, tuân thủ review và CI của repository. Hoàn thành bước trong chat không đồng nghĩa PR đã merge hoặc hệ thống đã phát hành.
- Có thể liên kết issue/PR nếu nhóm đang dùng; không bắt buộc tạo board/issue cho mọi trao đổi hoặc thay đổi Markdown nhỏ.
- Run thực nghiệm lưu cấu hình, seed, phiên bản mã, hash dữ liệu/split, dự đoán, metric và thời gian. MLflow/DVC là công cụ tùy nhu cầu, không thay minh chứng.
- Không dùng số commit, dòng code, giờ online hoặc phần trăm tự nhập để suy ra mức hiểu hay đóng góp.
- Không tạo checker tiến độ, scheduled Action, báo cáo tuần tự sinh hoặc thêm công cụ quản lý khi chưa có nhu cầu và yêu cầu cụ thể.

## Trao đổi với GVHD

Hướng dẫn đề xuất nhịp hằng tuần hoặc hai tuần/lần. Người dùng thống nhất lịch thực tế với cô; trợ lý chỉ chuẩn bị nội dung khi được yêu cầu, không tự gửi hoặc tạo nhắc việc.

Nội dung gọn: bước vừa hoàn thành và minh chứng; khó khăn cụ thể; quyết định cần cô góp ý; bước tiếp theo. Thay đổi mô hình hay thử nghiệm so với hướng dẫn cần nêu mục đích và cách kiểm chứng, không tự ghi là cô đã duyệt.

## Điều kiện hoàn thành và các điểm cần dừng

- Tài liệu: đúng nguồn, phân biệt kế hoạch với thực tế, liên kết hợp lệ và không mâu thuẫn phương pháp hiện hành.
- Dữ liệu: bảo toàn/giải thích số lượng, đúng schema và đúng quy tắc chống rò rỉ.
- Mô hình: ví dụ tính tay phù hợp, điểm hữu hạn, loại lịch sử, thứ tự ổn định, xuất/nạp đúng.
- Thực nghiệm: cùng protocol, chỉ validation chọn cấu hình, có kết quả truy vết và kết luận đúng giới hạn.
- Prototype: chỉ làm sau thực nghiệm; offline/API nhất quán, thử môi trường sạch và demo được.
- Phát hiện cặp trùng count khác nhau, nguồn không rõ, leakage hoặc evaluator sai: giải thích và giải quyết trong phạm vi được phép trước khi chuyển tiếp.
- Kết quả không cải thiện vẫn là kết quả hợp lệ; không thay split, lọc đuôi dài hoặc mở test để tìm bảng đẹp hơn.
