from __future__ import annotations

import logging
import shutil
import tempfile
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path

import pymupdf
from flask import jsonify, send_file
from pypdf import PdfReader, PdfWriter
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

TEMP_PREFIX = "trans-guinea-job-"
MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_REQUEST_BYTES = 100 * 1024 * 1024
DAMAGED_MESSAGE = "The uploaded PDF could not be read. The file appears to be damaged or unsupported."


class ConversionError(Exception):
    """An expected error that can be safely shown to the user."""


class PasswordRequired(ConversionError):
    """The PDF is encrypted and needs a (correct) password."""

    def __init__(self, message: str, incorrect: bool = False):
        super().__init__(message)
        self.incorrect = incorrect
        self.index: int | None = None
        self.name: str | None = None


def purge_leftover_jobs() -> None:
    """Remove working folders left behind by a previous crash."""
    for leftover in Path(tempfile.gettempdir()).glob(f"{TEMP_PREFIX}*"):
        shutil.rmtree(leftover, ignore_errors=True)


@contextmanager
def job_dir():
    """Private working folder that is always deleted when the job ends."""
    with tempfile.TemporaryDirectory(prefix=TEMP_PREFIX, ignore_cleanup_errors=True) as work:
        yield Path(work)


def safe_stem(original_name: str, fallback: str = "document") -> str:
    return Path(secure_filename(original_name)).stem or fallback


def save_pdf_upload(uploaded_file, destination: Path) -> str:
    """Save an uploaded PDF into the job folder after basic checks; return its safe name."""
    name = secure_filename(uploaded_file.filename or "")
    if not name.lower().endswith(".pdf"):
        raise ConversionError("Only PDF files are supported.")
    uploaded_file.save(destination)
    if destination.stat().st_size > MAX_FILE_BYTES:
        raise ConversionError("That file is too large. Please upload a PDF smaller than 25 MB.")
    try:
        with destination.open("rb") as handle:
            has_header = b"%PDF-" in handle.read(1024)
    except OSError:
        has_header = False
    if not has_header:
        raise ConversionError("The uploaded file is not a valid PDF.")
    return name


def prepare_pdf(pdf_path: Path, password: str | None, work_dir: Path, decrypted_name: str = "decrypted.pdf") -> Path:
    """Validate the PDF and return a readable (decrypted if needed) copy inside work_dir."""
    try:
        reader = PdfReader(str(pdf_path), strict=False)
        usable_path = pdf_path
        if reader.is_encrypted:
            if not password:
                raise PasswordRequired("This PDF is password protected.")
            if reader.decrypt(password) == 0:
                raise PasswordRequired("The password is incorrect. Please try again.", incorrect=True)
            usable_path = work_dir / decrypted_name
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


def page_count(pdf_path: Path) -> int:
    with pymupdf.open(str(pdf_path)) as document:
        return document.page_count


def file_response(data: bytes, mimetype: str, download_name: str):
    response = send_file(BytesIO(data), mimetype=mimetype, as_attachment=True, download_name=download_name)
    response.headers["Cache-Control"] = "no-store"
    return response


def error_response(exc: ConversionError):
    if isinstance(exc, PasswordRequired):
        return jsonify({
            "password_required": True,
            "incorrect": exc.incorrect,
            "error": str(exc),
            "file_index": exc.index,
            "file_name": exc.name,
        }), 401
    return jsonify({"error": str(exc)}), 400
