# ruff: noqa: E501, F821
# Phase 3 edits for report v20 (advisor feedback of 10/11/2026), run by build_v19.py after
# edits_v19.py: covers, Tóm tắt, Abstract, Lời cam đoan, lists of abbreviations and symbols,
# Chapter 1, Chapter 5 split into Chapters 5 and 6, references, Appendices C and D, and the
# removal of every advisor note left in the document. Indices refer to the advisor's copy.
import json as _json

import pandas as _pd

FIG = "docs/results/chinh_thuc_cloud_20261026/bo_sung_2/hinh_bao_cao/"
LOAD = _json.loads(open("docs/results/chuong_5/load_test.json", encoding="utf-8").read())
EXAMPLE = _json.loads(open("docs/results/chuong_5/vi_du_recommend.json", encoding="utf-8").read())
TITLE_VI = "MUSICREC: XÂY DỰNG HỆ THỐNG KHUYẾN NGHỊ NGHỆ SĨ DỰA TRÊN LỌC CỘNG TÁC"
TITLE_VI_SENT = "MusicRec: Xây dựng hệ thống khuyến nghị nghệ sĩ dựa trên lọc cộng tác"


def vn(x, d=2):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def set_text(p, s, bold=None):
    """Put s in the first run of p (creating one from the paragraph mark formatting if empty)."""
    runs = p.findall("w:r", NS)
    if runs:
        for r in runs[1:]:
            p.remove(r)
        r = runs[0]
        for t in r.findall("w:t", NS):
            r.remove(t)
        for br in r.findall("w:br", NS):
            r.remove(br)
    else:
        r = etree.SubElement(p, q("r"))
        mark = p.find("w:pPr/w:rPr", NS)
        if mark is not None:
            r.append(copy.deepcopy(mark))
    t = etree.SubElement(r, q("t"))
    t.text = s
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return p


def remove(*elements):
    for e in elements:
        if e.getparent() is not None:
            e.getparent().remove(e)


def sub_text(e, old, new):
    hits = [t for t in e.iter(q("t")) if t.text and old in t.text]
    if not hits:
        raise KeyError(f"'{old}' not found")
    for t in hits:
        t.text = t.text.replace(old, new)


def heading_like(tpl_index, text_):
    p = blacken(strip_ids(copy.deepcopy(ORIG[tpl_index])))
    return set_text(p, text_)


def para_like(tpl_index, text_):
    p = blacken(strip_ids(copy.deepcopy(ORIG[tpl_index])))
    rpr = copy.deepcopy(p.find("w:r/w:rPr", NS))
    return fill(p, text_, rpr=rpr)


# =====================================================================================
# Covers (main, sub, English)
# =====================================================================================
for name_i, line_i, title_i, date_i in [(7, 9, 11, 20), (30, 32, 33, 42)]:
    set_text(ORIG[name_i], "CAO TRỌNG NGUYỄN – MSSV: 22671461")
    set_text(ORIG[name_i + 1], "LÊ KHẮC GIA KHANG – MSSV: 22690991")
    set_text(ORIG[line_i], "LỚP: DHKHMT18BTT – KHÓA: 18")
    set_text(ORIG[title_i], TITLE_VI)
    set_text(ORIG[date_i], "THÀNH PHỐ HỒ CHÍ MINH, THÁNG 12 NĂM 2026")
for title_i in (11, 33):
    ppr = ORIG[title_i].find("w:pPr", NS)
    ind = ppr.find("w:ind", NS)
    if ind is None:
        ind = etree.Element(q("ind"))
        ppr.find("w:jc", NS).addprevious(ind)
    ind.attrib.clear()
    ind.set(q("firstLine"), "0")
set_text(ORIG[52], "CAO TRONG NGUYEN – STUDENT ID: 22671461")
set_text(ORIG[53], "LE KHAC GIA KHANG – STUDENT ID: 22690991")
set_text(ORIG[54], "CLASS: DHKHMT18BTT – COHORT: 18")
set_text(ORIG[63], "HO CHI MINH CITY, DECEMBER 2026")
remove(ORIG[21])

# =====================================================================================
# Tóm tắt (before Abstract), Abstract, Lời cam đoan (after Abstract)
# =====================================================================================
TOMTAT = [
    "Các dịch vụ nghe nhạc trực tuyến cung cấp kho nội dung lớn hơn nhiều so với khả năng khám phá của mỗi người nghe, vì vậy hệ thống khuyến nghị giúp người dùng tìm được những nghệ sĩ phù hợp với sở thích. Khóa luận xây dựng và đánh giá một hệ thống khuyến nghị nghệ sĩ dựa trên lọc cộng tác, sử dụng số lượt nghe trong bộ dữ liệu Last.fm HetRec 2011 làm phản hồi ngầm.",
    "Sau khi làm sạch, dữ liệu gồm 1.877 người dùng và 92.801 cặp người dùng–nghệ sĩ, được chia theo từng người dùng thành tập huấn luyện, xác thực và kiểm thử. Sáu mô hình đối sánh (Random, Popularity, lọc cộng tác dựa trên người dùng, lọc cộng tác dựa trên nghệ sĩ, SVD có độ lệch và PureSVD) được tinh chỉnh trên tập xác thực theo NDCG@10 và khóa cấu hình trước khi mở tập kiểm thử. Khóa luận đề xuất hai mô-đun: M1 là bộ tái xếp hạng tham lam theo tinh thần độ liên quan biên cực đại, có thêm thành phần phạt mức phổ biến; M2 là cơ chế dự phòng lai cho người dùng mới, kết hợp điểm ItemCF, thẻ nghệ sĩ và mức phổ biến, được đánh giá theo giao thức Given-N. Implicit ALS được thực hiện như một thực nghiệm mở rộng. Việc đánh giá dùng các chỉ số xếp hạng và các chỉ số ngoài độ chính xác, kèm kiểm định Wilcoxon theo cặp, hiệu chỉnh Holm, khoảng tin cậy bootstrap, cỡ hiệu ứng và kiểm định tương đương.",
    "Trên tập kiểm thử, với cấu hình đã khóa, PureSVD đạt NDCG@10 cao nhất trong sáu mô hình đối sánh (0,1828 so với 0,0688 của Popularity, khác biệt có ý nghĩa thống kê), còn các mô hình láng giềng và SVD có độ lệch không vượt được Popularity. Phân tích bổ sung sau khi khóa cấu hình cho thấy kết luận về mô hình láng giềng phụ thuộc cách tổng hợp điểm: khi chấm điểm theo kiểu top-N, UserCF và ItemCF đạt 0,1937 và 0,1940, vượt PureSVD có ý nghĩa. M1 giảm độ phổ biến trung bình của danh sách gợi ý 15,69% và tương đương PureSVD về NDCG@10 theo kiểm định tương đương ở biên 5%; M1 cải thiện độ chính xác cho nhóm người dùng ít ưa chuộng nghệ sĩ phổ biến. M2 chưa vượt Popularity khi tập đích là các cặp kiểm thử, nhưng vượt Popularity ở N = 3 và N = 5 khi tập đích là toàn bộ nghệ sĩ người dùng chưa cung cấp. Implicit ALS đạt NDCG@10 0,2175, cao nhất trong các mô hình đã đo. Các mô hình được đóng gói thành dịch vụ FastAPI và giao diện Next.js; danh sách gợi ý trên ứng dụng trùng hoàn toàn với đánh giá ngoại tuyến, thời gian phản hồi trung vị từ 3,8 đến 11,5 ms trên máy tính cá nhân.",
    "**Từ khóa:** khuyến nghị âm nhạc, lọc cộng tác, phản hồi ngầm, thiên lệch phổ biến, khởi động nguội, Last.fm.",
]
abstract_head = ORIG[64]
for e in [heading_like(64, "TÓM TẮT")] + [para_like(66, s) for s in TOMTAT]:
    abstract_head.addprevious(e)
