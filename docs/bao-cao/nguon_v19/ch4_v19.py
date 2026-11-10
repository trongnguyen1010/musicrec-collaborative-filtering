# ruff: noqa: E501, F821
# Chapter 4 of report v19 (advisor feedback of 10/11/2026). Numbers are read from the result
# files below, never typed from memory, except where the text says otherwise.
# Locked runs: docs/results/chinh_thuc_cloud_20261026/{test,m2,bo_sung}.
# Supplementary analyses after locking (phase 1, 10/11/2026): .../bo_sung_2/.
import json as _json

import pandas as _pd

D = "docs/results/chinh_thuc_cloud_20261026/"
BS = D + "bo_sung/"
B2 = D + "bo_sung_2/"


def f(x, d=6):
    s = f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s.replace("-", "−")


def num(x):
    return f"{int(x):,}".replace(",", ".")


def pct(x, d=2):
    return f(100 * x, d) + "%"


def pv(p):
    """p-value convention of Section 4.1.2: < 10⁻¹⁰, < 0,001 or three decimals."""
    if p < 1e-10:
        return "< 10⁻¹⁰"
    if p < 0.001:
        return "< 0,001"
    return f(p, 3)


def pv_text(p):
    return "p " + pv(p) if p < 0.001 else "p = " + pv(p)


def ci(r, lo="ci95_low", hi="ci95_high"):
    return f"[{f(r[lo])}; {f(r[hi])}]"


def load(path):
    return _json.loads(open(path, encoding="utf-8").read())


test = _pd.read_csv(D + "test/metrics.csv")
test = test[test.seed == 42]


def tm(model, k, metric):
    return float(test[(test.model == model) & (test.k == k)][metric].iloc[0])


stats = load(B2 + "thong_ke/kiem_dinh_bo_sung.json")
pre = {(r["a"], r["b"]): r for r in stats["predeclared_pairs_recomputed"]}
fam = {r["b"]: r for r in stats["supplementary_family_pure_svd_vs_others_holm"]}
means = stats["mean_ndcg10_bootstrap_ci"]
tost = stats["m1_pure_svd_equivalence"]
m1_tests = {r["a"]: r for r in load(B2 + "thong_ke/m1_kiem_dinh_bien_the.json")}
m2_stats = {
    (r["n"], r["b"]): r for r in load(B2 + "thong_ke/m2_statistics_ndcg_at_10.json")["pairs"]
}
seeds = load(D + "test/seed_summary.json")
groups = _pd.read_csv(D + "test/history_groups.csv")
split = load(BS + "chenh_lech_puresvd_popularity.json")
variants = _pd.read_csv(BS + "m1_bien_the_test.csv").set_index("bien_the")
ild_models = load(BS + "ild_the_mo_hinh.json")
examples = _pd.read_csv(BS + "m1_vi_du.csv")
paths = _pd.read_csv(BS + "m2_duong_xu_ly.csv").set_index("n")
m2 = _pd.read_csv(D + "m2/test/metrics.csv")
m2 = m2[m2.k == 10]
m2_sel = load(D + "m2/validation/selection.json")
cost = _pd.read_csv(D + "test/cost.csv").set_index("model")
m1_grid = _pd.read_csv(D + "m1_metrics.csv")
m1_grid = m1_grid[(m1_grid.seed == 42) & (m1_grid.k == 10)]
curve = _pd.read_csv(BS + "learning_curve.csv")
check = load(BS + "doi_chieu_chinh_thuc.json")
hist_ci = _pd.read_csv(B2 + "e_c/nhom_lich_su_ci.csv")
ms_ci = _pd.read_csv(B2 + "e_c/bang_4_10_ci.csv")
kw = _pd.read_csv(B2 + "e_c/bang_4_10_kruskal_wallis.csv").set_index("mo_hinh")
ec_tests = {
    r["nhom"]: r for r in load(B2 + "e_c/metrics.json")["m1_minus_pure_svd_by_group_holm_over_3"]
}
e7 = _pd.read_csv(B2 + "e7/metrics.csv")
e7 = e7[e7.k == 10].set_index("model")
e7_stats = load(B2 + "e7/statistics_ndcg_at_10.json")
e7_pairs = {(r["a"], r["b"]): r for r in e7_stats["pairs"]}
e7_sel = load(B2 + "e7/selection.json")["winners"]
e7_val = _pd.read_csv(B2 + "e7/validation_summary.csv")
eg = _pd.read_csv(B2 + "eg/metrics.csv")
eg = eg[eg.k == 10]
eg_stats = {(r["n"], r["b"]): r for r in load(B2 + "eg/statistics_ndcg_at_10.json")["pairs"]}
es = _pd.read_csv(B2 + "e_s/baselines_validation.csv")
es_m2 = _pd.read_csv(B2 + "e_s/m2_mean_n135.csv")
eb = _pd.read_csv(B2 + "e_b/hinh_4_6.csv")
eb_meta = load(B2 + "e_b/metrics.json")
ep = _pd.read_csv(B2 + "e_p/popularity_validation.csv").set_index("score")
EG_EVAL = "outputs/chuong_4_bo_sung_2/eg/n_{}/m2/evaluation.json"
eg_targets = {}
for _n in [0, 1, 3, 5]:
    _pu = load(EG_EVAL.format(_n))["per_user"]
    eg_targets[_n] = (
        sum(v["targets_total"] for v in _pu.values()) / len(_pu),
        sum(v["targets_in_catalog"] for v in _pu.values()) / len(_pu),
    )

NAMES = {
    "random": "Random",
    "popularity": "Popularity",
    "user_cf": "UserCF",
    "item_cf": "ItemCF",
    "svd": "SVD có độ lệch",
    "pure_svd": "PureSVD",
    "m1": "M1 (PureSVD + tái xếp hạng)",
    "implicit_als": "Implicit ALS (mở rộng)",
}
SHORT = {"m1": "M1", "implicit_als": "Implicit ALS"}
SIX = ["random", "popularity", "user_cf", "item_cf", "svd", "pure_svd"]
ALL = SIX + ["m1", "implicit_als"]
pop, pure = tm("popularity", 10, "ndcg"), tm("pure_svd", 10, "ndcg")

CHAPTER(4)
KEEP(767)  # CHƯƠNG 4
P(
    "Chương này trình bày kết quả huấn luyện và đánh giá các mô hình theo giao thức đã mô tả ở mục 3.10. "
    "Thứ tự trình bày bám theo các câu hỏi nghiên cứu ở Bảng 1.1: mục 4.1 nêu môi trường và quy ước báo "
    "cáo; mục 4.2 tóm tắt dữ liệu sau tiền xử lý; mục 4.3 tổng hợp các thực nghiệm; mục 4.4 trình bày quá "
    "trình tinh chỉnh trên tập xác thực; mục 4.5 so sánh các mô hình trên tập kiểm thử (RQ1); mục 4.6 phân "
    "tích theo độ dài lịch sử và theo từng người dùng (RQ2); mục 4.7 đánh giá mô-đun tái xếp hạng M1 "
    "(RQ3); mục 4.8 đánh giá mô-đun dự phòng M2 (RQ4, RQ2); mục 4.9 trình bày thực nghiệm mở rộng với "
    "implicit ALS; mục 4.10 so sánh chi phí xử lý; mục 4.11 trình bày các phân tích bổ sung được thực hiện "
    "sau khi đã khóa cấu hình; mục 4.12 thảo luận chung và mục 4.13 kết luận chương. Tập kiểm thử chỉ được "
    "dùng sau khi mọi cấu hình của các thực nghiệm chính đã được chốt trên tập xác thực."
)

H2("4.1 Môi trường và quy ước báo cáo")
H3("4.1.1 Môi trường thực nghiệm")
P(
    "Các số liệu huấn luyện, tinh chỉnh và kiểm thử của các thực nghiệm chính đến từ một lần chạy liên tục "
    "trên máy ảo đám mây (Linux 6.18 x86_64, bộ xử lý Intel Xeon 2,10 GHz với 4 luồng logic, khoảng 15,7 "
    "GiB RAM), bắt đầu từ dữ liệu gốc và đi qua tiền xử lý, chia tập, tinh chỉnh, khóa cấu hình và kiểm "
    "thử. Mã nguồn dùng Python 3.11.17 cùng NumPy 2.4.6, SciPy 1.17.1 [31], pandas 2.3.3, pyarrow 19.0.1, "
    "scikit-learn 1.9.1 và implicit 0.7.3 [30] cho mô hình ALS. Phân rã PureSVD dùng hàm svds của SciPy với "
    "bộ giải ARPACK. Mọi bước đặt thư viện đại số tuyến tính chạy một luồng để kết quả tái lập được. Toàn "
    "bộ lần chạy mất khoảng 48 phút, trong đó tinh chỉnh chiếm 42,8 phút."
)
P(
    "Lần chạy trên chỉ lưu bảng chỉ số tổng hợp của tập kiểm thử. Để phân tích theo từng người dùng, kiểm "
    "định lại với bootstrap dùng chung chỉ số và chạy các phân tích bổ sung ở mục 4.11, nhóm chấm lại tập "
    "kiểm thử trên máy cá nhân (Windows 11, Intel Core i5-11300H 3,10 GHz với 8 luồng logic, 15,7 GiB RAM, "
    "Python 3.11.9 và cùng phiên bản NumPy, SciPy, pandas, pyarrow, implicit) bằng đúng các mô hình đã khóa. "
    "PureSVD, M1 và ALS được nạp lại từ tệp mô hình đã lưu; UserCF, ItemCF và SVD có độ lệch được huấn "
    "luyện lại với cấu hình đã khóa và cho NDCG@10 xác thực trùng tới mọi chữ số với lần chạy chính thức. "
    "Trên tập kiểm thử, 24 chỉ số (8 chỉ số tại K = 5, 10, 20) của cả tám mô hình khớp với bảng chính "
    "thức, sai lệch lớn nhất nhỏ hơn 10⁻¹⁴ do làm tròn số thực; chênh lệch trung bình và giá trị p của các "
    "cặp kiểm định trùng với các giá trị đã khóa. Lần chấm lại không chọn lại cấu hình nào. Thời gian xử lý "
    "ở mục 4.10 là số đo trên máy đám mây."
)
P(
    "Mỗi lần chạy được lưu thành một bộ tệp theo quy ước ở Phụ lục A, gồm cấu hình, mã băm dữ liệu, ánh "
    "xạ, quy tắc biến đổi, tham số mô hình, danh sách dự đoán theo người dùng và bảng chỉ số. Hạt giống "
    "chia dữ liệu split_seed = 42 được giữ cố định cho mọi mô hình. Các mô hình có yếu tố ngẫu nhiên dùng "
    "hạt giống 42 để chọn cấu hình, sau đó cấu hình thắng được chạy lại ở hạt giống 43 và 44 để xem mức "
    "dao động."
)
H3("4.1.2 Quy ước báo cáo và kiểm định thống kê")
P(
    "Các chỉ số xếp hạng Precision@K, Recall@K và NDCG@K được tính cho từng người dùng có ít nhất một đích "
    "hợp lệ rồi lấy trung bình không trọng số, tại K = 5, 10 và 20. NDCG@10 là chỉ số chính để chọn cấu "
    "hình và so sánh mô hình. Các chỉ số bổ sung gồm độ bao phủ, hệ số Gini, độ phổ biến trung bình (ARP), "
    "độ mới và độ đa dạng trong danh sách (ILD) được tính tại K = 10. Độ bao phủ và Gini là chỉ số trên "
    "toàn danh mục nên chỉ có một giá trị cho mỗi mô hình. RMSE trên điểm đại diện chỉ là chỉ số phụ, không "
    "dùng để xếp hạng mô hình."
)
P(
    "Vì các mô hình được đánh giá trên cùng một nhóm người dùng, sự khác biệt giữa hai mô hình được kiểm "
    "định theo cặp trên NDCG@10 của từng người dùng bằng kiểm định Wilcoxon có dấu hai phía (mục 2.6). Với "
    "mỗi cặp, những người dùng có chênh lệch bằng 0 bị loại khỏi kiểm định Wilcoxon và cỡ hiệu ứng; số "
    "người còn lại được ghi trong tệp kết quả. Khi có nhiều cặp so sánh, giá trị p được hiệu chỉnh theo "
    "phương pháp Holm với mức ý nghĩa 0,05. Bốn cặp kiểm định chính được ghi vào tệp khóa trước khi mở tập "
    "kiểm thử: PureSVD với Popularity, SVD có độ lệch với PureSVD, M1 với PureSVD và ALS với PureSVD. Các "
    "so sánh thêm ngoài bốn cặp này được ghi là kiểm định bổ sung và hiệu chỉnh Holm trong họ riêng của "
    "chúng."
)
P(
    "Khoảng tin cậy 95% (và 90% khi dùng cho kiểm định tương đương) được tính bằng bootstrap phân vị với "
    "1.000 lần lấy mẫu lại theo người dùng, hạt giống 42. Mọi cặp mô hình trên cùng một nhóm người dùng "
    "dùng chung một bộ chỉ số được lấy mẫu ở mỗi lần lặp, nên khoảng tin cậy của hai cặp ngược chiều đối "
    "xứng với nhau và các khoảng của cùng một bảng so sánh được với nhau. Cỡ hiệu ứng là hệ số tương quan "
    "hạng hai chuỗi ⟦r_rb⟧ theo (2.28). Giá trị p nhỏ hơn ⟦10^(-10)⟧ được ghi là “< 10⁻¹⁰”, vì ở mức này "
    "phép xấp xỉ chuẩn không còn ý nghĩa về chữ số; giá trị từ 10⁻¹⁰ đến dưới 0,001 được ghi là “< 0,001”; "
    "các giá trị còn lại ghi ba chữ số thập phân."
)

