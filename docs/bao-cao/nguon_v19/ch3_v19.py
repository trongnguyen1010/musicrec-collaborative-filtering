# ruff: noqa: E501, F821
# Chapter 3 of report v19 (advisor feedback of 10/11/2026). Indices refer to the advisor's copy.
# Data statistics come from the E-D run (scripts/report_e_d_data.py), copied in
# docs/results/chinh_thuc_cloud_20261026/bo_sung_2/e_d/.
import json as _json

ED = "docs/results/chinh_thuc_cloud_20261026/bo_sung_2/e_d/"
FIG = "docs/results/chinh_thuc_cloud_20261026/bo_sung_2/hinh_bao_cao/"
ed = _json.loads(open(ED + "metrics.json", encoding="utf-8").read())
raw, aft, tags = ed["raw"], ed["after_cleaning"], ed["tags"]


def vn(x, d=2):
    s = f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def n_(x):
    return f"{int(x):,}".replace(",", ".")


CHAPTER(3)
KEEP(590)  # CHƯƠNG 3
P(
    "Chương này chuyển bài toán ở mục 1.2.3 và cơ sở lý thuyết ở Chương 2 thành một thiết kế cụ thể. "
    "Trước hết, chương phân tích yêu cầu, đầu vào, đầu ra và kiến trúc tổng thể của hệ thống. Tiếp theo, "
    "chương mô tả bộ dữ liệu Last.fm HetRec 2011, quy trình làm sạch, chia tập và biến đổi, với nguyên "
    "tắc mọi thống kê chỉ học từ tập huấn luyện. Sau đó, chương trình bày cấu hình của sáu mô hình đối "
    "sánh, biến thể top-N của mô hình láng giềng, thiết kế hai mô-đun M1, M2 và quy trình tạo danh sách "
    "gợi ý. Cuối cùng, chương mô tả quy trình đánh giá thống nhất được dùng cho mọi thực nghiệm ở Chương 4."
)

H2("3.1 Phân tích yêu cầu")
H3("3.1.1 Yêu cầu chức năng")
KEEP(596)
TCAP("Các yêu cầu chức năng của hệ thống")
KEEP(598)
P(
    "Hình 3.1 trình bày sơ đồ ca sử dụng của phần ứng dụng. Người dùng có sẵn xem lịch sử nghe, nhận gợi "
    "ý và có thể bật M1 để so sánh với danh sách của PureSVD. Người dùng mới chọn một vài nghệ sĩ khởi "
    "đầu và nhận danh sách từ M2, hoặc danh sách phổ biến khi chưa chọn nghệ sĩ nào. Người đánh giá chạy "
    "lại thực nghiệm và đối chiếu bảng chỉ số, kiểm định với kết quả trong báo cáo."
)
F(FIG + "so_do_ca_su_dung.png", "Sơ đồ ca sử dụng của hệ thống", width_cm=14.0)
H3("3.1.2 Yêu cầu chất lượng")
P(
    "Bảng 3.2 liệt kê các yêu cầu chất lượng cùng tiêu chí kiểm tra để Chương 5 đối chiếu. Thời gian phản "
    "hồi không có ngưỡng đặt trước; nhóm đo và báo cáo trên môi trường cụ thể trước khi đưa ra nhận xét về "
    "tốc độ."
)
T(
    "Các yêu cầu chất lượng và cách kiểm tra",
    [800, 2000, 4188, 1800],
    ["Mã", "Yêu cầu", "Tiêu chí kiểm tra", "Minh chứng"],
    [
        [
            "Q01",
            "Tái lập",
            "Chạy lại cùng hạt giống cho tệp dữ liệu, ánh xạ và chỉ số trùng mã băm",
            "Mục 3.5, Phụ lục A",
        ],
        [
            "Q02",
            "Không rò rỉ dữ liệu",
            "Mọi thống kê, ngưỡng, từ vựng thẻ chỉ học từ tập huấn luyện; tinh chỉnh không đọc tệp kiểm thử",
            "Mục 3.5, 3.8, 4.4",
        ],
        [
            "Q03",
            "Nhất quán trực tuyến và ngoại tuyến",
            "100% danh sách top-10 trùng cả thứ tự",
            "Bảng 5.5",
        ],
        [
            "Q04",
            "Đúng ràng buộc danh sách",
            "Không trùng, không chứa lịch sử, tối đa K",
            "Bảng 5.4",
        ],
        ["Q05", "Thời gian phản hồi", "Đo và báo cáo", "Bảng 5.6"],
        [
            "Q06",
            "Dễ bảo trì",
            "Mô hình, API, giao diện tách lớp; giao diện mô hình chung",
            "Hình 5.1",
        ],
    ],
    align=["center", "left", "left", "left"],
)

