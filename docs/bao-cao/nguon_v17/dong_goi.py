"""Zip an unpacked docx back, keeping the part order of the original file first."""

import os
import sys
import zipfile

src, original, dst = sys.argv[1], sys.argv[2], sys.argv[3]
names = [i.filename for i in zipfile.ZipFile(original).infolist()]
files = [
    os.path.relpath(os.path.join(root, f), src).replace(os.sep, "/")
    for root, _, fs in os.walk(src)
    for f in fs
]
order = [n for n in names if n in files] + [n for n in files if n not in names]
with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
    for name in order:
        z.write(os.path.join(src, name), name)
print("packed", len(order), "parts")
