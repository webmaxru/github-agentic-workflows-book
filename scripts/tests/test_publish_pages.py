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
QUEUED = {"url": f"{BUILDS_URL}/latest", "status": "queued"}


def build(commit, status, message=None):
    return {"commit": commit, "status": status, "error": {"message": message}}


class PagesTests(unittest.TestCase):
    def run_build(self, polls, *, attempts=60, response=QUEUED, commit=COMMIT):
        api = approved_book.GitHub(REPO, "fixture")
        sleeps = []
        with patch.object(api, "request", side_effect=[SOURCE, response, *polls]) as request:
            try:
                return publish_pages.request_build(api, commit, sleep=sleeps.append, attempts=attempts)
            finally:
                self.calls, self.sleeps = request.call_args_list, sleeps

    def test_ignores_the_post_response_and_polls_only_the_trusted_build_list(self):
        for response in (
            QUEUED, {"url": f"{BUILDS_URL}/42"}, {}, {"url": None},
            {"url": "https://api.github.com/repositories/1/pages/builds/latest"},
            {"url": "https://api.github.com/repos/other/book/pages/builds/latest"},
            {"url": f"https://evil.example{BUILDS}/latest?x=1#y"}, [], "", None,
        ):
            with self.subTest(response=response):
                polls = [[build(OTHER, "built")], [build(COMMIT, "built"), build(OTHER, "built")]]
                result = self.run_build(polls, response=response)
                self.assertEqual(result, build(COMMIT, "built"))
                self.assertEqual(self.calls, [
                    call(f"/repos/{REPO}/pages"), call(BUILDS, "POST"), call(LIST), call(LIST),
                ])
                self.assertEqual(self.sleeps, [10])

    def test_post_response_claiming_success_is_not_trusted(self):
        claimed = {"url": "https://evil.example/build", "status": "built", "commit": COMMIT}
        with self.assertRaisesRegex(approved_book.PolicyError, "timeout.*last status: not seen"):
            self.run_build([[build(OTHER, "built")]] * 2, attempts=2, response=claimed)
        self.assertEqual(self.calls[2:], [call(LIST), call(LIST)])

    def test_post_failure_propagates_before_polling(self):
        api = approved_book.GitHub(REPO, "fixture")
        failure = approved_book.GitHubError("GitHub API POST failed: HTTP Error 403")
        with patch.object(api, "request", side_effect=[SOURCE, failure]) as request:
            with self.assertRaisesRegex(approved_book.GitHubError, "POST failed"):
                publish_pages.request_build(api, COMMIT, sleep=self.fail)
        self.assertEqual(request.call_args_list, [call(f"/repos/{REPO}/pages"), call(BUILDS, "POST")])

    def test_rejects_non_exact_commit_before_any_request(self):
        for commit in ("", "main", "A" * 40, "a" * 39, "a" * 41, COMMIT + "\n"):
            with self.subTest(commit=commit):
                api = approved_book.GitHub(REPO, "fixture")
                with patch.object(api, "request") as request:
                    with self.assertRaisesRegex(approved_book.PolicyError, "exact gh-pages commit SHA"):
                        publish_pages.request_build(api, commit)
                request.assert_not_called()

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
             r"timeout.*last error: Page build failed\."),
            ("exact cancelled without message", [build(COMMIT, "cancelled")], r"timeout.*last error: build cancelled"),
            ("exact failed with malformed error", [{"commit": COMMIT, "status": "failed", "error": "x"}],
             r"timeout.*last error: build failed"),
            ("other commits only", [build(OTHER, "built"), build(OTHER, "errored", "x")], r"last status: not seen"),
            ("exact still building", [build(COMMIT, "building"), build(OTHER, "built")], r"last status: building"),
        ):
            with self.subTest(name):
                with self.assertRaisesRegex(approved_book.PolicyError, message):
                    self.run_build([page] * 3, attempts=3)
                self.assertEqual(self.sleeps, [10, 10])

    def test_timeout_retains_last_error_after_newer_build_starts(self):
        errored = build(COMMIT, "errored", "Page build failed.")
        queued = build(COMMIT, "queued")
        building = build(COMMIT, "building")
        for name, polls, message in (
            ("error then new build", [[errored], [queued], [building]], "Page build failed."),
            ("error behind new build", [[queued, errored], [building], [building]], "Page build failed."),
            ("later exact error", [[errored], [build(COMMIT, "failed", "Retry failed.")], [building]],
             "Retry failed."),
            ("unrelated error", [[errored], [building, build(OTHER, "errored", "Other failure.")], [building]],
             "Page build failed."),
        ):
            with self.subTest(name):
                with self.assertRaisesRegex(approved_book.PolicyError, "timeout") as error:
                    self.run_build(polls, attempts=3)
                self.assertIn("last status: building", str(error.exception))
                self.assertIn(f"last error: {message}", str(error.exception))
                self.assertEqual(self.sleeps, [10, 10])
                self.assertEqual(self.calls.count(call(LIST)), 3)

    def test_wrong_source_and_malformed_build_list_are_errors(self):
        api = approved_book.GitHub(REPO, "fixture")
        with patch.object(api, "request", side_effect=[{"build_type": "workflow"}]):
            with self.assertRaises(approved_book.PolicyError):
                publish_pages.request_build(api, COMMIT)
        for page in ({"message": "Not Found"}, None, "built", {"commit": COMMIT, "status": "built"}):
            with self.subTest(page=page):
                with self.assertRaisesRegex(approved_book.PolicyError, "unexpected build list"):
                    self.run_build([page])
        junk = [None, "built", [COMMIT, "built"], {"commit": COMMIT}, {"commit": COMMIT.upper(), "status": "built"}]
        self.assertEqual(self.run_build([junk, [*junk, build(COMMIT, "built")]]), build(COMMIT, "built"))
        with self.assertRaisesRegex(approved_book.GitHubError, "GET failed"):
            self.run_build([approved_book.GitHubError("GitHub API GET failed")])


if __name__ == "__main__":
    unittest.main()
