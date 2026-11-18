# Rebuild report v23 (advisor feedback of 18/11/2026 on top of v22) from the advisor's annotated copy
# of 10/11/2026, then refresh Word fields and export a check PDF. Chapters 2-4 come from nguon_v19,
# the rest from nguon_v20 (v23 content edits are made in place there, as for v22), and
# nguon_v23/edits_v23.py runs last. Run from the repository root:
#   powershell -ExecutionPolicy Bypass -File docs/bao-cao/nguon_v23/dung_v23.ps1 -Pdf <check.pdf>
# Needs system Python with lxml, pandas and matplotlib, and Microsoft Word.
param(
    [string]$Src = "docs\bao-cao\GopY_GVHD_10-11-2026_KLTN_TrongNguyen_GiaKhang.docx",
    [string]$Pdf = "$env:TEMP\v23_check.pdf",
    [string]$Out = ""
)
$ErrorActionPreference = "Stop"
$out = if ($Out) { $Out } else { (Resolve-Path ".").Path + "\docs\bao-cao\33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_v23_18-11-2026.docx" }
$work = Join-Path $env:TEMP "musicrec_v23_build"
if (Test-Path $work) { Remove-Item -Recurse -Force $work }
python -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" $Src $work
$env:PYTHONIOENCODING = "utf-8"
python -X utf8 docs/bao-cao/nguon_v23/ve_hinh_v23.py docs/results/chinh_thuc_cloud_20261026/bo_sung_2/hinh_bao_cao
if ($LASTEXITCODE -ne 0) { throw "figure failed" }
$n = "docs/bao-cao/nguon_v19"
python -X utf8 "$n/build_v19.py" $work "$n/ch2_v19.py" "$n/ch3_v19.py" "$n/ch4_v19.py" "$n/edits_v19.py" "docs/bao-cao/nguon_v20/edits_v20.py" "docs/bao-cao/nguon_v23/edits_v23.py"
if ($LASTEXITCODE -ne 0) { throw "build failed" }
python -X utf8 docs/bao-cao/nguon_v17/dong_goi.py $work $Src $out
if ($LASTEXITCODE -ne 0) { throw "packing failed" }
powershell -ExecutionPolicy Bypass -File "docs/bao-cao/nguon_v23/post_v23.ps1" -Docx $out -Pdf $Pdf
