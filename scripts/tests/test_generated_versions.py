import unittest

from helpers import SourceTest

import release_content as release


class GeneratedVersionTests(SourceTest):
    def setUp(self):
        super().setUp()
        for name in ("index.html", "versions.html", "chapters/one.html"):
            self.put(
                f"site/{name}",
                '<meta name="book-content-version" content="1.1">'
                '<meta name="gh-aw-framework-version" content="v0.81.6">'
                '<a class="version-pill" href="versions.html" title="Content version 1.1 — history">v1.1</a>',
            )
        self.put(
            "site/book.html",
            '<meta name="book-content-version" content="1.1">'
            '<meta name="gh-aw-framework-version" content="v0.81.6">'
            '<p class="book-cover-meta">Version 1.1 · 1 chapter</p>',
        )
        (self.root / "site/gh-aw-book.pdf").write_bytes(b"%PDF-1.7\n" + b" " * 21_000)

    def test_current_generated_markers_and_pdf_pass(self):
        report = release.check_generated(self.root)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["html_pages"], 4)

    def test_old_generated_page_and_framework_markers_fail(self):
        self.put("site/chapters/one.html", '<a href="../versions.html">v1.0</a>')
        with self.assertRaisesRegex(release.ReleaseError, "content version mismatch"):
            release.check_generated(self.root)
        self.put(
            "site/chapters/one.html",
            '<meta name="book-content-version" content="1.1">'
            '<meta name="gh-aw-framework-version" content="v0.88.7">',
        )
        with self.assertRaisesRegex(release.ReleaseError, "framework version mismatch"):
            release.check_generated(self.root)

    def test_missing_framework_marker_fails(self):
        self.put("site/book.html", '<meta name="book-content-version" content="1.1">')
        with self.assertRaisesRegex(release.ReleaseError, "framework version mismatch or missing"):
            release.check_generated(self.root)

    def test_missing_or_invalid_pdf_fails(self):
        path = self.root / "site/gh-aw-book.pdf"
        path.unlink()
        with self.assertRaisesRegex(release.ReleaseError, "PDF is missing"):
            release.check_generated(self.root)
        path.write_bytes(b"not a PDF" + b" " * 21_000)
        with self.assertRaisesRegex(release.ReleaseError, "invalid header"):
            release.check_generated(self.root)


if __name__ == "__main__":
    unittest.main()
