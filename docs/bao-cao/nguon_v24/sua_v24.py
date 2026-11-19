# ruff: noqa: E501
"""Report v24: apply the advisor's feedback of 19/11/2026 to her annotated copy of v23.

Usage (from the repository root, after unzipping the advisor's docx into <unpacked>):
    python -X utf8 docs/bao-cao/nguon_v24/sua_v24.py <unpacked>

Body indices refer to the advisor's copy GopY_GVHD_19-11-2026_KLTN_TrongNguyen_GiaKhang.docx;
every index is checked against the start of its text before it is used. Red notes are
removed; blue rewrites are checked against the code and results, corrected where needed and
turned black. Every metric with more than four decimals is rounded to four decimals from the
value printed in the copy, except values whose last two printed digits are 50, which are
rounded from the raw value in the result files (ROUND_FROM_RAW).
"""

import copy
import re
import sys
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from thu_vien_v24 import (  # noqa: E402
    NS,
    M,
    blacken,
    colours,
    first_rpr,
    new_para,
    nor_number,
    paragraphs,
    preplace,
    q,
    replace_span,
    round_paragraph,
    set_text,
    strip_ids,
    text,
    visible,
)

root_dir = Path(sys.argv[1])
doc_path = root_dir / "word/document.xml"
tree = etree.parse(str(doc_path))
body = tree.getroot().find("w:body", NS)
B = list(body)
removed: set[int] = set()


def at(i, prefix):
    t = text(B[i]).strip()
    assert t.startswith(prefix), (i, t[:80], prefix)
    return B[i]


def drop(*idx):
    for i in idx:
        e = B[i]
        if e.getparent() is not None:
            body.remove(e)
        removed.add(i)


def after(anchor, *elements):
    for e in elements:
        anchor.addnext(e)
        anchor = e
    return anchor


def must(p, old, new):
    n = preplace(p, old, new, count=1)
    assert n == 1, (old, text(p)[:120])
    return n


def blue_text(i):
    """Text of a blue rewrite without the 'Gợi ý viết lại:' label."""
    return re.sub(r"^Gợi ý viết lại:\s*", "", text(B[i]).strip())


# ---------------------------------------------------------------- red notes
RED = [
    67,
    77,
    385,
    435,
    534,
    732,
    737,
    758,
    767,
    772,
    778,
    806,
    866,
    924,
    933,
    949,
    962,
    970,
    974,
    1089,
    1092,
    1097,
    1101,
    1228,
]
for i in RED:
    assert colours(B[i]) == {"FF0000"} and text(B[i]).startswith("Cô góp ý"), i
drop(*RED)
# general comments block (heading, two tables, empty separators) before Chapter 1
at(346, "NHẬN XÉT TỔNG QUÁT")
at(376, "GVHD: TS. Lê Thị Vĩnh Thanh")
for i in range(346, 377):
    assert colours(B[i]) <= {"FF0000", ""} or not text(B[i]).strip(), i
drop(*range(346, 377))

# ---------------------------------------------------------------- Tóm tắt, Abstract
at(64, "Các dịch vụ nghe nhạc trực tuyến")
at(74, "Online music services")
vi = [blue_text(i) for i in (68, 69, 70)]
# one page each for Tóm tắt and Abstract (the keywords line spilled onto a second page)
vi[0] = vi[0].replace(
    "Các dịch vụ nghe nhạc trực tuyến có kho nội dung lớn hơn nhiều so với khả năng khám phá của mỗi người nghe, nên hệ thống khuyến nghị giúp người dùng tìm được những nghệ sĩ phù hợp với sở thích.",
    "Hệ thống khuyến nghị giúp người nghe tìm được nghệ sĩ phù hợp trong kho nhạc trực tuyến rất lớn.",
)
vi[1] = vi[1].replace(
    "Sáu mô hình đối sánh (Random, Popularity, UserCF, ItemCF, SVD có độ lệch và PureSVD) được",
    "Sáu mô hình đối sánh (Random, Popularity, UserCF, ItemCF, SVD có độ lệch, PureSVD) được",
)
vi[2] = vi[2].replace("trung vị 3,8–11,5 ms.", "trung vị 3,8–11,5 ms trên máy tính cá nhân.")
en = [blue_text(i) for i in (78, 79, 80)]
en[0] = en[0].replace(
    "Online music services offer catalogues far larger than any listener can explore, so recommender systems help users find artists that match their taste.",
    "Recommender systems help listeners find suitable artists in very large online music catalogues.",
)
en[2] = en[2].replace("of 3.8–11.5 ms.", "of 3.8–11.5 ms on a personal computer.")
en[2] = en[2].replace(
    "The system was deployed as a FastAPI service with a Next.js interface; recommendations served by the application match the offline evaluation exactly,",
    "The FastAPI service and Next.js interface return exactly the lists of the offline evaluation,",
)
en[2] = en[2].replace(
    "and implicit ALS reached 0.2175, the highest of all measured models.",
    "and implicit ALS reached 0.2175, the best of all measured models.",
)
en[1] = en[1].replace(", with a collaborative weight that grows with profile length", "")
en[1] = en[1].replace(
    "Comparisons use paired Wilcoxon tests, Holm correction, bootstrap confidence intervals, effect sizes and a two one-sided equivalence test (TOST).",
    "Comparisons use paired Wilcoxon tests with Holm correction, bootstrap confidence intervals, effect sizes and the TOST equivalence test.",
)
en[2] = en[2].replace(
    "A supplementary analysis showed that neighbourhood models depend mainly on score aggregation:",
    "In a supplementary analysis, neighbourhood models depended mainly on score aggregation:",
)
en[2] = en[2].replace(
    "M1 reduced the average popularity of recommendations by 15.69%",
    "M1 cut average recommendation popularity by 15.69%",
)
assert "return exactly the lists" in en[2] and "the best of all" in en[2]
assert "profile length" not in en[1] and "TOST equivalence" in en[1] and "M1 cut" in en[2]
assert "máy tính cá nhân" in vi[2] and "personal computer" in en[2]
assert vi[0].startswith("Hệ thống khuyến nghị giúp") and en[0].startswith(
    "Recommender systems help"
)
for k, s in enumerate(vi):
    set_text(B[64 + k], s)
for k, s in enumerate(en):
    set_text(B[74 + k], s)
drop(68, 69, 70, 78, 79, 80)

# ---------------------------------------------------------------- Chương 1: thì đã thực hiện
p = at(384, "Từ những cơ sở thực tiễn")
must(p, "Kết quả sẽ được đánh giá", "Kết quả được đánh giá")
must(
    p,
    "Nhóm cũng dự kiến kiểm chứng mô-đun tái xếp hạng M1 và mô-đun dự phòng M2 nhằm khảo sát",
    "Nhóm đã kiểm chứng mô-đun tái xếp hạng M1 và mô-đun dự phòng M2 để khảo sát",
)
p = at(386, "Về mặt ứng dụng, đề tài hướng tới xây dựng")
must(p, "đề tài hướng tới xây dựng", "đề tài xây dựng")
p = at(395, "Đề tài xây dựng hệ thống")
must(p, "Nhóm sẽ so sánh", "Nhóm so sánh")
must(p, "Phương án được chọn sẽ được tích hợp", "Phương án được chọn được tích hợp")
must(at(426, "Phương pháp chính là thực nghiệm"), "Nhóm sẽ so sánh", "Nhóm so sánh")
must(at(428, "Bên cạnh thực nghiệm"), "Nhóm sẽ kiểm tra để", "Nhóm kiểm tra để")

