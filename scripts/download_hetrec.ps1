param([Parameter(Mandatory = $true)][string]$Destination)
$ErrorActionPreference = 'Stop'
$target = [System.IO.Path]::GetFullPath($Destination)
New-Item -ItemType Directory -Force (Split-Path -Parent $target) | Out-Null
Invoke-WebRequest -Uri 'https://files.grouplens.org/datasets/hetrec2011/hetrec2011-lastfm-2k.zip' -OutFile $target
