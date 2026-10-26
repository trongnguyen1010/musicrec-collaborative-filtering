# Đặc tả định trước cho lượt thực nghiệm bổ sung H1

Ngày hợp nhất: **27/10/2026**. Người hợp nhất: **GPT (Codex)**.

**Trạng thái: GPT và Claude đã thống nhất thiết kế phương pháp H1; debate phương pháp kết thúc. Chưa chạy thực nghiệm H1 trong đợt debate này. Đồng thuận của hai agent không phải là sự phê duyệt chạy thực nghiệm của người dùng.**

## 1. Ghi nhận đồng thuận cuối cùng

Claude đã nhận R3-1, R3-2, R3-4, R3-5, R3-6 và công thức R3-3 trong [Claude vòng 3](PHAN_HOI_CLAUDE_VONG_3_CHOT_DE_XUAT_H1.md). Claude chỉ đề nghị thay lưới β bằng tám mức và thêm quy tắc khi không có β dương khả thi, đồng thời xác nhận đồng ý kết thúc debate nếu GPT nhận hai thay đổi này.

**GPT chấp nhận cả lưới tám mức và quy tắc đó, đúng như mục 3.2–3.3 của Claude.** Lý do: các mức nhỏ thêm vào giúp đối chứng có độ phân giải tốt hơn gần nền, ngân sách được khai báo trước và không cần giả định phỏng đoán về phân phối điểm đã đúng. Nếu đối chứng không có điểm dương khả thi thì không biến việc H1 không bị trội thành bằng chứng ưu thế.

Đây là xác nhận đáp ứng điều kiện kết thúc mà Claude đã nêu, không phải GPT tự viết câu trả lời thay Claude. Không cần vòng debate tiếp theo về các điểm đã nhận.

Các bản làm căn cứ, giữ nguyên để truy vết:

| Tài liệu | Vai trò |
| --- | --- |
| [Khảo sát gốc](KHAO_SAT_HUONG_MOI_2021_2025.md) | Điểm xuất phát H1–H4; không dùng các phát biểu cũ đã được sửa làm thiết kế cuối. |
| [GPT vòng 2](PHAN_HOI_GPT_VONG_2_VE_KHAO_SAT_HUONG_MOI.md) | Phân biệt mục tiêu, phép toán, các mức bằng chứng. |
| [GPT vòng 3](PHAN_HOI_GPT_VONG_3_CHOT_DE_XUAT_H1.md) | R3-1–R3-6; nền tảng của đặc tả hợp nhất. SHA-256 `0b9d24a7a063844eddd316d3e01f0fc2be644ddb40410cc0b4c864dce2712e01`. |
| [Claude vòng 3](PHAN_HOI_CLAUDE_VONG_3_CHOT_DE_XUAT_H1.md) | Chấp nhận và hai sửa đổi cuối R3-3. SHA-256 `ee699a4a1fe58e9c7a3e9efb7d36c2533569c8f3097322a7f1779cce88ac98cf`. |

Nếu một điểm trong các vòng cũ khác file này, dùng **R3 của GPT cộng hai sửa đổi R3-3 của Claude đã được GPT nhận ở trên**. Không dùng bảng đề xuất chưa được nhận ở Claude vòng 2 để ghi đè đồng thuận cuối.

## 2. Câu hỏi, phạm vi và nền cố định

**Câu hỏi:** hậu xử lý thành phần phổ chính của ma trận điểm ALS, với mức sửa chung hoặc theo user, có tăng tỷ lệ vị trí gợi ý cho nghệ sĩ ngoài head trong khi NDCG@10 không giảm quá 5% tương đối so với chính nền ALS không? Trong ngân sách công bố, nó tạo được vùng đánh đổi nào so với phạt popularity trực tiếp?

- Item là **nghệ sĩ**, dữ liệu HetRec Last.fm hiện tại. Giữ split, catalog, evaluator, masking và cohort của giao thức warm-start; không chuyển sang tương tác gán thẻ hoặc sampled negatives.
- Nền H1 là **ALS của lượt Chương 4 chính thức đã khóa**: 32 factors, regularization=0,1, confidence=1+ln(1+count), seed 42/43/44. Nạp lại từng checkpoint, không chọn epoch mới và không refit để làm H1.
- PureSVD chỉ là kiểm cơ chế phụ, không được chọn làm nền thay thế sau khi xem kết quả. EASE là baseline riêng; dù EASE thắng, không chuyển H1 sang EASE trong lượt này.
- Các mốc nền có thể đối chiếu ở [config ALS](../../../configs/models/implicit_als.yaml) và [lock Chương 4](../../results/chinh_thuc_cloud_20261026/test/lock.json). Đường dẫn máy khác được ánh xạ sang bản artifact tương ứng bằng hash; không mặc định cùng tham số là cùng checkpoint.
- Tuning chỉ dùng validation seed 42. Các cấu hình đã chọn giữ nguyên cho 43/44; kết quả xác nhận không được dùng để đổi loại hay hệ số. Không dùng test cũ để chọn lại cấu hình của đợt chính thức.

