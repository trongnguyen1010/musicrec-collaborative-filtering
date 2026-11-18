# ruff: noqa: E501, F821
# Edits for report v23 (advisor feedback of 18/11/2026), run by build_v19.py after edits_v20.py.
# Content changes of v23 are made in place in nguon_v19/ch3_v19.py, ch4_v19.py and
# nguon_v20/edits_v20.py (as for v22); this script only fixes what those scripts cannot reach:
# - Section 3.4.1 cites "Bảng 3.5" for the data files table, which is Table 3.3 (edits_v19.py
#   renumbers "Bảng 3.3" from the table-of-contents entry of Chapter 5 on, which also catches
#   this sentence of Chapter 3);
# - the alternative text of every captioned figure becomes its caption title (pictures kept from
#   the advisor's copy still carried old numbers such as "Hình 3.2 Kiến trúc…");
# - the front matter (roman-numbered section) has no page number, as in the faculty template
#   (same change the group made by hand in the saved v22 file on 11/11/2026).
import re as _re

WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
PIC_NS = "http://schemas.openxmlformats.org/drawingml/2006/picture"

# ---- 3.4.1: Table 3.3
hits = [
    e
    for e in body
    if e.tag == q("p") and "Bảng 3.5 trình bày các thành phần được xem xét" in text(e)
]
assert len(hits) == 1, len(hits)
n_fixed = 0
for t in hits[0].iter(q("t")):
    if t.text and "Bảng 3.5 trình bày các thành phần" in t.text:
        t.text = t.text.replace("Bảng 3.5 trình bày", "Bảng 3.3 trình bày")
        n_fixed += 1
assert n_fixed == 1

# ---- alternative text = caption title
elements = list(body)
alt_fixed = []
for i, e in enumerate(elements[:-1]):
    if e.tag != q("p") or e.find(f".//{{{WP_NS}}}docPr") is None:
        continue
    cap = text(elements[i + 1]).strip()
    m = _re.match(r"Hình (\d+|[A-D])\.\s*\d+\s+(.*)", cap)
    if not m:
        continue
    title = m.group(2).strip()
    for el in list(e.iter(f"{{{WP_NS}}}docPr")) + list(e.iter(f"{{{PIC_NS}}}cNvPr")):
        old = el.get("descr") or ""
        # Only alternative texts that still carry a figure number; others (for instance the
        # "Nguồn: …" notes of Chapter 2) are kept.
        if _re.match(r"Hình \d", old) and old != title:
            alt_fixed.append((old, title))
            el.set("descr", title)
            el.set("name", title)
print("v23: alt texts changed", len(alt_fixed))
for old, new in alt_fixed:
    print("   ", old, "->", new)

# ---- front matter footer without page number
rels_xml = (root_dir / "word/_rels/document.xml.rels").read_text(encoding="utf-8")
roman = [
    sp
    for sp in body.iter(q("sectPr"))
    if sp.find(q("pgNumType")) is not None and sp.find(q("pgNumType")).get(q("fmt")) == "lowerRoman"
]
assert len(roman) == 1, len(roman)
ref = roman[0].find(q("footerReference"))
rid = ref.get(f"{{{R}}}id")
target = _re.search(rf'Id="{rid}"[^>]*Target="([^"]+)"', rels_xml) or _re.search(
    rf'Target="([^"]+)"[^>]*Id="{rid}"', rels_xml
)
footer_path = root_dir / "word" / target.group(1)
ftree = etree.parse(str(footer_path))
removed_runs = 0
for p_ in ftree.getroot().iter(q("p")):
    for r_ in list(p_):
        if r_.tag in (q("r"), q("fldSimple")):
            p_.remove(r_)
            removed_runs += 1
    jc = p_.find("w:pPr/w:jc", NS)
    if jc is not None:
        jc.getparent().remove(jc)
assert "PAGE" not in etree.tostring(ftree).decode()
ftree.write(str(footer_path), xml_declaration=True, encoding="UTF-8", standalone=True)
print("v23: front matter footer", footer_path.name, "runs removed", removed_runs)
