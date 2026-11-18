# ruff: noqa: E501
"""Build report v19 from the advisor's annotated copy (GopY_GVHD, 10/11/2026): Chapters 2-4.

Usage (from the repository root, after unzipping the advisor's docx into <unpacked>):
    python -X utf8 docs/bao-cao/nguon_v19/build_v19.py <unpacked> <ch2.py> <ch3.py> <ch4.py> <edits.py>

Everything between the "CHƯƠNG 2" heading and the "CHƯƠNG 5" heading is rebuilt from the three
content scripts. Those scripts can keep an original element by its body index in the advisor's
copy (KEEP), reuse an original Word equation (OMML) with a new number (EQ), or add new
paragraphs, headings, tables and figures. Formatting templates are taken from the same
document. Advisor colours (red notes are simply not kept; blue text that is kept) are turned
black. Inline maths in new text is written as ⟦UnicodeMath⟧ and built up by post_v19.ps1.
"""

import copy
import re
import shutil
import struct
import sys
from pathlib import Path

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
NS = {"w": W, "m": M, "r": R, "wp": WP, "a": A, "pic": PIC}


def q(tag, ns=W):
    return f"{{{ns}}}{tag}"


root_dir = Path(sys.argv[1])
doc_path = root_dir / "word/document.xml"
tree = etree.parse(str(doc_path))
body = tree.getroot().find("w:body", NS)
ORIG = list(body)


def text(e):
    return "".join(x.text or "" for x in e.iter(q("t"), q("t", M)))


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


def blacken(e):
    """Advisor blue/red text kept in the report becomes plain black text."""
    for c in e.iter(q("color")):
        if c.get(q("val"), "").upper() not in ("000000", "AUTO"):
            c.set(q("val"), "000000")
    for h in e.findall(".//w:highlight", NS):
        h.getparent().remove(h)
    return e


def idx(prefix, start=0):
    for i, e in enumerate(ORIG):
        if i >= start and e.tag == q("p") and text(e).startswith(prefix):
            return i
    raise KeyError(prefix)


# ---- templates (all from the advisor's copy) ----
body_tpl = strip_ids(copy.deepcopy(ORIG[396]))
h1_tpl = strip_ids(copy.deepcopy(ORIG[393]))
h2_tpl = strip_ids(copy.deepcopy(ORIG[399]))
h3_tpl = strip_ids(copy.deepcopy(ORIG[408]))
cap_tpl = strip_ids(copy.deepcopy(ORIG[690]))
tbl_tpl = copy.deepcopy(ORIG[691])
fig_cap_tpl = strip_ids(copy.deepcopy(ORIG[616]))
pic_tpl = strip_ids(copy.deepcopy(ORIG[615]))
note_tpl = strip_ids(copy.deepcopy(ORIG[809]))
eq_tpl = strip_ids(copy.deepcopy(ORIG[414]))
run_rpr = copy.deepcopy(body_tpl.find("w:r/w:rPr", NS))
if run_rpr is None:
    run_rpr = etree.Element(q("rPr"))


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


# ---- inline maths: a small UnicodeMath-like markup turned into OMML ----
ACCENTS = {"̂": "̂", "̃": "̃", "̅": "̅", "̄": "̅"}
UPRIGHT_SHORT = {"rb"}


def _mrun(s, upright=False):
    r = etree.Element(q("r", M))
    if upright:
        etree.SubElement(etree.SubElement(r, q("rPr", M)), q("sty", M)).set(q("val", M), "p")
    rpr = etree.SubElement(r, q("rPr"))
    fonts = etree.SubElement(rpr, q("rFonts"))
    fonts.set(q("ascii"), "Cambria Math")
    fonts.set(q("hAnsi"), "Cambria Math")
    t = etree.SubElement(r, q("t", M))
    t.text = s
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return r


def _group(s, i):
    """Return (content, next_index) of a balanced ( ... ) group starting at s[i] == '('."""
    depth = 0
    for j in range(i, len(s)):
        depth += {"(": 1, ")": -1}.get(s[j], 0)
        if depth == 0:
            return s[i + 1 : j], j + 1
    raise ValueError(f"unbalanced group in {s!r}")


def _script_arg(s, i):
    if s[i] == "(":
        return _group(s, i)
    j = i
    while j < len(s) and (s[j].isalnum()):
        j += 1
    if j == i:
        j = i + 1
    return s[i:j], j


def _wrap(tag, children):
    e = etree.Element(q(tag, M))
    for c in children:
        e.append(c)
    return e


