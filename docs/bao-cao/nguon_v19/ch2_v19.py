# ruff: noqa: E501, F821
# Chapter 2 of report v19 (advisor's structure 2.1-2.8, feedback of 10/11/2026).
# Numbers in KEEP/EQ are body indices of the advisor's copy
# 33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_GopY_GVHD.docx (see dump in the build notes).
# Equation numbers follow the order of appearance: (2.1)-(2.31).

CHAPTER(2)
KEEP(393)  # CHƯƠNG 2 CƠ SỞ LÝ THUYẾT
KEEP(396)
P(
    "Chương gồm tám mục. Mục 2.1 giới thiệu hệ thống khuyến nghị, phản hồi ngầm và hai mô hình cơ sở. "
    "Mục 2.2 trình bày lọc cộng tác dựa trên láng giềng, gồm UserCF, ItemCF, độ tương đồng và kỹ thuật "
    "co rút. Mục 2.3 trình bày các mô hình nhân tố tiềm ẩn: SVD có độ lệch, PureSVD và implicit ALS. "
    "Mục 2.4 xem xét khởi động nguội, khuyến nghị lai, thiên lệch phổ biến và tái xếp hạng, là cơ sở của "
    "hai mô-đun M1 và M2."
)
P(
    "Mục 2.5 giới thiệu các thước đo đánh giá: bên cạnh khả năng tìm đúng và sắp xếp các nghệ sĩ liên "
    "quan, chương xem xét phạm vi nghệ sĩ được gợi ý, mức phổ biến và độ đa dạng của kết quả. Mục 2.6 "
    "trình bày các phương pháp kiểm định thống kê dùng để so sánh mô hình. Mục 2.7 tổng hợp các nghiên "
    "cứu liên quan và khoảng trống khóa luận hướng tới; mục 2.8 kết luận chương."
)

H2("2.1 Hệ thống khuyến nghị và phản hồi ngầm")
for i in [400, 401, 402, 403, 404, 405, 406, 407]:
    KEEP(i)
P(
    "Khuyến nghị ngẫu nhiên (Random) và khuyến nghị theo mức phổ biến (Popularity) được dùng làm hai mô "
    "hình cơ sở để đối sánh (baseline). Random chọn từ các ứng viên hợp lệ theo thứ tự ngẫu nhiên. "
    "Popularity xếp các nghệ sĩ theo tổng lượt nghe đã biến đổi logarithm trên tập huấn luyện (mục "
    "3.6.2), một đại lượng gần với số người nghe nhưng có tính thêm cường độ nghe. Hai mô hình này giúp "
    "kiểm tra việc khai thác sở thích cá nhân có mang lại kết quả tốt hơn các cách gợi ý đơn giản hay "
    "không. Tất cả mô hình sử dụng cùng danh mục ứng viên và quy tắc loại nghệ sĩ đã nghe."
)