H2("4.2 Dữ liệu sau tiền xử lý")
P(
    "Sau bước làm sạch và điều kiện tối thiểu năm nghệ sĩ cho mỗi người dùng, dữ liệu còn 1.877 người dùng "
    "và 92.801 cặp tương tác (Bảng 3.4). Bảng 4.1 tóm tắt kết quả chia tập theo mục 3.5.2. Danh mục huấn "
    "luyện gồm 15.398 nghệ sĩ; các đích ở tập xác thực và kiểm thử không thuộc danh mục này được báo cáo "
    "riêng và không tham gia tính chỉ số."
)
T(
    "Thống kê các tập dữ liệu sau khi chia",
    [3388, 1800, 1800, 1800],
    ["Thông tin", "Huấn luyện", "Xác thực", "Kiểm thử"],
    [
        ["Số cặp tương tác", "74.275", "9.263", "9.263"],
        ["Số người dùng", "1.877", "1.877", "1.877"],
        ["Số nghệ sĩ trong danh mục huấn luyện", "15.398", "-", "-"],
        ["Đích ngoài danh mục huấn luyện", "-", "1.121 (12,10%)", "1.203 (12,99%)"],
        ["Số đích hợp lệ", "-", "8.142", "8.060"],
        ["Người dùng có ít nhất một đích hợp lệ", "-", "1.865", "1.855"],
    ],
)
below = groups[(groups.model == "popularity") & (groups.group == "below_mode")].iloc[0]
at = groups[(groups.model == "popularity") & (groups.group == "at_mode")].iloc[0]
above = groups[(groups.model == "popularity") & (groups.group == "above_mode")].iloc[0]
P(
    "Một đặc điểm quan trọng của dữ liệu là mỗi người dùng chỉ được ghi nhận những nghệ sĩ nghe nhiều nhất, "
    "và 1.829 người dùng có đúng 50 nghệ sĩ trong dữ liệu gốc. Với quy tắc chia ở công thức (3.2), trên tập "
    f"huấn luyện có {num(at.users_total)} người dùng có đúng 40 tương tác, {int(below.users_total)} người "
    f"dùng có ít hơn 40 và {int(above.users_total)} người dùng có nhiều hơn 40. Vì vậy, bài toán đánh giá "
    "trong khóa luận là tìm lại một phần danh sách nghệ sĩ yêu thích của người dùng từ phần còn lại, không "
    "phải dự đoán lần nghe tiếp theo. Phân bố số người nghe của nghệ sĩ và tổng lượt nghe của người dùng "
    "trên dữ liệu gốc được trình bày ở Hình 3.4 và Hình 3.5."
)

H2("4.3 Tổng hợp các thực nghiệm")
P(
    "Bảng 4.2 liệt kê các thực nghiệm và câu hỏi nghiên cứu tương ứng. Ngoại trừ E1 chỉ dùng tập xác thực, "
    "các thực nghiệm E2 đến E6 báo cáo kết quả trên tập kiểm thử với cấu hình đã chốt. Các thực nghiệm E7 "
    "đến E10 được thực hiện sau khi tập kiểm thử đã mở, nên được trình bày riêng ở mục 4.11 như phân tích "
    "bổ sung và không thay đổi cấu hình đã khóa."
)
T(
    "Các thực nghiệm và câu hỏi nghiên cứu",
    [800, 5188, 1600, 1200],
    ["Mã", "Nội dung", "Câu hỏi", "Mục"],
    [
        [
            "E1",
            "Tinh chỉnh tham số của các mô hình trên tập xác thực theo NDCG@10",
            "Chuẩn bị",
            "4.4",
        ],
        [
            "E2",
            "So sánh sáu mô hình đối sánh trên tập kiểm thử bằng chỉ số xếp hạng, chỉ số bổ sung và kiểm định",
            "RQ1",
            "4.5",
        ],
        [
            "E3",
            "Phân tích theo nhóm độ dài lịch sử, theo mức ưa chuộng nghệ sĩ phổ biến và theo từng người dùng",
            "RQ2",
            "4.6",
        ],
        ["E4", "Đánh giá M1 và các biến thể loại bỏ thành phần", "RQ3", "4.7"],
        ["E5", "Thực nghiệm mở rộng với implicit ALS", "RQ1 (bổ sung)", "4.9"],
        [
            "E6",
            "Đánh giá M2 theo giao thức người dùng mới Given-N với N = 0, 1, 3, 5",
            "RQ4, RQ2",
            "4.8",
        ],
        [
            "E7",
            "UserCF, ItemCF với cách tổng hợp top-N (3.5), (3.6), chọn trên tập xác thực, chấm trên tập kiểm thử",
            "RQ1 (bổ sung)",
            "4.11",
        ],
        [
            "E8",
            "Độ nhạy ngoài biên lưới tìm kiếm, chỉ trên tập xác thực",
            "Chuẩn bị (bổ sung)",
            "4.11",
        ],
        ["E9", "Mở rộng β của M1, chỉ trên tập xác thực", "RQ3 (bổ sung)", "4.7, 4.11"],
        ["E10", "Given-N với tập đích (3.14), cấu hình M2 đã khóa", "RQ4, RQ2 (bổ sung)", "4.11"],
    ],
    align=["center", "left", "center", "center"],
)

H2("4.4 Tinh chỉnh tham số trên tập xác thực")
P(
    "Tham số của các mô hình được chọn theo NDCG@10 trên tập xác thực ở hạt giống 42; tập kiểm thử chưa "
    "được dùng ở bước này và các script tinh chỉnh chặn mọi thao tác mở tệp kiểm thử. Bảng 4.3 tóm tắt "
    "không gian tìm kiếm, số cấu hình đã chạy và cấu hình được chọn. Tổng cộng có 48 cấu hình cho năm mô "
    "hình có tham số. UserCF, ItemCF, PureSVD và ALS quét toàn bộ lưới; SVD có độ lệch dùng cấu hình mặc "
    "định cộng 11 cấu hình sinh ngẫu nhiên bằng hạt giống 42. Với SVD có độ lệch và ALS, số vòng huấn luyện "
    "được chọn bằng dừng sớm theo NDCG@10 xác thực với số vòng chờ 5."
)
T(
    "Không gian tìm kiếm và cấu hình được chọn",
    [1500, 3088, 2700, 1500],
    ["Mô hình", "Không gian tìm kiếm (số cấu hình)", "Cấu hình chọn", "NDCG@10 (xác thực)"],
    [
        ["Random", "Không có tham số", "Hạt giống 42", "0,000372"],
        ["Popularity", "Không có tham số", "Tổng log2(1 + lượt nghe)", "0,062362"],
        [
            "UserCF",
            "L ∈ {20, 40, 80, 120}; co rút ∈ {0, 10, 50}; côsin (12)",
            "L = 20, co rút 0",
            "0,017488",
        ],
        [
            "ItemCF",
            "L ∈ {20, 40, 80, 120}; co rút ∈ {0, 10, 50}; côsin (12)",
            "L = 20, co rút 0",
            "0,015364",
        ],
        [
            "SVD có độ lệch",
            "d ∈ {16, 32, 64, 128}; η ∈ [0,001; 0,02], λreg ∈ [0,001; 0,1] thang log; tối đa 100 vòng, chờ 5 (12)",
            "d = 16, η = 0,001925, λreg = 0,01025, vòng 2",
            "0,060666",
        ],
        ["PureSVD", "k ∈ {16, 32, 64, 128}, biểu diễn nhị phân (4)", "k = 16", "0,166611"],
        [
            "Implicit ALS",
            "Số nhân tố ∈ {32, 64}; reg ∈ {0,01; 0,1}; a_conf ∈ {1, 10} (8)",
            "32 nhân tố, reg 0,1, a_conf 1, vòng 16",
            "0,197433",
        ],
    ],
    align=["left", "left", "left", "center"],
)
P(
    "Với UserCF và ItemCF, NDCG@10 giảm khi số láng giềng tăng; co rút làm ItemCF kém đi rõ rệt (với L = 20, "
    "NDCG@10 giảm từ 0,015364 khi không co rút xuống 0,005616 khi co rút 10). PureSVD đạt cao nhất ở k = 16 "
    "và giảm dần khi k tăng: 0,166611; 0,156427; 0,137042 và 0,114355 với k = 16, 32, 64, 128. Nhóm giữ "
    "nguyên lưới đã định trước và không mở rộng sau khi thấy kết quả, để tránh chọn cấu hình theo tập xác "
    "thực nhiều lần."
)
P(
    "Nhiều cấu hình được chọn nằm ở biên của lưới: L = 20 của UserCF và ItemCF, k = 16 của PureSVD là giá "
    "trị nhỏ nhất; ALS chọn 32 nhân tố và a_conf = 1 (nhỏ nhất) cùng reg = 0,1 (lớn nhất); M1 chọn β = 0,5 "
    "(lớn nhất, mục 3.7.3); M2 chọn α = 0,75 và n_min = 10 (đều lớn nhất). Để định lượng giới hạn này, nhóm "
    "chạy thêm một phân tích độ nhạy ngoài biên lưới chỉ trên tập xác thực, sau khi đã khóa cấu hình (E8). "
    "Kết quả ở Bảng 4.19, mục 4.11, cho thấy với PureSVD và ALS không cấu hình ngoài biên nào tốt hơn cấu "
    "hình đã chọn, với M2 tăng n_min chỉ cải thiện rất nhỏ, còn với UserCF và ItemCF cực đại nằm ngoài lưới cũ."
)
P(
    "Bảng 4.4 so sánh ba biểu diễn đầu vào của PureSVD ở cùng k = 32 trên tập xác thực, đo trong lần chạy "
    "phát triển trước lần chạy chính thức. Biểu diễn nhị phân đạt NDCG@10 cao nhất (0,156427), tiếp theo là "
    "log-count (0,154577) và điểm đại diện (0,151692). Giá trị của biểu diễn nhị phân trùng với cấu hình "
    "k = 32 trong lần chạy chính thức. Kết quả này phù hợp với bản chất phản hồi ngầm của dữ liệu: việc một "
    "người dùng có nghe một nghệ sĩ mang nhiều thông tin cho bài toán tìm lại nghệ sĩ hơn là mức độ nghe "
    "nhiều hay ít. Biểu diễn nhị phân được chọn trước khi mở tập kiểm thử."
)
T(
    "NDCG@10 trên tập xác thực của PureSVD với ba biểu diễn (k = 32)",
    [4394, 4394],
    ["Biểu diễn", "NDCG@10"],
    [["Nhị phân", "0,156427"], ["Log-count", "0,154577"], ["Điểm đại diện 1–5", "0,151692"]],
)
best_epoch = int(curve.loc[curve.validation_ndcg_at_10.idxmax(), "epoch"])
last = curve.iloc[-1]
first = curve.iloc[0]
min_rmse = curve.loc[curve.validation_proxy_rmse.idxmin()]
P(
    f"Đối với SVD có độ lệch, vòng tốt nhất theo NDCG@10 là vòng {best_epoch} trong khi số vòng tối đa là "
    "100. Để kiểm tra nguyên nhân, nhóm huấn luyện lại cấu hình đã chọn đủ 100 vòng, không dừng sớm, và ghi "
    "NDCG@10 cùng RMSE điểm đại diện trên tập huấn luyện và tập xác thực sau mỗi vòng (Hình 4.1). Bảy vòng "
    "đầu trùng từng chữ số với lần huấn luyện có dừng sớm. NDCG@10 xác thực đạt đỉnh "
    f"{f(curve.validation_ndcg_at_10.max())} ở vòng {best_epoch} rồi giảm dần, còn "
    f"{f(last.validation_ndcg_at_10)} ở vòng {int(last.epoch)}. Trong cùng khoảng đó RMSE trên tập huấn "
    f"luyện giảm từ {f(first.train_proxy_rmse, 4)} xuống {f(last.train_proxy_rmse, 4)}, và RMSE trên tập "
    f"xác thực giảm từ {f(first.validation_proxy_rmse, 4)} xuống thấp nhất "
    f"{f(min_rmse.validation_proxy_rmse, 4)} ở vòng {int(min_rmse.epoch)} rồi tăng nhẹ lên "
    f"{f(last.validation_proxy_rmse, 4)} ở vòng {int(last.epoch)}. Như vậy trong khoảng 50 vòng đầu, sai số "
    "dự đoán trên cả các cặp chưa dùng để huấn luyện vẫn được cải thiện trong khi chất lượng xếp hạng top-K "
    "trên toàn danh mục đi xuống: hai mục tiêu này không khớp nhau trên dữ liệu phản hồi ngầm. Ở các vòng "
    "đầu, mô hình chủ yếu học điểm trung bình và độ lệch của nghệ sĩ nên thứ tự gợi ý gần với mức phổ biến; "
    "càng về sau, mô hình càng khớp điểm của các cặp đã nghe nhưng không học gì từ các nghệ sĩ người dùng "
    "chưa nghe."
)
F(
    BS + "hinh/hinh_4_3.png",
    "NDCG@10 xác thực và RMSE điểm đại diện theo vòng huấn luyện của SVD có độ lệch",
    note="Đường học được đo trong 100 vòng với cấu hình đã khóa và hạt giống 42.",
)

