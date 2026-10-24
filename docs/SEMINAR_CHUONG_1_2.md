# Tài liệu chuẩn bị seminar MusicRec: Chương 1–2, dữ liệu và nghiên cứu liên quan

Ngày cập nhật phạm vi và phương pháp: 19/10/2026, theo [hướng dẫn của GVHD](Hướng%20dẫn%20từng%20bước%20hoàn%20thành%20khóa%20luận.docx) và [kế hoạch từng bước](WEEKLY_IMPLEMENTATION_PLAN.md). Đã có kiểm tra nguồn Bước 1 và EDA Bước 2 chạy lại từ dữ liệu gốc, xem [data card](data-card.md) và [metrics EDA](../outputs/runs/raw_eda_20261019_verified/metrics.json). Những thống kê seminar trước đây vẫn có nguồn thời điểm riêng; kết quả mô hình chưa có và các lựa chọn nghiên cứu chưa được xem là đã có GVHD duyệt.

## 1. Điều cần nói rõ trong 60 giây

> Nhóm nghiên cứu bài toán khuyến nghị Top-K nghệ sĩ chưa xuất hiện trong lịch sử quan sát của người dùng, từ số lượt nghe trong HetRec 2011 Last.fm 2K. Dữ liệu là phản hồi ngầm: nghe nhiều là bằng chứng về sự quan tâm, nhưng chưa nghe không chứng minh không thích. Nhóm dự kiến so sánh Random, Popularity, UserCF, ItemCF, MF có độ lệch và PureSVD trên cùng giao thức; sau đó kiểm chứng M1 về tái xếp hạng và M2 cho hồ sơ ít lịch sử. Kết quả được đánh giá bằng chất lượng xếp hạng, độ bao phủ, mức phổ biến và chi phí, rồi mới chọn mô hình để triển khai prototype.

**Bảy ý phải nắm trước khi lên trình bày:**

1. Item của bộ dữ liệu này là **nghệ sĩ**, không phải bài hát.
2. Một dòng là **một cặp user–artist với số lượt nghe tổng hợp**, không phải một lần phát nhạc.
3. Listening count không phải rating 1–5 sao; ô chưa quan sát không phải nhãn “không thích”.
4. User-CF tìm người có lịch sử tương tự; Item-CF tìm nghệ sĩ được các nhóm người nghe tương tự; MF học vector user/item.
5. RMSE và chất lượng Top-K đo hai mục tiêu khác nhau.
6. `user_artists.dat` không có timestamp, nên không thể dùng nó để chứng minh dự đoán theo thời gian.
7. Mọi phát biểu “cải tiến”, “tốt hơn”, “giảm bias” phải gắn với baseline, metric và điều kiện thực nghiệm.

## 2. Chương 1: hiểu bài toán và bảo vệ phạm vi

### 2.1. Bối cảnh → vấn đề → mục tiêu

| Nội dung trong đề cương | Cách hiểu và cách giải thích |
| --- | --- |
| Quá tải thông tin | Người dùng khó khám phá nghệ sĩ phù hợp trong một catalog lớn; hệ thống cần xếp hạng theo từng người. |
| Lựa chọn CF | Có dữ liệu hành vi user–artist; CF tận dụng quan hệ đồng nghe mà không bắt buộc có audio/lyrics. |
| Độ thưa | Phần lớn cặp user–artist chưa được quan sát; tương đồng và vector tiềm ẩn khó ước lượng ổn định. |
| Cold-start | User/item hoàn toàn mới thiếu bằng chứng để cá nhân hóa bằng CF. |
| Popularity bias | Nghệ sĩ đông người nghe có thể chiếm nhiều vị trí, làm người thích nhạc ngách nhận gợi ý kém phù hợp. |
| Mục tiêu | So sánh có kiểm soát, kiểm chứng một cải tiến, xây demo; chưa cam kết một mô hình sẽ thắng. |

Không nên nói “CF không cần thông tin gì về user/item”: CF vẫn cần lịch sử tương tác và định danh. Nó không bắt buộc cần thuộc tính nội dung.

### 2.2. Phát biểu toán học tối thiểu

Gọi $U$ là tập người dùng, $I$ là catalog nghệ sĩ, $H_u$ là lịch sử dùng làm đầu vào và $s(u,i)$ là điểm mô hình. Hệ thống xếp hạng:

$$L_u=\operatorname{TopK}_{i\in I\setminus H_u}s(u,i).$$

Input offline: `(userID, artistID, weight)`. Input demo: user có sẵn hoặc lịch sử nghệ sĩ nhập vào. Output: danh sách K nghệ sĩ, score và thông tin hiển thị nếu có. **Score không tự động là xác suất thích**; muốn diễn giải như xác suất phải có mô hình và kiểm tra hiệu chuẩn tương ứng.

“Chưa nghe” trong báo cáo nên viết thành “chưa xuất hiện trong lịch sử quan sát”. Bộ dữ liệu chỉ chứa một phần lịch sử tổng hợp, không chứng minh user chưa từng nghe nghệ sĩ đó ngoài đời.

### 2.3. Câu hỏi nghiên cứu nên trả lời bằng gì?

| RQ của đề cương | Minh chứng cần có |
| --- | --- |
| RQ1: mô hình nào phù hợp? | Cùng split/candidate/evaluator; ranking metric chính, coverage và thời gian suy luận. |
| RQ2: độ thưa/lịch sử ảnh hưởng thế nào? | Nhóm user xác định từ train; thí nghiệm giảm lịch sử có kiểm soát nếu các nhóm tự nhiên quá giống nhau. |
| RQ3: cải tiến có ích không? | Base model và base + cải tiến; chọn tham số trên validation; ablation và trade-off. |
| RQ4: fallback cho user mới/ít lịch sử? | Ca không có lịch sử và có vài nghệ sĩ; mô tả mức cá nhân hóa và thí nghiệm riêng. |
| RQ5: triển khai khả thi không? | API trả kết quả đúng với offline, loại seen items, đo latency trên máy thực nghiệm. |

Một cách cụ thể hóa RQ3 để thảo luận: **“Phạt độ phổ biến trong bước rerank có tăng coverage và giảm tỷ lệ nghệ sĩ phổ biến, với mức giảm NDCG@10 nằm trong ngưỡng chấp nhận đã định trước không?”** Ngưỡng này phải chốt trước khi đọc test; chưa có số liệu để khẳng định đáp án.

### 2.4. Đóng góp và giới hạn

Đóng góp dự kiến là quy trình so sánh tái lập, phân tích dữ liệu/nhóm user, kiểm chứng cải tiến và prototype. So sánh các thuật toán đã có là mục tiêu thực nghiệm có giá trị khi thiết kế rõ, nhưng **không đủ căn cứ để gọi là thuật toán mới** hoặc khẳng định khoảng trống của toàn ngành.

Giới hạn hợp lý: dữ liệu tĩnh năm 2011, quy mô nhỏ, không audio/lyrics, không phản hồi live, chưa đại diện người nghe Việt Nam năm 2026. Dữ liệu cũ vẫn dùng được để kiểm chứng phương pháp trong một benchmark; không dùng nó để khẳng định sở thích thị trường hiện nay.

## 3. Chương 2: hiểu trực giác trước khi học công thức

### 3.1. Các họ phương pháp

