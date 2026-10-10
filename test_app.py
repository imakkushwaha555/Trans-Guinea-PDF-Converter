import io
import tempfile
from pathlib import Path

import pymupdf
import pytest
from docx import Document

from app import TEMP_PREFIX, _convert_to_visual_docx, app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Trans-Guinea PDF Converter" in response.data


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_requires_file(client):
    response = client.post("/convert", data={"format": "docx"})
    assert response.status_code == 400
    assert "choose a PDF" in response.json["error"]


def test_rejects_non_pdf(client):
    response = client.post(
        "/convert",
        data={"format": "docx", "file": (io.BytesIO(b"not a pdf"), "notes.txt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "Only PDF" in response.json["error"]


def _make_pdf(password=None, pages=1):
    pdf = pymupdf.open()
    for index in range(pages):
        pdf.new_page().insert_text((72, 90), f"Page {index + 1} sample text", fontsize=14)
    buffer = io.BytesIO()
    if password:
        pdf.save(buffer, encryption=pymupdf.PDF_ENCRYPT_AES_256, user_pw=password, owner_pw=password)
    else:
        pdf.save(buffer)
    pdf.close()
    return buffer.getvalue()


def _post(client, data, name="sample.pdf", fmt="docx", password=None):
    form = {"format": fmt, "file": (io.BytesIO(data), name)}
    if password is not None:
        form["password"] = password
    return client.post("/convert", data=form, content_type="multipart/form-data")


def _job_dirs():
    return list(Path(tempfile.gettempdir()).glob(f"{TEMP_PREFIX}*"))


def test_password_protected_pdf_requests_password(client):
    response = _post(client, _make_pdf("secret"), "locked.pdf")
    assert response.status_code == 401
    assert response.json["password_required"] is True
    assert response.json["incorrect"] is False


def test_wrong_password_is_flagged(client):
    response = _post(client, _make_pdf("secret"), "locked.pdf", password="nope")
    assert response.status_code == 401
    assert response.json["incorrect"] is True


def test_correct_password_returns_file_and_cleans_up(client):
    response = _post(client, _make_pdf("secret"), "locked.pdf", password="secret")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"].startswith("attachment")
    assert Document(io.BytesIO(response.data)).paragraphs is not None
    assert _job_dirs() == []


def test_corrupted_pdf_is_rejected_and_cleaned_up(client):
    response = _post(client, b"%PDF-1.7\n1 0 obj\n<< broken", "broken.pdf")
    assert response.status_code == 400
    assert "damaged" in response.json["error"]
    assert _job_dirs() == []


def test_non_pdf_content_with_pdf_name_is_rejected(client):
    response = _post(client, b"plain text, not a pdf", "fake.pdf")
    assert response.status_code == 400
    assert "not a valid PDF" in response.json["error"]
    assert _job_dirs() == []


def test_download_route_is_gone(client):
    assert client.get("/download/anything.docx").status_code == 404


def test_rejects_unknown_format(client):
    response = client.post(
        "/convert",
        data={"format": "pptx", "file": (io.BytesIO(b"%PDF-1.7"), "sample.pdf")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "supported output format" in response.json["error"]


def test_visual_docx_contains_page_image(tmp_path):
    pdf_path = tmp_path / "visual-source.pdf"
    docx_path = tmp_path / "visual-output.docx"
    pdf = pymupdf.open()
    page = pdf.new_page(width=612, height=792)
    page.insert_text((72, 90), "Visual fidelity test", fontsize=18)
    page.draw_rect(pymupdf.Rect(72, 130, 250, 250), color=(0.5, 0.1, 0.3), fill=(0.9, 0.5, 0.7))
    pdf.save(pdf_path)
    pdf.close()

    _convert_to_visual_docx(Path(pdf_path), Path(docx_path))

    document = Document(docx_path)
    assert len(document.inline_shapes) == 1