fill(
    ORIG[67],
    "After cleaning, the data contain 1,877 users and 92,801 user–artist pairs, split per user into training, validation and test sets. Six comparison models (Random, Popularity, user-based and item-based collaborative filtering, biased SVD and PureSVD) were tuned on the validation set by NDCG@10 and locked before the test set was opened. Two modules were added: M1, a greedy re-ranker in the spirit of maximal marginal relevance with a popularity penalty, and M2, a hybrid fallback for new users that combines item-based scores, artist tags and popularity, evaluated with a Given-N protocol. Implicit ALS was run as an extension. Evaluation used ranking and beyond-accuracy metrics with paired Wilcoxon tests, Holm correction, bootstrap confidence intervals, effect sizes and an equivalence test.",
    rpr=copy.deepcopy(ORIG[67].find("w:r/w:rPr", NS)),
)
fill(
    ORIG[68],
    "On the test set, with the locked configurations, PureSVD achieved the highest NDCG@10 among the six models (0.1828 against 0.0688 for Popularity, a significant difference), while the neighbourhood models and biased SVD did not beat Popularity. A supplementary analysis after locking showed that this depends on how neighbourhood scores are aggregated: with top-N scoring, user-based and item-based CF reached 0.1937 and 0.1940, significantly above PureSVD. M1 reduced average recommendation popularity by 15.69% and was equivalent to PureSVD in NDCG@10 under a two one-sided test with a 5% margin; it improved accuracy for users with little interest in popular artists. M2 did not beat Popularity when the targets were the held-out test pairs, but it did at N = 3 and N = 5 when the targets were all artists the user had not supplied. Implicit ALS reached 0.2175, the best model measured. The models were packaged as a FastAPI service with a Next.js interface whose recommendation lists match the offline evaluation exactly, with median response times between 3.8 and 11.5 ms on a personal computer.",
    rpr=copy.deepcopy(ORIG[68].find("w:r/w:rPr", NS)),
)
CAMDOAN = [
    f"Chúng em xin cam đoan khóa luận “{TITLE_VI_SENT}” là công trình do chúng em thực hiện dưới sự hướng dẫn của TS. Lê Thị Vĩnh Thanh. Các số liệu và kết quả thực nghiệm trong khóa luận là trung thực, được tạo ra từ mã nguồn và dữ liệu do nhóm thực hiện, chưa từng được công bố trong công trình nào khác. Các nội dung tham khảo, kế thừa từ tài liệu, bộ dữ liệu và thư viện mã nguồn mở đều được trích dẫn đầy đủ.",
    "Trong quá trình thực hiện, nhóm có sử dụng công cụ trí tuệ nhân tạo Claude (Anthropic) và Codex (OpenAI), chủ yếu để hỗ trợ triển khai dự án, viết báo cáo và lập trình. Mọi nội dung, số liệu và mã nguồn có sự hỗ trợ của các công cụ này đều được nhóm kiểm tra, đối chiếu với kết quả chạy thật và chịu trách nhiệm.",
    "Nếu có sai phạm, chúng em xin hoàn toàn chịu trách nhiệm.",
]
anchor = ORIG[69]
for e in [heading_like(64, "LỜI CAM ĐOAN")] + [para_like(66, s) for s in CAMDOAN]:
    anchor.addnext(e)
    anchor = e
sign = [
    para_like(96, "Thành phố Hồ Chí Minh, ngày … tháng … năm 2026"),
    para_like(97, "Sinh viên thực hiện (ký và ghi rõ họ tên)"),
    para_like(97, "Cao Trọng Nguyễn          Lê Khắc Gia Khang"),
]
for e in sign:
    anchor.addnext(e)
    anchor = e
remove(*ORIG[70:79])

# =====================================================================================
# Lists of abbreviations and symbols; advisor's general block
# =====================================================================================
abbr = ORIG[287]
rows = abbr.findall("w:tr", NS)


def new_row(template_tr, cells):
    tr = strip_ids(copy.deepcopy(template_tr))
    for tc, val in zip(tr.findall("w:tc", NS), cells, strict=True):
        p = tc.find("w:p", NS)
        for extra in tc.findall("w:p", NS)[1:]:
            tc.remove(extra)
        rpr = copy.deepcopy(p.find("w:r/w:rPr", NS))
        fill(p, val, rpr=rpr)
    return tr


rows[1].addprevious(
    new_row(rows[1], ["ALS", "Alternating Least Squares", "Bình phương tối thiểu luân phiên"])
)
tfidf = next(r for r in rows if "TF–IDF" in text(r))
tfidf.addnext(new_row(tfidf, ["TOST", "Two One-Sided Tests", "Kiểm định tương đương hai phía"]))
sym = ORIG[289]
last = sym.findall("w:tr", NS)[-1]
SYMBOLS = [
    ("⟦H_u⟧", "Lịch sử huấn luyện (các nghệ sĩ đã biết) của người dùng u."),
    ("⟦N_i^L (u), N^L (i)⟧", "Láng giềng người dùng của u đã nghe i; L nghệ sĩ gần nhất của i."),
    ("⟦γ, n_uv⟧", "Hệ số co rút và số đối tượng chung của hai người dùng hoặc hai nghệ sĩ."),
    (
        "⟦p_ui, c_ui, a⟧",
        "Sở thích nhị phân, độ tin cậy và hệ số độ tin cậy a_conf của implicit ALS.",
    ),
    ("⟦x_u, y_i⟧", "Véc-tơ nhân tố người dùng và nghệ sĩ của implicit ALS."),
    ("⟦θ_1, …, θ_4⟧", "Bốn ngưỡng phân vị của log-count dùng để tạo điểm đại diện."),
    ("⟦s ̃_ui, p ̃_i⟧", "Điểm nền và mức phổ biến đã chuẩn hóa trong M1."),
    ("⟦d_u, W^+, W^-, r_rb⟧", "Chênh lệch theo người dùng, tổng hạng Wilcoxon và cỡ hiệu ứng."),
    ("⟦μ_d, δ⟧", "Chênh lệch trung bình và biên tương đương của TOST."),
    (
        "⟦P_u^((N)), T_u^N, ℐ_learn⟧",
        "Hồ sơ N nghệ sĩ, tập đích Given-N và danh mục nhóm học của M2.",
    ),
    ("⟦θ, θ^*⟧", "Cấu hình của mô hình và cấu hình được chọn trên tập xác thực."),
]
anchor = last
for sym_, meaning in SYMBOLS:
    row = new_row(last, [sym_, meaning])
    anchor.addnext(row)
    anchor = row
remove(*ORIG[291:322])

# =====================================================================================
# Chapter 1
# =====================================================================================
sub_text(
    ORIG[324],
    "số người dùng tài khoản đăng ký trả phí đạt 837 triệu",
    "số người dùng tài khoản đăng ký nghe nhạc trực tuyến trả phí đạt 837 triệu",
)
sub_text(ORIG[335], "(mục 4.8)", "(mục 4.8 và 4.11)")
remove(ORIG[331])