# ---------------------------------------------------------------- 1.7 Đóng góp
at(430, "Thứ nhất, khóa luận xây dựng một quy trình")
at(434, "Thứ năm, khóa luận đóng gói")
contrib = [blue_text(i) for i in range(436, 441)]
for k, s in enumerate(contrib):
    set_text(B[430 + k], s)
drop(*range(436, 441))

# ---------------------------------------------------------------- 2.5 gộp mục con
H = {}
H[538] = ("2.5.1 Độ chính xác Precision", "2.5.1 Precision và Recall")
H[550] = ("2.5.3 Chất lượng xếp hạng NDCG", "2.5.2 Chất lượng xếp hạng NDCG")
H[561] = (
    "2.5.4 Căn sai số bình phương trung bình RMSE",
    "2.5.3 Căn sai số bình phương trung bình RMSE",
)
H[567] = ("2.5.5 Độ bao phủ danh mục", "2.5.4 Độ bao phủ, hệ số Gini và độ phổ biến trung bình")
H[585] = ("2.5.8 Độ mới", "2.5.5 Độ mới")
H[591] = ("2.5.9 Độ đa dạng trong danh sách", "2.5.6 Độ đa dạng trong danh sách")
for i, (old, new) in H.items():
    must(at(i, old), old, new)
at(544, "2.5.2 Độ thu hồi Recall")
at(573, "2.5.6 Hệ số Gini")
at(579, "2.5.7 Độ phổ biến trung bình")
tpl = B[539]
set_text(
    at(539, "Độ chính xác (Precision)"),
    "Độ chính xác (Precision) đo tỷ lệ kết quả đúng trong các vị trí hệ thống đề xuất, còn độ thu hồi (Recall) đo tỷ lệ kết quả đúng hệ thống tìm lại được so với toàn bộ kết quả đúng cần tìm. Với K vị trí đầu của danh sách, hai chỉ số được tính như sau:",
)
after(B[540], B[546])  # (2.16) right after (2.15)
pr = new_para(
    tpl,
    "Trong công thức (2.15) và (2.16), ⟦L_u^K⟧ là danh sách K nghệ sĩ gợi ý cho người dùng u, ⟦T_u⟧ là tập nghệ sĩ liên quan (các nghệ sĩ được giữ lại để đánh giá) và hai dấu gạch đứng biểu thị số phần tử. Cả hai chỉ số nằm từ 0 đến 1; Recall không xác định khi ⟦T_u⟧ rỗng. Khóa luận giữ mẫu số của Precision bằng K kể cả khi mô hình trả thiếu, loại người dùng không có nghệ sĩ đích khỏi phép tính và lấy trung bình theo người dùng.",
)
pr2 = new_para(
    tpl,
    "Hai chỉ số không phân biệt kết quả đúng nằm ở đầu hay cuối danh sách, và một nghệ sĩ ngoài tập đích vẫn có thể phù hợp với người nghe. Vì vậy chúng chỉ phản ánh khả năng tìm lại dữ liệu được giữ lại, còn thứ tự xếp hạng được đánh giá bằng NDCG.",
)
after(B[546], pr, pr2)
drop(541, 542, 543, 544, 545, 547, 548, 549)
# NDCG
at(555, "Trong công thức (2.17)")
set_text(
    B[555],
    "Trong công thức (2.17) và (2.18), j là vị trí trong danh sách và ⟦rel_(uj)⟧ là mức liên quan của kết quả tại vị trí đó; mẫu số logarithm làm giảm đóng góp của kết quả nằm xa đầu danh sách. IDCG là DCG của thứ tự lý tưởng trên cùng độ dài danh sách và cùng tập đích, nên NDCG nằm từ 0 đến 1 khi IDCG dương và không xác định khi IDCG bằng 0. Khóa luận dùng nhãn liên quan nhị phân: nghệ sĩ thuộc tập đích nhận 1, các nghệ sĩ khác nhận 0; khi đó IDCG được tính theo (2.19), công thức cũng được dùng cho các ví dụ tính tay ở Phụ lục B:",
)
drop(556, 557, 558)
at(560, "Khóa luận dùng NDCG@10 làm tiêu chí chính")
# RMSE
set_text(
    at(564, "Trong công thức (2.20)"),
    "Trong công thức (2.20), ⟦Ω_test⟧ là tập cặp người dùng–nghệ sĩ được đánh giá, ⟦r_ui⟧ là giá trị mục tiêu và ⟦r̂_ui⟧ là giá trị dự đoán; RMSE càng nhỏ thì dự đoán càng gần mục tiêu. Trong khóa luận, RMSE chỉ dùng bổ sung cho các mô hình dự đoán điểm đại diện trên thang 1–5. Điểm này được quy đổi từ lượt nghe bằng các ngưỡng học trên tập huấn luyện, không phải điểm do người nghe tự chấm. Điểm xếp hạng của PureSVD không nằm trên thang này, nên RMSE không thay thế các chỉ số xếp hạng khi chọn mô hình.",
)
drop(565, 566)
# Coverage, Gini, ARP
set_text(
    at(568, "Độ bao phủ danh mục (Catalog Coverage)"),
    "Ba chỉ số trong mục này mô tả phạm vi và mức tập trung của các nghệ sĩ được gợi ý. Độ bao phủ danh mục (Catalog Coverage) là tỷ lệ nghệ sĩ trong danh mục xuất hiện ít nhất một lần trong các danh sách gợi ý:",
)
set_text(
    at(570, "Trong công thức (2.21)"),
    "Trong công thức (2.21), U là tập người dùng được đánh giá, ⟦L_u^K⟧ là danh sách tối đa K nghệ sĩ của người dùng u và ⟦I_eval⟧ là danh mục nghệ sĩ đủ điều kiện, dùng chung làm mẫu số cho mọi mô hình. Độ bao phủ không cho biết số lần xuất hiện có đồng đều hay không, nên được xem cùng hệ số Gini (Gini coefficient) tính trên tần suất xuất hiện của các nghệ sĩ, sắp theo thứ tự tăng dần:",
)
after(B[570], B[575])  # (2.22)
gini = new_para(
    tpl,
    "Trong công thức (2.22), m là số nghệ sĩ trong danh mục và f(j) là số lần nghệ sĩ đứng thứ j được gợi ý, kể cả nghệ sĩ có tần suất 0. Gini bằng 0 khi mọi nghệ sĩ xuất hiện như nhau và tăng khi lượt gợi ý dồn vào ít nghệ sĩ; chỉ số không xác định khi không có kết quả nào. Độ phổ biến trung bình của khuyến nghị (Average Recommendation Popularity, ARP) lấy trung bình mức phổ biến tại các vị trí được gợi ý:",
)
after(B[575], gini, B[581])  # (2.23)
arp = new_para(
    tpl,
    "Trong công thức (2.23), ⟦c_i⟧ là số người dùng phân biệt đã nghe nghệ sĩ i trên tập huấn luyện; danh sách trả thiếu được tính trên số vị trí thực trả và báo cáo kèm tỷ lệ trả đủ. ARP thấp nghĩa là danh sách thiên về nghệ sĩ ít người nghe hơn. Gini và ARP chỉ mô tả mức tập trung và mức phổ biến của kết quả, không trực tiếp cho biết gợi ý có phù hợp hay hệ thống có công bằng; khi phân tích M1, khóa luận đối chiếu chúng với NDCG, độ bao phủ và độ đa dạng.",
)
after(B[581], arp)
drop(571, 572, 573, 574, 576, 577, 578, 579, 580, 582, 583, 584)
# Novelty
set_text(
    at(588, "Trong công thức (2.24)"),
    "Trong công thức (2.24), ⟦c_i⟧ là số người nghe phân biệt của nghệ sĩ i trên tập huấn luyện, cùng cách đếm với ARP, và ⟦P_i⟧ là mức phổ biến sau khi cộng một rồi chuẩn hóa trên danh mục ⟦I_eval⟧; ⟦−log_2 P_i⟧ là lượng thông tin của nghệ sĩ, tính bằng bit. Độ mới của danh sách là trung bình lượng thông tin của các nghệ sĩ được trả, nên càng cao khi danh sách càng thiên về nghệ sĩ ít phổ biến. Độ mới cao chưa chứng minh nghệ sĩ xa lạ với người nghe ngoài hệ thống, và ⟦P_i⟧ không phải xác suất người dùng yêu thích nghệ sĩ.",
)
drop(589, 590)
# ILD
set_text(
    at(594, "Trong công thức (2.25)"),
    "Trong công thức (2.25), ⟦i_a⟧ và ⟦i_b⟧ là hai nghệ sĩ ở vị trí a và b, sim là độ tương đồng côsin và tổng xét mỗi cặp một lần; với véc-tơ không âm, ILD nằm từ 0 đến 1 và càng cao thì các nghệ sĩ càng ít giống nhau. Nhóm cố định véc-tơ người nghe nhị phân trên tập huấn luyện để tính côsin cho mọi mô hình; danh sách ngắn được tính theo số nghệ sĩ thực trả và danh sách dưới hai nghệ sĩ được ghi là không áp dụng. Cách đo này không biểu thị trực tiếp khác biệt về âm thanh hay thể loại, nên được xem cùng chất lượng xếp hạng.",
)
drop(595, 596)