H2("2.2 Lọc cộng tác dựa trên láng giềng")
KEEP(409)
FKEEP(410, "Lọc cộng tác dựa trên láng giềng")
KEEP(412)
KEEP(413)
EQ(428, "2.1")
KEEP(
    415,
    subs=[
        (
            "Khi tính côsin, khóa luận biểu diễn",
            "Ký hiệu ⊤ là phép chuyển vị và ∥·∥₂ là chuẩn Euclid. Khi tính côsin, khóa luận biểu diễn",
        )
    ],
)
KEEP(416)
EQ(429, "2.2")
P(
    "Trong công thức (2.2), ⟦r ̂_(ui)⟧ là điểm dự đoán của người dùng ⟦u⟧ đối với nghệ sĩ ⟦i⟧. Các giá "
    "trị ⟦r ̅_u⟧ và ⟦r ̅_v⟧ là điểm trung bình trên những tương tác huấn luyện đã quan sát của từng "
    "người. Tập ⟦N_i^L (u)⟧ gồm những người dùng thuộc ⟦L⟧ láng giềng gần nhất của ⟦u⟧ và đã nghe nghệ "
    "sĩ ⟦i⟧. Mỗi láng giềng đóng góp phần chênh lệch giữa điểm của họ với điểm trung bình; người có độ "
    "tương đồng cao hơn được gán trọng số lớn hơn."
)
KEEP(419)
KEEP(420)
EQ(430, "2.3")
KEEP(422)
KEEP(423)
EQ(431, "2.4")
P(
    "Trong công thức (2.4), ⟦r_(uj)⟧ là điểm của người dùng ⟦u⟧ đối với nghệ sĩ ⟦j⟧ đã nghe. Tập "
    "⟦N^L (i)⟧ gồm ⟦L⟧ nghệ sĩ gần nhất của ứng viên ⟦i⟧, còn ⟦H_u⟧ là lịch sử huấn luyện của ⟦u⟧; "
    "giao của hai tập, ký hiệu ⟦N^L (i;u)⟧, chứa các nghệ sĩ trong lịch sử của ⟦u⟧ thuộc tập láng "
    "giềng của ⟦i⟧. Hai ký hiệu ⟦N_i^L (u)⟧ ở (2.2) và ⟦N^L (i;u)⟧ ở (2.4) được tách riêng vì một tập "
    "chứa người dùng, còn tập kia chứa nghệ sĩ. Nghệ sĩ càng giống ứng viên thì đóng góp càng lớn vào "
    "điểm dự đoán. Nếu tập này rỗng hoặc tổng trọng số bằng 0, công thức chưa thể tạo điểm và hệ thống "
    "cần chuyển sang phương án dự phòng."
)
P(
    "Khi hai người dùng (hoặc hai nghệ sĩ) chỉ có rất ít đối tượng chung, độ tương đồng côsin có thể cao "
    "một cách ngẫu nhiên. Kỹ thuật co rút (shrinkage) nhân độ tương đồng với một hệ số tăng dần theo "
    "lượng bằng chứng [12]:"
)
EQ(435, "2.5")
P(
    "Trong công thức (2.5), ⟦n_(uv)⟧ là số nghệ sĩ mà cả ⟦u⟧ và ⟦v⟧ cùng nghe (với ItemCF là số người "
    "cùng nghe hai nghệ sĩ) và ⟦γ≥0⟧ là hệ số co rút; ⟦γ=0⟧ tương ứng không co rút. Các cặp có số đối "
    "tượng chung nhỏ hơn ngưỡng tối thiểu được loại khỏi tập láng giềng; khóa luận dùng ngưỡng một đối "
    "tượng chung, đúng bằng điều kiện để côsin của hai véc-tơ không âm lớn hơn 0. Co rút làm giảm trọng "
    "số của những cặp có ít bằng chứng, nhưng cũng làm giảm điểm của các ứng viên chỉ được ít láng giềng "
    "hỗ trợ."
)
P(
    "Công thức (2.2) và (2.4) là trung bình có trọng số, được thiết kế để dự đoán điểm của một cặp "
    "người dùng–nghệ sĩ. Khi dùng để xếp hạng trên phản hồi ngầm, phép chia cho tổng độ tương đồng làm "
    "mất thông tin về số láng giềng cùng ủng hộ một ứng viên. Vì vậy, các nghiên cứu về khuyến nghị "
    "top-N như Deshpande và Karypis [39] hay Cremonesi và cộng sự [13] dùng tổng độ tương đồng có trọng "
    "số, không chia cho tổng trọng số. Biến thể này được trình bày ở mục 3.6.3."
)
KEEP(437)
KEEP(438)

