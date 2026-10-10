$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.11+ is required to build the Windows package."
}

python -m pip install --upgrade pip
python -m pip install ".[build]"
python -m PyInstaller --noconfirm --clean packaging/trans_guinea_pdf_converter.spec

$releaseDir = Join-Path $projectRoot "release"
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
$zipPath = Join-Path $releaseDir "Trans-Guinea-PDF-Converter-0.1.0-portable.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path (Join-Path $projectRoot "dist\Trans-Guinea PDF Converter\*") -DestinationPath $zipPath

$iscc = Get-Command iscc.exe -ErrorAction SilentlyContinue
if ($iscc) {
    & $iscc.Source (Join-Path $projectRoot "packaging\Trans-Guinea-PDF-Converter.iss")
} else {
    Write-Warning "Inno Setup is not installed; portable ZIP was created but the installer was skipped."
}

Write-Host "Release artifacts are in $releaseDir"