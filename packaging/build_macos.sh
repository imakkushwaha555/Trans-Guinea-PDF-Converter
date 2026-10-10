#!/usr/bin/env bash
# Builds the macOS .app and a drag-to-Applications .dmg into release/.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -m pip install --upgrade pip
python3 -m pip install ".[build]"
python3 tools/make_icon.py
python3 -m PyInstaller --noconfirm --clean packaging/trans_guinea_pdf_converter.spec

arch="$(uname -m)"
mkdir -p release
dmg="release/Trans-Guinea-PDF-Converter-0.1.0-macos-${arch}.dmg"
rm -f "$dmg"
stage="$(mktemp -d)"
cp -R "dist/Trans-Guinea PDF Converter.app" "$stage/"
ln -s /Applications "$stage/Applications"
hdiutil create -volname "Trans-Guinea PDF Converter" -srcfolder "$stage" -ov -format UDZO "$dmg"
rm -rf "$stage"

(cd release && shasum -a 256 "$(basename "$dmg")" > "SHA256SUMS-macos-${arch}.txt")
echo "Release artifacts are in release/"
