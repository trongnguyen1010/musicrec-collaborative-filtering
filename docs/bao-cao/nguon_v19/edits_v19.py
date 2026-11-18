# ruff: noqa: E501, F821
# Edits outside Chapters 2-4 for report v19, run by build_v19.py after the chapter rebuild.
# Scope: references [39]-[43], cross-references that the renumbering forces, Appendix A.4 (log-style
# details moved out of Section 3.5) and Appendix D.1 (full ranking table cited in Section 4.5).
import pandas as _pd


def cur_find(prefix):
    for e in body:
        if e.tag == q("p") and text(e).startswith(prefix):
            return e
    raise KeyError(prefix)


def replace_in_runs(old, new, scope=None):
    hits = 0
    for t in (scope if scope is not None else body).iter(q("t")):
        if t.text and old in t.text:
            t.text = t.text.replace(old, new)
            hits += 1
    return hits


def insert_after(anchor, elements):
    for e in elements:
        anchor.addnext(e)
        anchor = e
    return anchor


def collect(fn):
    """Run content helpers (P, H2, T, ...) and return the elements they produce."""
    start = len(content)
    fn()
    made = content[start:]
    del content[start:]
    return made


# ---- references [39]-[43] after [38] ----
ref38 = cur_find("[38] He, X.")
ref_rpr = copy.deepcopy(ref38.find("w:r/w:rPr", NS))
refs = [
    "[39] Deshpande, M., & Karypis, G. (2004). Item-based top-N recommendation algorithms. ACM Transactions on Information Systems, 22(1), 143–177. https://doi.org/10.1145/963770.963776",
    "[40] Breese, J. S., Heckerman, D., & Kadie, C. (1998). Empirical analysis of predictive algorithms for collaborative filtering. In Proceedings of the 14th Conference on Uncertainty in Artificial Intelligence (UAI ’98), 43–52.",
    "[41] Cantador, I., Brusilovsky, P., & Kuflik, T. (2011). Second workshop on information heterogeneity and fusion in recommender systems (HetRec 2011). In Proceedings of the 5th ACM Conference on Recommender Systems (RecSys ’11), 387–388.",
    "[42] Schuirmann, D. J. (1987). A comparison of the two one-sided tests procedure and the power approach for assessing the equivalence of average bioavailability. Journal of Pharmacokinetics and Biopharmaceutics, 15(6), 657–680.",
    "[43] Kerby, D. S. (2014). The simple difference formula: An approach to teaching nonparametric correlation. Comprehensive Psychology, 3, 11.IT.3.1.",
]
anchor = ref38
for s in refs:
    p = fill(strip_ids(copy.deepcopy(ref38)), s, rpr=ref_rpr)
    anchor.addnext(p)
    anchor = p
for prefix in ["[39] Deshpande", "[40] Breese", "[41] Cantador", "[42] Schuirmann", "[43] Kerby"]:
    for e in list(body):
        if (
            e.tag == q("p")
            and text(e).startswith(prefix)
            and e.find(".//w:color[@w:val='0000FF']", NS) is not None
        ):
            body.remove(e)

# ---- cross-references forced by renumbering ----
appendix_b = cur_find("Xét danh mục minh họa gồm bốn nghệ sĩ")
assert replace_in_runs("công thức (2.16)", "công thức (2.22)", appendix_b) == 1
ch5_start = list(body).index(cur_find("CHƯƠNG 5 XÂY DỰNG"))
for e in list(body)[ch5_start:]:
    replace_in_runs("Bảng 3.3", "Bảng 3.5", e)

# ---- Appendix A.4: details moved out of Section 3.5 ----
a3_text = cur_find("Gói phục vụ phải chứa đúng danh mục")