# ---------------------------------------------------------------- Chương 3: công thức, thuật toán
def swap_equation(old_i, new_i, prefix_new):
    """Keep the layout and number of old_i, take the maths of the advisor's version new_i."""
    old, new = B[old_i], B[new_i]
    assert text(new).strip().startswith(prefix_new), new_i
    olds = old.findall("m:oMath", NS)
    news = [blacken(copy.deepcopy(m)) for m in new.findall(".//m:oMath", NS)]
    assert len(olds) == len(news) == 1, (old_i, len(olds), len(news))
    olds[0].addprevious(news[0])
    old.remove(olds[0])
    drop(new_i)


swap_equation(731, 733, "i*=argmax")
swap_equation(757, 759, "hu=")
swap_equation(765, 768, "ωn=min")
swap_equation(766, 769, "sfallback=")

p = at(735, "Độ tương đồng giữa nghệ sĩ được tính bằng một cách biểu diễn cố định")
set_text(
    p,
    "Trong cài đặt, sim(i, j) là côsin giữa hai véc-tơ người nghe nhị phân trên tập huấn luyện; ⟦p̃_i⟧ tính theo (3.8). Thuật toán 3.1 trình bày toàn bộ M1. Với mỗi người dùng, M1 tính ma trận độ tương đồng C × C giữa các ứng viên (10.000 giá trị với C = 100) rồi thực hiện K bước chọn, mỗi bước duyệt tối đa C ứng viên, tức khoảng 1.000 lần tra độ tương đồng với K = 10. Ở trung vị, M1 chậm hơn PureSVD khoảng 3,4 ms (Bảng 5.6).",
)
drop(736)
# 3.9 explanation: the tilde covered the whole s_ui and p_i
set_text(
    at(734, "Trong công thức (3.9)"),
    "Trong công thức (3.9), ⟦𝒞⟧ là tập ứng viên, S là tập đã chọn; ⟦s̃_ui⟧ và ⟦p̃_i⟧ lần lượt là điểm phù hợp và mức phổ biến đã chuẩn hóa. Hàm sim đo độ tương đồng giữa hai nghệ sĩ. Hệ số λ nằm từ 0 đến 1 và β không âm. Khi S rỗng, phần phạt tương đồng bằng 0. Với λ = 1 và β = 0, thứ tự trở về thứ tự của mô hình nền. Tăng mức phạt có thể làm danh sách khác biệt hoặc ít phổ biến hơn, nhưng cũng có thể giảm mức phù hợp.",
)


def algorithm(table_i, caption_i, lines):
    """Rewrite the one-cell pseudo-code table: lines separated by line breaks.

    Only the 'Đầu vào:' and 'Đầu ra:' labels are bold; the script letter 𝒞 is set in
    Cambria Math (Times New Roman has no glyph for it).
    """
    blacken(B[caption_i])
    tb = blacken(B[table_i])
    para = tb.find(".//w:tc/w:p", NS)
    rpr = first_rpr(para)
    for b in rpr.findall("w:b", NS) + rpr.findall("w:bCs", NS):
        rpr.remove(b)
    for c in list(para):
        if c.tag != q("pPr"):
            para.remove(c)

    def add(s, bold=False, br=False, math_font=False):
        r = etree.SubElement(para, q("r"))
        rp = copy.deepcopy(rpr)
        if bold:
            rp.insert(0, etree.Element(q("b")))
        if math_font:
            f = rp.find("w:rFonts", NS)
            if f is None:
                f = etree.Element(q("rFonts"))
                rp.insert(0, f)
            for a in ("ascii", "hAnsi", "cs"):
                f.set(q(a), "Cambria Math")
        r.append(rp)
        if br:
            etree.SubElement(r, q("br"))
        if s:
            t = etree.SubElement(r, q("t"))
            t.text = s
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    for k, line in enumerate(lines):
        label = re.match(r"^(Đầu vào:|Đầu ra:)(.*)$", line)
        if label:
            add(label.group(1), bold=True, br=k > 0)
            line = label.group(2)
        elif k:
            add("", br=True)
        for n, piece in enumerate(line.split("𝒞")):
            if n:
                add("𝒞", math_font=True)
            if piece:
                add(piece)