def _formal():
    P(
        "Gọi ⟦𝒰⟧ là tập người dùng, ⟦ℐ⟧ là danh mục nghệ sĩ và ⟦Ω⊂𝒰×ℐ⟧ là tập cặp đã quan sát, mỗi cặp ⟦(u,i)⟧ kèm số lượt nghe ⟦w_ui>0⟧. Dữ liệu được chia thành ba phần rời nhau:"
    )
    EQ(344, "1.1")
    P(
        "Với mỗi người dùng ⟦u⟧, gọi ⟦H_u={i:(u,i)∈Ω_train}⟧ là lịch sử hệ thống được biết và ⟦ℐ_train⟧ là danh mục nghệ sĩ có tương tác huấn luyện. Một mô hình ⟦f⟧ với cấu hình ⟦θ⟧ học từ ⟦Ω_train⟧ và gán điểm ⟦s_ui=f_θ (u,i)⟧ cho mọi ứng viên chưa có trong lịch sử. Danh sách gợi ý độ dài ⟦K⟧ gồm ⟦K⟧ ứng viên có điểm cao nhất:"
    )
    EQ(346, "1.2")
    P(
        "Với tập đích ⟦T_u⟧ gồm các nghệ sĩ của ⟦u⟧ trong tập đánh giá thuộc ⟦ℐ_train⟧, cấu hình được chọn trên tập xác thực để cực đại chất lượng xếp hạng trung bình:"
    )
    EQ(348, "1.3")
    P(
        "Trong công thức (1.3), ⟦𝒰_val⟧ là tập người dùng có ít nhất một đích xác thực hợp lệ. Cấu hình ⟦θ^*⟧ được khóa trước khi đánh giá trên tập kiểm thử; khi kiểm thử, các nghệ sĩ bị loại khỏi tập ứng viên gồm cả ⟦H_u⟧ và lịch sử xác thực của người dùng. Bên cạnh NDCG@10, hệ thống được mô tả thêm bằng độ bao phủ, mức phổ biến, độ mới và độ đa dạng (mục 2.5)."
    )


insert_after(ORIG[340], collect(_formal))
remove(*ORIG[342:350])


def _contrib():
    H2("1.7 Đóng góp của khóa luận")
    P(
        "Thứ nhất, khóa luận xây dựng một quy trình thực nghiệm có thể tái lập trên Last.fm HetRec 2011: ánh xạ và ngưỡng biến đổi chỉ học từ tập huấn luyện, đích ngoài danh mục được báo cáo riêng, cấu hình được khóa trước khi mở tập kiểm thử và bộ đánh giá được kiểm chứng bằng ví dụ tính tay cùng thư viện chuẩn."
    )
    P(
        "Thứ hai, khóa luận so sánh sáu mô hình đối sánh và implicit ALS trên cùng giao thức, kèm kiểm định Wilcoxon theo cặp, hiệu chỉnh Holm, khoảng tin cậy bootstrap và cỡ hiệu ứng. Với cấu hình đã khóa, PureSVD là mô hình đối sánh duy nhất vượt Popularity; phân tích bổ sung chỉ ra rằng kết quả kém của UserCF và ItemCF đến từ cách tổng hợp điểm dự đoán, vì khi tổng hợp theo kiểu top-N hai mô hình này vượt cả PureSVD."
    )
    P(
        "Thứ ba, khóa luận đề xuất mô-đun tái xếp hạng M1 kết hợp ý tưởng MMR với phạt mức phổ biến. M1 giảm ARP@10 15,69% và tương đương mô hình nền về NDCG@10 theo kiểm định tương đương ở biên 5%, đồng thời cải thiện độ chính xác cho nhóm người dùng ít ưa chuộng nghệ sĩ phổ biến. Khóa luận cũng chỉ ra và xử lý tính vòng tròn khi dùng cùng độ tương đồng cho hàm lựa chọn và chỉ số ILD."
    )
    P(
        "Thứ tư, khóa luận xây dựng mô-đun dự phòng M2 cho người dùng mới với giao thức Given-N tách biệt người dùng học và người dùng đánh giá. Kết quả cho thấy đánh giá M2 phụ thuộc định nghĩa tập đích: M2 không vượt Popularity khi đích là các cặp kiểm thử, nhưng vượt Popularity ở N = 3 và N = 5 khi đích là toàn bộ nghệ sĩ người dùng chưa cung cấp."
    )
    P(
        "Thứ năm, khóa luận đóng gói các mô hình thành dịch vụ FastAPI và giao diện Next.js có danh sách gợi ý trùng hoàn toàn với đánh giá ngoại tuyến."
    )


insert_after(ORIG[374], collect(_contrib))
remove(*ORIG[375:382])
set_text(ORIG[382], "1.8 Cấu trúc báo cáo")
sub_text(ORIG[383], "năm chương", "sáu chương")
fill(
    ORIG[385],
    "Chương 2: Cơ sở lý thuyết. Giới thiệu hệ thống khuyến nghị, phản hồi ngầm, lọc cộng tác dựa trên láng giềng và các mô hình nhân tố tiềm ẩn (SVD có độ lệch, PureSVD, implicit ALS), cùng các vấn đề khởi động nguội, thiên lệch phổ biến và tái xếp hạng. Chương này cũng trình bày các thước đo đánh giá, các phương pháp kiểm định thống kê và các nghiên cứu liên quan.",
    rpr=copy.deepcopy(ORIG[385].find("w:r/w:rPr", NS)),
)
fill(
    ORIG[387],
    "Chương 4: Huấn luyện và thực nghiệm đánh giá. Trình bày môi trường thực nghiệm, dữ liệu sau tiền xử lý, quá trình tinh chỉnh tham số trên tập xác thực và kết quả so sánh các mô hình trên tập kiểm thử kèm kiểm định thống kê. Chương này đánh giá M1, M2 và thực nghiệm mở rộng với implicit ALS, phân tích kết quả theo nhóm người dùng, chi phí xử lý, các phân tích bổ sung sau khi khóa cấu hình và trả lời các câu hỏi RQ1 đến RQ4.",
    rpr=copy.deepcopy(ORIG[387].find("w:r/w:rPr", NS)),
)
fill(
    ORIG[388],
    "Chương 5: Xây dựng hệ thống. Mô tả cách tổ chức mã nguồn, đóng gói và nạp mô hình, dịch vụ API bằng FastAPI và giao diện minh họa bằng Next.js. Chương này trình bày kết quả kiểm thử chức năng, đối chiếu kết quả trên ứng dụng với đánh giá ngoại tuyến (RQ5), thời gian phản hồi và kiểm thử tải.",
    rpr=copy.deepcopy(ORIG[388].find("w:r/w:rPr", NS)),
)
ORIG[388].addnext(
    para_like(
        388,
        "Chương 6: Kết luận và hướng phát triển. Đối chiếu mục tiêu với kết quả đạt được, tóm tắt câu trả lời cho RQ1 đến RQ5, nêu các hạn chế và hướng phát triển của đề tài.",
    )
)
remove(*ORIG[389:392])
fill(
    ORIG[392],
    "Phần tài liệu tham khảo liệt kê các công trình và nguồn thông tin được trích dẫn trong báo cáo. Các phụ lục trình bày quy ước cấu hình và tệp kết quả, ví dụ kiểm tra bộ đánh giá, hướng dẫn cài đặt và chạy lại, và các bảng kết quả đầy đủ.",
    rpr=copy.deepcopy(ORIG[392].find("w:r/w:rPr", NS)),
)

# =====================================================================================
# Chapters 5 and 6 (rebuilt from the advisor's copy)
# =====================================================================================
counters["DoanMa"] = 0


def CODECAP(title):
    p = _caption(cap_tpl, f"Đoạn mã {chapter[0]}.", "DoanMa", title)
    content.append(p)


def CODE(lines):
    """Monospace block (Consolas 10 pt), single spacing, light grey shading."""
    for line in lines:
        p = fill(copy.deepcopy(body_tpl), "")
        rpr = etree.Element(q("rPr"))
        fonts = etree.SubElement(rpr, q("rFonts"))
        for attr in ["ascii", "hAnsi", "cs", "eastAsia"]:
            fonts.set(q(attr), "Consolas")
        for tag in ["sz", "szCs"]:
            etree.SubElement(rpr, q(tag)).set(q("val"), "20")
        p.append(make_run(line or " ", rpr=rpr))
        ppr = p.find("w:pPr", NS)
        for tag in ["spacing", "ind", "jc", "shd"]:
            for el in ppr.findall(f"w:{tag}", NS):
                ppr.remove(el)
        etree.SubElement(ppr, q("shd")).attrib.update(
            {q("val"): "clear", q("color"): "auto", q("fill"): "F2F2F2"}
        )
        etree.SubElement(ppr, q("spacing")).attrib.update(
            {q("before"): "0", q("after"): "0", q("line"): "240", q("lineRule"): "auto"}
        )
        etree.SubElement(ppr, q("ind")).attrib.update({q("left"): "284", q("firstLine"): "0"})
        etree.SubElement(ppr, q("jc")).set(q("val"), "left")
        content.append(p)


