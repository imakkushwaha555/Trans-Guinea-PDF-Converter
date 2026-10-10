# Project state (updated 2026-10-10, release v0.1.1)

Repo: imakkushwaha555/trans-guinea-pdf-converter, branch main. Shell on the dev PC is PowerShell 5.1 (no `&&`, `-Encoding` on Tee-Object not supported).

## Done
- Tools: Convert (Word/visual Word/Excel), Merge, Split. In-app help (`help_content.py`, `/help`, `/help/search`).
- Branding: `assets/logo.svg`; `tools/make_icon.py` generates ico/png/icns.
- **Native window**: `run.py` starts a Werkzeug server on a random 127.0.0.1 port in a thread and opens it with pywebview (Edge WebView2 on Windows, WebKit on macOS). Closing the window quits the app. `python run.py --browser` or any pywebview failure falls back to the default browser. Downloads use the native Save As dialog (`ALLOW_DOWNLOADS`). Windowed builds log to `%LOCALAPPDATA%\Trans-Guinea PDF Converter\app.log` (macOS: `~/Library/Logs/...`).
- Packaging: `packaging/trans_guinea_pdf_converter.spec` (PyInstaller one-folder, windowed), `build_windows.ps1` (portable zip + Inno Setup installer + `release\SHA256SUMS.txt`, finds ISCC in LocalAppData/Program Files), `Trans-Guinea-PDF-Converter.iss`, `build_macos.sh` (.dmg per arch).
- CI: `.github/workflows/release.yml` on `v*` tags builds Windows + macOS (macos-13 Intel, macos-14 ARM) and attaches to the GitHub release.
- Release v0.1.1 published: Windows installer, portable zip, macOS arm64 dmg. The macOS Intel (macos-13) job was still queued at last check; it attaches itself when done.
- winget manifests in `packaging/winget/` are at 0.1.1 with the real installer SHA256 and pass `winget validate`.
- 36 tests pass (`python -m pytest test_app.py`).

## Decisions
- Windows is 64-bit only (32-bit Windows is about 0.01% of users and key wheels are 64-bit only). macOS has no 32-bit.
- No universal2 macOS dmg: numpy, Pillow, PyMuPDF, opencv, pypdfium2 and cffi have no universal2 wheels. Keep separate arm64 and x86_64 dmgs.
- Installer is unsigned (SmartScreen and Gatekeeper warn).
- Version string `0.1.1` is hardcoded in: pyproject.toml, the .iss, build_macos.sh, build_windows.ps1, release.yml, winget yamls, README. Bump all of them for a release.

## Gotchas
- Tool policy blocks `Stop-Process -Name`; always use `-Id`.
- `build.log` and `*.code-workspace` are gitignored. Run only one `build_windows.ps1` at a time.
- A first tag push can run before the workflow is registered; re-push the tag if no run starts.
- Merging with origin/main needed `--allow-unrelated-histories` once (already done).

## Open items
1. Check the macos-13 job finished and the Intel dmg is attached to v0.1.1 (`gh run view 38072556795`).
2. Submit the winget PR to microsoft/winget-pkgs (copy `packaging/winget/*` to `manifests/i/imakkushwaha555/TransGuineaPDFConverter/0.1.1/`).
3. Untested: drag-and-drop and the password prompt in the native window; the whole macOS build on a real Mac.
4. Optional: code signing, GitHub repo topics and a README screenshot, SECURITY.md review.
