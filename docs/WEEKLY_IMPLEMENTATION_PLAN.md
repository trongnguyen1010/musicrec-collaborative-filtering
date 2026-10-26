# Kế hoạch thực hiện khóa luận MusicRec theo từng bước

Cập nhật kết quả Bước 16 M2 ngày 26/10/2026 trên kế hoạch hiện hành, đối chiếu [Hướng dẫn từng bước hoàn thành khóa luận của GVHD](Hướng%20dẫn%20từng%20bước%20hoàn%20thành%20khóa%20luận.docx) và các lựa chọn đã trao đổi với người dùng. Word gần nhất vẫn là [báo cáo Bước 6](reports/33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_25-10-2026.docx); chỉ sửa Word khi người dùng yêu cầu rõ ràng. Bằng chứng Bước 7–16/ALS nằm trong run và tài liệu làm việc. Ưu tiên nguồn nghiên cứu 2022–2026; [đối chiếu M2](TONG_QUAN_TAI_LIEU_THAM_KHAO.md#doi-chieu-m2-20261026) dùng nguồn 2024 và phân biệt thiết kế riêng của nhóm.

Đây là kế hoạch cho các bước còn lại, không phải xác nhận đã hoàn thành toàn bộ thực nghiệm hoặc đã được GVHD duyệt. Đã hoàn thành Bước 1–16 trên validation theo phép người dùng. M1 qua gate @10; M2 chọn α=0.75/ngưỡng10 trên user tinh chỉnh tách biệt, giữ 189 user để dành. Tiếp theo là **Bước 17: khóa cấu hình/protocol rồi đánh giá cuối** khi được cho phép. Chưa tuning số chiều/CF/MF/ALS, khóa mô hình test, chạy BPR/SLIM hoặc đánh giá test. **Hạn nộp demo người dùng đã xác nhận là cuối tháng 11/2026.** Dùng ngày 30/11/2026 làm mốc lập kế hoạch khi chưa có ngày/giờ nộp cụ thể, hoàn thành nội bộ ngày 27/11 và giữ 28–30/11 làm dự phòng. Lịch này thay cả lịch 12 tuần cũ và nhịp 16 tuần tham khảo; không suy ra hạn nộp toàn bộ khóa luận từ hạn demo.

## 1. Mục tiêu và phạm vi

- Bài toán chính: xếp hạng Top-K **nghệ sĩ chưa có trong lịch sử quan sát** từ phản hồi nghe nhạc ngầm.
- Dữ liệu chính dự kiến giữ **HetRec 2011 Last.fm 2K** vì có trực tiếp người dùng–nghệ sĩ–lượt nghe và thẻ. Đổi dữ liệu vẫn được phép nếu kiểm tra nguồn/EDA cho thấy không phù hợp, nhưng phải giải thích ảnh hưởng trước khi triển khai.
- Sáu mô hình nền: Random, Popularity, UserCF, ItemCF, SVD có độ lệch và PureSVD.
- Khảo sát mở rộng ngày 24/10/2026: ưu tiên implicit ALS rồi BPR-MF, dự phòng SLIM. Chưa thay sáu baseline hoặc báo cáo Word; điều kiện thử sau baseline và trước khóa test nằm ở mục thực nghiệm bổ sung dưới đây.
- SVD có độ lệch là MF học nhân tố và bias bằng SGD trên điểm đại diện; PureSVD dùng phân rã ma trận. Không coi hai cách này là cùng một mô hình, không thay MF bằng TruncatedSVD rồi giữ nguyên tên/kết luận.
- M1: tái xếp hạng nhằm kiểm chứng đánh đổi giữa chất lượng, đa dạng và mức phổ biến.
- M2: kết hợp ItemCF từ hồ sơ, nội dung thẻ và Popularity cho người dùng chưa có tham số đã học hoặc ít lịch sử.
- Chương 5 và prototype được thực hiện sau khi đã chọn mô hình bằng thực nghiệm. Không làm API/UI song song để vượt qua các bước nghiên cứu còn thiếu.

Câu hỏi cần có minh chứng: RQ1 so sánh mô hình; RQ2 ảnh hưởng lịch sử/độ thưa; RQ3 đánh đổi của M1; RQ4 hiệu quả M2 ở các mức lịch sử; RQ5 tính đúng đắn và khả thi của prototype. Đối chiếu cách diễn đạt chính xác với bản báo cáo mới nhất trước khi xuất Word.

## 2. Vận dụng hướng dẫn của cô

| Nội dung hướng dẫn | Cách áp dụng trong dự án |
| --- | --- |
| Bốn giai đoạn trong 16 tuần | Giữ trình tự học → dữ liệu/mô hình → thực nghiệm → prototype, nhưng sắp vào lịch 19/10–30/11/2026 theo hạn demo. Ôn lý thuyết ngay trước bước cần dùng, tận dụng tài liệu đã có thay vì bắt đầu lại bốn tuần học. |
| Không tự chế số liệu, ghi lý do quyết định | Kết luận từ kết quả thật. Ghi trao đổi cuối bước trong chat và cấu hình/kết quả trong run; không tạo thêm NHATKY.md hoặc báo cáo tiến độ song song. |
| Hiểu nền tảng trước khi code | Tự giải thích thuật ngữ, tính ví dụ CF và độ đo bằng tay; học công cụ đúng lúc cần. |
| EDA trước mô hình, ngưỡng lọc có căn cứ | Tách kiểm tra nguồn, EDA và làm sạch. Không lọc nghệ sĩ đuôi dài chỉ để tăng chỉ số. |
| Một giao diện mô hình chung | Giữ fit, predict, recommend hiện có; evaluator dùng chung, tách khỏi mô hình. |
| Evaluator trước tinh chỉnh | Kiểm tra evaluator trước cả lần chạy baseline chính thức đầu tiên. |
| Popularity, Random, CF và SVD | Giữ sáu mô hình đã chọn; thêm PureSVD và so sánh biểu diễn có kiểm soát. Không mặc định bổ sung ALS/BPR. |
| Random search khoảng 20–30 cấu hình | Dùng ngân sách nhỏ đã thống nhất: tối đa 12 cấu hình cho từng CF/MF, bốn số chiều cho PureSVD. Không bắt buộc random search nếu lưới nhỏ đã rõ. |
| M1 sau SVD ổn định | M1 sau khi so sánh toàn bộ mô hình nền; chọn nền bằng validation, không định trước SVD phải tốt nhất. |
| Báo cáo tiến độ với GVHD định kỳ | Chuẩn bị nội dung để người dùng báo cô hằng tuần hoặc hai tuần/lần theo lịch thống nhất. Không tự gửi tin/báo cáo hoặc tạo lịch tự động. |

Hướng dẫn là căn cứ tổ chức công việc, không thay thế kiểm chứng kỹ thuật. Ví dụ: không kết luận mô hình phức tạp bắt buộc phải vượt Popularity; không suy ra ma trận đặc chắc chắn tràn bộ nhớ chỉ từ độ thưa. Dùng sparse cho tương tác và đo tài nguyên khi thực sự triển khai.

## 3. Nguyên tắc làm từng bước

1. Chỉ làm bước đang được người dùng cho phép. Chấp nhận kế hoạch không cho phép chạy nối tiếp các bước.
2. Xong bước phải giải thích và dừng; chỉ chuyển khi người dùng đồng ý.
3. Chạy một cấu hình đầu và tinh chỉnh UserCF, ItemCF, SVD có độ lệch, PureSVD là hai điểm dừng riêng.
4. Trình bày thiết kế M1 và M2 trước khi chạy từng mô-đun; thay đổi tiêu chí phải được nêu trước kết quả.
5. Chạy kiểm tra logic trên ví dụ/tập nhỏ trước, rồi mới chạy phạm vi thực nghiệm của bước đó. Không coi số liệu của tập nhỏ là kết quả toàn bộ benchmark.
6. Mỗi bước phải giải thích đủ đầu vào, đầu ra, lựa chọn, kiểm chứng và giới hạn để người dùng bảo vệ được.

Cuối mỗi bước, chat gồm: việc/tệp đã đổi; kết quả thật hoặc trạng thái chưa có số liệu; bài báo và phần tự thiết kế; ý nghĩa/giới hạn; 2–3 câu hỏi bảo vệ kèm trả lời ngắn; báo cáo có cần cập nhật không. Bước chỉ sửa tài liệu không đòi có số đo thực nghiệm.

## 4. Lộ trình và điều kiện hoàn thành

Bước 0 dọn đợt triển khai vượt phạm vi đã hoàn thành: nền khang-dev tại e80cfbf, lịch sử cũ và lastfm-reproduction được giữ riêng. Không phục hồi kết quả đợt cũ làm kết quả mới.

Trạng thái ngày 26/10: Bước 1–14 đã có bằng chứng; [data card](data-card.md) giữ nguồn và toàn bộ run. Đã tổng hợp tám cấu hình thuộc sáu họ baseline, xác nhận seed và phân tích chi phí/nhóm lịch sử trên cùng catalog 15.398 artist, 1.877 danh sách và cohort 1.865 user/8.142 đích. NDCG@10 mean ± sample std qua seed 42/43/44: PureSVD nhị phân **0.1564272628 ± 0**, SVD **0.0576259192 ± 0.0010411842**, Random **0.0004124977 ± 0.0001408550**. Popularity 0.0623622664 vẫn vượt SVD ở cả ba seed. PureSVD nhị phân là ứng viên nền M1 trong phạm vi cấu hình chưa tuning; chưa khóa nền hoặc chọn seed tốt nhất. Nhóm train <40/=40/>40 có 41/1.822/2 user hợp lệ; không suy rộng nhóm nhỏ/cold-start. Điều kiện baseline/protocol/lịch cho phép đề xuất ALS riêng, chưa triển khai hoặc chốt thay nền. Dừng Bước 14; chưa mở test, tuning, học thẻ/M1/M2.

Sau điểm dừng Bước 14, người dùng cho chạy một cấu hình ALS. Run [implicit_als_k32_c1_r01_validation_20261026](../outputs/runs/implicit_als_k32_c1_r01_validation_20261026/metrics.json) có 32 factors, reg=0.1, a_conf=1, seed 42; tốt nhất vòng 18, dừng vòng 23/patience 5. NDCG@10 **0.1974107044**, cao hơn đối chứng nhị phân **26,1997% tương đối**; Coverage@10 4,9682%, ARP 138,0209 và ILD 0,813204. Fit/monitor tổng 176,550137 giây, OS peak cả tiến trình 178 MiB; 73 tests và kiểm toán độc lập đạt. Chỉ một cấu hình/seed, không thay nền M1 hoặc chạy BPR/SLIM. **Đề xuất điều chỉnh nhỏ:** ưu tiên xác nhận chính cấu hình này ở seed 43/44 trước khi quyết định có cần lưới ALS; chưa thực hiện hai seed đó. Nếu đáp ứng tiêu chí trung bình và ít nhất 2/3 seed đã định trước, tổng hợp lại validation rồi mới duyệt nền/thiết kế M1. Giữ M1/M2, split/metric và mốc demo; không thêm MICE/GNN/planning vì bài mới dùng chúng. Đây là đề xuất sau kết quả, chưa phải quyền chạy tiếp hoặc xác nhận người dùng đã duyệt.

**Điều chỉnh đã được người dùng cho phép và hoàn thành:** chạy đúng hai fit mới seed 43/44, không đổi cấu hình; NDCG@10 lần lượt 0.1974665063 (vòng 32/dừng 37) và 0.1948784471 (vòng 12/dừng 17). [Tổng hợp lại validation](../outputs/runs/validation_summary_als_confirmed_20261026/metrics.json) của 17 run cho ALS mean ± sample std **0.1965852193 ± 0.0014783714**, đối chứng PureSVD nhị phân 0.1564272628 ± 0; tăng 25,6720% tương đối và thắng **3/3 seed**. Đã qua quy tắc giữ, cập nhật **ứng viên nền M1 sang ALS k32/reg0.1/a_conf1, seed 42 tham chiếu**, không chọn seed 43 có điểm cao nhất. Giữ PureSVD/Popularity làm đối chứng và toàn bộ kết quả cũ. Hoãn lưới tuning; chưa mở BPR/SLIM. Bước tiếp theo **Bước 15: trình bày và duyệt thiết kế M1 trước khi triển khai**, giữ C=100/ablation/ngưỡng giảm NDCG tối đa 5% đã định trước; chưa chạy reranker, M2 hoặc test. Các mốc và phạm vi chính giữ nguyên, chưa khóa mô hình cuối.

**Bước 15 đã hoàn thành sau đó theo yêu cầu người dùng:** giải thích thiết kế trước chạy, đóng băng [YAML M1](../configs/models/m1.yaml) và manifest bảo toàn; nạp checkpoint ALS, chỉ học thống kê nhị phân train. Seed 42 chạy đúng 12 tổ hợp, chọn full λ=0.75/β=0.5 rồi giữ nguyên cho 43/44 cùng ba đối chứng ablation. [Run M1](../outputs/runs/m1_als_validation_20261026/metrics.json) có 20 phép đánh giá cấu hình–seed. Mean NDCG@10 0.1880698319 ± 0.0018438691, giảm 4,3317%; ARP giảm 24,7101%, ILD tăng 0.0279024, coverage từ 4,9898% lên 6,5225%. Giảm NDCG từng seed 4,3618%/4,0664%/4,5699%, đều ≤5%. NDCG@5 giảm mean 6,2175%, không suy rộng gate @10 sang mọi K. Có đủ ablation/đường đánh đổi/identity/reload, 83 tests đạt; không fit ALS, đọc test, đổi Word hoặc chuyển M2. Giữ kế hoạch chính và dừng chờ Bước 16.

**Bước 16 đã hoàn thành theo phép người dùng:** [config M2](../configs/models/m2.yaml) và thiết kế được đóng băng trước chạy. Chia 1.501/187/189 user bằng seed 42; chỉ học từ 59.371 tương tác train của 1.501 user, thẻ đúng cặp train. Chín cặp α/ngưỡng, ba đối chứng và N=0/1/3/5 cho 48 phép đánh giá, cohort tinh chỉnh cố định 187/186 user hợp lệ, catalog 13.210. Chọn α=0.75/ngưỡng10 bằng mean NDCG@10 N=1/3/5 **0.0454919147**, Pop **0.0288284384**, nội dung **0.0386541308**, ItemCF hồ sơ **0.0229237450**; N=0 khớp Pop. Audit/list/reload/toy và 91 tests đạt, 887 tệp cũ/11 Word giữ nguyên. [Data card](data-card.md) giữ toàn bộ grid/chi phí/thiếu thành phần/giới hạn. Chưa dùng 189 user để dành, test hoặc triển khai prototype; dừng trước Bước 17.

| Bước | Phạm vi được làm khi đến bước | Điều kiện hoàn thành trước khi dừng |
| --- | --- | --- |
| 1. Kiểm tra nguồn | README, tệp, mã băm, cột, kiểu và quan hệ bảng; chưa làm sạch/EDA/huấn luyện. | Nguồn, phiên bản, giấy phép, tình trạng ngày tải và schema rõ; phân biệt lượt nghe với thời gian gán thẻ. |
| 2. EDA dữ liệu gốc | Thiếu/trùng, count bất hợp lệ, phân bố lịch sử/người nghe/count, độ thưa, mức có thẻ và nối mã. | Bảng/hình từ dữ liệu thật, nhận xét cụ thể, đề xuất quy tắc làm sạch có lý do; chưa áp dụng làm sạch. |
| 3. Làm sạch | Áp dụng từng quy tắc đã giải thích; lưu số lượng trước/sau và lý do loại. | Không mất dòng không giải thích được; giữ nguyên nguồn; chưa chia tập hoặc chạy mô hình. |
| 4. Chia tập | Tạo split cố định theo người dùng, ánh xạ ID ổn định và kiểm tra bảo toàn. | Train/validation/test không giao, đủ tương tác, cùng seed tạo cùng split; gọi đúng là che giấu tương tác ngẫu nhiên. |
| 5. Biểu diễn | Lưu riêng count gốc, log2(1 + count), điểm đại diện 1–5 và nhị phân; ngưỡng chỉ học train. | Giải thích điểm đại diện không phải sao thật; ô chưa quan sát không bị biến thành đánh giá thấp. |
| 6. Bộ đánh giá | Ứng viên, lọc lịch sử, Precision/Recall/NDCG và chỉ số bổ sung; ví dụ nhỏ tính tay. | Công thức đúng; phát hiện trùng/seen/đích rỗng/list thiếu K; chưa chạy so sánh mô hình. |
| 7. Random | Một baseline seed 42 trên validation. | Có mốc ngẫu nhiên thật, cùng danh mục và lọc lịch sử với các mô hình sau. |
| 8. Popularity | Tổng log-count theo V1; xử lý hòa điểm ổn định. | Phân biệt score Popularity với listener count dùng đo mức phổ biến; chưa thay định nghĩa sau khi nhìn test. |
| 9. UserCF | Một cấu hình L = 40, shrinkage = 0; giải thích láng giềng, đóng góp và fallback. | Điểm hữu hạn, ví dụ kiểm tra được, xuất/nạp nhất quán; dừng trước lưới 12 cấu hình. |
| 10. ItemCF | Một cấu hình như UserCF; kiểm tra tương đồng và điểm từ lịch sử. | Hiểu đồng nghe không đồng nghĩa giống âm thanh/thể loại; dừng trước tinh chỉnh. |
| 11. SVD có độ lệch | Một cấu hình 32 nhân tố, learning rate 0,005, regularization 0,02; theo dõi học và xuất/nạp. | Biết target, bias, điều chuẩn và dừng sớm; dừng trước tối đa 12 cấu hình tổng cộng. |
| 12. PureSVD | Chạy 32 chiều trước; sau điểm dừng mới thử tổng cộng {16,32,64,128}. | Phân biệt phép phân rã với MF học bằng SGD và ý nghĩa các ô 0. |
| 13. Kiểm tra biểu diễn | PureSVD: nhị phân, log, điểm 1–5; cùng split, số chiều và seed. | Đo độ nhạy tại cấu hình cố định; không kết luận một biểu diễn luôn tối ưu. |
| 14. Tổng hợp validation | So sáu mô hình, kiểm tra seed, tài nguyên và nhóm lịch sử; xét điều kiện mở rộng trước khi chốt nền M1. | Giải thích lựa chọn cả khi mô hình đơn giản thắng; nếu mở rộng thì tổng hợp lại validation trước Bước 15; chưa xem chỉ số test. |
| 15. M1 | Duyệt thiết kế trước; nền, chỉ đa dạng, chỉ phạt phổ biến, đầy đủ. | Có ablation, đường đánh đổi và kiểm tra khôi phục nền; không chọn tiêu chí sau kết quả. |
| 16. M2 | Duyệt thiết kế trước; Popularity, nội dung thẻ, ItemCF hồ sơ, kết hợp tại N = 0,1,3,5. | Tách người dùng học/tinh chỉnh/kiểm tra; không dùng tương tác/thẻ của người dùng đánh giá để học. |
| 17. Đánh giá cuối | Khóa phương pháp/cấu hình rồi đánh giá test, kiểm định, phân tích lỗi và cập nhật tài liệu làm việc; Word chỉ khi được yêu cầu. | Số liệu truy vết được, trả lời RQ1–RQ4 trong phạm vi dữ liệu; ghi cả giả thuyết không được ủng hộ. |

Các kiểm tra kỹ thuật ở Bước 4–6 được phép kiểm tra cấu trúc/phân tách của test nhưng không dùng kết quả xếp hạng trên test để chọn phương pháp.

### Đối chiếu với E0–E6 trong báo cáo V1

Mã E là nhóm kết quả để viết Chương 4, không phải quyền thực hiện nhiều bước trong một lượt.

| Mã báo cáo | Nội dung | Bước cung cấp bằng chứng |
| --- | --- | --- |
| E0 | Random và Popularity | 7–8; cùng evaluator đã kiểm tra ở Bước 6. |
| E1 | UserCF | 9 và lần tinh chỉnh riêng được phép. |
| E2 | ItemCF | 10 và lần tinh chỉnh riêng được phép. |
| E3 | SVD có độ lệch và PureSVD | 11–13; báo riêng phép kiểm tra biểu diễn. |
| E4 | Nền và các biến thể M1 | 15, sau lựa chọn nền ở Bước 14. |
| E5 | Phân tích nhóm độ dài lịch sử | 14 và 17; ngưỡng nhóm chỉ từ train, báo số user/đích và nhóm trống nếu có. |
| E6 | M2 tại N = 0,1,3,5 | 16 với user chia riêng và protocol đã công bố. |

Chỉ đưa kết quả test cuối vào bản kết luận sau Bước 17. Không điền số kỳ vọng vào bảng E0–E6 trong lúc chuẩn bị tài liệu.

### Quy ước dữ liệu và đánh giá dự kiến

- Loại mã rỗng, count không hữu hạn hoặc không dương; trùng hoàn toàn giữ một. Cùng cặp user–artist có count khác nhau thì dừng xác minh, không tự cộng.
- Giữ mã nghệ sĩ hợp lệ nhưng thiếu tên và dùng tên dự phòng. Thống kê và loại mã không có trong danh mục nguồn khỏi tập chính.
- Tập chính dự kiến giữ user có ít nhất năm nghệ sĩ; xác nhận tính phù hợp sau EDA. Không đặt thêm ngưỡng số người nghe của artist để làm đẹp kết quả.
- Seed 42, thứ tự ID ổn định; mỗi user có n_val = n_test = max(1, floor(0,1 × n)); train nhận phần còn lại. Không gọi đây là leave-one-out hay temporal split.
- Bước 4 đã hiện thực: sắp ID theo giá trị số tăng dần, dùng một random.Random(42) qua các user; lấy validation trước, test tiếp rồi train. Mapping liên tiếp từ 0 chỉ theo train. Holdout ngoài catalog vẫn giữ cặp/count với item_index null; xem thống kê đích/người dùng đủ điều kiện trong data card. configs/base.yaml đã thay chiến lược leave_one_out cũ, chưa nối chuỗi DVC.
- Bốn phân vị 20/40/60/80% trên log-count train, nội suy tuyến tính; điểm = 1 + số ngưỡng mà giá trị lớn hơn nghiêm ngặt. Đây là phép quy đổi của nhóm, không phải tối ưu được Hu et al. chứng minh.
- Bước 5 đã hiện thực: ngưỡng train lần lượt 6.392317422778761, 7.562242424221073, 8.491853096329674, 9.579315937580015; validation/test áp dụng nguyên giá trị. Ba Parquet giữ đủ dòng/chỉ số gốc; bốn CSR train cùng mapping có shape 1.877 × 15.398 và 74.275 ô quan sát mỗi ma trận. transform.json lưu quy tắc/độ chính xác đầy đủ; không biến ô thiếu thành điểm 1 hoặc xóa đích ngoài catalog. Chưa nối chuỗi DVC.
- Catalog chính là artist xuất hiện trong train. Đích đánh giá giao catalog; báo riêng tỷ lệ đích ngoài catalog và user không còn đích hợp lệ.
- Full ranking; validation lọc train, test lọc train + validation. Hồ sơ chấm điểm chỉ dùng train, không tự refit train + validation.
- Chọn bằng NDCG@10 validation; báo Precision/Recall/NDCG tại K = 5,10,20. Precision chia K ngay cả khi trả thiếu.
- Bổ sung Coverage, Gini, ARP, Novelty, ILD và thời gian. ARP dùng listener count train; ILD dùng cùng biểu diễn tương tác nhị phân train cho mọi mô hình.
- RMSE chỉ cho mô hình dự đoán cùng điểm đại diện 1–5; không áp lên Random/PureSVD/reranker như thể cùng thang dự đoán, không dùng chọn mô hình ranking.
- Bước 6 đã kiểm chứng: từ chối trùng/seen/ngoài catalog; danh sách rỗng của user còn đích vẫn nhận 0 trong trung bình ranking. Các chỉ số bổ sung dùng cùng cohort; Coverage/Gini toàn catalog (gồm tần suất 0), ARP/Novelty trung bình các vị trí thực trả, ILD trung bình user có ít nhất hai mục và báo mẫu số. Novelty giữ phân bố `(listeners + 1) / sum_catalog(listeners + 1)` của báo cáo V14. Giá trị không xác định lưu null cùng số lượng liên quan. Hòa điểm theo thứ tự mapping train, không phụ thuộc thứ tự dict đầu vào. CLI hiện chỉ chạy ví dụ tổng hợp; thời gian fit/recommend sẽ đo riêng ở run mô hình.
- Bước 7 đã chạy: Random dùng `random.Random("musicrec-random-v1:42:{user_id}")` xáo trộn catalog theo thứ tự ID số trước lọc lịch sử. Tất cả K dùng prefix cùng thứ tự, score là thứ hạng hoán vị giảm dần; không phải sở thích đã học. Lựa chọn RNG theo user của nhóm giúp không phụ thuộc thứ tự gọi, không đổi seed sau kết quả. CLI chỉ đọc train/validation/mapping, lưu thời gian và snapshot; không dùng `scripts/train.py` cũ. Chưa chạy Bước 8.
- Bước 8 đã chạy: Popularity nhận count gốc, biến đổi từng cặp thành log2(1 + count) rồi cộng trên train bằng tổng ổn định theo thứ tự dòng; hòa điểm theo ID số tăng dần. Fit cố định thứ tự toàn catalog, recommend lọc lịch sử và lấy prefix. Điểm này khác số người nghe dùng ARP/Novelty; không thử thêm biến thể listener count. Model xác định, seed 42 chỉ ghi nhận nguồn split. Hai baseline dùng chung runner I/O/evaluator, không đọc test, không đổi Word. Chưa chạy UserCF.
- Bước 9 đã chạy cấu hình đầu: L=40, shrinkage=0, cosine toàn vector proxy, chỉ giữ tương đồng dương và bỏ chính user. Chọn top-L toàn user rồi giao láng giềng đã nghe từng item; mean chỉ tính quan sát train. Co rút khi dùng là cosine × n_common/(n_common + shrinkage), ít nhất một artist chung; lượt hiện tại shrinkage=0. Không có đóng góp dùng mean user, user mới dùng mean chung, chưa phải M2. Khóa sort neighbor/item làm tròn 12 chữ số rồi theo mapping để loại nhiễu số thực; score gốc không clip. Nạp CSR/model không fit lại, kiểm tra đủ 1.877 user; RMSE proxy chỉ bổ sung. Run chốt có hậu tố checked, run ban đầu có audit không dùng báo cáo. Chưa tuning hoặc chạy ItemCF.

### Ngân sách và mô-đun cải tiến

- Bước 10 đã chạy cấu hình đầu ItemCF: L=40, shrinkage=0, cosine toàn cột proxy train, giữ dương/bỏ self và ít nhất một user chung. Co rút khi dùng là cosine × n_common/(n_common + shrinkage). Chọn top-L toàn catalog theo từng artist đích rồi giao lịch sử user; trung bình điểm quan sát có trọng số, fallback mean user hoặc mean chung cho user mới. Khóa sort 12 chữ số rồi mapping số, score không clip. Tính Gram từng khối 256 artist, chỉ giữ top-L; ma trận trọng số có chiều target × neighbor, không đảo thành mở rộng theo nghệ sĩ nguồn. Dùng cùng evaluator/cohort, RMSE proxy chỉ bổ sung; đã kiểm tra độc lập/nạp lại/chạy lại, chưa tuning.

- UserCF: cosine và dự đoán trừ trung bình theo V1; ItemCF: cosine và trung bình có trọng số. Cùng lưới L ∈ {20,40,80,120}, shrinkage ∈ {0,10,50}, tối thiểu một nghệ sĩ/người nghe chung tương ứng. Công thức co rút, cách lấy láng giềng và fallback phải ghi rõ trước chạy.
- MF có độ lệch: tối đa 12 cấu hình tính cả lần đầu; miền còn lại đối chiếu V1 trước khi chạy. Tối đa 100 epoch, patience 5 theo NDCG@10 validation; lưu checkpoint tốt nhất. Bước 11 đã chạy một cấu hình 32 nhân tố/lr=0.005/reg=0.02/seed=42, float64, bias=0 và factor normal(0,0.1) với PCG64. Mean proxy train cố định; SGD từng cặp quan sát, xáo trộn sau sắp mapping, cập nhật đồng thời hai factor từ trạng thái cũ và L2 theo từng quan sát. Từ epoch 1 đánh giá mỗi epoch; tăng nghiêm ngặt mới cải thiện, hòa giữ epoch sớm nhất. Dừng ở epoch 6 và khôi phục epoch 1; RMSE không chọn epoch, validation không tạo gradient. User mới dùng mean + bias artist, không clip score, khóa sort 12 chữ số; BLAS một luồng. Đã kiểm tra/nạp lại/chạy lại; chưa tuning hoặc kiểm tra thêm seed.
- PureSVD: bốn số chiều tính cả lần đầu. Bước 12 đã chạy 32 chiều trên proxy train/seed 42, không trừ mean/chuẩn hóa/bias; ô thiếu bằng 0 đại số của phép phân rã. Dùng svds/ARPACK lấy singular values lớn nhất, tolerance=1e-10/maxiter=10000/ncv mặc định, vector đầu PCG64 và BLAS một luồng. Score R V32 V32.T, không nhân Sigma lần nữa hoặc fit validation, không RMSE; user mới zero profile với reason riêng. Khóa sort 12 chữ số rồi mapping số; không clip. Bước 13 đã so nhị phân/log/proxy tại đúng cấu hình này, dùng hai config mới và giữ đối chứng proxy nguyên vẹn; nhị phân tốt nhất NDCG@10 trong phép so cố định, chưa chọn biểu diễn/rank cuối. Đã đối chiếu NumPy SVD trên toy và eigh user–user trên dữ liệu thật, nạp lại/chạy lại. Chưa thử 16/64/128 chiều. Mô hình có ngẫu nhiên kiểm tra cấu hình được chọn với seed 42,43,44 ở lần được phép; không chọn seed tốt nhất để báo cáo.
- M1: C = 100; λ ∈ {0,5;0,75;1}, β ∈ {0;0,1;0,25;0,5}. Mức giảm NDCG@10 tương đối tối đa 5% so nền được chốt trước chạy. Trong các cấu hình đầy đủ đạt điều kiện, chọn ARP thấp nhất, rồi ILD cao nhất, rồi NDCG cao nhất. Nếu không cấu hình phù hợp thì báo đúng như vậy. λ = 1, β = 0 phải khôi phục nền.
- Thiết kế M1 đã giải thích/đóng băng trước chạy: `λ*r - (1-λ)*max_cosine - β*p`; r min-max trên pool Top-100 cố định, phẳng → 1; cosine nhị phân train, max trên tập rỗng → 0; p=ln(1+listeners)/ln(1+max_listeners) toàn catalog train. Hòa làm tròn 12 chữ số rồi base rank; score trả về là ALS gốc, không sắp lại M1 theo score. Chọn ở seed 42; cố định full và trọng số ablation ở 43/44, gate 5% từng seed và mean, không retuning. Chỉ ma trận 100×100 theo user, không Gram đặc toàn catalog. Catalog/đích đánh giá giữ nguyên. Bằng chứng công thức, 12 tổ hợp, chi phí và giới hạn tại [data card](data-card.md).
- M2: chín cặp α ∈ {0,25;0,5;0,75}, ngưỡng lịch sử ∈ {3,5,10}; chọn theo trung bình NDCG@10 validation tại N = 1,3,5. N = 0 kiểm tra đường Popularity.
- M2 chia user học/tinh chỉnh/kiểm tra 80/10/10 bằng seed cố định. ItemCF, popularity, từ vựng/IDF và đặc trưng thẻ chỉ học từ tương tác train/thẻ của nhóm học được phép dùng. User đánh giá chỉ cung cấp N tương tác từ lịch sử train; đích validation/test tương ứng. Giữ cùng nhóm có ít nhất năm tương tác hồ sơ cho mọi N và chỉ lọc N nghệ sĩ đã cung cấp. Thiếu thẻ phải có đường xử lý và số lượng trường hợp.
- Thiết kế M2 đã giải thích/đóng băng ở Bước 16: công thức V1 `w*CF+(1-w)*(alpha*content+(1-alpha)*pop)`, w=min(1,N/ngưỡng); thiếu CF đặt w=0 theo artist, thiếu nội dung dùng pop. CF proxy chuẩn hóa (s−1)/4; nội dung cosine; Pop tổng log2(1+count)/max nhóm học. Fit lại quantile và ItemCF từ learning train, không dùng proxy/checkpoint warm-start có query đóng góp. Thẻ normalize casefold/whitespace, TF distinct learner/artist/tag, min df=2, smooth IDF và L2. N=0 khớp thứ tự Pop. User split floor80%/floor10%/còn lại, `random.Random(42)` qua ID số; hồ sơ shuffle theo user/seed và lấy prefix lồng nhau. Chỉ user tinh chỉnh được chấm validation ở Bước 16, không xem kết quả nhóm để dành. Có [đường N](../outputs/runs/m2_cold_user_validation_20261026/m2_history_curve.png) và đủ chín cấu hình; không chọn riêng từng N hoặc thêm grid sau kết quả.
- Ghi rõ M2 khác protocol warm-start chính; không dùng thay đổi protocol để tuyên bố thắng trực tiếp các bảng không tương đương.

### Thực nghiệm bổ sung có giới hạn

Các phần mở rộng đã nằm trong lộ trình là PureSVD, so sánh ba biểu diễn, ablation M1 và đánh giá M2 theo N. Chúng cần minh chứng chứ chưa phải cải tiến đã được xác nhận.

Khảo sát ngày 24/10/2026 chọn **implicit ALS → BPR-MF** làm hai ứng viên ưu tiên, **SLIM** dự phòng. Căn cứ bài báo, mục tiêu học, khác biệt dữ liệu và khả năng hiện thực ở [phần khảo sát mở rộng](TONG_QUAN_TAI_LIEU_THAM_KHAO.md#khao-sat-mo-rong-20261024). Đây là thiết kế của nhóm chưa chạy, không phải cấu hình tối ưu được các bài báo xác nhận trên HetRec của nhóm.

- Chỉ xét nhánh này sau Bước 14 khi cả sáu baseline có validation hợp lệ, evaluator đã kiểm tra và còn đủ thời gian cho M1/M2 cùng đánh giá cuối trước 15/11. Tách lượt chạy đầu, giải thích và tinh chỉnh thành các điểm dừng riêng, chỉ làm bước được người dùng cho phép.
- Đặt nhánh mở rộng giữa Bước 14 và 15, tổng hợp lại validation rồi mới chốt nền M1. Nếu sáu baseline chưa xong ở mốc 08/11 hoặc nhánh phụ đe dọa lịch M1/M2, hoãn phần chưa chạy đến sau demo; không giảm kiểm chứng của các bước chính để lấy chỗ.
- Giữ dữ liệu sạch hiện có, không lọc thêm artist, đổi split/catalog/candidate/evaluator hoặc thu thập dữ liệu ngoài. Validation lọc train; test lọc train + validation; học và hồ sơ chấm điểm vẫn chỉ dùng train. RMSE không dùng chọn ba mô hình này.

Ngân sách đề xuất dưới đây chỉ có hiệu lực khi đến bước thực nghiệm được phép. Các lưới đều tính cả cấu hình đầu; seed 42 dùng chọn cấu hình. Không tăng lưới sau khi thấy kết quả không thắng.

| Ứng viên | Lượt chạy đầu trên validation | Miền tinh chỉnh tối đa |
| --- | --- | --- |
| Implicit ALS | 32 factors, regularization = 0,1, a_conf = 1; p = 1 cho cặp train đã nghe, c = 1 + a_conf × ln(1 + count) cho cặp đó; c = 1, p = 0 cho ô chưa quan sát. | factors ∈ {32,64}, regularization ∈ {0,01;0,1}, a_conf ∈ {1,10}: tối đa 8 cấu hình. Tối đa 50 vòng, đánh giá mỗi vòng, patience 5 theo NDCG@10, lưu checkpoint tốt nhất. |
| BPR-MF | Nhị phân train; 32 factors, learning rate = 0,01, regularization = 0,01, verify_negative_samples = true. | factors ∈ {32,64}, learning rate ∈ {0,01;0,05}, regularization ∈ {0,001;0,01}: tối đa 8 cấu hình. Tối đa 100 epoch, đánh giá mỗi 5 epoch, patience 3 lần đánh giá, lưu checkpoint tốt nhất. |
| SLIM dự phòng | Nhị phân train; ElasticNet alpha = 0,01, l1_ratio = 0,1, positive = true, fit_intercept = false; loại cột đích khỏi đầu vào khi học từng artist, diag(W) = 0. | alpha ∈ {0,001;0,01}, l1_ratio ∈ {0,1;0,5}: tối đa 4 cấu hình. selection = cyclic, tol = 1e-4, max_iter = 1000 cho mỗi hồi quy; lưu cảnh báo hội tụ, không âm thầm tăng ngân sách. |

ALS dùng ln riêng cho confidence, không thay biểu diễn log2 của các baseline. Với implicit.cpu.als dự kiến, truyền confidence đã tính và đặt alpha thư viện = 1 để tránh nhân a_conf hai lần. BPR dự kiến dùng bản CPU của implicit 0.7.3: bỏ qua trọng số count, có item bias, lấy mẫu ứng viên âm từ danh sách item của các tương tác train rồi bỏ qua mẫu là positive train; không gọi đó là lấy mẫu đều trên catalog. Không nhìn validation/test để loại riêng các đích ẩn khỏi bộ lấy mẫu.

Ưu tiên CPU, float32 cho ALS/BPR; đặt num_threads = 1 và giới hạn luồng BLAS để kiểm tra tái lập. SLIM dùng sparse cho X/W, không tạo ma trận item × item đặc. Trước tinh chỉnh, lượt chạy đầu phải đo thời gian fit, đánh giá, suy luận, bộ nhớ đỉnh và kích thước artifact trên máy thực tế. Nếu có lỗi môi trường, hết bộ nhớ, không hội tụ hoặc không còn quỹ thời gian, ghi đúng trạng thái và hoãn; không cắt catalog để làm run vừa máy.

Chỉ mở SLIM sau khi ALS/BPR đã được giải thích và còn thời gian. Trần là 20 cấu hình ở seed 42; xác nhận cấu hình ALS/BPR được chọn với seed 43 và 44 bổ sung tối đa 4 lượt fit. SLIM với selection = cyclic là xác định, không tạo ba seed giả lập. Không phải chạy đủ trần hoặc tự chạy liên tục.

Tiêu chí đề xuất giữ mô hình mới: NDCG@10 validation trung bình qua seed cao hơn baseline mạnh nhất trong sáu mô hình; với ALS/BPR, chênh lệch dương ở ít nhất 2/3 seed tương ứng. Dùng cấu hình seed 42 đã chọn rồi giữ nguyên khi kiểm tra seed 43/44; baseline đối chiếu cũng kiểm tra seed theo quy ước hiện hành. Nếu SLIM đạt điều kiện khảo sát, so điểm xác định của nó với trung bình baseline và nêu rõ cách tổng hợp. Khi bằng điểm giữ baseline hiện có; công bố thêm P/R/NDCG@5,10,20, Coverage, Gini, ARP, Novelty, ILD và chi phí, không chọn seed đẹp nhất hoặc coi kiểm tra validation là xác nhận độc lập.

Nếu ứng viên mới thắng và được chọn làm nền M1, phải chạy M1 cùng ablation trên nền đó; không tự thay ItemCF của M2. Chốt mô hình, cấu hình, quy tắc tổng hợp seed và cặp kiểm định trước Bước 17. Test chỉ xác nhận sau khóa; nếu test không ủng hộ thì báo kết quả đó, không quay lại tuning. Nếu cấu hình đã khóa/test đã mở trước khi xét nhánh này, lưu nó thành nghiên cứu bổ sung, không dùng test đã xem để chọn lại mô hình của đợt cũ.

Khi cần rút gọn báo cáo sau khi có bằng chứng, rút phần diễn giải mô hình ít đóng góp hoặc chuyển chi tiết xuống phụ lục; giữ bảng kết quả đầy đủ và run của mọi mô hình đã chạy. Khảo sát ngày 24/10 chỉ cập nhật tài liệu làm việc; lượt ALS ngày 26/10 đã tạo config/cài extra thư viện và chạy một cấu hình theo phép riêng. Word giữ nguyên, contract fit/predict/recommend và API phục vụ không đổi; chưa có quyền tuning/mở rộng tiếp.

Tạm hoãn đối chứng Popularity theo số người nghe so với tổng log-count đến sau đợt nộp demo. Đây không phải điều kiện để nộp và không dùng ba ngày dự phòng để chạy thêm. Khi đề xuất lại phải nêu giả thuyết, giữ split/candidate cố định, chọn trên validation và dừng trao đổi trước khi chạy. Dữ liệu thứ hai, audio/lyrics, GNN và LLM không thuộc phạm vi mặc định.

## 5. Học và đọc đúng lúc

Trước dữ liệu: phân biệt implicit/explicit, artist/track, sparsity/cold-start/popularity bias; đủ pandas, NumPy, scipy.sparse để hiểu đầu vào. Không đòi học hết framework trước khi thực nghiệm.

Theo thứ tự cô gợi ý, đọc tám tài liệu nền: Resnick 1994 → Sarwar 2001 → Koren/Bell/Volinsky 2009 → Hu/Koren/Volinsky 2008 → Herlocker 2004 → Cremonesi/Koren/Turrin 2010 → Kowald/Schedl/Lex 2020 → Ji et al. 2023. Sau mỗi bài giải thích 3–4 câu: bài toán, dữ liệu, ý chính và quyết định nào của nhóm được hỗ trợ. [Tài liệu ôn tập hiện có](SEMINAR_CHUONG_1_2.md) giúp chuẩn bị; kiểm tra PDF/nguồn gốc trước khi dùng chi tiết hay số liệu từ bản tổng hợp.

| Bước | Căn cứ cần đọc | Phần nhóm tự lựa chọn |
| --- | --- | --- |
| Nguồn/EDA | README HetRec, hướng dẫn GVHD | Quy tắc hợp lệ, cách trình bày phân bố và phạm vi benchmark. |
| Biểu diễn | Hu et al. 2008 | Log2 và điểm phân vị 1–5; không gán công thức riêng cho bài gốc. |
| Split/evaluator | Herlocker et al. 2004; Cremonesi et al. 2010; Ji et al. 2023 | Tỷ lệ split, catalog, masking, K và metric chọn cấu hình. |
| UserCF/ItemCF | Resnick 1994; Herlocker et al. 2002 về lựa chọn neighborhood; Sarwar 2001 | Chuyển thể sang điểm đại diện, lưới nhỏ và fallback. |
| MF/PureSVD | Koren et al. 2009; Cremonesi et al. 2010 | Cấu hình và biểu diễn; không coi kết quả trên dataset khác là kết quả của nhóm. |
| M1 | Carraro & Bridge, arXiv v2 17/06/2024; Ungruh et al., RecSys 2024; [đối chiếu nguồn](TONG_QUAN_TAI_LIEU_THAM_KHAO.md#doi-chieu-m1-20261026) | Greedy reranking/đánh đổi và giới hạn offline; công thức kết hợp, chuẩn hóa, grid và gate là thiết kế nhóm, không tái hiện nguyên bản hoặc dùng ARP chứng minh hài lòng/công bằng. Trích dẫn MMR lịch sử giữ trong tổng quan. |
| M2 | Lin et al., KDD 2024; Zhou/Dai/Joachims, arXiv v1/workshop 2024; [đối chiếu](TONG_QUAN_TAI_LIEU_THAM_KHAO.md#doi-chieu-m2-20261026) | Thẻ chỉ từ dữ liệu học và khảo sát theo số lịch sử; dữ liệu/tác vụ khác nên không sao chép điểm. Công thức V1, ItemCF + TF–IDF + Pop, normalization/min_df/grid/user split là thiết kế nhóm; Burke 2002 giữ vai trò lịch sử. |

Trước chuyển sang mô hình phải tự tính được một ví dụ UserCF/ItemCF, giải thích ô chưa quan sát và vì sao RMSE thấp chưa chắc Top-K tốt. Trước kết luận cuối phải hiểu so sánh theo từng user, bootstrap, Wilcoxon và Holm ở mức đủ diễn giải.

## 6. Lịch mục tiêu từ 19/10 đến cuối tháng 11/2026

Còn sáu tuần và ngày 30/11 để chuẩn bị demo. Lịch dưới đây là mục tiêu làm việc, chưa phải ước lượng đã đo từ thời gian chạy thực tế. Cần trao đổi đều để xử lý từng điểm dừng; chậm bước nào phải nêu ảnh hưởng lịch ngay, không tự chuyển bước hoặc bỏ kiểm chứng để bù tiến độ.

| Thời gian | Công việc mục tiêu theo thứ tự | Đầu ra phải có cuối mốc |
| --- | --- | --- |
| 19–25/10 | Bước 1–6: nguồn → EDA → làm sạch → split → biểu diễn → evaluator; sau đó Random và Popularity ở Bước 7–8. | Nguồn và dữ liệu có trạng thái rõ; evaluator vượt ví dụ tính tay; hai baseline có validation thật. |
| 26/10–01/11 | UserCF rồi ItemCF, mỗi mô hình có cấu hình đầu và điểm dừng riêng trước tinh chỉnh. | E1/E2 chạy đúng cùng protocol, có ví dụ giải thích, fallback và kiểm tra xuất/nạp. |
| 02–08/11 | SVD có độ lệch → PureSVD → kiểm tra biểu diễn → tổng hợp validation, Bước 11–14; xét điều kiện nhánh ALS/BPR-MF/SLIM. | E3, sáu baseline và phân tích E5; nếu mở rộng thì tổng hợp lại trước khi chốt nền M1, chưa xem chỉ số test. |
| 09–15/11 | Duyệt và thực hiện M1, sau đó M2; khóa phương pháp/cấu hình rồi làm Bước 17. | E4/E6, test cuối và phân tích có bằng chứng; chốt mô hình, biến đổi, mapping và fallback cho demo. |
| 16–22/11 | Các bước prototype: artifact → API → UI → kiểm tra offline/API. Mục tiêu tích hợp bản đầu ngày 20/11. | **Chậm nhất 22/11 có demo chạy đủ luồng**, nạp lại được artifact và thử các hồ sơ quy định. |
| 23–27/11 | Sửa lỗi, kiểm tra môi trường sạch, đo thời gian, README chạy lại, nội dung báo cáo cần đồng bộ và luyện demo. | **27/11: bản nội bộ sẵn sàng nộp**, gói chạy, kết quả thật và phương án video dự phòng. |
| 28–30/11 | Dự phòng lỗi cài đặt, đóng gói, yêu cầu định dạng nộp và bàn giao. | Demo được người dùng kiểm tra để tự nộp theo lịch thực tế của cô; không thêm tính năng/thí nghiệm. |

### Các mốc cần bảo vệ

- **25/10:** nếu dữ liệu/evaluator chưa ổn, ưu tiên sửa trước mọi mô hình; không nén bằng cách bỏ kiểm tra rò rỉ hoặc ví dụ tính tay.
- **08/11:** nếu sáu baseline chưa xong, không mở thêm mô hình/dataset. Trình bày phần trễ và đề xuất giảm các lượt tinh chỉnh chưa chạy, sau đó người dùng chốt phạm vi tiếp theo. Các lưới ở mục 4 là ngân sách tối đa; không tăng ngân sách để tìm kết quả thắng.
- **15/11:** chốt phạm vi mô hình cho demo. Nếu M1/M2 chưa được kiểm chứng, báo rõ và đề xuất demo mô hình nền đã kiểm chứng cùng fallback Popularity, đồng thời ghi M1/M2 là chưa hoàn thành. Không tự tuyên bố đã giải quyết cold-start hoặc giảm bias, không âm thầm bỏ các mục tiêu nghiên cứu.
- **16/11:** bắt đầu quỹ thời gian prototype khi đã có mô hình được chọn hợp lệ. Không đợi mô hình phức tạp thắng baseline, cũng không kéo dài tuning sang tuần sửa demo.
- **22/11:** dừng thêm chức năng; 23–27/11 dành cho lỗi, tính đúng và khả năng chạy lại. Không làm giao diện đẹp, Docker, tracking server hoặc dashboard trước khi luồng chính ổn.
- **27/11:** hoàn thành nội bộ, giữ nguyên ba ngày dự phòng. Nếu có lỗi phương pháp hoặc lỗi mô hình làm thay đổi kết quả, phải ghi nhận, sửa và đánh giá lại phần bị ảnh hưởng; không dùng test để chọn lại siêu tham số.

Mọi phương án thu hẹp phạm vi phải giải thích và được người dùng chốt trước triển khai; nếu ảnh hưởng nội dung đã thống nhất với GVHD thì chuẩn bị phần để người dùng trao đổi với cô. Không tự đổi phương pháp chỉ vì đến ngày mốc. Hạn/giờ nộp chính thức cụ thể hơn sẽ thay mốc lập kế hoạch 30/11; không mặc định được phép nộp muộn nếu cô yêu cầu sớm hơn.

### Phối hợp để giữ tiến độ

Phân công tham khảo: Cao Trọng Nguyên phụ trách chính dữ liệu/đánh giá/phân tích; Lê Khắc Gia Khang phụ trách chính mô hình và prototype sau này; cả hai đọc chéo và phải hiểu toàn bộ luồng. Hai người có thể đọc bài, kiểm tra kết quả và chuẩn bị phần giải thích của bước hiện tại song song; không triển khai bước phụ thuộc khi đầu vào chưa được kiểm chứng hoặc chưa được phép.

Mỗi lượt bắt đầu bằng mục tiêu nhỏ, cuối lượt giải thích và dừng. Cuối mỗi mốc tuần đối chiếu đầu ra với bảng trên ngay trong chat; nếu trễ, nêu việc còn thiếu và thời gian dự kiến cần thêm trước khi quyết định phạm vi. Không bắt buộc tạo GitHub Project, nhật ký mới, ADR, DVC remote hoặc MLflow để theo lịch này.

Chương 1–2 tận dụng bản đã có; chỉ ôn đúng phần cần cho bước đang làm. Kết quả mới lưu trong run và tài liệu làm việc. Theo yêu cầu mới nhất ngày 25/10/2026, chỉ cập nhật Word khi người dùng yêu cầu rõ ràng, không tự cập nhật sau từng bước hoặc sau khi chạy hết mô hình. Hạn nộp toàn bộ báo cáo và ngày bảo vệ chưa được xác nhận.

## 7. Lưu bằng chứng và đồng bộ báo cáo

- Mỗi run riêng lưu config, seed, Git SHA kèm tình trạng thay đổi chưa commit nếu có, mã băm dữ liệu/split, ngưỡng biến đổi, dự đoán theo user, metrics và thời gian. Không ghi đè kết quả.
- Đánh giá cuối: trung bình/độ lệch chuẩn qua seed khi phù hợp; bootstrap 95% với 1.000 lần lấy mẫu user. Không coi nhiều seed của cùng user là các user độc lập.
- So sánh cặp định trước: mô hình chọn với Popularity, SVD với PureSVD, M1 với nền, M2 với Popularity tại N = 3; dùng Wilcoxon và Holm trên các user tương ứng, giải thích cả mức chênh lệch thực tế. Trường hợp toàn chênh lệch bằng 0 phải có cách báo cáo phù hợp.
- Nếu giữ ứng viên mở rộng, thêm cặp ứng viên được chọn với baseline mạnh nhất của nhóm sáu mô hình đã xác định bằng validation vào cùng họ kiểm định Holm trước khi mở test. Trung bình theo seed trong từng user trước so sánh; không coi ba seed là ba user độc lập.
- Số liệu seminar hoặc lastfm-reproduction không thay thế kết quả của quy trình đang làm lại.
- Chỉ cập nhật Word khi người dùng yêu cầu rõ ràng; không tự sửa sau từng bước hoặc khi chạy xong các mô hình. Khi được yêu cầu, xuất **bản khóa luận đầy đủ mới**, kế thừa bản mới nhất. Bằng chứng vẫn lưu ngay trong run và tài liệu làm việc hiện có; không tạo báo cáo tiến độ Word/Markdown khác.
- Theo [quy tắc lưu báo cáo](../DEVELOPMENT_RULES.md): giữ nguyên nội dung các bản đã bàn giao; tên tệp dùng `33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_DD-MM-YYYY.docx`, ngày tạo bản thực tế tại Việt Nam, không thêm thứ hoặc Vn vào tên. Không ghi đè; bản mới trùng ngày lưu trong thư mục con Vn theo quy tắc. Kiểm tra toàn bộ trang của bản sửa nội dung trước bàn giao để người dùng tự gửi cô.

## 8. Giai đoạn prototype sau thực nghiệm

Khung prototype mục tiêu là 16–27/11, sau mốc chọn mô hình 15/11. Chỉ thực hiện từng bước khi được phép: chọn artifact → xuất/nạp kiểm tra mapping → API tối thiểu → UI tối thiểu → kiểm tra offline/API nhất quán → đo thời gian → thử môi trường sạch → luyện demo và cập nhật phần Chương 5 đã làm thật.

Demo cần trường hợp user có lịch sử, user chưa có tham số đã học và hồ sơ rỗng; lý do/fallback hiển thị phải đúng cơ chế. Không train trong request. Nếu hiển thị bài hát minh họa, không coi đó là kết quả đánh giá khuyến nghị bài hát.

### Điều kiện bản demo sẵn sàng ngày 27/11

1. Nạp artifact đã chọn từ đĩa, đúng mapping và biến đổi; khởi động lại vẫn cho kết quả nhất quán. Không bắt buộc phục vụ cả sáu mô hình trong giao diện.
2. API/UI chạy đủ luồng chọn user hoặc nhập hồ sơ → chọn K → xem danh sách nghệ sĩ có tên và thông báo cơ chế/fallback trung thực. M1/M2 chỉ đưa vào khi đã kiểm chứng.
3. Không trùng kết quả, không chứa lịch sử được cung cấp, điểm hợp lệ; API nhất quán với suy luận offline cho cùng đầu vào và chế độ.
4. Có kiểm tra user đã biết, hồ sơ ngắn, hồ sơ rỗng và đầu vào lỗi. Popularity ở hồ sơ rỗng được ghi rõ là chưa cá nhân hóa.
5. Có README với lệnh đã kiểm tra, phiên bản thư viện và cách lấy artifact/dữ liệu cần thiết; thử trên môi trường sạch, không phụ thuộc biến còn trong notebook hoặc đường dẫn cá nhân không được giải thích.
6. Có bảng kết quả thực tế cùng model/config/version để giải thích lựa chọn; đo thời gian trên máy demo, không đặt số đáp ứng chưa đo. Báo cáo mới nếu cần phải theo quy tắc không ghi đè.
7. Luyện demo ít nhất ba lần, có một lần người khác xem; chuẩn bị video ngắn và gói chạy dự phòng trước 27/11. Chưa có yêu cầu nộp video chính thức thì coi đây là phương án dự phòng, không tự suy ra định dạng cô yêu cầu.

Trước bảo vệ: đối chiếu RQ1–RQ5 với bằng chứng, xác minh trích dẫn, nêu dữ liệu tĩnh và giới hạn chia ngẫu nhiên, luyện demo ít nhất ba lần và một lần có người khác xem; chuẩn bị phương án dự phòng. Chưa triển khai các việc này trong lượt sửa Markdown.
