# Accessibility statement

Trans-Guinea PDF Converter is intended to be usable by as many people as
possible. Accessibility is part of our normal design and review process, not a
separate feature. We welcome reports that help us identify barriers and improve
the application.

## Current commitment

The application provides a local web interface with several accessibility
foundations, including:

- Semantic HTML landmarks and headings.
- A labelled navigation region and current-page indication.
- Explicit labels for file, select, radio, text, and password controls.
- A file-picker alternative to drag-and-drop interactions.
- Keyboard-operable buttons, links, forms, and expandable FAQ sections.
- Status and error messaging using live regions where appropriate.
- Alternative text treatment for the decorative brand mark and icons.
- Responsive layouts for small screens.
- A `prefers-reduced-motion` mode that reduces animation and transition effects.
- Local processing, which avoids requiring users to upload documents to a
  remote service.

We aim to follow WCAG 2.1 AA practices where practical. This project has not
yet completed a formal WCAG conformance audit, and this statement is not a
claim of full conformance.

## Supported environments

The application is designed for:

- Windows, macOS, and Linux when run from source with Python 3.11 or newer.
- The packaged Windows installer and portable release.
- macOS releases for Apple Silicon and Intel where published.
- The application's embedded window, or a current desktop browser when started
  with `python run.py --browser`.

The browser interface is built with standard HTML, CSS, and JavaScript. Users
who encounter an issue with the embedded application window can try the browser
mode to compare behavior with their browser and assistive technology.

## Known limitations

Known limitations include:

- The project does not currently have a formal accessibility test matrix for
  every screen reader, browser, operating system, or high-contrast mode.
- Drag-and-drop behavior and dynamic conversion feedback may not be equally
  clear in every assistive technology. The file picker and status messages are
  intended as alternatives.
- Visual-fidelity conversion produces page images inside a Word document; the
  resulting document may not contain the source PDF's semantic structure or
  accessible text.
- PDF and Office files supplied by users may themselves contain inaccessible
  content that this tool cannot repair.
- The application is still evolving, so some accessibility issues may remain
  in focus indication, error recovery, or third-party rendering behavior.

## Reporting an accessibility barrier

Please [open an accessibility issue][accessibility-issue] and include:

- The page, tool, or release where the barrier occurred.
- The operating system, browser or embedded-window mode, and assistive
  technology, if relevant.
- The steps that caused the problem and what you expected to happen.
- A description of the barrier, including whether it blocks or merely makes a
  task difficult.
- A minimal screenshot or recording only if it contains no private documents,
  passwords, or personal information.

You may also report an accessibility concern privately if the report includes
sensitive information. Do not include real user documents or passwords in a
public issue. We will acknowledge reports as soon as practical, assess their
impact, and track appropriate fixes in the public project when possible.

## Contributing accessibility improvements

Pull requests that improve keyboard access, focus behavior, semantics, screen
reader support, contrast, reduced motion, responsive behavior, or accessible
documentation are welcome. Please describe how you tested the change in the
pull request, including the environment and assistive technology when
available.

[accessibility-issue]: https://github.com/imakkushwaha555/Trans-Guinea-PDF-Converter/issues/new?template=bug_report.md&labels=accessibility