H2("3.2 Phân tích đầu vào và đầu ra")
H3("3.2.1 Đầu vào của dữ liệu và mô hình")
KEEP(608)
KEEP(609)
H3("3.2.2 Đầu ra và ý nghĩa điểm số")
KEEP(611)
KEEP(612)

H2("3.3 Kiến trúc tổng thể")
P(
    "Hệ thống gồm hai luồng như Hình 3.2. Luồng ngoại tuyến kiểm tra dữ liệu, chia tập, biến đổi, huấn "
    "luyện, tinh chỉnh, đánh giá rồi xuất gói mô hình. Luồng trực tuyến nhận yêu cầu, kiểm tra đầu vào, "
    "định tuyến nhánh xử lý, chấm điểm bằng mô hình chính, M1 hoặc M2 và trả phản hồi. Hai luồng chỉ nối "
    "với nhau qua gói mô hình có mã băm, nên ứng dụng dùng đúng phiên bản mô hình đã đánh giá."
)
F(FIG + "luong_hai_lan.png", "Luồng xử lý ngoại tuyến và trực tuyến của hệ thống", width_cm=15.5)
P(
    "Các tham số mô hình, ánh xạ mã và ngưỡng biến đổi phải được nạp cùng phiên bản. Tập kiểm thử được "
    "giữ riêng với dữ liệu phục vụ ứng dụng. Hình 3.3 thể hiện vị trí của mô hình và hai mô-đun M1, M2 "
    "trong hệ thống."
)
FKEEP(618, "Kiến trúc mô hình và dịch vụ MusicRec")
KEEP(620)