Tài liệu này là thiết kế cho **một lượt bổ sung sau khi đã xem test**, không phải đăng ký trước lần xem test đầu tiên. NDCG và cơ hội xuất hiện offline không chứng minh sở thích thật, mức tiêu thụ, công bằng hay thu nhập nghệ sĩ.

## 3. Train-only context, nhóm ngoài head và metric

Gọi I là catalog train, n_i là số user train phân biệt nghe artist i và M=Σ_i n_i là số cặp tương tác train, không phải tổng play count.

1. Sắp artist theo n_i giảm dần. Head H là prefix ngắn nhất có tổng n_i≥0,2M, mở rộng để mọi artist hòa n_i tại điểm cắt đều thuộc H.
2. Ngoài head T=I\H. T gộp cả mid và tail, không gọi là nhóm tail hẹp của bài UMAP 2021. Lưu H/T và hash; mọi model/seed dùng cùng chúng.
3. Metric chính bổ sung tên **Non-head exposure@10**: e_u=|R_u[:10]∩T|/10, trung bình theo user trên đúng cohort đủ đích trong catalog của NDCG. Nếu danh sách thiếu thì mẫu số vẫn là 10, không xóa user để cải thiện chỉ số.
4. Báo số artist, tỷ trọng cặp tương tác và ngưỡng listener của H/T. Head có thể vượt 20% do hòa. Nếu T rỗng, giả thuyết exposure không áp dụng; không đổi ngưỡng để cứu thực nghiệm.

Các thống kê popularity, nhóm và context chỉ học từ train. Validation che train; test che train+validation nhưng không thêm validation vào các thống kê học. Báo riêng user/đích ngoài catalog theo evaluator hiện có ở [evaluation.yaml](../../../configs/evaluation.yaml).

## 4. Can thiệp phổ và gate

Với nhân tố user P, item Q, S=PQ^T là ma trận điểm **chưa che lịch sử**. Dùng QR mỏng của hai nhân tố rồi SVD ma trận nhỏ để lấy singular triplet chính (σ₁,l₁,r₁); không giả định SVD(Q) đủ đúng ở checkpoint early stopping.

Điểm H1: **s'_ui=s_ui−γ_uσ₁l₁(u)r₁(i)**. Sau sửa điểm mới áp mask và ranking theo quy ước mapping số/làm tròn 12 chữ số. Khi γ₀=0 trả đúng ranking nền để kiểm identity.

Hai loại:

- **γ chung:** γ_u=γ₀ cho mọi user.
- **γ theo sai lệch:** p(i)=ln(1+n_i)/ln(1+max n_i); h_u là trung bình đều p(i) trên train history. g_u là trung bình p(i) trên Top-10 của nền sau khi che train. d_u=max(0,g_u−h_u), d_ref là quantile 90 nội suy tuyến tính trên các d_u>0. γ_u=γ₀·min(1,d_u/d_ref). Nếu không có d_u dương thì đặt toàn bộ γ_u=0 và báo rõ.

Gate tính một lần cho mỗi checkpoint seed, rồi đóng băng cho validation/test; test thêm mask validation nhưng không fit lại gate. Không dùng nhãn giữ lại để tối ưu γ riêng từng user. Việc backbone đã chọn epoch bằng validation vẫn phải được ghi trong provenance.

Lưới **γ₀={0;0,1;0,25;0,5;0,75;1}**, tổng 11 cấu hình khác nhau do hai nhãn 0 trùng nền. Kiểm toán năng lượng, khoảng cách phổ, cân bằng ALS và tương quan với listeners chỉ để mô tả, không có cổng ngưỡng tùy ý 0,5/1,05. Phổ gần trùng cần báo tính không duy nhất/độ nhạy; không tự chuyển sang loại nhiều thành phần để cứu kết quả.

## 5. Đối chứng phạt trực tiếp — lưới cuối cùng

Với mỗi user và checkpoint, min–max score ALS trên toàn catalog chưa nghe trong train. Nếu khoảng biến thiên bằng 0 dùng vector toàn 1. Lưu min/max, không fit lại theo validation/test.