| Phương pháp | Tín hiệu chính | Ví dụ |
| --- | --- | --- |
| Content-based | Đặc trưng nghệ sĩ/nhạc: tag, thể loại, audio… | Gợi ý nghệ sĩ có đặc trưng gần hồ sơ sở thích. |
| Collaborative filtering | Hành vi của nhiều user | Người thường nghe A cũng nghe B. |
| Hybrid | Kết hợp hành vi và nội dung | Dùng tương tác khi đủ dữ liệu, nội dung hỗ trợ item ít tương tác. |
| Popularity baseline | Độ phổ biến toàn cục | Những nghệ sĩ nhiều người nghe; không cá nhân hóa score. |

Item-CF vẫn là CF: “item giống nhau” được tính từ hành vi user, không nhất thiết từ thể loại hoặc âm thanh. Hai nghệ sĩ đồng nghe chưa chắc có nhạc giống nhau theo cảm nhận.

### 3.2. Explicit và implicit feedback

Explicit: user chủ động đánh giá 1–5 sao hoặc like/dislike. Implicit: nghe, click, mua, xem; suy ra quan tâm gián tiếp. Người nghe 100 lần không nhất thiết thích gấp 10 lần người nghe 10 lần: có thể khác thời gian sử dụng, playlist, nghe nền hoặc mức tiếp xúc.

Với số lượt nghe $w_{ui}$:

$$x_{ui}=\log_2(1+w_{ui}).$$

Log làm giảm chênh lệch giữa giá trị rất lớn và nhỏ: `1 → 1`, `10 → 3,459`, `100 → 6,658`. Nó giữ thứ tự nhưng nén thang đo. **Log-transform không biến count thành rating thật và không xử lý hết vấn đề implicit feedback.**

Thiết kế hiện hành còn giữ riêng tương tác nhị phân và điểm đại diện 1–5. Điểm đại diện dùng bốn phân vị 20/40/60/80% của log-count trên train, nội suy tuyến tính và quy tắc lớn hơn nghiêm ngặt; không học lại ngưỡng từ validation/test. UserCF, ItemCF và MF có độ lệch bắt đầu từ điểm đại diện theo V1; PureSVD sẽ kiểm tra ba biểu diễn tại cấu hình cố định. Đây là lựa chọn nhóm kiểm chứng, không phải phép biến đổi được Hu et al. chứng minh tối ưu.

Theo Hu et al. (2008), có thể tách:

$$p_{ui}=\mathbf{1}[w_{ui}>0],\qquad c_{ui}=1+\alpha w_{ui}.$$

$p$ là tín hiệu ưu tiên nhị phân; $c$ là độ tin cậy trong mục tiêu huấn luyện. Cặp không quan sát có $p=0$ và confidence thấp hơn cặp được nghe nhiều; đây là giả định mô hình, không chứng minh user không thích. Có thể thử biến thể confidence dùng log; phải công bố công thức và chọn $\alpha$ trên validation. Không sao chép tham số của bài báo và coi là tối ưu cho Last.fm.

### 3.3. User-based CF

Trực giác: tìm người có lịch sử gần user mục tiêu, rồi lấy tín hiệu từ các nghệ sĩ họ nghe mà user mục tiêu chưa có trong lịch sử.

Ví dụ minh họa, **không phải bản ghi thật**:

| User | A | B | C | D |
| --- | ---: | ---: | ---: | ---: |
| An | 1 | 1 | 0 | 0 |
| Bình | 1 | 1 | 1 | 0 |
| Chi | 0 | 0 | 0 | 1 |

An và Bình gần nhau; C là ứng viên gợi ý cho An. Số 0 chỉ là không có tương tác quan sát.

Một baseline cosine trên vector tương tác đã chọn:

$$\operatorname{sim}(u,v)=\frac{\mathbf{x}_u^\top\mathbf{x}_v}{\|\mathbf{x}_u\|\|\mathbf{x}_v\|},$$

Với điểm đại diện $r$ và trung bình các quan sát train $\bar r_u$, biến thể dự đoán trừ trung bình dự kiến theo V1 là:

$$\hat r_{ui}=\bar r_u+\frac{\sum_{v\in N_k(u;i)}\operatorname{sim}(u,v)(r_{vi}-\bar r_v)}{\sum_{v\in N_k(u;i)}|\operatorname{sim}(u,v)|}.$$

$N_k(u;i)$ chỉ gồm láng giềng hợp lệ có quan sát về nghệ sĩ i. Cần chốt cách lấy danh sách láng giềng và fallback khi mẫu số bằng 0 trước triển khai; không lấy trung bình trên các ô chưa quan sát như điểm 0 thật.

Cần nói rõ vector binary, log-count hay điểm đại diện; cấu hình đầu dự kiến dùng điểm đại diện theo V1. Công thức cosine giữ nguyên nguyên tắc nhưng ý nghĩa giá trị đầu vào thay đổi. Phải ghi cách xử lý thiếu dữ liệu, láng giềng hợp lệ và mẫu số bằng 0. Không nhầm $k$ láng giềng với $K$ kết quả.

Pearson trong CF rating so sánh độ lệch khỏi điểm trung bình của mỗi user, hữu ích khi user có thói quen chấm điểm khác nhau. Áp dụng vào log-count là **một lựa chọn chuyển thể cần kiểm chứng**, không phải mặc định đúng cho implicit.

Ít item chung có thể khiến similarity thiếu tin cậy. Có thể giảm trọng số:

$$\operatorname{sim}'(u,v)=\operatorname{sim}(u,v)\frac{\min(n_{uv},\gamma)}{\gamma},$$

với $n_{uv}$ là số nghệ sĩ chung trong train, $\gamma$ là ngưỡng. Nếu chỉ chung 1 nghệ sĩ và $\gamma=20$, hệ số là 0,05. Đây là ví dụ về significance weighting; cần thử tác động tới ranking và số user phải fallback.

Ưu điểm: trực giác dễ hiểu. Hạn chế: overlap thấp, user mới thiếu lịch sử, chi phí tìm láng giềng. Không khẳng định User-CF luôn kém hơn Item-CF.

### 3.4. Item-based CF

So sánh các **cột** nghệ sĩ theo các user nghe chúng; tích lũy score từ nghệ sĩ trong lịch sử:

$$\hat r_{ui}=\frac{\sum_{j\in H_u\cap N_k(i)}\operatorname{sim}(i,j)r_{uj}}{\sum_{j\in H_u\cap N_k(i)}|\operatorname{sim}(i,j)|}.$$

Đây là biến thể trung bình có trọng số dự kiến theo V1; cần xử lý mẫu số 0. Biến thể chỉ lấy tổng là phương án khác, không được âm thầm đổi giữa các lần chạy. Với Item-CF, lý do gợi ý có thể là “nghệ sĩ này thường được nghe cùng các nghệ sĩ trong lịch sử của bạn”.

Sarwar et al. trình bày cosine, correlation, adjusted cosine và cách dự đoán rating. Adjusted cosine trừ mean rating của user, phù hợp bối cảnh rating tường minh; không được lấy nguyên giả định đó cho count mà không giải thích.

Có thể tính trước similarity offline, nhưng không đồng nghĩa luôn tiết kiệm bộ nhớ. Last.fm có nhiều item hơn user: ma trận item–item đầy đủ có khoảng 311 triệu ô, tốn khoảng 1,24 GB với float32, chưa tính overhead; user–user khoảng 3,58 triệu ô, gần 14,3 MB. Đây là ước lượng cho ma trận dense, chưa phải phép đo thực nghiệm. Nên giữ sparse/top-k neighbors khi phù hợp.

### 3.5. Matrix factorization, SVD và implicit ALS

MF học vector user và item trong không gian chiều thấp:

