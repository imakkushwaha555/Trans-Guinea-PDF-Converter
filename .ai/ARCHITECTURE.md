# Architecture and rules

- `app.py`: Flask app factory, registers blueprints, security headers.
- `pdf_common.py`: header check, `prepare_pdf` (validate + decrypt), `PasswordRequired`, `job_dir()` temp-folder context manager.
- `tools/convert.py`, `tools/merge.py`, `tools/split.py`: one blueprint each.
- `templates/`: `base.html` plus one template per page.

## Privacy rules (never break)
1. Files only live inside `job_dir()` (system temp, prefix `trans-guinea-job-`), deleted when the request ends.
2. Results are returned in the same response; nothing is kept for later download.
3. Passwords are never logged or stored.
4. Only PDFs are accepted, and are checked for damage before use.
5. Leftover job folders are purged at startup.