**s_direct(u,i)=s_norm(u,i)−βp(i)**, với lưới cuối cùng:

**β={0;0,01;0,025;0,05;0,1;0,25;0,5;1}.**

β=0 trả đúng ranking nền. β>0 sort score sửa làm tròn 12 chữ số rồi mapping số; mask giống H1. Không thêm gate vào đối chứng. β của mô hình này không cùng thang với β của M1, vì M1 min–max trong Top-100; không so trực tiếp các giá trị hệ số đó.

Ngân sách vòng 1 trên ALS seed 42: **11 cấu hình phổ+8 cấu hình phạt trực tiếp−1 nền trùng=18 danh sách cấu hình khác nhau**. Phần tăng độ phân giải dành cho đối chứng được khai báo trước; không chỉnh lưới bên nào sau khi xem kết quả. Chi phí inference/metric/hash/kiểm toán vẫn được đo dù không fit lại ALS.

## 6. Cổng phát triển và quy tắc khóa trên validation

Gọi N(c) là NDCG@10, E(c) là Non-head exposure@10, b là ALS và ε=10^−12 chỉ là dung sai số học. Cổng dùng point estimate validation seed 42, không phải mức bảo đảm thống kê sau lựa chọn.

1. Xét cấu hình phổ γ₀>0 có N(c)≥0,95N(b) và E(c)>E(b)+ε. Không có thì dừng nhánh phổ, lưu mọi kết quả.
2. Tập điểm đối chứng gồm nền và mọi β dương trong lưới có N≥0,95N(b). q trội c nếu N(q)≥N(c)−ε, E(q)≥E(c)−ε và ít nhất một chiều tốt hơn quá ε.
3. Nếu có β dương khả thi và mọi cấu hình phổ đều bị trội, không tiến vòng đối chứng nâng cao. Chỉ kết luận chưa thấy giá trị thêm trong ngân sách này.
4. **Trường hợp cuối được Claude bổ sung và GPT nhận:** nếu không có β>0 nào đạt biên NDCG, ghi “đối chứng phạt trực tiếp không có điểm khả thi trong lưới đã khóa”. H1 vẫn được chọn/khóa và đi tiếp nếu đạt bước 1; việc không bị trội không được viết thành bằng chứng H1 tốt hơn đối chứng phạt trực tiếp. Mọi kết luận so sánh phải nêu giới hạn này. Không mở rộng lưới sau kết quả.
5. Trong cấu hình phổ còn được xét, khóa tối đa một ứng viên mỗi loại theo E lớn nhất → N lớn nhất → γ₀ nhỏ nhất. Nếu cần duy nhất một H1 đại diện, dùng cùng thứ tự, hòa hoàn toàn ưu tiên γ chung. Loại không có ứng viên được ghi không vượt cổng, không thay bằng ứng viên sau test.
6. Khóa một đối chứng phạt trực tiếp theo cùng biên accuracy rồi E lớn nhất → N lớn nhất → β nhỏ nhất; nếu không có β dương làm E tăng thì giữ nền β=0 và báo đúng tình trạng.
7. Chạy nguyên cấu hình trên seed 43/44; gate/context của từng seed tính bằng cùng công thức. Không chọn lại hệ số/loại từ kết quả xác nhận. Không đạt điều kiện xác nhận thì báo chưa xác nhận, không thay bằng cấu hình dự phòng thuận lợi hơn.

Vẽ mọi điểm/scatter/Pareto để thấy đánh đổi. Đường nối chỉ minh họa; không dùng nội suy tuyến tính, ưu thế mọi mức NDCG hay diện tích dưới đường làm cổng. Không quét lại lưới trên test.

## 7. Kiểm định và diễn giải kết quả đã khóa

Hai điều kiện cho phương pháp j so nền ALS:

- z_N,u=a_j,u−0,95b_u, với a/b là NDCG@10 mới/nền; cần mean(z_N)>0.
- z_E,u=e_j,u−e_b,u; cần mean(z_E)>0.

Trung bình a/b/e qua seed 42/43/44 **trong từng user trước**, rồi bootstrap user; báo thêm từng seed. Không dùng user×seed như các quan sát độc lập.

Thủ tục đã thống nhất: bootstrap cặp B=10.000, seed 42, dùng cùng chỉ số user resample cho mọi phương pháp và hai contrast. CI hiệu ứng lấy từ z chưa center, quantile nội suy tuyến tính. Với một contrast z, center z⁰=z−mean(z), p một phía=(1+số mean(z⁰*)≥mean(z))/(B+1); mọi z=0 thì p=1. Đây là thủ tục bootstrap **xấp xỉ**, cần kiểm ví dụ/trường hợp biên trước triển khai. Dữ liệu không hữu hạn/cohort rỗng làm phép đánh giá không hợp lệ; không tự xóa user để làm p thuận lợi.