H2("4.5 So sánh các mô hình trên tập kiểm thử")
P(
    "Bảng 4.5 trình bày chất lượng xếp hạng của sáu mô hình đối sánh trên tập kiểm thử với hạt giống 42, "
    "tính trên cùng 1.855 người dùng có đích hợp lệ. Danh sách gợi ý trên tập kiểm thử loại cả lịch sử huấn "
    "luyện và lịch sử xác thực. Hai dòng cuối, ngăn cách với sáu mô hình đối sánh, là M1 (mục 4.7) và "
    "implicit ALS (mục 4.9) để tiện so sánh trên cùng giao thức. Bảng đầy đủ Precision, Recall và NDCG tại "
    "K = 5, 10 và 20 của tám mô hình được trình bày ở Phụ lục D."
)
rank_rows = []
for m in ALL:
    cells = [
        f(tm(m, 10, "precision")),
        f(tm(m, 10, "recall")),
        f(tm(m, 5, "ndcg")),
        f(tm(m, 10, "ndcg")),
        f(tm(m, 20, "ndcg")),
    ]
    if m == "pure_svd":
        cells = [f"**{c}**" for c in cells]
    rank_rows.append([NAMES[m]] + cells)
rank_rows.insert(6, ["Thực nghiệm bổ sung trên cùng giao thức", "", "", "", "", ""])
T(
    "Chất lượng xếp hạng trên tập kiểm thử",
    [2228, 1312, 1312, 1312, 1312, 1312],
    ["Mô hình", "P@10", "R@10", "NDCG@5", "NDCG@10", "NDCG@20"],
    rank_rows,
    note="Mọi chỉ số càng cao càng tốt; số in đậm là giá trị cao nhất trong sáu mô hình đối sánh.",
)
P(
    "Bảng 4.6 trình bày các chỉ số ngoài độ chính xác tại K = 10 và RMSE của ba mô hình dự đoán điểm đại "
    "diện. RMSE được tính trên 8.060 cặp kiểm thử có nghệ sĩ trong danh mục; RMSE không áp dụng cho Random, "
    "Popularity, PureSVD, M1 và ALS vì điểm của các mô hình này không nằm trên thang 1–5."
)
rmse = {"user_cf": 0.9327, "item_cf": 0.9610, "svd": 1.2713}
COLS = [("catalog_coverage", max), ("gini", min), ("arp", min), ("novelty", max), ("ild", max)]
best = {c: fn(SIX, key=lambda m, c=c: tm(m, 10, c)) for c, fn in COLS}
best_rmse = min(rmse, key=rmse.get)
extra_rows = []
for m in ALL:
    cells = [
        pct(tm(m, 10, "catalog_coverage")),
        f(tm(m, 10, "gini"), 4),
        f(tm(m, 10, "arp"), 2),
        f(tm(m, 10, "novelty"), 3),
        f(tm(m, 10, "ild"), 4),
        f(rmse[m], 4) if m in rmse else "-",
    ]
    for j, (c, _) in enumerate(COLS):
        if best[c] == m:
            cells[j] = f"**{cells[j]}**"
    if m == best_rmse:
        cells[5] = f"**{cells[5]}**"
    extra_rows.append([NAMES[m]] + cells)
extra_rows.insert(6, ["Thực nghiệm bổ sung trên cùng giao thức", "", "", "", "", "", ""])
T(
    "Các chỉ số bổ sung trên tập kiểm thử (K = 10)",
    [2500, 1060, 1046, 1046, 1046, 1045, 1045],
    ["Mô hình", "Bao phủ ↑", "Gini ↓", "ARP ↓", "Độ mới ↑", "ILD ↑", "RMSE ↓"],
    extra_rows,
    note="Bao phủ tính trên 15.398 nghệ sĩ; độ mới tính bằng bit. Số in đậm là giá trị tốt nhất của từng cột theo chiều mũi tên, trong sáu mô hình đối sánh.",
)
P(
    "Bảng 4.7 trình bày NDCG@10 trung bình kèm khoảng tin cậy 95% của từng mô hình, và Bảng 4.8 trình bày "
    "kết quả kiểm định theo cặp. Phần trên của Bảng 4.8 là bốn cặp khai báo trước. Phần dưới là kiểm định "
    "bổ sung giữa PureSVD và từng mô hình đối sánh còn lại; họ này gồm năm cặp, nhưng hai cặp PureSVD − "
    "Popularity và PureSVD − SVD có độ lệch đã có ở phần trên (cặp sau ngược dấu) nên không in lại."
)
T(
    "NDCG@10 trung bình trên tập kiểm thử và khoảng tin cậy 95%",
    [3600, 1700, 3488],
    ["Mô hình", "NDCG@10", "Khoảng tin cậy 95%"],
    [[NAMES[m], f(means[m]["mean"]), ci(means[m])] for m in ALL],
    note="Bootstrap 1.000 lần theo người dùng, hạt giống 42, cùng một bộ chỉ số cho mọi mô hình; 1.855 người dùng.",
)
pair_rows = []
for a, b in [
    ("pure_svd", "popularity"),
    ("svd", "pure_svd"),
    ("m1", "pure_svd"),
    ("implicit_als", "pure_svd"),
]:
    r = pre[(a, b)]
    lab = lambda x: SHORT.get(x, NAMES[x])  # noqa: E731
    pair_rows.append(
        [
            f"{lab(a)} − {lab(b)}",
            "Khai báo trước",
            f(r["mean_difference"]),
            ci(r),
            f(r["rank_biserial"], 3),
            pv(r["holm_p"]),
        ]
    )
for b in ["random", "user_cf", "item_cf"]:
    r = fam[b]
    pair_rows.append(
        [
            f"PureSVD − {NAMES[b]}",
            "Bổ sung",
            f(r["mean_difference"]),
            ci(r),
            f(r["rank_biserial"], 3),
            pv(r["holm_p"]),
        ]
    )
T(
    "Kiểm định Wilcoxon theo cặp trên NDCG@10 của tập kiểm thử",
    [2350, 1250, 1200, 2088, 950, 950],
    ["Cặp (A − B)", "Họ kiểm định", "Chênh lệch", "Khoảng tin cậy 95%", "⟦r_rb⟧", "p (Holm)"],
    pair_rows,
    note=(
        "Họ khai báo trước có 4 cặp; họ bổ sung có 5 cặp PureSVD − {Random, Popularity, UserCF, ItemCF, SVD có độ lệch}, "
        "hiệu chỉnh Holm trên đủ 5 cặp. Hai cặp trùng với phần khai báo trước không in lại; p sau Holm của chúng trong họ "
        f"bổ sung lần lượt là {pv(fam['popularity']['holm_p'])} và {pv(fam['svd']['holm_p'])}."
    ),
    align=["left", "center", "center", "center", "center", "center"],
    size=22,
)
r_ps = pre[("pure_svd", "popularity")]
P(
    f"PureSVD nhị phân có NDCG@10 cao nhất trong sáu mô hình đối sánh ({f(pure)}), gấp khoảng "
    f"{f(pure / pop, 2)} lần Popularity ({f(pop)}). Chênh lệch với Popularity là "
    f"{f(r_ps['mean_difference'])}, khoảng tin cậy 95% {ci(r_ps)}, ⟦r_rb⟧ = {f(r_ps['rank_biserial'], 3)} và "
    "p sau hiệu chỉnh Holm nhỏ hơn 10⁻¹⁰, nên khác biệt có ý nghĩa thống kê và có cỡ hiệu ứng lớn. PureSVD "
    "cũng hơn có ý nghĩa mọi mô hình đối sánh còn lại trong kiểm định bổ sung. Thứ tự các mô hình trên tập "
    "kiểm thử giống trên tập xác thực."
)
u7, i7 = e7_pairs[("user_cf_e7", "PureSVD")], e7_pairs[("item_cf_e7", "PureSVD")]
P(
    "Popularity là đối chứng mạnh trên dữ liệu này: UserCF, ItemCF và SVD có độ lệch đều có NDCG@10 thấp "
    "hơn Popularity, trên cả tập xác thực và tập kiểm thử. Với SVD có độ lệch, Hình 4.1 cho thấy mục tiêu "
    "sai số bình phương không dẫn tới xếp hạng tốt; mô hình được chọn ở vòng 2 nên danh sách gần với mức "
    f"phổ biến (ARP {f(tm('svd', 10, 'arp'), 2)} so với {f(tm('popularity', 10, 'arp'), 2)} của Popularity) "
    "nhưng kém Popularity về độ chính xác. Với UserCF và ItemCF, danh sách nghiêng mạnh về nghệ sĩ ít phổ "
    f"biến (ARP {f(tm('user_cf', 10, 'arp'), 2)} và {f(tm('item_cf', 10, 'arp'), 2)}), trong khi đích kiểm "
    "thử lại tập trung vào nghệ sĩ được nhiều người nghe."
)
P(
    "Nguyên cách tổng hợp điểm là nguyên nhân chính: công thức (2.2) và (2.4) chia cho tổng độ tương đồng "
    "nên bỏ mất thông tin về số láng giềng cùng nghe, làm các nghệ sĩ chỉ có một người nghe trong nhóm láng "
    "giềng được xếp ngang hoặc cao hơn nghệ sĩ được nhiều láng giềng nghe. Thực nghiệm bổ sung E7 (mục 4.11) "
    "với biến thể tổng độ tương đồng (3.5), (3.6) cho NDCG@10 trên tập kiểm thử bằng "
    f"{f(e7.loc['item_cf'].ndcg)} với ItemCF và {f(e7.loc['user_cf'].ndcg)} với UserCF, vượt Popularity và "
    f"vượt cả PureSVD (p sau Holm {pv(i7['holm_p'])} và {pv(u7['holm_p'])}), qua đó khẳng định giả thuyết "
    "này. Kết quả của hai mô hình láng giềng trong Bảng 4.5 vì vậy phản ánh cách chấm điểm dự đoán, không "
    "phản ánh giới hạn của phương pháp láng giềng. Giữa hai mô hình láng giềng đã khóa, UserCF chính xác "
    "hơn ItemCF một chút ở K = 10 nhưng ItemCF phủ danh mục rộng hơn gấp đôi."
)
P(
    "Các chỉ số bổ sung cho thấy sự đánh đổi giữa độ chính xác và mức tập trung. Popularity và SVD có độ "
    "lệch phủ dưới 0,4% danh mục và có ARP trên 300. PureSVD chính xác nhất nhưng chỉ phủ "
    f"{pct(tm('pure_svd', 10, 'catalog_coverage'))} danh mục với Gini {f(tm('pure_svd', 10, 'gini'), 4)}. "
    "UserCF và ItemCF phủ rộng hơn nhiều nhưng độ chính xác thấp. Random có độ bao phủ và độ mới cao nhất "
    "nhưng gần như không gợi ý đúng. RMSE không thống nhất với thứ hạng: SVD có độ lệch có RMSE cao nhất "
    "trong ba mô hình dự đoán điểm, vì vòng của nó được chọn theo NDCG@10."
)
P(
    "Qua ba hạt giống 42, 43 và 44, NDCG@10 trên tập kiểm thử của SVD có độ lệch là "
    f"{f(seeds['svd']['at_k']['10']['ndcg']['mean'])} ± {f(seeds['svd']['at_k']['10']['ndcg']['sample_std'])}. "
    "PureSVD và M1 cho kết quả giống hệt ở cả ba hạt giống, vì hạt giống chỉ đổi véc-tơ khởi đầu của ARPACK "
    "và thuật toán hội tụ về cùng không gian con; do đó việc chạy lại hai mô hình này không phải là kiểm "
    "chứng độc lập. Trả lời RQ1: trong sáu mô hình đối sánh với cấu hình đã khóa, PureSVD nhị phân với "
    "k = 16 cho chất lượng xếp hạng tốt nhất và là mô hình cá nhân hóa duy nhất vượt Popularity; ba mô hình "
    "UserCF, ItemCF và SVD có độ lệch không vượt được Popularity. Kết luận về hai mô hình láng giềng phụ "
    "thuộc vào cách tổng hợp điểm: với cách tổng hợp top-N ở mục 4.11, cả hai vượt PureSVD."
)

