from __future__ import annotations

import json
import logging
import shutil
import sys
import tempfile
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import pymupdf
import pdfplumber
from docx import Document
from docx.enum.section import WD_SECTION
from docx.shared import Inches, Pt
from flask import Flask, jsonify, render_template, request, send_file
from pdf2docx import Converter
from pypdf import PdfReader, PdfWriter
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", BASE_DIR))
ALLOWED_FORMATS = {"docx", "docx_visual", "xlsx"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
TEMP_PREFIX = "trans-guinea-job-"
MIME_TYPES = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def _purge_leftover_jobs() -> None:
    """Remove working folders left behind by a previous crash."""
    for leftover in Path(tempfile.gettempdir()).glob(f"{TEMP_PREFIX}*"):
        shutil.rmtree(leftover, ignore_errors=True)


_purge_leftover_jobs()

app = Flask(__name__, template_folder=str(RESOURCE_DIR / "templates"))
app.config.update(MAX_CONTENT_LENGTH=MAX_UPLOAD_BYTES)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """An expected error that can be safely shown to the user."""


class PasswordRequired(ConversionError):
    """The PDF is encrypted and needs a (correct) password."""

    def __init__(self, message: str, incorrect: bool = False):
        super().__init__(message)
        self.incorrect = incorrect


def _has_pdf_header(path: Path) -> bool:
    try:
        with path.open("rb") as file_handle:
            return b"%PDF-" in file_handle.read(1024)
    except OSError:
        return False


def _safe_output_name(original_name: str, extension: str) -> str:
    stem = Path(secure_filename(original_name)).stem or "converted-document"
    return f"{stem}.{extension}"


def _output_extension(target_format: str) -> str:
    return "docx" if target_format in {"docx", "docx_visual"} else "xlsx"


DAMAGED_MESSAGE = "The uploaded PDF could not be read. The file appears to be damaged or unsupported."


def _prepare_pdf(pdf_path: Path, password: str | None, work_dir: Path) -> Path:
    """Validate the PDF and return a readable (decrypted if needed) copy inside work_dir."""
    try:
        reader = PdfReader(str(pdf_path), strict=False)
        usable_path = pdf_path
        if reader.is_encrypted:
            if not password:
                raise PasswordRequired("This PDF is password protected.")
            if reader.decrypt(password) == 0:
                raise PasswordRequired("The password is incorrect. Please try again.", incorrect=True)
            usable_path = work_dir / "decrypted.pdf"
        if not len(reader.pages):
            raise ConversionError(DAMAGED_MESSAGE)
        if usable_path != pdf_path:
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            with usable_path.open("wb") as handle:
                writer.write(handle)

        with pymupdf.open(str(usable_path)) as document:
            if document.needs_pass or document.page_count < 1:
                raise ConversionError(DAMAGED_MESSAGE)
            for page in document:
                page.get_text("text")
            document.load_page(0).get_pixmap(matrix=pymupdf.Matrix(0.2, 0.2))
        return usable_path
    except ConversionError:
        raise
    except Exception as exc:
        logger.warning("PDF validation failed: %s", type(exc).__name__)
        raise ConversionError(DAMAGED_MESSAGE) from exc


def _convert_to_docx(pdf_path: Path, output_path: Path) -> None:
    converter = None
    try:
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
            document.add_picture(BytesIO(pixmap.tobytes("png")), width=Pt(width_points))
    document.save(str(output_path))


def _convert_to_xlsx(pdf_path: Path, output_path: Path) -> None:
    tables: list[tuple[int, pd.DataFrame]] = []
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                table = page.extract_table()
                if not table or len(table) < 2:
                    continue
                headers = [str(value or f"Column_{index + 1}") for index, value in enumerate(table[0])]
                frame = pd.DataFrame(table[1:], columns=headers)
                frame = frame.loc[:, ~frame.columns.duplicated()]
                tables.append((page_number, frame))
    except Exception as exc:
        raise ConversionError(DAMAGED_MESSAGE) from exc

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

    output_name = _safe_output_name(original_name, _output_extension(target_format))
    output_kind = _output_extension(target_format)

    try:
        with tempfile.TemporaryDirectory(prefix=TEMP_PREFIX, ignore_cleanup_errors=True) as work:
            work_dir = Path(work)
            pdf_path = work_dir / "upload.pdf"
            output_path = work_dir / f"output.{output_kind}"
            uploaded_file.save(pdf_path)
            if not _has_pdf_header(pdf_path):
                raise ConversionError("The uploaded file is not a valid PDF.")
            conversion_path = _prepare_pdf(pdf_path, password, work_dir)

            warnings = _analyze_pdf(conversion_path)
            if target_format == "docx":
                _convert_to_docx(conversion_path, output_path)
            elif target_format == "docx_visual":
                _convert_to_visual_docx(conversion_path, output_path)
            else:
                _convert_to_xlsx(conversion_path, output_path)
            result = output_path.read_bytes()

        response = send_file(
            BytesIO(result),
            mimetype=MIME_TYPES[output_kind],
            as_attachment=True,
            download_name=output_name,
        )
        response.headers["X-Conversion-Warnings"] = quote(json.dumps(warnings))
        response.headers["Cache-Control"] = "no-store"
        return response
    except PasswordRequired as exc:
        return jsonify({"password_required": True, "incorrect": exc.incorrect, "error": str(exc)}), 401
    except ConversionError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        logger.exception("Conversion failed")
        return jsonify({"error": "Conversion failed. Please check the PDF and try again."}), 500


@app.after_request
def disable_caching(response):
    response.headers["Cache-Control"] = "no-store"
    return response


if __name__ == "__main__":
    app.run(debug=True, port=5000)