# ruff: noqa: E501
"""Build the SSRC paper v1 from the advisor's template (GopY_GVHD_18-11-2026_BaiBaoMau_SSRC.docx).

The template keeps its SSRC layout (Letter, two columns, Roman headings, IEEE references); this
script only replaces text inside document.xml and footnotes.xml, every replacement asserted to hit
exactly once, so a template change makes the build fail instead of silently skipping an edit.
Changes (all numbers from report v23 and its result files, see GHI_CHU_BAI_BAO_v1.md):
- remove the four red advisor notes (general note, IFPI, Table 4.13, response times);
- Table III: 95% CIs of the two E7 models; rounding 0,0627 -> 0,0626 (biased SVD) and in Table VI
  0,0598 -> 0,0597 (Popularity, N = 5), rounded once from the full value;
- post-lock wording and "small effect on one split" for E7, M1 by group and M2 with targets (5);
  conditions on the neighbourhood conclusion; M2 presented as preliminary; Popularity N = 0/1;
- e-mails of the two students; draft AI statement and submission date highlighted in yellow for
  the group to confirm (no red text left).
Usage (repository root):
    python -X utf8 docs/bai-bao-ssrc/dung_bai_bao_v1.py <template.docx> <out.docx>
"""

import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
work = Path(tempfile.mkdtemp())
zipfile.ZipFile(src).extractall(work)
doc_p, foot_p = work / "word/document.xml", work / "word/footnotes.xml"
doc = doc_p.read_text(encoding="utf-8")
foot = foot_p.read_text(encoding="utf-8")