H2("2.3 Lọc cộng tác dựa trên mô hình")
KEEP(440)
KEEP(441)
FKEEP(442, "Phân rã ma trận có độ lệch")
KEEP(444)
EQ(445, "2.6")
KEEP(446, subs=[("Trong công thức (2.5)", "Trong công thức (2.6)")])
KEEP(447)
EQ(451, "2.7")
KEEP(449, subs=[("Trong công thức (2.6)", "Trong công thức (2.7)")])
P(
    "Khóa luận sử dụng phương pháp giảm dần theo độ dốc ngẫu nhiên (Stochastic Gradient Descent, SGD) để "
    "học tham số. Thuật toán lần lượt xét các tương tác, tính sai số dự đoán rồi điều chỉnh độ lệch và "
    "véc-tơ nhân tố theo hướng giảm sai số. Quy tắc cập nhật như sau:"
)
EQ(459, "2.8")
P(
    "Trong công thức (2.8), ⟦e_(ui)=r_(ui)-r ̂_(ui)⟧ là sai số của cặp đang xét và ⟦η⟧ là tốc độ học. "
    "Hệ số điều chuẩn được phân bổ theo số tương tác, ⟦λ_u=λ_reg/n_u⟧ và ⟦λ_i=λ_reg/n_i⟧, với ⟦n_u⟧, "
    "⟦n_i⟧ là số tương tác huấn luyện của người dùng ⟦u⟧ và nghệ sĩ ⟦i⟧, để tổng các bước cập nhật "
    "theo từng tương tác phù hợp với hàm mục tiêu (2.7). Cả bốn phép cập nhật dùng giá trị tham số "
    "trước bước điều chỉnh; hệ số 2 khi lấy đạo hàm sai số bình phương được gộp vào tốc độ học. Các lựa "
    "chọn về số chiều, tốc độ học và điều chuẩn được kiểm tra trên tập xác thực."
)
KEEP(461)
KEEP(462)
KEEP(463)
FKEEP(464, "Tạo gợi ý bằng PureSVD")
KEEP(466)
EQ(467, "2.9")
KEEP(468, subs=[("Trong công thức (2.8)", "Trong công thức (2.9)")])
KEEP(469)
EQ(470, "2.10")
KEEP(471, subs=[("Trong công thức (2.9)", "Trong công thức (2.10)")])
for i in [472, 473, 474, 475]:
    KEEP(i)
P(
    "Với mỗi cặp ⟦(u,i)⟧, implicit ALS tách số lượt nghe ⟦w_(ui)⟧ thành sở thích nhị phân ⟦p_(ui)⟧ và độ "
    "tin cậy ⟦c_(ui)⟧:"
)
EQ(478, "2.11")
P(
    "Trong công thức (2.11), ⟦a≥0⟧ điều khiển mức tăng độ tin cậy theo lượt nghe; khóa luận dùng biến "
    "thể logarithm của [8], với tham số ⟦a⟧ được ký hiệu là a_conf ở Chương 4 và giá trị đã chọn bằng 1. "
    "Véc-tơ nhân tố ⟦x_u⟧ của người dùng và ⟦y_i⟧ của nghệ sĩ được học bằng cách cực tiểu hàm mất mát "
    "có trọng số trên toàn bộ ma trận, kể cả các ô chưa quan sát (có ⟦c_(ui)=1⟧):"
)
EQ(480, "2.12")
P(
    "Trong công thức (2.12), ⟦λ⟧ là hệ số điều chuẩn, ký hiệu reg ở Chương 4. Khi cố định ⟦Y⟧, bài toán "
    "theo từng ⟦x_u⟧ là bình phương tối thiểu có trọng số và có nghiệm đóng; khi cố định ⟦X⟧ thì tương "
    "tự với ⟦y_i⟧:"
)
EQ(482, "2.13")
P(
    "Trong công thức (2.13), ⟦C^u⟧ là ma trận đường chéo chứa ⟦c_(ui)⟧ của người dùng ⟦u⟧ trên mọi nghệ "
    "sĩ và ⟦p(u)⟧ là véc-tơ sở thích của ⟦u⟧; ⟦C^i⟧ và ⟦p(i)⟧ được định nghĩa tương tự theo nghệ sĩ. "
    "Hu và cộng sự [8] chỉ ra rằng ⟦Y^⊤ C^u Y=Y^⊤ Y+Y^⊤ (C^u-I)Y⟧; ⟦Y^⊤ Y⟧ được tính một lần cho mọi "
    "người dùng, còn ⟦C^u-I⟧ chỉ khác 0 tại các nghệ sĩ ⟦u⟧ đã nghe, nên mỗi vòng có chi phí tuyến tính "
    "theo số tương tác quan sát. Điểm xếp hạng là ⟦s ̂_(ui)=x_u^⊤ y_i⟧, không nằm trên thang 1–5, nên "
    "RMSE không áp dụng cho ALS. Khóa luận dùng implicit ALS trong một thực nghiệm mở rộng ở Chương 4."
)

