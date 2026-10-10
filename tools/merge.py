from __future__ import annotations

import json
import logging

from flask import Blueprint, jsonify, render_template, request
from pypdf import PdfWriter

from pdf_common import (
    ConversionError,
    PasswordRequired,
    error_response,
    file_response,
    job_dir,
    prepare_pdf,
    save_pdf_upload,
)

logger = logging.getLogger(__name__)
bp = Blueprint("merge", __name__)

MIN_FILES = 2
MAX_FILES = 20


def _parse_passwords(raw: str | None) -> dict[str, str]:
    try:
        data = json.loads(raw or "{}")
    except ValueError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(key): value for key, value in data.items() if isinstance(value, str)}


@bp.get("/merge")
def page():
    return render_template("merge.html")


@bp.post("/merge")
def run():
    uploads = [item for item in request.files.getlist("files") if item.filename]
    passwords = _parse_passwords(request.form.get("passwords"))

    if len(uploads) < MIN_FILES:
        return jsonify({"error": f"Please add at least {MIN_FILES} PDF files to merge."}), 400
    if len(uploads) > MAX_FILES:
        return jsonify({"error": f"You can merge up to {MAX_FILES} files at a time."}), 400

    try:
        with job_dir() as work_dir:
            prepared = []
            for index, item in enumerate(uploads):
                source = work_dir / f"in-{index}.pdf"
                label = item.filename
                try:
                    save_pdf_upload(item, source)
                    prepared.append(prepare_pdf(source, passwords.get(str(index)), work_dir, f"dec-{index}.pdf"))
                except PasswordRequired as exc:
                    exc.index, exc.name = index, label
                    raise
                except ConversionError as exc:
                    raise ConversionError(f"{label}: {exc}") from exc

            writer = PdfWriter()
            for path in prepared:
                writer.append(str(path))
            merged_path = work_dir / "merged.pdf"
            with merged_path.open("wb") as handle:
                writer.write(handle)
            writer.close()
            result = merged_path.read_bytes()
        return file_response(result, "application/pdf", "merged.pdf")
    except ConversionError as exc:
        return error_response(exc)
    except Exception:
        logger.exception("Merge failed")
        return jsonify({"error": "Merge failed. Please check the PDFs and try again."}), 500
