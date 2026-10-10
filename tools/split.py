from __future__ import annotations

import logging
import re
import zipfile
from io import BytesIO

from flask import Blueprint, jsonify, render_template, request
from pypdf import PdfReader, PdfWriter

from pdf_common import (
    ConversionError,
    error_response,
    file_response,
    job_dir,
    page_count,
    prepare_pdf,
    safe_stem,
    save_pdf_upload,
)

logger = logging.getLogger(__name__)
bp = Blueprint("split", __name__)

MAX_PARTS = 200
_TOKEN = re.compile(r"^(\d{1,6})(?:\s*-\s*(\d{1,6}))?$")


def parse_ranges(text: str, total_pages: int) -> list[tuple[int, int]]:
    """Parse '1-3, 5, 8-10' into 1-based inclusive (start, end) pairs."""
    tokens = [token.strip() for token in (text or "").split(",") if token.strip()]
    if not tokens:
        raise ConversionError("Enter the page numbers to split, for example 1-3, 5, 8-10.")
    ranges = []
    for token in tokens:
        match = _TOKEN.match(token)
        if not match:
            raise ConversionError(f"'{token}' is not a valid page or range. Use numbers like 3 or 2-5.")
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if start < 1 or end < start:
            raise ConversionError(f"'{token}' is not a valid page range.")
        if end > total_pages:
            raise ConversionError(f"'{token}' is outside the document, which has {total_pages} page(s).")
        ranges.append((start, end))
    return ranges


@bp.get("/split")
def page():
    return render_template("split.html")


@bp.post("/split")
def run():
    uploaded_file = request.files.get("file")
    mode = request.form.get("mode", "ranges")
    password = request.form.get("password") or None

    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"error": "Please choose a PDF file to upload."}), 400
    if mode not in {"ranges", "every_page"}:
        return jsonify({"error": "Please choose a supported split mode."}), 400

    try:
        with job_dir() as work_dir:
            source = work_dir / "upload.pdf"
            name = save_pdf_upload(uploaded_file, source)
            prepared = prepare_pdf(source, password, work_dir)
            total = page_count(prepared)
            if mode == "every_page":
                ranges = [(number, number) for number in range(1, total + 1)]
            else:
                ranges = parse_ranges(request.form.get("ranges", ""), total)
            if len(ranges) > MAX_PARTS:
                raise ConversionError(f"Please split into at most {MAX_PARTS} parts at a time.")

            stem = safe_stem(name)
            reader = PdfReader(str(prepared))
            parts: list[tuple[str, bytes]] = []
            for number, (start, end) in enumerate(ranges, start=1):
                writer = PdfWriter()
                for index in range(start - 1, end):
                    writer.add_page(reader.pages[index])
                buffer = BytesIO()
                writer.write(buffer)
                label = f"{start}" if start == end else f"{start}-{end}"
                parts.append((f"{stem}_part{number}_pages_{label}.pdf", buffer.getvalue()))

        if len(parts) == 1:
            return file_response(parts[0][1], "application/pdf", parts[0][0])
        archive = BytesIO()
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            for part_name, data in parts:
                bundle.writestr(part_name, data)
        return file_response(archive.getvalue(), "application/zip", f"{stem}_split.zip")
    except ConversionError as exc:
        return error_response(exc)
    except Exception:
        logger.exception("Split failed")
        return jsonify({"error": "Split failed. Please check the PDF and try again."}), 500