$$\hat y_{ui}=\mu+b_u+b_i+\mathbf{a}_u^\top\mathbf{b}_i.$$

Bias giải thích xu hướng chung của user/item; tích vô hướng mô hình hóa tương tác riêng giữa chúng. Các chiều latent **không tự động mang tên “buồn”, “sôi động”, “rock”**; những tên này chỉ giúp minh họa.

Ví dụ: vector user `[0,1; 0,9]`, nghệ sĩ A `[0,2; 0,8]`, B `[0,9; 0,1]`; tích vô hướng là 0,74 và 0,18. Đó là score minh họa, không phải xác suất hay kết quả MusicRec.

Cần phân biệt ba cách dùng tên “SVD”:

| Thuật ngữ | Ý nghĩa |
| --- | --- |
| SVD đại số | $R=U\Sigma V^\top$; cần xác định ma trận đầu vào và cách xử lý missing. |
| MF thường được gọi SVD trong recommender | Học factor/bias bằng tối ưu trên các tương tác quan sát; không nhất thiết chạy phân rã SVD đại số. |
| PureSVD | Baseline phân rã ma trận theo cách dựng dữ liệu cụ thể; khác MF rating có bias và khác implicit ALS. |

SVD có độ lệch dự kiến học bằng SGD trên các cặp quan sát có điểm đại diện 1–5, với loss bình phương và điều chuẩn; không phải phân rã đại số trực tiếp. PureSVD là mô hình nền riêng, khởi đầu theo biểu diễn V1 và kiểm tra thêm nhị phân/log ở bước riêng. Không coi TruncatedSVD là cách thay thế tương đương cho MF có bias. Hồi quy điểm suy từ lượt nghe có giới hạn; không được gọi là mô hình confidence của Hu et al.

Implicit ALS dưới đây giúp đối chiếu lý thuyết. Từ khảo sát ngày 24/10/2026, đây còn là ứng viên mở rộng có điều kiện, chưa thuộc sáu baseline đã chọn và không tự thay SVD trong repo:

$$\min_{A,B}\sum_{u,i}c_{ui}(p_{ui}-\mathbf{a}_u^\top\mathbf{b}_i)^2+\lambda\left(\sum_u\|\mathbf{a}_u\|^2+\sum_i\|\mathbf{b}_i\|^2\right).$$

ALS giữ một phía cố định và giải phía còn lại luân phiên. $f$ là số chiều latent; $\lambda$ hạn chế overfitting; $\alpha$ điều khiển confidence. “ALS” là cách tối ưu; mô hình implicit còn nằm ở cách định nghĩa target, confidence và loss. MF không tự giải quyết cold-start: user/item chưa có dữ liệu không tự có vector hữu ích.

### 3.6. Sparsity, cold-start, bias và đa dạng

$$\text{sparsity}=1-\frac{\text{số cặp tương tác quan sát}}{|U|\,|I|}.$$

Sparsity khác cold-start: ma trận có thể rất thưa trong khi mọi user/item đều có ít nhất một tương tác. User ít lịch sử là tình huống khó, nhưng khác user hoàn toàn mới.

Popularity bias là xu hướng ưu ái item phổ biến. Không phải mọi đề xuất item phổ biến đều sai: nếu user thích mainstream thì chúng có thể phù hợp. Cần đo sự phù hợp cho các nhóm sở thích, không chỉ ép long tail xuất hiện.

Coverage = có nhiều nghệ sĩ khác nhau được đề xuất trên toàn hệ thống. Diversity = các nghệ sĩ trong một danh sách khác nhau tới mức nào theo một similarity được định nghĩa. Novelty = mức ít phổ biến/chưa quen thuộc theo thước đo đã chọn. Serendipity còn cần yếu tố bất ngờ và hữu ích. **Coverage tăng không tự chứng minh diversity, novelty, serendipity hay fairness đều tăng.**

Fallback Popularity giúp trả danh sách cho user rỗng lịch sử, nhưng chưa cá nhân hóa. Onboarding một vài nghệ sĩ có thể giúp dựng hồ sơ Item-CF. Với item hoàn toàn mới, cần thông tin nội dung hoặc chiến lược khám phá; không thể suy ra quan hệ đồng nghe từ dữ liệu chưa tồn tại.

## 4. Bộ dữ liệu dự kiến: các thông tin đã kiểm tra

