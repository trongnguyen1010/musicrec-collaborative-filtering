"""Build report v17 from the advisor's copy (GopY_GVHD_06-11-2026): rewrite Chapter 4.

Usage (from the repository root, after unzipping the advisor's docx into <unpacked>):
    python docs/bao-cao/nguon_v17/build_v17.py <unpacked> docs/bao-cao/nguon_v17/ch4_v17.py

Only Chapter 4 is replaced. Outside Chapter 4 the only edit is the PureSVD log-count value
in section 3.6.4 (0,153543 has no source; data card gives 0,154577) and the advisor's blue
"(chi tiết ở Bảng 4.4)" turned black. Every other advisor mark is left for later chapters.
Templates (body text, headings, caption, table, source note, picture) are copied from
Chapter 3 of the same document so the styles match.
"""

import copy
import re
import shutil
import struct
import sys
from pathlib import Path

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
NS = {"w": W, "r": R, "wp": WP, "a": A, "pic": PIC}


def q(tag: str, ns: str = W) -> str:
    return f"{{{ns}}}{tag}"


root_dir, content_file = Path(sys.argv[1]), sys.argv[2]
doc_path = root_dir / "word/document.xml"
tree = etree.parse(str(doc_path))
body = tree.getroot().find("w:body", NS)


def text(e):
    return "".join(e.itertext())


def find_para(prefix, start=300):
    for i, e in enumerate(list(body)):
        if i >= start and e.tag == q("p") and text(e).startswith(prefix):
            return e
    raise KeyError(prefix)


def strip_ids(e):
    for el in e.iter():
        for k in list(el.attrib):
            if k.endswith("}paraId") or k.endswith("}textId"):
                del el.attrib[k]
    for bm in e.findall(".//w:bookmarkStart", NS) + e.findall(".//w:bookmarkEnd", NS):
        bm.getparent().remove(bm)
    for el in e.findall(".//w:lastRenderedPageBreak", NS):
        el.getparent().remove(el)
    return e


# ---- templates from Chapter 3 ----
body_tpl = strip_ids(copy.deepcopy(find_para("Mô hình nền của M1 là PureSVD")))
h2_tpl = strip_ids(copy.deepcopy(find_para("3.6 Thiết kế các mô hình")))
h3_tpl = strip_ids(copy.deepcopy(find_para("3.6.4 SVD có độ lệch")))
cap_tpl = strip_ids(copy.deepcopy(find_para("Bảng 3. SEQ Bang 3 Đầu vào")))
tbl_tpl = copy.deepcopy(find_para("Bảng 3. SEQ Bang 3 Đầu vào").getnext())
note_tpl = strip_ids(copy.deepcopy(find_para("Nguồn: trường config")))
FIG31 = r"Hình 3. SEQ Hinh \r 1 1"
pic_tpl = strip_ids(copy.deepcopy(find_para(FIG31).getprevious()))
fig_cap_tpl = strip_ids(copy.deepcopy(find_para(FIG31)))
run_rpr = copy.deepcopy(body_tpl.find("w:r/w:rPr", NS))


def make_run(s, bold=False, italic=False, rpr=None):
    r = etree.Element(q("r"))
    p = copy.deepcopy(rpr if rpr is not None else run_rpr)
    for flag, tag in [(bold, "b"), (italic, "i")]:
        if flag and p.find(f"w:{tag}", NS) is None:
            p.insert(0, etree.Element(q(tag)))
    r.append(p)
    t = etree.SubElement(r, q("t"))
    t.text = s
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return r


def fill(p, s, rpr=None):
    """Replace runs of p with s; **x** marks bold."""
    for c in list(p):
        if c.tag != q("pPr"):
            p.remove(c)
    for k, part in enumerate(re.split(r"\*\*", s)):
        if part:
            p.append(make_run(part, bold=k % 2 == 1, rpr=rpr))
    return p


def para(s):
    return fill(copy.deepcopy(body_tpl), s)


def note(s):
    p = copy.deepcopy(note_tpl)
    return fill(p, s, rpr=note_tpl.find("w:r/w:rPr", NS))


def heading(tpl, s):
    p = copy.deepcopy(tpl)
    return fill(p, s, rpr=copy.deepcopy(tpl.find("w:r/w:rPr", NS)))


counters = {"Bang": 0, "Hinh": 0}


