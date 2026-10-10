from __future__ import annotations

import logging
import os
import secrets
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pymupdf
import pdfplumber
from docx import Document
from docx.enum.section import WD_SECTION
from docx.shared import Inches, Pt
from flask import Flask, jsonify, render_template, request, send_from_directory
from pdf2docx import Converter
from pypdf import PdfReader, PdfWriter
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", BASE_DIR))
APP_DATA_DIR = Path(
    os.environ.get(
        "TRANS_GUINEA_DATA_DIR",
        Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        / "Trans-Guinea PDF Converter",
    )
)
UPLOAD_FOLDER = APP_DATA_DIR / "uploads"
CONVERTED_FOLDER = APP_DATA_DIR / "converted"
ALLOWED_FORMATS = {"docx", "docx_visual", "xlsx"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
CONVERTED_FOLDER.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, template_folder=str(RESOURCE_DIR / "templates"))
app.config.update(
    MAX_CONTENT_LENGTH=MAX_UPLOAD_BYTES,
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    CONVERTED_FOLDER=CONVERTED_FOLDER,
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """An expected error that can be safely shown to the user."""


def _is_pdf(path: Path) -> bool:
    try:
        with path.open("rb") as file_handle:
            return file_handle.read(5) == b"%PDF-"
    except OSError:
        return False


def _safe_output_name(original_name: str, extension: str) -> str:
    stem = Path(secure_filename(original_name)).stem or "converted-document"
    return f"{stem}-{secrets.token_hex(6)}.{extension}"


def _output_extension(target_format: str) -> str:
    return "docx" if target_format in {"docx", "docx_visual"} else "xlsx"


def _prepare_pdf(pdf_path: Path, password: str | None) -> Path:
    try:
        reader = PdfReader(str(pdf_path), strict=False)
        if not reader.is_encrypted:
            return pdf_path
        if not password:
            raise ConversionError("This PDF is password protected. Enter its password and try again.")
        if reader.decrypt(password) == 0:
            raise ConversionError("The PDF password is incorrect. Please check it and try again.")
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        decrypted_handle = tempfile.NamedTemporaryFile(
            mode="wb", suffix=".pdf", prefix="trans-guinea-convert-", delete=False
        )
        decrypted_path = Path(decrypted_handle.name)
        try:
            writer.write(decrypted_handle)
        finally:
            decrypted_handle.close()
        return decrypted_path
    except ConversionError:
        raise
    except Exception as exc:
        logger.exception("Unable to inspect uploaded PDF")
        raise ConversionError("The uploaded PDF could not be opened. It may be damaged or unsupported.") from exc


def _convert_to_docx(pdf_path: Path, output_path: Path, password: str | None) -> None:
    converter = None
    try:
        try:
            converter = Converter(str(pdf_path), password=password)
        except TypeError:
            converter = Converter(str(pdf_path))
        converter.convert(str(output_path), start=0, end=None)
    finally:
        if converter is not None:
            converter.close()


def _analyze_pdf(pdf_path: Path) -> list[str]:
    warnings = []
    try:
        with pymupdf.open(str(pdf_path)) as document:
            image_only_pages = 0
            image_pages = 0
            for page in document:
                text = page.get_text("text").strip()
                images = page.get_images(full=True)
                image_pages += bool(images)
                image_only_pages += bool(images) and len(text) < 20
            if image_only_pages:
                warnings.append(
                    f"{image_only_pages} page(s) appear to be scanned or image-only. "
                    "Visual-fidelity Word mode is recommended."
                )
            elif image_pages:
                warnings.append(
                    "This PDF contains embedded images. Visual-fidelity Word mode preserves "
                    "their appearance more reliably."
                )
    except Exception:
        logger.warning("Unable to analyze PDF content", exc_info=True)
    return warnings


def _convert_to_visual_docx(pdf_path: Path, output_path: Path) -> None:
    document = Document()
    document.core_properties.title = "Visual-fidelity PDF conversion"
    with pymupdf.open(str(pdf_path)) as pdf:
        if not pdf.page_count:
            raise ConversionError("The PDF has no pages to convert.")
        for index, page in enumerate(pdf):
            if index:
                section = document.add_section(WD_SECTION.NEW_PAGE)
            else:
                section = document.sections[0]
            width_points = page.rect.width
            height_points = page.rect.height
            section.page_width = Pt(width_points)
            section.page_height = Pt(height_points)
            section.top_margin = Inches(0)
            section.bottom_margin = Inches(0)
            section.left_margin = Inches(0)
            section.right_margin = Inches(0)

            pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
            image_handle = tempfile.NamedTemporaryFile(
                suffix=".png", prefix="trans-guinea-page-", delete=False
            )
            image_path = Path(image_handle.name)
            image_handle.close()
            try:
                pixmap.save(str(image_path))
                document.add_picture(str(image_path), width=Pt(width_points))
            finally:
                image_path.unlink(missing_ok=True)
    document.save(str(output_path))


def _convert_to_xlsx(pdf_path: Path, output_path: Path, password: str | None) -> None:
    tables: list[tuple[int, pd.DataFrame]] = []
    try:
        with pdfplumber.open(str(pdf_path), password=password) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                table = page.extract_table()
                if not table or len(table) < 2:
                    continue
                headers = [str(value or f"Column_{index + 1}") for index, value in enumerate(table[0])]
                frame = pd.DataFrame(table[1:], columns=headers)
                frame = frame.loc[:, ~frame.columns.duplicated()]
                tables.append((page_number, frame))
    except Exception as exc:
        message = str(exc).lower()
        if "password" in message or "decrypt" in message:
            raise ConversionError("The PDF password is incorrect. Please check it and try again.") from exc
        raise

    if not tables:
        raise ConversionError("No tables were found in this PDF for Excel conversion.")

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for page_number, frame in tables:
            frame.to_excel(writer, sheet_name=f"Page_{page_number}"[:31], index=False)


@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(_error):
    return jsonify({"error": "That file is too large. Please upload a PDF smaller than 25 MB."}), 413


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/convert", methods=["POST"])
def convert():
    uploaded_file = request.files.get("file")
    target_format = request.form.get("format", "").lower().strip()
    password = request.form.get("password") or None

    if uploaded_file is None:
        return jsonify({"error": "Please choose a PDF file to upload."}), 400
    if not uploaded_file.filename:
        return jsonify({"error": "Please choose a PDF file to upload."}), 400
    if target_format not in ALLOWED_FORMATS:
        return jsonify({"error": "Please choose a supported output format."}), 400

    original_name = secure_filename(uploaded_file.filename)
    if not original_name.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    token = secrets.token_hex(12)
    pdf_path = UPLOAD_FOLDER / f"{token}.pdf"
    output_name = _safe_output_name(original_name, _output_extension(target_format))
    output_path = CONVERTED_FOLDER / output_name
    conversion_path = pdf_path

    try:
        uploaded_file.save(pdf_path)
        if not _is_pdf(pdf_path):
            raise ConversionError("The uploaded file is not a valid PDF.")
        conversion_path = _prepare_pdf(pdf_path, password)

        warnings = _analyze_pdf(conversion_path)
        if target_format == "docx":
            _convert_to_docx(conversion_path, output_path, None)
        elif target_format == "docx_visual":
            _convert_to_visual_docx(conversion_path, output_path)
        else:
            _convert_to_xlsx(conversion_path, output_path, None)

        return jsonify({
            "download_url": f"/download/{output_name}",
            "filename": output_name,
            "warnings": warnings,
        })
    except ConversionError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        logger.exception("Conversion failed for %s", original_name)
        return jsonify({"error": "Conversion failed. Please check the PDF and try again."}), 500
    finally:
        pdf_path.unlink(missing_ok=True)
        if conversion_path != pdf_path:
            conversion_path.unlink(missing_ok=True)


@app.route("/download/<path:filename>")
def download(filename):
    return send_from_directory(CONVERTED_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5000)