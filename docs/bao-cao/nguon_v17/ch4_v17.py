# ruff: noqa: E501, F821
# Chapter 4 of report v17, in the advisor's frame (feedback of 06/11/2026).
# Executed by build_v17.py with H2, H3, P, N, T, F in scope. Numbers are read from the
# result files below, never typed from memory, except where a source note says otherwise.
import json as _json

import pandas as _pd

D = "docs/results/chinh_thuc_cloud_20261026/"
X = "outputs/chinh_thuc_cloud_20261026/chuong_4_bo_sung/phan_tich/"


def f(x, d=6):
    s = f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s.replace("-", "−")


def num(x):
    return f"{int(x):,}".replace(",", ".")


def pct(x, d=2):
    return f(100 * x, d) + "%"


def pval(p):
    if p >= 0.001:
        return f(p, 3)
    m, e = f"{p:.2e}".split("e")
    return f"{m.replace('.', ',')}e−{int(e[1:])}" if e.startswith("-") else f"{m}e{int(e)}"


def load(path):
    return _json.loads(open(path, encoding="utf-8").read())


test = _pd.read_csv(D + "test/metrics.csv")
test = test[test.seed == 42]


def tm(model, k, metric):
    return float(test[(test.model == model) & (test.k == k)][metric].iloc[0])


official_stats = {(r["a"], r["b"]): r for r in load(D + "test/statistics_ndcg_at_10.json")["pairs"]}
extra = load(X + "kiem_dinh_bo_sung.json")
family = {r["b"]: r for r in extra["supplementary_family_pure_svd_vs_others_holm"]}
ci = extra["mean_ndcg10_bootstrap_ci"]
seeds = load(D + "test/seed_summary.json")
groups = _pd.read_csv(D + "test/history_groups.csv")
mainstream = _pd.read_csv(X + "nhom_uu_pho_bien.csv")
split = load(X + "chenh_lech_puresvd_popularity.json")
variants = _pd.read_csv(X + "m1_bien_the_test.csv").set_index("bien_the")
m1_tests = {r["a"]: r for r in load(X + "m1_kiem_dinh_bien_the.json")}
ild_models = load(X + "ild_the_mo_hinh.json")
examples = _pd.read_csv(X + "m1_vi_du.csv")
paths = _pd.read_csv(X + "m2_duong_xu_ly.csv").set_index("n")
m2 = _pd.read_csv(D + "m2/test/metrics.csv")
m2 = m2[m2.k == 10]
m2_stats = load(D + "m2/test/statistics_ndcg_at_10.json")["pairs"]
m2_sel = load(D + "m2/validation/selection.json")
cost = _pd.read_csv(D + "test/cost.csv").set_index("model")
m1_grid = _pd.read_csv(D + "m1_metrics.csv")
m1_grid = m1_grid[(m1_grid.seed == 42) & (m1_grid.k == 10)]
curve = _pd.read_csv(
    "outputs/chinh_thuc_cloud_20261026/chuong_4_bo_sung/tuning/svd_curve/learning_curve.csv"
)
check = load(X + "doi_chieu_chinh_thuc.json")

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
SIX = ["random", "popularity", "user_cf", "item_cf", "svd", "pure_svd"]
ALL = SIX + ["m1", "implicit_als"]

P(
    "Chương này trình bày kết quả huấn luyện và đánh giá các mô hình theo giao thức đã mô tả ở "
    "mục 3.10. Thứ tự trình bày bám theo các câu hỏi nghiên cứu ở Bảng 1.1: mục 4.1 nêu môi trường "
    "và quy ước báo cáo; mục 4.2 tóm tắt dữ liệu sau tiền xử lý; mục 4.3 tổng hợp các thực nghiệm; "
    "mục 4.4 trình bày quá trình tinh chỉnh trên tập xác thực; mục 4.5 so sánh các mô hình trên tập "
    "kiểm thử (RQ1); mục 4.6 phân tích theo độ dài lịch sử và theo từng người dùng (RQ2); mục 4.7 "
    "đánh giá mô-đun tái xếp hạng M1 (RQ3); mục 4.8 đánh giá mô-đun dự phòng M2 (RQ4, RQ2); mục 4.9 "
    "trình bày thực nghiệm mở rộng với implicit ALS; mục 4.10 so sánh chi phí xử lý; mục 4.11 thảo "
    "luận chung. Tập kiểm thử chỉ được dùng sau khi mọi cấu hình đã được chốt trên tập xác thực."
)

H2("4.1 Môi trường và quy ước báo cáo")
H3("4.1.1 Môi trường thực nghiệm")
P(
    "Các số liệu huấn luyện, tinh chỉnh và kiểm thử của chương đến từ một lần chạy liên tục trên "
    "máy ảo đám mây (Linux 6.18 x86_64, bộ xử lý Intel Xeon 2,10 GHz với 4 luồng logic, khoảng "
    "15,7 GiB RAM), bắt đầu từ dữ liệu gốc và đi qua tiền xử lý, chia tập, tinh chỉnh, khóa cấu "
    "hình và kiểm thử. Mã nguồn dùng Python 3.11.17 cùng NumPy 2.4.6, SciPy 1.17.1 [31], pandas 2.3.3, "
    "pyarrow 19.0.1, scikit-learn 1.9.1 và implicit 0.7.3 [30] cho mô hình ALS. Phân rã PureSVD "
    "dùng hàm svds của SciPy với bộ giải ARPACK. Mọi bước đặt thư viện đại số tuyến tính chạy một "
    "luồng để kết quả tái lập được. Toàn bộ lần chạy mất khoảng 48 phút, trong đó tinh chỉnh chiếm "
    "42,8 phút."
)
P(
    "Lần chạy trên chỉ lưu bảng chỉ số tổng hợp của tập kiểm thử. Để vẽ các hình theo từng người "
    "dùng ở mục 4.5 đến 4.8, nhóm chấm lại tập kiểm thử trên máy cá nhân (Windows 11, Intel Core "
    "i5-11300H 3,10 GHz với 8 luồng logic, 15,7 GiB RAM, Python 3.11.9 và cùng phiên bản NumPy, "
    "SciPy, pandas, pyarrow, implicit) bằng đúng các mô hình đã khóa. PureSVD, M1 và ALS được nạp "
    "lại từ tệp mô hình đã lưu; UserCF, ItemCF và SVD có độ lệch được huấn luyện lại với cấu hình "
    "đã khóa và cho NDCG@10 xác thực trùng tới mọi chữ số với lần chạy chính thức. Trên tập kiểm "
    "thử, 24 chỉ số (8 chỉ số tại K = 5, 10, 20) của cả tám mô hình khớp với bảng chính thức, sai "
    f"lệch lớn nhất là {max(v['max_abs_difference'] for v in check.values()):.1e} do làm tròn số "
    "thực, và bốn cặp kiểm định khai báo trước cho đúng các giá trị cũ. Lần chấm lại không chọn lại "
    "cấu hình nào. Thời gian xử lý ở mục 4.10 là số đo trên máy đám mây."
)
P(
    "Mỗi lần chạy được lưu thành một bộ tệp theo quy ước ở Phụ lục A, gồm cấu hình, mã băm dữ liệu, "
    "ánh xạ, quy tắc biến đổi, tham số mô hình, danh sách dự đoán theo người dùng và bảng chỉ số. "
    "Hạt giống chia dữ liệu split_seed = 42 được giữ cố định cho mọi mô hình. Các mô hình có yếu tố "
    "ngẫu nhiên dùng hạt giống 42 để chọn cấu hình, sau đó cấu hình thắng được chạy lại ở hạt giống "
    "43 và 44 để xem mức dao động."
)
H3("4.1.2 Quy ước báo cáo và kiểm định thống kê")
P(
    "Các chỉ số xếp hạng Precision@K, Recall@K và NDCG@K được tính cho từng người dùng có ít nhất "
    "một đích hợp lệ rồi lấy trung bình không trọng số, tại K = 5, 10 và 20. NDCG@10 là chỉ số "
    "chính để chọn cấu hình và so sánh mô hình. Các chỉ số bổ sung gồm độ bao phủ, hệ số Gini, độ "
    "phổ biến trung bình (ARP), độ mới và độ đa dạng trong danh sách (ILD) được tính tại K = 10. "
    "Độ bao phủ và Gini là chỉ số trên toàn danh mục nên chỉ có một giá trị cho mỗi mô hình. RMSE "
    "trên điểm đại diện chỉ là chỉ số phụ, không dùng để xếp hạng mô hình."
)
P(
    "Vì các mô hình được đánh giá trên cùng một nhóm người dùng, sự khác biệt giữa hai mô hình được "
    "kiểm định theo cặp trên NDCG@10 của từng người dùng bằng kiểm định Wilcoxon có dấu hai phía "
    "[27], bỏ các chênh lệch bằng 0. Khi có nhiều cặp so sánh, giá trị p được hiệu chỉnh theo "
    "phương pháp Holm [28] với mức ý nghĩa 0,05. Khoảng tin cậy 95% được tính bằng bootstrap phân "
    "vị với 1.000 lần lấy mẫu lại theo người dùng, hạt giống 42 [29]. Bốn cặp kiểm định chính được "
    "ghi vào tệp khóa trước khi mở tập kiểm thử: PureSVD với Popularity, SVD có độ lệch với "
    "PureSVD, M1 với PureSVD và ALS với PureSVD. Các so sánh thêm ngoài bốn cặp này được ghi là "
    "kiểm định bổ sung và hiệu chỉnh Holm trong họ riêng của chúng."
)