def omml(s):
    """Parse the markup into a list of OMML elements (runs, sSub, sSup, sSubSup, acc)."""
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch in "_^":
            base = [out.pop()] if out else [_mrun("")]
            sub = sup = None
            while i < len(s) and s[i] in "_^":
                arg, i = _script_arg(s, i + 1)
                if ch == "_" and sub is None:
                    sub = arg
                else:
                    sup = arg
                if i < len(s):
                    ch = s[i]
            if sub is not None and sup is not None:
                el = etree.Element(q("sSubSup", M))
                el.append(_wrap("e", base))
                el.append(_wrap("sub", omml(sub)))
                el.append(_wrap("sup", omml(sup)))
            elif sub is not None:
                el = etree.Element(q("sSub", M))
                el.append(_wrap("e", base))
                el.append(_wrap("sub", omml(sub)))
            else:
                el = etree.Element(q("sSup", M))
                el.append(_wrap("e", base))
                el.append(_wrap("sup", omml(sup)))
            out.append(el)
            continue
        # accent: base char, optional space, combining mark
        nxt = s[i + 1] if i + 1 < len(s) else ""
        nxt2 = s[i + 2] if i + 2 < len(s) else ""
        mark = nxt if nxt in ACCENTS else (nxt2 if nxt == " " and nxt2 in ACCENTS else "")
        if mark:
            acc = etree.Element(q("acc", M))
            etree.SubElement(etree.SubElement(acc, q("accPr", M)), q("chr", M)).set(
                q("val", M), ACCENTS[mark]
            )
            acc.append(_wrap("e", [_mrun(ch)]))
            out.append(acc)
            i += 2 if nxt == mark else 3
            continue
        if ch.isalpha():
            j = i
            while j < len(s) and s[j].isalpha() and s[j] not in "∈∑":
                j += 1
            word = s[i:j]
            if j < len(s) and s[j] in "_^" and len(word) > 1 and len(word) < 3:
                # two-letter word followed by a script: script attaches to the last letter only
                out.append(_mrun(word[:-1]))
                out.append(_mrun(word[-1]))
            else:
                out.append(_mrun(word, upright=len(word) >= 3 or word in UPRIGHT_SHORT))
            i = j
            continue
        if ch.isdigit():
            j = i
            while j < len(s) and (
                s[j].isdigit() or (s[j] == "," and j + 1 < len(s) and s[j + 1].isdigit())
            ):
                j += 1
            out.append(_mrun(s[i:j]))
            i = j
            continue
        if ch != " ":
            out.append(_mrun("−" if ch == "-" else ch, upright=ch in "()[]{};:,|"))
        i += 1
    return out


def math_inline(s):
    m = etree.Element(q("oMath", M))
    for e in omml(s):
        m.append(e)
    return m


def fill(p, s, rpr=None):
    """Replace runs of p with s; **x** marks bold, ⟦...⟧ inline maths (URLs stay intact)."""
    for c in list(p):
        if c.tag != q("pPr"):
            p.remove(c)
    for n, seg in enumerate(re.split(r"⟦(.*?)⟧", s)):
        if n % 2 == 1:
            p.append(math_inline(seg))
            continue
        for k, part in enumerate(re.split(r"\*\*", seg)):
            if part:
                p.append(make_run(part, bold=k % 2 == 1, rpr=rpr))
    return p


content: list = []
chapter = ["2"]
counters = {"Bang": 0, "Hinh": 0}


def P(s):
    content.append(fill(copy.deepcopy(body_tpl), s))


def N(s):
    content.append(fill(copy.deepcopy(note_tpl), s, rpr=note_tpl.find("w:r/w:rPr", NS)))


def _heading(tpl, s):
    p = copy.deepcopy(tpl)
    content.append(fill(p, s, rpr=copy.deepcopy(tpl.find("w:r/w:rPr", NS))))


def H1(s):
    _heading(h1_tpl, s)


def H2(s):
    _heading(h2_tpl, s)


def H3(s):
    _heading(h3_tpl, s)


def CHAPTER(n):
    chapter[0] = str(n)
    counters.update({"Bang": 0, "Hinh": 0})


def KEEP(i, subs=()):
    """Copy an original body element; subs are (old, new) replaced inside single text nodes."""
    e = blacken(strip_ids(copy.deepcopy(ORIG[i])))
    for old, new in subs:
        hits = [t for t in e.iter(q("t")) if t.text and old in t.text]
        if not hits:
            raise KeyError(f"KEEP({i}): '{old}' not found in one text node")
        for t in hits:
            t.text = t.text.replace(old, new)
    content.append(e)
    return e