Giả thuyết không kết hợp của j là mean(z_N)≤0 **hoặc** mean(z_E)≤0. Dùng p_joint,j=max(p_N,p_E). Tuyên bố thành công chỉ khi hai điều kiện cùng đạt; không thêm hiệu chỉnh giữa hai thành phần của cùng tuyên bố intersection–union.

Họ ban đầu gồm γ chung, γ_u và phạt trực tiếp, dùng Holm trên các p_joint. Họ không tìm được cấu hình khả thi được ghi không đạt, tương đương p_joint=1. Khi công bố nhiều phương pháp, cận CI 95% danh nghĩa riêng không thay được quyết định có hiệu chỉnh. Các so sánh vòng 2 muốn có tuyên bố suy luận riêng phải được liệt kê và xác định họ trước lần chấm đó; không thêm cặp sau khi xem p-value.

Không giả định p_E sẽ nhỏ hoặc p_joint chắc chắn do accuracy quyết định; đó chỉ là dự đoán của Claude, chưa phải dữ kiện. Dù dự đoán xảy ra, vẫn áp dụng đúng hai điều kiện đã khóa. CI rộng/không đạt không được diễn giải thành tương đương hoặc không có đánh đổi.

Các kiểm định trên validation sau tuning là bằng chứng phát triển. Các kiểm định trên test dùng lại không khôi phục tính độc lập của giả thuyết mới. Biên 5% kế thừa lựa chọn nhóm cho M1, không phải ngưỡng thiệt hại đã được xác thực bằng user study.

## 8. Các chỉ số phụ và giới hạn phía user/nghệ sĩ

- Giữ Precision/Recall/NDCG@5/10/20, coverage, ARP, Gini, novelty, ILD theo evaluator hiện tại để đối chiếu. Không dùng metric phụ để chọn lại khi metric chính không thuận lợi.
- A_history đo chênh popularity trung bình giữa danh sách và lịch sử train; A_target so với đích giữ lại trong catalog. Hai đại lượng khác nhau; A_target cũng dùng nhãn giữ lại. Báo cùng cohort với NDCG và số đích/user, không gán popularity=0 cho item ngoài catalog để đưa vào trung bình.
- Báo kích thước/cohort của phân tích mainstream; định nghĩa và quy tắc hòa cần có trong cấu hình trước khi chạy phân tích nhóm. Chưa có ngưỡng mainstream số cụ thể được hai bên chốt; mục này không phải quyền tự lựa theo test.
- Coverage là hợp item trên toàn cohort, không phải trung bình coverage riêng từng user. Nếu có bootstrap coverage, phải recompute hợp trên cùng resample cặp và báo giới hạn của thống kê này; không dùng nó thay metric cộng theo user trong kiểm định chính.
- Gate một chiều không bảo đảm alignment cải thiện hay toàn bộ sở thích user được bảo vệ; NDCG là ràng buộc accuracy tổng theo thiết kế. Không tuyên bố artist thực sự được nghe hoặc hưởng lợi kinh tế chỉ từ exposure offline.

## 9. Vòng đối chứng nâng cao và nhánh độc lập

Chỉ đề xuất vòng 2 sau khi H1 đi tiếp theo cổng; không mặc định được chạy trong lượt bàn giao đặc tả này.

| Thành phần | Phạm vi đã thống nhất |
| --- | --- |
| M1 trên cùng nền | ALS, C=100; λ={0,5;0,75;1}, β={0;0,1;0,25;0,5}, 12 cặp; giữ quy tắc lựa chọn M1 đã có. Tham khảo [m1.yaml](../../../configs/models/m1.yaml), không dùng nền PureSVD của M1 chính thức thay vào đây. |
| H1-top100 | Cùng H1 đã khóa; gate/điểm sửa cố định; Top-100 nền lấy một lần; không tune lại. |
| PPD-MF | Thích nghi theo phương pháp gốc, bỏ propagation, dùng cùng ALS; β={0;0,1;0,2;0,3}×φ={0;0,25;0,5;0,75;1}, 20 tổ hợp, ε phương pháp=10^−8. Công khai ngân sách lệch, không gọi là tái lập đầy đủ trước khi kiểm. |
| EASE | Baseline riêng, không thay nền H1; năm λ dương nhưng giá trị cụ thể chưa chốt. Chỉ chạy khi phụ lục cấu hình riêng hoàn chỉnh và được người dùng cho phép. |
| H3 | Protocol xã hội riêng; không nằm trong lượt H1. Không dùng checkpoint ALS đã học toàn bộ 1.877 user làm nền M2 học từ 1.501 learning users. |