at(738, "Thuật toán 3.1")
algorithm(
    739,
    738,
    [
        "Đầu vào: người dùng u; điểm s_ui của mô hình nền (PureSVD nhị phân, k = 16); lịch sử huấn luyện H_u; số ứng viên C = 100; độ dài danh sách K; tham số λ, β; độ tương đồng sim(i, j); số người nghe c_i trên tập huấn luyện.",
        "Đầu ra: danh sách S gồm tối đa K nghệ sĩ theo thứ tự, mỗi nghệ sĩ kèm điểm gốc s_ui.",
        "1. 𝒞 ← tối đa C nghệ sĩ có s_ui cao nhất, không thuộc H_u, giữ thứ tự của mô hình nền",
        "2. Tính s̃_ui theo (3.7) trên 𝒞 và p̃_i theo (3.8)",
        "3. if λ = 1 và β = 0 then return K nghệ sĩ đầu của 𝒞",
        "4. S ← danh sách rỗng",
        "5. while |S| < K và 𝒞 \\ S khác rỗng do",
        "6.     for each i ∈ 𝒞 \\ S do",
        "7.         d(i) ← max_{j ∈ S} sim(i, j)   (d(i) = 0 khi S rỗng)",
        "8.         g(i) ← λ·s̃_ui − (1 − λ)·d(i) − β·p̃_i, làm tròn 12 chữ số thập phân",
        "9.     i* ← argmax g(i); nếu hòa, chọn nghệ sĩ đứng trước trong thứ tự của mô hình nền",
        "10.    Thêm i* vào cuối S",
        "11. return S",
    ],
)
p = at(764, "M2 kết hợp điểm cộng tác với điểm dự phòng")
must(
    p,
    "Trọng số cộng tác tăng theo số nghệ sĩ hợp lệ trong lịch sử",
    "Trọng số cộng tác tăng theo số nghệ sĩ được cung cấp",
)
must(
    p,
    "Các thành phần được chuẩn hóa về thang tương thích trước khi cộng:",
    "Các thành phần được đưa về đoạn [0, 1] trước khi cộng: điểm ItemCF (trung bình có trọng số trên thang điểm đại diện 1–5) được quy đổi bằng (s − 1)/4, điểm nội dung là côsin cắt về [0, 1], còn điểm phổ biến được chia cho giá trị lớn nhất trên danh mục:",
)
p = at(771, "Với cấu hình đã chọn")
set_text(
    p,
    "Với cấu hình đã chọn (α = 0,75; n_{min} = 10) và N ≤ 5 thì ω(N) = N/10 ≤ 0,5, trong đó N là số nghệ sĩ được cung cấp. Bảng 3.6 cho trọng số danh nghĩa của ba thành phần trên thang đã chuẩn hóa.",
)
at(779, "Thuật toán 3.2")
algorithm(
    780,
    779,
    [
        "Đầu vào: hồ sơ P gồm các nghệ sĩ người dùng cung cấp (có thể rỗng) kèm lượt nghe; ItemCF với L = 40 láng giềng, không co rút, học trên nhóm học; véc-tơ thẻ TF–IDF x_i theo (3.10); điểm phổ biến pop_i (tổng log₂(1 + w) trên nhóm học); α = 0,75; n_min = 10; K.",
        "Đầu ra: danh sách K nghệ sĩ và nhãn đường xử lý (Bảng 4.14).",
        "1. if P rỗng then return K nghệ sĩ có pop_i cao nhất, nhãn “popularity”",
        "2. n ← |P|; P′ ← các nghệ sĩ của P có trong danh mục nhóm học",
        "3. 𝒞 ← danh mục nhóm học bỏ đi các nghệ sĩ của P",
        "4. for each i ∈ 𝒞: s_CF(i) ← trung bình có trọng số (2.4) của điểm đại diện 1–5 của các nghệ sĩ trong P′ là láng giềng của i; không khả dụng nếu không có nghệ sĩ nào như vậy",
        "5. h ← hồ sơ thẻ theo (3.11) trên P′; s_content(i) ← cos(h, x_i), không khả dụng nếu h = 0 hoặc i không có thẻ",
        "6. s̃_CF(i) ← (s_CF(i) − 1)/4 cắt về [0, 1]; s̃_content(i) ← max(0, s_content(i)); s̃_pop(i) ← pop_i / max_j pop_j",
        "7. ω(i) ← min(1, n/n_min) nếu s_CF(i) khả dụng, ngược lại ω(i) ← 0",
        "8. s_fallback(i) ← α·s̃_content(i) + (1 − α)·s̃_pop(i), hoặc s̃_pop(i) nếu thiếu điểm nội dung   (3.13)",
        "9. s_M2(i) ← ω(i)·s̃_CF(i) + (1 − ω(i))·s_fallback(i)   (3.12)",
        "10. return K nghệ sĩ có s_M2 cao nhất (điểm làm tròn 12 chữ số thập phân, hòa thì theo thứ tự mã nghệ sĩ) và nhãn đường xử lý",
    ],
)
p = at(777, "Lịch sử rỗng dẫn đến gợi ý theo mức phổ biến")
must(
    p,
    "Hình 3.6 tóm tắt các tình huống này.",
    "Hình 3.6 tóm tắt các tình huống này, còn Thuật toán 3.2 trình bày toàn bộ luồng xử lý.",
)
p = at(805, "Nhóm đã kiểm chứng bộ đánh giá")
must(p, "Kiểm tra lưu và nạp mô hình sẽ thực hiện khi triển khai từng mô hình.", blue_text(807))
drop(807)

# 3.7.4 (illustration) folded into the 3.9 explanation, as the advisor asked to shorten it
at(746, "3.7.4 Minh họa cách chọn kết quả")
at(747, "Nếu hai ứng viên có điểm phù hợp cao")
must(
    B[734],
    "nhưng cũng có thể giảm mức phù hợp.",
    "nhưng cũng có thể giảm mức phù hợp. Ví dụ, khi hai ứng viên có điểm phù hợp cao nhưng rất giống nhau, M1 có thể giữ một nghệ sĩ rồi chọn một nghệ sĩ khác biệt hơn; nghệ sĩ ít phổ biến cũng có thể được đưa lên nếu mức phù hợp vẫn đủ tốt.",
)
drop(746, 747)