def rep(text, old, new, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit(f"expected {count} hit(s), found {n}: {old[:90]!r}")
    return text.replace(old, new)


def drop_paragraph(text, marker):
    i = text.index(marker)
    s = max(text.rfind("<w:p>", 0, i), text.rfind("<w:p ", 0, i))
    e = text.index("</w:p>", i) + len("</w:p>")
    assert text.count(marker) == 1, marker
    return text[:s] + text[e:]


SZ = '<w:rPr><w:sz w:val="14"/><w:szCs w:val="14"/></w:rPr>'
HL = '<w:rPr><w:highlight w:val="yellow"/></w:rPr>'

# ---- red advisor notes
for marker in [
    "Cô gợi ý chỉnh sửa: Bài này được viết",
    "Cô gợi ý chỉnh sửa: Khóa luận Mục 1.1",
    "Cô gợi ý chỉnh sửa: Bảng 4.13",
    "Cô gợi ý chỉnh sửa: Bảng 5.6",
]:
    doc = drop_paragraph(doc, marker)

# ---- Abstract and Tóm tắt: M2 result with targets (5) is post-lock and preliminary
doc = rep(
    doc,
    "does not beat Popularity when the targets are the held-out test pairs, but does at N = 3 and N = 5 when all artists not given to the system are targets.",
    "does not beat Popularity when the targets are the held-out test pairs; in a post-lock analysis it scores higher at N = 3 and N = 5 when all artists not given to the system are targets, a preliminary result on 189 users.",
)
doc = rep(
    doc,
    "không vượt Popularity khi tập đích là các cặp kiểm thử, nhưng vượt ở N = 3 và N = 5 khi tập đích là toàn bộ nghệ sĩ chưa cung cấp cho hệ thống.",
    "không vượt Popularity khi tập đích là các cặp kiểm thử; phân tích sau khi khóa cấu hình cho thấy M2 cao hơn Popularity ở N = 3 và N = 5 khi tập đích là toàn bộ nghệ sĩ chưa cung cấp cho hệ thống, nhưng đây là kết quả sơ bộ trên 189 người dùng.",
)

# ---- equations (3) and (4) are cited by number (checklist of Part 7)
doc = rep(
    doc,
    " cũng là đại lượng tạo nên ARP, chúng tôi báo cáo thêm ILD theo thẻ,",
    " trong (3) cũng là đại lượng tạo nên ARP, chúng tôi báo cáo thêm ILD theo thẻ,",
)
doc = rep(
    doc,
    ") được chọn trên nhóm tinh chỉnh từ chín cấu hình",
    ") của (4) được chọn trên nhóm tinh chỉnh từ chín cấu hình",
)

# ---- Section IV-A: L = 5 (E8)
doc = rep(
    doc,
    "giảm L xuống 5 tăng NDCG@10 xác thực lên 0,0652 và 0,0565.",
    "giảm L xuống 5 tăng NDCG@10 xác thực lên 0,0652 và 0,0565; giá trị 0,0652 của UserCF cao hơn Popularity (0,0624).",
)

# ---- Table III: 95% CIs of the E7 models, single rounding of biased SVD
for value, ci in [("0,1937", "[0,1841; 0,2032]"), ("0,1940", "[0,1844; 0,2036]")]:
    doc = rep(
        doc,
        f'<w:r>{SZ}<w:t xml:space="preserve">{value}</w:t></w:r></w:p></w:tc>',
        f'<w:r>{SZ}<w:t xml:space="preserve">{value}</w:t></w:r><w:r><w:br/></w:r>'
        f'<w:r>{SZ}<w:t xml:space="preserve">{ci}</w:t></w:r></w:p></w:tc>',
    )
doc = rep(doc, '">0,0627</w:t>', '">0,0626</w:t>')
doc = rep(
    doc,
    "KTC bằng bootstrap 1.000 lần theo người dùng; khóa luận không báo KTC riêng cho hai mô hình E7.",
    "KTC bằng bootstrap 1.000 lần theo người dùng, hạt giống 42, trên một lần chia dữ liệu.",
)

# ---- Section IV-B: condition of the negative neighbourhood result
doc = rep(
    doc,
    "Popularity là đối chứng mạnh trên dữ liệu này: UserCF, ItemCF và SVD có độ lệch đều thấp hơn Popularity trên cả tập xác thực và tập kiểm thử.",
    "Popularity là đối chứng mạnh trên dữ liệu này: với cách tổng hợp trung bình có trọng số và lưới đã khóa, UserCF và ItemCF thấp hơn Popularity trên cả tập xác thực và tập kiểm thử, SVD có độ lệch cũng vậy.",
)

# ---- Section IV-C: E7
doc = rep(
    doc,
    "vượt Popularity với cỡ hiệu ứng lớn và vượt PureSVD 0,0109 và 0,0112 với cỡ hiệu ứng nhỏ (r",
    "cao hơn Popularity với cỡ hiệu ứng lớn và cao hơn PureSVD 0,0109 và 0,0112 với cỡ hiệu ứng nhỏ (r",
)
doc = rep(
    doc,
    "nhưng vẫn thấp hơn ALS (Bảng III, IV).",
    "nhưng vẫn thấp hơn ALS (Bảng III, IV). Hai chênh lệch với PureSVD chỉ dựa trên một lần chia dữ liệu, và KTC 95% của NDCG@10 trung bình của hai mô hình chồng lấn với KTC của PureSVD.",
)

# ---- Section IV-D: groups of popularity preference
doc = rep(
    doc,
    "thực hiện sau khi tập kiểm thử đã mở, chia người dùng",
    "là phân tích sau khi khóa cấu hình, chia người dùng",
)

# ---- Section IV-E: M2 preliminary, Popularity at N = 0 and N = 1, single rounding
doc = rep(
    doc,
    "NDCG@10 của Popularity chỉ 0,0276–0,0297 trên nhóm tinh chỉnh nhưng 0,0565–0,0598 trên nhóm để dành.",
    "NDCG@10 của Popularity chỉ 0,0276–0,0297 trên nhóm tinh chỉnh nhưng 0,0565–0,0597 trên nhóm để dành, và cấu hình được chọn nằm ở góc lưới, nên kết quả về M2 là sơ bộ. Popularity có cùng giá trị ở N = 0 và N = 1 vì chỉ 9 trên 189 người có nghệ sĩ được cung cấp nằm trong top-10 Popularity, và việc loại nghệ sĩ đó không làm đổi vị trí của đích nào.",
)
doc = rep(doc, '">0,0598</w:t>', '">0,0597</w:t>')
doc = rep(
    doc,
    "Vì giao thức (5) được chọn sau khi biết kết quả của giao thức đã khóa, chúng tôi xem đây là bằng chứng bổ sung.",
    "Vì giao thức (5) được chọn sau khi biết kết quả của giao thức đã khóa, đây là phân tích sau khi khóa cấu hình và là bằng chứng bổ sung.",
)

# ---- Discussion and conclusion
doc = rep(
    doc,
    "trong khi PureSVD, ALS và hai mô hình láng giềng chấm điểm kiểu top-N đều vượt rõ, phù hợp với [11], [17].",
    "trong khi PureSVD, ALS và (trong phân tích sau khi khóa cấu hình) hai mô hình láng giềng chấm điểm kiểu top-N đều cao hơn Popularity rõ rệt, phù hợp với [11], [17].",
)
doc = rep(
    doc,
    "Kết quả dựa trên một lần chia ngẫu nhiên với một hạt giống;",
    "Kết quả dựa trên một lần chia ngẫu nhiên với hạt giống 42;",
)
doc = rep(
    doc,
    "và mô hình láng giềng chỉ cạnh tranh khi chấm điểm kiểu top-N (0,1937 và 0,1940).",
    "và mô hình láng giềng chỉ cạnh tranh khi chấm điểm kiểu top-N (0,1937 và 0,1940, phân tích sau khi khóa cấu hình, cỡ hiệu ứng nhỏ so với PureSVD).",
)
doc = rep(
    doc,
    "còn M2 chỉ vượt Popularity khi tập đích là toàn bộ nghệ sĩ chưa cung cấp.",
    "còn M2 chỉ cao hơn Popularity khi tập đích là toàn bộ nghệ sĩ chưa cung cấp, trong phân tích sau khi khóa cấu hình và ở mức sơ bộ.",
)
doc = rep(
    doc,
    "Hướng tiếp theo gồm lặp lại thực nghiệm trên nhiều lần chia,",
    "Hướng tiếp theo gồm lặp lại thực nghiệm trên nhiều lần chia, đánh giá M2 bằng kiểm định chéo theo người dùng,",
)

# ---- Acknowledgement: draft AI statement, highlighted for the group to confirm
ai = (
    "Trong quá trình thực hiện, nhóm tác giả sử dụng các công cụ trí tuệ nhân tạo Claude (Anthropic) "
    "và Codex (OpenAI) để hỗ trợ viết và kiểm thử mã nguồn, đối chiếu số liệu giữa kết quả thực nghiệm "
    "và bản thảo, soạn nháp và chỉnh sửa diễn đạt một số đoạn văn. Nhóm tác giả đã kiểm tra lại toàn bộ "
    "mã nguồn, số liệu và nội dung, và chịu hoàn toàn trách nhiệm về bài báo."
)
m = re.search(
    r'<w:r><w:rPr><w:color w:val="FF0000"/></w:rPr><w:t xml:space="preserve">\[CẦN BỔ SUNG: câu công bố.*?</w:t></w:r>',
    doc,
)
assert m
doc = doc[: m.start()] + f'<w:r>{HL}<w:t xml:space="preserve">{ai}</w:t></w:r>' + doc[m.end() :]

# ---- Footnote: e-mails and submission date
foot = rep(
    foot,
    '<w:r><w:rPr><w:color w:val="FF0000"/></w:rPr><w:t xml:space="preserve">[CẦN BỔ SUNG: e-mail từng sinh viên]</w:t></w:r>',
    '<w:r><w:t xml:space="preserve">(e-mail: caotrongnguyen9@gmail.com, lekhang2004h@gmail.com)</w:t></w:r>',
)
foot = rep(
    foot,
    '<w:r><w:rPr><w:color w:val="FF0000"/></w:rPr><w:t xml:space="preserve"> Ngày nộp bài: [CẦN BỔ SUNG]. </w:t></w:r>',
    '<w:r><w:t xml:space="preserve"> Ngày nộp bài: </w:t></w:r>'
    f'<w:r>{HL}<w:t xml:space="preserve">…/…/2026</w:t></w:r>'
    '<w:r><w:t xml:space="preserve">. </w:t></w:r>',
)

# The template has the author footnote (affiliations, e-mails, submission date) in footnotes.xml
# but no reference to it, so Word does not print it. Attach it to the end of the title with a
# blank custom mark, as in the IEEE template (the footnote itself starts with a blank Symbol mark).
assert "footnoteReference" not in doc
doc = rep(
    doc,
    "giảm thiên lệch phổ biến</w:t></w:r></w:p>",
    "giảm thiên lệch phổ biến</w:t></w:r>"
    '<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr>'
    '<w:footnoteReference w:customMarkFollows="1" w:id="1"/>'
    '<w:sym w:font="Symbol" w:char="F020"/></w:r></w:p>',
)

for name, text in [("document", doc), ("footnotes", foot)]:
    assert 'w:val="FF0000"' not in text, f"red text left in {name}"
    assert "CẦN BỔ SUNG" not in text, f"placeholder left in {name}"
doc_p.write_text(doc, encoding="utf-8")
foot_p.write_text(foot, encoding="utf-8")

out.parent.mkdir(parents=True, exist_ok=True)
names = zipfile.ZipFile(src).namelist()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for n in names:
        z.write(work / n, n)
shutil.rmtree(work)
print("written", out)