H2("4.2 Dữ liệu sau tiền xử lý")
P(
    "Sau bước làm sạch và điều kiện tối thiểu năm nghệ sĩ cho mỗi người dùng, dữ liệu còn 1.877 "
    "người dùng và 92.801 cặp tương tác. Bảng 4.1 tóm tắt kết quả chia tập theo mục 3.5.2. Danh mục "
    "huấn luyện gồm 15.398 nghệ sĩ; các đích ở tập xác thực và kiểm thử không thuộc danh mục này "
    "được báo cáo riêng và không tham gia tính chỉ số."
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
    "outputs/chinh_thuc_cloud_20261026/chuong_3/run/split/metrics.json; " + D + "test/metrics.csv.",
)
below = groups[(groups.model == "popularity") & (groups.group == "below_mode")].iloc[0]
at = groups[(groups.model == "popularity") & (groups.group == "at_mode")].iloc[0]
above = groups[(groups.model == "popularity") & (groups.group == "above_mode")].iloc[0]
P(
    "Một đặc điểm quan trọng của dữ liệu là mỗi người dùng chỉ được ghi nhận những nghệ sĩ nghe "
    "nhiều nhất, và 1.829 người dùng có đúng 50 nghệ sĩ trong dữ liệu gốc. Với quy tắc chia ở công "
    f"thức (3.2), trên tập huấn luyện có {num(at.users_total)} người dùng có đúng 40 tương tác, "
    f"{int(below.users_total)} người dùng có ít hơn 40 và {int(above.users_total)} người dùng có "
    "nhiều hơn 40. Vì vậy, bài toán đánh giá trong khóa luận là tìm lại một phần danh sách nghệ sĩ "
    "yêu thích của người dùng từ phần còn lại, không phải dự đoán lần nghe tiếp theo."
)
P(
    "Hình 4.1 cho thấy phân bố số người nghe của nghệ sĩ trên tập huấn luyện có dạng đuôi dài: một "
    "nhóm nhỏ nghệ sĩ có hàng trăm người nghe, còn phần lớn danh mục chỉ có một vài người nghe. "
    "Hình 4.2 cho thấy tổng lượt nghe của người dùng trải rộng nhiều bậc độ lớn, nên lượt nghe gốc "
    "cần được biến đổi trước khi dùng làm điểm (mục 3.5.3). Kết quả khám phá dữ liệu gốc được trình "
    "bày ở mục 3.4.3."
)
F(
    X + "hinh/hinh_4_1.png",
    "Số người nghe của nghệ sĩ trên tập huấn luyện theo thứ hạng",
    X + "hinh/hinh_4_1.csv.",
)
F(
    X + "hinh/hinh_4_2.png",
    "Phân bố tổng lượt nghe theo người dùng trên tập huấn luyện",
    X + "hinh/hinh_4_2.csv.",
)

H2("4.3 Tổng hợp các thực nghiệm")
P(
    "Bảng 4.2 liệt kê các thực nghiệm và câu hỏi nghiên cứu tương ứng. Ngoại trừ E1 chỉ dùng tập "
    "xác thực, các thực nghiệm còn lại báo cáo kết quả trên tập kiểm thử với cấu hình đã chốt."
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
    ],
    "thiết kế thực nghiệm ở mục 3.6 đến 3.10.",
    align=["center", "left", "center", "center"],
)