# ---------------------------------------------------------------- Chương 4
p = at(820, "Khoảng tin cậy 95% (và 90%")
must(
    p,
    "các giá trị còn lại ghi ba chữ số thập phân.",
    "các giá trị còn lại ghi ba chữ số thập phân. Các chỉ số, chênh lệch và khoảng tin cậy được ghi bốn chữ số thập phân, làm tròn từ giá trị gốc trong tệp kết quả; chênh lệch được tính từ giá trị gốc rồi mới làm tròn. Tham số mô hình như η và λreg được ghi đúng giá trị đã cấu hình.",
)
# 4.6: Bảng 4.9 -> Phụ lục D.6
set_text(
    at(867, "Như đã nêu ở mục 4.2"),
    "Như đã nêu ở mục 4.2, gần như mọi người dùng có đúng 40 tương tác huấn luyện: trong 1.855 người dùng có đích kiểm thử hợp lệ, chỉ 37 người có dưới 40 tương tác. Khoảng tin cậy của nhóm này rất rộng, nên NDCG@10 theo độ dài lịch sử chỉ mang tính mô tả và được đưa vào Bảng 4.9 ở Phụ lục D. Ảnh hưởng của độ dài lịch sử được khảo sát chủ động bằng thí nghiệm Given-N ở mục 4.8 và 4.11.",
)
cap49, tb49, note49 = at(868, "Bảng 4.9"), B[869], at(870, "Bootstrap 1.000 lần")
# 4.9 ALS: one sentence, details moved to 6.4
set_text(
    at(923, "Nhóm có thử thêm một hướng giảm thiên lệch phổ biến trên ALS"),
    "Nhóm cũng thử một hướng giảm thiên lệch độ phổ biến riêng cho ALS, chỉ trên tập xác thực; hướng này không vượt cách phạt phổ biến trực tiếp trên ALS nên không được chấm trên tập kiểm thử (mục 6.4). Ứng dụng ở Chương 5 cho phép chọn cả PureSVD, M1 và ALS.",
)
# 4.11 intro
at(932, "Các phân tích trong mục này được thực hiện")
set_text(B[932], blue_text(934))
drop(934)
# 4.11.2: Bảng 4.19 -> Phụ lục D.5
cap419, tb419, note419 = at(945, "Bảng 4.19"), B[946], at(947, "Chỉ dùng tập xác thực")
p = at(948, "Bảng 4.19 cho thấy ba nhóm kết quả")
must(p, "Bảng 4.19 cho thấy ba nhóm kết quả.", "Bảng 4.19 ở Phụ lục D cho thấy ba nhóm kết quả.")
# 4.12: bảng tổng hợp, RQ1, mô hình mặc định
at(961, "Về RQ1, với cấu hình đã khóa")
cap_new = strip_ids(copy.deepcopy(cap49))
runs = cap_new.findall("w:r", NS)
number_run = next(
    r
    for r in runs
    if r.find("w:t", NS) is not None and (r.find("w:t", NS).text or "").strip().isdigit()
)
number_run.find("w:t", NS).text = "22"
runs[-1].find("w:t", NS).text = " Tổng hợp NDCG@10 trên tập kiểm thử của mọi mô hình đã đo"
at(963, "Bảng 4.22 Tổng hợp")
tb_new = blacken(B[964])
note_new = new_para(
    note49, "Số liệu lấy từ Bảng 4.5 và Bảng 4.17, cùng 1.855 người dùng của tập kiểm thử."
)
rq1 = new_para(B[961], blue_text(966))
after(B[961], cap_new, tb_new, note_new, rq1)
drop(963, 965, 966)
set_text(
    at(969, "Từ các kết quả trên, ứng dụng ở Chương 5 dùng PureSVD"),
    "Từ các kết quả trên, ứng dụng ở Chương 5 giữ PureSVD làm mô hình mặc định cho người dùng có sẵn vì ba lý do. Thứ nhất, đây là mô hình tốt nhất trong các mô hình đã khóa trước khi mở tập kiểm thử. Thứ hai, M1 được tinh chỉnh và kiểm định tương đương trên nền PureSVD, nên khi bật M1 người dùng chỉ thấy thứ tự thay đổi trên cùng một tập ứng viên. Thứ ba, cấu hình này đã qua các ca kiểm thử chức năng ở Bảng 5.4 và phép đối chiếu với đánh giá ngoại tuyến ở mục 5.4.2. Implicit ALS, có NDCG@10 cao nhất trong các mô hình đã đo, được cung cấp như một lựa chọn; các mô hình láng giềng top-N chưa được đưa vào vì là kết quả của phân tích bổ sung trên một lần chia. Người dùng mới được phục vụ bởi M2, còn lịch sử rỗng được phục vụ bởi Popularity. Việc chuyển mô hình mặc định sang ALS hoặc áp dụng M1 trên ALS cần một lần chia mới để chọn lại tham số mà không dùng tập kiểm thử hiện tại, và được nêu ở mục 6.4.",
)
drop(971)
p = at(973, "Chương 4 đã trình bày kết quả tinh chỉnh")
must(
    p,
    "trên tập kiểm thử (0,182780), hơn Popularity 0,114005 và khác biệt có ý nghĩa thống kê;",
    "trên tập kiểm thử (0,182780, so với 0,068775 của Popularity; chênh lệch 0,114005, có ý nghĩa thống kê);",
)
must(p, "kèm các phân tích bổ sung sau khi khóa cấu hình.", "kèm các phân tích bổ sung.")
drop(975)

# ---------------------------------------------------------------- Chương 6
set_text(
    at(1088, "Với cấu hình đã khóa, PureSVD nhị phân"),
    "Trong các mô hình đã khóa, PureSVD nhị phân tốt nhất và là mô hình cá nhân hóa duy nhất vượt Popularity; với cách tổng hợp trung bình có trọng số và lưới đã khóa, UserCF, ItemCF và SVD có độ lệch không vượt Popularity. Phân tích bổ sung cho thấy hai kết luận phụ thuộc lựa chọn thiết kế: với cách tổng hợp top-N, mô hình láng giềng cao hơn PureSVD với cỡ hiệu ứng nhỏ trên một lần chia; và M2 cao hơn Popularity khi tập đích là toàn bộ nghệ sĩ người dùng chưa cung cấp, ở mức sơ bộ. M1 giảm độ phổ biến trung bình của danh sách mà vẫn tương đương mô hình nền về NDCG@10. Xét mọi mô hình đã đo, implicit ALS đạt NDCG@10 cao nhất (0,217453); ứng dụng giữ PureSVD làm mặc định vì M1 được tinh chỉnh và kiểm định tương đương trên mô hình này. Hệ thống được đóng gói thành dịch vụ FastAPI và giao diện Next.js, cho danh sách trùng hoàn toàn với đánh giá ngoại tuyến. Bảng 6.2 tóm tắt câu trả lời cho năm câu hỏi nghiên cứu kèm số liệu.",
)
tb62 = B[1091]
rows = tb62.findall("w:tr", NS)
rq1_cell = rows[1].findall("w:tc", NS)[1]
assert text(rq1_cell).startswith("Với cấu hình đã khóa, PureSVD nhị phân (k = 16)")
cell_p = rq1_cell.findall("w:p", NS)
for extra in cell_p[1:]:
    rq1_cell.remove(extra)
set_text(
    cell_p[0],
    "Trong các mô hình đã khóa, PureSVD nhị phân (k = 16) tốt nhất, NDCG@10 = 0,182780 so với 0,068775 của Popularity, chênh lệch có ý nghĩa thống kê; UserCF, ItemCF (trung bình có trọng số) và SVD có độ lệch không vượt Popularity. Phân tích bổ sung: với cách tổng hợp top-N, UserCF và ItemCF cao hơn PureSVD với cỡ hiệu ứng nhỏ; implicit ALS (mở rộng) cao nhất trong mọi mô hình đã đo, 0,217453.",
)
p = at(1098, "Ngắn hạn, các hướng sau")
als = new_para(
    p,
    "Trên tập xác thực, nhóm đã thử giảm thiên lệch độ phổ biến của ALS bằng cách trừ khỏi ma trận điểm thành phần ứng với giá trị suy biến lớn nhất (thành phần này có hệ số tương quan hạng Spearman 0,737 với số người nghe của nghệ sĩ), với mức trừ chung hoặc theo từng người dùng. Cả sáu cấu hình còn trong ngưỡng giảm 5% NDCG@10 đều bị cách phạt phổ biến trực tiếp trên ALS trội hơn, nên hướng tiếp theo là phạt phổ biến hoặc áp dụng M1 trên ALS. Sau khi kiểm chứng trên một lần chia mới, ứng dụng có thể chuyển mô hình mặc định sang ALS hoặc mô hình láng giềng top-N.",
)
after(p, als)

