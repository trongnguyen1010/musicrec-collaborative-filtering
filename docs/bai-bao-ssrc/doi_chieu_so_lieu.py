# ruff: noqa: E501
"""Check every number of Tables II-VI (and key numbers of the text) of the SSRC paper.

The expected value is read from the same result files that build report v23 and rounded as the
paper rounds it (ranking metrics and differences 4 decimals, ARP 2, coverage % 2, r_rb and p 3).
Usage (repository root): python -X utf8 docs/bai-bao-ssrc/doi_chieu_so_lieu.py <paper.docx>
Prints one line per checked number and exits with status 1 if any number differs.
"""

import json
import re
import sys
import zipfile

import pandas as pd

D = "docs/results/chinh_thuc_cloud_20261026/"
B2 = D + "bo_sung_2/"


def load(p):
    return json.loads(open(p, encoding="utf-8").read())


def vn(x, d=4):
    s = f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s.replace("-", "−")


def pv(p):
    if p < 1e-10:
        return "< 10−10"
    if p < 0.001:
        return "< 0,001"
    return vn(p, 3)


test = pd.read_csv(D + "test/metrics.csv")
test = test[(test.seed == 42) & (test.k == 10)].set_index("model")
st = load(B2 + "thong_ke/kiem_dinh_bo_sung.json")
means = st["mean_ndcg10_bootstrap_ci"]
pre = {(r["a"], r["b"]): r for r in st["predeclared_pairs_recomputed"]}
fam = {r["b"]: r for r in st["supplementary_family_pure_svd_vs_others_holm"]}
e7 = pd.read_csv(B2 + "e7/metrics.csv")
e7 = e7[e7.k == 10].set_index("model")
e7s = load(B2 + "e7/statistics_ndcg_at_10.json")
e7p = {(r["a"], r["b"]): r for r in e7s["pairs"]}
e7ci = e7s["mean_ndcg10_ci"]
var = pd.read_csv(D + "bo_sung/m1_bien_the_test.csv").set_index("bien_the")
m2 = pd.read_csv(D + "m2/test/metrics.csv")
m2 = m2[m2.k == 10]
eg = pd.read_csv(B2 + "eg/metrics.csv")
eg = eg[eg.k == 10]

exp = {}  # label -> expected text
for m, lab in [
    ("random", "Random"),
    ("popularity", "Popularity"),
    ("user_cf", "UserCF"),
    ("item_cf", "ItemCF"),
    ("svd", "SVD có độ lệch"),
    ("pure_svd", "PureSVD"),
    ("m1", "M1"),
    ("implicit_als", "Implicit ALS"),
]:
    r, c = test.loc[m], means[m]
    exp[f"III {lab}"] = [
        vn(r.recall),
        f"{vn(r.ndcg)}[{vn(c['ci95_low'])}; {vn(c['ci95_high'])}]",
        vn(100 * r.catalog_coverage, 2),
        vn(r.arp, 2),
        vn(r.ild, 4),
    ]
for m, lab in [("user_cf", "UserCF top-N"), ("item_cf", "ItemCF top-N")]:
    r, c = e7.loc[m], e7ci[m]
    exp[f"III {lab}"] = [
        vn(r.recall),
        f"{vn(r.ndcg)}[{vn(c['ci95_low'])}; {vn(c['ci95_high'])}]",
        vn(100 * r.catalog_coverage, 2),
        vn(r.arp, 2),
        vn(r.ild, 4),
    ]


def pair(r):
    return [
        vn(r["mean_difference"]),
        f"[{vn(r['ci95_low'])}; {vn(r['ci95_high'])}]",
        vn(r["rank_biserial"], 3),
        pv(r["holm_p"]),
    ]


