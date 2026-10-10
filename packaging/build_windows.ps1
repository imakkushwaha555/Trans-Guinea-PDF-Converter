$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
$version = if ($env:RELEASE_VERSION) { $env:RELEASE_VERSION.TrimStart("v") } elseif ($env:GITHUB_REF_NAME) { $env:GITHUB_REF_NAME.TrimStart("v") } else { "0.1.2" }

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.11+ is required to build the Windows package."
}

python -m pip install --upgrade pip
python -m pip install ".[build]"
python tools/make_icon.py
python -m PyInstaller --noconfirm --clean packaging/trans_guinea_pdf_converter.spec

$releaseDir = Join-Path $projectRoot "release"
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
$zipPath = Join-Path $releaseDir "Trans-Guinea-PDF-Converter-$version-portable.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path (Join-Path $projectRoot "dist\Trans-Guinea PDF Converter\*") -DestinationPath $zipPath

$iscc = Get-Command iscc.exe -ErrorAction SilentlyContinue
$isccPath = $null
if ($iscc) { $isccPath = $iscc.Source }
else {
    $candidates = @("$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe", "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:ProgramFiles\Inno Setup 6\ISCC.exe")
    $isccPath = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if ($isccPath) {
    & $isccPath "/DMyAppVersion=$version" (Join-Path $projectRoot "packaging\Trans-Guinea-PDF-Converter.iss")
} else {
    Write-Warning "Inno Setup is not installed; portable ZIP was created but the installer was skipped."
}

Get-ChildItem $releaseDir -File | Where-Object { $_.Name -ne "SHA256SUMS.txt" } | ForEach-Object {
    "$((Get-FileHash $_.FullName -Algorithm SHA256).Hash)  $($_.Name)"
} | Set-Content (Join-Path $releaseDir "SHA256SUMS.txt")

Write-Host "Release artifacts are in $releaseDir"