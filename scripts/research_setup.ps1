$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.tools/uv-cache'
$env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.tools/python'
if (-not (Test-Path '.venv-legacy/Scripts/python.exe')) {
    python -c "import sys; assert sys.version_info[:2] == (3, 10), 'Bootstrap requires Python 3.10'"
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.10 and make it the bootstrap python command' }
    python -m venv .venv-legacy
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.10 is required for the isolated legacy environment' }
}
& '.venv-legacy/Scripts/python.exe' -c "import sys; assert sys.version_info[:2] == (3, 10)"
if ($LASTEXITCODE -ne 0) { throw 'The existing legacy environment must use Python 3.10' }
& '.venv-legacy/Scripts/python.exe' -m pip install uv==0.13.0
if ($LASTEXITCODE -ne 0) { throw 'uv installation failed' }
$uv = '.venv-legacy/Scripts/uv.exe'
& $uv sync --python 3.11 --frozen --extra dev --extra research --extra experiments
if ($LASTEXITCODE -ne 0) { throw 'Core environment setup failed' }
& $uv pip install --python '.venv-legacy/Scripts/python.exe' --index-strategy unsafe-best-match -r 'requirements/legacy-reproduction.txt'
if ($LASTEXITCODE -ne 0) { throw 'Legacy environment setup failed' }
Write-Output 'Ready: .venv/Scripts/python.exe scripts/research.py all'
