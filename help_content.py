"""Help articles shown on the home page search and /help."""
from __future__ import annotations

ISSUES_URL = "https://github.com/imakkushwaha555/trans-guinea-pdf-converter/issues"

ARTICLES = [
    {"id": "convert-word", "title": "Convert a PDF to Word", "tags": "docx word editable layout fidelity",
     "body": "Open Convert PDF, choose a PDF, pick Word, then download the .docx. Use the visual-fidelity mode to keep the layout, or the editable mode to get text you can change."},
    {"id": "convert-excel", "title": "Convert PDF tables to Excel", "tags": "xlsx excel spreadsheet tables",
     "body": "Open Convert PDF and choose Excel. Tables found in the PDF become sheets in an .xlsx file. Scanned pages without real text cannot be read."},
    {"id": "merge", "title": "Merge several PDFs", "tags": "combine join order",
     "body": "Open Merge PDFs, add two or more files, put them in the order you want, then merge. The result is one PDF."},
    {"id": "split", "title": "Split a PDF by pages", "tags": "extract pages range cut",
     "body": "Open Split PDF and enter page numbers such as 1-3, 5, 8-10. Each range becomes its own PDF."},
    {"id": "password", "title": "Password-protected PDFs", "tags": "encrypted locked unlock",
     "body": "You are asked for the password in a popup only when needed. It is used for that job only and is never stored or logged."},
    {"id": "size", "title": "File size limits", "tags": "large too big upload limit 25 MB 100 MB",
     "body": "Each PDF must be under 25 MB and the total under 100 MB per job. Split large files first."},
    {"id": "privacy", "title": "Are my files uploaded anywhere?", "tags": "privacy offline cloud security delete",
     "body": "No. Files are processed on this computer in a temporary folder and removed when the job finishes."},
    {"id": "scanned", "title": "Scanned PDFs give empty results", "tags": "ocr image scan blank empty",
     "body": "Scanned pages are images, so there is no text to extract. OCR is not included in this version."},
    {"id": "browser", "title": "The app did not open in my browser", "tags": "start launch window port blank",
     "body": "The app runs locally and opens your default browser. If nothing appears, start it again from the Start menu or Applications folder and wait a few seconds. Only one copy should be running."},
    {"id": "close", "title": "How do I close the app?", "tags": "quit exit stop running",
     "body": "Close the browser tab, then end the app from Task Manager (Windows) or Activity Monitor (macOS)."},
    {"id": "logs", "title": "Where are the log files?", "tags": "log error crash debug report",
     "body": "Windows: %LOCALAPPDATA%\\Trans-Guinea PDF Converter\\app.log. macOS: ~/Library/Logs/Trans-Guinea PDF Converter. Attach it to a bug report; it contains no PDF content."},
    {"id": "gatekeeper", "title": "Windows SmartScreen or macOS Gatekeeper warning", "tags": "unsigned blocked unidentified developer more info",
     "body": "Release builds are not code-signed yet. On Windows choose More info, then Run anyway. On macOS right-click the app and choose Open."},
    {"id": "install", "title": "Install with winget", "tags": "powershell command line update uninstall",
     "body": "Run: winget install imakkushwaha555.TransGuineaPDFConverter. Uninstall with winget uninstall, or from Windows Settings."},
]


def search(query: str, limit: int = 6) -> list[dict]:
    terms = [t for t in query.lower().split() if t]
    if not terms:
        return []
    scored = []
    for article in ARTICLES:
        title = article["title"].lower()
        haystack = f"{title} {article['tags']} {article['body'].lower()}"
        if not all(term in haystack for term in terms):
            continue
        score = sum(3 for term in terms if term in title) + sum(1 for term in terms if term in article["tags"])
        scored.append((-score, article["title"], article))
    scored.sort(key=lambda item: item[:2])
    return [item[2] for item in scored[:limit]]