H2("3.4 Bộ dữ liệu Last.fm HetRec 2011")
H3("3.4.1 Thành phần dữ liệu")
KEEP(624, subs=[("Bảng 3.2", "Bảng 3.3")])
TCAP("Các tệp dữ liệu và vai trò sử dụng")
KEEP(626)
H3("3.4.2 Đặc điểm quy mô và độ thưa")
KEEP(628)
EQ(629, "3.1")
KEEP(630)
H3("3.4.3 Kết quả khám phá dữ liệu gốc")
KEEP(632)
KEEP(633)
P(
    "Bảng 3.4 tổng hợp các thống kê mô tả của dữ liệu gốc và của dữ liệu sau điều kiện tối thiểu năm nghệ "
    "sĩ cho mỗi người dùng. Tổng số lượt nghe trong dữ liệu gốc là "
    f"{n_(raw['total_listens'])}; sau khi loại 15 người dùng có lịch sử ngắn, tổng này còn "
    f"{n_(aft['total_listens'])}. Tỷ lệ người dùng có đúng 50 nghệ sĩ tăng từ "
    f"{vn(raw['users_exactly_50_artists_pct'])}% lên {vn(aft['users_exactly_50_artists_pct'])}% vì mẫu số "
    "giảm, còn số người không đổi."
)
T(
    "Thống kê mô tả bộ dữ liệu Last.fm HetRec 2011",
    [3988, 2400, 2400],
    ["Thống kê", "Dữ liệu gốc", "Sau khi lọc (≥ 5 nghệ sĩ/người)"],
    [
        ["Số người dùng", n_(raw["users"]), n_(aft["users"])],
        ["Số nghệ sĩ trong danh mục", n_(raw["artists_catalog"]), n_(aft["artists_catalog"])],
        [
            "Số nghệ sĩ có tương tác",
            n_(raw["artists_with_interactions"]),
            n_(aft["artists_with_interactions"]),
        ],
        ["Số cặp người dùng–nghệ sĩ", n_(raw["interactions"]), n_(aft["interactions"])],
        [
            "Mật độ ma trận (trên danh mục)",
            vn(raw["density_pct"], 4) + "%",
            vn(aft["density_pct"], 4) + "%",
        ],
        [
            "Số nghệ sĩ mỗi người dùng: trung bình / trung vị",
            f"{vn(raw['mean_artists_per_user'])} / {n_(raw['median_artists_per_user'])}",
            f"{vn(aft['mean_artists_per_user'])} / {n_(aft['median_artists_per_user'])}",
        ],
        [
            "Số nghệ sĩ mỗi người dùng: nhỏ nhất / lớn nhất",
            f"{raw['min_artists_per_user']} / {raw['max_artists_per_user']}",
            f"{aft['min_artists_per_user']} / {aft['max_artists_per_user']}",
        ],
        [
            "Số người dùng có đúng 50 nghệ sĩ",
            f"{n_(raw['users_exactly_50_artists'])} ({vn(raw['users_exactly_50_artists_pct'])}%)",
            f"{n_(aft['users_exactly_50_artists'])} ({vn(aft['users_exactly_50_artists_pct'])}%)",
        ],
        [
            "Số người nghe mỗi nghệ sĩ có tương tác: trung bình / trung vị",
            f"{vn(raw['mean_listeners_per_active_artist'])} / {n_(raw['median_listeners_per_active_artist'])}",
            f"{vn(aft['mean_listeners_per_active_artist'])} / {n_(aft['median_listeners_per_active_artist'])}",
        ],
        [
            "Số nghệ sĩ chỉ có một người nghe",
            n_(raw["single_listener_artists"]),
            n_(aft["single_listener_artists"]),
        ],
        ["Tổng số lượt nghe", n_(raw["total_listens"]), n_(aft["total_listens"])],
        [
            "Số lượt nghe của một cặp: trung vị / lớn nhất",
            f"{n_(raw['median_pair_listening_count'])} / {n_(raw['max_pair_listening_count'])}",
            f"{n_(aft['median_pair_listening_count'])} / {n_(aft['max_pair_listening_count'])}",
        ],
        [
            "Số dòng gán thẻ / nối được danh mục",
            f"{n_(tags['tag_assignment_rows_raw'])} / {n_(tags['tag_assignment_rows_joined_catalog'])}",
            "Không đổi (thẻ không lọc theo người dùng)",
        ],
        [
            "Số nghệ sĩ trong danh mục chưa có thẻ",
            n_(tags["catalog_artists_without_tags"]),
            f"{n_(tags['active_artists_without_tags'])} (trong số nghệ sĩ có tương tác)",
        ],
    ],
    note="Mật độ tính theo công thức (3.1) với mẫu số là số người dùng nhân với 17.632 nghệ sĩ của danh mục. Tổng lượt nghe sau lọc là con số được dùng ở các mục sau.",
    align=["left", "center", "center"],
)
P(
    "Hình 3.4 vẽ số người nghe của từng nghệ sĩ theo thứ hạng trên dữ liệu gốc: phân bố có dạng đuôi dài, "
    "một nhóm nhỏ nghệ sĩ có hàng trăm người nghe, còn "
    f"{n_(raw['single_listener_artists'])} nghệ sĩ chỉ có một người nghe. Hình 3.5 cho thấy tổng lượt nghe "
    "của người dùng trải rộng nhiều bậc độ lớn, nên lượt nghe gốc cần được biến đổi trước khi dùng làm điểm "
    "(mục 3.5.3)."
)
F(
    ED + "hinh_4_1_goc.png",
    "Số người nghe của nghệ sĩ theo thứ hạng trên dữ liệu gốc",
    width_cm=15.0,
)
F(ED + "hinh_4_2_goc.png", "Phân bố tổng lượt nghe theo người dùng trên dữ liệu gốc", width_cm=15.0)