H2("2.4 Khởi động nguội, khuyến nghị lai, thiên lệch phổ biến và tái xếp hạng")
for i in [485, 486, 487, 488]:
    KEEP(i)
EQ(490, "2.14")
P(
    "Trong công thức (2.14), ⟦Q⟧ là truy vấn, ⟦R⟧ là tập tài liệu ứng viên, ⟦S⟧ là tập đã chọn, "
    "⟦Sim_1⟧ đo mức liên quan với truy vấn và ⟦Sim_2⟧ đo mức giống nhau giữa hai tài liệu [18]. Hàm lựa "
    "chọn (3.9) của M1 chính là (2.14) với ⟦Sim_1⟧ thay bằng điểm mô hình nền đã chuẩn hóa, ⟦Sim_2⟧ là "
    "côsin giữa hai nghệ sĩ, và thêm số hạng phạt phổ biến theo ý tưởng của [19]."
)
KEEP(492)
KEEP(493)

H2("2.5 Các thước đo đánh giá mô hình")
for i in [498, 499, 500]:
    KEEP(i)
H3("2.5.1 Độ chính xác Precision")
KEEP(502)
EQ(503, "2.15")
KEEP(504, subs=[("Trong công thức (2.10)", "Trong công thức (2.15)")])
KEEP(505)
KEEP(506)
H3("2.5.2 Độ thu hồi Recall")
KEEP(508)
EQ(509, "2.16")
KEEP(510, subs=[("Trong công thức (2.11)", "Trong công thức (2.16)")])
KEEP(511)
KEEP(512)
H3("2.5.3 Chất lượng xếp hạng NDCG")
KEEP(514)
KEEP(515)
EQ(516, "2.17")
EQ(517, "2.18")
KEEP(518, subs=[("Trong công thức (2.12)", "Trong công thức (2.17)")])
KEEP(519, subs=[("Trong công thức (2.13)", "Trong công thức (2.18)")])
KEEP(520)
P(
    "Với nhãn nhị phân, IDCG được tính theo công thức sau; Phụ lục B dùng công thức này để kiểm tra các "
    "ví dụ tính tay:"
)
EQ(522, "2.19")
KEEP(523)
H3("2.5.4 Căn sai số bình phương trung bình RMSE")
KEEP(525)
EQ(526, "2.20")
KEEP(527, subs=[("Trong công thức (2.14)", "Trong công thức (2.20)")])
KEEP(528)
KEEP(529)
H3("2.5.5 Độ bao phủ danh mục")
KEEP(531)
EQ(532, "2.21")
KEEP(533, subs=[("Trong công thức (2.15)", "Trong công thức (2.21)")])
KEEP(534)
KEEP(535)
H3("2.5.6 Hệ số Gini")
KEEP(537)
EQ(538, "2.22")
KEEP(539, subs=[("Trong công thức (2.16)", "Trong công thức (2.22)")])
KEEP(540)
KEEP(541)
H3("2.5.7 Độ phổ biến trung bình")
KEEP(543)
EQ(560, "2.23")
KEEP(545, subs=[("Trong công thức (2.17)", "Trong công thức (2.23)")])
KEEP(546)
KEEP(547)
H3("2.5.8 Độ mới")
KEEP(549)
EQ(561, "2.24")
KEEP(551, subs=[("Trong công thức (2.18)", "Trong công thức (2.24)")])
KEEP(552)
KEEP(553)
H3("2.5.9 Độ đa dạng trong danh sách")
KEEP(555)
EQ(562, "2.25")
KEEP(557, subs=[("Trong công thức (2.19)", "Trong công thức (2.25)")])
KEEP(563)
KEEP(564)

