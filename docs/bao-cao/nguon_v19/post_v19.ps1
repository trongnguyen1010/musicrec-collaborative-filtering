# Post-process report v19 in Microsoft Word: refresh fields, table of contents and lists of
# figures/tables, save, and export a check PDF outside the hand-over folder. Inline maths is
# already OMML (build_v19.py).
# Usage: powershell -File docs/bao-cao/nguon_v19/post_v19.ps1 -Docx <full path> -Pdf <full path>
param([string]$Docx, [string]$Pdf)
$ErrorActionPreference = "Stop"
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
$d = $w.Documents.Open($Docx, $false, $false)
$d.Fields.Update() | Out-Null
foreach ($t in $d.TablesOfContents) { $t.Update() | Out-Null }
foreach ($t in $d.TablesOfFigures) { $t.Update() | Out-Null }
$d.Fields.Update() | Out-Null
$d.Save()
$d.ExportAsFixedFormat($Pdf, 17)
"pages: " + $d.ComputeStatistics(2)
"equations: " + $d.OMaths.Count
$d.Close()
try { $w.Quit() } catch { "Word quit skipped" }
