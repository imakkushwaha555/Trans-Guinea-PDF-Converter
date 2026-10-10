# Trans-Guinea PDF Converter

**Free, open-source, offline PDF tools: convert PDF to Word or Excel, merge PDFs, and split PDFs by page numbers.** Files are processed locally on your computer, so you never upload sensitive documents to an online PDF service.

## Tools

| Tool | What it does |
| --- | --- |
| **Convert** | PDF to editable Word, visual-fidelity Word, or Excel tables |
| **Merge** | Combine several PDFs into one, in the order you choose |
| **Split** | Cut a PDF into parts using page numbers such as `1-3, 5, 8-10`, or one file per page |

Password-protected PDFs are supported in every tool: a popup asks for the password only when needed.

### Why use Trans-Guinea PDF Converter?

- **PDF to Word conversion** for editable text and reconstructed document layout.
- **Visual-fidelity PDF to Word conversion** for scanned PDFs, images, unusual fonts, spacing, and page alignment.
- **PDF to Excel conversion** for extracting detected tables into worksheets.
- **Merge and split PDF** without any cloud service.
- **Local and privacy-focused processing**: temporary files only, deleted as soon as the job finishes.
- **Windows installer and portable release** planned for direct GitHub downloads and WinGet distribution.

Search terms: PDF to Word converter, PDF to Excel converter, merge PDF, split PDF, offline PDF tools, local PDF converter, privacy-focused document converter, editable Word from PDF, scanned PDF converter, and Windows PDF converter.

## Output modes

- **Editable Word** — uses `pdf2docx` to reconstruct editable text and layout.
- **Visual-fidelity Word** — renders each PDF page into a page-sized image inside a DOCX. This preserves images, unusual or illegible fonts, spacing, and alignment much more reliably, but the page content is not editable.
- **Excel tables** — extracts detected tables into separate worksheets. Excel output is intentionally table-focused and is not a complete visual reproduction of a PDF page.

For scanned PDFs, image-only pages, custom fonts, or documents where alignment is more important than editability, use Visual-fidelity Word.

## Requirements

- Python 3.11 or newer
- Windows, macOS, or Linux
- 25 MB maximum per PDF and 100 MB per request (merge accepts up to 20 files)

## Run locally

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

python -m pip install -r requirements.txt
python run.py
```

The app opens in its own window (use `python run.py --browser` to open it in your browser instead).

## Install as a package

```bash
python -m pip install .
trans-guinea-pdf-converter
```

For development and tests:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Windows distribution

End users do not need Python or the packages in `requirements.txt` when using a release build. The Windows release bundles the Python runtime and application dependencies into a PyInstaller build, then packages it with an Inno Setup installer.

### Build locally on Windows

Install Python 3.11 or newer and Inno Setup, then run PowerShell from the project root:

```powershell
.\packaging\build_windows.ps1
```

The `release/` directory will contain a setup executable and a portable ZIP. The installer is the recommended download for normal users; the ZIP is useful when installation privileges are unavailable.

### GitHub Releases and WinGet

Create a version tag such as `v0.1.2` and push it to GitHub. The release workflow builds the Windows installer and portable ZIP and attaches both to a GitHub Release. The installer URL and its SHA-256 hash can then be used to create a WinGet manifest. WinGet submissions require a stable package identifier/version and installer metadata, including the installer type, download URL, and SHA-256 hash.

### Advanced install (PowerShell)

The installer wizard offers a desktop shortcut option. From PowerShell:

```powershell
# From source: pull the latest code and run it
git clone https://github.com/imakkushwaha555/trans-guinea-pdf-converter.git
cd trans-guinea-pdf-converter
git pull
python -m pip install .
trans-guinea-pdf-converter

# From WinGet, once the package is published
winget install imakkushwaha555.TransGuineaPDFConverter

# Test the local manifest (run once as admin: winget settings --enable LocalManifestFiles)
winget install --manifest .\packaging\winget
```

Before submitting to winget-pkgs, replace `InstallerSha256` in `packaging/winget` with the value from the release's `SHA256SUMS.txt`.

## macOS distribution

Release builds ship as a `.dmg` for Apple Silicon (`arm64`) and Intel (`x86_64`): open it and drag the app to Applications. The app is unsigned, so on first launch right-click it and choose Open (or allow it under System Settings > Privacy & Security).

To build locally on a Mac with Python 3.11+:

```bash
bash packaging/build_macos.sh
```

From source on macOS or Linux:

```bash
git clone https://github.com/imakkushwaha555/trans-guinea-pdf-converter.git
cd trans-guinea-pdf-converter && python3 -m pip install . && trans-guinea-pdf-converter
```

## Security and privacy

- Only PDF files are accepted, and each upload is checked for damage before conversion.
- Passwords are requested in a popup only for protected PDFs, and are never logged or written to disk.
- Each job runs in a private temporary folder that is deleted as soon as the job finishes, including on errors.
- The converted file is returned directly to the browser; no copy is kept by the app. Leftover working folders from a crash are purged at startup.
- This application is intended for local use. Do not expose it to the public internet without adding authentication, rate limiting, HTTPS, and deployment-specific hardening.

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## Community and accessibility

Please read the [Code of Conduct](CODE_OF_CONDUCT.md) before participating.
Accessibility goals, supported environments, known limitations, and barrier
reporting are documented in [ACCESSIBILITY.md](ACCESSIBILITY.md). Bug reports,
feature requests, and pull requests use the templates in `.github` so that
reports include useful context without exposing private documents or
credentials.

## License

MIT. See [LICENSE](LICENSE).

## Attribution

The original Trans-Guinea PDF Converter project is copyright **IMakKushwaha**.
If you use, redistribute, or substantially modify this project, preserve the
[LICENSE](LICENSE) and [NOTICE](NOTICE) files and provide reasonable credit to
**IMakKushwaha** and the **Trans-Guinea PDF Converter contributors** in
documentation or other accompanying attribution notices. See
[AUTHORS.md](AUTHORS.md) for the contributor-credit policy.