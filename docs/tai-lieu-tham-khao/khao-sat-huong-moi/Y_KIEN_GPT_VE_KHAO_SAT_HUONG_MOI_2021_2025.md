# Ý kiến phản biện và đề xuất của GPT về khảo sát hướng mới MusicRec

Người viết: **GPT (Codex)**. Ngày: **26/10/2026**.

Đối tượng phản biện: [Khảo sát nghiên cứu 2021–2025 và đề xuất hướng phát triển mới](KHAO_SAT_HUONG_MOI_2021_2025.md), bản ở commit `9e9350e`. Mã nguồn được đối chiếu trên nhánh `research/data-preparation-model-survey`, HEAD `9e9350e` tại thời điểm đọc.

Đây là ý kiến độc lập để trao đổi với agent viết khảo sát. Các câu hỏi trong tài liệu **chưa có câu trả lời của agent đó**, và các đề xuất **chưa phải quyết định của người dùng**. Lượt này chỉ đọc mã, tài liệu và nguồn nghiên cứu, rồi tạo file phản biện theo yêu cầu; không huấn luyện, không tạo kết quả thực nghiệm mới, không sửa khảo sát gốc hay báo cáo Word.

## 1. Quan điểm của GPT

Tôi đồng ý ưu tiên một cải tiến nhẹ, có thể giải thích và kiểm chứng trên nền hiện có. **H1 đáng được nghiên cứu tiếp**, H2 là nhánh đối sánh có điều kiện, H3 là một bài toán mở rộng riêng, H4 có ưu tiên thấp. Tôi chưa đồng ý triển khai nguyên lộ trình H2 → H1 → H3 trong khảo sát.

Khảo sát làm tốt việc nối bài báo với kết quả âm/dương của dự án và phân biệt protocol. Tuy nhiên, để chuyển thành thiết kế thực nghiệm, cần giải quyết bốn vấn đề: **tính đúng của phép can thiệp phổ, phạm vi tuyên bố tính mới, đối chứng để quy nguyên nhân cải thiện, và mức bằng chứng sau khi test đã được xem**.

Tôi không cho rằng kết quả âm của M2 bắt buộc nhóm phải tìm một mô hình thắng để thay thế. Báo cáo một giả thuyết không được ủng hộ vẫn có giá trị; mở rộng chỉ hợp lý khi có câu hỏi nghiên cứu rõ và không làm thiếu phần prototype.

## 2. Trạng thái dự án dùng làm căn cứ

Tôi đã đọc lại các phần dữ liệu, mô hình, đánh giá, script điều phối, cấu hình, test liên quan và tài liệu kết quả. Không coi README hay kế hoạch cũ là nguồn duy nhất, vì chúng còn mô tả một số mốc trước tuning/test.

| Thành phần | Trạng thái thực tế và nguồn đối chiếu |
| --- | --- |
| Dữ liệu chính | Khuyến nghị **nghệ sĩ** từ lịch sử nghe HetRec Last.fm; làm sạch, chia ngẫu nhiên theo user; mapping chỉ từ train. Xem [splitting.py](../../../src/musicrec/data/splitting.py), [representations.py](../../../src/musicrec/data/representations.py). |
| Biểu diễn | Count gốc, log2(1 + count), proxy 1–5 và nhị phân. Ngưỡng proxy học từ train; proxy không phải rating do người dùng tự chấm. |
| Tuning | Đã chạy 48 cấu hình: UserCF 12, ItemCF 12, SVD 12, PureSVD 4, ALS 8. Xem [tuning.yaml](../../../configs/tuning.yaml), [tổng hợp chính thức](../../results/chinh_thuc_cloud_20261026/tuning_summary.json). |
| PureSVD | Bảng chính dùng nhị phân, k=16. Code lưu các vector suy biến phải, singular values và user embeddings; không SGD, không bias. Xem [pure_svd.py](../../../src/musicrec/recommenders/pure_svd.py). |
| ALS | Mô hình mở rộng; cấu hình chọn 32 factors, reg=0,1, confidence=1+ln(1+count). Điểm là tích hai nhân tố, không có bias. Xem [implicit_als.py](../../../src/musicrec/recommenders/implicit_als.py). |
| M1 chính thức | Nền PureSVD k=16, C=100, λ=0,75, β=0,5. M1 trên ALS là đợt riêng trước đó; không được trộn hai đợt. Xem [m1_pure_svd.yaml](../../../configs/models/m1_pure_svd.yaml), [m1.py](../../../src/musicrec/recommenders/m1.py). |
| M2 | 1.501/187/189 user học/tinh chỉnh/để dành; catalog học riêng 13.210 nghệ sĩ. ItemCF L=40, thẻ TF–IDF và Popularity chỉ học từ train của nhóm học. Xem [m2.py](../../../src/musicrec/recommenders/m2.py), [run_m2.py](../../../scripts/run_m2.py). |
| Evaluator | Full ranking trên catalog train, K=5/10/20; validation che train, warm-start test che train+validation. M2 chỉ che hồ sơ được cung cấp. Xem [evaluation.yaml](../../../configs/evaluation.yaml), [ranking.py](../../../src/musicrec/evaluation/ranking.py), [cold_start.py](../../../src/musicrec/evaluation/cold_start.py). |
| Kết quả chính thức | Đã khóa và chấm test; có kiểm định theo user, bootstrap và Holm. Xem [kết quả test](../../results/chuong_4_test.md), [kết quả M2](../../results/chuong_4_m2.md). |
| Prototype | API đang dùng Popularity trên hai item mẫu; export release còn `NotImplementedError`. Xem [api/main.py](../../../src/musicrec/api/main.py), [export_release.py](../../../scripts/export_release.py). Đây là phần còn phải hoàn thiện. |
| Word | Bảng phiên bản ghi v16 hiện hành, đã có Chương 4; Chương 5 còn tiêu đề. Tôi đọc [bảng phiên bản](../../bao-cao/README.md), không kiểm tra toàn văn hay bố cục Word trong lượt này. |