def caption(tpl, prefix, kind, title):
    p = copy.deepcopy(tpl)
    runs = p.findall("w:r", NS)
    runs[0].find("w:t", NS).text = prefix
    instr = next(r.find("w:instrText", NS) for r in runs if r.find("w:instrText", NS) is not None)
    counters[kind] += 1
    instr.text = f" SEQ {kind} \\r 1 " if counters[kind] == 1 else f" SEQ {kind} "
    number = next(
        r
        for r in runs
        if r.find("w:t", NS) is not None and r.find("w:t", NS).text.strip().isdigit()
    )
    number.find("w:t", NS).text = str(counters[kind])
    runs[-1].find("w:t", NS).text = " " + title
    return p


def table(widths, header, rows, align=None):
    tb = copy.deepcopy(tbl_tpl)
    tb.find("w:tblPr/w:tblW", NS).set(q("w"), str(sum(widths)))
    grid = tb.find("w:tblGrid", NS)
    for g in list(grid):
        grid.remove(g)
    for w in widths:
        etree.SubElement(grid, q("gridCol")).set(q("w"), str(w))
    trs = tb.findall("w:tr", NS)
    head_tr, body_tr = trs[0], trs[1]
    for tr in trs:
        tb.remove(tr)
    align = align or (["left"] + ["center"] * (len(widths) - 1))

    def build(tpl_tr, cells, bold):
        tr = copy.deepcopy(tpl_tr)
        for tc in tr.findall("w:tc", NS):
            tr.remove(tc)
        tc_tpl = tpl_tr.find("w:tc", NS)
        for w, val, al in zip(widths, cells, align, strict=True):
            tc = copy.deepcopy(tc_tpl)
            tc.find("w:tcPr/w:tcW", NS).set(q("w"), str(w))
            p = strip_ids(tc.find("w:p", NS))
            p.find("w:pPr/w:jc", NS).set(q("val"), "center" if bold else al)
            rpr = copy.deepcopy(p.find("w:r/w:rPr", NS))
            if bold and rpr.find("w:b", NS) is None:
                rpr.insert(0, etree.Element(q("b")))
            fill(p, val if val else " ", rpr=rpr)
            tr.append(tc)
        return strip_ids(tr)

    tb.append(build(head_tr, header, True))
    for row in rows:
        tb.append(build(body_tr, row, False))
    return tb


# ---- pictures ----
rels_path = root_dir / "word/_rels/document.xml.rels"
rels = etree.parse(str(rels_path))
rid_numbers = [int(r.get("Id")[3:]) for r in rels.getroot() if r.get("Id", "").startswith("rId")]
next_rid = [max(rid_numbers) + 1]
doc_pr_ids = [int(e.get("id")) for e in tree.getroot().iter(q("docPr", WP))]
next_pr = [max(doc_pr_ids) + 1]
(root_dir / "word/media").mkdir(exist_ok=True)


def picture(png: Path, width_cm: float, title: str):
    data = png.read_bytes()
    w_px, h_px = struct.unpack(">II", data[16:24])
    cx = int(width_cm * 360000)
    cy = int(cx * h_px / w_px)
    name = f"ch4_{next_rid[0]}.png"
    shutil.copyfile(png, root_dir / "word/media" / name)
    rid = f"rId{next_rid[0]}"
    next_rid[0] += 1
    etree.SubElement(
        rels.getroot(),
        "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship",
        Id=rid,
        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
        Target=f"media/{name}",
    )
    p = copy.deepcopy(pic_tpl)
    p.find(".//wp:extent", NS).attrib.update({"cx": str(cx), "cy": str(cy)})
    p.find(".//a:ext", NS).attrib.update({"cx": str(cx), "cy": str(cy)})
    for tag, ns in [("docPr", WP), ("cNvPr", PIC)]:
        e = p.find(f".//{{{ns}}}{tag}")
        e.attrib.update({"id": str(next_pr[0]), "name": title, "descr": title})
    next_pr[0] += 1
    p.find(".//a:blip", NS).set(q("embed", R), rid)
    return p


# ---- 1. Section 3.6.4: fix the unsourced log-count value, blackened advisor note ----
for t in body.iter(q("t")):
    if t.text and "0,153543" in t.text:
        t.text = t.text.replace("0,153543", "0,154577")
for r in body.iter(q("r")):
    if "chi tiết ở Bảng 4.4" in text(r):
        r.find("w:rPr/w:color", NS).set(q("val"), "000000")