**Lưu ý provenance khi triển khai M1:** `m1.yaml` hiện trỏ các run ALS/representations cũ trong `outputs/runs/`. Tái dùng công thức/lưới/quy tắc của file đó, nhưng bản cấu hình cho đối chứng H1 phải trỏ đúng checkpoint ALS Chương 4 chính thức và cùng representations đã khóa bằng hash. Không dùng nguyên đường dẫn cũ để trộn hai đợt. Đây là kiểm tra ánh xạ artifact, không phải lựa chọn mô hình mới.

PPD cần phụ lục ghi normalization, chọn nhúng, min–max phẳng và projection norm gần 0, sau khi đọc mục 4.1–4.2, Algorithm 1/B.2 và kiểm code gốc. EASE cần phụ lục λ cụ thể, cách giải hệ, kiểm numerical stability, mapping và save/load. Phụ lục triển khai chưa hoàn chỉnh không đồng nghĩa còn bất đồng phương pháp H1, cũng không cho phép lấp chỗ trống theo kết quả test.

Nếu không làm PPD thì chỉ kết luận trong tập đối chứng đã chạy, ghi chưa so họ phép chiếu node; không trì hoãn việc báo kết quả vòng 1. Không dự đoán thời gian/RAM thấp chỉ vì phương pháp là hậu xử lý.

## 10. Kiểm tra, khóa artifact và điểm dừng trước thực nghiệm

Trước khi có triển khai được phép, cần kiểm các phần sau mà không thay giao thức đã thống nhất:

1. Xác định đúng checkpoint từng seed, mappings, split/transform và SHA-256; kiểm input không ghi đè nguồn hay run cũ. Đường dẫn khác máy phải giải quyết bằng provenance.
2. QR/SVD đối chiếu SVD đặc trên toy; kiểm đổi cơ sở nhân tố khi hướng chính phân biệt, γ=0/β=0 identity, masking/tie-break và save/load. Khi singular values trùng/gần trùng phải kiểm tính không duy nhất/độ nhạy thay vì hứa một hướng duy nhất luôn invariant.
3. Kiểm group/tie boundary, T rỗng, d_ref không tồn tại, min–max phẳng, danh sách ngắn và các trường hợp cổng có/không có β khả thi.
4. Kiểm công thức metric và bootstrap/contrast/Holm bằng ví dụ độc lập và trường hợp biên; không viết test chỉ lặp lại production code.
5. Lưu toàn bộ cấu hình/điểm validation, kể cả ngoài biên và bị trội; khóa cấu hình trước xác nhận/test. Kiểm provenance của backbone đã dùng validation để chọn epoch.
6. Đo runtime/RAM/model size khi thực sự chạy; không benchmark hai tiến trình tranh tài nguyên rồi so như cùng điều kiện. Không phát sinh model fit mới chỉ để kiểm tài liệu.

Chỉ thay đổi Markdown trong lượt hợp nhất này. Không thêm module/config chạy, không fit, không đọc dataset test, không sửa Word và không commit.

## 11. Nhãn bằng chứng và kết thúc debate

Nhãn đã được hai bên nhận:

> Đánh giá bổ sung cho mục tiêu giảm thiên lệch đã có trước; phương pháp, tiêu chí và cấu hình cụ thể được thiết kế sau khi kết quả test đợt đầu đã được xem. Việc chọn bổ sung dùng validation và khóa trước lần chấm mới. Kết quả trên test dùng lại không được coi là xác nhận hoàn toàn độc lập cho giả thuyết mới.

Có thể ghi thêm dữ kiện thứ hạng NDCG validation/test gần giống nhau, trừ M1/PureSVD đổi chỗ, dựa trên [kết quả đã công bố](../../results/chuong_4_test.md); không dùng dữ kiện này để khẳng định mức ảnh hưởng của lần xem test là nhỏ.

**Debate phương pháp H1 kết thúc ở đây:** Claude đã nhận năm điểm và đưa phương án cố định cho điểm cuối; GPT đã nhận phương án đó tại mục 1. Các thiếu sót còn lại là công việc chuẩn bị triển khai/phụ lục, không phải lý do tự mở rộng debate hay thực nghiệm. Người dùng quyết định có làm, làm bước nào và thứ tự so với prototype.