def _ch5():
    CHAPTER(5)
    content.append(heading_like(898, "CHƯƠNG 5 XÂY DỰNG HỆ THỐNG"))
    P(
        "Chương này trình bày cách tổ chức mã nguồn và đóng gói mô hình, thiết kế dịch vụ API bằng FastAPI [32], giao diện minh họa bằng Next.js [33] và kết quả kiểm thử hệ thống. Hệ thống sử dụng các mô hình đã khóa cấu hình trong Chương 4."
    )
    H2("5.1 Kiến trúc triển khai")
    H3("5.1.1 Tổ chức mã nguồn")
    KEEP(905)
    FKEEP(906, "Tổ chức mã nguồn của hệ thống")
    P(
        "Hình 5.2 trình bày sơ đồ thành phần và triển khai. Trình duyệt chỉ giao tiếp với giao diện Next.js; giao diện gọi dịch vụ FastAPI qua HTTP và nhận JSON. Dịch vụ chuyển yêu cầu cho lớp DemoService, lớp này định tuyến sang mô hình phù hợp trong gói mô hình đã nạp. Gói mô hình chỉ được nạp một lần khi dịch vụ khởi động và mọi tệp đều được kiểm tra mã băm. Giao diện Streamlit dùng chung DemoService và chỉ giữ làm phương án dự phòng."
    )
    F(FIG + "trien_khai.png", "Sơ đồ thành phần và triển khai của hệ thống", width_cm=15.5)
    P(
        "Mọi mô hình kế thừa cùng một lớp trừu tượng Recommender với ba phương thức huấn luyện (fit), dự đoán điểm (predict) và gợi ý (recommend); mỗi lớp cài đặt thêm save và load để lưu, nạp mô hình mà không huấn luyện lại (Hình 5.3). M1 nhận một mô hình nền và tái xếp hạng tập ứng viên của nó, còn M2 chứa một ItemCF và nhận hồ sơ người dùng mới qua set_profile. Nhờ giao diện chung, bộ đánh giá ngoại tuyến và dịch vụ trực tuyến gọi các mô hình theo cùng một cách."
    )
    F(FIG + "so_do_lop.png", "Sơ đồ lớp của giao diện mô hình chung", width_cm=15.0)
    H3("5.1.2 Nạp gói mô hình")
    KEEP(909)
    TCAP("Các tệp trong gói mô hình phục vụ")
    KEEP(911)
    KEEP(912)
    H2("5.2 Thiết kế dịch vụ API")
    H3("5.2.1 Các chức năng và lược đồ")
    KEEP(915, subs=[("(Hình 5.2)", "(Hình 5.4)")])
    TCAP("Các chức năng của dịch vụ API")
    KEEP(917)
    FKEEP(918, "Tài liệu tương tác của API tại đường dẫn /docs")
    P(
        "Hình 5.5 trình bày sơ đồ tuần tự của POST /recommend. Sau khi Pydantic kiểm tra kiểu và miền giá trị, dịch vụ chọn một trong ba nhánh: có user_id thì gọi recommend_existing với PureSVD, M1 hoặc ALS và che lịch sử huấn luyện, xác thực; có từ một đến năm nghệ sĩ thì gọi recommend_new với M2; hồ sơ rỗng thì gọi recommend_popular và đánh dấu dự phòng. Mã người dùng không tồn tại trả lỗi 404."
    )
    F(FIG + "tuan_tu_recommend.png", "Sơ đồ tuần tự của POST /recommend", width_cm=15.5)
    H3("5.2.2 Ví dụ hợp đồng đầu vào đầu ra")
    KEEP(921)
    req, res = EXAMPLE["request"], EXAMPLE["response"]
    lines = ["POST /recommend", _json.dumps(req, ensure_ascii=False), ""]
    head = {
        k: res[k]
        for k in [
            "model_version",
            "branch",
            "model",
            "fallback_used",
            "fallback_reason",
            "ignored_item_ids",
        ]
    }
    lines.append("{")
    for k, v in head.items():
        lines.append(f'  "{k}": {_json.dumps(v, ensure_ascii=False)},')
    lines.append(f'  "mean_listeners": {round(res["mean_listeners"], 2)},')
    lines.append('  "recommendations": [')
    recs = res["recommendations"]
    for n, r in enumerate(recs):
        lines.append(
            f'    {{"rank": {r["rank"]}, "item_id": "{r["item_id"]}", "name": "{r["name"]}", "listeners": {r["listeners"]},'
        )
        lines.append(f'     "score": {round(r["score"], 4)}, "reason": "{r["reason"]}",')
        lines.append(f'     "url": "{r["url"]}",')
        lines.append(
            f'     "picture_url": "{r["picture_url"]}"}}' + ("," if n < len(recs) - 1 else "")
        )
    lines += ["  ]", "}"]
    CODECAP("Ví dụ yêu cầu và phản hồi của POST /recommend")
    CODE(lines)
    N(
        "Phản hồi thật của dịch vụ với gói mô hình demo-chinh-thuc-20261026; score làm tròn bốn chữ số thập phân, mean_listeners làm tròn hai chữ số."
    )
    KEEP(936)
    H3("5.2.3 Xử lý yêu cầu không hợp lệ")
    KEEP(938)
    TCAP("Xử lý các trường hợp đầu vào không hợp lệ hoặc đặc biệt")
    KEEP(940)
    KEEP(941)
    H2("5.3 Thiết kế giao diện minh họa")
    H3("5.3.1 Luồng sử dụng")
    KEEP(944)
    P(
        "Hình 5.6 trình bày sơ đồ điều hướng. Trang giới thiệu dẫn tới bốn trang chức năng; thanh điều hướng chung cho phép chuyển qua lại giữa năm trang. Hai trang người dùng có sẵn và người dùng mới gọi POST /recommend, còn trang luồng hoạt động và trang kết quả hiển thị nội dung tĩnh sinh từ tệp kết quả."
    )
    F(FIG + "dieu_huong.png", "Sơ đồ điều hướng giữa năm trang của giao diện", width_cm=15.0)
    KEEP(945, subs=[("(Hình 5.3)", "(Hình 5.7)")])
    FKEEP(946, "Trang người dùng có sẵn so sánh PureSVD và M1 (người dùng 2, K = 10)")
    KEEP(948, subs=[("(Hình 5.4)", "(Hình 5.8)"), ("(Hình 5.5)", "(Hình 5.9)")])
    FKEEP(949, "Trang người dùng mới với ba nghệ sĩ đã chọn (M2)")
    FKEEP(951, "Trang người dùng mới khi chưa chọn nghệ sĩ (dự phòng Popularity)")
    H3("5.3.2 Thông báo và thời gian chờ")
    KEEP(954, subs=[("(mục 5.7)", "(mục 6.3)")])
    H2("5.4 Kiểm thử hệ thống")
    H3("5.4.1 Kiểm thử chức năng")
    KEEP(957, subs=[("(145 ca,", "(166 ca,")])
    TCAP("Các ca kiểm thử chức năng trên gói mô hình thật")
    KEEP(959)
    H3("5.4.2 Đối chiếu trực tuyến và ngoại tuyến")
    KEEP(961)
    TCAP("Đối chiếu danh sách top-10 giữa API và đánh giá ngoại tuyến")
    KEEP(963)
    KEEP(964, subs=[("không quá 1e−12", "không quá 10⁻¹²")])
    H3("5.4.3 Đo thời gian phản hồi")
    KEEP(966)
    TCAP("Thời gian phản hồi của dịch vụ (ms)")
    KEEP(968)
    KEEP(
        969,
        subs=[
            (
                "và chưa có tải đồng thời",
                "và chưa có tải đồng thời; phép đo tải được trình bày ở mục 5.4.4",
            )
        ],
    )
    H3("5.4.4 Kiểm thử tải")
    rt = LOAD["runtime"]
    P(
        f"Nhóm đo thêm thông lượng khi nhiều yêu cầu đến cùng lúc bằng một script Python gửi POST /recommend (người dùng có sẵn, PureSVD, K = 10) từ nhiều luồng, mỗi luồng giữ một phiên HTTP riêng và gửi liên tục cho tới khi đủ số yêu cầu; mã người dùng thay đổi luân phiên trong 200 người dùng đầu. Dịch vụ chạy bằng uvicorn với một tiến trình, trên cùng máy với chương trình gửi (Windows 11, Intel Core i5-11300H, {rt['cpu_count']} luồng logic, Python {rt['python']}, FastAPI {rt['fastapi']}, uvicorn {rt['uvicorn']}). Mỗi mức đồng thời gửi {vn(LOAD['levels'][0]['requests'], 0)} yêu cầu sau một lượt khởi động. Bảng 5.7 trình bày kết quả."
    )
    T(
        "Kết quả kiểm thử tải của POST /recommend (PureSVD, K = 10)",
        [1900, 2100, 1600, 1600, 1588],
        [
            "Số yêu cầu đồng thời",
            "Thông lượng (yêu cầu/giây)",
            "Trung vị (ms)",
            "P95 (ms)",
            "Tỷ lệ lỗi (%)",
        ],
        [
            [
                str(r["concurrency"]),
                vn(r["throughput_rps"], 1),
                vn(r["median_ms"], 2),
                vn(r["p95_ms"], 2),
                vn(r["error_rate_pct"], 2),
            ]
            for r in LOAD["levels"]
        ],
        note="Thời gian tính từ phía chương trình gửi, gồm cả truyền trên máy cục bộ; chương trình gửi và dịch vụ dùng chung bộ xử lý.",
        align=["center"] * 5,
    )
    l1, l8, l32 = LOAD["levels"]
    P(
        f"Với một yêu cầu tại một thời điểm, dịch vụ xử lý {vn(l1['throughput_rps'], 1)} yêu cầu mỗi giây với trung vị {vn(l1['median_ms'], 2)} ms. Khi có 8 yêu cầu đồng thời, thông lượng tăng lên {vn(l8['throughput_rps'], 1)} yêu cầu mỗi giây nhưng trung vị tăng lên {vn(l8['median_ms'], 2)} ms; ở 32 yêu cầu đồng thời, thông lượng không tăng thêm ({vn(l32['throughput_rps'], 1)}) còn trung vị và P95 tăng lên {vn(l32['median_ms'], 2)} và {vn(l32['p95_ms'], 2)} ms, tức dịch vụ một tiến trình đã bão hòa và yêu cầu phải xếp hàng. Không có yêu cầu nào lỗi ở cả ba mức. Đây là phép đo trên một máy cá nhân, chưa phải trên máy chủ triển khai; để phục vụ nhiều người dùng hơn cần chạy nhiều tiến trình hoặc nhiều máy."
    )
    H2("5.5 Kết luận chương")
    P(
        "Chương 5 đã trình bày việc đóng gói các mô hình đã khóa thành một gói phát hành có kiểm tra mã băm, dịch vụ FastAPI với ba nhánh xử lý và giao diện Next.js gồm năm trang. Kết quả kiểm thử cho thấy 12 trên 12 ca kiểm thử chức năng đạt, danh sách gợi ý trên API trùng hoàn toàn với đánh giá ngoại tuyến cho cả bốn mô hình được phục vụ, thời gian phản hồi trung vị từ 3,78 đến 11,46 ms khi có một yêu cầu tại một thời điểm, và dịch vụ một tiến trình xử lý được khoảng "
        f"{vn(l8['throughput_rps'], 0)} yêu cầu mỗi giây khi có nhiều yêu cầu đồng thời. Chương 6 đối chiếu các kết quả này với mục tiêu ban đầu và rút ra kết luận chung của khóa luận."
    )