H2("4.4 Tinh chỉnh tham số trên tập xác thực")
P(
    "Tham số của các mô hình được chọn theo NDCG@10 trên tập xác thực ở hạt giống 42; tập kiểm thử "
    "chưa được dùng ở bước này và các script tinh chỉnh chặn mọi thao tác mở tệp kiểm thử. Bảng 4.3 "
    "tóm tắt không gian tìm kiếm, số cấu hình đã chạy và cấu hình được chọn. Tổng cộng có 48 cấu "
    "hình cho năm mô hình có tham số. UserCF, ItemCF, PureSVD và ALS quét toàn bộ lưới; SVD có độ "
    "lệch dùng cấu hình mặc định cộng 11 cấu hình sinh ngẫu nhiên bằng hạt giống 42. Với SVD có độ "
    "lệch và ALS, số vòng huấn luyện được chọn bằng dừng sớm theo NDCG@10 xác thực với số vòng chờ 5."
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
    D
    + "tuning_summary.json; docs/results/chuong_4/tuning_*.csv; configs/tuning.yaml. Random và Popularity: docs/data-card.md.",
    align=["left", "left", "left", "center"],
)
P(
    "Với UserCF và ItemCF, NDCG@10 giảm khi số láng giềng tăng; co rút làm ItemCF kém đi rõ rệt (với "
    "L = 20, NDCG@10 giảm từ 0,015364 khi không co rút xuống 0,005616 khi co rút 10). PureSVD đạt cao "
    "nhất ở k = 16 và giảm dần khi k tăng: 0,166611; 0,156427; 0,137042 và 0,114355 với k = 16, 32, "
    "64, 128. Cấu hình tốt nhất của UserCF, ItemCF và PureSVD đều nằm ở giá trị nhỏ nhất của lưới. "
    "Nhóm giữ nguyên lưới đã định trước và không mở rộng sau khi thấy kết quả, để tránh chọn cấu "
    "hình theo tập xác thực nhiều lần. Đây là một hạn chế: có thể tồn tại cấu hình tốt hơn với L nhỏ "
    "hơn 20 hoặc k nhỏ hơn 16."
)
P(
    "Bảng 4.4 so sánh ba biểu diễn đầu vào của PureSVD ở cùng k = 32 trên tập xác thực, đo trong lần "
    "chạy phát triển trước lần chạy chính thức. Biểu diễn nhị phân đạt NDCG@10 cao nhất (0,156427), "
    "tiếp theo là log-count (0,154577) và điểm đại diện (0,151692). Giá trị của biểu diễn nhị phân "
    "trùng với cấu hình k = 32 trong lần chạy chính thức. Kết quả này phù hợp với bản chất phản hồi "
    "ngầm của dữ liệu: việc một người dùng có nghe một nghệ sĩ mang nhiều thông tin cho bài toán tìm "
    "lại nghệ sĩ hơn là mức độ nghe nhiều hay ít. Biểu diễn nhị phân được chọn trước khi mở tập kiểm "
    "thử."
)
T(
    "NDCG@10 trên tập xác thực của PureSVD với ba biểu diễn (k = 32)",
    [4394, 4394],
    ["Biểu diễn", "NDCG@10"],
    [["Nhị phân", "0,156427"], ["Log-count", "0,154577"], ["Điểm đại diện 1–5", "0,151692"]],
    "docs/data-card.md, bảng so sánh biểu diễn PureSVD k = 32 (lần chạy phát triển); "
    "docs/results/chuong_4/tuning_pure_svd.csv cho biểu diễn nhị phân.",
)
best_epoch = int(curve.loc[curve.validation_ndcg_at_10.idxmax(), "epoch"])
last = curve.iloc[-1]
first = curve.iloc[0]
min_rmse = curve.loc[curve.validation_proxy_rmse.idxmin()]
P(
    f"Đối với SVD có độ lệch, vòng tốt nhất theo NDCG@10 là vòng {best_epoch} trong khi số vòng tối "
    "đa là 100. Để kiểm tra nguyên nhân, nhóm huấn luyện lại cấu hình đã chọn đủ 100 vòng, không dừng "
    "sớm, và ghi NDCG@10 cùng RMSE điểm đại diện trên tập huấn luyện và tập xác thực sau mỗi vòng "
    "(Hình 4.3). Bảy vòng đầu trùng từng chữ số với lần huấn luyện có dừng sớm. NDCG@10 xác thực đạt "
    f"đỉnh {f(curve.validation_ndcg_at_10.max())} ở vòng {best_epoch} rồi giảm dần, còn "
    f"{f(last.validation_ndcg_at_10)} ở vòng {int(last.epoch)}. Trong cùng khoảng đó RMSE trên tập "
    f"huấn luyện giảm từ {f(first.train_proxy_rmse, 4)} xuống {f(last.train_proxy_rmse, 4)}, và RMSE "
    f"trên tập xác thực giảm từ {f(first.validation_proxy_rmse, 4)} xuống thấp nhất "
    f"{f(min_rmse.validation_proxy_rmse, 4)} ở vòng {int(min_rmse.epoch)} rồi tăng nhẹ lên "
    f"{f(last.validation_proxy_rmse, 4)} ở vòng {int(last.epoch)}. Như vậy trong khoảng 50 vòng đầu, sai "
    "số dự đoán trên cả các cặp chưa dùng để huấn luyện vẫn được cải thiện trong khi chất lượng xếp hạng top-K trên "
    "toàn danh mục đi xuống: hai mục tiêu này không khớp nhau trên dữ liệu phản hồi ngầm. Ở các vòng "
    "đầu, mô hình chủ yếu học điểm trung bình và độ lệch của nghệ sĩ nên thứ tự gợi ý gần với mức phổ "
    "biến; càng về sau, mô hình càng khớp điểm của các cặp đã nghe nhưng không học gì từ các nghệ sĩ "
    "người dùng chưa nghe."
)
F(
    X + "hinh/hinh_4_3.png",
    "NDCG@10 xác thực và RMSE điểm đại diện theo vòng huấn luyện của SVD có độ lệch",
    "outputs/chinh_thuc_cloud_20261026/chuong_4_bo_sung/tuning/svd_curve/learning_curve.csv "
    "(cấu hình đã khóa, hạt giống 42, 100 vòng; script scripts/rebuild_locked_runs.py).",
)

H2("4.5 So sánh các mô hình trên tập kiểm thử")
P(
    "Bảng 4.5 trình bày chất lượng xếp hạng của sáu mô hình đối sánh trên tập kiểm thử với hạt giống "
    "42, tính trên cùng 1.855 người dùng có đích hợp lệ. Danh sách gợi ý trên tập kiểm thử loại cả "
    "lịch sử huấn luyện và lịch sử xác thực. Hai dòng cuối, ngăn cách với sáu mô hình đối sánh, là M1 "
    "(mục 4.7) và implicit ALS (mục 4.9) để tiện so sánh trên cùng giao thức."
)
rank_rows = []
for m in ALL:
    vals = [
        tm(m, 10, "precision"),
        tm(m, 10, "recall"),
        tm(m, 5, "ndcg"),
        tm(m, 10, "ndcg"),
        tm(m, 20, "ndcg"),
    ]
    cells = [f(v) for v in vals]
    if m == "pure_svd":
        cells = [f"**{c}**" for c in cells]
    rank_rows.append([NAMES[m]] + cells)
rank_rows.insert(6, ["Thực nghiệm bổ sung trên cùng giao thức", "", "", "", "", ""])
T(
    "Chất lượng xếp hạng trên tập kiểm thử",
    [2228, 1312, 1312, 1312, 1312, 1312],
    ["Mô hình", "P@10", "R@10", "NDCG@5", "NDCG@10", "NDCG@20"],
    rank_rows,
    D
    + "test/metrics.csv (hạt giống 42). Mọi chỉ số càng cao càng tốt; số in đậm là giá trị cao nhất trong sáu mô hình đối sánh.",
)
extra_rows = []
rmse = {"user_cf": "0,9327", "item_cf": "0,9610", "svd": "1,2713"}
for m in ALL:
    extra_rows.append(
        [
            NAMES[m],
            pct(tm(m, 10, "catalog_coverage")),
            f(tm(m, 10, "gini"), 4),
            f(tm(m, 10, "arp"), 2),
            f(tm(m, 10, "novelty"), 3),
            f(tm(m, 10, "ild"), 4),
            rmse.get(m, "-"),
        ]
    )