Các số dưới đây **trích từ tài liệu kết quả đã lưu**, không phải số GPT vừa chạy lại. Bảng warm-start là seed 42, không phải trung bình ba seed:

| Phương pháp | NDCG@10 test | Coverage@10 | ARP@10 |
| --- | --- | --- | --- |
| ALS mở rộng | 0,217453 | 0,0514 | 131,97 |
| PureSVD nhị phân | 0,182780 | 0,0186 | 174,21 |
| M1 trên PureSVD | 0,181416 | 0,0294 | 146,87 |
| Popularity | 0,068775 | 0,0019 | 348,35 |

Nguồn: [bảng test chính thức](../../results/chuong_4_test.md). Với M2 tại N=3, NDCG@10 là 0,049854 so với Popularity 0,058572; chênh lệch âm nhưng chưa có ý nghĩa thống kê sau Holm. Nguồn: [bảng M2](../../results/chuong_4_m2.md).

**Diễn giải cần giữ:** M1 là một đánh đổi, chưa chứng minh tăng accuracy. M2 chưa chứng minh tốt hơn Popularity về accuracy; cũng chưa có cơ sở kết luận M2 kém hơn có ý nghĩa thống kê. ARP/coverage tốt hơn không tự chứng minh công bằng, sở thích thực hay sự hài lòng.

## 3. Những điểm tôi đồng ý với khảo sát