def _ch6():
    CHAPTER(6)
    content.append(heading_like(898, "CHƯƠNG 6 KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN"))
    P(
        "Chương này đối chiếu các mục tiêu ở mục 1.3.2 với kết quả đạt được, tóm tắt câu trả lời cho năm câu hỏi nghiên cứu, rồi nêu các hạn chế và hướng phát triển của khóa luận."
    )
    H2("6.1 Mức độ đạt mục tiêu")
    P(
        "Bảng 6.1 đối chiếu năm mục tiêu cụ thể ở mục 1.3.2 với kết quả đạt được; mục tiêu thứ ba được tách thành hai dòng cho M1 và M2."
    )
    T(
        "Đối chiếu mục tiêu và kết quả",
        [2900, 1300, 4588],
        ["Mục tiêu", "Mức độ", "Minh chứng"],
        [
            [
                "1. Quy trình tiền xử lý Last.fm kiểm tra và chạy lại được",
                "Đạt",
                "Mục 3.4, 3.5; chạy lại từ dữ liệu gốc cho tệp trùng từng byte; Phụ lục A, B, C.",
            ],
            [
                "2. Bốn mô hình lọc cộng tác và hai mô hình cơ sở dùng chung giao diện",
                "Đạt",
                "Bảng 3.5, 4.3, 4.5; tinh chỉnh 48 cấu hình trên tập xác thực, khóa cấu hình trước khi kiểm thử; Hình 5.3.",
            ],
            [
                "3a. M1 kèm thử nghiệm loại bỏ thành phần",
                "Đạt",
                "Bảng 4.11, công thức (4.1): ARP@10 giảm 15,69%, tương đương mô hình nền về NDCG@10 theo TOST ở biên 5%.",
            ],
            [
                "3b. M2 hỗ trợ người dùng mới",
                "Đạt một phần",
                "Bảng 4.13–4.15, 4.20–4.21: theo giao thức đã khóa M2 chưa vượt Popularity; với tập đích (3.14) M2 vượt Popularity ở N = 3 và N = 5. Kết luận phụ thuộc định nghĩa tập đích.",
            ],
            [
                "4. Đánh giá bằng chỉ số xếp hạng và chỉ số bổ sung",
                "Đạt",
                "Bảng 4.5 đến 4.8: tám chỉ số tại K = 5, 10, 20, kiểm định Wilcoxon, hiệu chỉnh Holm, khoảng tin cậy bootstrap, cỡ hiệu ứng.",
            ],
            [
                "5. Dịch vụ API, giao diện minh họa, xử lý đầu vào không hợp lệ",
                "Đạt một phần",
                "Mục 5.2 đến 5.4; Bảng 5.3 đến 5.7: 12/12 ca kiểm thử đạt, danh sách trùng hoàn toàn với đánh giá ngoại tuyến, kiểm thử tải tới 32 yêu cầu đồng thời. Giao diện chính là Next.js (Streamlit giữ làm dự phòng); chưa triển khai lên máy chủ công khai.",
            ],
        ],
        align=["left", "center", "left"],
    )
    H2("6.2 Kết luận")
    P(
        "Khóa luận đã xây dựng một hệ thống khuyến nghị nghệ sĩ dựa trên lọc cộng tác với quy trình thực nghiệm thống nhất trên bộ dữ liệu Last.fm HetRec 2011. Quy trình dữ liệu được kiểm chứng chặt chẽ: ánh xạ và các ngưỡng biến đổi chỉ học từ tập huấn luyện, đích ngoài danh mục được báo cáo riêng, bộ đánh giá được kiểm tra bằng ví dụ tính tay và đối chiếu với thư viện chuẩn, và cấu hình được khóa trước khi mở tập kiểm thử."
    )
    P(
        "Với cấu hình đã khóa, PureSVD nhị phân đạt NDCG@10 cao nhất trong sáu mô hình đối sánh là 0,182780, cao hơn Popularity 0,114005 và khác biệt có ý nghĩa thống kê; UserCF, ItemCF và SVD có độ lệch không vượt được Popularity. Các phân tích bổ sung sau khi khóa cấu hình cho thấy hai kết luận phụ thuộc vào lựa chọn thiết kế: mô hình láng giềng vượt PureSVD khi tổng hợp điểm theo kiểu top-N, và M2 vượt Popularity ở N = 3, 5 khi tập đích là toàn bộ nghệ sĩ người dùng chưa cung cấp. Mô-đun M1 giảm độ phổ biến trung bình của danh sách 15,69% và tương đương mô hình nền về NDCG@10 ở biên 5%. Implicit ALS đạt NDCG@10 0,217453, cao nhất trong các mô hình đã đo. Hệ thống được đóng gói thành dịch vụ FastAPI và giao diện Next.js, cho danh sách trùng hoàn toàn với đánh giá ngoại tuyến. Bảng 6.2 tóm tắt câu trả lời cho năm câu hỏi nghiên cứu."
    )
    T(
        "Tóm tắt câu trả lời các câu hỏi nghiên cứu",
        [900, 5888, 2000],
        ["Câu hỏi", "Câu trả lời", "Bằng chứng"],
        [
            [
                "RQ1",
                "Với cấu hình đã khóa, PureSVD nhị phân (k = 16) tốt nhất trong sáu mô hình đối sánh, NDCG@10 = 0,182780, hơn Popularity 0,114005 có ý nghĩa; UserCF, ItemCF, SVD có độ lệch không vượt Popularity. Với cách tổng hợp top-N (phân tích bổ sung), UserCF đạt 0,193668 và ItemCF đạt 0,193973, vượt PureSVD có ý nghĩa. Implicit ALS đạt 0,217453, cao nhất.",
                "Bảng 4.5–4.8, 4.17–4.18",
            ],
            [
                "RQ2",
                "Phép chia hiện tại gần như không có biến thiên độ dài lịch sử. Trong Given-N, NDCG@10 của M2 tăng từ N = 1 lên N = 3 ở cả hai giao thức (0,043317 lên 0,049854 với đích là cặp kiểm thử; 0,236658 lên 0,306828 với tập đích (3.14)); kết quả mang tính mô tả.",
                "Bảng 4.9, 4.13, 4.20",
            ],
            [
                "RQ3",
                "M1 giảm ARP@10 15,69% và tăng độ bao phủ từ 1,86% lên 2,94%; chênh lệch NDCG@10 là −0,001364 với khoảng tin cậy 90% [−0,003641; 0,000888] nằm trong biên ±0,009139, nên tương đương mô hình nền theo TOST. M1 hơn PureSVD có ý nghĩa ở nhóm ít ưa chuộng nghệ sĩ phổ biến.",
                "Bảng 4.10, 4.11; công thức (4.1)",
            ],
            [
                "RQ4",
                "Phụ thuộc định nghĩa tập đích: theo giao thức đã khóa, M2 không vượt Popularity ở N = 1, 3, 5; với tập đích (3.14), M2 vượt Popularity ở N = 3 (+0,063028, p sau Holm 0,001) và N = 5.",
                "Bảng 4.13–4.15, 4.20–4.21",
            ],
            [
                "RQ5",
                f"Danh sách top-10 trên API trùng 100% cả thứ tự với đánh giá ngoại tuyến; 12/12 ca kiểm thử chức năng đạt; trung vị thời gian phản hồi 3,78–11,46 ms; dịch vụ một tiến trình đạt {vn(l8_tp, 1)} yêu cầu mỗi giây ở 8 yêu cầu đồng thời.",
                "Bảng 5.4–5.7",
            ],
        ],
        align=["center", "left", "left"],
    )
    H2("6.3 Hạn chế")
    P(
        "Thứ nhất, dữ liệu Last.fm HetRec 2011 không có thời điểm của từng lượt nghe, nên phép chia ngẫu nhiên chỉ kiểm tra khả năng tìm lại một phần nghệ sĩ đã nghe, không mô phỏng việc dự đoán lần nghe tiếp theo. Thứ hai, mỗi người dùng chỉ được ghi nhận những nghệ sĩ nghe nhiều nhất và phần lớn có đúng 50 nghệ sĩ, nên ảnh hưởng của độ dài lịch sử chỉ khảo sát được qua thí nghiệm Given-N. Thứ ba, dữ liệu được thu thập năm 2011 nên không phản ánh thị hiếu âm nhạc hiện nay. Thứ tư, điểm đại diện 1–5 là phép quy đổi của nhóm từ phân vị lượt nghe, không phải đánh giá do người nghe tự chấm, nên RMSE chỉ có ý nghĩa tham khảo. Thứ năm, kết quả dựa trên một lần chia dữ liệu với một hạt giống; PureSVD là tất định nên chạy lại với hạt giống khác không tạo ra kiểm chứng độc lập."
    )
    P(
        "Thứ sáu, một số cấu hình được chọn nằm ở biên lưới tìm kiếm, và các phân tích bổ sung ở mục 4.11 (biến thể top-N, độ nhạy ngoài biên, tập đích (3.14), mở rộng β) được thực hiện sau khi đã mở tập kiểm thử, nên là bằng chứng bổ sung chứ không thay kết quả đã khóa. Thứ bảy, độ đa dạng ILD và phần phạt của M1 cùng dựa trên độ tương đồng đồng nghe; thước đo độc lập theo thẻ cho thấy mức tăng đa dạng nhỏ hơn, và chỉ 36,69% nghệ sĩ của danh mục huấn luyện có véc-tơ thẻ dùng được. Thứ tám, thẻ nghệ sĩ do người dùng gán làm giới hạn M2, và giao thức người dùng mới chỉ có chưa tới 200 người mỗi nhóm. Thứ chín, M1 được tinh chỉnh trên PureSVD trong khi ALS là mô hình chính xác nhất đã đo. Cuối cùng, ứng dụng ở mức minh họa: chưa triển khai lên máy chủ công khai, giao diện chưa đặt thời gian chờ riêng cho lời gọi API, kiểm thử tải mới thực hiện trên một máy cá nhân và chưa đánh giá với người dùng thật."
    )
    H2("6.4 Hướng phát triển")
    P(
        "**Ngắn hạn**, các hướng sau có thể làm ngay trên hệ thống hiện tại. Về mô hình, áp dụng M1 trên mô hình nền ALS và chấm trên một lần chia mới; thay thành phần ItemCF trong M2 bằng biến thể tổng hợp top-N, vốn cho kết quả tốt hơn rõ rệt ở mục 4.11; mở rộng lưới tìm kiếm ra ngoài các biên đã phát hiện và cá nhân hóa mức phạt phổ biến theo từng người dùng như Abdollahpouri và cộng sự [19]. Về đánh giá, lặp lại thực nghiệm trên nhiều lần chia để ước lượng bất định và dùng giao thức Given-N theo (3.14) với nhiều nhóm người dùng luân phiên để tăng cỡ mẫu. Về hệ thống, bổ sung thời gian chờ, bộ nhớ đệm, chạy nhiều tiến trình và triển khai lên môi trường đám mây."
    )
    P(
        "**Dài hạn**, có thể dùng bộ dữ liệu nghe nhạc có dấu thời gian như LFM-2b [35] để chia tập theo mốc thời gian thay cho chia ngẫu nhiên; bổ sung các mô hình tối ưu trực tiếp cho xếp hạng như BPR [36] hoặc EASE [37] và các mô hình dựa trên đồ thị như LightGCN [38]; khai thác quan hệ bạn bè có sẵn trong dữ liệu; dùng biểu diễn độc lập với chỉ số đánh giá cho phần đa dạng của M1 (thể loại, đặc trưng âm thanh); bổ sung siêu dữ liệu nghệ sĩ từ nguồn bên ngoài để tăng độ phủ nội dung của M2, cho phép người dùng mới chọn thể loại yêu thích ở bước đầu; và khảo sát người dùng thật về độ mới, độ đa dạng của danh sách gợi ý."
    )