H2("3.5 Tiền xử lý và chia tập")
H3("3.5.1 Kiểm tra và chuẩn hóa dữ liệu")
P(
    "Mã người dùng và nghệ sĩ được giữ dưới dạng định danh nguyên dương. Số lượt nghe phải là số nguyên "
    "dương hữu hạn. Bản ghi trùng hoàn toàn chỉ giữ một; nếu cùng một cặp có số lượt nghe khác nhau, quy "
    "trình dừng để xác minh thay vì tự cộng. Dữ liệu thực tế không có dòng bị loại bởi các kiểm tra này. "
    "Số lượt nghe lớn nhất của một cặp (352.698) được giữ nguyên, không cắt ngoại lai; các biểu diễn bổ "
    "sung được tạo sau khi chia tập."
)
P(
    "Bước làm sạch giữ nguyên tệp nguồn và lưu riêng từng dòng bị loại cùng lý do. Danh mục và từ điển thẻ "
    "được bảo toàn. Có 15 nghệ sĩ không còn tương tác sau khi loại nhóm người dùng ít lịch sử; các mã này "
    "vẫn nằm trong danh mục. Chi tiết về bảng mã ký tự và cách đối chiếu tệp nguồn được trình bày ở Phụ "
    "lục A.4."
)
KEEP(642)
KEEP(643)
P(
    "Cách giới hạn nội dung thẻ theo danh mục tương tác và cách đọc từ điển thẻ bằng bảng mã ISO-8859-1 "
    "của nhóm thống nhất với mã tiền xử lý đã công bố của PoissonMF-CS [24] và CoLaKG [25]. Các công trình "
    "này không báo cáo số dòng gán thẻ không nối được danh mục; con số 1.538 dòng do nhóm tự kiểm tra trên "
    "tệp nén chính thức của GroupLens. Điều kiện mỗi người dùng có tối thiểu năm nghệ sĩ là lựa chọn riêng "
    "của khóa luận."
)
H3("3.5.2 Chia tập theo người dùng")
KEEP(648)
EQ(649, "3.2")
KEEP(650)
P(
    "Kết quả chia gồm 74.275 tương tác huấn luyện, 9.263 tương tác xác thực và 9.263 tương tác kiểm thử; "
    "mỗi tập đều có đủ 1.877 người dùng. Ba tập không giao cặp người dùng–nghệ sĩ và bảo toàn đủ 92.801 "
    "tương tác cùng từng giá trị lượt nghe. Nhóm giữ cố định các tập cho mọi mô hình đối sánh, không chuyển "
    "tương tác giữa các tập để cải thiện kết quả."
)
KEEP(652)
KEEP(653)
H3("3.5.3 Biến đổi sau chia tập")
KEEP(655)
P(
    "Với ⟦y_(ui)=log_2 (1+w_(ui))⟧ và bốn ngưỡng ⟦θ_1≤θ_2≤θ_3≤θ_4⟧ là các phân vị 20%, 40%, 60%, 80% "
    "(nội suy tuyến tính) của ⟦y⟧ trên ⟦Ω_train⟧, điểm đại diện được tính bằng:"
)
EQ(658, "3.3")
P(
    "Trong công thức (3.3), ⟦𝟙[⋅]⟧ bằng 1 khi điều kiện đúng và bằng 0 trong trường hợp ngược lại; giá trị "
    "bằng ngưỡng thuộc mức thấp hơn. Các ngưỡng chỉ học trên ⟦Ω_train⟧ và được giữ nguyên khi áp dụng cho "
    "tập xác thực và kiểm thử."
)
KEEP(660)
P(
    "Mỗi biểu diễn huấn luyện được lưu thành ma trận thưa 1.877 × 15.398 với 74.275 ô quan sát, cùng thứ "
    "tự hàng và cột theo ánh xạ đã chốt. Ô không quan sát không được thêm vào như nhãn không thích hoặc "
    "điểm một sao. Ba bảng tương tác vẫn giữ nguyên từng cặp, số lượt nghe và chỉ số nguồn, kể cả chỉ số "
    "nghệ sĩ để trống ở đích ngoài danh mục. Mức phổ biến, độ tương đồng và đặc trưng thẻ chưa được học ở "
    "bước này."
)
KEEP(662)
H3("3.5.4 Giới hạn của phép chia ngẫu nhiên")
KEEP(664)
KEEP(665)