exp["IV PureSVD − Popularity"] = pair(pre[("pure_svd", "popularity")])
exp["IV SVD có độ lệch − PureSVD"] = pair(pre[("svd", "pure_svd")])
exp["IV M1 − PureSVD"] = pair(pre[("m1", "pure_svd")])
exp["IV ALS − PureSVD"] = pair(pre[("implicit_als", "pure_svd")])
exp["IV PureSVD − UserCF"] = pair(fam["user_cf"])
exp["IV PureSVD − ItemCF"] = pair(fam["item_cf"])
exp["IV PureSVD − Random"] = pair(fam["random"])
exp["IV UserCF top-N − Popularity"] = pair(e7p[("user_cf_e7", "Popularity")])
exp["IV UserCF top-N − PureSVD"] = pair(e7p[("user_cf_e7", "PureSVD")])
exp["IV ItemCF top-N − Popularity"] = pair(e7p[("item_cf_e7", "Popularity")])
exp["IV ItemCF top-N − PureSVD"] = pair(e7p[("item_cf_e7", "PureSVD")])
base = var.loc["nen"]
for key, lab in [
    ("nen", "Nền (1; 0)"),
    ("chi_da_dang", "Chỉ đa dạng (0,75; 0)"),
    ("chi_phat_pho_bien", "Chỉ phạt phổ biến (1; 0,5)"),
    ("m1_day_du", "M1 đầy đủ (0,75; 0,5)"),
]:
    v = var.loc[key]
    d = (v.ndcg / base.ndcg - 1) * 100
    exp[f"V {lab}"] = [
        vn(v.ndcg),
        "0" if key == "nen" else ("+" if d > 0 else "") + vn(d, 2),
        vn(v.arp, 2),
        vn(100 * v.catalog_coverage, 2),
        vn(v.ild, 4),
        vn(v.ild_tag, 4),
    ]
for tab, frame in [("VI khóa", m2), ("VI (5)", eg)]:
    for meth, lab in [
        ("popularity", "Popularity"),
        ("item_cf", "Chỉ ItemCF"),
        ("content", "Chỉ nội dung thẻ"),
        ("m2", "M2"),
    ]:
        exp[f"{tab} {lab}"] = [
            vn(float(frame[(frame.method == meth) & (frame.n == n)].ndcg.iloc[0]))
            for n in [0, 1, 3, 5]
        ]

# ---- read the paper tables
x = zipfile.ZipFile(sys.argv[1]).read("word/document.xml").decode("utf-8")
tables = re.findall(r"<w:tbl>.*?</w:tbl>", x, flags=re.S)


def rows(tb):
    out = []
    for tr in re.findall(r"<w:tr[ >].*?</w:tr>", tb, flags=re.S):
        cells = []
        for tc in re.findall(r"<w:tc>.*?</w:tc>", tr, flags=re.S):
            t = "".join(re.findall(r"<(?:w|m):t[^>]*>([^<]*)</(?:w|m):t>", tc))
            cells.append(t.replace("&lt;", "<").replace("&amp;", "&").strip())
        out.append(cells)
    return out


found = {}
for tb in tables:
    rs = rows(tb)
    head = " ".join(rs[0]) if rs else ""
    if "R@10" in head:
        tag = "III"
    elif "rrb" in head or "p Holm" in head:
        tag = "IV"
    elif "ILD thẻ" in head:
        tag = "V"
    elif "N = 0" in head:
        tag = "VI"
    else:
        continue
    section = "khóa"
    for r in rs[1:]:
        if tag == "VI" and len(r) == 1:
            section = "(5)" if "(5)" in r[0] else "khóa"
            continue
        if len(r) < 2:
            continue
        key = f"{tag} {section} {r[0]}" if tag == "VI" else f"{tag} {r[0]}"
        key = re.sub(r"\s+", " ", key)
        found[key] = r[1:]

bad = 0
for key, want in exp.items():
    got = found.get(key)
    ok = got == want
    bad += not ok
    print("OK " if ok else "DIFF", key, "| bài:", got, "| tệp:", want if not ok else "")
for key in found:
    if key not in exp:
        print("NOT CHECKED", key, found[key])
print("checked", len(exp), "differences", bad)
sys.exit(1 if bad else 0)