l8_tp = LOAD["levels"][1]["throughput_rps"]
ref_head = ORIG[991]  # the real heading, not its entry in the table of contents
_ppr = ref_head.find("w:pPr", NS)
if _ppr.find("w:pageBreakBefore", NS) is None:
    _ps = _ppr.find("w:pStyle", NS)
    if _ps is not None:
        _ps.addnext(etree.Element(q("pageBreakBefore")))
    else:
        _ppr.insert(0, etree.Element(q("pageBreakBefore")))
new_content = collect(_ch5) + collect(_ch6)
for e in new_content:
    ref_head.addprevious(e)
remove(*ORIG[898:991])

# =====================================================================================
# References
# =====================================================================================
refs = [e for e in body if e.tag == q("p") and re.match(r"\[\d+\] ", text(e) or "")]
ACCESS = "(Truy cập ngày 11/11/2026)"
for p in refs:
    for t in p.iter(q("t")):
        if t.text:
            t.text = re.sub(r"\s+,", ",", t.text)
            t.text = re.sub(r"(?<![\w/.\-])(\d+)-(\d+)(?![\w/])", r"\1–\2", t.text)
            t.text = t.text.replace(" (Truy cập ngày 20/10/2026)", "")
for p in refs:
    s = text(p)
    rpr = copy.deepcopy(p.find("w:r/w:rPr", NS))
    if s.startswith("[1] IFPI"):
        fill(
            p,
            "[1] IFPI. (2026, March 18). Global Music Report 2026: Global recorded music revenues grow 6.4% as record companies drive innovation. https://www.ifpi.org/global-music-report-2026-global-recorded-music-revenues-grow-6-4-as-record-companies-drive-innovation/ "
            + ACCESS
            + ".",
            rpr=rpr,
        )
    elif s.startswith("[4] Spotify"):
        fill(
            p,
            "[4] Spotify. (2025, June 30). Discover Weekly turns 10: Celebrating 100 billion+ tracks streamed and a decade of personalized discovery. https://newsroom.spotify.com/2025-06-30/discover-weekly-turns-10-celebrating-100-billion-tracks-streamed-and-a-decade-of-personalized-discovery/ "
            + ACCESS
            + ".",
            rpr=rpr,
        )
    elif s.startswith("[32]"):
        fill(
            p,
            "[32] Ramírez, S. (không ghi năm). FastAPI. Tài liệu chính thức. https://fastapi.tiangolo.com "
            + ACCESS
            + ".",
            rpr=rpr,
        )
    elif s.startswith("[33]"):
        fill(
            p,
            "[33] Vercel. (2026). Next.js Documentation. https://nextjs.org/docs " + ACCESS + ".",
            rpr=rpr,
        )
    elif s.startswith("[34]"):
        fill(
            p,
            "[34] Snowflake Inc. (2026). Streamlit Documentation. https://docs.streamlit.io "
            + ACCESS
            + ".",
            rpr=rpr,
        )
    elif s.startswith("[42]"):
        fill(
            p,
            "[42] Schuirmann, D. J. (1987). A comparison of the two one-sided tests procedure and the power approach for assessing the equivalence of average bioavailability. Journal of Pharmacokinetics and Biopharmaceutics, 15(6), 657–680. https://doi.org/10.1007/BF01068419",
            rpr=rpr,
        )