H2("2.6 Kiểm định thống kê trong so sánh mô hình")
P(
    "Các mô hình được đánh giá trên cùng tập người dùng nên kết quả của hai mô hình A và B tạo thành các "
    "cặp quan sát. Với mỗi người dùng ⟦u⟧, gọi ⟦d_u=NDCG@10_A (u)-NDCG@10_B (u)⟧. Phân phối của ⟦d_u⟧ "
    "thường lệch mạnh và có nhiều giá trị bằng 0 (nhiều người dùng có NDCG@10 bằng 0 ở cả hai mô hình), "
    "nên kiểm định t theo cặp với giả định phân phối chuẩn không phù hợp. Khóa luận dùng kiểm định hạng "
    "có dấu Wilcoxon [27], một kiểm định phi tham số cho dữ liệu cặp."
)
P(
    "Sau khi bỏ các cặp có ⟦d_u=0⟧, còn lại ⟦n⟧ cặp. Các giá trị ⟦|d_u|⟧ được xếp hạng tăng dần, ⟦R_u⟧ "
    "là hạng của ⟦|d_u|⟧ (lấy hạng trung bình khi bằng nhau). Thống kê kiểm định là tổng hạng của các "
    "chênh lệch dương và âm:"
)
EQ(569, "2.26")
P(
    "Dưới giả thuyết ⟦H_0⟧ rằng phân phối của ⟦d_u⟧ đối xứng quanh 0, khi ⟦n⟧ lớn ⟦W^+⟧ xấp xỉ phân phối "
    "chuẩn (chưa kể hiệu chỉnh cho các hạng bằng nhau):"
)
EQ(571, "2.27")
P(
    "Giá trị p chỉ cho biết khác biệt quan sát được có dễ xảy ra do ngẫu nhiên hay không. Với gần 1.900 "
    "người dùng, khác biệt rất nhỏ cũng có thể cho p rất bé, vì vậy cần báo cáo thêm cỡ hiệu ứng. Với "
    "kiểm định Wilcoxon, một cỡ hiệu ứng dễ diễn giải là hệ số tương quan hạng hai chuỗi cho dữ liệu cặp "
    "(matched-pairs rank-biserial correlation) [43]:"
)
EQ(573, "2.28")
P(
    "Hệ số ⟦r_rb⟧ nằm trong đoạn ⟦[-1;1]⟧; ⟦r_rb=1⟧ khi A tốt hơn B ở mọi người dùng có chênh lệch khác "
    "0, và ⟦r_rb⟧ gần 0 khi số người được lợi và bị thiệt gần cân bằng về hạng."
)
P(
    "Khi thực hiện ⟦m⟧ kiểm định trong cùng một họ, xác suất mắc ít nhất một sai lầm loại I tăng theo "
    "⟦m⟧. Phương pháp Holm [28] sắp các giá trị p tăng dần ⟦p_((1))≤p_((2))≤…≤p_((m))⟧ và tính giá trị "
    "p hiệu chỉnh:"
)
EQ(576, "2.29")
P(
    "Giả thuyết thứ ⟦k⟧ bị bác bỏ khi giá trị p hiệu chỉnh ⟦p ̃_((k))≤α⟧. Holm kiểm soát xác suất mắc ít "
    "nhất một sai lầm loại I của cả họ ở mức ⟦α⟧ và ít bảo thủ hơn hiệu chỉnh Bonferroni."
)
P(
    "Khoảng tin cậy của chênh lệch trung bình được ước lượng bằng bootstrap phân vị [29]: lấy mẫu có "
    "hoàn lại ⟦n⟧ người dùng, tính trung bình chênh lệch ⟦d ̅_b^*⟧ trên mẫu thứ ⟦b⟧, lặp lại ⟦B⟧ lần. "
    "Khoảng tin cậy mức ⟦1-2a⟧ là:"
)
EQ(579, "2.30")
P(
    "Trong công thức (2.30), ⟦d ̅_((q))^*⟧ là phân vị ⟦q⟧ của ⟦B⟧ giá trị bootstrap; với khoảng 95% thì "
    "⟦a=0,025⟧. Để các khoảng tin cậy của nhiều cặp mô hình nhất quán với nhau, mọi cặp dùng chung một "
    "bộ chỉ số người dùng được lấy mẫu ở mỗi lần lặp. Khoảng tin cậy bootstrap không được hiệu chỉnh cho "
    "nhiều phép so sánh, nên có thể xảy ra trường hợp khoảng tin cậy không chứa 0 nhưng p sau Holm lớn "
    "hơn 0,05."
)
P(
    "Một kết quả không có ý nghĩa thống kê không chứng minh hai mô hình tương đương. Khi cần kết luận "
    "“mô hình A giữ được độ chính xác của B”, cần kiểm định tương đương hai phía (two one-sided tests, "
    "TOST) [42] với biên tương đương ⟦δ⟧ đặt trước: ⟦H_0: |μ_d |≥δ⟧ và ⟦H_1: -δ<μ_d<δ⟧. Ở mức ý nghĩa "
    "⟦α=0,05⟧, tương đương được chấp nhận khi khoảng tin cậy 90% của ⟦μ_d⟧ nằm trọn trong khoảng "
    "⟦(-δ;δ)⟧:"
)
EQ(582, "2.31")

