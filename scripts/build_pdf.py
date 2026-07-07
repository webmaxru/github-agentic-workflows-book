#!/usr/bin/env python3
"""Render the single-page book edition (site/book.html) into a downloadable PDF.

This is the second half of the book build: `site/generate.py` emits
`site/book.html` (all chapters on one printable page); this script loads that page
in headless Chromium (Playwright) and prints it to `site/gh-aw-book.pdf` with page
numbers, a running footer, and a PDF outline. Chromium runs highlight.js, so code
blocks keep their syntax colors in the PDF.

The PDF is a binary BUILD ARTIFACT: it is gitignored and produced fresh here (in CI
on every book change, and locally on demand) rather than committed to `main`.

Usage:
    python site/generate.py            # 1. (re)build site/book.html
    python scripts/build_pdf.py        # 2. render the PDF

Requirements (see scripts/requirements-pdf.txt):
    python -m pip install -r scripts/requirements-pdf.txt
    python -m playwright install chromium     # add --with-deps on Linux/CI
"""
from __future__ import annotations

import functools
import http.server
import socketserver
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BOOK_PAGE = "book.html"
PDF_PATH = SITE / "gh-aw-book.pdf"

# Running footer: book title on the left, "Page N / M" on the right. The
# pageNumber / totalPages spans are filled in by Chromium.
FOOTER_TEMPLATE = (
    '<div style="width:100%;font-family:\'Hanken Grotesk\',Arial,sans-serif;'
    'font-size:8px;color:#8a93a6;padding:0 14mm;display:flex;'
    'justify-content:space-between;align-items:center;">'
    '<span>GitHub Agentic Workflows \u2014 An Interactive Book</span>'
    '<span>Page <span class="pageNumber"></span> / <span class="totalPages"></span></span>'
    "</div>"
)
HEADER_TEMPLATE = '<div style="height:0"></div>'

PDF_MARGIN = {"top": "16mm", "bottom": "18mm", "left": "15mm", "right": "15mm"}


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # noqa: D401 - silence per-request logging
        pass


def _serve(directory: Path) -> tuple[socketserver.TCPServer, int]:
    """Serve `directory` on an ephemeral localhost port in a background thread."""
    handler = functools.partial(_QuietHandler, directory=str(directory))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


def build_pdf() -> Path:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise SystemExit(
            "Playwright is not installed. Run:\n"
            "  python -m pip install -r scripts/requirements-pdf.txt\n"
            "  python -m playwright install chromium"
        ) from exc

    book = SITE / BOOK_PAGE
    if not book.exists():
        raise SystemExit(
            f"{book} not found. Run `python site/generate.py` first to build it."
        )

    httpd, port = _serve(SITE)
    url = f"http://127.0.0.1:{port}/{BOOK_PAGE}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=90_000)
            # Wait for the page's load handler to run highlight.js and flag readiness.
            try:
                page.wait_for_function(
                    "document.documentElement.getAttribute('data-book-ready') === '1'",
                    timeout=20_000,
                )
            except Exception:  # highlight.js CDN slow/unavailable — print anyway
                pass
            # Ensure web fonts are laid out before measuring page breaks.
            page.evaluate("() => (document.fonts ? document.fonts.ready : true)")
            page.wait_for_timeout(400)

            pdf_kwargs = dict(
                path=str(PDF_PATH),
                format="A4",
                print_background=True,
                display_header_footer=True,
                header_template=HEADER_TEMPLATE,
                footer_template=FOOTER_TEMPLATE,
                margin=PDF_MARGIN,
            )
            # `outline`/`tagged` add PDF bookmarks + accessibility on newer
            # Playwright; fall back cleanly if the installed version lacks them.
            try:
                page.pdf(outline=True, tagged=True, **pdf_kwargs)
            except TypeError:
                page.pdf(**pdf_kwargs)
            browser.close()
    finally:
        httpd.shutdown()

    return PDF_PATH


def main() -> None:
    pdf = build_pdf()
    size_kb = pdf.stat().st_size / 1024
    print(f"Wrote {pdf} ({size_kb:,.0f} KB)")
    if size_kb < 20:
        print("Warning: PDF is unexpectedly small — check the render.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