def EQ(i, number):
    """Display equation: original OMML of element i, numbered (number) at the right tab."""
    maths = ORIG[i].findall(".//m:oMath", NS)
    if not maths:
        raise KeyError(f"EQ({i}): no equation")
    p = etree.Element(q("p"))
    p.append(copy.deepcopy(eq_tpl.find("w:pPr", NS)))
    tab = etree.SubElement(etree.SubElement(p, q("r")), q("tab"))
    del tab
    for m in maths:
        p.append(blacken(copy.deepcopy(m)))
    etree.SubElement(etree.SubElement(p, q("r")), q("tab"))
    num = copy.deepcopy(eq_tpl.findall("w:r", NS)[-1])
    num.find("w:t", NS).text = f"({number})"
    p.append(num)
    content.append(strip_ids(p))


def _caption(tpl, prefix, kind, title):
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


def TCAP(title):
    content.append(_caption(cap_tpl, f"Bảng {chapter[0]}.", "Bang", title))
    return f"{chapter[0]}.{counters['Bang']}"


def FCAP(title):
    content.append(_caption(fig_cap_tpl, f"Hình {chapter[0]}.", "Hinh", title))
    return f"{chapter[0]}.{counters['Hinh']}"


def table(widths, header, rows, align=None, size=None):
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
            for extra in tc.findall("w:p", NS)[1:]:
                tc.remove(extra)
            p = strip_ids(tc.find("w:p", NS))
            ppr = p.find("w:pPr", NS)
            jc = ppr.find("w:jc", NS)
            if jc is None:
                jc = etree.SubElement(ppr, q("jc"))
            jc.set(q("val"), "center" if bold else al)
            rpr = copy.deepcopy(p.find("w:r/w:rPr", NS))
            if rpr is None:
                rpr = etree.Element(q("rPr"))
            for b in rpr.findall("w:b", NS):
                rpr.remove(b)
            if bold:
                rpr.insert(0, etree.Element(q("b")))
            if size:
                for tag in ["sz", "szCs"]:
                    el = rpr.find(f"w:{tag}", NS)
                    if el is None:
                        el = etree.SubElement(rpr, q(tag))
                    el.set(q("val"), str(size))
            fill(p, val if val else " ", rpr=blacken(rpr))
            tr.append(tc)
        return strip_ids(tr)

    tb.append(build(head_tr, header, True))
    for row in rows:
        tb.append(build(body_tr, row, False))
    return blacken(tb)


def T(title, widths, header, rows, note=None, align=None, size=None):
    number = TCAP(title)
    content.append(table(widths, header, rows, align, size))
    if note:
        N(note)
    return number


# ---- pictures ----
rels_path = root_dir / "word/_rels/document.xml.rels"
rels = etree.parse(str(rels_path))
rid_numbers = [int(r.get("Id")[3:]) for r in rels.getroot() if r.get("Id", "").startswith("rId")]
next_rid = [max(rid_numbers) + 1]
doc_pr_ids = [int(e.get("id")) for e in tree.getroot().iter(q("docPr", WP))]
next_pr = [max(doc_pr_ids) + 1]


def picture(png, width_cm, title):
    data = Path(png).read_bytes()
    w_px, h_px = struct.unpack(">II", data[16:24])
    cx = int(width_cm * 360000)
    cy = int(cx * h_px / w_px)
    name = f"v19_{next_rid[0]}.png"
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


def F(png, title, note=None, width_cm=15.5):
    content.append(picture(png, width_cm, title))
    number = FCAP(title)
    if note:
        N(note)
    return number


def FKEEP(i, title, note=None):
    """Keep an original picture paragraph and give it a new automatic caption."""
    KEEP(i)
    number = FCAP(title)
    if note:
        N(note)
    return number


# ---- rebuild Chapters 2-4 ----
start = idx("CHƯƠNG 2 CƠ SỞ LÝ THUYẾT", 300)
end = idx("CHƯƠNG 5 XÂY DỰNG", start)
anchor = ORIG[start - 1]
for e in ORIG[start:end]:
    body.remove(e)
scope = globals()
for script in sys.argv[2:5]:
    exec(open(script, encoding="utf-8").read(), scope)
for e in content:
    anchor.addnext(e)
    anchor = e

# ---- edits outside Chapters 2-4 ----
for edits in sys.argv[5:]:
    exec(open(edits, encoding="utf-8").read(), scope)

tree.write(str(doc_path), xml_declaration=True, encoding="UTF-8", standalone=True)
rels.write(str(rels_path), xml_declaration=True, encoding="UTF-8", standalone=True)
print("ok: elements", len(content))