extra_rows.insert(6, ["Thực nghiệm bổ sung trên cùng giao thức", "", "", "", "", "", ""])
P(
    "Bảng 4.6 trình bày các chỉ số ngoài độ chính xác tại K = 10 và RMSE của ba mô hình dự đoán điểm "
    "đại diện. RMSE được tính trên 8.060 cặp kiểm thử có nghệ sĩ trong danh mục; RMSE không áp dụng "
    "cho Random, Popularity, PureSVD, M1 và ALS vì điểm của các mô hình này không nằm trên thang 1–5."
)
T(
    "Các chỉ số bổ sung trên tập kiểm thử (K = 10)",
    [2500, 1060, 1046, 1046, 1046, 1045, 1045],
    ["Mô hình", "Bao phủ ↑", "Gini ↓", "ARP ↓", "Độ mới ↑", "ILD ↑", "RMSE ↓"],
    extra_rows,
    D
    + "test/metrics.csv; RMSE: docs/results/chuong_4_test.md. Bao phủ tính trên 15.398 nghệ sĩ; độ mới tính bằng bit.",
)
P(
    "Bảng 4.7 trình bày NDCG@10 trung bình kèm khoảng tin cậy 95% của từng mô hình, và Bảng 4.8 "
    "trình bày kết quả kiểm định theo cặp. Phần trên của Bảng 4.8 là bốn cặp khai báo trước; phần "
    "dưới là kiểm định bổ sung giữa PureSVD và từng mô hình đối sánh còn lại, hiệu chỉnh Holm trong "
    "họ năm cặp."
)
T(
    "NDCG@10 trung bình trên tập kiểm thử và khoảng tin cậy 95%",
    [3600, 1700, 3488],
    ["Mô hình", "NDCG@10", "Khoảng tin cậy 95%"],
    [
        [NAMES[m], f(ci[m]["mean"]), f"[{f(ci[m]['ci95_low'])}; {f(ci[m]['ci95_high'])}]"]
        for m in ALL
    ],
    X
    + "kiem_dinh_bo_sung.json (bootstrap 1.000 lần theo người dùng, hạt giống 42; 1.855 người dùng).",
)
pair_rows = []
for a, b in [
    ("pure_svd", "popularity"),
    ("svd", "pure_svd"),
    ("m1", "pure_svd"),
    ("implicit_als", "pure_svd"),
]:
    r = official_stats[(a, b)]
    pair_rows.append(
        [
            f"{NAMES[a]} − {NAMES[b]}",
            "Khai báo trước",
            f(r["mean_difference"]),
            f"[{f(r['ci95_low'])}; {f(r['ci95_high'])}]",
            pval(r["holm_p"]),
        ]
    )
for b in ["random", "popularity", "user_cf", "item_cf", "svd"]:
    r = family[b]
    pair_rows.append(
        [
            f"PureSVD − {NAMES[b]}",
            "Bổ sung",
            f(r["mean_difference"]),
            f"[{f(r['ci95_low'])}; {f(r['ci95_high'])}]",
            pval(r["holm_p"]),
        ]
    )
T(
    "Kiểm định Wilcoxon theo cặp trên NDCG@10 của tập kiểm thử",
    [2700, 1288, 1300, 1900, 1600],
    ["Cặp (A − B)", "Họ kiểm định", "Chênh lệch", "Khoảng tin cậy 95%", "p (Holm)"],
    pair_rows,
    D
    + "test/statistics_ndcg_at_10.json (khai báo trước); "
    + X
    + "kiem_dinh_bo_sung.json (bổ sung).",
    align=["left", "center", "center", "center", "center"],
)
pop, pure = tm("popularity", 10, "ndcg"), tm("pure_svd", 10, "ndcg")
P(
    f"PureSVD nhị phân có NDCG@10 cao nhất trong sáu mô hình đối sánh ({f(pure)}), gấp khoảng "
    f"{f(pure / pop, 2)} lần Popularity ({f(pop)}). Chênh lệch với Popularity là "
    f"{f(official_stats[('pure_svd', 'popularity')]['mean_difference'])}, khoảng tin cậy 95% không "
    "chứa 0 và p sau hiệu chỉnh Holm rất nhỏ, nên khác biệt có ý nghĩa thống kê. PureSVD cũng hơn có "
    "ý nghĩa mọi mô hình đối sánh còn lại trong kiểm định bổ sung. Thứ tự các mô hình trên tập kiểm "
    "thử giống trên tập xác thực."
)
P(
    "Popularity là đối chứng mạnh trên dữ liệu này: UserCF, ItemCF và SVD có độ lệch đều có NDCG@10 "
    "thấp hơn Popularity, trên cả tập xác thực và tập kiểm thử. Với SVD có độ lệch, Hình 4.3 cho thấy "
    "mục tiêu sai số bình phương không dẫn tới xếp hạng tốt; mô hình được chọn ở vòng 2 nên danh sách "
    f"gần với mức phổ biến (ARP {f(tm('svd', 10, 'arp'), 2)} so với {f(tm('popularity', 10, 'arp'), 2)} "
    "của Popularity) nhưng kém Popularity về độ chính xác. Với UserCF và ItemCF, danh sách nghiêng mạnh "
    f"về nghệ sĩ ít phổ biến (ARP {f(tm('user_cf', 10, 'arp'), 2)} và {f(tm('item_cf', 10, 'arp'), 2)}), "
    "trong khi đích kiểm thử lại tập trung vào nghệ sĩ được nhiều người nghe. Nhóm cho rằng việc tổng "
    "hợp trên điểm đại diện với số láng giềng nhỏ là một nguyên nhân có thể, nhưng chưa kiểm chứng giả "
    "thuyết này. Giữa hai mô hình láng giềng, UserCF chính xác hơn ItemCF một chút ở K = 10 nhưng ItemCF "
    "phủ danh mục rộng hơn gấp đôi."
)
P(
    "Các chỉ số bổ sung cho thấy sự đánh đổi giữa độ chính xác và mức tập trung. Popularity và SVD có "
    "độ lệch phủ dưới 0,4% danh mục và có ARP trên 300. PureSVD chính xác nhất nhưng chỉ phủ "
    f"{pct(tm('pure_svd', 10, 'catalog_coverage'))} danh mục với Gini {f(tm('pure_svd', 10, 'gini'), 4)}. "
    "UserCF và ItemCF phủ rộng hơn nhiều nhưng độ chính xác thấp. Random có độ bao phủ và độ mới cao "
    "nhất nhưng gần như không gợi ý đúng. RMSE không thống nhất với thứ hạng: SVD có độ lệch có RMSE "
    "cao nhất trong ba mô hình dự đoán điểm, vì vòng của nó được chọn theo NDCG@10."
)
P(
    "Qua ba hạt giống 42, 43 và 44, NDCG@10 trên tập kiểm thử của SVD có độ lệch là "
    f"{f(seeds['svd']['at_k']['10']['ndcg']['mean'])} ± {f(seeds['svd']['at_k']['10']['ndcg']['sample_std'])}. "
    "PureSVD và M1 cho kết quả giống hệt ở cả ba hạt giống, vì hạt giống chỉ đổi véc-tơ khởi đầu của "
    "ARPACK và thuật toán hội tụ về cùng không gian con; do đó việc chạy lại hai mô hình này không phải "
    "là kiểm chứng độc lập. Trả lời RQ1: trong sáu mô hình đối sánh, PureSVD nhị phân với k = 16 cho "
    "chất lượng xếp hạng tốt nhất và là mô hình cá nhân hóa duy nhất vượt Popularity; ba mô hình UserCF, "
    "ItemCF và SVD có độ lệch không vượt được Popularity."
)

