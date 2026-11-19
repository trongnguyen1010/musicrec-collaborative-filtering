# ruff: noqa: E501
"""Paper v3 (19/11/2026): the advisor's clean copy _v2_nop with three corrections.

Usage (from the repository root):
    python -X utf8 docs/bai-bao-ssrc/dung_bai_bao_v3.py

1. Four-decimal values rounded from the raw results, not from the six printed decimals:
   biased SVD NDCG@10 0.0626499310 -> 0,0626 (the copy has 0,0627);
   Popularity, Given-N N = 5, 0.0597495843 -> 0,0597 (the copy has 0,0598, twice).
   Sources: docs/results/chinh_thuc_cloud_20261026/test/metrics.csv (svd, seed 42, k 10) and
   docs/results/chinh_thuc_cloud_20261026/m2/test/metrics.csv (n 5, popularity, k 10).
2. The Section II paragraph heading still read "Thiên lệch phổ biến"; the advisor changed the
   term to "thiên lệch độ phổ biến" everywhere else.
"""

import zipfile
from pathlib import Path

SRC = Path("docs/bai-bao-ssrc/GopY_GVHD_19-11-2026_BaiBao_SSRC_v2_nop.docx")
DST = Path(
    "docs/bai-bao-ssrc/CaoTrongNguyen_LeKhacGiaKhang_KhuyenNghiNgheSi_BaiBao_SSRC_v3_19-11-2026.docx"
)
EDITS = [
    ("0,0627", "0,0626", 1),
    ("0,0598", "0,0597", 2),
    (
        "Thiên lệch phổ biến trong khuyến nghị âm nhạc",
        "Thiên lệch độ phổ biến trong khuyến nghị âm nhạc",
        1,
    ),
]
with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/document.xml":
            xml = data.decode("utf-8")
            for old, new, n in EDITS:
                assert xml.count(old) == n, (old, xml.count(old))
                xml = xml.replace(old, new)
            data = xml.encode("utf-8")
        zout.writestr(item, data)
print("written", DST)
