# Trans-Guinea PDF Converter

**Trans-Guinea PDF Converter** is a free, privacy-focused PDF converter for Windows and desktop use. Convert PDF files to editable Word documents, visual-fidelity Word documents, or Excel workbooks containing detected tables. Files are processed locally on your computer, so you do not need to upload sensitive documents to an online PDF conversion service.

### Why use Trans-Guinea PDF Converter?

- **PDF to Word conversion** for editable text and reconstructed document layout.
- **Visual-fidelity PDF to Word conversion** for scanned PDFs, images, unusual fonts, spacing, and page alignment.
- **PDF to Excel conversion** for extracting detected tables into worksheets.
- **Local and privacy-focused processing** with no cloud upload required.
- **Windows installer and portable release** planned for direct GitHub downloads and WinGet distribution.

Search terms: PDF to Word converter, PDF to Excel converter, offline PDF converter, local PDF converter, privacy-focused document converter, editable Word from PDF, scanned PDF converter, and Windows PDF converter.

## Output modes

- **Editable Word** — uses `pdf2docx` to reconstruct editable text and layout.
- **Visual-fidelity Word** — renders each PDF page into a page-sized image inside a DOCX. This preserves images, unusual or illegible fonts, spacing, and alignment much more reliably, but the page content is not editable.
- **Excel tables** — extracts detected tables into separate worksheets. Excel output is intentionally table-focused and is not a complete visual reproduction of a PDF page.

For scanned PDFs, image-only pages, custom fonts, or documents where alignment is more important than editability, use Visual-fidelity Word.

## Requirements

- Python 3.11 or newer
- Windows, macOS, or Linux
- 25 MB maximum upload size by default

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

Open `http://127.0.0.1:5000` in a browser.

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

Create a version tag such as `v0.1.0` and push it to GitHub. The release workflow builds the Windows installer and portable ZIP and attaches both to a GitHub Release. The installer URL and its SHA-256 hash can then be used to create a WinGet manifest. WinGet submissions require a stable package identifier/version and installer metadata, including the installer type, download URL, and SHA-256 hash.

## Security and privacy

- Passwords are never logged or written to disk.
- Uploaded PDFs are stored under generated random names and removed after conversion.
- Decrypted working PDFs and rendered page images are temporary and removed immediately.
- Generated output files remain in `converted/` until manually deleted or cleaned by the operator.
- This application is intended for local use. Do not expose it to the public internet without adding authentication, rate limiting, HTTPS, and deployment-specific hardening.

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## License

MIT. See [LICENSE](LICENSE).