H2("3.6 Thiết kế các mô hình đối sánh")
H3("3.6.1 Khuyến nghị ngẫu nhiên")
KEEP(668)
H3("3.6.2 Khuyến nghị theo mức phổ biến")
KEEP(670, subs=[("Trong chương này, nhóm sử dụng", "Trong khóa luận, nhóm sử dụng")])
EQ(671, "3.4")
KEEP(672, subs=[("Trong công thức (3.3)", "Trong công thức (3.4)")])
H3("3.6.3 Mô hình láng giềng")
KEEP(675)
KEEP(676)
KEEP(677)
P(
    "Các công thức (2.2) và (2.4) là trung bình có trọng số, được thiết kế để dự đoán điểm. Khi chia cho "
    "tổng độ tương đồng, một nghệ sĩ chỉ được một láng giềng nghe với điểm đại diện cao có thể có điểm "
    "bằng hoặc cao hơn một nghệ sĩ được nhiều láng giềng cùng nghe, nên thông tin về độ hỗ trợ bị mất. "
    "Ngoài ra, các ứng viên không có láng giềng nhận cùng một điểm trung bình và được xếp theo mã nghệ sĩ. "
    "Với bài toán xếp hạng trên phản hồi ngầm, nhóm bổ sung một biến thể top-N, trong đó điểm của ứng "
    "viên là tổng độ tương đồng có trọng số, không chia cho tổng trọng số [13], [39]:"
)
EQ(681, "3.5")
EQ(682, "3.6")
P(
    "Trong công thức (3.5) và (3.6), ⟦x⟧ là giá trị tương tác, bằng 1 với biểu diễn nhị phân hoặc "
    "⟦log_2 (1+w)⟧ với biểu diễn log-count, và ⟦x_(vi)=0⟧ khi ⟦v⟧ chưa nghe ⟦i⟧. Cùng biểu diễn này được "
    "dùng để tính côsin. Khác với (2.2) và (2.4), một nghệ sĩ được nhiều láng giềng cùng nghe sẽ có điểm "
    "cao hơn, nên độ hỗ trợ được giữ lại; ứng viên không có láng giềng hỗ trợ có điểm bằng 0."
)
P(
    "Thực nghiệm E7 đánh giá biến thể này với biểu diễn nhị phân và log-count, ⟦L∈{10,20,50,100,200}⟧ và "
    "hệ số co rút ⟦γ∈{0,10}⟧, tức 20 cấu hình cho mỗi mô hình. Cấu hình được chọn theo NDCG@10 trên tập "
    "xác thực với hạt giống 42, rồi chấm một lần trên tập kiểm thử và kiểm định với Popularity và "
    "PureSVD. Vì E7 được thêm sau khi tập kiểm thử đã mở cho sáu mô hình đối sánh, kết quả được báo cáo "
    "trong mục phân tích bổ sung (mục 4.11) và không thay đổi các cấu hình đã khóa."
)
H3("3.6.4 SVD có độ lệch và PureSVD")
KEEP(686)
KEEP(687)
KEEP(688)
KEEP(689)
TCAP("Đầu vào và tham số đã chốt của các mô hình")
KEEP(691)

