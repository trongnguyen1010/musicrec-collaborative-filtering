# Rebuild report v18 from the advisor's copy, then refresh Word fields and export a check PDF.
# Run from the repository root:  powershell -File docs/bao-cao/nguon_v17/dung_v18.ps1 -Pdf <check.pdf>
# Needs system Python with lxml (the project .venv has no lxml) and Microsoft Word.
param([string]$Pdf = "$env:TEMP\v18_check.pdf")
$ErrorActionPreference = "Stop"
$src = "docs\bao-cao\GopY_GVHD_06-11-2026_KLTN_TrongNguyen_GiaKhang.docx"
$out = (Resolve-Path ".").Path + "\docs\bao-cao\33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_v18_07-11-2026.docx"
$work = Join-Path $env:TEMP "musicrec_v18_build"
if (Test-Path $work) { Remove-Item -Recurse -Force $work }
python -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" $src $work
$env:PYTHONIOENCODING = "utf-8"
python -X utf8 docs/bao-cao/nguon_v17/build_v17.py $work docs/bao-cao/nguon_v17/ch4_v17.py docs/bao-cao/nguon_v17/ch5_v18.py docs/bao-cao/nguon_v17/edits_v18.py
python -X utf8 docs/bao-cao/nguon_v17/dong_goi.py $work $src $out
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
$d = $w.Documents.Open($out, $false, $false)
$d.Fields.Update() | Out-Null
foreach ($t in $d.TablesOfContents) { $t.Update() | Out-Null }
foreach ($t in $d.TablesOfFigures) { $t.Update() | Out-Null }
$d.Fields.Update() | Out-Null
$d.Save()
$d.ExportAsFixedFormat($Pdf, 17)
"pages: " + $d.ComputeStatistics(2)
$d.Close()
try { $w.Quit() } catch { "Word quit skipped" }
