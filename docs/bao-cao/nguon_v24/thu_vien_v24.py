# ruff: noqa: E501
"""Helpers for report v24: edit the advisor's annotated copy of 19/11/2026 in place (lxml).

The inline-maths markup (⟦...⟧ turned into OMML) is the one of nguon_v19/build_v19.py.
"""

import copy
import re
from decimal import ROUND_HALF_UP, Decimal

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W, "m": M}
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def q(tag, ns=W):
    return f"{{{ns}}}{tag}"


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
    """Advisor blue/red colour becomes black; bold of the 'Gợi ý viết lại' label is not kept here."""
    for c in e.iter(q("color")):
        if c.get(q("val"), "").upper() not in ("000000", "AUTO"):
            c.set(q("val"), "000000")
    for h in e.findall(".//w:highlight", NS):
        h.getparent().remove(h)
    return e


def colours(e):
    return {c.get(q("val"), "").upper() for c in e.iter(q("color"))}


def make_run(s, rpr=None, bold=False, sub=False, italic=False):
    r = etree.Element(q("r"))
    p = copy.deepcopy(rpr) if rpr is not None else etree.Element(q("rPr"))
    for b in (
        p.findall("w:b", NS)
        + p.findall("w:bCs", NS)
        + p.findall("w:i", NS)
        + p.findall("w:iCs", NS)
    ):
        p.remove(b)
    if italic:
        p.insert(0, etree.Element(q("i")))
    if bold:
        p.insert(0, etree.Element(q("b")))
    if sub:
        etree.SubElement(p, q("vertAlign")).set(q("val"), "subscript")
    r.append(p)
    t = etree.SubElement(r, q("t"))
    t.text = s
    t.set(XML_SPACE, "preserve")
    return r


# ---- inline maths (same markup as nguon_v19/build_v19.py) ----
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
    t.set(XML_SPACE, "preserve")
    return r


def _group(s, i):
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
    while j < len(s) and s[j].isalnum():
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
            if j < len(s) and s[j] in "_^" and 1 < len(word) < 3:
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
            r = _mrun(s[i:j])
            nor_number(r)
            out.append(r)
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


def nor_number(mr):
    """Mark a maths run as normal text so Word keeps '0,5' tight (no space after the comma)."""
    rpr = mr.find("m:rPr", NS)
    if rpr is None:
        rpr = etree.Element(q("rPr", M))
        mr.insert(0, rpr)
    if rpr.find("m:nor", NS) is None:
        rpr.append(etree.Element(q("nor", M)))


def fill(p, s, rpr=None):
    """Replace the runs of p with s: **x** bold, §x§ italic, ⟦...⟧ inline maths, x_{y} subscript."""
    for c in list(p):
        if c.tag != q("pPr"):
            p.remove(c)
    for n, seg in enumerate(re.split(r"⟦(.*?)⟧", s)):
        if n % 2 == 1:
            p.append(math_inline(seg))
            continue
        for k, part in enumerate(re.split(r"\*\*", seg)):
            for j, ipart in enumerate(part.split("§")):
                for m, piece in enumerate(re.split(r"_\{(.*?)\}", ipart)):
                    if piece:
                        p.append(
                            make_run(
                                piece, rpr=rpr, bold=k % 2 == 1, sub=m % 2 == 1, italic=j % 2 == 1
                            )
                        )
    return p


def first_rpr(p):
    r = p.find(".//w:r/w:rPr", NS)
    return blacken(copy.deepcopy(r)) if r is not None else etree.Element(q("rPr"))


def new_para(tpl, s):
    """New paragraph with the paragraph and run properties of tpl."""
    p = strip_ids(copy.deepcopy(tpl))
    rpr = first_rpr(tpl)
    return fill(p, s, rpr)


def set_text(p, s):
    """Keep p's paragraph properties, replace its content."""
    return fill(p, s, first_rpr(p))


# ---- text replacement across runs (w:t outside maths) ----
def _wtexts(p):
    return [t for t in p.iter(q("t")) if not any(a.tag == q("oMath", M) for a in t.iterancestors())]


def replace_span(p, pos, end, new):
    """Replace characters [pos, end) of the visible text of p (w:t outside maths) by new."""
    acc = 0
    first = True
    for t in _wtexts(p):
        s = t.text or ""
        a, b = acc, acc + len(s)
        acc = b
        if b <= pos or a >= end:
            continue
        lo, hi = max(pos, a) - a, min(end, b) - a
        t.text = s[:lo] + (new if first else "") + s[hi:]
        t.set(XML_SPACE, "preserve")
        first = False


def visible(p):
    return "".join(t.text or "" for t in _wtexts(p))


def preplace(p, old, new, count=None):
    """Replace old by new in the visible text of p, even across runs, scanning left to right."""
    hits = 0
    start = 0
    while count is None or hits < count:
        full = visible(p)
        pos = full.find(old, start)
        if pos < 0:
            break
        replace_span(p, pos, pos + len(old), new)
        start = pos + len(new)
        hits += 1
    return hits


def paragraphs(e):
    if e.tag == q("p"):
        return [e]
    return list(e.iter(q("p")))


# ---- rounding to four decimals ----
NUM = re.compile(r"(?<![\d,.])([−-]?)(\d+),(\d{5,})(?!\d|,\d)")
SKIP_BEFORE = re.compile(r"(η|λreg|λ_reg|reg)\s*=?\s*$")


def round4(sign, whole, frac, overrides):
    key = f"{whole},{frac}"
    if key in overrides:
        return sign + overrides[key]
    rest = frac[4:]
    if rest.rstrip("0") == "5":
        raise ValueError(f"tie when rounding {sign}{key}: give the raw value in overrides")
    v = Decimal(f"{whole}.{frac}").quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    out = f"{v:.4f}".replace(".", ",")
    if out == "0,0000" and Decimal(f"{whole}.{frac}") != 0:
        raise ValueError(f"{sign}{key} rounds to zero: give a value in overrides")
    return sign + out


def round_string(s, overrides, log):
    out = []
    last = 0
    for m in NUM.finditer(s):
        if SKIP_BEFORE.search(s[max(0, m.start() - 12) : m.start()]):
            continue
        new = round4(m.group(1), m.group(2), m.group(3), overrides)
        out.append(s[last : m.start()])
        out.append(new)
        log.append((m.group(0), new))
        last = m.end()
    out.append(s[last:])
    return "".join(out)


def round_paragraph(p, overrides, log):
    nodes = _wtexts(p)
    full = "".join(t.text or "" for t in nodes)
    matches = [
        m
        for m in NUM.finditer(full)
        if not SKIP_BEFORE.search(full[max(0, m.start() - 12) : m.start()])
    ]
    for m in reversed(matches):
        new = round4(m.group(1), m.group(2), m.group(3), overrides)
        log.append((m.group(0), new))
        pos, end = m.start(), m.end()
        acc = 0
        first = True
        spans = []
        for t in nodes:
            s = t.text or ""
            spans.append((t, acc, acc + len(s)))
            acc += len(s)
        for t, a, b in spans:
            if b <= pos or a >= end:
                continue
            s = t.text or ""
            lo, hi = max(pos, a) - a, min(end, b) - a
            t.text = s[:lo] + (new if first else "") + s[hi:]
            t.set(XML_SPACE, "preserve")
            first = False
    for mt in p.iter(q("t", M)):
        if mt.text and NUM.search(mt.text):
            mt.text = round_string(mt.text, overrides, log)