H2("4.6 Phân tích theo độ dài lịch sử và theo từng người dùng")
hc = hist_ci.set_index(["mo_hinh", "nhom"])
n_lo = int(hist_ci[hist_ci.nhom == "Dưới 40"].so_nguoi.iloc[0])
n_hi = int(hist_ci[hist_ci.nhom == "Từ 40 trở lên"].so_nguoi.iloc[0])
P(
    "Như đã nêu ở mục 4.2, gần như mọi người dùng có đúng 40 tương tác huấn luyện. Trong 1.855 người dùng "
    f"có đích kiểm thử hợp lệ, nhóm dưới 40 chỉ có {n_lo} người và nhóm từ 40 trở lên có {num(n_hi)} người. "
    "Bảng 4.9 trình bày NDCG@10 của hai nhóm kèm khoảng tin cậy 95%. Khoảng tin cậy của nhóm dưới 40 rất "
    "rộng, nên bảng chỉ mang tính mô tả và không đủ để kết luận về ảnh hưởng của độ dài lịch sử. Ảnh hưởng "
    "này được khảo sát chủ động bằng thí nghiệm Given-N ở mục 4.8 và 4.11."
)
HL = [
    ("popularity", "Popularity"),
    ("user_cf", "UserCF"),
    ("item_cf", "ItemCF"),
    ("svd", "SVD có độ lệch"),
    ("pure_svd", "PureSVD"),
    ("m1", "M1"),
    ("implicit_als", "Implicit ALS"),
]
hist_rows = []
for m, lab in HL:
    lo, hi = hc.loc[(lab, "Dưới 40")], hc.loc[(lab, "Từ 40 trở lên")]
    hist_rows.append([NAMES[m], f(lo["mean"]), ci(lo), f(hi["mean"]), ci(hi)])
T(
    "NDCG@10 trên tập kiểm thử theo độ dài lịch sử huấn luyện",
    [2588, 1100, 2000, 1100, 2000],
    [
        "Mô hình",
        f"Dưới 40 ({n_lo} người)",
        "Khoảng tin cậy 95%",
        f"Từ 40 trở lên ({num(n_hi)} người)",
        "Khoảng tin cậy 95%",
    ],
    hist_rows,
    note="Bootstrap 1.000 lần theo người dùng trong từng nhóm, hạt giống 42.",
    size=22,
)
P(
    "Hình 4.2 trình bày phân bố NDCG@10 theo từng người dùng. Với mọi mô hình, phần lớn người dùng có "
    "NDCG@10 bằng 0 hoặc rất thấp, và trung bình được kéo lên bởi một nhóm người dùng tìm lại được nhiều "
    "đích. Hình 4.3 trình bày hiệu NDCG@10 của PureSVD trừ Popularity cho từng người dùng: "
    f"{num(split['improved'])} người dùng ({pct(split['improved'] / split['users'], 1)}) được cải thiện, "
    f"{split['equal']} người ({pct(split['equal'] / split['users'], 1)}) giữ nguyên, trong đó "
    f"{split['equal_both_zero']} người có NDCG@10 bằng 0 ở cả hai mô hình, và {split['worse']} người "
    f"({pct(split['worse'] / split['users'], 1)}) bị giảm."
)
F(
    BS + "hinh/hinh_4_4.png",
    "Phân bố NDCG@10 theo người dùng trên tập kiểm thử",
    note="Hình thoi là giá trị trung bình.",
)
F(BS + "hinh/hinh_4_5.png", "Hiệu NDCG@10 của PureSVD và Popularity theo từng người dùng")
msi = ms_ci.set_index(["mo_hinh", "nhom"])
lo_t, mid_t, hi_t = ec_tests["Thấp"], ec_tests["Trung bình"], ec_tests["Cao"]
P(
    "Theo gợi ý của Kowald và cộng sự [9], nhóm chia người dùng thành ba nhóm có cỡ mẫu gần bằng nhau theo "
    "mức ưa chuộng nghệ sĩ phổ biến, đo bằng số người nghe trung bình (trên tập huấn luyện) của các nghệ sĩ "
    "trong lịch sử huấn luyện của người dùng. Bảng 4.10 cho thấy mọi mô hình đều kém hơn rõ rệt ở nhóm ưa "
    "chuộng thấp. Popularity gần như không hữu ích cho nhóm này (NDCG@10 "
    f"{f(msi.loc[('Popularity', 'Thấp')]['mean'])} so với {f(msi.loc[('Popularity', 'Cao')]['mean'])} ở "
    f"nhóm cao). Ở nhóm thấp, ItemCF ({f(msi.loc[('ItemCF', 'Thấp')]['mean'])}) vượt Popularity, ngược với "
    "kết quả trung bình toàn bộ. Kiểm định Kruskal–Wallis giữa ba nhóm, hiệu chỉnh Holm trên tám mô hình, "
    f"có ý nghĩa với mọi mô hình trừ Random (p sau Holm {pv(kw.loc['Random', 'holm_p'])}) và ItemCF "
    f"({pv(kw.loc['ItemCF', 'holm_p'])})."
)
MS = [
    ("popularity", "Popularity"),
    ("user_cf", "UserCF"),
    ("item_cf", "ItemCF"),
    ("svd", "SVD có độ lệch"),
    ("pure_svd", "PureSVD"),
    ("m1", "M1"),
    ("implicit_als", "Implicit ALS"),
]
ranges = {"Thấp": "1,1–45,0", "Trung bình": "45,0–84,3", "Cao": "84,3–262,2"}
size = {g: int(ms_ci[ms_ci.nhom == g].so_nguoi.iloc[0]) for g in ranges}
ms_rows = []
for m, lab in MS:
    cells = [f"{f(msi.loc[(lab, g)]['mean'])} {ci(msi.loc[(lab, g)])}" for g in ranges]
    ms_rows.append([NAMES[m], *cells, pv(kw.loc[lab, "holm_p"])])
T(
    "NDCG@10 trên tập kiểm thử theo mức ưa chuộng nghệ sĩ phổ biến của người dùng",
    [1888, 1850, 1850, 1850, 1350],
    ["Mô hình"]
    + [f"{g} ({size[g]} người; {ranges[g]})" for g in ranges]
    + ["p (Holm) Kruskal–Wallis"],
    ms_rows,
    note="Mỗi ô ghi NDCG@10 trung bình và khoảng tin cậy 95% (bootstrap 1.000 lần trong từng nhóm, hạt giống 42). Khoảng trong tiêu đề cột là số người nghe trung bình của các nghệ sĩ trong lịch sử người dùng.",
    size=22,
)
P(
    "Kiểm định M1 − PureSVD riêng trong từng nhóm (hiệu chỉnh Holm trên ba nhóm) cho thấy hai hiệu ứng ngược "
    f"chiều. Ở nhóm ưa chuộng thấp, M1 cao hơn PureSVD {f(lo_t['mean_difference'])}, khoảng tin cậy 95% "
    f"{ci(lo_t)}, ⟦r_rb⟧ = {f(lo_t['rank_biserial'], 3)}, {pv_text(lo_t['holm_p'])} sau Holm. Ở nhóm trung "
    f"bình, chênh lệch là {f(mid_t['mean_difference'])} ({pv_text(mid_t['holm_p'])}). Ở nhóm cao, M1 thấp "
    f"hơn PureSVD {f(-hi_t['mean_difference'])}, khoảng tin cậy {ci(hi_t)}, {pv_text(hi_t['holm_p'])}. Như "
    "vậy M1 giúp người dùng ít ưa chuộng nghệ sĩ phổ biến tìm lại được nhiều đích hơn, đổi lại một phần độ "
    "chính xác ở nhóm ưa chuộng cao; hai hiệu ứng này gần bù trừ nhau trên toàn bộ người dùng (mục 4.7). "
    "Đây là phân tích sau khi đã mở tập kiểm thử nên được xem là bằng chứng bổ sung."
)