# ---------------------------------------------------------------- Tài liệu tham khảo (IEEE)
IEEE = {
    1: "IFPI, “Global Music Report 2026: Global recorded music revenues grow 6.4% as record companies drive innovation,” Mar. 18, 2026. [Online]. Available: https://www.ifpi.org/global-music-report-2026-global-recorded-music-revenues-grow-6-4-as-record-companies-drive-innovation/ (truy cập ngày 11/11/2026).",
    2: "G. Adomavicius and A. Tuzhilin, “Toward the next generation of recommender systems: A survey of the state-of-the-art and possible extensions,” IEEE Trans. Knowl. Data Eng., vol. 17, no. 6, pp. 734–749, 2005.",
    3: "M. Schedl, H. Zamani, C.-W. Chen, Y. Deldjoo, and M. Elahi, “Current challenges and visions in music recommender systems research,” Int. J. Multimed. Inf. Retr., vol. 7, no. 2, pp. 95–116, 2018.",
    4: "Spotify, “Discover Weekly turns 10: Celebrating 100 billion+ tracks streamed and a decade of personalized discovery,” Jun. 30, 2025. [Online]. Available: https://newsroom.spotify.com/2025-06-30/discover-weekly-turns-10-celebrating-100-billion-tracks-streamed-and-a-decade-of-personalized-discovery/ (truy cập ngày 11/11/2026).",
    5: "B. Sarwar, G. Karypis, J. Konstan, and J. Riedl, “Item-based collaborative filtering recommendation algorithms,” in Proc. 10th Int. World Wide Web Conf. (WWW), 2001, pp. 285–295. [Online]. Available: https://files.grouplens.org/papers/www10_sarwar.pdf",
    6: "Y. Koren, R. Bell, and C. Volinsky, “Matrix factorization techniques for recommender systems,” Computer, vol. 42, no. 8, pp. 30–37, 2009, doi: 10.1109/MC.2009.263.",
    7: "GroupLens Research, “hetrec2011-lastfm-2k: Readme,” version 1.0, May 2011. [Online]. Available: https://files.grouplens.org/datasets/hetrec2011/hetrec2011-lastfm-readme.txt",
    8: "Y. Hu, Y. Koren, and C. Volinsky, “Collaborative filtering for implicit feedback datasets,” in Proc. 8th IEEE Int. Conf. Data Mining (ICDM), 2008, pp. 263–272.",
    9: "D. Kowald, M. Schedl, and E. Lex, “The unfairness of popularity bias in music recommendation: A reproducibility study,” in Advances in Information Retrieval (ECIR 2020), ser. LNCS, vol. 12036. Cham, Switzerland: Springer, 2020, pp. 35–42.",
    10: "M. Kaminskas and D. Bridge, “Diversity, serendipity, novelty, and coverage: A survey and empirical analysis of beyond-accuracy objectives in recommender systems,” ACM Trans. Interact. Intell. Syst., vol. 7, no. 1, Art. no. 2, 2016.",
    11: "F. Wilcoxon, “Individual comparisons by ranking methods,” Biometrics Bull., vol. 1, no. 6, pp. 80–83, 1945.",
    12: "S. Holm, “A simple sequentially rejective multiple test procedure,” Scand. J. Statist., vol. 6, no. 2, pp. 65–70, 1979.",
    13: "B. Efron and R. J. Tibshirani, An Introduction to the Bootstrap. New York, NY, USA: Chapman & Hall/CRC, 1993.",
    14: "J. Herlocker, J. A. Konstan, and J. Riedl, “An empirical analysis of design choices in neighborhood-based collaborative filtering algorithms,” Inf. Retr., vol. 5, no. 4, pp. 287–310, 2002, doi: 10.1023/A:1020443909834.",
    15: "C. Desrosiers and G. Karypis, “A comprehensive survey of neighborhood-based recommendation methods,” in Recommender Systems Handbook, F. Ricci, L. Rokach, and B. Shapira, Eds. Boston, MA, USA: Springer, 2011, pp. 107–144.",
    16: "P. Cremonesi, Y. Koren, and R. Turrin, “Performance of recommender algorithms on top-N recommendation tasks,” in Proc. 4th ACM Conf. Recommender Systems (RecSys), 2010, pp. 39–46, doi: 10.1145/1864708.1864721.",
    17: "M. Deshpande and G. Karypis, “Item-based top-N recommendation algorithms,” ACM Trans. Inf. Syst., vol. 22, no. 1, pp. 143–177, 2004, doi: 10.1145/963770.963776.",
    18: "N. Halko, P.-G. Martinsson, and J. A. Tropp, “Finding structure with randomness: Probabilistic algorithms for constructing approximate matrix decompositions,” SIAM Rev., vol. 53, no. 2, pp. 217–288, 2011.",
    19: "A. I. Schein, A. Popescul, L. H. Ungar, and D. M. Pennock, “Methods and metrics for cold-start recommendations,” in Proc. 25th Annu. Int. ACM SIGIR Conf. (SIGIR), 2002, pp. 253–260.",
    20: "B. Lika, K. Kolomvatsos, and S. Hadjiefthymiades, “Facing the cold start problem in recommender systems,” Expert Syst. Appl., vol. 41, no. 4, pp. 2065–2073, 2014.",
    21: "R. Burke, “Hybrid recommender systems: Survey and experiments,” User Model. User-Adapt. Interact., vol. 12, no. 4, pp. 331–370, 2002.",
    22: "J. Carbonell and J. Goldstein, “The use of MMR, diversity-based reranking for reordering documents and producing summaries,” in Proc. 21st Annu. Int. ACM SIGIR Conf. (SIGIR), 1998, pp. 335–336.",
    23: "H. Abdollahpouri, R. Burke, and B. Mobasher, “Managing popularity bias in recommender systems with personalized re-ranking,” in Proc. 32nd Int. FLAIRS Conf., 2019, pp. 413–418.",
    24: "J. L. Herlocker, J. A. Konstan, L. G. Terveen, and J. T. Riedl, “Evaluating collaborative filtering recommender systems,” ACM Trans. Inf. Syst., vol. 22, no. 1, pp. 5–53, 2004.",
    25: "Z. Sun, D. Yu, H. Fang, J. Yang, X. Qu, J. Zhang, and C. Geng, “Are we evaluating rigorously? Benchmarking recommendation for reproducible evaluation and fair comparison,” in Proc. 14th ACM Conf. Recommender Systems (RecSys), 2020, pp. 23–32.",
    26: "Y. Ji, A. Sun, J. Zhang, and C. Li, “A critical study on data leakage in recommender system offline evaluation,” ACM Trans. Inf. Syst., vol. 41, no. 3, Art. no. 75, 2023, doi: 10.1145/3569930.",
    27: "K. Järvelin and J. Kekäläinen, “Cumulated gain-based evaluation of IR techniques,” ACM Trans. Inf. Syst., vol. 20, no. 4, pp. 422–446, 2002.",
    28: "D. S. Kerby, “The simple difference formula: An approach to teaching nonparametric correlation,” Compr. Psychol., vol. 3, Art. no. 11.IT.3.1, 2014.",
    29: "D. J. Schuirmann, “A comparison of the two one-sided tests procedure and the power approach for assessing the equivalence of average bioavailability,” J. Pharmacokinet. Biopharm., vol. 15, no. 6, pp. 657–680, 1987, doi: 10.1007/BF01068419.",
    30: "J. S. Breese, D. Heckerman, and C. Kadie, “Empirical analysis of predictive algorithms for collaborative filtering,” in Proc. 14th Conf. Uncertainty in Artificial Intelligence (UAI), 1998, pp. 43–52.",
    31: "I. Cantador, P. Brusilovsky, and T. Kuflik, “Second workshop on information heterogeneity and fusion in recommender systems (HetRec 2011),” in Proc. 5th ACM Conf. Recommender Systems (RecSys), 2011, pp. 387–388.",
    32: "E. S. da Silva, H. Langseth, and H. Ramampiaro, “Content-based social recommendation with Poisson matrix factorization,” in Proc. ECML PKDD, 2017, pp. 530–546, doi: 10.1007/978-3-319-71249-9_32.",
    33: "Z. Cui, Y. Weng, X. Tang, F. Lyu, D. Liu, X. He, and C. Ma, “Comprehending knowledge graphs with large language models for recommender systems,” in Proc. 48th Int. ACM SIGIR Conf. (SIGIR), 2025, pp. 1229–1239, doi: 10.1145/3726302.3729932.",
    34: "scikit-learn developers, “sklearn.metrics.ndcg_score,” scikit-learn API documentation. [Online]. Available: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html (truy cập ngày 25/10/2026).",
    35: "P. Virtanen, R. Gommers, T. E. Oliphant, et al., “SciPy 1.0: Fundamental algorithms for scientific computing in Python,” Nat. Methods, vol. 17, no. 3, pp. 261–272, 2020, doi: 10.1038/s41592-019-0686-2.",
    36: "B. Frederickson, “implicit: Fast Python collaborative filtering for implicit feedback datasets,” version 0.7.3. [Online]. Available: https://github.com/benfred/implicit",
    37: "S. Ramírez, “FastAPI,” official documentation. [Online]. Available: https://fastapi.tiangolo.com (truy cập ngày 11/11/2026).",
    38: "Vercel, “Next.js Documentation,” 2026. [Online]. Available: https://nextjs.org/docs (truy cập ngày 11/11/2026).",
    39: "Snowflake Inc., “Streamlit Documentation,” 2026. [Online]. Available: https://docs.streamlit.io (truy cập ngày 11/11/2026).",
    40: "M. Schedl, S. Brandl, O. Lesota, E. Parada-Cabaleiro, D. Penz, and N. Rekabsaz, “LFM-2b: A dataset of enriched music listening events for recommender systems research and fairness analysis,” in Proc. ACM SIGIR Conf. Human Information Interaction and Retrieval (CHIIR), 2022, pp. 337–341, doi: 10.1145/3498366.3505791.",
    41: "S. Rendle, C. Freudenthaler, Z. Gantner, and L. Schmidt-Thieme, “BPR: Bayesian personalized ranking from implicit feedback,” in Proc. 25th Conf. Uncertainty in Artificial Intelligence (UAI), 2009, pp. 452–461.",
    42: "H. Steck, “Embarrassingly shallow autoencoders for sparse data,” in Proc. World Wide Web Conf. (WWW), 2019, pp. 3251–3257, doi: 10.1145/3308558.3313710.",
    43: "X. He, K. Deng, X. Wang, Y. Li, Y. Zhang, and M. Wang, “LightGCN: Simplifying and powering graph convolution network for recommendation,” in Proc. 43rd Int. ACM SIGIR Conf. (SIGIR), 2020, pp. 639–648, doi: 10.1145/3397271.3401063.",
}
IEEE[13] = IEEE[13].replace(
    "An Introduction to the Bootstrap.", "§An Introduction to the Bootstrap§."
)