H2("4.6 Phân tích theo độ dài lịch sử và theo từng người dùng")
P(
    f"Như đã nêu ở mục 4.2, gần như mọi người dùng có đúng 40 tương tác huấn luyện. Trong 1.855 người "
    f"dùng có đích kiểm thử hợp lệ, nhóm dưới 40 có {int(below.users_eligible)} người, nhóm đúng 40 có "
    f"{num(at.users_eligible)} người và nhóm trên 40 chỉ có {int(above.users_eligible)} người. Do "
    "đó, Bảng 4.9 chỉ mang tính mô tả và không đủ để kết luận về ảnh hưởng của độ dài lịch sử. Ảnh "
    "hưởng này được khảo sát chủ động bằng thí nghiệm Given-N ở mục 4.8."
)
hist_rows = []
for m in ["popularity", "user_cf", "item_cf", "svd", "pure_svd", "m1", "implicit_als"]:
    g = groups[groups.model == m].set_index("group").ndcg_at_10
    hist_rows.append([NAMES[m], f(g["below_mode"]), f(g["at_mode"]), f(g["above_mode"])])
T(
    "NDCG@10 trên tập kiểm thử theo độ dài lịch sử huấn luyện",
    [3088, 1900, 1900, 1900],
    [
        "Mô hình",
        f"Dưới 40 ({int(below.users_eligible)} người)",
        f"Đúng 40 ({num(at.users_eligible)} người)",
        f"Trên 40 ({int(above.users_eligible)} người)",
    ],
    hist_rows,
    D + "test/history_groups.csv (script scripts/test_breakdown.py).",
)
P(
    "Hình 4.4 trình bày phân bố NDCG@10 theo từng người dùng. Với mọi mô hình, phần lớn người dùng có "
    "NDCG@10 bằng 0 hoặc rất thấp, và trung bình được kéo lên bởi một nhóm người dùng tìm lại được nhiều "
    "đích. Hình 4.5 trình bày hiệu NDCG@10 của PureSVD trừ Popularity cho từng người dùng: "
    f"{num(split['improved'])} người dùng ({pct(split['improved'] / split['users'], 1)}) được cải thiện, "
    f"{split['equal']} người ({pct(split['equal'] / split['users'], 1)}) giữ nguyên, trong đó "
    f"{split['equal_both_zero']} người có NDCG@10 bằng 0 ở cả hai mô hình, và {split['worse']} người "
    f"({pct(split['worse'] / split['users'], 1)}) bị giảm."
)
F(
    X + "hinh/hinh_4_4.png",
    "Phân bố NDCG@10 theo người dùng trên tập kiểm thử",
    X + "ndcg10_tung_nguoi_dung.csv. Hình thoi là giá trị trung bình.",
)
F(
    X + "hinh/hinh_4_5.png",
    "Hiệu NDCG@10 của PureSVD và Popularity theo từng người dùng",
    X + "hinh/hinh_4_5.csv; " + X + "chenh_lech_puresvd_popularity.json.",
)
P(
    "Theo gợi ý của Kowald và cộng sự [9], nhóm chia người dùng thành ba nhóm có cỡ mẫu gần bằng nhau "
    "theo mức ưa chuộng nghệ sĩ phổ biến, đo bằng số người nghe trung bình (trên tập huấn luyện) của "
    "các nghệ sĩ trong lịch sử huấn luyện của người dùng. Bảng 4.10 cho thấy mọi mô hình đều kém hơn "
    "rõ rệt ở nhóm ưa chuộng thấp. Popularity gần như không hữu ích cho nhóm này "
    f"(NDCG@10 {f(mainstream.Popularity[0])} so với {f(mainstream.Popularity[2])} ở nhóm cao). Ở nhóm "
    f"thấp, ItemCF ({f(mainstream.ItemCF[0])}) vượt Popularity, ngược với kết quả trung bình toàn bộ. "
    f"M1 có NDCG@10 cao hơn PureSVD ở nhóm thấp ({f(mainstream.M1[0])} so với {f(mainstream.PureSVD[0])}) "
    f"và thấp hơn ở nhóm cao ({f(mainstream.M1[2])} so với {f(mainstream.PureSVD[2])}). Đây là phân "
    "tích mô tả, chưa kiểm định thống kê theo từng nhóm."
)
T(
    "NDCG@10 trên tập kiểm thử theo mức ưa chuộng nghệ sĩ phổ biến của người dùng",
    [2788, 2000, 2000, 2000],
    ["Mô hình"]
    + [
        f"{r.nhom} ({r.so_nguoi} người; {f(r.trung_binh_nguoi_nghe_min, 1)}–{f(r.trung_binh_nguoi_nghe_max, 1)})"
        for r in mainstream.itertuples()
    ],
    [
        [NAMES[m], *[f(mainstream[col][i]) for i in range(3)]]
        for m, col in [
            ("popularity", "Popularity"),
            ("user_cf", "UserCF"),
            ("item_cf", "ItemCF"),
            ("svd", "SVD có độ lệch"),
            ("pure_svd", "PureSVD"),
            ("m1", "M1"),
            ("implicit_als", "Implicit ALS"),
        ]
    ],
    X
    + "nhom_uu_pho_bien.csv. Khoảng trong tiêu đề cột là số người nghe trung bình của các nghệ sĩ trong lịch sử người dùng.",
)