# ---- 2. Rewrite chapters (Chapter 4, and Chapter 5 when a second content file is given) ----
CHAPTERS = [("CHƯƠNG 4 HUẤN LUYỆN", "CHƯƠNG 5 XÂY DỰNG", "4", content_file)]
if len(sys.argv) > 3:
    CHAPTERS.append(("CHƯƠNG 5 XÂY DỰNG", "TÀI LIỆU THAM KHẢO", "5", sys.argv[3]))
chapter = ["4"]
content: list = []
new_refs: list[str] = []
H2 = lambda s: content.append(heading(h2_tpl, s))  # noqa: E731
H3 = lambda s: content.append(heading(h3_tpl, s))  # noqa: E731
P = lambda s: content.append(para(s))  # noqa: E731
N = lambda s: content.append(note(s))  # noqa: E731


def CODE(s):
    """Monospace block, 11 pt, left aligned, one paragraph per line."""
    for line in s.split("\n"):
        p = para("")
        rpr = copy.deepcopy(run_rpr)
        fonts = rpr.find("w:rFonts", NS)
        if fonts is None:
            fonts = etree.Element(q("rFonts"))
            rpr.insert(0, fonts)
        for attr in ["ascii", "hAnsi", "cs"]:
            fonts.set(q(attr), "Consolas")
        for tag in ["sz", "szCs"]:
            el = rpr.find(f"w:{tag}", NS)
            if el is None:
                el = etree.SubElement(rpr, q(tag))
            el.set(q("val"), "21")
        p.append(make_run(line or " ", rpr=rpr))
        pPr = p.find("w:pPr", NS)
        sp = pPr.find("w:spacing", NS)
        if sp is None:
            sp = etree.SubElement(pPr, q("spacing"))
        sp.attrib.update(
            {q("before"): "0", q("after"): "0", q("line"): "240", q("lineRule"): "auto"}
        )
        jc = pPr.find("w:jc", NS)
        if jc is None:
            jc = etree.SubElement(pPr, q("jc"))
        jc.set(q("val"), "left")
        ind = pPr.find("w:ind", NS)
        if ind is None:
            ind = etree.SubElement(pPr, q("ind"))
        ind.attrib.update({q("firstLine"): "0", q("left"): "284"})
        content.append(p)


def T(title, widths, header, rows, source, align=None):
    content.append(caption(cap_tpl, f"Bảng {chapter[0]}.", "Bang", title))
    content.append(table(widths, header, rows, align))
    N("Nguồn: " + source)


def F(png, title, source, width_cm=15.5):
    number = f"Hình {chapter[0]}.{counters['Hinh'] + 1} {title}"
    content.append(picture(Path(png), width_cm, number))
    content.append(caption(fig_cap_tpl, f"Hình {chapter[0]}.", "Hinh", title))
    N("Nguồn: " + source)


for start_text, end_text, number, source_file in CHAPTERS:
    kids = list(body)
    start = kids.index(find_para(start_text))
    end = kids.index(find_para(end_text))
    for e in kids[start + 1 : end]:
        body.remove(e)
    anchor = kids[start]
    chapter[0] = number
    counters.update({"Bang": 0, "Hinh": 0})
    content = []
    scope = {**globals(), "content": content}
    exec(open(source_file, encoding="utf-8").read(), scope)
    new_refs.extend(scope.get("REFS", []))
    for e in content:
        anchor.addnext(e)
        anchor = e

# ---- 3. New references after [30] ----
ref_tpl = strip_ids(copy.deepcopy(find_para("[30] Frederickson")))
anchor = find_para("[30] Frederickson")
for s in new_refs:
    p = fill(copy.deepcopy(ref_tpl), s, rpr=copy.deepcopy(ref_tpl.find("w:r/w:rPr", NS)))
    anchor.addnext(p)
    anchor = p

# ---- 4. Edits outside the rewritten chapters (optional fourth argument) ----
if len(sys.argv) > 4:
    exec(open(sys.argv[4], encoding="utf-8").read(), globals())

tree.write(str(doc_path), xml_declaration=True, encoding="UTF-8", standalone=True)
rels.write(str(rels_path), xml_declaration=True, encoding="UTF-8", standalone=True)
print("ok: tables", counters["Bang"], "figures", counters["Hinh"])