def ieee_italic(s):
    """Italic venue: proceedings or book after 'in', otherwise the journal before 'vol.'."""
    if "§" in s:
        return s
    m = re.search(r"(”,? in )(.+?)(, (?:ser\.|F\. Ricci|\d{4}))", s)
    if m:
        return s[: m.start(2)] + "§" + m.group(2) + "§" + s[m.end(2) :]
    m = re.search(r"(”,? )([^“”]+?)(, (?:vol\.|\d{4}))", s)
    if (
        m
        and "Available" not in m.group(2)
        and "version" not in m.group(2)
        and not re.match(r"[A-Z][a-z]{2}\. \d", m.group(2))
    ):
        return s[: m.start(2)] + "§" + m.group(2) + "§" + s[m.end(2) :]
    return s


for n in range(1, 44):
    p = at(1104 + n, f"[{n}]")
    set_text(p, f"[{n}] {ieee_italic(IEEE[n])}")
drop(1102, 1103, 1104)

# ---------------------------------------------------------------- Phụ lục D.5, D.6
p = at(1213, "N@K là NDCG@K;")
must(
    p,
    "N@K là NDCG@K; giá trị làm tròn bốn chữ số thập phân (giá trị sáu chữ số của K = 10 ở Bảng 4.5).",
    "N@K là NDCG@K; giá trị làm tròn bốn chữ số thập phân từ giá trị gốc.",
)
head_d5 = at(1226, "D.5 Bảng độ nhạy ngoài biên lưới")
must(head_d5, "D.5 Bảng độ nhạy ngoài biên lưới", "D.5 Độ nhạy ngoài biên lưới trên tập xác thực")
cap_tpl = B[1223]


def appendix_caption(title):
    c = strip_ids(copy.deepcopy(cap_tpl))
    rs = c.findall("w:r", NS)
    rs[-1].find("w:t", NS).text = " " + title
    num = next(
        r
        for r in rs
        if r.find("w:t", NS) is not None and (r.find("w:t", NS).text or "").strip().isdigit()
    )
    num.find("w:t", NS).text = "0"
    return c


d5 = [appendix_caption("Độ nhạy ngoài biên lưới trên tập xác thực"), tb419, note419]
head_d6 = new_para(head_d5, "D.6 NDCG@10 theo độ dài lịch sử huấn luyện")
d6_intro = new_para(
    B[1227],
    "Bảng D.6 trình bày NDCG@10 trên tập kiểm thử của hai nhóm độ dài lịch sử huấn luyện (mục 4.6), kèm khoảng tin cậy 95%.",
)
d6 = [
    head_d6,
    d6_intro,
    appendix_caption("NDCG@10 trên tập kiểm thử theo độ dài lịch sử huấn luyện"),
    tb49,
    note49,
]
at(1227, "Kết quả độ nhạy ngoài biên lưới")
set_text(
    B[1227],
    "Bảng D.5 trình bày toàn bộ các cấu hình ngoài biên lưới của mục 4.11.2, gồm PureSVD, UserCF, ItemCF, implicit ALS và M2, chỉ đo trên tập xác thực.",
)
for e in [cap419, cap49]:
    body.remove(e)