H2("4.7 Đánh giá mô-đun tái xếp hạng M1")
grid_base = m1_grid[(m1_grid["lambda"] == 1) & (m1_grid.beta == 0)].iloc[0]
within = int((m1_grid.ndcg >= 0.95 * grid_base.ndcg).sum())
new_pts = eb[eb.nguon == "mo_rong"]
P(
    "M1 được áp dụng trên 100 ứng viên đầu của PureSVD nhị phân k = 16. Lưới tham số gồm λ ∈ {0,5; 0,75; 1} "
    "và β ∈ {0; 0,1; 0,25; 0,5}. Theo quy tắc chọn đặt trước ở mục 3.7.3, trong các biến thể đầy đủ có mức "
    "giảm NDCG@10 xác thực không quá 5% so với mô hình nền, biến thể có ARP thấp nhất được chọn, sau đó xét "
    f"ILD cao nhất rồi NDCG cao nhất; cấu hình được chọn là λ = 0,75 và β = 0,5. {within} trên 12 điểm của "
    "lưới nằm trong ngưỡng giảm 5%."
)
P(
    "Hình 4.4 trình bày 12 điểm của lưới cùng 12 điểm mở rộng với β ∈ {0,75; 1; 1,5; 2} (E9), chỉ đo trên "
    "tập xác thực sau khi đã khóa cấu hình. Đường đánh đổi cho thấy tăng β làm ARP giảm đều, còn giảm λ "
    f"xuống 0,5 làm NDCG@10 giảm nhanh khi β lớn. Trong 12 điểm mở rộng, chỉ "
    f"{int((~new_pts.duoi_nguong_5pct).sum())} điểm còn nằm trong ngưỡng 5%: λ = 0,75, β = 0,75 và λ = 1, "
    "β = 0,75 hoặc 1. Đường đánh đổi cắt ngưỡng giữa β = 0,75 và β = 1 khi λ = 0,75. Nếu áp dụng cùng quy "
    "tắc chọn trên lưới mở rộng, cấu hình được chọn sẽ là λ = 0,75, β = 0,75 (NDCG@10 xác thực "
    f"{f(eb[(eb['lambda'] == 0.75) & (eb.beta == 0.75)].ndcg.iloc[0])}, ARP "
    f"{f(eb[(eb['lambda'] == 0.75) & (eb.beta == 0.75)].arp.iloc[0], 2)}). Điều này xác nhận β = 0,5 được "
    "chọn do giới hạn của lưới; cấu hình đã khóa không thay đổi vì tập kiểm thử đã mở."
)
F(
    B2 + "e_b/hinh_4_6.png",
    "Đánh đổi giữa NDCG@10 và ARP của các cấu hình M1 trên tập xác thực",
    note="Điểm màu xanh là 12 cấu hình của lưới đã khóa, điểm màu cam là 12 cấu hình β mở rộng (phân tích sau khi khóa); điểm rỗng nằm dưới ngưỡng. Đường nét đứt là ngưỡng giảm 5% NDCG@10 so với mô hình nền (λ = 1, β = 0).",
)
P(
    "Bảng 4.11 so sánh bốn biến thể trên tập kiểm thử: mô hình nền, chỉ thành phần đa dạng, chỉ phạt phổ "
    "biến và M1 đầy đủ. Quy tắc chọn chỉ dùng tập xác thực; ba biến thể ngoài M1 đầy đủ được chấm trên tập "
    "kiểm thử sau khi tập này đã mở, nên đây là phân tích bổ sung và không dùng để chọn lại cấu hình. Cột "
    "ILD theo thẻ là độ đa dạng tính bằng côsin giữa véc-tơ TF–IDF thẻ của hai nghệ sĩ, dựng theo cùng cách "
    f"với M2 trên toàn bộ tập huấn luyện ({num(ild_models['tag_features']['vocabulary_size'])} thẻ, "
    f"{num(ild_models['tag_features']['tagged_catalog_artists'])} trong 15.398 nghệ sĩ có thẻ), chỉ tính "
    "trên các cặp nghệ sĩ đều có thẻ; cả 1.855 danh sách đều có ít nhất một cặp như vậy."
)
VAR = [
    ("nen", "Mô hình nền (λ = 1; β = 0)"),
    ("chi_da_dang", "Chỉ đa dạng (λ = 0,75; β = 0)"),
    ("chi_phat_pho_bien", "Chỉ phạt phổ biến (λ = 1; β = 0,5)"),
    ("m1_day_du", "M1 đầy đủ (λ = 0,75; β = 0,5)"),
]
base_v = variants.loc["nen"]
var_rows = []
for key, label in VAR:
    v = variants.loc[key]
    delta = "0" if key == "nen" else f((v.ndcg / base_v.ndcg - 1) * 100, 2) + "%"
    var_rows.append(
        [
            label,
            f(v.ndcg),
            delta,
            f(v.arp, 2),
            pct(v.catalog_coverage),
            f(v.ild, 4),
            f(v.ild_tag, 4),
        ]
    )
T(
    "Kết quả loại bỏ thành phần của M1 trên tập kiểm thử (K = 10)",
    [2600, 1100, 1000, 1000, 1030, 1029, 1029],
    ["Biến thể", "NDCG@10", "Δ NDCG", "ARP ↓", "Bao phủ ↑", "ILD ↑", "ILD theo thẻ ↑"],
    var_rows,
)
v_full = variants.loc["m1_day_du"]
t_full = pre[("m1", "pure_svd")]
t_div, t_pop = m1_tests["m1_chi_da_dang"], m1_tests["m1_chi_phat_pho_bien"]
P(
    "Khi diễn giải Bảng 4.11 cần lưu ý rằng hàm lựa chọn của M1 dùng cùng độ tương đồng côsin trên véc-tơ "
    "người nghe nhị phân với chỉ số ILD, và dùng số người nghe trên tập huấn luyện, cũng là đại lượng tạo "
    "nên ARP. Vì vậy, việc ILD tăng và ARP giảm khi bật các thành phần tương ứng phần lớn là hệ quả trực "
    "tiếp của hàm mục tiêu, không phải bằng chứng độc lập. Các thước đo không tham gia hàm lựa chọn cho thấy "
    f"mức cải thiện thật nhỏ hơn: ILD theo thẻ của M1 đầy đủ tăng từ {f(base_v.ild_tag, 4)} lên "
    f"{f(v_full.ild_tag, 4)} (so với mức tăng ILD theo người nghe từ {f(base_v.ild, 4)} lên {f(v_full.ild, 4)}), "
    "còn biến thể chỉ phạt phổ biến làm ILD theo thẻ giảm nhẹ xuống "
    f"{f(variants.loc['chi_phat_pho_bien'].ild_tag, 4)}. Độ bao phủ tăng từ {pct(base_v.catalog_coverage)} "
    f"lên {pct(v_full.catalog_coverage)} và Gini giảm từ {f(base_v.gini, 4)} xuống {f(v_full.gini, 4)}, "
    "nhưng danh sách vẫn tập trung vào một phần rất nhỏ danh mục."
)
P(
    f"Về độ chính xác, M1 đầy đủ thấp hơn mô hình nền {f(-t_full['mean_difference'])} NDCG@10 (khoảng tin cậy "
    f"95% {ci(t_full)}, ⟦r_rb⟧ = {f(t_full['rank_biserial'], 3)}, p sau Holm {pv(t_full['holm_p'])} trong họ "
    "bốn cặp khai báo trước), nên chưa phát hiện được khác biệt có ý nghĩa thống kê. Trong kiểm định bổ "
    "sung của hai biến thể còn lại so với mô hình nền (hiệu chỉnh Holm trong họ ba cặp), chỉ đa dạng có "
    f"chênh lệch {f(t_div['mean_difference'])} với khoảng tin cậy 95% {ci(t_div)} và p sau Holm "
    f"{pv(t_div['holm_p'])}; chỉ phạt phổ biến có p sau Holm {pv(t_pop['holm_p'])}. Khoảng tin cậy của biến "
    "thể chỉ đa dạng không chứa 0 nhưng p sau Holm lớn hơn 0,05 vì khoảng tin cậy bootstrap không được hiệu "
    "chỉnh cho nhiều phép so sánh (mục 2.6). Trên tập xác thực, M1 đầy đủ tăng NDCG@10 0,52%, còn trên tập "
    "kiểm thử giảm 0,75%."
)
P(
    "Một kết quả không có ý nghĩa thống kê chưa đủ để nói M1 giữ được độ chính xác. Nhóm dùng kiểm định tương "
    "đương TOST (2.31) với biên đã đặt trước ở mục 3.7.3, tức mức giảm tương đối tối đa 5% so với NDCG@10 "
    "của mô hình nền:"
)
EQ(860, "4.1")
P(
    f"Khoảng tin cậy 90% của chênh lệch M1 − PureSVD là [{f(tost['ci90'][0])}; {f(tost['ci90'][1])}], nằm "
    f"trọn trong khoảng (−{f(tost['delta'])}; {f(tost['delta'])}), nên giả thuyết không tương đương bị bác bỏ "
    "ở mức ý nghĩa 0,05."
)
ex_user = examples.user_id.iloc[0]
ex = examples[examples.user_id == ex_user]
P(
    f"Bảng 4.12 minh họa danh sách 10 nghệ sĩ của người dùng mã {ex_user} trước và sau M1. M1 thay một số "
    "nghệ sĩ rất phổ biến bằng nghệ sĩ có ít người nghe hơn nhưng gần với lịch sử của người dùng, đồng thời "
    "đổi thứ tự trong phần giữ lại. Ví dụ này được lấy là người dùng đầu tiên theo mã có ít nhất ba nghệ sĩ "
    "khác nhau giữa hai danh sách, không chọn theo kết quả."
)
T(
    f"Danh sách gợi ý của người dùng {ex_user} trước và sau M1 (tập kiểm thử)",
    [850, 2944, 1350, 2294, 1350],
    ["Hạng", "PureSVD", "Số người nghe", "M1", "Số người nghe"],
    [
        [
            str(r.hang),
            r.puresvd + (" (đúng)" if r.puresvd_dung else ""),
            str(r.puresvd_nguoi_nghe),
            r.m1 + (" (đúng)" if r.m1_dung else ""),
            str(r.m1_nguoi_nghe),
        ]
        for r in ex.itertuples()
    ],
    note="“(đúng)” là nghệ sĩ thuộc tập đích kiểm thử của người dùng; số người nghe tính trên tập huấn luyện.",
    align=["center", "left", "center", "left", "center"],
)
arp_drop = (1 - v_full.arp / base_v.arp) * 100
ndcg_drop = (1 - v_full.ndcg / base_v.ndcg) * 100
P(
    f"Trả lời RQ3: so với mô hình nền trên tập kiểm thử, M1 giảm ARP@10 {f(arp_drop, 2)}% (từ "
    f"{f(base_v.arp, 2)} xuống {f(v_full.arp, 2)}) và tăng độ bao phủ từ {pct(base_v.catalog_coverage)} lên "
    f"{pct(v_full.catalog_coverage)}, trong khi chênh lệch NDCG@10 là {f(t_full['mean_difference'])} với "
    f"khoảng tin cậy 90% [{f(tost['ci90'][0])}; {f(tost['ci90'][1])}] nằm trọn trong biên tương đương "
    f"±{f(tost['delta'])} (5% NDCG@10 của mô hình nền) đã đặt trước ở mục 3.7.3. Do đó M1 tương đương mô "
    "hình nền về độ chính xác ở biên đã chọn. Mức tăng đa dạng đo bằng thước đo độc lập theo thẻ (từ "
    f"{f(base_v.ild_tag, 4)} lên {f(v_full.ild_tag, 4)}) nhỏ hơn mức tăng đo bằng ILD theo người nghe, vì ILD "
    "theo người nghe dùng chung độ tương đồng với hàm lựa chọn của M1. Phân tích theo nhóm ở mục 4.6 cho "
    "thấy M1 cải thiện độ chính xác cho người dùng ít ưa chuộng nghệ sĩ phổ biến."
)

