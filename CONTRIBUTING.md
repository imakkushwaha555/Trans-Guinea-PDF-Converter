# Contributing

1. Create a branch for your change.
2. Keep user documents, passwords, generated files, virtual environments, and secrets out of commits.
3. Add or update tests for behavior changes.
4. Run:

```bash
python -m py_compile app.py run.py test_app.py
python -m pytest
```

5. Describe conversion fidelity limitations clearly in pull requests and documentation.

Please do not submit PDFs containing private or copyrighted material as fixtures. Prefer small synthetic PDFs generated during tests.