# =====================================================================================
# Appendix C (installation and reruns) and Appendix D.2-D.5
# =====================================================================================
d_head = next(
    e for e in body if e.tag == q("p") and text(e).startswith("PHỤ LỤC D BẢNG KẾT QUẢ ĐẦY ĐỦ")
)


def _appC():
    CHAPTER("C")
    H1("PHỤ LỤC C HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY LẠI")
    H2("C.1 Yêu cầu môi trường")
    P(
        "Mã nguồn yêu cầu Python từ 3.11 đến dưới 3.13. Lần chạy chính thức dùng Python 3.11.17 trên Linux; các phân tích bổ sung và ứng dụng chạy trên Windows 11 với Python 3.11.9. Các thư viện chính gồm NumPy 2.4.6, SciPy 1.17.1, pandas 2.3.3, pyarrow 19.0.1, scikit-learn 1.9.1, implicit 0.7.3 và FastAPI 0.141.1 (mục 4.1.1, 5.4.3). Giao diện dùng Next.js 16.4.3 với React 19.3.0; máy cá nhân dùng Node.js 24.12.0. Kho mã nguồn: https://github.com/trongnguyen1010/musicrec-collaborative-filtering."
    )
    H2("C.2 Cài đặt")
    P(
        "Các lệnh dưới đây tạo môi trường, cài thư viện và chuẩn bị dữ liệu. Tệp nén của GroupLens phải có mã băm SHA-256 trùng với giá trị ghi trong cấu hình làm sạch trước khi giải nén vào thư mục data/raw/hetrec2011."
    )
    CODE(
        [
            "git clone https://github.com/trongnguyen1010/musicrec-collaborative-filtering.git",
            "cd musicrec-collaborative-filtering",
            "uv sync --all-extras          # hoặc: python -m venv .venv",
            '                              #       .venv/Scripts/python -m pip install ".[dev,als]"',
            "# Tải https://files.grouplens.org/datasets/hetrec2011/hetrec2011-lastfm-2k.zip vào data/raw/",
            "# SHA-256: 6738f48195667ff03caaab4d32ca9a3133d8cc026b7c3cdaf6ce1010e913c59c",
            "# Giải nén vào data/raw/hetrec2011/",
        ]
    )
    H2("C.3 Chạy lại thực nghiệm")
    P(
        "Các bước được chạy lần lượt; mỗi lệnh ghi một thư mục kết quả mới và không ghi đè thư mục đã có. Bước kiểm thử ghi tệp khóa trước khi mở tập kiểm thử."
    )
    CODE(
        [
            "python -B scripts/run_chuong_3.py --label <may> --output-dir outputs/chuong_3/<run>",
            "python -B scripts/tune_validation.py --representations-run outputs/chuong_3/<run>/run/representations \\",
            "    --output-dir outputs/chuong_4/tuning_<run>",
            "python -B scripts/run_m1.py --config configs/models/m1_pure_svd.yaml --output-dir outputs/chuong_4/m1_<run>",
            "python -B scripts/evaluate_test.py --representations-run <...>/representations \\",
            "    --tuning-dir outputs/chuong_4/tuning_<run> --m1-run outputs/chuong_4/m1_<run> \\",
            "    --output-dir outputs/chuong_4/test_<run>",
            "python -B scripts/test_statistics.py --test-run outputs/chuong_4/test_<run>",
            "python -B scripts/run_m2.py --config configs/models/m2.yaml --output-dir outputs/chuong_4/m2_tuning_<run>",
            "python -B scripts/evaluate_m2_test.py --m2-run outputs/chuong_4/m2_tuning_<run> --output-dir outputs/chuong_4/m2_test_<run>",
        ]
    )
    P(
        "Trên máy đám mây ở mục 4.1.1, bốn bước làm sạch, chia tập, biến đổi và khám phá dữ liệu mất dưới 13 giây, tinh chỉnh 48 cấu hình mất 42,8 phút, chấm tập kiểm thử mất 1,5 phút và toàn bộ lần chạy khoảng 48 phút. Các phân tích bổ sung ở mục 4.11 dùng các script report_ch4_extras.py, run_e7_topn.py, run_e_s_sensitivity.py, run_e_b_m1_beta.py, report_e_c_groups.py, report_e_d_data.py và evaluate_m2_test.py với tùy chọn --target-mode all_but_profile; trên máy cá nhân, lưới E7 mất 5 phút 42 giây, phần ALS của phân tích độ nhạy khoảng 21 phút, các phần còn lại mỗi phần dưới 4 phút."
    )
    H2("C.4 Chạy dịch vụ và giao diện")
    CODE(
        [
            "python scripts/export_release.py --version demo-chinh-thuc-20261026   # gói đã có trong artifacts/releases/",
            "uvicorn musicrec.api.main:app --port 8000      # tài liệu API: http://127.0.0.1:8000/docs",
            "cd frontend",
            "npm install",
            "npm run dev                                    # giao diện: http://localhost:3000",
        ]
    )
    P(
        "Biến môi trường MUSICREC_RELEASE_DIR chọn gói mô hình (mặc định artifacts/releases/demo-chinh-thuc-20261026), MUSICREC_CORS_ORIGINS khai báo địa chỉ giao diện được phép gọi API, còn NEXT_PUBLIC_API_URL của giao diện trỏ tới dịch vụ (mặc định http://127.0.0.1:8000)."
    )
    H2("C.5 Cấu trúc thư mục kết quả")
    P(
        "Mỗi lần chạy nằm trong một thư mục con của outputs/ với bộ tệp theo Bảng A.1: cấu hình, bản kê dữ liệu và mã băm, ánh xạ, quy tắc biến đổi, tham số mô hình, danh sách gợi ý theo người dùng, bảng chỉ số và tệp metrics.json ghi cấu hình máy, phiên bản thư viện và commit. Thư mục docs/results/ lưu bản sao các tệp kết quả nhỏ được dẫn trong báo cáo, còn artifacts/releases/ chứa gói mô hình phục vụ ứng dụng."
    )


