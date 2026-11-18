# Post-process report v22 in Microsoft Word: refresh fields, table of contents and lists of
# figures/tables, then drop the page numbers of appendix entries (the appendix pages carry no
# number, as in the faculty template), save, and export a check PDF.
# Usage: powershell -File docs/bao-cao/nguon_v22/post_v22.ps1 -Docx <full path> -Pdf <full path>
# Note: updating the table of contents again in Word brings these page numbers back; run this
# script instead.
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
$appendix = '^(PHỤ LỤC [A-D]|[A-D]\.[0-9]|Bảng [A-D]\.|Hình [A-D]\.)'
$dropped = 0
$lists = @($d.TablesOfContents) + @($d.TablesOfFigures)
foreach ($t in $lists) {
    foreach ($p in $t.Range.Paragraphs) {
        $txt = $p.Range.Text.Trim()
        if ($txt -notmatch $appendix) { continue }
        $refs = @($p.Range.Fields | Where-Object { $_.Type -eq 37 })
        if ($refs.Count -eq 0) { continue }
        foreach ($f in $refs) { $f.Delete(); $dropped++ }
        # remove the last tab of the entry (the dotted leader that led to the page number)
        $last = -1
        $text = $p.Range.Text
        for ($i = $text.Length - 1; $i -ge 0; $i--) { if ($text[$i] -eq "`t") { $last = $i; break } }
        if ($last -ge 0) {
            $find = $p.Range.Duplicate
            $pos = -1
            $find.Find.ClearFormatting()
            while ($find.Find.Execute("^t")) {
                if ($find.End -gt $p.Range.End) { break }
                $pos = $find.Start
                $find.Collapse(0)
            }
            if ($pos -ge 0) { $d.Range($pos, $pos + 1).Delete() | Out-Null }
        }
    }
}
"appendix page numbers dropped: " + $dropped
$d.Save()
$d.ExportAsFixedFormat($Pdf, 17)
"pages: " + $d.ComputeStatistics(2)
"equations: " + $d.OMaths.Count
$d.Close()
try { $w.Quit() } catch { "Word quit skipped" }
