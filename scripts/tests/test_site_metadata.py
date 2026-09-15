"""Presentation metadata checks; all source fixtures and generated files are temporary.

Run: python -B -m unittest discover -s scripts/tests -p test_site_metadata.py -v
No browser, network, real chapter files, or tracked site output is needed.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from types import ModuleType
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import content_version  # noqa: E402

UPSTREAM_RELEASES = "https://github.com/github/gh-aw/releases/tag/"
# Deliberately unrelated to the real corpus: change framework alone, then prose alone.
VERSION_CASES = (("7.4", "v3.21.8"), ("7.4", "v3.22.0"), ("7.5", "v3.22.0"))


class ParsedHTML(HTMLParser):
    """Extract actual metadata, link labels, and JSON-LD without a UI dependency."""

    def __init__(self, markup: str):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.links = []
        self.graph = []
        self.text = ""
        self._href = None
        self._link_text = ""
        self._json = None
        self.feed(markup)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and "name" in attrs:
            self.meta[attrs["name"]] = attrs.get("content")
        elif tag == "a":
            self._href = attrs.get("href")
            self._link_text = ""
        elif tag == "script" and attrs.get("type") == "application/ld+json":
            self._json = ""

    def handle_data(self, data):
        self.text += data
        if self._href is not None:
            self._link_text += data
        if self._json is not None:
            self._json += data

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, self._link_text.strip()))
            self._href = None
        elif tag == "script" and self._json is not None:
            self.graph.extend(json.loads(self._json)["@graph"])
            self._json = None


def load_script(relative_path: str) -> ModuleType:
    """A fresh import models a new CLI build after source metadata changes."""
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(f"_metadata_test_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    # Both scripts add scripts/ to sys.path; do not accumulate entries between tests.
    with mock.patch.object(sys, "path", sys.path.copy()):
        spec.loader.exec_module(module)
    return module


class SiteMetadataTests(unittest.TestCase):
    def setUp(self):
        scratch_root = ROOT / "build" / "tests"
        scratch_root.mkdir(parents=True, exist_ok=True)
        scratch = TemporaryDirectory(prefix="book-metadata-", dir=scratch_root)
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.content = self.root / "content"
        self.fragments = self.content / "chapters"
        self.fragments.mkdir(parents=True)
        self.output = self.root / "site"
        self.output.mkdir()
        for attr, filename in (
            ("VERSION_PATH", "VERSION"),
            ("FRAMEWORK_VERSION_PATH", "FRAMEWORK_VERSION"),
            ("CHANGELOG_PATH", "CHANGELOG.md"),
        ):
            patch = mock.patch.object(content_version, attr, self.content / filename)
            patch.start()
            self.addCleanup(patch.stop)
        # Avoid reading a real local .env while keeping the existing analytics wiring testable.
        connection_string = os.environ.get("APPINSIGHTS_CONNECTION_STRING")
        os.environ["APPINSIGHTS_CONNECTION_STRING"] = "metadata-test"
        if connection_string is None:
            self.addCleanup(os.environ.pop, "APPINSIGHTS_CONNECTION_STRING", None)
        else:
            self.addCleanup(os.environ.__setitem__, "APPINSIGHTS_CONNECTION_STRING", connection_string)

        self.chapters = [
            {"id": "foundations", "slug": "foundations", "number": 1,
             "title": "Fixture concepts", "objective": "A concept fixture.", "sections": ["Concept"]},
            {"id": "capabilities", "slug": "capabilities", "number": 2,
             "title": "Fixture capabilities", "objective": "A capability fixture.",
             "sections": ["Practice"], "depends_on": ["foundations"], "features": ["safe-outputs"]},
        ]
        self.parts = [
            {"number": 1, "title": "Part I — Fixtures", "chapters": ["foundations", "capabilities"]}
        ]
        self.slots = {
            "foundations": {
                "concept": '<p>Fixture concept. <a class="xref" href="capabilities.html">Capability</a></p>'
            },
            "capabilities": {
                "practice": '<p>Fixture capability. <a class="xref" href="foundations.html">Concept</a></p>'
            },
        }
        for slug, slots in self.slots.items():
            fragment = "\n".join(
                f'<section data-slot="{slot}">{body}</section>' for slot, body in slots.items()
            )
            (self.fragments / f"{slug}.html").write_text(fragment, encoding="utf-8")
        (self.content / "toc.yml").write_text(
            json.dumps({"chapters": self.chapters, "parts": self.parts}), encoding="utf-8"
        )
        self.set_metadata(*VERSION_CASES[0])

    def set_metadata(self, edition: str, framework: str):
        (self.content / "VERSION").write_text(edition + "\n", encoding="utf-8")
        (self.content / "FRAMEWORK_VERSION").write_text(framework + "\n", encoding="utf-8")
        (self.content / "CHANGELOG.md").write_text(
            f"## [{edition}] - 2026-09-15\n\nCurrent fixture.\n\n### Changed\n\n- Fixture change.\n\n"
            "## [7.3] - 2026-01-01\n\nArchived fixture.\n",
            encoding="utf-8",
        )

    def generator(self):
        generator = load_script("site/generate.py")
        generator.SITE = self.output
        generator.CHAPTERS_DIR = self.output / "chapters"
        generator.CONTENT_CHAPTERS_DIR = self.fragments
        generator.TOC_PATH = self.content / "toc.yml"
        return generator

    def region(self, markup: str, tag: str, class_name: str) -> ParsedHTML:
        match = re.search(
            rf'<{tag}\b[^>]*class="{re.escape(class_name)}"[^>]*>(.*?)</{tag}>',
            markup, re.DOTALL,
        )
        self.assertIsNotNone(match, f"Missing {tag}.{class_name}")
        return ParsedHTML(match.group(1))

    def assert_framework_link(self, document: ParsedHTML, framework: str):
        self.assertIn(
            (UPSTREAM_RELEASES + framework, f"Verified with gh-aw {framework}"), document.links
        )

    def test_source_versions_flow_independently_to_all_editions(self):
        for edition, framework in VERSION_CASES:
            with self.subTest(edition=edition, framework=framework):
                self.set_metadata(edition, framework)
                with mock.patch.object(
                    content_version, "read_framework_version",
                    wraps=content_version.read_framework_version,
                ) as read_framework:
                    generator = self.generator()
                    pdf = load_script("scripts/build_pdf.py")
                self.assertEqual(read_framework.call_count, 2)
                self.assertEqual(generator.CONTENT_VERSION_TAG, f"content-v{edition}")
                self.assertTrue(generator.RELEASE_URL.endswith(f"/content-v{edition}"))
                grouped = generator.group_parts(self.chapters, self.parts)
                pages = [
                    (generator.render_index(grouped), "section", "cover", "colophon", "Book"),
                    (generator.render_chapter(self.chapters, grouped, 0, self.slots["foundations"]),
                     "header", "chapter-header", "site-footer chapter-footer", "TechArticle"),
                    (generator.render_book(self.chapters, grouped, self.slots),
                     "header", "book-cover", "book-colophon", "Book"),
                    (generator.render_versions(), "section", "version-hero", "colophon", None),
                ]
                for markup, tag, chrome_class, footer_class, schema_type in pages:
                    with self.subTest(page=chrome_class):
                        document = ParsedHTML(markup)
                        self.assertEqual(document.meta["book-content-version"], edition)
                        self.assertEqual(document.meta["gh-aw-framework-version"], framework)
                        chrome = self.region(markup, tag, chrome_class)
                        footer = self.region(markup, "footer", footer_class)
                        for region in (chrome, footer):
                            self.assert_framework_link(region, framework)
                            self.assertIn("content edition", region.text.lower())
                            self.assertIn(f"v{edition}", region.text)
                        if schema_type:
                            node = next(n for n in document.graph if n["@type"] == schema_type)
                            field = "bookEdition" if schema_type == "Book" else "version"
                            self.assertEqual(node[field], edition)
                            self.assertEqual(node["about"]["@type"], "SoftwareApplication")
                            self.assertEqual(node["about"]["softwareVersion"], framework)
                            self.assertEqual(node["about"]["url"], UPSTREAM_RELEASES + framework)
                footer = ParsedHTML(pdf.FOOTER_TEMPLATE)
                self.assertIn(f"Content edition v{edition}", footer.text)
                self.assert_framework_link(footer, framework)
                self.assertIn('class="pageNumber"', pdf.FOOTER_TEMPLATE)
                self.assertIn('class="totalPages"', pdf.FOOTER_TEMPLATE)

    def test_history_keeps_current_coverage_out_of_release_cards(self):
        generator = self.generator()
        markup = generator.render_versions()
        self.assertIn("not to past releases listed below.", markup)
        cards = re.findall(r'<article class="release\b[^"]*"[^>]*>.*?</article>', markup, re.DOTALL)
        self.assertEqual(len(cards), 2)
        for card, edition in zip(cards, ("7.4", "7.3")):
            with self.subTest(edition=edition):
                document = ParsedHTML(card)
                self.assertIn(f"Content edition v{edition}", document.text)
                self.assertIn(
                    (f"{generator.REPO_URL}/releases/tag/content-v{edition}", f"content-v{edition} ↗"),
                    document.links,
                )
                self.assertNotIn("Verified with gh-aw", card)
                self.assertNotIn("v3.21.8", card)
                self.assertNotIn(UPSTREAM_RELEASES, card)
                self.assertEqual("release--current" in card, edition == "7.4")

    def test_discovery_versions_and_tagged_links_follow_source_changes(self):
        for edition, framework in VERSION_CASES:
            with self.subTest(edition=edition, framework=framework):
                self.set_metadata(edition, framework)
                generator = self.generator()
                generator.write_discovery_files(self.chapters)
                llms = (self.output / "llms.txt").read_text(encoding="utf-8")
                full = (self.output / "llms-full.txt").read_text(encoding="utf-8")
                self.assertIn(f"Content edition v{edition}", llms)
                self.assertIn(f"Content edition: v{edition}", full)
                for discovery in (llms, full):
                    self.assertIn(
                        f"[Verified with gh-aw {framework}]({UPSTREAM_RELEASES}{framework})",
                        discovery,
                    )
                    self.assertNotIn("/releases/latest", discovery)
                self.assertEqual((self.output / "CNAME").read_text().strip(), "aw.isainative.dev")

    def test_temporary_build_preserves_fragments_navigation_and_chrome(self):
        generator = self.generator()
        originals = {path: path.read_bytes() for path in self.fragments.iterdir()}
        with mock.patch("sys.stdout", new=io.StringIO()):
            generator.main()
        for path, original in originals.items():
            self.assertEqual(path.read_bytes(), original)
        index = (self.output / "index.html").read_text(encoding="utf-8")
        book = (self.output / "book.html").read_text(encoding="utf-8")
        self.assertEqual(ParsedHTML(book).meta["robots"], "noindex, follow")
        self.assertIn('id="ch-foundations--concept"', book)
        self.assertIn('href="#ch-capabilities"', book)
        chapter_files = sorted(path.name for path in (self.output / "chapters").glob("*.html"))
        self.assertEqual(chapter_files, ["capabilities.html", "foundations.html"])
        for chapter in self.chapters:
            slug = chapter["slug"]
            page = (self.output / "chapters" / f"{slug}.html").read_text(encoding="utf-8")
            self.assertIn(f'href="chapters/{slug}.html"', index)
            self.assertIn(f'aria-current="page" href="{slug}.html"', page)
            for slot, body in self.slots[slug].items():
                self.assertIn(f'id="{slot}"', page)
                self.assertIn(body, page)
            for theme in ("light", "sepia", "dark"):
                self.assertIn(f'data-theme-value="{theme}"', page)
            self.assertIn('class="skip-link" href="#main-content"', page)
            self.assertIn('<script defer src="../assets/analytics.js"></script>', page)
            self.assertIn('window.__APPINSIGHTS_CONNECTION_STRING__="metadata-test"', page)
            self.assertIn(
                f'<link rel="canonical" href="https://aw.isainative.dev/chapters/{slug}.html">', page
            )
            direction, neighbor = (
                ("next", "capabilities") if slug == "foundations" else ("prev", "foundations")
            )
            self.assertIn(f'rel="{direction}" href="{neighbor}.html"', page)
        for filename in ("index.html", "versions.html"):
            markup = (self.output / filename).read_text(encoding="utf-8")
            self.assertIn('<script defer src="assets/analytics.js"></script>', markup)
            self.assertIn('aria-label="Content edition v7.4 — view version history"', markup)

    def test_pdf_renderer_passes_the_versioned_footer_to_chromium(self):
        pdf = load_script("scripts/build_pdf.py")
        pdf.SITE = self.output
        pdf.PDF_PATH = self.output / "fixture.pdf"
        (self.output / pdf.BOOK_PAGE).write_text("<!doctype html><title>Fixture</title>", encoding="utf-8")
        # Mock at the lazy-import boundary, so Playwright/Chromium need not be installed.
        sync_api = ModuleType("playwright.sync_api")
        sync_api.sync_playwright = mock.MagicMock()
        playwright = ModuleType("playwright")
        playwright.sync_api = sync_api
        browser = sync_api.sync_playwright.return_value.__enter__.return_value.chromium.launch.return_value
        page = browser.new_page.return_value
        httpd = mock.Mock()
        with mock.patch.dict(sys.modules, {"playwright": playwright, "playwright.sync_api": sync_api}):
            with mock.patch.object(pdf, "_serve", return_value=(httpd, 12345)):
                self.assertEqual(pdf.build_pdf(), pdf.PDF_PATH)
        page.pdf.assert_called_once()
        kwargs = page.pdf.call_args.kwargs
        self.assertEqual(kwargs["footer_template"], pdf.FOOTER_TEMPLATE)
        self.assertTrue(kwargs["display_header_footer"])
        self.assertTrue(kwargs["tagged"])
        self.assertTrue(kwargs["outline"])
        self.assert_framework_link(ParsedHTML(kwargs["footer_template"]), "v3.21.8")
        httpd.shutdown.assert_called_once()

    def test_framework_reader_errors_are_not_hidden_by_presentation_fallbacks(self):
        for script in ("site/generate.py", "scripts/build_pdf.py"):
            for problem in ("missing", "malformed"):
                with self.subTest(script=script, problem=problem):
                    error = ValueError(f"{problem} framework metadata: FRAMEWORK_VERSION")
                    with mock.patch.object(content_version, "read_framework_version", side_effect=error):
                        with self.assertRaises(ValueError) as raised:
                            load_script(script)
                    self.assertIs(raised.exception, error)
        self.assertEqual(list(self.output.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