def _a4():
    H2("A.4 Chi tiết kiểm tra dữ liệu")
    P(
        "Bảng tương tác và bảng nghệ sĩ được đọc theo bảng mã UTF-8, còn từ điển thẻ được đọc theo bảng mã "
        "ISO-8859-1 (Latin-1). Tám giá trị thẻ ngoài ASCII như español và rock français được giữ đúng ký tự; "
        "quy trình không dùng cơ chế bỏ hoặc thay ký tự lỗi. Bản ghi tương tác trùng hoàn toàn chỉ giữ một, "
        "còn cùng một cặp với số lượt nghe khác nhau sẽ làm quy trình dừng; dữ liệu thực tế không có trường "
        "hợp nào. Số lượt nghe được giữ ở kiểu số nguyên 64 bit."
    )
    P(
        "Tệp nén chính thức của GroupLens được tải lại và so sánh với bản đang dùng; hai bản trùng từng byte. "
        "Con số 1.538 dòng gán thẻ không nối được danh mục (thuộc 390 mã nghệ sĩ) được nhóm kiểm tra trên tệp "
        "này, vì các mã tiền xử lý đã công bố của [24] và [25] không ghi trực tiếp con số đó. Tên hiển thị "
        "dự phòng được chuẩn bị cho nghệ sĩ thiếu tên, nhưng dữ liệu nguồn không có trường hợp này."
    )
    P(
        "Sau khi chia tập, một kiểm tra độc lập xác nhận ba tập không giao cặp người dùng–nghệ sĩ, bảo toàn đủ "
        "92.801 tương tác và từng giá trị lượt nghe. Kiểm tra độc lập cũng tính lại từng giá trị biến đổi và "
        "tọa độ ma trận. Chạy lại cùng hạt giống cho các tệp dữ liệu và ánh xạ trùng mã băm; ở bước biến đổi, "
        "chín tệp dữ liệu, ánh xạ và quy tắc biến đổi trùng mã băm với lần chạy trước."
    )


insert_after(a3_text, collect(_a4))

# ---- Appendix D.1: full ranking table (Section 4.5) ----
_test = _pd.read_csv("docs/results/chinh_thuc_cloud_20261026/test/metrics.csv")
_test = _test[_test.seed == 42]
_names = [
    ("random", "Random"),
    ("popularity", "Popularity"),
    ("user_cf", "UserCF"),
    ("item_cf", "ItemCF"),
    ("svd", "SVD có độ lệch"),
    ("pure_svd", "PureSVD"),
    ("m1", "M1"),
    ("implicit_als", "Implicit ALS"),
]


def _v(m, k, c):
    x = float(_test[(_test.model == m) & (_test.k == k)][c].iloc[0])
    return f"{x:.4f}".replace(".", ",")


blue_d = [e for e in body if e.tag == q("p") and text(e).startswith("PHỤ LỤC D BẢNG KẾT QUẢ")]
anchor_d = blue_d[0]


def _d():
    CHAPTER("D")
    H1("PHỤ LỤC D BẢNG KẾT QUẢ ĐẦY ĐỦ")
    H2("D.1 Chỉ số xếp hạng của tám mô hình trên tập kiểm thử")
    P(
        "Bảng D.1 trình bày Precision, Recall và NDCG tại K = 5, 10 và 20 của tám mô hình trên tập kiểm thử, "
        "hạt giống 42, tính trên 1.855 người dùng có đích hợp lệ (mục 4.5)."
    )
    T(
        "Precision, Recall và NDCG tại K = 5, 10, 20 trên tập kiểm thử",
        [1640, 794, 794, 794, 794, 794, 794, 794, 794, 790],
        ["Mô hình", "P@5", "P@10", "P@20", "R@5", "R@10", "R@20", "N@5", "N@10", "N@20"],
        [
            [lab] + [_v(m, k, c) for c in ["precision", "recall", "ndcg"] for k in [5, 10, 20]]
            for m, lab in _names
        ],
        note="N@K là NDCG@K; giá trị làm tròn bốn chữ số thập phân (giá trị sáu chữ số của K = 10 ở Bảng 4.5). M1 và Implicit ALS là hai thực nghiệm bổ sung trên cùng giao thức.",
        size=18,
    )


insert_after(anchor_d, collect(_d))
for e in blue_d:
    body.remove(e)
