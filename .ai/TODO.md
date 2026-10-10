# Backlog

Work is split into small pieces. Tick a box only when its check passes (`python -m pytest`).

## 0. Privacy purge
- [x] Remove generated documents from all local Git history and refs
- [x] Ignore `*.docx`, `*.xlsx`, `*.pdf`, `*.zip` in `.gitignore`
- [ ] Before the first push: `git log --all -- converted` must print nothing

## 1. Structure
- [x] `pdf_common.py`: shared validation, password signalling, temp-job helper
- [x] `tools/convert.py`, `tools/merge.py`, `tools/split.py` as Flask blueprints
- [x] `app.py` only creates the app and registers blueprints

## 2. Merge
- [x] `POST /merge`: many PDFs, upload order kept, limits enforced
- [x] Password popup per protected file (index + name in the response)
- [x] UI: reorder (Up/Down) and remove files

## 3. Split
- [x] `POST /split`: ranges like `1-3, 5, 8-10`, ZIP result (single part returns a PDF)
- [x] Range validation with clear errors
- [x] UI: range input and "one file per page" option

## 4. Landing page
- [x] `/` shows Convert, Merge, Split cards
- [x] Shared `base.html`; each tool on its own page

## 5. SEO and metadata
- [x] Title, description, canonical, Open Graph, Twitter, JSON-LD per page
- [x] `robots.txt`, `sitemap.xml`
- [x] `pyproject.toml` keywords/classifiers, README opening
- [ ] Set GitHub repo topics (`merge-pdf`, `split-pdf`) and add a screenshot to the README

## 6. Release
- [x] Tests for all tools; temp folder empty after every job
- [x] README updated
- [ ] SECURITY.md review
- [ ] Browser smoke test of all three pages
- [ ] Push only after item 0 check passes