H2("2.7 Các nghiên cứu liên quan")
P(
    "Hướng thứ nhất là các mô hình láng giềng và nhân tố tiềm ẩn cho bài toán gợi ý top-N. Sarwar và "
    "cộng sự [5] đề xuất ItemCF và cho thấy độ tương đồng giữa các đối tượng có thể tính trước, nhưng "
    "đánh giá chủ yếu bằng sai số dự đoán điểm trên dữ liệu chấm điểm tường minh. Deshpande và Karypis "
    "[39] chuyển ItemCF sang bài toán top-N, tính điểm ứng viên bằng tổng độ tương đồng với các đối tượng "
    "người dùng đã có và chuẩn hóa ma trận tương đồng, đánh giá bằng tỷ lệ trúng (HR) và ARHR. Cremonesi "
    "và cộng sự [13] so sánh các mô hình láng giềng, mô hình tối ưu RMSE và PureSVD trên Netflix và "
    "MovieLens, và cho thấy mô hình tối ưu sai số dự đoán điểm không nhất thiết xếp hạng tốt, trong khi "
    "PureSVD rất cạnh tranh ở bài toán top-N. Hai công trình sau là cơ sở trực tiếp cho thực nghiệm E7 và "
    "cho cách giải thích kết quả của SVD có độ lệch ở Chương 4."
)
P(
    "Hướng thứ hai là mô hình cho phản hồi ngầm và giao thức đánh giá. Hu và cộng sự [8] đề xuất implicit "
    "ALS, tách mỗi quan sát thành sở thích và độ tin cậy, trên dữ liệu xem truyền hình. Về giao thức, "
    "Breese và cộng sự [40] so sánh các thuật toán lọc cộng tác theo nhiều giao thức thực nghiệm, trong "
    "đó có các giao thức chỉ cung cấp cho hệ thống một số ít đối tượng của người dùng, là nguồn gốc của "
    "thí nghiệm Given-N ở khóa luận. Sun và cộng sự [21] chỉ ra nhiều nghiên cứu dùng phép chia, tập ứng "
    "viên và chỉ số khác nhau nên kết quả khó so sánh, còn Ji và cộng sự [22] cho thấy rò rỉ thông tin "
    "từ dữ liệu đánh giá có thể làm sai lệch kết luận khi đánh giá ngoại tuyến. Hai công trình này là căn "
    "cứ cho việc khóa cấu hình trước khi mở tập kiểm thử và dùng chung một bộ đánh giá cho mọi mô hình."
)
P(
    "Hướng thứ ba là thiên lệch phổ biến và các chỉ số ngoài độ chính xác trong khuyến nghị âm nhạc. "
    "Kaminskas và Bridge [10] tổng hợp các thước đo đa dạng, độ mới, tính bất ngờ và độ bao phủ. "
    "Abdollahpouri và cộng sự [19] dùng tái xếp hạng cá nhân hóa để tăng cơ hội cho các mục ít phổ biến, "
    "đánh giá bằng ARP cùng các chỉ số về mục đuôi dài. Kowald và cộng sự [9] lặp lại nghiên cứu về tính "
    "không công bằng của thiên lệch phổ biến trên bộ LFM-1b và thấy nhóm người dùng ít ưa chuộng nghệ sĩ "
    "phổ biến nhận gợi ý kém hơn. Bộ Last.fm HetRec 2011 được công bố tại hội thảo HetRec 2011 [41] và "
    "được dùng trong nhiều công trình, chẳng hạn PoissonMF-CS [24] kết hợp nội dung và quan hệ xã hội, "
    "hay CoLaKG [25] dùng mô hình ngôn ngữ lớn để khai thác đồ thị tri thức. Bảng 2.1 tóm tắt các công "
    "trình này."
)
T(
    "Tóm tắt một số nghiên cứu liên quan",
    [1500, 1250, 1600, 1450, 1650, 1338],
    [
        "Công trình",
        "Dữ liệu",
        "Phương pháp",
        "Giao thức, chỉ số",
        "Kết quả chính",
        "Liên hệ với khóa luận",
    ],
    [
        [
            "Sarwar và cộng sự [5], 2001",
            "MovieLens",
            "ItemCF với các độ đo tương đồng khác nhau",
            "MAE trên điểm tường minh",
            "ItemCF cho chất lượng tốt, có thể tính trước độ tương đồng",
            "Cơ sở của ItemCF và thành phần cộng tác của M2",
        ],
        [
            "Deshpande và Karypis [39], 2004",
            "Tám bộ dữ liệu thực",
            "ItemCF top-N: tổng độ tương đồng, chuẩn hóa ma trận tương đồng",
            "Tỷ lệ trúng (HR), ARHR",
            "Nhanh hơn tới hai bậc độ lớn so với láng giềng người dùng, chất lượng tương đương hoặc tốt hơn",
            "Cơ sở của biến thể top-N trong E7",
        ],
        [
            "Hu và cộng sự [8], 2008",
            "Dữ liệu xem truyền hình (phản hồi ngầm)",
            "Implicit ALS có trọng số tin cậy",
            "Xếp hạng phần trăm kỳ vọng",
            "Vượt mô hình láng giềng và mô hình phổ biến",
            "Mô hình mở rộng E5",
        ],
        [
            "Cremonesi và cộng sự [13], 2010",
            "Netflix, MovieLens",
            "PureSVD, láng giềng top-N, mô hình tối ưu RMSE",
            "Recall@N",
            "Mô hình tối ưu RMSE không tốt cho top-N; PureSVD rất cạnh tranh",
            "Giải thích SVD có độ lệch thua PureSVD",
        ],
        [
            "Abdollahpouri và cộng sự [19], 2019",
            "MovieLens 1M, Epinions",
            "Tái xếp hạng cá nhân hóa (xQuAD) để cân bằng mục phổ biến và đuôi dài",
            "Kiểm định chéo 5 phần; ARP, APLT, ACLT, NDCG",
            "Tăng mục đuôi dài với mức giảm độ chính xác nhỏ; ARP một mình chưa đủ",
            "Ý tưởng phạt phổ biến của M1",
        ],
        [
            "Kowald và cộng sự [9], 2020",
            "LFM-1b (mẫu 3.000 người dùng)",
            "Các thuật toán lọc cộng tác phổ biến",
            "MAE theo nhóm mức ưa chuộng nghệ sĩ phổ biến",
            "Nhóm ít ưa chuộng phổ biến nhận gợi ý kém hơn",
            "Cơ sở cho Bảng 4.10",
        ],
        [
            "da Silva và cộng sự [24], 2017",
            "Last.fm HetRec 2011 (1.892 người dùng, 17.632 nghệ sĩ), tương tác nhị phân hóa",
            "PoissonMF-CS (nội dung từ thẻ và mạng xã hội)",
            "Chia ngẫu nhiên 85/15, lặp 30 lần; Recall@M trung bình trên người dùng",
            "Vượt rõ CTR và CTR-SMF (số liệu đối sánh lấy từ bài gốc của CTR-SMF)",
            "Cùng bộ dữ liệu, giao thức khác",
        ],
        [
            "Cui và cộng sự [25], 2025",
            "Last-FM (HetRec 2011; 1.859 người dùng, 2.813 mục), MovieLens, MIND, Fund",
            "CoLaKG (mô hình ngôn ngữ lớn và đồ thị tri thức)",
            "Chia 80/20 theo người dùng; Recall@K, NDCG@K, K = 10, 20, xếp hạng toàn danh mục",
            "Vượt các mô hình đối sánh trên cả bốn bộ dữ liệu",
            "Hướng phát triển",
        ],
    ],
    align=["left"] * 6,
    size=20,
)
P(
    "So với các công trình trên, khóa luận hướng tới ba điểm. Thứ nhất, so sánh các mô hình kinh điển "
    "(láng giềng, phân rã ma trận, implicit ALS) trên Last.fm HetRec 2011 theo cùng một giao thức chặt "
    "chẽ: cấu hình được khóa trên tập xác thực, các cặp kiểm định được khai báo trước, có khoảng tin cậy, "
    "cỡ hiệu ứng và hiệu chỉnh cho nhiều phép so sánh. Thứ hai, khi đánh giá tái xếp hạng, khóa luận tách "
    "các chỉ số dùng chung đại lượng với hàm lựa chọn khỏi các thước đo độc lập, vì chỉ số đa dạng tính "
    "bằng cùng độ tương đồng với hàm lựa chọn sẽ tăng gần như theo định nghĩa. Thứ ba, khóa luận dùng giao "
    "thức Given-N để đánh giá khả năng hỗ trợ người dùng mới trên bộ dữ liệu này."
)

H2("2.8 Kết luận chương")
P(
    "Chương 2 đã trình bày cơ sở của các mô hình được sử dụng trong khóa luận: lọc cộng tác dựa trên láng "
    "giềng (UserCF, ItemCF), các mô hình nhân tố tiềm ẩn (SVD có độ lệch học trên các cặp quan sát, "
    "PureSVD xấp xỉ toàn bộ ma trận và implicit ALS cho phản hồi ngầm), cùng các hướng hỗ trợ khi thiếu "
    "lịch sử và khi cần giảm thiên lệch phổ biến. Chương cũng xác định các thước đo xếp hạng, các thước "
    "đo ngoài độ chính xác và các phương pháp kiểm định được dùng để so sánh mô hình. Một điểm xuyên suốt "
    "là mô hình tối ưu sai số dự đoán điểm chưa chắc xếp hạng tốt, nên khóa luận chọn NDCG@10 làm tiêu "
    "chí chính. Chương 3 vận dụng các cơ sở này để thiết kế dữ liệu, mô hình, hai mô-đun M1, M2 và quy "
    "trình đánh giá thống nhất."
)
