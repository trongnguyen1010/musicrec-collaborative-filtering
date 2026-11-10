# Rebuild report v19 from the advisor's annotated copy, then refresh Word fields and export a
# check PDF. Run from the repository root:
#   powershell -ExecutionPolicy Bypass -File docs/bao-cao/nguon_v19/dung_v19.ps1 -Src <advisor docx> -Pdf <check.pdf>
# Needs system Python with lxml and pandas, and Microsoft Word.
param(
    [string]$Src = "docs\bao-cao\GopY_GVHD_10-11-2026_KLTN_TrongNguyen_GiaKhang.docx",
    [string]$Pdf = "$env:TEMP\v19_check.pdf",
    [string]$Out = ""
)
$ErrorActionPreference = "Stop"
$out = if ($Out) { $Out } else { (Resolve-Path ".").Path + "\docs\bao-cao\33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_v19_10-11-2026.docx" }
$work = Join-Path $env:TEMP "musicrec_v19_build"
if (Test-Path $work) { Remove-Item -Recurse -Force $work }
python -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" $Src $work
$env:PYTHONIOENCODING = "utf-8"
$n = "docs/bao-cao/nguon_v19"
python -X utf8 "$n/build_v19.py" $work "$n/ch2_v19.py" "$n/ch3_v19.py" "$n/ch4_v19.py" "$n/edits_v19.py"
if ($LASTEXITCODE -ne 0) { throw "build failed" }
python -X utf8 docs/bao-cao/nguon_v17/dong_goi.py $work $Src $out
if ($LASTEXITCODE -ne 0) { throw "packing failed" }
powershell -ExecutionPolicy Bypass -File "$n/post_v19.ps1" -Docx $out -Pdf $Pdf
