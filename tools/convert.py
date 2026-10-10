from __future__ import annotations

import json
import logging
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import pdfplumber
import pymupdf
from docx import Document
from docx.enum.section import WD_SECTION
from docx.shared import Inches, Pt
from flask import Blueprint, jsonify, render_template, request
from pdf2docx import Converter

from pdf_common import (
    DAMAGED_MESSAGE,
    ConversionError,
    error_response,
    file_response,
    job_dir,
    prepare_pdf,
    safe_stem,
    save_pdf_upload,
)

logger = logging.getLogger(__name__)
bp = Blueprint("convert", __name__)

ALLOWED_FORMATS = {"docx", "docx_visual", "xlsx"}
MIME_TYPES = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def _output_extension(target_format: str) -> str:
    return "docx" if target_format in {"docx", "docx_visual"} else "xlsx"


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


@bp.get("/convert")
def page():
    return render_template("convert.html")


@bp.post("/convert")
def run():
    uploaded_file = request.files.get("file")
    target_format = request.form.get("format", "").lower().strip()
    password = request.form.get("password") or None

    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"error": "Please choose a PDF file to upload."}), 400
    if target_format not in ALLOWED_FORMATS:
        return jsonify({"error": "Please choose a supported output format."}), 400

    output_kind = _output_extension(target_format)
    try:
        with job_dir() as work_dir:
            pdf_path = work_dir / "upload.pdf"
            output_path = work_dir / f"output.{output_kind}"
            original_name = save_pdf_upload(uploaded_file, pdf_path)
            conversion_path = prepare_pdf(pdf_path, password, work_dir)

            warnings = _analyze_pdf(conversion_path)
            if target_format == "docx":
                _convert_to_docx(conversion_path, output_path)
            elif target_format == "docx_visual":
                _convert_to_visual_docx(conversion_path, output_path)
            else:
                _convert_to_xlsx(conversion_path, output_path)
            result = output_path.read_bytes()

        response = file_response(
            result, MIME_TYPES[output_kind], f"{safe_stem(original_name, 'converted-document')}.{output_kind}"
        )
        response.headers["X-Conversion-Warnings"] = quote(json.dumps(warnings))
        return response
    except ConversionError as exc:
        return error_response(exc)
    except Exception:
        logger.exception("Conversion failed")
        return jsonify({"error": "Conversion failed. Please check the PDF and try again."}), 500