H2("3.7 Mô-đun tái xếp hạng M1")
H3("3.7.1 Chuẩn bị ứng viên và điểm")
KEEP(694)
KEEP(695)
P("Điểm nền và mức phổ biến được chuẩn hóa như sau:")
EQ(699, "3.7")
EQ(700, "3.8")
P(
    "Trong công thức (3.7) và (3.8), ⟦𝒞⟧ là tập ⟦C⟧ ứng viên của người dùng ⟦u⟧ và ⟦c_i⟧ là số người nghe "
    "phân biệt của nghệ sĩ ⟦i⟧ trên tập huấn luyện. Khi mọi ứng viên có cùng điểm nền, mẫu số của (3.7) "
    "bằng 0 và ⟦s ̃_(ui)⟧ được đặt bằng 1 cho mọi ứng viên, nên thành phần liên quan không phân biệt các "
    "ứng viên. Mẫu số của (3.8) luôn dương vì danh mục huấn luyện có ít nhất một nghệ sĩ có người nghe. "
    "Mọi biến thể dùng cùng quy tắc chuẩn hóa."
)
H3("3.7.2 Hàm lựa chọn tuần tự")
KEEP(703)
EQ(704, "3.9")
KEEP(705, subs=[("Trong công thức (3.4)", "Trong công thức (3.9)")])
KEEP(706)
KEEP(707)
H3("3.7.3 Kiểm chứng bằng loại bỏ thành phần")
KEEP(709)
KEEP(710)
KEEP(711)
P(
    "Quy tắc chọn ARP thấp nhất trong các cấu hình giảm NDCG@10 không quá 5% luôn đẩy ⟦β⟧ lên giá trị "
    "lớn nhất còn thỏa ngưỡng. Vì 10 trên 12 điểm của lưới thỏa ngưỡng, ⟦β=0,5⟧ được chọn chủ yếu do giới "
    "hạn của lưới chứ không do dữ liệu. Mục 4.11 mở rộng ⟦β⟧ trên tập xác thực để vẽ trọn đường đánh đổi; "
    "kết quả mở rộng chỉ dùng để thảo luận, cấu hình đã khóa không thay đổi."
)
H3("3.7.4 Minh họa cách chọn kết quả")
KEEP(714)

H2("3.8 Mô-đun dự phòng M2")
H3("3.8.1 Biểu diễn thẻ nghệ sĩ")
KEEP(717)
KEEP(718)
EQ(719, "3.10")
KEEP(720, subs=[("Trong công thức (3.5)", "Trong công thức (3.10)")])
KEEP(721)
H3("3.8.2 Hồ sơ người dùng từ lịch sử")
KEEP(723)
EQ(724, "3.11")
KEEP(725, subs=[("Trong công thức (3.6)", "Trong công thức (3.11)")])
KEEP(726)
H3("3.8.3 Kết hợp điểm và xử lý dự phòng")
KEEP(728)
KEEP(729)
EQ(730, "3.12")
EQ(731, "3.13")
KEEP(
    732,
    subs=[
        ("Trong công thức (3.7)", "Trong công thức (3.12)"),
        ("Trong công thức (3.8)", "Trong công thức (3.13)"),
    ],
)
P(
    "Với cấu hình đã chọn (⟦α=0,75⟧; ⟦n_min=10⟧) và ⟦N≤5⟧ thì ⟦ω(N)=N/10≤0,5⟧, trong đó ⟦N⟧ là số nghệ "
    "sĩ được cung cấp. Bảng 3.6 cho trọng số danh nghĩa của ba thành phần trên thang đã chuẩn hóa."
)
T(
    "Trọng số danh nghĩa của các thành phần trong M2 theo N",
    [1000, 2400, 2700, 2688],
    ["N", "Cộng tác ω(N)", "Nội dung (1 − ω)α", "Phổ biến (1 − ω)(1 − α)"],
    [
        ["0", "0", "0 (không có hồ sơ)", "1"],
        ["1", "0,100", "0,675", "0,225"],
        ["3", "0,300", "0,525", "0,175"],
        ["5", "0,500", "0,375", "0,125"],
    ],
    note="Trọng số áp dụng cho ứng viên có cả điểm ItemCF và điểm nội dung. Ứng viên không có điểm ItemCF nhận ω = 0, nên toàn bộ trọng số chuyển sang phần dự phòng; khi hồ sơ không có nghệ sĩ nào có thẻ, phần dự phòng chỉ còn mức phổ biến.",
    align=["center"] * 4,
)
P(
    "Như vậy trong toàn bộ thí nghiệm Given-N, M2 về bản chất là mô hình nội dung có pha thêm ItemCF; "
    "thành phần phổ biến chỉ chiếm 12,5–22,5% trọng số khi người dùng có ít nhất một nghệ sĩ được cung cấp."
)
KEEP(739, subs=[("Hình 3.3", "Hình 3.6")])
FKEEP(740, "Các tình huống xử lý của mô-đun M2")
H3("3.8.4 Giới hạn và cách kiểm tra")
KEEP(743)
KEEP(744)
KEEP(745)
KEEP(746)
P(
    "Trong giao thức đã khóa, tập đích của người dùng để dành là các cặp kiểm thử của họ giao với danh "
    "mục nhóm học, trung bình khoảng năm nghệ sĩ mỗi người. Hệ thống chỉ che N nghệ sĩ được cung cấp, nên "
    "khoảng 40 − N nghệ sĩ huấn luyện còn lại của người dùng vẫn nằm trong tập ứng viên nhưng không thuộc "
    "tập đích; mỗi lần hệ thống gợi ý trúng một nghệ sĩ như vậy đều bị tính là sai. Giao thức Given-N gốc "
    "của Breese và cộng sự [40] lấy toàn bộ phần lịch sử không được cung cấp làm tập đích:"
)
EQ(748, "3.14")
P(
    "Trong công thức (3.14), ⟦P_u^((N))⟧ là hồ sơ ⟦N⟧ nghệ sĩ được cung cấp và ⟦ℐ_learn⟧ là danh mục "
    "13.210 nghệ sĩ của nhóm học; chỉ ⟦N⟧ nghệ sĩ trong hồ sơ bị loại khỏi tập ứng viên. Với cách này mỗi "
    "người có khoảng 40 đích nên phương sai giảm. Nhóm giữ nguyên kết quả đã khóa theo giao thức cũ và "
    "chạy phương án (3.14) như một phân tích bổ sung ở mục 4.11."
)

