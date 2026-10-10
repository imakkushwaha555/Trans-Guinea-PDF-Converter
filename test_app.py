import io
from pathlib import Path

import pymupdf
import pytest
from docx import Document

from app import _convert_to_visual_docx, app


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


def test_password_protected_pdf_requests_password(client, monkeypatch, tmp_path):
    monkeypatch.setattr("app.UPLOAD_FOLDER", tmp_path)

    class EncryptedReader:
        is_encrypted = True

        def __init__(self, *_args, **_kwargs):
            pass

        def decrypt(self, _password):
            return 0

    monkeypatch.setattr("app.PdfReader", EncryptedReader)
    response = client.post(
        "/convert",
        data={"format": "docx", "file": (io.BytesIO(b"%PDF-1.7"), "locked.pdf")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "password protected" in response.json["error"]


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