# long appendix tables may break across pages (only the header row stays with the caption)
for tb in (tb419, tb49):
    for row in tb.findall("w:tr", NS)[1:]:
        for kn in row.iter(q("keepNext")):
            kn.getparent().remove(kn)
    head = tb.find("w:tr", NS)
    trpr = head.find("w:trPr", NS)
    if trpr is None:
        trpr = etree.Element(q("trPr"))
        head.insert(0, trpr)
    if trpr.find("w:tblHeader", NS) is None:
        trpr.append(etree.Element(q("tblHeader")))
after(B[1227], *d5, *d6)

# ---------------------------------------------------------------- toàn văn
ROUND_FROM_RAW = {  # printed value -> four decimals of the raw value in the result files
    "0,009850": "0,0098",  # 0.0098498669 Popularity, nhóm ưa chuộng thấp
    "0,010350": "0,0104",  # 0.0103500018 cận trên khoảng tin cậy UserCF
    "0,018850": "0,0189",  # 0.0188500018 UserCF, NDCG@10 kiểm thử
    "0,021650": "0,0216",  # 0.0216499276 ItemCF, nhóm ưa chuộng thấp
    "0,042350": "0,0424",  # 0.0423503912 M2 α = 0,90, n_min = 15
    "0,059750": "0,0597",  # 0.0597495843 Popularity, Given-N N = 5
    "0,062650": "0,0626",  # 0.0626499310 SVD có độ lệch, NDCG@10 kiểm thử
    "0,100150": "0,1001",  # 0.1001495078 cận dưới khoảng tin cậy M2 − ItemCF, N = 3
    "0,004450": "0,0045",  # −0.0044500100 cận dưới khoảng tin cậy M1 − PureSVD, nhóm trung bình
    "0,61315": "0,6131",  # 1/1,630930 (ví dụ tính tay, Phụ lục B)
    "0,000039": "0,00004",  # −0,000039: giữ một chữ số có nghĩa thay vì −0,0000
}
PHRASES = [
    ("các phân tích bổ sung sau khi khóa cấu hình", "các phân tích bổ sung"),
    ("Trong phân tích sau khi khóa cấu hình này", "Trong phân tích bổ sung này"),
    ("Phân tích sau khi khóa cấu hình", "Phân tích bổ sung"),
    ("phân tích sau khi khóa cấu hình", "phân tích bổ sung"),
    ("(phân tích sau khi khóa)", "(phân tích bổ sung)"),
    ("Thiên lệch phổ biến", "Thiên lệch độ phổ biến"),
    ("thiên lệch phổ biến", "thiên lệch độ phổ biến"),
]
TABLE_MAP = {"4.9": "D.6", "4.19": "D.5", "4.22": "4.20"}
for n in range(10, 19):
    TABLE_MAP[f"4.{n}"] = f"4.{n - 1}"
TABLE_MAP["4.20"], TABLE_MAP["4.21"] = "4.18", "4.19"
REF = re.compile(r"(Bảng|bảng)(\s+)(4\.\d+(?:\s*(?:,|–|và)\s*(?:Bảng\s+)?4\.\d+)*)")


def renumber(m):
    nums = re.sub(r"4\.\d+", lambda k: TABLE_MAP.get(k.group(0), k.group(0)), m.group(3))
    return m.group(1) + m.group(2) + nums


def merge_math_numbers(e):
    """Join maths runs '0' ',' '05' into one run '0,05' (Word spaces a lone comma operator)."""
    merged = 0
    for parent in list(e.iter()):
        kids = [k for k in parent if k.tag == q("r", M)]
        i = 0
        while i + 2 < len(kids):
            a, c, d = kids[i], kids[i + 1], kids[i + 2]
            ta, tc, td = (k.find("m:t", NS) for k in (a, c, d))
            if (
                None not in (ta, tc, td)
                and a.getnext() is c
                and c.getnext() is d
                and re.fullmatch(r"[−-]?\d+", ta.text or "")
                and tc.text == ","
                and re.fullmatch(r"\d+", td.text or "")
            ):
                ta.text = ta.text + "," + td.text
                parent.remove(c)
                parent.remove(d)
                kids = [k for k in parent if k.tag == q("r", M)]
                merged += 1
                continue
            i += 1
    return merged


log: list = []
merged_numbers = sum(merge_math_numbers(e) for e in body)
print("maths numbers joined:", merged_numbers)
phrase_hits = dict.fromkeys(PHRASES, 0)
ref_changes = []
for e in list(body):
    blacken(e)
    for p in paragraphs(e):
        for old, new in PHRASES:
            phrase_hits[(old, new)] += preplace(p, old, new)
        is_caption = (
            p.find("w:pPr/w:pStyle", NS) is not None
            and p.find("w:pPr/w:pStyle", NS).get(q("val")) == "Caption"
        )
        full = visible(p)
        if not is_caption:
            for m in reversed(list(REF.finditer(full))):
                new = renumber(m)
                if new != m.group(0):
                    ref_changes.append((m.group(0), new))
                    replace_span(p, m.start(), m.end(), new)
        round_paragraph(p, ROUND_FROM_RAW, log)
    for mr in e.iter(q("r", M)):
        if re.search(r"\d,\d", "".join(t.text or "" for t in mr.iter(q("t", M)))):
            nor_number(mr)

# leftovers
for e in body:
    t = text(e)
    assert "Cô góp ý" not in t and "Gợi ý viết lại" not in t, t[:80]
    assert not ({"FF0000", "0000FF"} & colours(e)), t[:80]
    assert "sau khi khóa cấu hình E7" not in t
print("rounded numbers:", len(log))
print("phrases:", {k[0]: v for k, v in phrase_hits.items()})
print("table references changed:", len(ref_changes))
for a, b in ref_changes:
    print("   ", a, "->", b)
tree.write(str(doc_path), xml_declaration=True, encoding="UTF-8", standalone=True)

# tighter spacing in the table of contents and the lists of figures and tables
styles_path = root_dir / "word/styles.xml"
styles = etree.parse(str(styles_path))
for sid in ("TOC1", "TOC2", "TOC3", "TableofFigures"):
    st = styles.getroot().find(f"w:style[@w:styleId='{sid}']", NS)
    ppr = st.find("w:pPr", NS)
    if ppr is None:
        ppr = etree.SubElement(st, q("pPr"))
    sp = ppr.find("w:spacing", NS)
    if sp is None:
        sp = etree.SubElement(ppr, q("spacing"))
    sp.set(q("before"), "40")
    sp.set(q("after"), "20" if sid != "TableofFigures" else "0")
    sp.set(q("line"), "276")
    sp.set(q("lineRule"), "auto")
styles.write(str(styles_path), xml_declaration=True, encoding="UTF-8", standalone=True)
print("ok")
