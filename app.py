from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from flask import Flask, Response, jsonify, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge

from pdf_common import MAX_REQUEST_BYTES, purge_leftover_jobs
from tools import convert, merge, split

BASE_DIR = Path(__file__).resolve().parent
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", BASE_DIR))

TOOLS = [
    {
        "endpoint": "convert.page",
        "path": "/convert",
        "icon": "W",
        "title": "Convert PDF",
        "summary": "Turn a PDF into an editable Word document, a visual-fidelity Word file, or Excel tables.",
    },
    {
        "endpoint": "merge.page",
        "path": "/merge",
        "icon": "+",
        "title": "Merge PDFs",
        "summary": "Combine several PDF files into one document, in the order you choose.",
    },
    {
        "endpoint": "split.page",
        "path": "/split",
        "icon": "/",
        "title": "Split PDF",
        "summary": "Cut a PDF into separate files using page numbers such as 1-3, 5, 8-10.",
    },
]

purge_leftover_jobs()

app = Flask(
    __name__,
    template_folder=str(RESOURCE_DIR / "templates"),
    static_folder=str(RESOURCE_DIR / "static"),
)
app.config.update(MAX_CONTENT_LENGTH=MAX_REQUEST_BYTES)
logging.basicConfig(level=logging.INFO)

for module in (convert, merge, split):
    app.register_blueprint(module.bp)


def _site_url() -> str:
    return (os.environ.get("SITE_URL") or request.url_root).rstrip("/")


@app.context_processor
def inject_site():
    return {"tools": TOOLS, "site_url": _site_url(), "canonical_url": _site_url() + request.path}


@app.after_request
def secure_response(response):
    response.headers.setdefault("Cache-Control", "no-store")
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    )
    return response


@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(_error):
    return jsonify({"error": "The upload is too large. Each PDF must be under 25 MB and the total under 100 MB."}), 413


@app.get("/")
def index():
    return render_template("home.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/robots.txt")
def robots():
    body = f"User-agent: *\nAllow: /\nSitemap: {_site_url()}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@app.get("/sitemap.xml")
def sitemap():
    base = _site_url()
    urls = "".join(
        f"<url><loc>{escape(base + path)}</loc></url>" for path in ["/", *[tool["path"] for tool in TOOLS]]
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    return Response(xml, mimetype="application/xml")


if __name__ == "__main__":
    app.run(debug=False, port=5000)