H2("4.8 Đánh giá mô-đun dự phòng M2")
P(
    "M2 được đánh giá theo giao thức người dùng mới ở mục 3.8.4. Người dùng của tập huấn luyện được chia "
    "thành nhóm học (1.501 người), nhóm tinh chỉnh (187 người) và nhóm để dành (189 người); mọi thành phần "
    "của M2 chỉ học từ nhóm học, với danh mục 13.210 nghệ sĩ. Với mỗi người dùng đánh giá, hệ thống chỉ nhận "
    "N ∈ {0, 1, 3, 5} nghệ sĩ từ lịch sử huấn luyện của chính họ, các hồ sơ lồng nhau theo một thứ tự xáo "
    "cố định. Trên tập xác thực của nhóm tinh chỉnh, cấu hình được chọn là α = "
    f"{f(m2_sel['winner']['alpha'], 2)} và n_min = {m2_sel['winner']['history_threshold']}, với NDCG@10 "
    f"trung bình ở N = 1, 3, 5 bằng {f(m2_sel['winner']['mean_ndcg_at_10'])}. Cấu hình này nằm ở góc của "
    "lưới, nghĩa là ở N ≤ 5 phần dự phòng chủ yếu dựa vào nội dung thẻ (Bảng 3.6). Bảng 4.13 trình bày "
    "NDCG@10 trên tập kiểm thử của nhóm để dành, chấm một lần sau khi khóa cấu hình; tập đích là các cặp "
    "kiểm thử của người dùng giao với danh mục học. 187 trên 189 người có đích trong danh mục và 14,59% cặp "
    "kiểm thử của nhóm này nằm ngoài danh mục học."
)
LAB = [
    ("popularity", "Popularity"),
    ("item_cf", "Chỉ ItemCF (L = 40)"),
    ("content", "Chỉ nội dung thẻ"),
    ("m2", "M2 (α = 0,75; n_min = 10)"),
]
T(
    "NDCG@10 theo số nghệ sĩ được cung cấp (Given-N) trên nhóm để dành",
    [3188, 1400, 1400, 1400, 1400],
    ["Phương án", "N = 0", "N = 1", "N = 3", "N = 5"],
    [
        [label]
        + [f(float(m2[(m2.method == meth) & (m2.n == n)].ndcg.iloc[0])) for n in [0, 1, 3, 5]]
        for meth, label in LAB
    ],
    note="Kết quả tại K = 10 được tính trên 187 người dùng có nghệ sĩ đích trong danh mục.",
)
F(BS + "hinh/hinh_4_7.png", "NDCG@10 theo số nghệ sĩ được cung cấp của các phương án M2")
P(
    "Bảng 4.14 thống kê tần suất các đường xử lý của M2 ở từng mức N trên 189 người để dành: tỷ lệ yêu cầu "
    "có điểm nội dung, tỷ lệ chuyển hoàn toàn về mức phổ biến (không có điểm nội dung lẫn điểm cộng tác) và "
    "số nghệ sĩ đầu vào nằm ngoài ánh xạ của nhóm học."
)
T(
    "Tần suất các đường xử lý của M2",
    [3988, 1200, 1200, 1200, 1200],
    ["Thống kê", "N = 0", "N = 1", "N = 3", "N = 5"],
    [
        ["Có điểm nội dung (%)"]
        + [f(paths.loc[n, "co_diem_noi_dung_pct"], 2) for n in [0, 1, 3, 5]],
        ["Chuyển hoàn toàn về phổ biến (%)"]
        + [f(paths.loc[n, "chuyen_hoan_toan_pho_bien_pct"], 2) for n in [0, 1, 3, 5]],
        ["Nghệ sĩ đầu vào ngoài ánh xạ (số lượng)"]
        + [str(int(paths.loc[n, "nghe_si_dau_vao_ngoai_anh_xa"])) for n in [0, 1, 3, 5]],
        ["Tổng số nghệ sĩ đầu vào"] + [str(189 * n) for n in [0, 1, 3, 5]],
    ],
)
s3p = m2_stats[(3, "popularity")]
P(
    "Bảng 4.15 trình bày kiểm định của M2 so với từng phương án thành phần. Ở N = 0, mọi phương án trả đúng "
    "thứ tự Popularity nên có cùng giá trị NDCG@10; đây là kiểm tra tính đúng của cài đặt. Ở N = 1, 3, 5, "
    "phương án chỉ dùng mức phổ biến có NDCG@10 cao nhất. Ở so sánh chính (N = 3), M2 thấp hơn Popularity "
    f"{f(-s3p['mean_difference'])}, khoảng tin cậy 95% {ci(s3p)}, ⟦r_rb⟧ = {f(s3p['rank_biserial'], 3)}, p sau "
    f"Holm {pv(s3p['holm_p'])}. Bảng 4.14 giải thích một phần kết quả ở N = 1: "
    f"{int(paths.loc[1, 'nghe_si_dau_vao_ngoai_anh_xa'])} trên 189 người dùng có nghệ sĩ duy nhất nằm ngoài "
    f"ánh xạ, đúng bằng {f(paths.loc[1, 'chuyen_hoan_toan_pho_bien_pct'], 2)}% yêu cầu phải chuyển hoàn toàn "
    "về mức phổ biến."
)
st_rows = []
for n in [1, 3, 5]:
    for b, lab in [
        ("popularity", "Popularity"),
        ("content", "Chỉ nội dung thẻ"),
        ("item_cf", "Chỉ ItemCF"),
    ]:
        r = m2_stats[(n, b)]
        cells = [
            str(n),
            f"M2 − {lab}" + (" (chính)" if (n, b) == (3, "popularity") else ""),
            f(r["mean_difference"]),
            ci(r),
            f(r["rank_biserial"], 3),
            pv(r["holm_p"]),
        ]
        if (n, b) == (3, "popularity"):
            cells = [f"**{c}**" for c in cells]
        st_rows.append(cells)
T(
    "Kiểm định NDCG@10 của M2 trên tập kiểm thử (187 người dùng)",
    [550, 2800, 1250, 2188, 1000, 1000],
    ["N", "Cặp (A − B)", "Chênh lệch", "Khoảng tin cậy 95%", "⟦r_rb⟧", "p (Holm)"],
    st_rows,
    note="Chín cặp khai báo trước, hiệu chỉnh Holm trên cả chín cặp; bootstrap dùng chung một bộ chỉ số cho mọi cặp.",
    align=["center", "left", "center", "center", "center", "center"],
    size=22,
)
m2_n3 = m2[m2.n == 3].set_index("method")
s5i = m2_stats[(5, "item_cf")]
P(
    "Kết quả trên tập xác thực và tập kiểm thử lệch nhau rõ. Trên 187 người tinh chỉnh, mức phổ biến chỉ đạt "
    "NDCG@10 từ 0,027627 đến 0,029728, còn trên 189 người để dành đạt từ 0,056508 đến 0,059750. Hai nhóm "
    "người dùng khác nhau và mỗi nhóm chưa tới 200 người, nên độ chính xác của cùng một phương pháp dao động "
    "mạnh giữa hai nhóm; cấu hình M2 chọn trên nhóm đầu không giữ được ưu thế ở nhóm sau. M2 vẫn có tác dụng "
    f"về đa dạng: ở N = 3, M2 tăng độ bao phủ từ {pct(m2_n3.loc['popularity'].catalog_coverage)} lên "
    f"{pct(m2_n3.loc['m2'].catalog_coverage)} và giảm ARP từ {f(m2_n3.loc['popularity'].arp, 2)} xuống "
    f"{f(m2_n3.loc['m2'].arp, 2)} so với Popularity. Trong các thành phần, nội dung thẻ đóng góp nhiều nhất "
    "khi hồ sơ dài hơn: M2 hơn phương án chỉ dùng nội dung ở N = 1 có ý nghĩa (p sau Holm "
    f"{pv(m2_stats[(1, 'content')]['holm_p'])}), còn thành phần ItemCF yếu dần khi N tăng."
)
P(
    f"Ở N = 5, cặp M2 − Chỉ ItemCF có khoảng tin cậy 95% {ci(s5i)} không chứa 0 nhưng p sau Holm bằng "
    f"{pv(s5i['holm_p'])}. Hai kết quả không mâu thuẫn: họ kiểm định gồm chín cặp nên giá trị p được hiệu "
    "chỉnh cho nhiều phép so sánh, còn khoảng tin cậy bootstrap của từng cặp thì không (mục 2.6). Bảng 3.6 "
    "giải thích trực tiếp kết quả âm của M2: với n_min = 10, ở N ≤ 5 M2 chủ yếu là mô hình nội dung, thành "
    "phần phổ biến chỉ chiếm 12,5–22,5% trọng số, trong khi trên nhóm để dành Popularity lại là phương án "
    "mạnh nhất."
)
P(
    "Trả lời RQ4 theo giao thức đã khóa: chưa tìm thấy bằng chứng M2 hỗ trợ người dùng ít lịch sử tốt hơn mức "
    "phổ biến về độ chính xác; M2 không vượt Popularity ở N nào trên tập kiểm thử, dù tăng độ bao phủ và "
    "giảm ARP. Về RQ2, khi số nghệ sĩ được cung cấp tăng từ 1 lên 3, NDCG@10 của M2 tăng từ "
    f"{f(float(m2[(m2.method == 'm2') & (m2.n == 1)].ndcg.iloc[0]))} lên "
    f"{f(float(m2[(m2.method == 'm2') & (m2.n == 3)].ndcg.iloc[0]))}, nhưng không tăng thêm ở N = 5 "
    f"({f(float(m2[(m2.method == 'm2') & (m2.n == 5)].ndcg.iloc[0]))}); phương án chỉ dùng nội dung tăng đều "
    "theo N, còn phương án chỉ dùng ItemCF giảm. Với cỡ mẫu 187 người và khoảng năm đích mỗi người, các xu "
    "hướng này chỉ mang tính mô tả. Mục 4.11 trình bày kết quả của cùng mô hình M2 khi tập đích gồm toàn bộ "
    "nghệ sĩ không được cung cấp theo (3.14); với tập đích này, kết luận về RQ4 thay đổi."
)

H2("4.9 Thực nghiệm mở rộng với implicit ALS")
r_als = pre[("implicit_als", "pure_svd")]
P(
    "Implicit ALS [8] được cài đặt bằng thư viện implicit 0.7.3 [30], với độ tin cậy (2.11) a = 1, 32 nhân "
    "tố, hệ số điều chuẩn 0,1 và vòng tốt nhất là vòng 16 theo NDCG@10 xác thực. Khác với SVD có độ lệch, "
    "hàm mất mát (2.12) của ALS đưa cả các ô chưa quan sát vào với độ tin cậy thấp, nên phù hợp hơn với dữ "
    f"liệu phản hồi ngầm. Trên tập kiểm thử, ALS đạt NDCG@10 {f(tm('implicit_als', 10, 'ndcg'))}, cao hơn "
    f"PureSVD {f(r_als['mean_difference'])} với khoảng tin cậy 95% {ci(r_als)}, ⟦r_rb⟧ = "
    f"{f(r_als['rank_biserial'], 3)} và p sau Holm {pv(r_als['holm_p'])}. ALS cũng có độ bao phủ cao hơn "
    f"({pct(tm('implicit_als', 10, 'catalog_coverage'))} so với {pct(tm('pure_svd', 10, 'catalog_coverage'))}) "
    f"và ARP thấp hơn ({f(tm('implicit_als', 10, 'arp'), 2)} so với {f(tm('pure_svd', 10, 'arp'), 2)}). Qua ba "
    f"hạt giống, NDCG@10 của ALS là {f(seeds['implicit_als']['at_k']['10']['ndcg']['mean'])} ± "
    f"{f(seeds['implicit_als']['at_k']['10']['ndcg']['sample_std'])}."
)
P(
    "Lưới của ALS chỉ có 8 cấu hình và cấu hình được chọn nằm ở biên ở cả ba chiều, nên 0,217453 chưa chắc "
    "là mức tốt nhất của ALS trên dữ liệu này. Phân tích độ nhạy ở mục 4.11 (Bảng 4.19) kiểm tra các hướng ra "
    "ngoài biên (ít nhân tố hơn, a_conf nhỏ hơn, reg lớn hơn) trên tập xác thực: không cấu hình nào tốt hơn "
    "cấu hình đã chọn, nên giới hạn này không làm thay đổi kết luận về ALS theo các hướng đã thử. Dù ALS tốt hơn PureSVD có ý nghĩa thống kê, nhóm vẫn giữ PureSVD làm mô hình nền "
    "của M1: M1 được thiết kế, tinh chỉnh và khóa trên PureSVD trước khi mở tập kiểm thử, nên chuyển M1 sang "
    "ALS sau khi đã thấy kết quả kiểm thử sẽ là một lần chọn hậu kiểm."
)
P(
    "Nhóm có thử thêm một hướng giảm thiên lệch phổ biến trên ALS, chỉ trên tập xác thực: trừ khỏi ma trận "
    "điểm ALS thành phần ứng với giá trị suy biến lớn nhất của nó (thành phần này có hệ số tương quan hạng "
    "Spearman 0,737 với số người nghe của nghệ sĩ), với mức trừ chung hoặc theo từng người dùng, 11 cấu "
    "hình. Cả sáu cấu hình phổ còn nằm trong ngưỡng giảm 5% NDCG@10 đều bị một cấu hình phạt phổ biến trực "
    "tiếp trên ALS trội hơn, tức có NDCG@10 không thấp hơn và tỷ lệ vị trí dành cho nghệ sĩ ngoài nhóm phổ "
    "biến nhất cao hơn. Ví dụ, phạt trực tiếp với β = 0,25 đạt NDCG@10 xác thực 0,194903, còn cấu hình phổ "
    "gần nhất đạt 0,193040 với tỷ lệ vị trí ngoài nhóm phổ biến thấp hơn. Vì vậy hướng này dừng ở tập xác "
    "thực và không được chấm trên tập kiểm thử. Áp dụng M1 trên ALS và chấm bằng một lần chia mới là hướng "
    "phát triển. Ứng dụng ở Chương 5 cho phép chọn cả PureSVD, M1 và ALS."
)