def _appD():
    CHAPTER("D")
    counters["Bang"] = 1  # D.1 already exists
    H2("D.2 Kết quả của 48 cấu hình tinh chỉnh trên tập xác thực")
    rows_ = []
    lab = {
        "user_cf": "UserCF",
        "item_cf": "ItemCF",
        "svd": "SVD có độ lệch",
        "pure_svd": "PureSVD",
        "implicit_als": "Implicit ALS",
    }
    for m in ["user_cf", "item_cf", "svd", "pure_svd", "implicit_als"]:
        d = _pd.read_csv(f"docs/results/chuong_4/tuning_{m}.csv")
        d = d[d.seed == 42]
        for r in d.itertuples():
            if m in ("user_cf", "item_cf"):
                cfg = f"L = {r.neighbors}, co rút {r.shrinkage}"
            elif m == "svd":
                cfg = f"d = {r.latent_factors}, η = {vn(r.learning_rate, 6).rstrip('0')}, λreg = {vn(r.regularization, 6).rstrip('0')}"
            elif m == "pure_svd":
                cfg = f"k = {r.latent_factors}"
            else:
                cfg = f"{r.latent_factors} nhân tố, reg {vn(r.regularization, 2).rstrip('0').rstrip(',')}, a_conf {r.confidence_scale}"
            rows_.append([lab[m], cfg, vn(r.ndcg_at_10, 6), vn(r.recall_at_10, 6)])
    T(
        "NDCG@10 và Recall@10 trên tập xác thực của 48 cấu hình tinh chỉnh",
        [1900, 3888, 1500, 1500],
        ["Mô hình", "Cấu hình", "NDCG@10", "Recall@10"],
        rows_,
        note="Hạt giống 42; giá trị của các cấu hình được chọn trùng với Bảng 4.3.",
        align=["left", "left", "center", "center"],
        size=20,
    )
    H2("D.3 Mười hai điểm của lưới M1 trên tập xác thực")
    g = _pd.read_csv("docs/results/chinh_thuc_cloud_20261026/m1_metrics.csv")
    g = g[(g.seed == 42) & (g.k == 10)]
    T(
        "Lưới M1 trên tập xác thực (K = 10)",
        [1500, 1500, 1500, 1400, 1400, 1488],
        ["λ", "β", "NDCG@10", "ARP", "ILD", "Bao phủ"],
        [
            [
                vn(r._2, 2),
                vn(r.beta, 2),
                vn(r.ndcg, 6),
                vn(r.arp, 2),
                vn(r.ild, 4),
                vn(100 * r.catalog_coverage, 2) + "%",
            ]
            for r in g.itertuples()
        ],
        note="Điểm λ = 1, β = 0 là mô hình nền PureSVD; cấu hình được chọn là λ = 0,75, β = 0,5.",
        align=["center"] * 6,
    )
    H2("D.4 Chín cấu hình của lưới M2 trên nhóm tinh chỉnh")
    sel = _json.loads(
        open(
            "docs/results/chinh_thuc_cloud_20261026/m2/validation/selection.json", encoding="utf-8"
        ).read()
    )
    m2rows = []
    for r in sel["grid"]:
        v = r["ndcg_by_n"]
        m2rows.append(
            [
                vn(r["alpha"], 2),
                str(r["history_threshold"]),
                vn(v["1"], 6),
                vn(v["3"], 6),
                vn(v["5"], 6),
                vn((v["1"] + v["3"] + v["5"]) / 3, 6),
            ]
        )
    T(
        "Lưới M2 trên tập xác thực của nhóm tinh chỉnh (NDCG@10)",
        [1200, 1200, 1600, 1600, 1600, 1588],
        ["α", "n_min", "N = 1", "N = 3", "N = 5", "Trung bình"],
        m2rows,
        note="187 người dùng nhóm tinh chỉnh; cấu hình được chọn là α = 0,75, n_min = 10.",
        align=["center"] * 6,
    )
    H2("D.5 Bảng độ nhạy ngoài biên lưới")
    P(
        "Kết quả độ nhạy ngoài biên lưới trên tập xác thực, gồm PureSVD, UserCF, ItemCF, implicit ALS và M2, được trình bày đầy đủ ở Bảng 4.19 (mục 4.11.2)."
    )


for e in collect(_appC):
    d_head.addprevious(e)
remove(ORIG[1057], ORIG[1058])
blue_left = [
    e
    for e in body
    if e.tag == q("p")
    and text(e).startswith("D.1 Precision, Recall và NDCG tại K = 5, 10, 20 của tám mô hình")
]
anchor = blue_left[0] if blue_left else None
appd = collect(_appD)
if anchor is not None:
    for e in appd:
        anchor.addprevious(e)
    remove(anchor)

# =====================================================================================
# Remove every remaining advisor note (red) and check that no blue text is left
# =====================================================================================
removed = 0
for e in list(body):
    if e.tag not in (q("p"), q("tbl")):
        continue
    colors = {c.get(q("val"), "").upper() for c in e.iter(q("color"))}
    if "FF0000" in colors:
        remove(e)
        removed += 1
blue = [
    text(e)[:60]
    for e in body
    if e.tag in (q("p"), q("tbl"))
    and any(c.get(q("val"), "").upper() == "0000FF" for c in e.iter(q("color")))
]
print("v20: removed red notes", removed, "| blue left", len(blue), blue[:5])

# Word document properties
core = root_dir / "docProps/core.xml"
ct = core.read_text(encoding="utf-8")
ct = re.sub(r"<dc:subject>.*?</dc:subject>", f"<dc:subject>{TITLE_VI_SENT}</dc:subject>", ct)
ct = re.sub(r"<dc:title>.*?</dc:title>", f"<dc:title>{TITLE_VI_SENT}</dc:title>", ct)
core.write_text(ct, encoding="utf-8")

# Running header: same title as the covers
for hdr in sorted((root_dir / "word").glob("header*.xml")):
    h = hdr.read_text(encoding="utf-8")
    if "Xây dựng hệ thống khuyến nghị nghệ sĩ" in h and "MusicRec:" not in h:
        hdr.write_text(
            h.replace(
                "Xây dựng hệ thống khuyến nghị nghệ sĩ",
                "MusicRec: Xây dựng hệ thống khuyến nghị nghệ sĩ",
                1,
            ),
            encoding="utf-8",
        )
        print("header updated", hdr.name)