H2("4.7 Đánh giá mô-đun tái xếp hạng M1")
grid_base = m1_grid[(m1_grid["lambda"] == 1) & (m1_grid.beta == 0)].iloc[0]
within = int((m1_grid.ndcg >= 0.95 * grid_base.ndcg).sum())
P(
    "M1 được áp dụng trên 100 ứng viên đầu của PureSVD nhị phân k = 16. Lưới tham số gồm λ ∈ {0,5; "
    "0,75; 1} và β ∈ {0; 0,1; 0,25; 0,5}. Theo quy tắc chọn đặt trước ở mục 3.7.3, trong các biến thể "
    "đầy đủ có mức giảm NDCG@10 xác thực không quá 5% so với mô hình nền, biến thể có ARP thấp nhất được "
    "chọn, sau đó xét ILD cao nhất rồi NDCG cao nhất; cấu hình được chọn là λ = 0,75 và β = 0,5. Hình 4.6 "
    f"trình bày toàn bộ 12 điểm của lưới trên tập xác thực; {within} trên 12 điểm nằm trong ngưỡng giảm "
    "5%. Đường đánh đổi cho thấy tăng β làm ARP giảm đều, còn giảm λ xuống 0,5 làm NDCG@10 giảm nhanh khi "
    "β lớn."
)
F(
    X + "hinh/hinh_4_6.png",
    "Đánh đổi giữa NDCG@10 và ARP của 12 cấu hình M1 trên tập xác thực",
    D
    + "m1_metrics.csv (hạt giống 42, K = 10). Điểm λ = 1, β = 0 là mô hình nền; đường nét đứt là ngưỡng giảm 5% NDCG@10 so với mô hình nền.",
)
P(
    "Bảng 4.11 so sánh bốn biến thể trên tập kiểm thử: mô hình nền, chỉ thành phần đa dạng, chỉ phạt "
    "phổ biến và M1 đầy đủ. Quy tắc chọn chỉ dùng tập xác thực; ba biến thể ngoài M1 đầy đủ được chấm "
    "trên tập kiểm thử sau khi tập này đã mở, nên đây là phân tích bổ sung và không dùng để chọn lại "
    "cấu hình. Cột ILD theo thẻ là độ đa dạng tính bằng côsin giữa véc-tơ TF-IDF thẻ của hai nghệ sĩ, "
    "dựng theo cùng cách với M2 trên toàn bộ tập huấn luyện "
    f"({num(ild_models['tag_features']['vocabulary_size'])} thẻ, "
    + f"{num(ild_models['tag_features']['tagged_catalog_artists'])} trong 15.398 nghệ sĩ có thẻ), "
    + "chỉ tính trên các cặp nghệ sĩ đều có thẻ; cả 1.855 danh sách đều có ít nhất một cặp như vậy."
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
    X
    + "m1_bien_the_test.csv (phân tích bổ sung trên tập kiểm thử); M1 đầy đủ trùng với "
    + D
    + "test/metrics.csv.",
)
t_full = official_stats[("m1", "pure_svd")]
t_div, t_pop = m1_tests["m1_chi_da_dang"], m1_tests["m1_chi_phat_pho_bien"]
v_full = variants.loc["m1_day_du"]
P(
    "Khi diễn giải Bảng 4.11 cần lưu ý rằng hàm lựa chọn của M1 dùng cùng độ tương đồng côsin trên "
    "véc-tơ người nghe nhị phân với chỉ số ILD, và dùng số người nghe trên tập huấn luyện, cũng là đại "
    "lượng tạo nên ARP. Vì vậy, việc ILD tăng và ARP giảm khi bật các thành phần tương ứng phần lớn là "
    "hệ quả trực tiếp của hàm mục tiêu, không phải bằng chứng độc lập. Các thước đo không tham gia hàm "
    "lựa chọn cho thấy mức cải thiện thật nhỏ hơn: ILD theo thẻ của M1 đầy đủ tăng từ "
    f"{f(base_v.ild_tag, 4)} lên {f(v_full.ild_tag, 4)} (so với mức tăng ILD theo người nghe từ "
    f"{f(base_v.ild, 4)} lên {f(v_full.ild, 4)}), còn biến thể chỉ phạt phổ biến làm ILD theo thẻ giảm "
    f"nhẹ xuống {f(variants.loc['chi_phat_pho_bien'].ild_tag, 4)}. Độ bao phủ tăng từ "
    f"{pct(base_v.catalog_coverage)} lên {pct(v_full.catalog_coverage)} và Gini giảm từ "
    f"{f(base_v.gini, 4)} xuống {f(v_full.gini, 4)}, nhưng danh sách vẫn tập trung vào một phần rất nhỏ "
    "danh mục."
)
P(
    f"Về độ chính xác, M1 đầy đủ thấp hơn mô hình nền {f(-t_full['mean_difference'])} NDCG@10 "
    f"(khoảng tin cậy 95% [{f(t_full['ci95_low'])}; {f(t_full['ci95_high'])}], p sau Holm "
    f"{pval(t_full['holm_p'])} trong họ bốn cặp khai báo trước), nên khác biệt không có ý nghĩa thống kê. "
    "Trong kiểm định bổ sung của hai biến thể còn lại so với mô hình nền (hiệu chỉnh Holm trong họ ba "
    f"cặp), chỉ đa dạng có p sau Holm {pval(t_div['holm_p'])}, chỉ phạt phổ biến có p sau Holm "
    f"{pval(t_pop['holm_p'])}; không biến thể nào khác mô hình nền có ý nghĩa. Trên tập xác thực, M1 "
    "đầy đủ tăng NDCG@10 0,52%, còn trên tập kiểm thử giảm 0,75%; cả hai thay đổi đều nhỏ và nằm trong "
    "ngưỡng 5% đặt trước."
)
ex_user = examples.user_id.iloc[0]
ex = examples[examples.user_id == ex_user]
P(
    f"Bảng 4.12 minh họa danh sách 10 nghệ sĩ của người dùng mã {ex_user} trước và sau M1. M1 thay một "
    "số nghệ sĩ rất phổ biến bằng nghệ sĩ có ít người nghe hơn nhưng gần với lịch sử của người dùng, "
    "đồng thời đổi thứ tự trong phần giữ lại. Ví dụ này được lấy là người dùng đầu tiên theo mã có ít "
    "nhất ba nghệ sĩ khác nhau giữa hai danh sách, không chọn theo kết quả."
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
    X
    + "m1_vi_du.csv. “(đúng)” là nghệ sĩ thuộc tập đích kiểm thử của người dùng; số người nghe tính trên tập huấn luyện.",
    align=["center", "left", "center", "left", "center"],
)
arp_drop = (1 - v_full.arp / base_v.arp) * 100
ndcg_drop = (1 - v_full.ndcg / base_v.ndcg) * 100
P(
    f"Trả lời RQ3: so với mô hình nền trên tập kiểm thử, M1 giảm ARP@10 {f(arp_drop, 2)}% và NDCG@10 "
    f"giảm {f(ndcg_drop, 2)}% nhưng không khác biệt có ý nghĩa thống kê. M1 giảm lệ thuộc vào nghệ sĩ phổ "
    "biến mà vẫn giữ độ chính xác; mức tăng đa dạng đo bằng thước đo độc lập theo thẻ nhỏ hơn mức tăng "
    "đo bằng ILD theo người nghe."
)

H2("4.8 Đánh giá mô-đun dự phòng M2")
P(
    "M2 được đánh giá theo giao thức người dùng mới ở mục 3.8.4. Người dùng của tập huấn luyện được chia "
    "thành nhóm học (1.501 người), nhóm tinh chỉnh (187 người) và nhóm để dành (189 người); mọi thành "
    "phần của M2 chỉ học từ nhóm học, với danh mục 13.210 nghệ sĩ. Với mỗi người dùng đánh giá, hệ thống "
    "chỉ nhận N ∈ {0, 1, 3, 5} nghệ sĩ từ lịch sử huấn luyện của chính họ, các hồ sơ lồng nhau theo một "
    "thứ tự xáo cố định. Trên tập xác thực của nhóm tinh chỉnh, cấu hình được chọn là α = "
    f"{f(m2_sel['winner']['alpha'], 2)} và n_min = {m2_sel['winner']['history_threshold']}, với NDCG@10 "
    f"trung bình ở N = 1, 3, 5 bằng {f(m2_sel['winner']['mean_ndcg_at_10'])}. Cấu hình này nằm ở góc của "
    "lưới, nghĩa là ở N ≤ 5 phần dự phòng chủ yếu dựa vào nội dung thẻ. Bảng 4.13 trình bày NDCG@10 trên "
    "tập kiểm thử của nhóm để dành, chấm một lần sau khi khóa cấu hình; 187 trên 189 người có đích trong "
    "danh mục và 14,59% cặp kiểm thử của nhóm này nằm ngoài danh mục học."
)
LAB = [
    ("popularity", "Popularity"),
    ("item_cf", "Chỉ ItemCF (L = 40)"),
    ("content", "Chỉ nội dung thẻ"),
    ("m2", "M2 (α = 0,75; n_min = 10)"),
]
m2_rows = []
for meth, label in LAB:
    row = [label]
    for n in [0, 1, 3, 5]:
        v = float(m2[(m2.method == meth) & (m2.n == n)].ndcg.iloc[0])
        row.append(f(v))
    m2_rows.append(row)