H2("4.10 Chi phí xử lý")
P(
    "Bảng 4.16 so sánh thời gian huấn luyện, thời gian tạo danh sách gợi ý và dung lượng mô hình của cấu "
    "hình đã chọn, đo trong lần chạy trên tập xác thực với một luồng tính toán trên máy đám mây. Thời gian "
    "tạo gợi ý là trung bình trên một người dùng. Các số này mô tả cấp độ chi phí trên một máy cụ thể, không "
    "phải phép đo hiệu năng có kiểm soát."
)
COST = [
    ("random", "Random"),
    ("popularity", "Popularity"),
    ("user_cf", "UserCF"),
    ("item_cf", "ItemCF"),
    ("svd", "SVD có độ lệch"),
    ("pure_svd", "PureSVD"),
    ("implicit_als", "Implicit ALS"),
]
cost_rows = [
    [
        lab,
        f(cost.loc[m, "fit_seconds"], 2),
        f(cost.loc[m, "recommend_mean_ms_per_user"], 2),
        f(cost.loc[m, "model_bytes"] / 1e6, 2),
    ]
    for m, lab in COST
]
cost_rows.append(
    [
        "PureSVD + M1",
        "0 (dùng lại PureSVD)",
        f"{f(cost.loc['m1', 'candidate_mean_ms_per_user'], 2)} lấy ứng viên + {f(cost.loc['m1', 'rerank_mean_ms_per_user'], 2)} tái xếp hạng",
        f"{f(cost.loc['m1', 'model_bytes'] / 1e6, 2)} cộng mô hình nền",
    ]
)
T(
    "Chi phí huấn luyện và suy luận",
    [2200, 2000, 2788, 1800],
    [
        "Mô hình",
        "Thời gian huấn luyện (s)",
        "Thời gian gợi ý / người dùng (ms)",
        "Dung lượng mô hình (MB)",
    ],
    cost_rows,
    note="1 MB = 1.000.000 byte.",
)
P(
    "PureSVD có chi phí thấp: huấn luyện dưới 0,2 giây và khoảng 2 ms cho mỗi danh sách gợi ý. SVD có độ "
    "lệch tốn thời gian huấn luyện nhất vì dùng SGD tuần tự trên từng cặp quan sát. M1 không cần huấn luyện "
    "lại mô hình nền; chi phí chính là lấy 100 ứng viên, còn bước tái xếp hạng chỉ khoảng 0,2 ms."
)

H2("4.11 Phân tích bổ sung sau khi khóa cấu hình")
P(
    "Các phân tích trong mục này được thực hiện sau khi tập kiểm thử đã mở cho các thực nghiệm chính, theo "
    "góp ý về cách tổng hợp điểm của mô hình láng giềng, giới hạn của lưới tìm kiếm và tập đích của giao "
    "thức Given-N. Mọi lựa chọn cấu hình mới chỉ dùng tập xác thực; các cấu hình đã khóa ở mục 4.4 đến 4.8 "
    "không thay đổi. Vì đã biết kết quả kiểm thử của các thực nghiệm chính, kết quả ở đây là bằng chứng bổ "
    "sung, không thay thế kết quả đã khóa."
)
H3("4.11.1 Mô hình láng giềng với cách tổng hợp top-N (E7)")
uw, iw = e7_sel["user_cf"], e7_sel["item_cf"]
uv = e7_val[e7_val.model == "user_cf"].validation_ndcg_at_10
iv = e7_val[e7_val.model == "item_cf"].validation_ndcg_at_10
P(
    "E7 đánh giá UserCF và ItemCF theo (3.5) và (3.6) trên lưới 20 cấu hình cho mỗi mô hình. Trên tập xác "
    f"thực, NDCG@10 của UserCF nằm trong khoảng {f(uv.min())}–{f(uv.max())} và của ItemCF trong khoảng "
    f"{f(iv.min())}–{f(iv.max())}, so với 0,017488 và 0,015364 của hai mô hình dùng cách tổng hợp trung bình "
    f"đã khóa. Cấu hình được chọn của UserCF là biểu diễn log-count, L = {uw['selected']['neighbors']}, "
    f"γ = {uw['selected']['shrinkage']} (NDCG@10 xác thực {f(uw['validation_ndcg_at_10_seed42'])}); của ItemCF "
    f"là log-count, L = {iw['selected']['neighbors']}, γ = {iw['selected']['shrinkage']} "
    f"({f(iw['validation_ndcg_at_10_seed42'])}). Bảng 4.17 trình bày kết quả trên tập kiểm thử sau khi khóa "
    "hai cấu hình này."
)
e7_rows = []
for model, lab in [("user_cf", "UserCF top-N"), ("item_cf", "ItemCF top-N")]:
    r = e7.loc[model]
    e7_rows.append(
        [
            lab,
            f(r.ndcg),
            f(r.precision),
            f(r.recall),
            pct(r.catalog_coverage),
            f(r.arp, 2),
            f(r.ild, 4),
        ]
    )
for m in ["popularity", "pure_svd", "implicit_als"]:
    e7_rows.append(
        [
            SHORT.get(m, NAMES[m]),
            f(tm(m, 10, "ndcg")),
            f(tm(m, 10, "precision")),
            f(tm(m, 10, "recall")),
            pct(tm(m, 10, "catalog_coverage")),
            f(tm(m, 10, "arp"), 2),
            f(tm(m, 10, "ild"), 4),
        ]
    )
T(
    "Kết quả của mô hình láng giềng top-N trên tập kiểm thử (K = 10)",
    [2188, 1300, 1100, 1100, 1050, 1000, 1050],
    ["Mô hình", "NDCG@10", "P@10", "R@10", "Bao phủ", "ARP", "ILD"],
    e7_rows,
    note="Ba dòng cuối là các mô hình đã khóa ở Bảng 4.5 và 4.6, đưa vào để so sánh trên cùng 1.855 người dùng.",
)
e7_rows2 = []
for (a, b), r in e7_pairs.items():
    lab = "UserCF top-N" if a.startswith("user") else "ItemCF top-N"
    e7_rows2.append(
        [f"{lab} − {b}", f(r["mean_difference"]), ci(r), f(r["rank_biserial"], 3), pv(r["holm_p"])]
    )
T(
    "Kiểm định NDCG@10 của mô hình láng giềng top-N trên tập kiểm thử",
    [3088, 1300, 2400, 1000, 1000],
    ["Cặp (A − B)", "Chênh lệch", "Khoảng tin cậy 95%", "⟦r_rb⟧", "p (Holm)"],
    e7_rows2,
    note="Họ E7 gồm bốn cặp, hiệu chỉnh Holm trong họ; bootstrap 1.000 lần, hạt giống 42, cùng một bộ chỉ số cho mọi cặp.",
    align=["left", "center", "center", "center", "center"],
    size=22,
)
P(
    f"Cả hai mô hình top-N vượt Popularity với cỡ hiệu ứng lớn (⟦r_rb⟧ khoảng 0,88) và vượt PureSVD khoảng "
    f"{f(u7['mean_difference'])} đến {f(i7['mean_difference'])} NDCG@10 với cỡ hiệu ứng nhỏ (⟦r_rb⟧ "
    f"{f(u7['rank_biserial'], 3)} và {f(i7['rank_biserial'], 3)}); hai khác biệt với PureSVD có ý nghĩa sau "
    "Holm. Implicit ALS vẫn có NDCG@10 cao nhất trong các mô hình đã đo. Như vậy, kết luận RQ1 rằng "
    "UserCF và ItemCF không vượt Popularity chỉ đúng với cách tổng hợp trung bình có trọng số; với cách "
    "tổng hợp phù hợp bài toán top-N, mô hình láng giềng là đối thủ mạnh trên dữ liệu này, phù hợp với "
    "nhận xét của Cremonesi và cộng sự [13]."
)
H3("4.11.2 Độ nhạy ngoài biên lưới (E8)")
es_rows = []
lock_val = {
    "pure_svd": "k = 16: 0,166611",
    "user_cf": "L = 20, γ = 0: 0,017488",
    "item_cf": "L = 20, γ = 0: 0,015364",
    "implicit_als": "32 nhân tố, reg 0,1, a_conf 1: 0,197433",
}
for model, lab in [
    ("pure_svd", "PureSVD"),
    ("user_cf", "UserCF"),
    ("item_cf", "ItemCF"),
    ("implicit_als", "Implicit ALS"),
]:
    sub = es[es.model == model].drop_duplicates(subset="run")
    for k, r in enumerate(sub.itertuples()):
        if model == "pure_svd":
            cfg = f"k = {int(r.latent_factors)}"
        elif model == "implicit_als":
            cfg = f"{int(r.latent_factors)} nhân tố, reg {f(r.regularization, 1).rstrip('0').rstrip(',')}, a_conf {f(r.confidence_scale, 1).rstrip('0').rstrip(',')}"
        else:
            cfg = f"L = {int(r.neighbors)}, γ = {int(r.shrinkage)}"
        es_rows.append(
            [lab if k == 0 else "", cfg, f(r.ndcg_at_10), lock_val[model] if k == 0 else ""]
        )
best_m2 = es_m2.loc[es_m2.mean_ndcg_at_10_n135.idxmax()]
for r in es_m2.itertuples():
    if (r.alpha, r.history_threshold) == (0.75, 10):
        continue
    es_rows.append(
        [
            "M2 (trung bình N = 1, 3, 5)"
            if len([x for x in es_rows if x[0].startswith("M2")]) == 0
            else "",
            f"α = {f(r.alpha, 2)}, n_min = {r.history_threshold}",
            f(r.mean_ndcg_at_10_n135),
            "α = 0,75, n_min = 10: 0,045492"
            if len([x for x in es_rows if x[0].startswith("M2")]) == 0
            else "",
        ]
    )