H2("3.9 Quy trình tạo danh sách gợi ý")
KEEP(751)
KEEP(752)

H2("3.10 Quy trình đánh giá thống nhất")
H3("3.10.1 Tập đích và tập ứng viên")
KEEP(755)
KEEP(756)
H3("3.10.2 Tính chỉ số và nhóm người dùng")
KEEP(758)
KEEP(759, subs=[("công thức (2.18)", "công thức (2.24)")])
KEEP(760)
KEEP(761)
H3("3.10.3 Kiểm tra trước thực nghiệm")
KEEP(763)

H2("3.11 Kết luận chương")
P(
    "Chương 3 đã phân tích yêu cầu và thiết kế toàn bộ hệ thống, từ dữ liệu đến mô hình và quy trình đánh "
    "giá. Dữ liệu Last.fm HetRec 2011 sau khi lọc gồm 1.877 người dùng và 92.801 cặp, được chia theo từng "
    "người dùng với tỷ lệ xấp xỉ 80/10/10; ánh xạ, ngưỡng điểm đại diện, mức phổ biến và đặc trưng thẻ "
    "chỉ học từ tập huấn luyện. Sáu mô hình đối sánh dùng chung danh mục ứng viên và quy tắc lọc; mô hình "
    "láng giềng có thêm biến thể top-N cho phân tích bổ sung. Mô-đun M1 tái xếp hạng 100 ứng viên của "
    "PureSVD bằng hàm lựa chọn kết hợp mức phù hợp, độ khác biệt và phạt phổ biến; mô-đun M2 kết hợp "
    "ItemCF, nội dung thẻ và mức phổ biến cho người dùng mới, được đánh giá bằng giao thức Given-N riêng. "
    "Quy trình đánh giá thống nhất xác định rõ tập đích, tập ứng viên và cách xử lý các trường hợp biên. "
    "Chương 4 trình bày kết quả của các thiết kế này."
)