T(
    "NDCG@10 theo số nghệ sĩ được cung cấp (Given-N) trên nhóm để dành",
    [3188, 1400, 1400, 1400, 1400],
    ["Phương án", "N = 0", "N = 1", "N = 3", "N = 5"],
    m2_rows,
    D + "m2/test/metrics.csv (K = 10, 187 người có đích trong danh mục).",
)
F(
    X + "hinh/hinh_4_7.png",
    "NDCG@10 theo số nghệ sĩ được cung cấp của các phương án M2",
    D + "m2/test/metrics.csv.",
)
P(
    "Bảng 4.14 thống kê tần suất các đường xử lý của M2 ở từng mức N trên 189 người để dành: tỷ lệ yêu "
    "cầu có điểm nội dung, tỷ lệ chuyển hoàn toàn về mức phổ biến (không có điểm nội dung lẫn điểm cộng "
    "tác) và số nghệ sĩ đầu vào nằm ngoài ánh xạ của nhóm học."
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
    X + "m2_duong_xu_ly.csv (mô hình M2 đã khóa, cùng hồ sơ với lần chấm chính thức).",
)
stat = {(r["n"], r["b"]): r for r in m2_stats}
P(
    "Bảng 4.15 trình bày kiểm định của M2 so với từng phương án thành phần. Ở N = 0, mọi phương án trả "
    "đúng thứ tự Popularity nên có cùng giá trị NDCG@10; đây là kiểm tra tính đúng của cài đặt. Ở N = 1, "
    "3, 5, phương án chỉ dùng mức phổ biến có NDCG@10 cao nhất. Ở so sánh chính (N = 3), M2 thấp hơn "
    f"Popularity {f(-stat[(3, 'popularity')]['mean_difference'])}, khoảng tin cậy 95% "
    f"[{f(stat[(3, 'popularity')]['ci95_low'])}; {f(stat[(3, 'popularity')]['ci95_high'])}], p sau Holm "
    f"{pval(stat[(3, 'popularity')]['holm_p'])}. Bảng 4.14 giải thích một phần kết quả ở N = 1: "
    f"{int(paths.loc[1, 'nghe_si_dau_vao_ngoai_anh_xa'])} trên 189 người dùng có nghệ sĩ duy nhất nằm ngoài "
    f"ánh xạ, đúng bằng {f(paths.loc[1, 'chuyen_hoan_toan_pho_bien_pct'], 2)}% yêu cầu phải chuyển hoàn "
    "toàn về mức phổ biến."
)
st_rows = []
for n in [1, 3, 5]:
    for b, lab in [
        ("popularity", "Popularity"),
        ("content", "Chỉ nội dung thẻ"),
        ("item_cf", "Chỉ ItemCF"),
    ]:
        r = stat[(n, b)]
        label = f"M2 − {lab}" + (" (chính)" if (n, b) == (3, "popularity") else "")
        cells = [
            str(n),
            label,
            f(r["mean_difference"]),
            f"[{f(r['ci95_low'])}; {f(r['ci95_high'])}]",
            pval(r["holm_p"]),
        ]
        if (n, b) == (3, "popularity"):
            cells = [f"**{c}**" for c in cells]
        st_rows.append(cells)
T(
    "Kiểm định NDCG@10 của M2 trên tập kiểm thử (187 người dùng)",
    [600, 3088, 1500, 2400, 1200],
    ["N", "Cặp (A − B)", "Chênh lệch", "Khoảng tin cậy 95%", "p (Holm)"],
    st_rows,
    D + "m2/test/statistics_ndcg_at_10.json (chín cặp khai báo trước, hiệu chỉnh Holm).",
    align=["center", "left", "center", "center", "center"],
)
m2_n3 = m2[m2.n == 3].set_index("method")
P(
    "Kết quả trên tập xác thực và tập kiểm thử lệch nhau rõ. Trên 187 người tinh chỉnh, mức phổ biến chỉ "
    "đạt NDCG@10 từ 0,027627 đến 0,029728, còn trên 189 người để dành đạt từ 0,056508 đến 0,059750. Hai "
    "nhóm người dùng khác nhau và mỗi nhóm chưa tới 200 người, nên độ chính xác của cùng một phương pháp "
    "dao động mạnh giữa hai nhóm; cấu hình M2 chọn trên nhóm đầu không giữ được ưu thế ở nhóm sau. M2 "
    f"vẫn có tác dụng về đa dạng: ở N = 3, M2 tăng độ bao phủ từ {pct(m2_n3.loc['popularity'].catalog_coverage)} "
    f"lên {pct(m2_n3.loc['m2'].catalog_coverage)} và giảm ARP từ {f(m2_n3.loc['popularity'].arp, 2)} xuống "
    f"{f(m2_n3.loc['m2'].arp, 2)} so với Popularity. Trong các thành phần, nội dung thẻ đóng góp nhiều nhất "
    f"khi hồ sơ dài hơn: M2 hơn phương án chỉ dùng nội dung ở N = 1 có ý nghĩa (p sau Holm "
    f"{pval(stat[(1, 'content')]['holm_p'])}), còn thành phần ItemCF yếu dần khi N tăng."
)
P(
    "Trả lời RQ4: chưa tìm thấy bằng chứng M2 hỗ trợ người dùng ít lịch sử tốt hơn mức phổ biến về độ "
    "chính xác; M2 không vượt Popularity ở N nào trên tập kiểm thử, dù tăng độ bao phủ và giảm ARP. Về "
    "RQ2, khi số nghệ sĩ được cung cấp tăng từ 1 lên 3, NDCG@10 của M2 tăng từ "
    f"{f(float(m2[(m2.method == 'm2') & (m2.n == 1)].ndcg.iloc[0]))} lên "
    f"{f(float(m2[(m2.method == 'm2') & (m2.n == 3)].ndcg.iloc[0]))}, nhưng không tăng thêm ở N = 5 "
    f"({f(float(m2[(m2.method == 'm2') & (m2.n == 5)].ndcg.iloc[0]))}); phương án chỉ dùng nội dung tăng "
    "đều theo N, còn phương án chỉ dùng ItemCF giảm. Với cỡ mẫu 187 người, các xu hướng này chỉ mang tính "
    "mô tả."
)