T(
    "Độ nhạy ngoài biên lưới trên tập xác thực",
    [2000, 3088, 1500, 2200],
    ["Mô hình", "Cấu hình ngoài biên", "NDCG@10", "Cấu hình đã khóa"],
    es_rows,
    note="Chỉ dùng tập xác thực, hạt giống 42, sau khi đã khóa cấu hình; tập kiểm thử không được chấm lại. M2 dùng nhóm tinh chỉnh và lấy trung bình NDCG@10 ở N = 1, 3, 5 như quy tắc chọn ban đầu.",
    align=["left", "left", "center", "left"],
)
als_es = es[es.model == "implicit_als"].drop_duplicates(subset="run")
als_best = als_es.loc[als_es.ndcg_at_10.idxmax()]
us_best = es[es.model == "user_cf"].ndcg_at_10.max()
it_best = es[es.model == "item_cf"].ndcg_at_10.max()
P(
    "Bảng 4.19 cho thấy ba nhóm kết quả. Với PureSVD, k = 4 và k = 8 đều kém k = 16, nên cực đại nằm trong "
    "lưới. Với M2, tăng α làm NDCG@10 giảm, còn tăng n_min lên 15 hoặc 20 chỉ tăng nhẹ (cao nhất "
    f"{f(best_m2.mean_ndcg_at_10_n135)} ở α = {f(best_m2.alpha, 2)}, n_min = {int(best_m2.history_threshold)}). "
    "Với UserCF và ItemCF dùng cách tổng hợp trung bình, giảm L xuống 5 tăng NDCG@10 lên tới "
    f"{f(us_best)} và {f(it_best)}, gấp khoảng 3,7 lần cấu hình đã khóa nhưng vẫn thấp hơn rất xa cách tổng "
    "hợp top-N ở E7. Với ALS, không cấu hình ngoài biên nào vượt cấu hình đã khóa: cao nhất là "
    f"{int(als_best.latent_factors)} nhân tố, reg {f(als_best.regularization, 1).rstrip('0').rstrip(',')}, "
    f"a_conf {f(als_best.confidence_scale, 1).rstrip('0').rstrip(',')} với NDCG@10 xác thực "
    f"{f(als_best.ndcg_at_10)}, so với 0,197433; giảm số nhân tố xuống 16 hoặc 8 làm NDCG@10 giảm rõ. Các "
    "giới hạn này được định lượng ở đây và nêu lại ở mục 4.12."
)
H3("4.11.3 Given-N với tập đích (3.14) (E10)")
eg_lab = [
    ("popularity", "Popularity"),
    ("item_cf", "Chỉ ItemCF (L = 40)"),
    ("content", "Chỉ nội dung thẻ"),
    ("m2", "M2 (α = 0,75; n_min = 10)"),
]
e3p = eg_stats[(3, "popularity")]
P(
    "E10 chấm lại cùng mô hình M2 đã khóa và cùng hồ sơ N nghệ sĩ của 189 người để dành, nhưng với tập đích "
    "(3.14): toàn bộ nghệ sĩ trong lịch sử huấn luyện, xác thực và kiểm thử của người dùng trừ N nghệ sĩ "
    "được cung cấp, giao với danh mục học; chỉ N nghệ sĩ này bị loại khỏi tập ứng viên. Cả 189 người đều có "
    "đích hợp lệ ở mọi N. Số đích trung bình mỗi người là "
    + "; ".join(f"{f(eg_targets[n][1], 2)} ở N = {n}" for n in [0, 1, 3, 5])
    + " (tính trong danh mục học; trước khi giao danh mục lần lượt là "
    + "; ".join(f"{f(eg_targets[n][0], 2)}" for n in [0, 1, 3, 5])
    + "). Bảng 4.20 trình bày NDCG@10 và Bảng 4.21 trình bày kiểm định theo cùng chín cặp và cách hiệu "
    "chỉnh Holm như giao thức cũ."
)
T(
    "NDCG@10 theo Given-N với tập đích (3.14) trên nhóm để dành",
    [3188, 1400, 1400, 1400, 1400],
    ["Phương án", "N = 0", "N = 1", "N = 3", "N = 5"],
    [
        [label]
        + [f(float(eg[(eg.method == meth) & (eg.n == n)].ndcg.iloc[0])) for n in [0, 1, 3, 5]]
        for meth, label in eg_lab
    ],
    note="K = 10, 189 người dùng; cùng mô hình và hồ sơ với Bảng 4.13, chỉ khác tập đích.",
)
eg_rows = []
for n in [1, 3, 5]:
    for b, lab in [
        ("popularity", "Popularity"),
        ("content", "Chỉ nội dung thẻ"),
        ("item_cf", "Chỉ ItemCF"),
    ]:
        r = eg_stats[(n, b)]
        cells = [
            str(n),
            f"M2 − {lab}" + (" (chính)" if (n, b) == (3, "popularity") else ""),
            f(r["mean_difference"]),
            ci(r),
            f(r["rank_biserial"], 3),
            pv(r["holm_p"]),
        ]
        if (n, b) == (3, "popularity"):
            cells = [f"**{c}**" for c in cells]
        eg_rows.append(cells)
T(
    "Kiểm định NDCG@10 của M2 theo Given-N với tập đích (3.14) (189 người dùng)",
    [550, 2800, 1250, 2188, 1000, 1000],
    ["N", "Cặp (A − B)", "Chênh lệch", "Khoảng tin cậy 95%", "⟦r_rb⟧", "p (Holm)"],
    eg_rows,
    note="Chín cặp như Bảng 4.15, hiệu chỉnh Holm trên cả chín cặp; bootstrap dùng chung một bộ chỉ số cho mọi cặp cùng N.",
    align=["center", "left", "center", "center", "center", "center"],
    size=22,
)
e5p = eg_stats[(5, "popularity")]
e1p = eg_stats[(1, "popularity")]
P(
    f"Với tập đích (3.14), M2 cao hơn Popularity ở so sánh chính N = 3 là {f(e3p['mean_difference'])}, "
    f"khoảng tin cậy 95% {ci(e3p)}, ⟦r_rb⟧ = {f(e3p['rank_biserial'], 3)}, p sau Holm {pv(e3p['holm_p'])}; ở "
    f"N = 5 chênh lệch là {f(e5p['mean_difference'])} (p sau Holm {pv(e5p['holm_p'])}). Ở N = 1, M2 chưa khác "
    f"Popularity có ý nghĩa ({f(e1p['mean_difference'])}, p sau Holm {pv(e1p['holm_p'])}), phù hợp với việc "
    "22,75% yêu cầu ở mức này phải chuyển hoàn toàn về mức phổ biến (Bảng 4.14). Như vậy cùng một mô hình M2 "
    "cho kết luận ngược nhau ở hai giao thức. Với khoảng năm đích mỗi người, các nghệ sĩ huấn luyện không "
    "được cung cấp bị tính là sai khi được gợi ý, nên phương án nào gợi ý đúng sở thích lâu dài của người "
    "dùng cũng bị phạt; với khoảng 40 đích theo (3.14), phương sai nhỏ hơn và lợi thế của nội dung thẻ khi "
    "có từ ba nghệ sĩ trở lên thể hiện rõ. Giao thức (3.14) gần với cách Breese và cộng sự [40] định nghĩa "
    "Given-N, nhưng được chọn sau khi đã biết kết quả của giao thức cũ, nên nhóm trình bày cả hai và coi kết "
    "quả ở đây là bằng chứng bổ sung."
)
P(
    "Kết quả mở rộng β của M1 (E9) đã được trình bày cùng Hình 4.4 ở mục 4.7. Ngoài ra, khi xếp Popularity "
    "theo số người nghe phân biệt ⟦c_i⟧ thay cho tổng lượt nghe đã biến đổi, NDCG@10 xác thực là "
    f"{f(ep.loc['listeners'].ndcg)}, so với {f(ep.loc['log_count_sum'].ndcg)} của biến thể đã dùng; chênh lệch "
    "nhỏ này không thay đổi vị trí của Popularity so với các mô hình khác."
)

H2("4.12 Thảo luận")
P(
    "Về RQ1, với cấu hình đã khóa, PureSVD nhị phân là mô hình tốt nhất trong sáu mô hình đối sánh và là mô "
    f"hình cá nhân hóa duy nhất vượt Popularity, với NDCG@10 {f(pure)} so với {f(pop)}. Kết quả này phù hợp "
    "với nhận xét của Cremonesi và cộng sự [13] rằng PureSVD hoạt động tốt cho bài toán gợi ý top-N. Tuy "
    "nhiên, phân tích bổ sung E7 cho thấy kết luận về mô hình láng giềng phụ thuộc vào cách tổng hợp điểm: "
    "khi tổng hợp theo kiểu top-N, UserCF và ItemCF vượt cả PureSVD. Về RQ2, phép chia hiện tại gần như "
    "không có biến thiên về độ dài lịch sử; bằng chứng từ Given-N cho thấy chất lượng của M2 tăng từ N = 1 "
    "lên N = 3 ở cả hai giao thức. Phân tích theo mức ưa chuộng nghệ sĩ phổ biến cho thấy biến thiên giữa "
    "người dùng lớn hơn nhiều so với biến thiên theo độ dài lịch sử. Về RQ3, M1 giảm ARP@10 "
    f"{f(arp_drop, 2)}% và tương đương mô hình nền về NDCG@10 ở biên 5%, đồng thời cải thiện độ chính xác "
    "cho nhóm người dùng ít ưa chuộng nghệ sĩ phổ biến. Về RQ4, kết luận phụ thuộc định nghĩa tập đích: M2 "
    "không vượt Popularity khi đích là các cặp kiểm thử, nhưng vượt Popularity ở N = 3 và N = 5 khi đích là "
    "toàn bộ nghệ sĩ không được cung cấp."
)
P(
    "Nhóm chưa đối chiếu con số với các công trình khác dùng dữ liệu Last.fm như [9], [24], [25], vì các công "
    "trình này dùng bộ dữ liệu con, giao thức chia, cách chọn đích và chỉ số khác nhau nên các con số không "
    "so sánh trực tiếp được. Điểm có thể đối chiếu là xu hướng: tương tự nhận xét của Kowald và cộng sự [9] "
    "về thiên lệch phổ biến trong gợi ý âm nhạc, người dùng ít ưa chuộng nghệ sĩ phổ biến nhận kết quả kém "
    "hơn rõ rệt ở mọi mô hình trong thực nghiệm của nhóm (Bảng 4.10)."
)
P(
    "Các giới hạn của thực nghiệm được nhóm lại theo ba loại mối đe dọa đối với tính hợp lệ. Về tính hợp lệ "
    "nội tại, kết quả dựa trên một lần chia ngẫu nhiên với hạt giống 42; một số cấu hình được chọn nằm ở "
    "biên lưới tìm kiếm, và Bảng 4.19 cho thấy với UserCF và ItemCF cực đại nằm ngoài lưới cũ; giao "
    "thức người dùng mới chỉ có chưa tới 200 người mỗi nhóm; các phân tích ở mục 4.11 được thực hiện sau "
    "khi đã mở tập kiểm thử. Về tính hợp lệ của phép đo, nhãn liên quan là nhị phân và chỉ gồm những nghệ sĩ "
    "bị che giấu, nên một nghệ sĩ phù hợp nhưng chưa từng nghe vẫn bị tính là sai, và kết luận về M2 thay "
    "đổi theo định nghĩa tập đích; RMSE được tính trên điểm đại diện do nhóm quy đổi; ILD theo người nghe "
    "dùng chung độ tương đồng với hàm lựa chọn của M1, còn ILD theo thẻ chỉ tính được trên "
    f"{num(ild_models['tag_features']['tagged_catalog_artists'])} trong 15.398 nghệ sĩ của danh mục huấn luyện "
    f"({pct(ild_models['tag_features']['tagged_catalog_artists'] / 15398)}), tức các nghệ sĩ có véc-tơ thẻ "
    "với thẻ xuất hiện ở ít nhất hai nghệ sĩ. Về tính hợp lệ bên ngoài, dữ liệu được thu thập năm 2011, mỗi "
    "người dùng chỉ có danh sách nghệ sĩ nghe nhiều nhất và không có dấu thời gian, nên kết quả chưa thể "
    "khái quát cho việc dự đoán lần nghe tiếp theo trên các nền tảng hiện nay."
)
P(
    "Từ các kết quả trên, ứng dụng ở Chương 5 dùng PureSVD làm mô hình mặc định cho người dùng có sẵn, cho "
    "bật M1 khi muốn giảm thiên lệch phổ biến, dùng M2 với cơ chế dự phòng về mức phổ biến cho người dùng "
    "mới, và cho chọn ALS như mô hình có độ chính xác cao nhất đã đo."
)

H2("4.13 Kết luận chương")
P(
    "Chương 4 đã trình bày kết quả tinh chỉnh và đánh giá các mô hình trên cùng giao thức, kèm các phân tích "
    "bổ sung sau khi khóa cấu hình. Với cấu hình đã khóa, PureSVD nhị phân với k = 16 đạt NDCG@10 cao nhất "
    f"trong sáu mô hình đối sánh trên tập kiểm thử ({f(pure)}), hơn Popularity {f(r_ps['mean_difference'])} "
    "và khác biệt có ý nghĩa thống kê; UserCF, ItemCF và SVD có độ lệch không vượt được Popularity. Kết luận "
    "về hai mô hình láng giềng có điều kiện: nó đúng với cách tổng hợp trung bình có trọng số, còn với cách "
    f"tổng hợp top-N, UserCF và ItemCF đạt {f(e7.loc['user_cf'].ndcg)} và {f(e7.loc['item_cf'].ndcg)}, vượt "
    "PureSVD có ý nghĩa. Mô-đun M1 với λ = 0,75 và β = 0,5 làm ARP giảm "
    f"{f(arp_drop, 2)}% và tương đương mô hình nền về NDCG@10 ở biên 5%. Mô-đun M2 chưa vượt Popularity về "
    "NDCG@10 khi đích là các cặp kiểm thử, nhưng vượt Popularity ở N = 3 và N = 5 khi đích là toàn bộ nghệ "
    "sĩ không được cung cấp; kết luận về RQ4 vì vậy phụ thuộc định nghĩa tập đích. Thực nghiệm mở rộng cho "
    "thấy implicit ALS vượt PureSVD có ý nghĩa thống kê. Chương 5 trình bày việc đóng gói các mô hình đã "
    "chọn thành dịch vụ và giao diện minh họa."
)