Nguồn: [GroupLens HetRec 2011](https://grouplens.org/datasets/hetrec-2011/). Bản ZIP được kiểm tra ngày 05/10/2026, README ghi Version 1.0 (May 2011). Kiểm tra này phục vụ chuẩn bị seminar; cấu hình/pipeline nghiên cứu của repo vẫn cần hoàn thiện riêng.

Bổ sung Bước 1–2 ngày 19/10/2026: ZIP trùng hash trước đây, bảy tệp khớp thành viên ZIP và nguồn giữ nguyên sau EDA. Không có trùng cặp hoặc count bất hợp lệ trong bảng tương tác. Có 444 URL ảnh trống, tám chuỗi thẻ không hợp lệ UTF-8; mỗi bản gán thẻ có 1.538 dòng thuộc 390 mã artist không nối danh mục. Hai bản gán thẻ không được cộng đôi. Có 12.133 artist có thẻ và 5.499 chưa có thẻ (31,19%). Đây là độ phủ toàn snapshot, không phải dữ liệu được phép học M2 sau chia tập. Chưa làm sạch hoặc huấn luyện.

| Thuộc tính | Số liệu từ file gốc, trước lọc |
| --- | ---: |
| Người dùng | 1.892 |
| Nghệ sĩ | 17.632 |
| Cặp user–artist | 92.834 |
| Mật độ ma trận | 0,2783% |
| Độ thưa | 99,7217% |
| Số nghệ sĩ/user trung bình | 49,067 |
| User có đúng 50 nghệ sĩ | 1.829/1.892 |
| Số nghệ sĩ/user nhỏ nhất / lớn nhất | 1 / 50 |
| User dưới 3 / dưới 5 nghệ sĩ | 9 / 15 |
| Nghệ sĩ dưới 5 người nghe | 14.804, tương đương 83,96% |
| Count nhỏ nhất / trung vị / lớn nhất | 1 / 260 / 352.698 |
| Count phân vị 99% | Khoảng 7.228 |
| Cặp user–artist trùng | 0 |
| Giá trị thiếu trong ba cột tương tác | 0 |
| Count không dương | 0 |

Số 92.834 là **số cặp quan sát**, không phải tổng lượt nghe. Trang giới thiệu GroupLens làm tròn thành 92.800; số chính xác đã đối chiếu README và file.

### 4.1. Mỗi file dùng làm gì?

| File | Schema/ý nghĩa | Cách dùng dự kiến |
| --- | --- | --- |
| `user_artists.dat` | `userID, artistID, weight`; weight là listening count | Nguồn CF chính. |
| `artists.dat` | `id, name, url, pictureURL` | Ghép tên/hiển thị; không có audio hay album/genre chuẩn sẵn. |
| `tags.dat` | `tagID, tagValue` | Từ vựng tag, có thể nhiễu; không đồng nhất với genre chuẩn. |
| `user_taggedartists.dat` | User–artist–tag và ngày/tháng/năm gắn tag | Phân tích/mở rộng nếu đã nêu phạm vi. |
| `user_taggedartists-timestamps.dat` | User–artist–tag–timestamp | **Thời điểm gắn tag**, không phải thời điểm nghe. |
| `user_friends.dat` | `userID, friendID` | Quan hệ xã hội; ngoài baseline CF nếu chưa có thí nghiệm social. |

Ví dụ thật được README cung cấp: `2\t51\t13883`, nghĩa là user 2 có listening count 13.883 đối với artist 51. Không có cột track, timestamp lượt nghe, rating hay skip.

### 4.2. Vì sao chọn và điều gì chưa làm được?

Phù hợp: dữ liệu công khai, nhỏ để chạy trên máy cá nhân, schema rõ, có count để nghiên cứu implicit CF và metadata cơ bản để demo. README cho phép sử dụng **phi thương mại**, yêu cầu ghi nhận Last.fm; có thông tin trích dẫn HetRec. Không tự gán giấy phép MIT/CC-BY cho bộ dữ liệu.

Giới hạn quan trọng:

- 1.829 user có đúng 50 nghệ sĩ và README mô tả các nghệ sĩ được nghe nhiều nhất: đây là lịch sử tuyển chọn/tổng hợp, không phải log nghe đầy đủ.
- Mức trần 50 làm nhóm “lịch sử ít/nhiều” tự nhiên thiếu biến thiên. Nếu muốn đo sparsity, có thể giữ lần lượt một số lượng nghệ sĩ trong train và cố định test; phải mô tả đây là mô phỏng giảm thông tin.
- Lọc item có dưới 5 user sẽ loại rất nhiều nghệ sĩ đuôi dài; số liệu sau lọc phải báo cáo lại. Không coi ngưỡng 5 trong YAML là lựa chọn đã được chứng minh tốt.
- Timestamp gắn tag không thể dùng thay timestamp nghe. Không tuyên bố thực nghiệm temporal chỉ từ `user_artists.dat`.
- Không có đánh giá âm rõ ràng, mức tiếp xúc hay ngữ cảnh nghe; ground-truth offline chỉ là các tương tác được giữ lại, không phải danh sách tất cả nghệ sĩ user sẽ thích.

SHA-256 ZIP đã kiểm tra:

```text
6738f48195667ff03caaab4d32ca9a3133d8cc026b7c3cdaf6ce1010e913c59c
```

Chi tiết lưu ở [dataset_verified.json](seminar/dataset_verified.json) và [README gốc](seminar/hetrec2011_lastfm_readme.txt).

## 5. Đánh giá: phần thường bị hỏi sâu

### 5.1. Một giao thức đề xuất để đem thảo luận

1. Khóa bộ dữ liệu, schema, phạm vi item và quy tắc hợp lệ; báo cáo thống kê trước/sau lọc.
2. Chia ngẫu nhiên theo user vì không có timestamp nghe: seed 42, ID có thứ tự ổn định; n_val = n_test = max(1, floor(0,1 × n)), còn lại train. Tập chính dự kiến user có ít nhất năm nghệ sĩ; kiểm tra lý do ngưỡng sau EDA. Đây là **random per-user holdout**, không phải leave-one-out hay leave-last-one-out.
3. Tính similarity, factors, popularity và mọi thống kê phục vụ score/rerank từ train. Dùng validation chọn tham số.
4. Với warm-start, xác định candidate catalog là item có trong train; item giữ lại nhưng vắng hoàn toàn khỏi train phải được báo cáo/xử lý thành tình huống cold-start riêng. Công bố số user/test cases bị loại hoặc không thể xếp hạng.
5. Validation lọc train; test lọc train + validation. Thiết kế hiện hành không refit train + validation; hồ sơ chấm điểm và thành phần học vẫn chỉ dùng train.
6. Full ranking trên cùng catalog hợp lệ với mọi model; nếu dùng sampled negatives thì cùng cách lấy mẫu và tập ứng viên, không so trực tiếp score với full ranking.
7. Tính metric trung bình theo user, thêm độ bất định/độ biến thiên và phân tích nhóm phù hợp; test không dùng để lựa chọn cấu hình.

Nếu đặt ngưỡng lọc dựa trên toàn bộ snapshot trước split, phải công bố đó là cách định nghĩa benchmark; khi muốn mô phỏng triển khai không biết test thì ngưỡng/thống kê thích nghi phải dựa trên train. Không âm thầm dùng toàn bộ count để chuẩn hóa, tính popularity hoặc chọn trọng số.

Quy tắc user tối thiểu và số lượng giữ/loại sẽ được kiểm chứng ở bước dữ liệu. Không dùng ngưỡng dưới ba của phương án leave-one-out cũ thay cho thiết kế ít nhất năm nghệ sĩ hiện hành.

### 5.2. Công thức và ví dụ phải tự tính được

Gọi $T_u$ là tập nghệ sĩ phù hợp giữ lại, $L_u$ là K kết quả và $h_u=|T_u\cap L_u|$:

$$P@K=\frac{h_u}{K},\qquad R@K=\frac{h_u}{|T_u|}.$$

Ví dụ $T_u=\{C,D,E\}$ và top-5 là `[C, X, D, Y, Z]`: Precision@5 = 2/5 = 0,4; Recall@5 = 2/3 ≈ 0,667. Đảo C/D xuống cuối list giữ nguyên Precision/Recall nhưng thay đổi chất lượng thứ tự.

Với relevance nhị phân:

$$DCG@K=\sum_{r=1}^{K}\frac{rel_r}{\log_2(r+1)},\qquad NDCG@K=\frac{DCG@K}{IDCG@K}.$$

NDCG thưởng việc đặt item đúng lên đầu. Nếu chỉ có một relevant item ở hạng 3, NDCG@10 = $1/\log_2(4)=0,5$; ở hạng 1 bằng 1. IDCG là DCG của thứ tự lý tưởng theo relevance đã định nghĩa. User không có ground-truth hợp lệ cần quy tắc xử lý rõ.

**Bẫy leave-one-out:** khi $|T_u|=1$, Recall@10 = HitRate@10, còn Precision@10 = HitRate@10/10. Precision@10 tối đa chỉ 0,1. Không so giá trị này với bài có nhiều positives/user hoặc kết luận hệ thống yếu vì chưa tới 1. NDCG vẫn phân biệt vị trí của hit; MAP với một positive cũng giảm thành reciprocal rank nếu item nằm trong cutoff, nên nhiều metric không còn cung cấp nhiều thông tin độc lập.

$$RMSE=\sqrt{\frac{1}{|\Omega_{test}|}\sum_{(u,i)\in\Omega_{test}}(y_{ui}-\hat y_{ui})^2}.$$

RMSE yêu cầu target và thang đo rõ. Thiết kế hiện hành chỉ dùng RMSE khi mô hình dự đoán cùng điểm đại diện 1–5; không áp lên mọi score ranking. Không so RMSE giữa count thô, log-count và điểm đại diện như thể cùng đơn vị. NDCG@10 validation chọn mô hình; RMSE là phân tích phụ và không đo trực tiếp “độ thích”.

$$Coverage@K=\frac{|\bigcup_u L_u|}{|I_{eval}|}.$$

Mẫu số phải là catalog đánh giá đã chốt. Lọc bỏ phần lớn long tail có thể làm coverage tăng do mẫu số nhỏ hơn; không quy hết cho thuật toán.

Score Popularity dự kiến là tổng log2(1 + count) trên train theo V1. ARP và các thành phần đo mức phổ biến dùng số người nghe riêng biệt trên train. Hai đại lượng có vai trò khác nhau; nếu thử Popularity theo listener count phải trình bày đó là một đối chứng riêng trước khi chạy.

Popularity ratio: tỷ lệ vị trí khuyến nghị thuộc nhóm head, ví dụ top 20% item theo listener count **trong train**. Chốt nhóm head trước test. Diversity cần similarity riêng được xác định và tính từ dữ liệu được phép; dùng similarity CF chỉ đo đa dạng trong hành vi, chưa chứng minh đa dạng thể loại/âm thanh.

### 5.3. Một cải tiến nhỏ nhưng kiểm chứng được

Ví dụ rerank:

$$s'(u,i)=\widetilde{s}(u,i)-\beta\,\widetilde{pop}(i),\qquad\beta\ge 0.$$

Tilde biểu thị phép đưa score/popularity về thang đo tương thích, được định nghĩa trước. Tính popularity từ train; chọn $\beta$ trên validation. Không cộng trực tiếp count hàng nghìn với score nhỏ mà không kiểm tra thang đo.

Thí nghiệm cần có base ($\beta=0$), base + penalty và đường trade-off giữa ranking/coverage/popularity. Phạt popularity không tự bảo đảm diversity: có thể đề xuất nhiều nghệ sĩ ít phổ biến nhưng cùng một nhóm. Muốn tăng diversity có thể cân nhắc lựa chọn tuần tự có penalty similarity, nhưng đó là một thành phần khác và phải ablate riêng.

“Tăng Recall từ 0,20 lên 0,22” là tăng 0,02 tuyệt đối, 2 điểm phần trăm và 10% tương đối. Nêu đúng đơn vị; thêm biến thiên giữa seed/user trước khi gọi mức cải thiện là ổn định.

### 5.4. M1 và M2 trong kế hoạch hiện hành

Ví dụ phạt popularity ở trên giúp hiểu một thành phần, chưa phải toàn bộ M1. M1 kiểm tra bốn biến thể: nền, chỉ đa dạng, chỉ phạt phổ biến và đầy đủ. Chọn nền bằng validation; chốt mức giảm NDCG@10 tương đối tối đa 5% trước chạy. Giảm ARP không tự chứng minh tăng đa dạng hoặc công bằng; cần đọc cùng ILD, coverage, Gini và ranking.

M2 kết hợp ItemCF từ hồ sơ, TF–IDF thẻ và Popularity tại N = 0,1,3,5. Tách user học/tinh chỉnh/kiểm tra và không dùng đóng góp tương tác/thẻ của user đánh giá để học thành phần chung. So cùng nhóm đủ năm tương tác hồ sơ, cùng đích, chỉ lọc N nghệ sĩ đã cung cấp. N = 0 là đường Popularity; chưa cá nhân hóa. Đây là protocol riêng cho user chưa có tham số đã học, không chỉ cắt lịch sử rồi vẫn dùng vector user đã được học từ phần bị giấu.

Trước khi chạy mỗi mô-đun phải giải thích thiết kế, phép chuẩn hóa score, xử lý thiếu thẻ/điểm cộng tác và tiêu chí chọn. Công thức chi tiết đối chiếu báo cáo V1 và [kế hoạch hiện hành](WEEKLY_IMPLEMENTATION_PLAN.md); chưa có kết quả để khẳng định M1/M2 cải thiện.

## 6. Các bài báo: đọc để bảo vệ một quyết định nghiên cứu

### 6.1. Những bài cần hiểu sâu

| Công trình | Phải nhớ điều gì? | Liên hệ với MusicRec và giới hạn |
| --- | --- | --- |
| Resnick et al. (1994), *GroupLens: An Open Architecture for Collaborative Filtering of Netnews* | Khuyến nghị từ ý kiến người dùng tương tự; Pearson và hiệu chỉnh mean trong bối cảnh rating. | Cơ sở User-CF. Đối tượng gốc là bài viết Netnews và rating, khác listening count; không phải bài dùng Last.fm. |
| Sarwar et al. (2001), *Item-Based Collaborative Filtering Recommendation Algorithms* | Tính quan hệ item từ hành vi user; so sánh similarity và phương pháp dự đoán; mục tiêu chất lượng/khả năng mở rộng. | Cơ sở Item-CF. Có adjusted cosine cho rating; không suy ra “Item-CF giải quyết hoàn toàn scalability” hay chắc chắn thắng trên dataset này. |
| Koren, Bell, Volinsky (2009), *Matrix Factorization Techniques for Recommender Systems* | Factor user/item, bias, regularization, cách tối ưu và các mở rộng. | Cơ sở MF/SVD. Bối cảnh Netflix/rating; phải giải thích phép chuyển thể sang implicit. |
| Hu, Koren, Volinsky (2008), *Collaborative Filtering for Implicit Feedback Datasets* | Tách preference và confidence; loss có trọng số trên cả cặp quan sát/chưa quan sát; tối ưu ALS. | Bài quan trọng nhất để bảo vệ cách xử lý count. Thực nghiệm bài gốc về xem TV, không phải chứng cứ đã thắng trên HetRec. |
| Herlocker et al. (2004), *Evaluating Collaborative Filtering Recommender Systems* | Đánh giá phụ thuộc tác vụ, dữ liệu, metric và thiết kế thử nghiệm; accuracy chưa bao quát trải nghiệm. | Cơ sở lựa chọn evaluator và báo cáo điều kiện. Là tổng quan phương pháp đánh giá, không phải mô hình mới cần cài. |
| Cremonesi, Koren, Turrin (2010), *Performance of Recommender Algorithms on Top-N Recommendation Tasks* | RMSE tốt không bảo đảm Top-N tốt; Popularity có thể cạnh tranh; head items ảnh hưởng kết quả; PureSVD là baseline cần phân biệt. | Bảo vệ việc dùng ranking metric và Popularity. Thực nghiệm MovieLens/Netflix, khác Last.fm và candidate protocol; không bê nguyên số metric qua. |
| Kowald, Schedl, Lex (2020), *The Unfairness of Popularity Bias in Music Recommendation: A Reproducibility Study* | Phân tích ba nhóm mainstreamness; người thích nhạc ngách có thể nhận chất lượng thấp hơn. | Căn cứ phân tích popularity bias. Dùng subset LFM-1b: 3.000 user, 352.805 artist; **khác HetRec 2K**. Nhóm ít lịch sử không đồng nghĩa nhóm low-mainstream. |
| Ji et al. (2023), *A Critical Study on Data Leakage in Recommender System Offline Evaluation* | Bỏ qua timeline toàn cục có thể đưa thông tin tương lai vào train và đổi thứ tự mô hình, kể cả split theo lịch sử từng user. | Căn cứ minh bạch giới hạn temporal. Dữ liệu MusicRec không có timestamp nghe nên chưa hiện thực được đề xuất timeline của bài; random split không trở thành an toàn temporal chỉ nhờ cố định seed. |

Đọc theo thứ tự: **Hu → Cremonesi → Koren/Sarwar → Kowald → Ji**, sau đó Resnick/Herlocker để hoàn thiện nền tảng. Với mỗi bài, đọc abstract, phần phương pháp liên quan và conclusion, rồi kiểm tra dataset/evaluation trước khi ghi kết quả.

Nguồn công khai để tra:

- [Hu et al., bản PDF từ trang tác giả](https://yifanhu.net/PUB/cf.pdf).
- [Sarwar et al., PDF GroupLens](https://files.grouplens.org/papers/www10_sarwar.pdf).
- [Koren et al., DOI](https://doi.org/10.1109/MC.2009.263).
- [Cremonesi et al., DOI](https://doi.org/10.1145/1864708.1864721).
- [Kowald et al., bản thảo tác giả](https://arxiv.org/abs/1912.04696); bản hội nghị ECIR 2020 có DOI `10.1007/978-3-030-45442-5_5`.
- [Ji et al., bản thảo tác giả](https://arxiv.org/abs/2010.11060); bản ACM TOIS 2023 có DOI `10.1145/3569930`.

### 6.2. Những bài cần biết để định vị đề tài

| Công trình trong repo | Vai trò trong seminar | Mức liên quan |
| --- | --- | --- |
| Song, Dixon, Pearce (2012), *A Survey of Music Recommendation Systems and Future Perspectives* | Bản đồ các hướng music recommendation; nhận diện content/CF/context. | Tổng quan; không dùng bảng dataset của survey như dataset thực nghiệm riêng của tác giả. |
| Schedl et al. (2015), *Music Recommender Systems*, chương 13 Handbook | Đặc điểm âm nhạc, playlist, ngữ cảnh và đánh giá. | Cơ sở phân biệt gợi ý nghệ sĩ với sinh playlist. |
| Schedl et al. (2018), *Current Challenges and Visions in Music Recommender Systems Research* | Những nhu cầu/khó khăn vượt ngoài tương tác đơn giản. | Cơ sở bối cảnh và giới hạn phạm vi. [Bản tác giả](https://arxiv.org/abs/1710.03208). |
| Deldjoo, Schedl, Knees, *Content-driven Music Recommendation: Evolution, State of the Art, and Challenges* | Phân loại nguồn nội dung và thách thức như cold-start, novelty/diversity. | Hướng phát triển hybrid. Có bản arXiv 2021 và cập nhật 2023; ghi đúng phiên bản được dùng. [Nguồn](https://arxiv.org/abs/2107.11803). |
| **Bevec, Tkalčič, Pesek (2024)**, *Hybrid music recommendation with graph neural networks* | PinSage trên đồ thị playlist–song kết hợp nội dung; đánh giá related-song, có beyond-accuracy. | Khác user–artist ranking; không mặc định GNN/hybrid luôn tốt hơn ở long tail. [Bài chính thức](https://link.springer.com/article/10.1007/s11257-024-09410-4). |
| Ziaoddini (2025), *Socially Aware Music Recommendation…* | MM-GNN kết hợp social và nhiều modality. | Bản thảo arXiv cho hướng mở rộng; cần dữ liệu ngoài ba cột CF. Không đánh đồng preprint với bài đã qua peer review. [Nguồn được tài liệu dẫn](https://arxiv.org/abs/2511.05497). |
| **Dinnissen, Bauer (2022)**, *Fairness in Music Recommender Systems: A Stakeholder-Centered Mini Review* | Fairness của user, artist/provider và platform có thể có mục tiêu khác nhau. | Coverage không đủ để tuyên bố fairness toàn diện. [Bài chính thức](https://www.frontiersin.org/journals/big-data/articles/10.3389/fdata.2022.913608/full). |
| Shakespeare et al. (2020), *Exploring Artist Gender Bias in Music Recommendation* | Phân tích đại diện giới của nghệ sĩ trong hệ khuyến nghị. | Minh họa bias khác popularity; muốn đo trong đề tài cần dữ liệu giới đáng tin cậy và protocol riêng. [Bản tác giả](https://arxiv.org/abs/2009.01715). |
| Doh, Choi, Nam (2025), *TALKPLAY: Multimodal Music Recommendation with Large Language Models* | Đề xuất khuyến nghị hội thoại bằng sinh token và tokenizer đa phương thức. | Khác input, dữ liệu và mục tiêu MusicRec; dùng để định vị hướng phát triển. arXiv đã có cập nhật năm 2026, cần ghi phiên bản. [Nguồn](https://arxiv.org/abs/2502.13713). |

Không cần thuộc mọi kiến trúc GNN/LLM để seminar Chương 1–2. Cần biết chúng giải quyết vấn đề gì, đòi thêm dữ liệu nào, đánh giá tác vụ nào và vì sao chưa chọn làm phạm vi chính.

### 6.3. Mẫu ghi chú cho mỗi bài

Điền một trang hoặc một slide theo sáu mục:

1. Tên, tác giả, năm, venue, DOI/version đã kiểm tra.
2. Bài toán: user–item, artist/track/playlist, rating/ranking/conversation?
3. Dữ liệu và input cần có; khác dữ liệu nhóm ở đâu?
4. Ý tưởng và công thức/thành phần cốt lõi.
5. Kết quả dưới protocol nào; metric, K, candidate, split; hạn chế.
6. **Một quyết định của đề tài được bài này hỗ trợ.**

Nếu chưa kiểm tra bảng kết quả, nói luận điểm định tính đã đọc; không tự ghi phần trăm vượt trội. Khác dataset/split/candidate thì không so trực tiếp giá trị metric để xếp hạng công trình.

## 7. Những điểm phải thống nhất trước khi đưa lên slide

| Chỗ trong tài liệu hiện tại | Điều cần thống nhất/sửa trong bài trình bày |
| --- | --- |
| Đề cương dùng lẫn bài hát/nghệ sĩ, track/artist | Với HetRec này, nói **artist recommendation** xuyên suốt. Track/playlist chỉ là tác vụ tham khảo hoặc hướng phát triển. |
| Có RMSE cùng Top-K nhưng chưa khóa mục tiêu chính | Đề xuất ranking là chính, NDCG@10 chọn model; P/R hỗ trợ. Nếu giữ RMSE phải ghi target/thang đo. |
| “SVD” dễ bị hiểu lẫn với PureSVD/ALS/BPR | MF có bias học điểm đại diện 1–5 bằng SGD; PureSVD phân rã ma trận; implicit ALS học preference/confidence; BPR-MF học thứ tự theo cặp. ALS/BPR-MF mới là ứng viên mở rộng đã khảo sát, chưa triển khai hoặc có kết quả. |
| `TONG_QUAN_TAI_LIEU_THAM_KHAO.md` ghi bài GNN 2024 là Lacic et al. | PDF gốc/nhà xuất bản ghi **Matej Bevec, Marko Tkalčič, Matevž Pesek**. |
| Bản tổng hợp ghi mini review fairness là Ferraro et al. | PDF gốc/nhà xuất bản ghi **Karlijn Dinnissen, Christine Bauer**. |
| Bản tổng hợp gán công thức/bảng/mục chi tiết cho đề cương | Kiểm tra lại: đề cương đang có nghiên cứu liên quan ở 2.8, công cụ ở 2.9; một số số mục/công thức trong tổng hợp không khớp file thực tế. |
| Dữ liệu ghi GroupLens/Kaggle/Last.fm tương đương | Chốt đúng HetRec Last.fm 2K Version 1.0; LFM-1b và Last.fm 360K là các dataset khác. |
| Low-history và low-mainstream dùng như cùng nhóm | Hai trục khác nhau: số nghệ sĩ đã nghe và mức yêu thích mainstream. |

### 7.1. Khảo sát mở rộng để chuẩn bị bảo vệ

Đối chiếu ngày 24/10/2026 ở [khảo sát tài liệu](TONG_QUAN_TAI_LIEU_THAM_KHAO.md#khao-sat-mo-rong-20261024): ưu tiên implicit ALS → BPR-MF, dự phòng SLIM, chưa thay sáu baseline chính. Lượt chạy đầu và tinh chỉnh chỉ thực hiện sau baseline khi được phép, trước chốt nền M1/test nếu còn thời gian; không ảnh hưởng M1/M2 hoặc mốc 15/11.

- **Vì sao thêm ALS/BPR khi đã có MF/PureSVD?** Chúng kiểm tra các mục tiêu học khác nhau: confidence trên phản hồi ngầm và xếp hạng theo cặp. Chưa thể nói mô hình nào tốt hơn nếu chưa chạy cùng protocol.
- **SLIM khác ItemCF ở đâu?** ItemCF dùng similarity định trước; SLIM học trọng số item–item với phạt L1/L2, không âm và đường chéo 0. Học sparse không bảo đảm train nhanh; cần đo cả chi phí và hội tụ.
- **Có bỏ mô hình cũ để chỉ giữ kết quả đẹp không?** Khi có căn cứ, có thể rút gọn diễn giải hoặc chuyển chi tiết xuống phụ lục, nhưng giữ bảng kết quả mọi mô hình đã chạy. Chọn trên validation, test chỉ xác nhận sau khóa; nếu đổi nền M1 phải đánh giá lại M1, còn M2 vẫn dùng ItemCF.

### 7.2. Trạng thái repo có thể trình bày trung thực

- Đã có đề cương, tài liệu tham khảo, khung module và cấu hình dự kiến.
- Đã làm sạch riêng ở Bước 3, giữ 1.877 user và 92.801 cặp nghe. CLI preprocess ghi run mới, dừng nếu cặp có count mâu thuẫn, không tự gộp count.
- Đã hoàn thành Bước 4 ngày 24/10/2026: train 74.275, validation/test mỗi tập 9.263 cặp; mapping train có 15.398 artist. Script split mới dùng protocol che giấu ngẫu nhiên theo user, seed 42; đích ngoài catalog giữ nguyên với chỉ số rỗng và được thống kê riêng trong data card. Chưa biến đổi count, học đặc trưng hoặc huấn luyện; dừng giải thích trước Bước 5.
- `SVDRecommender` còn `NotImplementedError`; evaluator script còn trạng thái `not_evaluated`. Không dùng khung bảng trong đề cương như kết quả đã có.

Tài liệu ôn tập này bổ sung kiến thức và đề xuất; không thay đổi cấu hình, mô hình hay đề cương gốc.

## 8. Câu hỏi phản biện và cách trả lời

**1. Đề tài gợi ý gì?**

Nghệ sĩ chưa xuất hiện trong lịch sử quan sát. Dataset chính có user–artist count, không có user–track nên chưa đánh giá gợi ý bài hát.

**2. Tại sao chọn CF?**

Có dữ liệu đồng nghe, phù hợp để tạo baseline từ hành vi và so sánh khả thi trên máy cá nhân. CF không đòi audio/lyrics, nhưng có giới hạn sparsity/cold-start mà nhóm sẽ đo.

**3. Điểm mới ở đâu khi thuật toán đã cũ?**

Đóng góp dự kiến là so sánh tái lập, phân tích điều kiện dữ liệu, kiểm chứng rerank và prototype. Chưa tuyên bố sáng tạo thuật toán hay tốt hơn mọi nghiên cứu trước.

**4. Count 1.000 nghĩa là thích hơn count 100 không?**

Nó là bằng chứng quan tâm thường mạnh hơn, nhưng không có thang đo tuyến tính về yêu thích. Phân biệt preference với confidence; log chỉ nén giá trị.

**5. Vì sao không gán mọi ô trống thành dislike?**

User có thể chưa tiếp xúc với artist. Mô hình implicit có thể dùng target 0 với confidence thấp; không diễn giải như nhãn dislike thật.

**6. User-CF khác Item-CF và content-based thế nào?**

User-CF so các hàng người dùng; Item-CF so các cột nghệ sĩ từ hành vi; content-based dùng thuộc tính nội dung. Item-CF không tự phân tích âm thanh.

**7. SVD của nhóm là SVD nào?**

Thiết kế dự kiến là MF có độ lệch học bằng SGD trên điểm đại diện 1–5 ở các cặp quan sát, với loss bình phương và điều chuẩn. PureSVD là mô hình riêng dùng phân rã ma trận. Không gọi hai mô hình này là implicit ALS; chưa có thực nghiệm hoàn chỉnh để báo kết quả.

**8. Tại sao không chỉ dùng RMSE?**

Mục tiêu là chọn và xếp hạng một số nghệ sĩ; sai số score trên các cặp giữ lại không đo trực tiếp thứ tự này. Cremonesi et al. là căn cứ cho việc đánh giá Top-N riêng.

**9. Ground-truth “thích” ở đâu?**

Là nghệ sĩ có tương tác được giữ lại, được dùng như positive trong benchmark. Nó không phải toàn bộ sở thích thật; đây là giới hạn offline evaluation.

**10. Có timestamp trong dataset, sao không temporal split?**

Timestamp hiện có là thời điểm gắn tag. Bảng listening count không có timestamp lượt nghe nên không đủ cơ sở dựng timeline nghe.

**11. Cố định seed có chống leakage không?**

Seed giúp tái lập split. Chống leakage còn cần tách dữ liệu dùng fit/chuẩn hóa/popularity/tuning và timeline nếu có. Hai việc khác nhau.

**12. Vì sao cần Popularity?**

Đây là mốc tham chiếu đơn giản nhưng có thể mạnh trên dữ liệu nghiêng về mainstream. Mô hình phức tạp chỉ có ích nếu lợi ích được thể hiện bằng chất lượng hoặc trade-off phù hợp.

**13. Popularity dựa trên tổng count hay listener count?**

Baseline dự kiến cộng log2(1 + count) trên train. Listener count train dùng đo ARP và mức phổ biến; nếu dùng nó làm score Popularity thì là một đối chứng khác, cần thiết kế riêng trước chạy.

**14. Lọc item dưới 5 người nghe có hợp lý không?**

Kế hoạch hiện hành không lọc thêm artist theo số người nghe. Việc lọc này có thể loại nhiều đuôi dài và thay đổi chính đối tượng nghiên cứu M1. Nếu cần thay đổi thì phải có bằng chứng EDA, thống kê mất dữ liệu và giải thích trước khi làm, không chỉ vì chỉ số tăng.

**15. Dữ liệu rất thưa nhưng user thường có 50 artist có mâu thuẫn không?**

Không: 50 rất nhỏ so với 17.632. Sparsity xét toàn ma trận, history length xét mỗi user; dữ liệu còn có trần lịch sử được quan sát.

**16. Đánh giá ít lịch sử thế nào khi gần như ai cũng có 50 artist?**

Nhóm tự nhiên có ít biến thiên. Có thể giảm lịch sử train có kiểm soát, giữ test cố định và gọi đúng là mô phỏng thiếu thông tin; hoặc chọn cách phân nhóm khác từ train và công bố số lượng.

**17. Recall@10 và Precision@10 sao khác mười lần?**

Điều đó xảy ra khi mỗi user chỉ có một đích hợp lệ: Precision@10 chia 10, Recall chia 1. Thiết kế 10% hiện hành có thể có nhiều đích/user nên không mặc định tỷ lệ mười lần; phải đọc đúng số đích sau giao catalog.

**18. Rerank giảm popularity có chắc làm chất lượng tốt hơn?**

Không. Nó có thể tăng coverage nhưng giảm NDCG. Chọn tham số trên validation, báo cáo đường trade-off và ablation; không khẳng định trước kết quả.

**19. Độ bao phủ cao có chứng minh công bằng không?**

Không. Fairness phải xác định bên liên quan/nhóm và tiêu chí. Coverage chỉ cho biết catalog được đề xuất rộng tới đâu.

**20. Fallback có giải quyết cold-start chưa?**

Popularity xử lý việc trả kết quả cho user mới nhưng chưa cá nhân hóa. Onboarding giúp có tín hiệu; item hoàn toàn mới cần nội dung hoặc khám phá, phải đánh giá riêng.

**21. Leave-one-out có kiểm chứng cold-start không?**

Thông thường đó là warm-start: user vẫn có lịch sử train, item có thể được user khác nghe. Muốn đo cold-start phải giữ user/item ra khỏi train có chủ đích và xác định candidate/metric riêng.

**22. Bài Kowald cũng dùng Last.fm, có so metric trực tiếp được không?**

Không chỉ dựa vào tên nền tảng. Bài dùng subset LFM-1b với quy mô khác, preprocessing và evaluation khác; đối chiếu cơ chế bias, chưa lấy số metric làm chuẩn ngang nhau.

**23. Tại sao không dùng GNN hoặc LLM?**

Đề tài ưu tiên kiểm chứng CF trên dữ liệu và nguồn lực hiện có. Các hướng đó đòi input khác như graph, audio, lyrics, hội thoại và protocol riêng. Có thể khảo sát để định vị/hướng phát triển; chưa có căn cứ để gọi chúng cần thiết cho mục tiêu hiện tại.

**24. Mô hình nào tốt nhất?**

Chưa có kết quả. Nhóm sẽ chọn theo metric và trade-off đã chốt trên cùng protocol. Không gọi SVD là tốt nhất chỉ vì thường được dùng làm baseline mạnh.

**25. Hiện nhóm làm xong gì?**

Có đề cương, khảo sát và khung phần mềm; dữ liệu gốc đã được kiểm tra cho tài liệu seminar. Mô hình/evaluator hoàn chỉnh và bảng kết quả chưa có bằng chứng trong nhánh hiện tại.

**26. Vì sao khuyến nghị nghệ sĩ thay vì bài hát?**

Mục tiêu là khám phá nghệ sĩ phù hợp từ lịch sử nghe. Dữ liệu quan sát trực tiếp ở cấp nghệ sĩ, đủ để kiểm chứng CF, M1 và M2 trong phạm vi đó. Gợi ý đúng nghệ sĩ không chứng minh chọn đúng bài hát hoặc người dùng thích mọi tác phẩm; bài toán bài hát cần dữ liệu và đánh giá riêng.

**27. Không làm đúng mọi mô hình/tham số trong hướng dẫn của cô có hợp lý không?**

Nhóm giữ trình tự nghiên cứu và nguyên tắc kiểm chứng. PureSVD, so sánh biểu diễn và các ablation được bổ sung để trả lời câu hỏi cụ thể; ngân sách nhỏ phù hợp việc kiểm tra từng bước. Mọi khác biệt phải giải thích, có đối chứng và số liệu thật, không gọi là yêu cầu hoặc phê duyệt của cô khi chưa có xác nhận.

## 9. Dàn ý trình bày 15–20 phút

Đây là dàn ý nội dung, chưa phải file PowerPoint. Điều chỉnh theo thời lượng seminar thực tế.

| Slide | Nội dung cần thấy | Thời lượng gợi ý |
| --- | --- | ---: |
| 1 | Tên đề tài, một câu xác định Top-K artist recommendation | 30 giây |
| 2 | Bối cảnh và 3 khó khăn: implicit, sparsity, popularity | 1 phút |
| 3 | Mục tiêu, phạm vi và đóng góp dự kiến | 1 phút |
| 4 | RQ → thí nghiệm/metric sẽ trả lời | 1 phút |
| 5 | Dataset, nguồn, schema và số liệu gốc đã kiểm tra | 2 phút |
| 6 | Count ≠ rating; timestamp tag ≠ timestamp nghe; ảnh chụp top artist | 1,5 phút |
| 7 | Ví dụ cùng một ma trận để phân biệt User-CF/Item-CF | 2 phút |
| 8 | MF và quyết định cần chốt về SVD/implicit | 2 phút |
| 9 | 5–6 bài cốt lõi và mỗi bài hỗ trợ quyết định nào | 2 phút |
| 10 | Split, candidate, loại seen items, chống leakage | 1,5 phút |
| 11 | Ví dụ P/R/NDCG; ranking và beyond-accuracy | 1,5 phút |
| 12 | Cải tiến dự kiến, trade-off, hiện trạng và việc tiếp theo | 1 phút |

Đưa các survey/GNN/LLM, công thức dài, chi tiết README/license và danh sách phản biện vào phần phụ lục. Khi nói về nghiên cứu liên quan, dùng mạch “vấn đề → bài hỗ trợ → quyết định của nhóm”, tránh chỉ đọc danh sách tác giả.

Một đoạn mở đầu có thể tập nói:

> “Trong đề tài này, chúng em giới hạn đơn vị khuyến nghị là nghệ sĩ. Dữ liệu Last.fm cho biết số lượt nghe tổng hợp của từng cặp người dùng–nghệ sĩ, nên vấn đề đầu tiên là xử lý phản hồi ngầm, không phải dự đoán sao đánh giá. Chúng em muốn kiểm chứng các mô hình CF trên cùng giao thức và xem một bước rerank giảm độ phổ biến tạo đánh đổi thế nào giữa chất lượng Top-K và khả năng khám phá.”

## 10. Cách ôn và tự kiểm tra

Nếu có **ba giờ**:

- 30 phút: phần 1–2; tập phát biểu đề tài 60 giây và trả lời đóng góp/phạm vi.
- 45 phút: phần 3–4; tự vẽ ma trận, tính similarity minh họa, phân biệt implicit/MF/ALS, nhớ schema và giới hạn dữ liệu.
- 45 phút: Hu, Cremonesi, Koren/Sarwar; viết một câu “bài này hỗ trợ quyết định gì” cho mỗi bài. Dùng phần 6 làm chỉ dẫn, tra PDF gốc khi có công thức/kết quả.
- 30 phút: split/candidate và ví dụ P/R/NDCG; luyện các bẫy ở phần 5.
- 30 phút: nói thử theo dàn ý, trả lời 10 câu phản biện mà không nhìn tài liệu.

Nếu chỉ có **một giờ**, ưu tiên phần 1, bảng dataset, mục SVD/implicit, ví dụ metric và các câu 1, 4, 7–10, 14, 17, 24–25.

Trước seminar, tự kiểm:

- [ ] Giải thích đề tài trong 60 giây, không dùng lẫn track và artist.
- [ ] Nói đúng 1.892 user, 17.632 artist, 92.834 cặp và ý nghĩa mỗi số.
- [ ] Giải thích được một ô trống và vì sao count không phải rating.
- [ ] Tự mô tả User-CF, Item-CF, MF; phân biệt SVD đại số/MF/implicit ALS.
- [ ] Tính đúng Precision, Recall, NDCG của ví dụ; biết bẫy một positive/user.
- [ ] Nêu split/candidate/masking và giới hạn thiếu timeline.
- [ ] Kết nối ít nhất 5 bài với 5 quyết định nghiên cứu.
- [ ] Nhận diện đúng tác giả bài GNN 2024 và fairness 2022.
- [ ] Có một cải tiến cụ thể, baseline, ablation và trade-off cần kiểm chứng.
- [ ] Phân biệt điều đã kiểm tra, điều dự kiến và điều chưa có kết quả.

Khi chưa biết câu trả lời, cách trả lời có ích là: **“Hiện nhóm chưa có thực nghiệm để kết luận điểm này; nhóm dự kiến kiểm chứng bằng … trên … và sẽ báo cáo …”**, điền một phép đo cụ thể thay vì đoán kết quả.
