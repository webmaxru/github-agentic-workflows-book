import unittest
from unittest.mock import call, patch

from helpers import ROOT

import approved_book
import publish_pages

REPO = "webmaxru/github-agentic-workflows-book"
COMMIT = "a" * 40
OTHER = "b" * 40
SOURCE = {"build_type": "legacy", "source": {"branch": "gh-pages", "path": "/"}}
BUILDS = f"/repos/{REPO}/pages/builds"
BUILDS_URL = f"https://api.github.com{BUILDS}"
LIST = f"{BUILDS}?per_page=100"


def build(commit, status, message=None):
    return {"commit": commit, "status": status, "error": {"message": message}}


class PagesTests(unittest.TestCase):
    def run_build(self, polls, *, attempts=60, url=f"{BUILDS_URL}/latest"):
        api = approved_book.GitHub(REPO, "fixture")
        sleeps = []
        with patch.object(api, "request", side_effect=[SOURCE, {"url": url}, *polls]) as request:
            try:
                return publish_pages.request_build(api, COMMIT, sleep=sleeps.append, attempts=attempts)
            finally:
                self.calls, self.sleeps = request.call_args_list, sleeps

    def test_accepts_documented_build_urls_and_polls_the_build_list(self):
        for target in ("latest", "42"):
            with self.subTest(target=target):
                result = self.run_build([[], [build(COMMIT, "built")]], url=f"{BUILDS_URL}/{target}")
                self.assertEqual(result["commit"], COMMIT)
                self.assertEqual(self.calls, [
                    call(f"/repos/{REPO}/pages"), call(BUILDS, "POST"), call(LIST), call(LIST),
                ])
                self.assertEqual(self.sleeps, [10])

    def test_rejects_unexpected_build_urls_before_polling(self):
        for url in (None, f"http://api.github.com{BUILDS}/latest", f"https://example.com{BUILDS}/latest",
                    "https://api.github.com/repos/other/book/pages/builds/latest",
                    f"{BUILDS_URL}/latest/", f"{BUILDS_URL}/latest-extra",
                    f"{BUILDS_URL}/latest?foo=1", f"{BUILDS_URL}/latest#fragment",
                    f"{BUILDS_URL}/latest?", f"{BUILDS_URL}/latest#"):
            with self.subTest(url=url):
                with self.assertRaisesRegex(approved_book.PolicyError, "unexpected build URL"):
                    self.run_build([], url=url)

    def test_waits_past_stale_and_superseded_builds_for_the_exact_commit(self):
        superseded = build(COMMIT, "errored", "Page build failed.")
        stale = build(OTHER, "built")
        for name, polls in (
            ("stale latest", [[stale], [build(COMMIT, "building"), stale], [build(COMMIT, "built"), stale]]),
            ("errored then built", [[superseded, stale], [build(COMMIT, "built"), superseded, stale]]),
            ("observed run", [[build(COMMIT, "built"), superseded, stale]]),
        ):
            with self.subTest(name):
                self.assertEqual(self.run_build(polls), build(COMMIT, "built"))
                self.assertEqual(len(self.sleeps), len(polls) - 1)

    def test_fails_closed_only_at_timeout_and_never_for_other_commits(self):
        for name, page, message in (
            ("exact errored", [build(COMMIT, "errored", "Page build failed."), build(OTHER, "built")],
             r"Pages build failed: Page build failed\."),
            ("other commits only", [build(OTHER, "built"), build(OTHER, "errored", "x")], r"last status: not seen"),
            ("exact still building", [build(COMMIT, "building"), build(OTHER, "built")], r"last status: building"),
        ):
            with self.subTest(name):
                with self.assertRaisesRegex(approved_book.PolicyError, message):
                    self.run_build([page] * 3, attempts=3)
                self.assertEqual(self.sleeps, [10, 10])

    def test_wrong_source_and_malformed_build_list_are_errors(self):
        api = approved_book.GitHub(REPO, "fixture")
        with patch.object(api, "request", side_effect=[{"build_type": "workflow"}]):
            with self.assertRaises(approved_book.PolicyError):
                publish_pages.request_build(api, COMMIT)
        with self.assertRaisesRegex(approved_book.PolicyError, "unexpected build list"):
            self.run_build([{"message": "Not Found"}])


if __name__ == "__main__":
    unittest.main()
