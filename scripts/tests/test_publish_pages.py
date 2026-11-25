import unittest
from unittest.mock import call, patch

from helpers import ROOT

import approved_book
import publish_pages

REPO = "webmaxru/github-agentic-workflows-book"
COMMIT = "a" * 40
SOURCE = {"build_type": "legacy", "source": {"branch": "gh-pages", "path": "/"}}
BUILDS = f"/repos/{REPO}/pages/builds"
BUILDS_URL = f"https://api.github.com{BUILDS}"


class PagesTests(unittest.TestCase):
    def test_build_requests_and_checks_exact_legacy_commit(self):
        api = approved_book.GitHub(REPO, "fixture")
        for target in ("latest", "42"):
            path = f"{BUILDS}/{target}"
            with self.subTest(target=target), patch.object(api, "request", side_effect=[
                SOURCE, {"url": f"{BUILDS_URL}/{target}"}, {"status": "building"},
                {"status": "built", "commit": COMMIT},
            ]) as request:
                result = publish_pages.request_build(api, COMMIT, sleep=lambda _: None)
                self.assertEqual(result["commit"], COMMIT)
                self.assertEqual(request.call_args_list, [
                    call(f"/repos/{REPO}/pages"), call(BUILDS, "POST"), call(path), call(path),
                ])

    def test_rejects_unexpected_build_urls_before_polling(self):
        api = approved_book.GitHub(REPO, "fixture")
        for url in (None, f"http://api.github.com{BUILDS}/latest", f"https://example.com{BUILDS}/latest",
                    "https://api.github.com/repos/other/book/pages/builds/latest",
                    f"{BUILDS_URL}/latest/", f"{BUILDS_URL}/latest-extra",
                    f"{BUILDS_URL}/latest?foo=1", f"{BUILDS_URL}/latest#fragment",
                    f"{BUILDS_URL}/latest?", f"{BUILDS_URL}/latest#"):
            with self.subTest(url=url), patch.object(api, "request", side_effect=[SOURCE, {"url": url}]):
                with self.assertRaisesRegex(approved_book.PolicyError, "unexpected build URL"):
                    publish_pages.request_build(api, COMMIT)

    def test_wrong_source_commit_failure_and_timeout_are_errors(self):
        api = approved_book.GitHub(REPO, "fixture")
        with patch.object(api, "request", side_effect=[{"build_type": "workflow"}]):
            with self.assertRaises(approved_book.PolicyError):
                publish_pages.request_build(api, COMMIT)
        for build, message in (({"status": "built", "commit": "b" * 40}, "different commit"),
                               ({"status": "errored", "error": {"message": "failed"}}, "build failed"),
                               ({"status": "building"}, "timeout")):
            with self.subTest(build=build), patch.object(api, "request", side_effect=[
                SOURCE, {"url": f"{BUILDS_URL}/latest"}, build,
            ]):
                with self.assertRaisesRegex(approved_book.PolicyError, message):
                    publish_pages.request_build(api, COMMIT, attempts=1)


if __name__ == "__main__":
    unittest.main()