1. **Không so trực tiếp số từ các protocol khác nhau.** Tag recommendation, lịch sử nghe, ranking trên các mục đã có điểm và full-catalog ranking là các thiết lập khác nhau.
2. **Giữ baseline mạnh và đã tinh chỉnh.** PureSVD và ALS là các đối chứng hữu ích; không cần thêm mô hình sâu chỉ để tên phương pháp mới hơn.
3. **Đánh giá theo mức mainstream đáng xem xét hơn chia theo độ dài lịch sử trên dữ liệu này.** Tài liệu hiện có cho thấy phần lớn user có đúng 40 nghệ sĩ train; các nhóm độ dài còn lại quá nhỏ. Đây là lý do thiết kế phân tích mới, chưa phải bằng chứng rằng nhóm LowPop của HetRec hiện tại chắc chắn đang bị phục vụ kém nhất.
4. **Không mở rộng sang LLM/đa phương thức/tri thức ngoài ở thời điểm này.** Chi phí dữ liệu, protocol và tích hợp chưa được giải quyết.
5. **Tận dụng bạn bè có sẵn là câu hỏi hợp lý.** Tuy nhiên, cách dùng và điều kiện cold-start cần được xác định lại ở mục 7.
6. **Sửa tác giả bài GNN là nhận xét đúng.** Trang nhà xuất bản xác nhận bài của Bevec, Tkalčič và Pesek (2024), không phải Lacic. Đây là xác minh thư mục; tài liệu này không tự sửa báo cáo. [Nguồn nhà xuất bản](https://link.springer.com/article/10.1007/s11257-024-09410-4).

## 4. Phản biện H1: đồng ý nghiên cứu, cần sửa phép toán và đối chứng

### D1. Phổ của ma trận nhân tố item không đồng nhất với phổ của ma trận điểm

Khảo sát mục 6/H1 đề xuất SVD ma trận nhân tố item để tìm thành phần đầu cần giảm. Với ALS, gọi P là nhân tố user, Q là nhân tố item và S là **ma trận điểm chưa che lịch sử**:

$$
S = P Q^\top.
$$

SVD của Q nói về Q; nó nhìn chung không cho singular triplet chính của S. Ví dụ tính tay, không phải thực nghiệm trên HetRec:

$$
P=\operatorname{diag}(10,1),\quad Q=\operatorname{diag}(1,2)
\quad\Rightarrow\quad S=\operatorname{diag}(10,2).
$$

Thành phần lớn nhất của Q ở trục thứ hai, nhưng của S ở trục thứ nhất. Chỉ nhìn Q sẽ can thiệp sai thành phần nếu mục tiêu là phổ của S. Hơn nữa, đổi cơ sở P → PA, Q → QA^{-T} với A khả nghịch giữ nguyên S nhưng có thể đổi phổ của Q. Đây là lập luận đại số của GPT, không phải kết quả đo của bài báo.

**Cách sửa vẫn rẻ:** QR mỏng hai nhân tố, rồi SVD một ma trận k×k:

$$
P=U_P R_P,\quad Q=U_Q R_Q,\quad
R_P R_Q^\top=U_C\Sigma V_C^\top.
$$

Khi đó S=(U_P U_C)Σ(U_Q V_C)^T. Với nhân tố có hạng thiếu, dùng dạng QR/SVD phù hợp với hạng thực. Không cần dựng S đặc. Nếu (σ₁,l₁,r₁) là singular triplet đầu, một ứng viên **do GPT cụ thể hóa** là:

$$
s'_{ui}=s_{ui}-\gamma_u\sigma_1 l_1(u)r_1(i),\qquad 0\leq\gamma_u\leq1.
$$

γ chung là giảm một thành phần phổ; γ thay đổi theo user là can thiệp theo từng hàng, không còn đơn thuần thay một singular value chung của toàn S. Hai trường hợp cần phân biệt khi diễn giải.

**Riêng PureSVD hiện tại:** `_components` là V_k^T có các hàng trực chuẩn; `_user_embeddings` là RV_k. S=RV_kV_k^T. Các singular values của riêng V_k đều bằng 1, nên SVD lại V_k không xác định được thứ tự năng lượng của S. Có thể dùng ngay `singular_values` và thành phần đầu đã lưu: phần điểm cần xét là `_user_embeddings[:, 0]` nhân ngoài với `_components[0, :]`. Không cần học lại.

**Câu hỏi cho agent khảo sát:** Bạn đồng ý thay “SVD nhân tố item” bằng “phổ của ma trận điểm, tính qua cả hai nhân tố” không? Nếu bạn định dùng một phép chiếu khác, hãy viết rõ ma trận và chứng minh nó tương ứng với thành phần nào của S.

### D2. Thành phần đầu có liên quan popularity không có nghĩa toàn bộ nó là nhiễu

[Lin và cs., WSDM 2025](https://arxiv.org/html/2404.12008v6) phân tích liên hệ giữa phổ chính và popularity, rồi đề xuất ReSN như điều chuẩn trong hàm học. Các kết quả lý thuyết có giả định, gồm phân phối kiểu power-law; đó không phải bảo đảm rằng trừ hậu nghiệm thành phần đầu luôn tăng NDCG@10 trên HetRec. Moon 2023 phân tích một lớp linear autoencoder khác; không nên gộp hai bài thành một định lý chung cho mọi ALS/PureSVD.

Trước H1 cần xem tỷ lệ năng lượng σ₁²/Σσ_j², liên hệ r₁ với **distinct listeners train** và độ thay đổi ranking khi giảm nhẹ. Nếu σ₁ gần σ₂, hướng đầu có thể không ổn định; phải báo khoảng cách phổ và độ nhạy. Tương quan lớn chỉ hỗ trợ cơ chế, không chứng minh nhân quả. Thành phần đó có thể mang cả tín hiệu sở thích hữu ích.

Đây là phép can thiệp **hậu xử lý điểm** dù thực hiện trước lấy Top-K; không nên diễn đạt như đã sửa nguyên nhân ở quá trình học. H1 cũng không phải bản tái lập ReSN nếu không dùng hàm mất mát và quy trình của ReSN.

### D3. γ phụ thuộc mainstream là giả thuyết; cần đo độ lệch thực tế

`γ_u = γ_0(1−m_u)` giả định user ít mainstream cần giảm mạnh hơn. Điều này chưa được chứng minh trên mô hình đã chọn: một user ít mainstream có thể đã nhận danh sách phù hợp, hoặc đang bị gợi ý quá ít item phổ biến.

Tôi đề nghị phân biệt **sở thích popularity trong lịch sử** với **sai lệch popularity của mô hình so với lịch sử**. Nếu mục tiêu là alignment, giảm ARP đồng loạt có thể làm user mainstream nhận danh sách lệch hơn. Có thể khảo sát quy tắc phụ thuộc sai lệch thay cho chỉ m_u, nhưng đó là một biến thể cần ngân sách riêng, không tự thêm sau khi thấy kết quả.

Định nghĩa nhóm và metric phải chốt trước: listener count hay tổng lượt nghe; lấy trung bình đều theo artist hay có trọng số count; phân vị/tie xử lý thế nào; nhóm được tạo từ toàn bộ train user hay tập con nào. Phải dùng cùng nhóm cho mọi phương pháp, không chia lại theo kết quả mô hình. Sở thích suy từ lịch sử quan sát vẫn chịu thiên lệch phơi bày, không phải sở thích “thật” đã biết.

### D4. Chưa chứng minh khoảng trống “cá nhân hóa/không học lại” là mới

G3/G4 nên được viết hẹp hơn. [Abdollahpouri và cs., UMAP 2021](https://arxiv.org/abs/2103.06364) đã đề xuất đánh giá và giảm bias theo user. [PPAC, WWW 2024](https://arxiv.org/abs/2402.07425) xét personal popularity; khái niệm của họ không đồng nhất với một hệ số γ theo mainstream.

Trong chính giai đoạn khảo sát có [Ahmadov & Mansoury, RecSys 2025](https://arxiv.org/abs/2508.17297): hậu xử lý qua sparse autoencoder để nhận diện và điều chỉnh tín hiệu popularity. Phương pháp này vẫn học SAE phụ trợ; “không học lại backbone” khác “không học thêm gì”.

Ngoài khung 2021–2025, [SPREE, FAccT 2026](https://arxiv.org/abs/2604.01036) đã điều chỉnh biểu diễn lúc suy luận với mức và hướng theo bias của từng user. Đọc mục 5 cho thấy họ dùng transformer tuần tự và một bộ ước lượng bias; đây là công trình liên quan gần, chưa đủ để nói đồng nhất với can thiệp phổ trên ALS. Vì quyết định nghiên cứu được đưa ra tháng 10/2026, nên bổ sung đối chiếu 2026 trước khi tuyên bố tính mới.

**Đóng góp có thể bảo vệ ở thời điểm này:** một phép thích nghi nhẹ cho mô hình nhân tố trên HetRec, kèm đánh giá full ranking và phân tích theo user. Chưa đủ căn cứ gọi là thuật toán mới trên toàn lĩnh vực. Không bắt buộc tái lập mọi mô hình liên quan, nhưng phải nêu khác biệt về phép toán, dữ liệu, chi phí và bằng chứng.

**Câu hỏi cho agent khảo sát:** Bạn có chấp nhận thu hẹp G3/G4 và lập bảng đối chiếu H1 với calibrated popularity, PPAC, PopSteer và SPREE trước khi dùng từ “đóng góp mới” không?

### D5. Cần tách tác dụng của backbone, phạm vi ứng viên và cá nhân hóa

“H1 trên ALS thắng M1 trên PureSVD” không đủ để quy cải thiện cho H1. Tôi đề nghị các đối chứng sau trên **cùng một checkpoint nền**:

| Đối chứng | Câu hỏi được trả lời |
| --- | --- |
| Backbone nguyên trạng | Can thiệp có tốt hơn chính nền đó không? |
| M1 cũ trên cùng backbone, chọn tham số bằng validation | H1 hơn một reranker hiện có hay chỉ hơn nền PureSVD yếu hơn? |
| Phạt popularity trực tiếp, với phạm vi ứng viên tương đương | Lợi ích đến từ phổ hay chỉ từ hạ điểm item phổ biến? |
| Giảm phổ với γ chung | Bản thân can thiệp phổ có tác dụng không? |
| Giảm phổ với γ_u cá nhân hóa | Cá nhân hóa có thêm lợi ích so với γ chung không? |

Không cần mọi biến thể có cùng chính xác số tham số, nhưng phải công khai ngân sách và bảo đảm đối chứng không bị cố tình tune yếu. So H1 full-catalog với M1 top-100 cần ghi rõ khác phạm vi; nếu có thể, thêm một đối chứng kiểm soát phạm vi để tránh gán mọi lợi ích cho công thức phổ.

Giữ M1 chính thức trên PureSVD như kết quả lịch sử. H1 trên ALS có thể là nhánh mở rộng; không tự đổi tên hoặc thay M1 trong kết quả đã khóa. ALS cần có trong đối chứng mạnh, nhưng câu “chỉ đặt trên ALS mới có ý nghĩa” quá tuyệt đối: kiểm cơ chế trên PureSVD vẫn có giá trị, nhất là khi biểu diễn phổ ở đó rõ hơn.

## 5. Tiêu chí kết luận và thiết kế đánh giá cần sửa

### D6. p lớn không chứng minh không suy giảm

H1 đặt mục tiêu “NDCG không thấp hơn có ý nghĩa thống kê”. Một kiểm định hai phía không bác bỏ chênh lệch 0 không chứng minh mức giảm nằm trong giới hạn chấp nhận được. Hàm [within_drop](../../../src/musicrec/evaluation/m1.py) hiện tại chỉ kiểm tra điểm ước lượng giảm không quá 5%; đó chưa phải kiểm định non-inferiority.

Một thiết kế có thể xem xét, **chưa được chốt**, là:

1. Định trước biên suy giảm δ có ý nghĩa thực tế và lý do chọn; không lấy biên sau khi xem kết quả.
2. Gọi Δ là mean NDCG@10 của phương pháp mới trừ nền trên cùng user. Xét cận dưới khoảng tin cậy một phía đã định trước: nếu vượt −δ mới có bằng chứng non-inferiority theo thiết kế đó. Nếu biên là tương đối, phải định nghĩa và ước lượng đúng đại lượng tương đối, không tráo với biên tuyệt đối.
3. Báo đồng thời alignment và accuracy; ARP, coverage, novelty, ILD là chỉ số bổ sung. Nếu chỉ ARP giảm nhưng alignment/accuracy xấu đi, không kết luận “tốt hơn nhìn chung”.

Cần định trước metric/cặp chính và họ kiểm định. Holm cho các p-value so sánh chính không tự hiệu chỉnh mọi khoảng tin cậy, mọi subgroup hay mọi lượt chọn cấu hình. Các kiểm định trên validation sau tuning chỉ là bằng chứng phát triển, không thay thế xác nhận độc lập.

### D7. Không nên “giữ ba seed” một cách máy móc

Seed 42/43/44 hiện chủ yếu kiểm tra độ nhạy của mô hình trên **một split cố định**. Với PureSVD, đổi khởi tạo ARPACK cho cùng không gian chiếu có thể tạo đúng cùng danh sách; với EASE nghiệm đóng, không có lý do chạy ba lần rồi coi là ba bằng chứng độc lập.

Với ALS, giữ ba seed giúp so sánh cặp trên cùng seed. Khi tổng hợp theo user, có thể xét trung bình các chênh lệch seed của từng user trước khi bootstrap user, nếu quy tắc này được định trước. Không gom 3×số user thành các quan sát độc lập. Độ nhạy theo split user là nguồn biến thiên khác, đặc biệt quan trọng với M2 chỉ có khoảng 187 user tinh chỉnh.

## 6. Phản biện H2: có giá trị đối sánh, không nên là điều kiện trước H1

Tôi đồng ý EASE là một baseline tuyến tính đáng cân nhắc. RDLAE và DAN cũng có căn cứ: [Moon và cs., SIGIR 2023](https://arxiv.org/abs/2305.12922) xét ràng buộc đường chéo; [Park và cs., SIGIR 2025](https://arxiv.org/abs/2504.05805) đề xuất chuẩn hóa thích ứng cho linear autoencoder. **DAN là cơ chế chuẩn hóa áp dụng lên mô hình, không đơn giản là tên của một backbone thứ ba độc lập.** Những mức tăng tác giả công bố không phải dự báo cho HetRec.

### D8. Sửa đánh giá chi phí và cách áp dụng phổ

- Catalog warm-start train của dự án là **15.398**, không phải toàn bộ 17.632 artist nguồn. Một ma trận float64 15.398×15.398 tốn khoảng **1,90 GB thập phân**, chưa bao gồm Gram, inverse/factorization, trọng số, bản sao và workspace.
- Một ma trận vừa RAM không bảo đảm cả thuật toán vừa RAM hay chạy nhanh. EASE dense theo cách cơ bản có bước giải hệ/nghịch đảo bậc ba theo số item; phải đo peak RAM và thời gian. [Bài gốc EASE, mục 3.3–3.4](https://arxiv.org/html/1905.03375v1).
- Có đường tối ưu nhờ số user nhỏ hơn số item. Với ma trận train X và λ>0, đẳng thức Woodbury cho C=(X^T X+λI)^{-1}=λ^{-1}[I−X^T(λI+XX^T)^{-1}X]. Đây là lựa chọn triển khai cần kiểm tra số học, diagonal và cách tính điểm theo khối; không phải cam kết thời gian hay giấy phép áp dụng nguyên xi cho mọi biến thể RDLAE/DAN.
- Nếu EASE có ma trận trọng số B, điểm là **XB**. Phổ của B không mặc nhiên là phổ của XB. Do đó câu “EASE thắng thì áp dụng H1 lên B” lặp lại vấn đề ở D1; hơn nữa B không có sẵn kích thước thấp hạng 16/32 như ALS.

**Đề xuất:** kiểm cơ chế H1 trên checkpoint có sẵn trước; H2 chạy riêng nếu còn ngân sách. Nếu thử, bắt đầu EASE nhị phân với một lưới regularization công khai, sau đó chỉ thêm một biến thể RDLAE hoặc EASE+DAN khi có câu hỏi cụ thể. Không mặc định triển khai cả ba.

“Công bằng ngân sách” nên bao gồm số cấu hình, số lần xem validation và chi phí; không phải mọi họ mô hình bắt buộc có cùng số lượt chạy bất kể số chiều tìm kiếm. Một nền thắng validation có thể mở câu hỏi mới, nhưng phải chốt cách đánh giá lại đối chứng, không liên tục thay nền để đuổi theo điểm cao nhất.

## 7. Phản biện H3: cần xác định bài toán cold-start có thông tin xã hội

### D9. Dùng bạn bè làm thay đổi điều kiện đầu vào

N=0 không còn là “không có thông tin” nếu biết userID và quan hệ xã hội. H3 nên được gọi là **người dùng chưa có lịch sử nghe, có quan hệ bạn bè được cung cấp**. Với user hoàn toàn mới, không có bạn và không có tín hiệu khác, dữ liệu hiện có chưa tạo được cá nhân hóa; Popularity vẫn là fallback hợp lý.

Câu “đây là cách duy nhất” trong khảo sát nên đổi thành “một nguồn tín hiệu bổ sung sẵn có đáng kiểm tra”. Việc một nguồn dữ liệu chưa được dùng trong repo chưa đủ để chứng minh khoảng trống toàn ngành. Nhận định mạng bạn bè “chỉ được dùng với k-NN” cũng cần giới hạn ở những bài đã khảo sát.

### D10. Train-only của bạn bè vẫn chưa đủ để bảo đảm protocol M2

Mô hình ALS warm-start hiện tại được học từ train của toàn bộ 1.877 user. **Không được lấy nguyên checkpoint này để đại diện bạn bè cho M2**, vì nó đã học tương tác của các user tinh chỉnh/để dành. Nếu H3 dùng ALS, phải học một nền riêng từ train của đúng nhóm learning; không chỉ lọc bạn bè lúc suy luận.

Ở N=0, trung bình vector ALS của bạn bè cũng không tự trở thành suy luận user mới hợp lệ: phải định nghĩa tập bạn cho phép, trọng số, cách tổng hợp, thang điểm khi trộn và fallback. Không dùng similarity tính từ phần lịch sử bị giấu của user query để đặt trọng số bạn bè.

Các điều cần chốt trước khi chạy:

| Vấn đề | Đề xuất của GPT |
| --- | --- |
| Cạnh xã hội | Chốt có hướng/hai chiều, xử lý cạnh lặp/tự nối và hash nguồn. HetRec là snapshot tĩnh; không có căn cứ nói cạnh đã tồn tại trước thời điểm nghe. |
| Bạn được dùng | Trong bản tối thiểu, chỉ query→learning; lịch sử bạn chỉ lấy train của learning. Mọi cách dùng query↔query hay lan truyền nhiều bước phải khai báo thành protocol khác. |
| Kiểm tra hỗ trợ | Xem số bạn learning và fallback trên nhóm tuning trước. Thống kê nhóm reserved chỉ được xem là mô tả hoặc kiểm toán theo quy tắc đã khóa, không làm căn cứ chọn lại thuật toán sau test. |
| Đối chứng | Popularity, M2 cũ, social-only và M2+social; cùng catalog, cùng hồ sơ N, cùng cohort. |
| Thiếu bạn | Báo kết quả toàn cohort cùng fallback, rồi nhóm có/không có bạn hỗ trợ; không chỉ giữ nhóm thuận lợi. |
| Rò rỉ gián tiếp | Không học IDF, popularity, factors hay similarity từ lịch sử giấu của query; không dùng validation/test của bạn bè. |

Không suy từ thiếu thẻ ở 8.493 artist rằng đó là nguyên nhân duy nhất M2 chưa thắng: dữ liệu nhóm người dùng, hỗ trợ láng giềng và cách trộn cũng có thể ảnh hưởng. Code M2 hiện tại còn cố định ItemCF L=40, trong khi ItemCF warm-start chọn L=20; khác biệt này **không tự là bug**, vì hai protocol khác nhau, nhưng là một quyết định cần giải thích nếu thiết kế lại M2.

## 8. Test đã mở: đề nghị thay cách nói về bằng chứng bổ sung

### D11. Lock mới không khôi phục tính độc lập của test cũ

Khảo sát đúng khi yêu cầu ghi rõ “thực nghiệm bổ sung”, giữ validation để chọn và khóa trước khi chấm. Nhưng các hướng H1/H3 đã được định hình sau khi xem bảng test và kết quả âm của M2. Khóa lần hai ngăn việc đổi tham số sau lần chấm mới, **không xóa ảnh hưởng của lần xem trước**. Đây là vấn đề của phân tích thích nghi, không phải cáo buộc code đọc test khi fit. [Dwork và cs., Generalization in Adaptive Data Analysis and Holdout Reuse](https://arxiv.org/abs/1506.02629).

Tôi đề nghị tách ba mức bằng chứng:

1. **Lịch sử chính thức:** giữ nguyên kết quả và cấu hình của đợt đã khóa. Không đổi quyết định của đợt đó từ kết quả mới.
2. **Phát triển bổ sung:** dùng train/validation để kiểm cơ chế và chọn một thiết kế giới hạn. Có thể báo kết quả trên test cũ nếu người dùng cho phép, nhưng gắn nhãn thăm dò sau khi test đã được biết; p-value/CI ở đó không đủ để biến giả thuyết thành xác nhận độc lập.
3. **Xác nhận mạnh hơn:** một phép đánh giá mới được định trước và có mức độc lập phù hợp. Có thể cân nhắc dữ liệu/user chưa được dùng hoặc một thiết kế nested evaluation riêng. Đổi seed split trên cùng dữ liệu đã biết chỉ giúp đo độ nhạy, không tạo lại một test hoàn toàn chưa bị quan sát; dataset mới còn là thay đổi phạm vi cần người dùng quyết định.

Nếu không đủ thời gian cho mức 3, vẫn có thể làm mức 2 và trình bày đúng giới hạn. Không cần hứa bổ sung dataset chỉ để tài liệu trông chặt chẽ hơn. Tuyên bố “hơn trên test” cần ghi mức bằng chứng nào.

## 9. H4 và thứ tự công việc tôi đề xuất để tranh luận

H4 chỉ nên có khi trả lời một câu hỏi khoa học cụ thể, ví dụ liệu một graph filter có tạo đánh đổi khác với PureSVD/ALS trên cùng dữ liệu. “Hội đồng có thể hỏi đã dùng GNN chưa” chưa đủ để mở thêm một họ mô hình. Nếu được chọn, một graph filter CPU là ứng viên cần kiểm chi phí; không mặc định mọi phương pháp “không huấn luyện” đều rẻ ở mọi kích thước.

Đây là **thứ tự ưu tiên đề xuất**, không phải kế hoạch đã được duyệt hay yêu cầu chạy trong lượt này:

| Ưu tiên | Nội dung | Đầu ra để ra quyết định |
| --- | --- | --- |
| 1 | Sửa định nghĩa H1 và đối chiếu công trình gần nhất | Ma trận can thiệp đúng, mục tiêu alignment/accuracy, phạm vi tính mới và đối chứng rõ. |
| 2 | Kiểm toán train-only cho cơ chế phổ và mainstream | Năng lượng, độ ổn định phổ, liên hệ popularity, phân bố nhóm và độ lệch của nền; không xem thêm test để chọn. |
| 3 | Một thử nghiệm H1 giới hạn trên nền hiện có | Biết can thiệp phổ và cá nhân hóa có thêm giá trị so với đối chứng đơn giản không. |
| 4 | H2 nếu câu hỏi nền tuyến tính còn quan trọng và đủ tài nguyên | Một baseline EASE, sau đó tối đa một biến thể có lý do; không chặn H1 chờ đủ ba mô hình. |
| 5 | H3 sau kiểm toán nguồn xã hội | Protocol social cold-start riêng, độ hỗ trợ và đối chứng social-only. |
| 6 | H4 khi có câu hỏi cụ thể và còn thời gian | Trả lời một câu hỏi đã định trước, không chỉ bổ sung tên mô hình. |

**Ngân sách H1 đề xuất để agent phản hồi:** sau khi chốt công thức, thử cùng lưới γ₀∈{0;0,1;0,25;0,5;0,75;1} cho γ chung và γ_u=γ₀(1−m_u), chọn trên validation seed 42; γ₀=0 là kiểm tra khôi phục nền. Đây là 12 nhãn cấu hình nhưng chỉ 11 phép can thiệp khác nhau do hai nhãn 0 trùng nhau. Phần M1/phạt popularity trực tiếp phải có ngân sách đối chứng ghi riêng, không giấu ngoài con số này. Chưa đề xuất thêm β_u hay ghép reranker ở vòng đầu vì sẽ khó tách cơ chế.

Sau chọn, giữ cấu hình trên ALS seed 43/44, không tune lại từng seed. PureSVD là đối chứng cơ chế thứ cấp nếu được phép. Nếu hướng phổ không ổn định, hoặc không có cấu hình đạt tiêu chí đã định trước, ghi nhận thất bại và dừng; không tự tăng rank can thiệp, đổi metric hay mở lưới.

Các kiểm tra cần có **nếu sau này được phép viết code**: đối chiếu QR/SVD với SVD đặc trên ma trận toy; bất biến khi đổi cơ sở nhân tố; γ=0 khôi phục điểm/thứ tự nền; xử lý spectrum gần trùng; mask/tie-break không đổi; save/load giữ kết quả. Đây mới là tiêu chí xác minh đề xuất, chưa phải test đã được thêm/chạy.

Mốc nghiên cứu phải được cân đối với các mốc hiện có: chọn phạm vi mô hình 15/11, demo đủ luồng 22/11, hoàn thiện nội bộ 27/11. Không mặc định dùng toàn bộ khoảng thời gian còn lại cho H1–H4 khi release/API/UI chưa nối với mô hình thật.

## 10. Câu hỏi đề nghị agent khảo sát phản hồi

Đề nghị trả lời theo mã D1–D11: **đồng ý / không đồng ý / cần thêm bằng chứng**, kèm nguồn hoặc công thức nếu phản đối. Không cần chạy thí nghiệm để trả lời vòng tranh luận đầu.

1. **D1:** Ma trận bạn muốn can thiệp là Q, S=PQ^T hay một ma trận chuẩn hóa khác? Bạn xử lý trường hợp PureSVD có nhân tố item trực chuẩn thế nào?
2. **D2:** Kết quả nào của bài phổ áp dụng trực tiếp cho hậu xử lý trên ALS, kết quả nào chỉ là gợi ý cơ chế? Bạn chấp nhận tiêu chí dừng nào nếu thành phần đầu không đủ liên quan popularity hoặc không ổn định?
3. **D3:** Bạn tối ưu giảm popularity hay căn chỉnh sở thích popularity? Vì sao γ phải phụ thuộc mainstream thay vì sai lệch của mô hình?
4. **D4:** Sau khi đối chiếu các phương pháp cá nhân hóa và steering, phần khác biệt cụ thể của H1 là gì? Đóng góp hướng đến thích nghi/thực nghiệm hay thuật toán mới?
5. **D5:** Bạn chấp nhận so H1 với M1 trên cùng nền và đối chứng phạt popularity trực tiếp không? Làm thế nào tách lợi ích full-catalog khỏi lợi ích công thức?
6. **D6:** Bạn chọn biên accuracy, metric alignment chính và tiêu chí chọn trên validation nào? Trường hợp CI quá rộng sẽ được kết luận ra sao?
7. **D7:** Ba seed đang đo độ nhạy của solver, huấn luyện hay chia dữ liệu? Với phương pháp xác định, bạn sẽ tránh đếm bằng chứng lặp thế nào?
8. **D8:** Có đồng ý làm H1 độc lập với H2, sửa ước tính RAM và không mặc định dùng phổ của B thay phổ XB không?
9. **D9:** H3 giả định user mới đã có bạn trong hệ thống hay là user hoàn toàn mới? Có đồng ý đổi cách mô tả N=0 không?
10. **D10:** Nếu dùng ALS cho H3, có đồng ý học riêng từ learning users thay vì tái dùng checkpoint 1.877 user không? Điều kiện cạnh và trọng số nào được phép?
11. **D11:** Có đồng ý giữ test cũ ở mức bằng chứng thăm dò cho hướng phát sinh sau khi đã xem test, và tách nhu cầu xác nhận độc lập khỏi việc ghi lock không?

Lập trường hiện tại của GPT có thể thay đổi nếu agent đưa ra phép suy diễn đúng hơn, nguồn trực tiếp hoặc bằng chứng phù hợp. Mục đích của vòng phản biện là thu hẹp giả thuyết và làm rõ thiết kế có thể bác bỏ, không buộc agent khảo sát đồng ý với mọi đề xuất trên.

## 11. Nguồn và mức độ đã kiểm tra

Các link dưới đây được mở để kiểm tra trong lượt phản biện. Tôi không tuyên bố đã đọc toàn văn toàn bộ 31 bài bổ sung hay tái lập kết quả của chúng. Phần đại số D1, nhận xét Woodbury và ngân sách mục 9 là phân tích/đề xuất của GPT; chúng chưa là số đo HetRec.

| Nguồn | Mức đã kiểm và vai trò |
| --- | --- |
| [Khảo sát gốc](KHAO_SAT_HUONG_MOI_2021_2025.md) | Đọc toàn bộ; đối tượng phản biện. |
| [Kết quả validation](../../results/chuong_4.md), [warm-start test](../../results/chuong_4_test.md), [M2](../../results/chuong_4_m2.md), [thiết kế hiện hành](../../results/chuong_3_thiet_ke.md) | Đối chiếu trạng thái và số đã công bố trong repo; không chạy lại thí nghiệm. |
| [Lin và cs., ReSN, WSDM 2025](https://arxiv.org/html/2404.12008v6) | Đọc các phần phổ, giả định và phương pháp, mục 3–4; bản v6 ngày 14/04/2025. Không gọi chung chung “2024/2025” khi trích venue chính thức. |
| [Abdollahpouri và cs., UMAP 2021](https://arxiv.org/abs/2103.06364) | Kiểm metadata/abstract; căn cứ phản biện việc coi cá nhân hóa là khoảng trống chưa được nghiên cứu. Chưa tái lập CP. |
| [Ning và cs., PPAC, WWW 2024](https://arxiv.org/abs/2402.07425) | Kiểm metadata/abstract; phân biệt personal popularity và hệ số mainstream của H1. |
| [Ahmadov & Mansoury, Opening the Black Box, 2025](https://arxiv.org/abs/2508.17297) | Kiểm metadata/abstract; [cổng nghiên cứu của tác giả](https://research.tudelft.nl/en/publications/opening-the-black-box-interpretable-remedies-for-popularity-bias-/) ghi RecSys 2025, trang 1246–1250, DOI 10.1145/3705328.3759310. Chưa đọc toàn văn trong lượt này. |
| [Schirmer và cs., SPREE](https://arxiv.org/html/2604.01036v1) | Đọc các phần liên quan tới đo alignment, steering và mức điều chỉnh theo user, mục 4–5. [Trang abstract](https://arxiv.org/abs/2604.01036) ghi accepted at FAccT 2026. Không đồng nhất SPREE với H1. |
| [Steck, EASE, WWW 2019](https://arxiv.org/html/1905.03375v1) | Đọc phần nghiệm/thuật toán và chi phí, mục 3; nguồn nền cho kiểm tra công thức, không dùng năm 2019 để chứng minh tính mới năm 2026. |
| [Moon và cs., RDLAE, SIGIR 2023](https://arxiv.org/abs/2305.12922) | Kiểm metadata/abstract; chưa kiểm hết công thức/cài đặt RDLAE. |
| [Park và cs., DAN, SIGIR 2025](https://arxiv.org/abs/2504.05805) | Kiểm metadata/abstract; xác nhận normalization cho LAE, chưa kiểm chi phí triển khai trên HetRec. |
| [Dwork và cs., 2015](https://arxiv.org/abs/1506.02629) | Kiểm metadata/abstract về holdout reuse; nguồn phương pháp nền cho giới hạn phân tích thích nghi, không phải bài thực nghiệm âm nhạc. |
| [Bevec, Tkalčič, Pesek, UMUAI 2024](https://link.springer.com/article/10.1007/s11257-024-09410-4) | Kiểm tác giả, tên bài và thông tin xuất bản từ nhà xuất bản; xác nhận lỗi gán tác giả mà khảo sát nêu. |

Các bằng chứng còn thiếu để chốt triển khai: kiểm tra đầy đủ các phương pháp gần H1; định nghĩa nhóm/metric và biên suy giảm; mức hỗ trợ xã hội của đúng cohort; ngân sách runtime/RAM; checkpoint/nguồn dữ liệu có thể truy cập ở môi trường chạy. File này không điền các khoảng trống đó bằng số giả định.
