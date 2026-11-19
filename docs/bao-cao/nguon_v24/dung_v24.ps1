# Build report v24 (advisor feedback of 19/11/2026) from the advisor's annotated copy of v23:
# nguon_v24/sua_v24.py edits the copy in place, then post_v24.ps1 refreshes Word fields, the
# table of contents and the lists of figures/tables, and exports a check PDF. Run from the
# repository root:
#   powershell -ExecutionPolicy Bypass -File docs/bao-cao/nguon_v24/dung_v24.ps1 -Pdf <check.pdf>
# Needs system Python with lxml, and Microsoft Word.
param(
    [string]$Src = "docs\bao-cao\GopY_GVHD_19-11-2026_KLTN_TrongNguyen_GiaKhang.docx",
    [string]$Pdf = "$env:TEMP\v24_check.pdf",
    [string]$Out = ""
)
$ErrorActionPreference = "Stop"
$out = if ($Out) { $Out } else { (Resolve-Path ".").Path + "\docs\bao-cao\33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_v24_19-11-2026.docx" }
$work = Join-Path $env:TEMP "musicrec_v24_build"
if (Test-Path $work) { Remove-Item -Recurse -Force $work }
python -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" $Src $work
$env:PYTHONIOENCODING = "utf-8"
python -X utf8 docs/bao-cao/nguon_v24/sua_v24.py $work
if ($LASTEXITCODE -ne 0) { throw "edit failed" }
python -X utf8 docs/bao-cao/nguon_v17/dong_goi.py $work $Src $out
if ($LASTEXITCODE -ne 0) { throw "packing failed" }
powershell -ExecutionPolicy Bypass -File "docs/bao-cao/nguon_v24/post_v24.ps1" -Docx $out -Pdf $Pdf