H2("4.9 Thực nghiệm mở rộng với implicit ALS")
r_als = official_stats[("implicit_als", "pure_svd")]
P(
    "Implicit ALS [8] được cài đặt bằng thư viện implicit 0.7.3 [30], với độ tin cậy c_ui = 1 + ln(1 + "
    "lượt nghe), 32 nhân tố, hệ số điều chuẩn 0,1 và vòng tốt nhất là vòng 16 theo NDCG@10 xác thực. Khác "
    "với SVD có độ lệch, hàm mất mát của ALS đưa cả các ô chưa quan sát vào với độ tin cậy thấp, nên phù "
    f"hợp hơn với dữ liệu phản hồi ngầm. Trên tập kiểm thử, ALS đạt NDCG@10 {f(tm('implicit_als', 10, 'ndcg'))}, "
    f"cao hơn PureSVD {f(r_als['mean_difference'])} với khoảng tin cậy 95% [{f(r_als['ci95_low'])}; "
    f"{f(r_als['ci95_high'])}] và p sau Holm {pval(r_als['holm_p'])}. ALS cũng có độ bao phủ cao hơn "
    f"({pct(tm('implicit_als', 10, 'catalog_coverage'))} so với {pct(tm('pure_svd', 10, 'catalog_coverage'))}) "
    f"và ARP thấp hơn ({f(tm('implicit_als', 10, 'arp'), 2)} so với {f(tm('pure_svd', 10, 'arp'), 2)}). "
    f"Qua ba hạt giống, NDCG@10 của ALS là {f(seeds['implicit_als']['at_k']['10']['ndcg']['mean'])} ± "
    f"{f(seeds['implicit_als']['at_k']['10']['ndcg']['sample_std'])}."
)
P(
    "Dù ALS tốt hơn PureSVD có ý nghĩa thống kê, nhóm vẫn giữ PureSVD làm mô hình nền của M1. M1 được "
    "thiết kế, tinh chỉnh và khóa trên PureSVD trước khi mở tập kiểm thử; chuyển M1 sang ALS sau khi đã "
    "thấy kết quả kiểm thử sẽ là một lần chọn hậu kiểm. Nhóm có thử một hướng khử thiên lệch phổ biến "
    "trên ALS ở vòng xác thực: một cấu hình phạt phổ biến trực tiếp trên ALS đạt NDCG@10 xác thực "
    "0,1949, nhưng hướng khử thiên lệch dựa trên phổ của ma trận không vượt được phương án phạt trực tiếp "
    "và chưa được chấm trên tập kiểm thử. Áp dụng M1 trên ALS và chấm bằng một lần chia mới là hướng phát "
    "triển. Ứng dụng ở Chương 5 cho phép chọn cả PureSVD, M1 và ALS."
)

H2("4.10 Chi phí xử lý")
P(
    "Bảng 4.16 so sánh thời gian huấn luyện, thời gian tạo danh sách gợi ý và dung lượng mô hình của cấu "
    "hình đã chọn, đo trong lần chạy trên tập xác thực với một luồng tính toán trên máy đám mây. Thời gian "
    "tạo gợi ý là trung bình trên một người dùng. Các số này mô tả cấp độ chi phí trên một máy cụ thể, "
    "không phải phép đo hiệu năng có kiểm soát."
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
    D + "test/cost.csv. 1 MB = 1.000.000 byte.",
)
P(
    "PureSVD có chi phí thấp: huấn luyện dưới 0,2 giây và khoảng 2 ms cho mỗi danh sách gợi ý. SVD có độ "
    "lệch tốn thời gian huấn luyện nhất vì dùng SGD tuần tự trên từng cặp quan sát. M1 không cần huấn luyện "
    "lại mô hình nền; chi phí chính là lấy 100 ứng viên, còn bước tái xếp hạng chỉ khoảng 0,2 ms."
)

H2("4.11 Thảo luận")
P(
    "Về RQ1, PureSVD nhị phân là mô hình tốt nhất trong sáu mô hình đối sánh và là mô hình cá nhân hóa "
    f"duy nhất vượt Popularity, với NDCG@10 {f(pure)} so với {f(pop)}. Kết quả này phù hợp với nhận xét của "
    "Cremonesi và cộng sự [13] rằng PureSVD hoạt động tốt cho bài toán gợi ý top-N. Về RQ2, phép chia "
    "hiện tại gần như không có biến thiên về độ dài lịch sử; bằng chứng từ Given-N cho thấy chất lượng của "
    "M2 tăng từ N = 1 lên N = 3 rồi chững lại. Phân tích theo mức ưa chuộng nghệ sĩ phổ biến cho thấy biến "
    "thiên giữa người dùng lớn hơn nhiều so với biến thiên theo độ dài lịch sử. Về RQ3, M1 giảm ARP@10 "
    f"{f(arp_drop, 2)}% mà không làm giảm có ý nghĩa NDCG@10. Về RQ4, kết quả là âm: M2 không vượt Popularity "
    "về độ chính xác cho người dùng mới."
)
P(
    "Nhóm chưa đối chiếu con số với các công trình khác dùng dữ liệu Last.fm như [9], [24], [25], vì các "
    "công trình này dùng bộ dữ liệu con, giao thức chia, cách chọn đích và chỉ số khác nhau nên các con "
    "số không so sánh trực tiếp được. Điểm có thể đối chiếu là xu hướng: tương tự nhận xét của Kowald và "
    "cộng sự [9] về thiên lệch phổ biến trong gợi ý âm nhạc, người dùng ít ưa chuộng nghệ sĩ phổ biến "
    "nhận kết quả kém hơn rõ rệt ở mọi mô hình trong thực nghiệm của nhóm (Bảng 4.10)."
)
P(
    "Thực nghiệm có các giới hạn sau. Thứ nhất, chỉ có một lần chia ngẫu nhiên theo người dùng với hạt "
    "giống 42. Thứ hai, dữ liệu không có thời điểm của từng lượt nghe, nên phép chia không mô phỏng việc "
    "dự đoán lần nghe tiếp theo. Thứ ba, danh sách nghệ sĩ của mỗi người dùng bị giới hạn ở những nghệ sĩ "
    "nghe nhiều nhất. Thứ tư, điểm đại diện 1–5 do nhóm quy đổi từ lượt nghe, nên RMSE chỉ đo khả năng dự "
    "đoán mức lượt nghe tương đối của các cặp đã nghe. Thứ năm, ILD theo người nghe dùng cùng độ tương đồng "
    "với hàm lựa chọn của M1; ILD theo thẻ chỉ tính được cho khoảng một phần ba danh mục có thẻ. Thứ sáu, "
    "cấu hình tốt nhất của một số mô hình nằm ở biên lưới, và giao thức người dùng mới chỉ có chưa tới 200 "
    "người mỗi nhóm."
)
P(
    "Từ các kết quả trên, ứng dụng ở Chương 5 dùng PureSVD làm mô hình mặc định cho người dùng có sẵn, cho "
    "bật M1 khi muốn giảm thiên lệch phổ biến, dùng M2 với cơ chế dự phòng về mức phổ biến cho người dùng "
    "mới, và cho chọn ALS như mô hình có độ chính xác cao nhất đã đo."
)

H2("4.12 Kết luận chương")
P(
    "Chương 4 đã trình bày kết quả tinh chỉnh và đánh giá các mô hình trên cùng giao thức. Kết quả cho thấy "
    f"PureSVD nhị phân với k = 16 đạt NDCG@10 cao nhất trong sáu mô hình đối sánh trên tập kiểm thử ({f(pure)}), "
    f"hơn Popularity {f(official_stats[('pure_svd', 'popularity')]['mean_difference'])} và khác biệt có ý nghĩa "
    "thống kê; UserCF, ItemCF và SVD có độ lệch không vượt được Popularity. Mô-đun M1 với λ = 0,75 và β = 0,5 "
    f"làm ARP giảm {f(arp_drop, 2)}% với mức giảm NDCG@10 {f(ndcg_drop, 2)}% không có ý nghĩa thống kê. "
    "Mô-đun M2 chưa vượt Popularity về NDCG@10 ở N = 1, 3 và 5, dù tăng độ bao phủ và giảm ARP. Thực "
    "nghiệm mở rộng cho thấy implicit ALS vượt PureSVD có ý nghĩa thống kê. Chương 5 trình bày việc đóng gói "
    "các mô hình đã chọn thành dịch vụ và giao diện minh họa."
)
