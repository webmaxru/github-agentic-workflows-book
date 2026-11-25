import unittest
from unittest.mock import patch

from helpers import ROOT

import approved_book
import publish_pages

REPO = "webmaxru/github-agentic-workflows-book"
COMMIT = "a" * 40


class PagesTests(unittest.TestCase):
    def test_build_requests_and_checks_exact_legacy_commit(self):
        api = approved_book.GitHub(REPO, "fixture")
        source = {"build_type": "legacy", "source": {"branch": "gh-pages", "path": "/"}}
        url = f"https://api.github.com/repos/{REPO}/pages/builds/42"
        with patch.object(api, "request", return_value={"url": url}) as post, \
                patch.object(api, "get", side_effect=[source, {"status": "building"},
                                                     {"status": "built", "commit": COMMIT}]), \
                patch.object(publish_pages.time, "sleep"):
            result = publish_pages.request_build(api, COMMIT, sleep=lambda _: None)
            self.assertEqual(result["commit"], COMMIT)
            post.assert_called_once_with(f"/repos/{REPO}/pages/builds", "POST")

    def test_wrong_source_url_commit_failure_and_timeout_are_errors(self):
        api = approved_book.GitHub(REPO, "fixture")
        source = {"build_type": "legacy", "source": {"branch": "gh-pages", "path": "/"}}
        with patch.object(api, "get", return_value={"build_type": "workflow"}):
            with self.assertRaises(approved_book.PolicyError):
                publish_pages.request_build(api, COMMIT)
        with patch.object(api, "get", return_value=source), \
                patch.object(api, "request", return_value={"url": "https://evil.example/x"}):
            with self.assertRaises(approved_book.PolicyError):
                publish_pages.request_build(api, COMMIT)
        url = f"https://api.github.com/repos/{REPO}/pages/builds/42"
        for build in ({"status": "built", "commit": "b" * 40},
                      {"status": "errored", "error": {"message": "failed"}},
                      {"status": "building"}):
            with self.subTest(build=build), patch.object(api, "request", return_value={"url": url}), \
                    patch.object(api, "get", side_effect=[source, build]):
                with self.assertRaises(approved_book.PolicyError):
                    publish_pages.request_build(api, COMMIT, attempts=1)


if __name__ == "__main__":
    unittest.main()
