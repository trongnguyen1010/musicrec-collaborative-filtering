# Khảo sát nghiên cứu 2021–2025 và đề xuất hướng phát triển mới cho MusicRec

Ngày lập: 26/10/2026. Đây là tài liệu **nghiên cứu**. Chưa viết code, chưa chạy thực nghiệm mới và chưa sửa báo cáo Word. Mọi hướng ở mục 6 là **giả thuyết cần kiểm chứng**, chưa có số đo nào trên HetRec của nhóm.

## Tóm tắt

- Đã đọc lại 10 bài 2021–2025 trong [nghien-cuu-2021-2025](../nghien-cuu-2021-2025/README.md), các bài nền mới trong [bai-bao-nen](../bai-bao-nen/) và các mục đối chiếu gần nhất trong [TONG_QUAN.md](../TONG_QUAN.md). Sau đó tìm thêm khoảng 35 bài 2021–2025 về lọc cộng tác phản hồi ngầm, thiên lệch phổ biến, người dùng mới, đồ thị/contrastive và LLM. Mọi bài bổ sung đều đã mở trang arXiv, ACM hoặc trang nhà xuất bản để kiểm tra tên, tác giả và nơi đăng (mục 9).
- Khoảng trống lớn nhất của các bài hiện có, xét theo đúng bài toán của nhóm, là: (1) các bài tag-aware/đồ thị trên HetRec dùng **tương tác gán thẻ** chứ không phải lịch sử nghe, chia ngẫu nhiên, và không báo độ phủ hay độ phổ biến; (2) các bài về thiên lệch phổ biến trong âm nhạc **chỉ đo**, ít bài vừa giảm thiên lệch vừa giữ độ chính xác; (3) các cách giảm thiên lệch dùng **một mức phạt chung cho mọi người dùng**, trong khi người nghe ít phổ biến (LowPop) là nhóm bị gợi ý kém nhất; (4) **đồ thị bạn bè `user_friends.dat` chưa được dùng** trong nhánh lịch sử nghe, kể cả cho người dùng mới.
- Đề xuất chính (H1): **giảm thiên lệch phổ biến theo phổ, có mức điều chỉnh riêng cho từng người dùng**, đặt trên nền mạnh nhất (ALS, hoặc EASE nếu H2 thắng). Căn cứ là hai kết quả lý thuyết 2023–2025: độ phổ biến nằm chủ yếu ở thành phần suy biến đầu tiên của ma trận điểm. Hướng này sửa đúng điểm yếu của M1 hiện tại (phạt chung, chỉ tái xếp hạng sau).
- Hai hướng hỗ trợ: H2 thêm **nền tuyến tính mạnh** (EASE, RDLAE, chuẩn hóa DAN của SIGIR 2025), rẻ trên CPU; H3 làm lại **M2 có dùng bạn bè**, để người dùng N = 0 nhận gợi ý cá nhân thay vì Popularity.
- Không khuyến nghị đưa LLM, đồ thị tri thức hay đa phương thức vào khóa luận lần này, vì HetRec không có âm thanh hay văn bản mô tả, máy chỉ có GPU 4 GB, và đã có bài cho thấy LLM cũng thiên lệch phổ biến (mục 4.5).
- Một lưu ý về phương pháp: **tập test đã mở**. Mọi mô hình mới phải ghi rõ là thực nghiệm bổ sung, chọn trên validation, khóa cấu hình trước khi chấm test.
- Một lỗi trích dẫn tìm thấy trong tài liệu sẵn có: [TONG_QUAN.md](../TONG_QUAN.md#5-lacic-et-al-2024) ghi bài "Hybrid music recommendation with graph neural networks" là của **Lacic et al. (2024)**, nhưng trang đầu PDF trong `bai-bao-nen/` ghi tác giả là **Matej Bevec, Marko Tkalčič, Matevž Pesek**, UMUAI 34:1891–1928, DOI 10.1007/s11257-024-09410-4. Cần sửa ở báo cáo nếu đã trích như vậy.

## 1. Phạm vi và cách làm

1. Đọc trước tài liệu sẵn có của nhóm, theo yêu cầu: 10 PDF trong `nghien-cuu-2021-2025/10_bai_bao_goc/`, các PDF 2021–2025 trong `bai-bao-nen/` (Ji 2023, Bevec 2024, Ziaoddini 2025, Dinnissen & Bauer 2022, Doh 2025 TalkPlay), cùng các mục đối chiếu M1, M2, ALS trong `TONG_QUAN.md`. Văn bản được trích bằng `pdftotext` và đọc phần tóm tắt, thiết lập, bảng kết quả, kết luận và hạn chế.
2. Tìm thêm bằng công cụ tìm kiếm web cho những nhóm còn thiếu. Với mỗi bài, mở trang arXiv hoặc trang nhà xuất bản để xác nhận. Với các bài bổ sung, nội dung tóm tắt dưới đây lấy **từ phần tóm tắt (abstract)**, chưa đọc toàn văn. Những con số trích từ bài bổ sung là con số tác giả công bố trong abstract, trên dữ liệu của họ, **không so trực tiếp được** với số của nhóm.
3. Đối chiếu với kết quả thật của nhóm ở `docs/results/chuong_4_test.md` và `chuong_4_m2.md` (bản chính thức chạy ngày 26/10/2026, commit `e1350ce`). Hai tệp này nằm ở nhánh Chương 4 trên máy local, chưa có trên nhánh research của GitHub; liên kết `../results/...` trong tài liệu này sẽ mở được sau khi gộp nhánh đó.

## 2. Điểm xuất phát: kết quả hiện tại của nhóm

Nguồn: [chuong_4_test.md](../../results/chuong_4_test.md) mục 3–5, bảng test K = 10, seed 42.

| Mô hình | NDCG@10 | Coverage | ARP | Ghi chú |
| --- | --- | --- | --- | --- |
| ALS (mở rộng) | 0,2175 | 0,0514 | 131,97 | Hơn PureSVD có ý nghĩa (p Holm 3,36e−25) |
| PureSVD nhị phân k = 16 | 0,1828 | 0,0186 | 174,21 | Tốt nhất trong sáu mô hình chính |
| M1 (λ = 0,75, β = 0,5) | 0,1814 | 0,0294 | 146,87 | NDCG không khác PureSVD có ý nghĩa (p Holm 0,608); ARP −15,69% |
| Popularity | 0,0688 | 0,0019 | 348,35 | |
| SVD có độ lệch | 0,0627 | 0,0038 | 319,77 | Thấp hơn Popularity |
| UserCF | 0,0189 | 0,1220 | 47,93 | Thấp hơn Popularity |
| ItemCF | 0,0175 | 0,2457 | 50,77 | Thấp hơn Popularity |

M2 (người dùng mới, [chuong_4_m2.md](../../results/chuong_4_m2.md)): trên 189 người để dành, M2 thua Popularity ở N = 1, 3, 5 về NDCG@10 (N = 3: −0,0087, p Holm 0,857), nhưng tăng coverage@10 từ 0,0009 lên 0,0555 và giảm ARP từ 294,9 xuống 129,1.

Ba điều rút ra cho việc chọn hướng mới:

- Nền tốt nhất hiện có (ALS) đã có ARP thấp hơn và coverage cao hơn M1. Vì vậy một phương pháp giảm thiên lệch mới **phải đặt trên ALS** (hoặc nền tốt hơn) mới có ý nghĩa, không thể chỉ so với PureSVD.
- M1 chỉ tái xếp hạng top-100 với một cặp (λ, β) chung. Độ phủ tăng ít (1,86% lên 2,94%).
- Người dùng N = 0 hiện chỉ nhận Popularity. Trong khi đó data card ghi `user_friends.dat` có 25.434 dòng, mọi đầu quan hệ đều thuộc tập người dùng, và **"Bảng bạn bè chưa dùng trong baseline"** ([data-card.md](../../data-card.md), dòng về `user_friends.dat`).

## 3. Đọc lại các bài đã có trong docs

### 3.1 Mười bài 2021–2025 (thư mục `nghien-cuu-2021-2025`)

| # | Bài | Phương pháp | Dữ liệu và cách đánh giá | Điểm mạnh | Hạn chế đối với bài toán của nhóm |
| --- | --- | --- | --- | --- | --- |
| 01 | Lesota và cs., RecSys 2021 | Đo thiên lệch phổ biến của 7 thuật toán (Random, Pop, ItemKNN, SLIM, ALS, BPR, VAE) theo giới tính | LFM-2b, bài hát, nhị phân | Dùng cả phân phối (KL, Kendall τ), không chỉ trung bình | Chỉ đo, không đề xuất cách giảm. Kết luận tự ghi hướng tương lai là "đưa thiên lệch vào hàm mất mát" và "chia người dùng theo mức mainstream" |
| 02 | Zhang và cs., LFGCF, arXiv 2022 | GCN nhẹ trên đồ thị folksonomy người dùng–thẻ–nghệ sĩ, điều chuẩn TransRT | HetRec Last.fm, nhưng **tương tác là các lần gán thẻ**, chia 60/20/20 | Đơn giản hóa GCN cho thẻ | Bản thảo chưa phản biện. Không dùng số lượt nghe, không báo độ phủ hay độ phổ biến |
| 03 | Zuo và cs., TRAL, Applied Sciences 2023 | Attention pooling trên vector thẻ, mô hình rộng và sâu | HetRec Last.fm, gán thẻ, HR và NDCG | Gom thẻ nhiều khía cạnh | Tác giả tự ghi hai hạn chế: thẻ thưa, và **không xử lý được người dùng mới** |
| 04 | Bertram và cs., EARS, ESWA 2023 | Nhúng đồ thị tri thức từ MusicBrainz + Last.fm | Bản Last.fm khác HetRec | Nhấn mạnh đa dạng và giải thích được | Cần dữ liệu ngoài (MusicBrainz), khó tái lập trên HetRec |
| 05 | Wang và cs., KCNR, Applied Sciences 2023 | Mạng attention trên đồ thị tri thức | HetRec bổ sung tri thức (KB4Rec) | Kết hợp láng giềng đa bước | Cần ánh xạ tri thức ngoài; đánh giá CTR/top-K trên mẫu âm |
| 06 | Sánchez-Moreno và cs., Information 2024 | Độ tương tự người dùng kết hợp lượt nghe và **cấu trúc mạng bạn bè** cho user k-NN | **Đúng HetRec Last.fm**, nhóm gray-sheep và cold-start | Bài duy nhất trong 10 bài dùng `user_friends`; cải thiện có ý nghĩa ở mọi kịch bản tác giả xét | Chỉ k-NN và MF đơn giản. NDCG khoảng 0,77–0,83 trong Bảng 1 là trên danh sách các mục đã có điểm, **không phải full ranking**, nên không so được với số của nhóm |
| 07 | Lin và cs., BoxGNN, KDD 2024 | Nhúng hộp (box) + GNN trên đồ thị người dùng–thẻ–mục | HetRec Last.fm, gán thẻ, 80/10/10, full ranking | Mô hình hóa sự đa dạng sở thích | Vẫn là tương tác gán thẻ; huấn luyện GPU; không báo thiên lệch phổ biến |
| 08 | Di Francesco và cs., GATSY, IJCNN 2025 | Graph attention cho độ tương tự nghệ sĩ | Olga (nghệ sĩ), không có người dùng | Bền vững khi thiếu đặc trưng | Là bài toán tương tự nghệ sĩ, không cá nhân hóa. Tác giả ghi hướng tương lai là đánh giá đuôi dài |
| 09 | Martal & Najib, Zeta 2025 | SVD và điền khuyết MICE | Last.fm, mẫu 500 người | Dễ hiểu | "Accuracy 96%" là độ nhất quán danh sách, không phải độ chính xác trên tập giữ lại (đã ghi ở TONG_QUAN) |
| 10 | Du và cs., SAPIENT, NAACL 2025 | Gợi ý hội thoại, MCTS | Last.fm chuyển sang hội thoại mô phỏng | Lập kế hoạch nhiều lượt | Khác hẳn bài toán; cần người dùng mô phỏng |

### 3.2 Bài 2021–2025 trong `bai-bao-nen`

| Bài | Nội dung chính | Liên quan |
| --- | --- | --- |
| Ji và cs., TOIS 2023, "A Critical Study on Data Leakage in Recommender System Offline Evaluation" | Chia tập không theo dòng thời gian toàn cục gây rò rỉ, làm đổi thứ hạng mô hình | HetRec không có thời điểm nghe nên không áp dụng trực tiếp được, nhưng là lý do phải giữ nguyên protocol khi so mô hình mới |
| Bevec, Tkalčič, Pesek, UMUAI 2024, "Hybrid music recommendation with graph neural networks" (TONG_QUAN đang ghi nhầm là Lacic et al.) | PinSage kết hợp đồ thị playlist và đặc trưng âm thanh; tác giả kết luận mô hình "cân bằng nhất" khi xét cả ngoài độ chính xác | Ủng hộ cách đánh giá nhiều tiêu chí. Không dùng được vì HetRec không có âm thanh |
| Ziaoddini, 2025, "Socially Aware Music Recommendation: A Multi-Modal GNN…" | GNN đa phương thức có đồ thị xã hội | Bản PDF là bản thảo một tác giả, mức bằng chứng thấp; chỉ nên trích làm ví dụ về hướng xã hội |
| Dinnissen & Bauer, Frontiers in Big Data 2022 | Tổng quan công bằng theo các bên liên quan (người nghe, nghệ sĩ) | Căn cứ cho việc báo độ phủ và độ phơi bày nghệ sĩ |
| Doh, Choi, Nam, TalkPlay (arXiv 2502.13713) | LLM đa phương thức sinh token gợi ý nhạc | Cần âm thanh, lời, ảnh; không khả thi trên HetRec |

### 3.3 Nhận xét chung về nhóm bài trong docs

- Bốn bài dùng HetRec có kết quả mạnh (LFGCF, TRAL, BoxGNN, Sánchez-Moreno) đều **khác protocol của nhóm**: dùng gán thẻ, hoặc xếp hạng trên mục đã có điểm. Không thể lấy số của họ làm mốc so sánh.
- Không bài nào trong 10 bài vừa (a) dùng lịch sử nghe của HetRec, (b) đánh giá full ranking, (c) báo cả độ chính xác lẫn độ phủ/độ phổ biến, và (d) có kiểm định thống kê. Thực nghiệm Chương 4 của nhóm đã làm đủ cả bốn, đây là điểm mạnh nên giữ.

## 4. Bài bổ sung 2021–2025 theo nhóm chủ đề

### 4.1 Mô hình phản hồi ngầm mạnh và so sánh công bằng

| Bài | Ý chính (theo abstract hoặc toàn văn đã kiểm) | Ý nghĩa cho nhóm |
| --- | --- | --- |
| Rendle, Krichene, Zhang, Koren, "Revisiting the Performance of iALS on Item Recommendation Benchmarks", RecSys 2022 | iALS được tinh chỉnh kỹ vẫn cạnh tranh với các phương pháp mới hơn trên các bộ chuẩn | Giải thích vì sao ALS thắng trong kết quả của nhóm; ALS là nền đúng để đặt cải tiến lên |
| Anelli và cs., "Top-N Recommendation Algorithms: A Quest for the State-of-the-Art", UMAP 2022 | So sánh nhiều baseline, gồm mô hình tuyến tính và iALS, cả độ chính xác lẫn ngoài độ chính xác | Đã có trong TONG_QUAN; ủng hộ việc thêm EASE/RP3β làm nền |
| Shehzad & Jannach, "Everyone's a Winner! On Hyperparameter Tuning of Recommendation Models", RecSys 2023 | Phần lớn bài mới mô tả kém việc tinh chỉnh baseline; baseline yếu nhất khi được tinh chỉnh vẫn thắng mô hình tốt nhất khi không tinh chỉnh | Lý do bắt buộc tinh chỉnh baseline cùng ngân sách nếu thêm mô hình mới |
| Milogradskii và cs., "Revisiting BPR: A Replicability Study…", RecSys 2024 | Nhiều cài đặt BPR khác nhau ở chi tiết, ảnh hưởng mạnh tới kết quả | Nếu thêm BPR phải ghi rõ cài đặt |
| Steck, EASE, WWW 2019 (nền, trước 2021) | Tự mã hóa tuyến tính có nghiệm đóng, ràng buộc đường chéo bằng 0 | Nền cho RDLAE và DAN bên dưới |
| Moon, Kim, Lee, "It's Enough: Relaxing Diagonal Constraints in Linear Autoencoders", SIGIR 2023 | Phân tích phổ: điều chuẩn L2 khuếch đại các thành phần chính đầu, có lợi cho mục phổ biến; ràng buộc đường chéo bằng 0 kìm các thành phần sau, hại mục ít phổ biến. Đề xuất RLAE/RDLAE, cải thiện mục đuôi dài | Liên hệ trực tiếp với PureSVD của nhóm và với thiên lệch phổ biến |
| Park, Yoon, Kim, Lee, "Why is Normalization Necessary for Linear Recommenders?", SIGIR 2025 | Chuẩn hóa thích ứng theo dữ liệu (DAN) cho các mô hình tự mã hóa tuyến tính, xử lý cả thiên lệch phổ biến và thiên lệch láng giềng. Abstract báo cải thiện đến 128,57% cho mục đuôi dài trên dữ liệu của tác giả | Ứng viên rẻ nhất có cơ sở để vừa tăng độ chính xác vừa giảm thiên lệch |

### 4.2 Đồ thị và học tương phản

| Bài | Ý chính | Ý nghĩa cho nhóm |
| --- | --- | --- |
| He và cs., LightGCN, SIGIR 2020 (nền) | GCN bỏ biến đổi phi tuyến | Mốc chuẩn cho các bài đồ thị |
| Shen và cs., "How Powerful is Graph Convolution for Recommendation?" (GF-CF), CIKM 2021 | Phân tích GCN như bộ lọc tín hiệu đồ thị; đề xuất bộ lọc không cần huấn luyện | Bộ lọc thông thấp lý tưởng của GF-CF có dạng gần PureSVD, nên là bước nối tự nhiên từ PureSVD |
| Choi và cs., BSPM, SIGIR 2023 | Mô hình làm mờ–làm sắc (ODE) trên đồ thị, không cần học tham số | Nền đồ thị rẻ trên CPU |
| Park và cs., Turbo-CF, SIGIR 2024 | Lọc đồ thị không cần phân rã ma trận, chạy rất nhanh | Như trên, rẻ hơn nữa |
| Yu và cs., SimGCL, SIGIR 2022; XSimGCL, TKDE 2023 | Học tương phản trên đồ thị chỉ cần nhiễu nhúng, không cần tăng cường đồ thị; tác giả liên hệ với độ đồng đều biểu diễn và giảm thiên lệch phổ biến | Ứng viên "mô hình học sâu 2022–2023" nếu cần một baseline hiện đại |
| Cai và cs., LightGCL, ICLR 2023 | Tăng cường bằng SVD cho học tương phản | Liên hệ với nhánh SVD của nhóm |
| Wang và cs., DirectAU, KDD 2022 | Tối ưu trực tiếp độ khớp và độ đồng đều của biểu diễn | Hàm mất mát đơn giản thay BPR |

### 4.3 Thiên lệch phổ biến

| Bài | Ý chính | Ý nghĩa cho nhóm |
| --- | --- | --- |
| Kowald, Schedl, Lex, ECIR 2020 (có trong docs) | Người nghe ít mainstream (LowMS) nhận gợi ý kém chính xác nhất trên Last.fm | Căn cứ chia nhóm người dùng theo mức mainstream |
| Kowald và cs., "Support the underground", EPJ Data Science 2021 | Đặc điểm người nghe ngoài dòng chính; gợi ý kém chính xác cho họ | Như trên |
| Kowald, "Investigating Popularity Bias Amplification… in the Entertainment Domain", EWAF 2025 | Trên Last.fm, MovieLens, MyAnimeList: nhóm LowPop nhận gợi ý kém chính xác nhất và lệch chuẩn (miscalibrated) nhất, có ý nghĩa thống kê. Riêng Last.fm, chỉ số popularity lift cho kết quả khó hiểu vì nhạc được nghe lặp lại | Bằng chứng mới nhất, đúng miền nhạc, rằng cần xử lý **theo nhóm người dùng**, không chỉ trung bình |
| Abdollahpouri và cs., "User-centered Evaluation of Popularity Bias", UMAP 2021 | Đề xuất chỉ số đánh giá thiên lệch theo mức chịu phổ biến của từng người dùng và một cách giảm thiên lệch theo hướng người dùng | Căn cứ cho mục tiêu "cá nhân hóa mức giảm" của H1 |
| Wei và cs., MACR, KDD 2021 | Suy luận phản thực tế, tách ảnh hưởng độ phổ biến ra khỏi điểm | Một họ phương pháp nhân quả; cần huấn luyện lại mô hình nhiều nhánh |
| Zhang và cs., PDA, SIGIR 2021 | Can thiệp nhân quả, tận dụng xu hướng phổ biến | Cần thông tin thời gian, HetRec không có |
| Zhang và cs., InvCF, WWW 2023 | Học biểu diễn bất biến với dịch chuyển phân phối phổ biến | Cần huấn luyện mô hình sâu |
| Cai và cs., PAAC, KDD 2024 | Căn chỉnh và tương phản có nhận biết độ phổ biến | Như trên |
| Lin và cs., "How Do Recommendation Models Amplify Popularity Bias? An Analysis from the Spectral Perspective", ACM (DOI 10.1145/3701551.3703579), arXiv 2404.12008 | Độ phổ biến được mã hóa ở **phổ chính** (thành phần suy biến đầu) của ma trận điểm dự đoán; hiện tượng sụp chiều làm thành phần này trội hơn, tăng thiên lệch. Đề xuất điều chuẩn chuẩn phổ để phạt giá trị suy biến lớn nhất | **Căn cứ lý thuyết chính cho H1**: với PureSVD/ALS có thể giảm trực tiếp thành phần này mà không cần huấn luyện lại |
| Klimashevskaia, Jannach, Elahi, Trattner, UMUAI 2024, "A survey on popularity bias in recommender systems" | Tổng quan định nghĩa, cách đo, cách giảm | Dùng làm khung phân loại trong Chương 2 |
| Ungruh và cs., RecSys 2024 (đã có trong TONG_QUAN) | Nghiên cứu người dùng: giảm thiên lệch trong gợi ý nhạc không tự động làm người dùng hài lòng hơn | Giới hạn diễn giải: chỉ số ngoài độ chính xác không chứng minh trải nghiệm |

### 4.4 Người dùng mới và mạng xã hội

| Bài | Ý chính | Ý nghĩa cho nhóm |
| --- | --- | --- |
| Sánchez-Moreno và cs., 2024 (bài 06) | Mạng bạn bè giúp gray-sheep và cold-start trên chính HetRec | Căn cứ trực tiếp cho H3 |
| Yu và cs., MHCN, WWW 2021 | Siêu đồ thị đa kênh cho gợi ý xã hội, tự giám sát | Mô hình xã hội mạnh nhưng cần GPU; dùng để trích dẫn |
| Yu và cs., SEPT, KDD 2021 | Huấn luyện ba nhánh có nhận biết quan hệ xã hội | Như trên |
| Wei và cs., CLCRec, ACM MM 2021 | Học tương phản cho mục mới dựa trên nội dung | Bài toán mục mới, khác người dùng mới của M2 |
| Huang và cs., ColdLLM, WSDM 2025 | Dùng LLM mô phỏng tương tác cho mục mới | Cần LLM; ngoài phạm vi |

### 4.5 LLM cho gợi ý

| Bài | Ý chính | Ý nghĩa cho nhóm |
| --- | --- | --- |
| Hou và cs., "Large Language Models are Zero-Shot Rankers for Recommender Systems", ECIR 2024 | LLM xếp hạng lại ứng viên mà không huấn luyện; tác giả ghi nhận LLM bị ảnh hưởng bởi thứ tự và độ phổ biến | Không có văn bản mô tả nghệ sĩ trong HetRec ngoài tên và thẻ |
| Lichtenberg, Buchholz, Schwöbel, "Large Language Models as Recommender Systems: A Study of Popularity Bias", 2024 | Nghiên cứu thiên lệch phổ biến của LLM khi làm gợi ý | Phản bác giả định LLM sẽ tự giảm thiên lệch |
| Doh và cs., TalkPlay 2025; Du và cs., SAPIENT 2025 (có trong docs) | Gợi ý nhạc đa phương thức hoặc hội thoại bằng LLM | Không khả thi với dữ liệu và phần cứng hiện có |
| Carraro & Bridge, 2024 (đã có trong TONG_QUAN) | Tái xếp hạng đa dạng bằng LLM tốn kém hơn, đánh đổi không tốt hơn phương pháp tham lam truyền thống | Ủng hộ giữ tái xếp hạng nhẹ |

## 5. Khoảng trống của các nghiên cứu hiện tại

| Mã | Khoảng trống | Bằng chứng |
| --- | --- | --- |
| G1 | Các mô hình đồ thị/thẻ trên HetRec không được đánh giá trên **lịch sử nghe**, không báo độ phủ hay độ phổ biến, và thường so với baseline không tinh chỉnh | Bài 02, 03, 07 (mục 3.1); Shehzad & Jannach 2023 |
| G2 | Nghiên cứu âm nhạc chủ yếu **đo** thiên lệch, ít bài giảm thiên lệch mà vẫn giữ độ chính xác | Lesota 2021 (kết luận), Kowald 2020, 2021, 2025 |
| G3 | Cách giảm thiên lệch hiện có dùng **một mức chung** cho mọi người, trong khi nhóm LowPop vừa bị gợi ý kém chính xác nhất vừa lệch chuẩn nhất | Kowald 2025; Abdollahpouri 2021; M1 của nhóm dùng (λ, β) chung |
| G4 | Phương pháp giảm thiên lệch mạnh (MACR, PAAC, InvCF, điều chuẩn phổ) đều cần **huấn luyện lại** mô hình sâu; chưa thấy trong các bài đã đọc một cách không cần huấn luyện áp dụng trực tiếp lên PureSVD/ALS, dù lý thuyết phổ chỉ ra đúng chỗ cần sửa | Lin và cs. (phổ), Moon 2023, Park 2025 |
| G5 | Đồ thị bạn bè có sẵn trong HetRec nhưng chỉ được dùng với k-NN; hướng người dùng mới thường dựa vào nội dung, mà nội dung (thẻ) của nhóm thiếu cho 8.493 nghệ sĩ | Sánchez-Moreno 2024; [chuong_4_m2.md](../../results/chuong_4_m2.md) mục 1 |
| G6 | Mô hình LLM/đa phương thức cần dữ liệu và tài nguyên mà bộ dữ liệu học thuật nhỏ không có, và vẫn thiên lệch phổ biến | TalkPlay, ColdLLM, Lichtenberg 2024 |

Lưu ý: cụm "chưa thấy trong các bài đã đọc" ở G4 chỉ phản ánh phạm vi khảo sát này (khoảng 45 bài), không phải khẳng định chưa ai làm. Trước khi viết vào báo cáo là "đóng góp mới", cần tìm thêm một lượt có mục tiêu.

## 6. Hướng đề xuất

Thứ tự là mức ưu tiên đề xuất. Mỗi hướng ghi rõ giả thuyết, điểm có thể thua và chi phí. Không có con số kỳ vọng vì chưa chạy.

### H1 (đề xuất chính): Giảm thiên lệch phổ biến theo phổ, cá nhân hóa theo người dùng

**Ý tưởng.** Với mô hình nhân tố (PureSVD, ALS), ma trận điểm có dạng tích thấp hạng. Theo Lin và cs. (2024/2025) và Moon và cs. (2023), độ phổ biến nằm chủ yếu ở thành phần suy biến đầu tiên. Thay vì phạt độ phổ biến sau khi đã có top-100 như M1, H1 giảm trực tiếp phần điểm nằm trên thành phần đó:

- Bước 1 (theo phổ, không huấn luyện lại): tính phân rã suy biến của ma trận nhân tố mục (kích thước số nghệ sĩ × k, với k = 16 hoặc 32 nên rất rẻ). Điểm mới của người dùng u là điểm gốc trừ đi một phần γ_u của thành phần chiếu lên hướng suy biến đầu.
- Bước 2 (cá nhân hóa): γ_u phụ thuộc mức mainstream của chính người dùng, đo bằng độ phổ biến trung bình các nghệ sĩ trong train của họ. Người nghe ít mainstream được giảm mạnh hơn, người nghe mainstream được giữ gần mô hình gốc. Ví dụ dạng hàm: γ_u = γ_0 · (1 − m_u), với m_u là phân vị mainstream trong [0, 1]; chỉ có 1–2 tham số chọn trên validation.
- Bước 3 (tùy chọn): giữ tái xếp hạng đa dạng của M1 phía sau, nhưng thay β chung bằng β_u.

**Giải quyết khoảng trống.** G2, G3, G4. Đồng thời là phiên bản có cơ sở lý thuyết của M1, nên **giữ được mạch báo cáo** (M1 vẫn là phương pháp của nhóm, chỉ nâng cấp).

**Giả thuyết kiểm chứng.** Trên ALS, H1 cho NDCG@10 không thấp hơn ALS có ý nghĩa thống kê, trong khi ARP thấp hơn, coverage cao hơn, và NDCG@10 của nhóm LowPop cao hơn. Đây đúng là dạng "có thể thua nhẹ ở độ chính xác tổng nhưng tốt hơn nhìn chung" mà bạn nêu.

**Có thể thua ở đâu.** NDCG@10 toàn tập có thể giảm nhẹ; nhóm người nghe mainstream có thể giảm độ chính xác. Lưu ý dữ liệu: gần như mọi người dùng có đúng 40 nghệ sĩ trong train, nên phải chia nhóm theo **mức mainstream**, không theo độ dài lịch sử (mục 7 của chuong_4_test.md cho thấy chia theo độ dài lịch sử không dùng được).

**Chi phí.** Rất thấp: một phân rã suy biến cỡ (số nghệ sĩ × 32), tính lại điểm. Không cần GPU. Phần lớn công sức là phân tích theo nhóm người dùng.

### H2: Thêm nền tuyến tính mạnh (EASE, RDLAE, DAN)

**Ý tưởng.** Thêm EASE (nghiệm đóng), RDLAE (SIGIR 2023) và chuẩn hóa DAN (SIGIR 2025) làm nền. Các bài này vừa có kết quả độ chính xác tốt vừa nhắm vào mục đuôi dài. Nếu một trong số đó vượt ALS trên validation, H1 sẽ đặt trên nền đó (với EASE, bước phổ áp dụng cho ma trận trọng số mục–mục).

**Giải quyết.** G1 (so với nền mạnh, tinh chỉnh công bằng) và G4.

**Có thể thua ở đâu.** Không có gì đảm bảo EASE thắng ALS trên HetRec: danh mục có 60,57% nghệ sĩ chỉ một người nghe (data card), mô hình mục–mục có thể kém ở vùng này.

**Chi phí.** Cần nghịch đảo ma trận Gram mục × mục. Cận trên theo danh mục gốc 17.632 nghệ sĩ là 17.632² × 8 byte ≈ 2,49 GB (float64), vừa RAM 16 GB. Thời gian chưa đo; sẽ thử trên mẫu nhỏ và báo ước tính trước khi chạy đủ.

### H3: M2 có dùng mạng bạn bè (người dùng mới)

**Ý tưởng.** Với người dùng có N nhỏ, thay nhánh Popularity bằng điểm tổng hợp từ lịch sử train của bạn bè (trung bình có trọng số các vector ALS của bạn bè, hoặc lan truyền một bước trên đồ thị bạn bè), rồi trộn với nhánh thẻ như M2 hiện tại. Với N = 0, đây là cách duy nhất có căn cứ để cá nhân hóa mà không cần dữ liệu ngoài.

**Giải quyết.** G5 và kết quả âm của M2 (thua Popularity ở cả N = 1, 3, 5).

**Có thể thua ở đâu.** Nếu người dùng để dành có ít bạn hoặc bạn có sở thích khác, kết quả có thể vẫn thua Popularity. **Phải đo trước** tỷ lệ người dùng trong 189 người để dành có ít nhất một bạn nằm trong nhóm học, chỉ dùng train. Chưa có số này.

**Lưu ý rò rỉ.** Chỉ dùng lịch sử **train** của bạn bè. Không dùng validation/test của bất kỳ ai.

**Chi phí.** Thấp, CPU.

### H4 (tùy chọn): Một baseline đồ thị hiện đại

Chọn **một** trong hai: (a) Turbo-CF hoặc GF-CF, không cần huấn luyện, chạy CPU, gần PureSVD nên dễ giải thích; hoặc (b) LightGCN/XSimGCL trên GPU 4 GB (HetRec nhỏ nên có thể vừa, chưa kiểm). Mục đích là trả lời câu hỏi hội đồng có thể hỏi: "đã so với mô hình đồ thị chưa?". Không kỳ vọng đây là đóng góp chính; theo Rendle 2022 và Anelli 2022, mô hình đơn giản được tinh chỉnh tốt thường cạnh tranh.

### Không khuyến nghị cho khóa luận lần này

| Hướng | Lý do |
| --- | --- |
| LLM (TalkPlay, SAPIENT, ColdLLM, xếp hạng zero-shot) | Không có âm thanh, lời, mô tả; cần GPU lớn hoặc API trả phí; LLM cũng thiên lệch phổ biến; khó tái lập |
| Đồ thị tri thức (EARS, KCNR) | Cần dữ liệu ngoài (MusicBrainz, KB4Rec), làm thay đổi phạm vi dữ liệu đã chốt ở Chương 3 |
| Phương pháp nhân quả cần thời gian (PDA) | HetRec không có thời điểm nghe |
| BoxGNN, LFGCF, TRAL | Thiết kế cho tương tác gán thẻ, không phải lịch sử nghe |

## 7. Lưu ý phương pháp nếu triển khai

1. **Tập test đã mở một lần** cho các mô hình hiện có. Mọi mô hình mới (H1–H4) phải được chọn chỉ trên validation, ghi `lock.json` trước khi chấm test, và báo cáo phải ghi rõ đây là "thực nghiệm bổ sung sau lần chấm test chính thức". Không đổi lại cấu hình của mô hình cũ.
2. Giữ nguyên split, catalog, evaluator và ba seed 42/43/44. Các cặp kiểm định khai báo trước, hiệu chỉnh Holm như Chương 4.
3. Bổ sung đánh giá theo **nhóm mainstream** (LowPop/MedPop/HighPop theo cách của Kowald và Abdollahpouri), và một chỉ số lệch chuẩn độ phổ biến (miscalibration). Phải định nghĩa nhóm chỉ từ train và đóng băng trước khi chạy mô hình.
4. Tinh chỉnh nền mới cùng mức ngân sách như các mô hình cũ (Shehzad & Jannach 2023).
5. Thử trên mẫu nhỏ trước, báo ước tính thời gian trước khi chạy đủ; ghi cấu hình máy và phiên bản thư viện như các run hiện có.

## 8. Lộ trình đề xuất và câu hỏi cần duyệt

Thứ tự đề xuất, mỗi bước một nhánh riêng tách từ `research/data-preparation-model-survey`, chỉ commit cục bộ:

1. Đo nhanh, không chọn mô hình: phân bố mainstream của người dùng; tỷ lệ người dùng để dành có bạn trong nhóm học; năng lượng của thành phần suy biến đầu trong ALS/PureSVD và tương quan của nó với độ phổ biến nghệ sĩ. Các số này quyết định H1 và H3 có đáng làm không.
2. H2 (EASE/RDLAE/DAN) trên validation.
3. H1 trên nền tốt nhất validation.
4. H3.
5. Khóa cấu hình, chấm test một lần, viết `docs/results/chuong_4_bo_sung.md`, dừng chờ duyệt.

Câu hỏi cần bạn quyết định trước khi làm:

- **QH1.** Có đồng ý H1 là hướng chính (nâng cấp M1), với H2 và H3 hỗ trợ không?
- **QH2.** Có chấp nhận thêm mô hình sau khi test đã mở, với điều kiện ghi rõ trong báo cáo là thực nghiệm bổ sung không?
- **QH3.** Có làm H4 không, và nếu có thì loại không cần huấn luyện (CPU) hay LightGCN/XSimGCL (GPU)?
- **QH4.** Sửa trích dẫn "Lacic et al. (2024)" thành "Bevec, Tkalčič, Pesek (2024)" trong TONG_QUAN và báo cáo?

## 9. Danh mục tài liệu bổ sung đã kiểm chứng

Kiểm tra ngày 26/10/2026 bằng cách mở trang arXiv hoặc trang nhà xuất bản. Các bài đã có trong `docs` xem [nghien-cuu-2021-2025/README.md](../nghien-cuu-2021-2025/README.md) và [TONG_QUAN.md](../TONG_QUAN.md).

Mô hình phản hồi ngầm và so sánh công bằng

1. S. Rendle, W. Krichene, L. Zhang, Y. Koren. Revisiting the Performance of iALS on Item Recommendation Benchmarks. RecSys 2022. https://arxiv.org/abs/2110.14037
2. V. W. Anelli và cs. Top-N Recommendation Algorithms: A Quest for the State-of-the-Art. UMAP 2022. https://arxiv.org/abs/2203.01155
3. F. Shehzad, D. Jannach. Everyone's a Winner! On Hyperparameter Tuning of Recommendation Models. RecSys 2023. https://web-ainf.aau.at/pub/jannach/files/Conference_RecSys_2023_Repro.pdf
4. A. Milogradskii và cs. Revisiting BPR: A Replicability Study of a Common Recommender System Baseline. RecSys 2024. https://arxiv.org/abs/2409.14217
5. H. Steck. Embarrassingly Shallow Autoencoders for Sparse Data. WWW 2019 (nền). https://arxiv.org/abs/1905.03375
6. J. Moon, H. Kim, J. Lee. It's Enough: Relaxing Diagonal Constraints in Linear Autoencoders for Recommendation. SIGIR 2023. https://arxiv.org/abs/2305.12922
7. S. Park, M. Yoon, H. Kim, J. Lee. Why is Normalization Necessary for Linear Recommenders? SIGIR 2025. https://arxiv.org/abs/2504.05805

Đồ thị và học tương phản

8. X. He và cs. LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation. SIGIR 2020 (nền). https://arxiv.org/abs/2002.02126
9. Y. Shen và cs. How Powerful is Graph Convolution for Recommendation? CIKM 2021. https://arxiv.org/abs/2108.07567
10. J. Choi và cs. Blurring-Sharpening Process Models for Collaborative Filtering. SIGIR 2023. https://arxiv.org/abs/2211.09324
11. J.-D. Park và cs. Turbo-CF: Matrix Decomposition-Free Graph Filtering for Fast Recommendation. SIGIR 2024. https://arxiv.org/abs/2404.14243
12. J. Yu và cs. Are Graph Augmentations Necessary? Simple Graph Contrastive Learning for Recommendation (SimGCL). SIGIR 2022. https://arxiv.org/abs/2112.08679
13. J. Yu và cs. XSimGCL: Towards Extremely Simple Graph Contrastive Learning for Recommendation. TKDE 2023. https://arxiv.org/abs/2209.02544
14. X. Cai và cs. LightGCL: Simple Yet Effective Graph Contrastive Learning for Recommendation. ICLR 2023. https://arxiv.org/abs/2302.08191
15. C. Wang và cs. Towards Representation Alignment and Uniformity in Collaborative Filtering (DirectAU). KDD 2022. https://arxiv.org/abs/2206.12811

Thiên lệch phổ biến

16. D. Kowald, M. Schedl, E. Lex. The Unfairness of Popularity Bias in Music Recommendation: A Reproducibility Study. ECIR 2020 (có trong docs). https://arxiv.org/abs/1912.04696
17. D. Kowald và cs. Support the Underground: Characteristics of Beyond-Mainstream Music Listeners. EPJ Data Science 2021. https://arxiv.org/abs/2102.12188
18. D. Kowald. Investigating Popularity Bias Amplification in Recommender Systems Employed in the Entertainment Domain. EWAF 2025 (PMLR). https://arxiv.org/abs/2504.04752
19. H. Abdollahpouri, M. Mansoury, R. Burke, B. Mobasher, E. Malthouse. User-centered Evaluation of Popularity Bias in Recommender Systems. UMAP 2021, DOI 10.1145/3450613.3456821. https://arxiv.org/abs/2103.06364
20. T. Wei và cs. Model-Agnostic Counterfactual Reasoning for Eliminating Popularity Bias in Recommender System (MACR). KDD 2021. https://arxiv.org/abs/2010.15363
21. Y. Zhang và cs. Causal Intervention for Leveraging Popularity Bias in Recommendation (PDA). SIGIR 2021. https://arxiv.org/abs/2105.06067
22. A. Zhang và cs. Invariant Collaborative Filtering to Popularity Distribution Shift (InvCF). WWW 2023. https://arxiv.org/abs/2302.05328
23. M. Cai và cs. Popularity-Aware Alignment and Contrast for Mitigating Popularity Bias (PAAC). KDD 2024. https://arxiv.org/abs/2405.20718
24. S. Lin và cs. How Do Recommendation Models Amplify Popularity Bias? An Analysis from the Spectral Perspective. ACM, DOI 10.1145/3701551.3703579. https://arxiv.org/abs/2404.12008
25. A. Klimashevskaia, D. Jannach, M. Elahi, C. Trattner. A Survey on Popularity Bias in Recommender Systems. UMUAI 2024. https://arxiv.org/abs/2308.01118

Người dùng mới và mạng xã hội

26. J. Yu và cs. Self-Supervised Multi-Channel Hypergraph Convolutional Network for Social Recommendation (MHCN). WWW 2021. https://arxiv.org/abs/2101.06448
27. J. Yu và cs. Socially-Aware Self-Supervised Tri-Training for Recommendation (SEPT). KDD 2021. https://arxiv.org/abs/2106.03569
28. Y. Wei và cs. Contrastive Learning for Cold-Start Recommendation (CLCRec). ACM MM 2021. https://arxiv.org/abs/2107.05315
29. F. Huang và cs. Large Language Model Simulator for Cold-Start Recommendation (ColdLLM). WSDM 2025. https://arxiv.org/abs/2402.09176

LLM cho gợi ý

30. Y. Hou và cs. Large Language Models are Zero-Shot Rankers for Recommender Systems. ECIR 2024. https://arxiv.org/abs/2305.08845
31. J. M. Lichtenberg, A. Buchholz, P. Schwöbel. Large Language Models as Recommender Systems: A Study of Popularity Bias. 2024. https://arxiv.org/abs/2406.01285

Hạn chế của danh mục này: các bài 1–31 mới được kiểm tên, tác giả, nơi đăng và nội dung tóm tắt; chưa tải PDF vào `docs/` và chưa đọc toàn văn từng bài. Tên bài và mã arXiv đều đã khớp trên trang tìm kiếm hoặc trang arXiv; riêng tên tác giả đầu và nơi đăng của một số bài (số 4, 9–15, 20–23, 26–30) ghi theo hiểu biết của tôi và tên hội nghị trong kết quả tìm kiếm, chưa đối chiếu trang đầu PDF. Cần đối chiếu lại trước khi đưa vào danh mục tài liệu tham khảo của báo cáo. Khi bạn chọn hướng, tôi sẽ tải toàn văn các bài liên quan trực tiếp vào `docs/tai-lieu-tham-khao/` và đọc kỹ phần phương pháp.
