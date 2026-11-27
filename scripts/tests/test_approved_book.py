import contextlib
import base64
import io
import json
import os
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from helpers import ROOT

import approved_book as policy

HEAD = "a" * 40
BASE = "b" * 40
MERGE = "c" * 40
PR_MERGE = "d" * 40
TREE = "e" * 40
REPO = "webmaxru/github-agentic-workflows-book"


class ApiFixture(unittest.TestCase):
    """A fake repository served as API routes; tests mutate the attributes between calls."""

    def setUp(self):
        scratch = ROOT.parent / "build" / "tests"
        scratch.mkdir(parents=True, exist_ok=True)
        directory = TemporaryDirectory(prefix="approval-", dir=scratch)
        self.addCleanup(directory.cleanup)
        self.summary = Path(directory.name) / "summary.md"
        self.pr = {
            "number": 7, "state": "open", "draft": False, "changed_files": 2, "mergeable": True,
            "user": {"login": "webmaxru"},
            "head": {"sha": HEAD, "repo": {"full_name": REPO}},
            "base": {"sha": BASE, "ref": "main"}, "merge_commit_sha": PR_MERGE,
        }
        self.files = [{"filename": "content/chapters/one.html"},
                      {"filename": "content/VERSION"}]
        self.comments = [{"id": 1, "user": {"login": "webmaxru"}, "body": "/release-book " + HEAD,
                          "created_at": "2026-01-02T00:00:00Z", "updated_at": "2026-01-02T00:00:00Z"}]
        self.review = [{"id": 1, "user": {"login": "webmaxru"}, "state": "APPROVED",
                        "commit_id": HEAD, "submitted_at": "2026-01-02T00:00:00Z"}]
        self.timeline = []
        self.check = {"id": 1, "name": "Book release preflight", "status": "completed",
                      "conclusion": "success", "app": {"slug": "github-actions"}}
        self.version = "1.2"
        self.releases = [{"tag_name": "content-v1.1", "draft": False, "prerelease": False}]
        self.main = BASE
        self.compare_status = "ahead"
        self.test_merge_parents = [BASE, HEAD]
        self.merge_parents = [BASE]
        self.merge_tree = TREE
        self.reject_merge = False
        self.reads = []
        self.writes = []

    def routes(self):
        content = base64.b64encode(f"{self.version}\n".encode()).decode()
        return {
            "pulls": [self.pr],
            "pulls/7": self.pr, "pulls/7/files": self.files, "pulls/7/reviews": self.review,
            "issues/7/comments": self.comments, "issues/7/timeline": self.timeline,
            "contents/content/VERSION": {"encoding": "base64", "content": content},
            "releases": self.releases,
            "git/ref/heads/main": {"object": {"sha": self.main}},
            f"compare/{self.main}...{HEAD}": {"status": self.compare_status},
            f"commits/{PR_MERGE}": {"parents": [{"sha": s} for s in self.test_merge_parents]},
            f"git/commits/{HEAD}": {"tree": {"sha": TREE}, "parents": [{"sha": BASE}]},
            f"git/commits/{MERGE}": {"tree": {"sha": self.merge_tree},
                                     "parents": [{"sha": s} for s in self.merge_parents]},
            f"commits/{HEAD}/check-runs": {"check_runs": [self.check]},
            f"commits/{HEAD}/statuses": [],
            f"commits/{PR_MERGE}/check-runs": {"check_runs": []},
            f"commits/{PR_MERGE}/statuses": [],
        }

    def api_request(self, path, method="GET", data=None, missing=False):
        route = path.split("?", 1)[0].split(f"/repos/{REPO}/", 1)[1]
        if method != "GET":
            if route == "pulls/7/merge" and self.reject_merge:
                raise policy.GitHubError("GitHub API PUT failed: HTTP Error 409", 409)
            self.writes.append((method, route, data))
            return {"merged": True, "sha": MERGE} if route == "pulls/7/merge" else {}
        self.reads.append(route)
        payload = self.routes().get(route)
        if payload is None and missing:
            return None
        if payload is None:
            self.fail(f"unexpected route {route}")
        return deepcopy(payload)

    def cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", ["approved_book.py", *args]), \
                patch.dict(os.environ, {"GITHUB_REPOSITORY": REPO, "GH_TOKEN": "fixture",
                                        "GITHUB_STEP_SUMMARY": str(self.summary)}), \
                patch.object(policy.GitHub, "request", self.api_request), \
                patch.object(policy.time, "sleep"), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = policy.main()
        return code, out.getvalue(), err.getvalue()

    def merged(self):
        self.pr.update(state="closed", merged=True, merge_commit_sha=MERGE)

    def eligible(self):
        api = policy.GitHub(REPO, "fixture")
        with patch.object(api, "request", self.api_request):
            return api.inspect(self.pr["number"])


class AuthorizationTests(ApiFixture):
    def test_owner_command_must_be_exact_current_and_from_owner(self):
        self.assertEqual(self.eligible()["head"], HEAD)
        command = self.comments[0]["body"]
        for body in ("/release-book " + "b" * 40, "/release-book " + HEAD[:12],
                     "/release-book " + HEAD.upper(), "please " + command, command + " now",
                     " " + command, command + " ", command + "\n", "/release-book  " + HEAD):
            self.comments[0]["body"] = body
            with self.subTest(body=body), self.assertRaises(policy.PolicyError):
                self.eligible()
        self.comments[0]["body"] = "/release-book " + HEAD
        self.comments[0]["user"]["login"] = "other"
        with self.assertRaises(policy.PolicyError):
            self.eligible()

    def test_other_comments_do_not_revoke_an_independently_valid_command(self):
        stamp = "2026-01-03T00:00:00Z"
        later = {**self.comments[0], "id": 2, "created_at": stamp, "updated_at": stamp}
        for body in ("Thanks!", "/release-book later", "/release-book " + "e" * 40):
            with self.subTest(body=body):
                self.comments[1:] = [{**later, "body": body}]
                self.assertEqual(self.eligible()["head"], HEAD)
        self.comments[1:] = [{**later, "updated_at": "2026-01-04T00:00:00Z"}]
        self.assertEqual(self.eligible()["head"], HEAD)
        del self.comments[0]
        with self.assertRaises(policy.PolicyError):
            self.eligible()

    def test_owner_cannot_self_review(self):
        self.comments.clear()
        with self.assertRaises(policy.PolicyError):
            self.eligible()

    def test_edited_or_deleted_command_is_revoked(self):
        self.comments[0]["updated_at"] = "2026-01-02T00:05:00Z"
        with self.assertRaises(policy.PolicyError):
            self.eligible()
        self.comments.clear()
        with self.assertRaises(policy.PolicyError):
            self.eligible()

    def test_non_owner_never_authorizes(self):
        self.pr["user"]["login"] = "book-bot"
        self.review[0]["user"]["login"] = "someone-else"
        with self.assertRaises(policy.PolicyError):
            self.eligible()
        self.review[0]["user"]["login"] = "webmaxru"
        self.assertEqual(self.eligible()["head"], HEAD)
        self.pr["user"]["login"] = "webmaxru"
        self.comments[0]["user"]["login"] = "someone-else"
        with self.assertRaises(policy.PolicyError):
            self.eligible()

    def test_non_author_approval_is_latest_and_bound_to_head(self):
        self.pr["user"]["login"] = "book-bot"
        self.assertEqual(self.eligible()["head"], HEAD)
        # A push after approval changes the head; the approval no longer matches it.
        self.pr["head"]["sha"] = "f" * 40
        with self.assertRaises(policy.PolicyError):
            self.eligible()
        self.pr["head"]["sha"] = HEAD
        self.review.append({**self.review[0], "id": 2, "state": "DISMISSED",
                            "submitted_at": "2026-01-03T00:00:00Z"})
        with self.assertRaises(policy.PolicyError):
            self.eligible()
        self.review[-1]["state"] = "APPROVED"
        self.review[-1]["commit_id"] = "f" * 40
        with self.assertRaises(policy.PolicyError):
            self.eligible()

    def test_owner_comment_review_neither_revokes_nor_grants_approval(self):
        self.pr["user"]["login"] = "book-bot"
        self.review.append({**self.review[0], "id": 2, "state": "COMMENTED",
                            "submitted_at": "2026-01-03T00:00:00Z"})
        self.assertEqual(self.eligible()["head"], HEAD)
        for state in ("CHANGES_REQUESTED", "DISMISSED"):
            self.review[0]["state"] = state
            with self.subTest(state=state), self.assertRaises(policy.PolicyError):
                self.eligible()
        del self.review[0]
        with self.assertRaises(policy.PolicyError):
            self.eligible()

    def test_changes_requested_is_a_barrier_for_both_authorization_paths(self):
        later = {"id": 9, "user": {"login": "reviewer"}, "state": "CHANGES_REQUESTED",
                 "commit_id": HEAD, "submitted_at": "2026-01-03T00:00:00Z"}
        # The owner's command predates the change request.
        self.review.append(later)
        with self.assertRaises(policy.PolicyError):
            self.eligible()
        # A fresh command after the change request authorizes again.
        self.comments.append({"id": 2, "user": {"login": "webmaxru"}, "body": "/release-book " + HEAD,
                              "created_at": "2026-01-04T00:00:00Z", "updated_at": "2026-01-04T00:00:00Z"})
        self.assertEqual(self.eligible()["head"], HEAD)
        # Someone else's PR: an approval before the change request is revoked, a newer one is not.
        self.pr["user"]["login"] = "book-bot"
        self.review.pop(0)
        self.review.insert(0, {"id": 1, "user": {"login": "webmaxru"}, "state": "APPROVED",
                               "commit_id": HEAD, "submitted_at": "2026-01-02T00:00:00Z"})
        with self.assertRaises(policy.PolicyError):
            self.eligible()
        self.review.append({"id": 10, "user": {"login": "webmaxru"}, "state": "APPROVED",
                            "commit_id": HEAD, "submitted_at": "2026-01-05T00:00:00Z"})
        self.assertEqual(self.eligible()["head"], HEAD)

    def test_dismissed_review_is_a_barrier(self):
        self.pr["user"]["login"] = "book-bot"
        self.timeline.append({"event": "review_dismissed", "created_at": "2026-01-03T00:00:00Z"})
        with self.assertRaises(policy.PolicyError):
            self.eligible()
        self.timeline[0]["created_at"] = "2026-01-01T00:00:00Z"
        self.assertEqual(self.eligible()["head"], HEAD)
        self.pr["user"]["login"] = "webmaxru"
        self.timeline[0]["created_at"] = "2026-01-03T00:00:00Z"
        with self.assertRaises(policy.PolicyError):
            self.eligible()


class EligibilityTests(ApiFixture):
    def test_rejects_mixed_infra_renames_and_non_content(self):
        for filename in (".github/workflows/release.yml", "scripts/build_pdf.py",
                         "site/generate.py", "site/assets/app.js", "package.json"):
            self.files[1]["filename"] = filename
            with self.subTest(filename=filename), self.assertRaises(policy.PolicyError):
                self.eligible()
        self.files[1] = {"filename": "content/VERSION", "previous_filename": "scripts/old.py"}
        with self.assertRaises(policy.PolicyError):
            self.eligible()
        self.files = [{"filename": "content/VERSION"}, {"filename": "content/CHANGELOG.md"}]
        with self.assertRaises(policy.PolicyError):
            self.eligible()

    def test_requires_an_open_non_draft_same_repo_mergeable_pr_against_main(self):
        original_pr, original_files = self.pr, self.files
        for key in ("draft", "fork", "partial", "wrong_base", "closed", "conflicting", "unknown"):
            self.pr, self.files = pr, files = deepcopy(original_pr), deepcopy(original_files)
            if key == "draft":
                pr["draft"] = True
            elif key == "fork":
                pr["head"]["repo"]["full_name"] = "other/book"
            elif key == "partial":
                files.pop()
            elif key == "wrong_base":
                pr["base"]["ref"] = "other"
            elif key == "closed":
                pr["state"] = "closed"
            elif key == "conflicting":
                pr["mergeable"] = False
            else:
                pr["mergeable"] = None
            with self.subTest(key=key), patch.object(policy.time, "sleep"), self.assertRaises(policy.PolicyError):
                self.eligible()

    def test_mergeability_is_retried_while_github_computes_it(self):
        self.pr["mergeable"] = None
        with patch.object(policy.time, "sleep", side_effect=lambda _: self.pr.update(mergeable=True)) as sleep:
            self.assertEqual(self.eligible()["head"], HEAD)
        sleep.assert_called_once_with(2)

    def test_checks_must_be_completed_successful_and_from_actions(self):
        policy.checks_pass([self.check], [])
        for change in ({"conclusion": "failure"}, {"status": "in_progress"},
                       {"app": {"slug": "other"}}):
            check = {**self.check, **change}
            with self.subTest(change=change), self.assertRaises(policy.PolicyError):
                policy.checks_pass([check], [])
        with self.assertRaises(policy.PolicyError):
            policy.checks_pass([], [])
        with self.assertRaises(policy.PolicyError):
            policy.checks_pass([self.check, {"id": 2, "name": "security",
                                "status": "completed", "conclusion": "failure"}], [])
        with self.assertRaises(policy.PolicyError):
            policy.checks_pass([self.check,
                                {"id": 2, "name": "security", "status": "completed",
                                 "conclusion": "failure", "app": {"id": 1}},
                                {"id": 3, "name": "security", "status": "completed",
                                 "conclusion": "success", "app": {"id": 2}}], [])
        with self.assertRaises(policy.PolicyError):
            policy.checks_pass([self.check], [{"context": "ci", "state": "pending"}])

    def test_preflight_must_be_green_on_the_exact_head(self):
        self.check["conclusion"] = "failure"
        code, _, err = self.cli("select", "--number", "7")
        self.assertEqual(code, 1)
        self.assertIn("Book release preflight", err)
        self.check.update(conclusion="success", status="in_progress")
        self.assertEqual(self.cli("select", "--number", "7")[0], 1)
        self.check.update(status="completed")
        self.assertEqual(self.cli("select", "--number", "7")[0], 0)

    def test_head_must_contain_the_current_main(self):
        self.assertEqual(self.cli("select", "--number", "7")[0], 0)
        for status in ("behind", "diverged"):
            self.compare_status = status
            with self.subTest(status=status):
                code, _, err = self.cli("select", "--number", "7")
                self.assertEqual(code, 1)
                self.assertIn("does not contain the current main", err)
        self.compare_status = "identical"
        self.assertEqual(self.cli("select", "--number", "7")[0], 0)
        # main moved after GitHub last computed the PR base: also not eligible.
        self.compare_status = "ahead"
        self.main = "9" * 40
        code, _, err = self.cli("select", "--number", "7")
        self.assertEqual(code, 1)
        self.assertIn(f"its base {BASE[:12]} is behind main {self.main[:12]}", err)

    def test_stale_base_is_reported_before_remaining_validation(self):
        self.main = "9" * 40
        message = (f"PR #7: approved, but its base {BASE[:12]} is behind main {self.main[:12]}; "
                   "update the branch from main, then approve the new head.")
        for args in ((), ("--number", "7")):
            with self.subTest(args=args):
                self.summary.write_text("Existing summary\n\n", encoding="utf-8")
                self.reads.clear()
                code, out, err = self.cli("select", *args)
                self.assertEqual(code, 1 if args else 0, err)
                self.assertEqual(out, "" if args else "{}\n")
                self.assertEqual(err.count("::warning::"), 1)
                self.assertIn("::warning::" + message, err)
                self.assertEqual(self.summary.read_text(encoding="utf-8"),
                                 "Existing summary\n\n" + message + "\n\n")
                self.assertNotIn(f"commits/{PR_MERGE}", self.reads)
                self.assertNotIn("releases", self.reads)
                self.assertNotIn("contents/content/VERSION", self.reads)
                self.assertEqual(self.writes, [])

    def test_stale_warning_requires_current_approval_and_green_preflight(self):
        self.main = "9" * 40
        for missing in ("approval", "preflight"):
            with self.subTest(missing=missing):
                if missing == "approval":
                    self.comments[0]["body"] = "/release-book " + "f" * 40
                else:
                    self.comments[0]["body"] = "/release-book " + HEAD
                    self.check["conclusion"] = "failure"
                code, out, err = self.cli("select")
                self.assertEqual((code, json.loads(out)), (0, {}))
                self.assertIn(missing, err)
                self.assertNotIn("::warning::", err)
                self.assertFalse(self.summary.exists())
                self.assertNotIn("git/ref/heads/main", self.reads)
                self.assertEqual(self.writes, [])

    def test_a_stale_pr_is_never_merged(self):
        self.compare_status = "behind"
        code, _, _ = self.cli("merge", "--number", "7", "--head", HEAD, "--base", BASE,
                              "--comparison", "content-v1.1")
        self.assertEqual(code, 1)
        self.assertFalse(self.writes)

    def test_pr_test_merge_must_match_base_and_head(self):
        self.test_merge_parents[0] = "f" * 40
        self.assertEqual(self.cli("select", "--number", "7")[0], 1)

    def test_scan_skips_ineligible_prs_and_selects_the_first_eligible(self):
        other = deepcopy(self.pr)
        other.update(number=8, draft=True)
        routes = self.routes

        def with_scan():
            table = routes()
            table["pulls"] = [other, self.pr]
            table["pulls/8"] = other
            table["pulls/8/files"] = self.files
            table["pulls/8/reviews"] = self.review
            table["issues/8/comments"] = self.comments
            table["issues/8/timeline"] = []
            return table

        with patch.object(self, "routes", with_scan):
            code, out, err = self.cli("select")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["number"], 7)
        self.assertIn("PR #8", err)


class ScopeSelectionTests(ApiFixture):
    def assert_scope_skip(self, reason, *, targeted=True, signal=None, warn=None, signal_reads=()):
        warn = targeted if warn is None else warn
        self.pr["changed_files"] = len(self.files)
        self.summary.write_text("Earlier step\n\n", encoding="utf-8")
        with patch.dict(os.environ, {"OWNER_REVIEW_SIGNAL": signal or ""}):
            result = self.cli("select", *(("--number", "7") if targeted else ()))
        expected_log = f"::warning::{reason}" if warn else f"PR #7: {reason}"
        self.assertEqual(result, (0, "{}\n", expected_log + "\n"))
        self.assertEqual(self.summary.read_text(encoding="utf-8"),
                         "Earlier step\n\n" + (reason + "\n\n" if warn else ""))
        allowed_reads = {"pulls/7", "pulls/7/files", *signal_reads}
        if not targeted and not warn:
            allowed_reads.add("pulls")
        if "pulls/7/reviews" in signal_reads:
            self.assertLess(self.reads.index("pulls/7/files"), self.reads.index("pulls/7/reviews"))
        self.assertEqual(set(self.reads), allowed_reads)
        self.assertEqual(self.writes, [])

    def test_explicit_tooling_only_is_a_warning_not_a_failure(self):
        self.pr["mergeable"] = None
        self.files = [{"filename": p} for p in
                      ("RELEASING.md", "scripts/one.py", "scripts/two.py", "a", "b", "c")]
        self.assert_scope_skip(
            "PR #7 is tooling-only (no book content changed: RELEASING.md, scripts/one.py, scripts/two.py, a, b); "
            "the release controller never merges or releases tooling PRs. Merge it yourself once its checks are green.")

    def test_explicit_mixed_includes_non_allowlisted_side_of_rename(self):
        self.pr["mergeable"] = False
        self.files = [{"filename": "content/VERSION", "previous_filename": "scripts/old.py"}]
        self.assert_scope_skip("PR #7 mixes book content with tooling (scripts/old.py); split it: "
                               "merge the tooling PR yourself, then authorize the content PR.")

    def test_scan_skips_tooling_only_quietly(self):
        self.files = [{"filename": "RELEASING.md"}]
        self.assert_scope_skip(
            "PR #7 is tooling-only (no book content changed: RELEASING.md); the release controller never "
            "merges or releases tooling PRs. Merge it yourself once its checks are green.", targeted=False)

    def test_only_a_current_owner_approval_signal_warns(self):
        self.pr["user"]["login"] = "book-bot"
        self.files[1] = {"filename": "scripts/build.py"}
        reason = ("PR #7 mixes book content with tooling (scripts/build.py); split it: "
                  "merge the tooling PR yourself, then authorize the content PR.")
        cases = (
            ("Owner approval for PR 7 review 1", {}, True),
            ("Owner approval for PR 7 review 1", {"commit_id": "f" * 40}, False),
            ("Owner approval for PR 7 review 1", {"state": "DISMISSED"}, False),
            ("Owner approval for PR 7 review 1", {"user": {"login": "contributor"}}, False),
            ("Owner approval for PR 7 review 1", {"id": 2}, False),
        )
        for signal, review, warn in cases:
            with self.subTest(signal=signal, review=review), patch.dict(self.review[0], review):
                self.reads.clear()
                self.assert_scope_skip(reason, targeted=False, signal=signal, warn=warn,
                                       signal_reads=("pulls/7/reviews", "issues/7/timeline"))
        for signal, reads in (("Owner approval for PR 8 review 1", ("pulls/8",)), ("Book review signal", ())):
            with self.subTest(signal=signal):
                self.reads.clear()
                self.assert_scope_skip(reason, targeted=False, signal=signal, warn=False, signal_reads=reads)

    def test_explicit_recovery_and_content_only_refusals_are_still_errors(self):
        self.files = [{"filename": "site/index.html"}, {"filename": "content/VERSION"}]
        self.assertEqual(self.cli("select", "--number", "7"),
                         (1, "", "ERROR: PR does not change a chapter or TOC.\n"))
        self.merged()
        self.files = [{"filename": "README.md"}, {"filename": "RELEASING.md"}]
        code, out, err = self.cli("select", "--number", "7")
        self.assertEqual((code, out), (1, ""))
        self.assertTrue(err.startswith("ERROR: "), err)
        self.assertEqual(self.writes, [])


class PublishedBaselineTests(ApiFixture):
    def test_published_baseline_and_recovery(self):
        api = policy.GitHub(REPO, "fixture")
        blob = {"encoding": "base64", "content": base64.b64encode(b"1.2\n").decode()}
        releases = [
            {"tag_name": "content-v1.0", "draft": False, "prerelease": False},
            {"tag_name": "content-v1.1", "draft": False, "prerelease": False},
            {"tag_name": "content-v1.3", "draft": True, "prerelease": False},
        ]
        with patch.object(api, "get", return_value=blob), patch.object(api, "pages", return_value=releases):
            self.assertEqual(api.previous_edition(HEAD), "content-v1.1")
            releases.append({"tag_name": "content-v1.2", "draft": False, "prerelease": False})
            with self.assertRaises(policy.PolicyError):
                api.previous_edition(HEAD)
            self.assertEqual(api.previous_edition(HEAD, merged=True), "content-v1.1")
            releases.append({"tag_name": "content-v1.3", "draft": False, "prerelease": False})
            self.assertEqual(api.previous_edition(HEAD, merged=True), "content-v1.1")
            releases[-2]["tag_name"] = "content-v1.2.1"
            with self.assertRaises(policy.PolicyError):
                api.previous_edition(HEAD, merged=True)

    def test_pagination_fetches_every_page(self):
        api = policy.GitHub(REPO, "fixture")
        with patch.object(api, "get", side_effect=[list(range(100)), [100]]) as get:
            self.assertEqual(len(api.pages("pulls/7/files")), 101)
            self.assertEqual(get.call_count, 2)

    def test_api_base_url_comes_from_the_runner_environment(self):
        with patch.dict(os.environ, {"GITHUB_API_URL": "http://127.0.0.1:1/"}):
            self.assertEqual(policy.GitHub(REPO, "fixture").api_url, "http://127.0.0.1:1")


class MergeAndDispatchTests(ApiFixture):
    def merge(self, head=HEAD, base=BASE, comparison="content-v1.1"):
        return self.cli("merge", "--number", "7", "--head", head, "--base", base,
                        "--comparison", comparison)

    def test_squash_merge_is_conditioned_on_the_exact_approved_head(self):
        code, out, _ = self.merge()
        self.assertEqual(code, 0)
        self.assertEqual(self.writes, [("PUT", "pulls/7/merge", {"sha": HEAD, "merge_method": "squash"})])
        result = json.loads(out)
        self.assertEqual((result["merge_sha"], result["tag"]), (MERGE, "content-v1.2"))

    def test_merge_refuses_when_anything_moved_after_preflight(self):
        self.assertEqual(self.merge(head="f" * 40)[0], 1)
        self.assertEqual(self.merge(base="f" * 40)[0], 1)
        self.assertEqual(self.merge(comparison="content-v1.0")[0], 1)
        self.assertEqual(self.cli("merge", "--number", "7")[0], 1)
        self.assertFalse(self.writes)

    def test_merge_refuses_without_approval_and_after_a_revoking_review(self):
        self.review.append({"id": 3, "user": {"login": "reviewer"}, "state": "CHANGES_REQUESTED",
                            "commit_id": HEAD, "submitted_at": "2026-01-03T00:00:00Z"})
        self.assertEqual(self.merge()[0], 1)
        self.assertFalse(self.writes)

    def test_github_refusing_the_head_precondition_is_an_error(self):
        self.reject_merge = True
        self.assertEqual(self.merge()[0], 1)
        self.assertFalse(self.writes)

    def test_merge_must_be_a_squash_of_the_approved_head(self):
        self.merge_parents = [BASE, HEAD]
        self.assertEqual(self.merge()[0], 1)
        self.merge_parents, self.merge_tree = [BASE], "0" * 40
        self.assertEqual(self.merge()[0], 1)

    def test_dispatch_starts_release_with_the_five_inputs_on_main(self):
        code, out, _ = self.cli("dispatch", "--number", "7", "--head", HEAD, "--base", BASE,
                                "--merge-sha", MERGE, "--tag", "content-v1.2")
        self.assertEqual(code, 0)
        self.assertEqual(self.writes, [("POST", "actions/workflows/release.yml/dispatches", {
            "ref": "main",
            "inputs": {"pr": "7", "head_sha": HEAD, "base_sha": BASE,
                       "merge_sha": MERGE, "tag": "content-v1.2"}})])
        self.assertEqual(json.loads(out)["dispatched"], "release.yml")

    def test_dispatch_refuses_malformed_inputs(self):
        for args in (("--head", "abc", "--base", BASE, "--merge-sha", MERGE, "--tag", "content-v1.2"),
                     ("--head", HEAD, "--base", BASE, "--merge-sha", MERGE, "--tag", "v1.2"),
                     ("--head", HEAD, "--base", BASE, "--merge-sha", MERGE, "--tag", "main")):
            with self.subTest(args=args):
                self.assertEqual(self.cli("dispatch", "--number", "7", *args)[0], 1)
        self.assertFalse(self.writes)


class RecoveryTests(ApiFixture):
    def setUp(self):
        super().setUp()
        self.merged()

    def verify(self, **override):
        args = {"head": HEAD, "base": BASE, "merge-sha": MERGE, "tag": "content-v1.2", **override}
        flat = [item for key, value in args.items() for item in (f"--{key}", value)]
        return self.cli("verify-merged", "--number", "7", *flat)

    def test_select_recovers_a_merged_pr_with_its_original_base(self):
        code, out, _ = self.cli("select", "--number", "7")
        self.assertEqual(code, 0)
        selected = json.loads(out)
        self.assertEqual((selected["merge_sha"], selected["base"], selected["tag"],
                          selected["comparison"]), (MERGE, BASE, "content-v1.2", "content-v1.1"))

    def test_verify_merged_returns_the_comparison_baseline(self):
        code, out, _ = self.verify()
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["comparison"], "content-v1.1")

    def test_forged_or_mismatched_provenance_fails_without_writes(self):
        self.assertEqual(self.verify(**{"merge-sha": "e" * 40})[0], 1)
        self.assertEqual(self.verify(head="f" * 40)[0], 1)
        self.assertEqual(self.verify(base="f" * 40)[0], 1)
        self.assertEqual(self.verify(tag="content-v1.3")[0], 1)
        self.merge_parents = [BASE, HEAD]
        self.assertEqual(self.verify()[0], 1)
        self.merge_parents, self.merge_tree = [BASE], "0" * 40
        self.assertEqual(self.verify()[0], 1)
        self.merge_tree = TREE
        self.comments.clear()
        self.assertEqual(self.verify()[0], 1)
        self.assertFalse(self.writes)

    def test_an_unmerged_pr_is_not_a_release_source(self):
        self.pr.update(state="open", merged=False)
        self.assertEqual(self.verify()[0], 1)


class SeparateProcessTests(ApiFixture):
    def test_select_script_in_separate_process_with_api_fixtures(self):
        fixture = {"routes": self.routes(), "repo": REPO, "head": HEAD}
        bootstrap = r"""
import io, json, os, runpy, sys, urllib.parse, urllib.request
data = json.loads(os.environ["FIXTURE"])
class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): self.close()
def fake(request, timeout=30):
    path = urllib.parse.urlsplit(request.full_url).path.split("/repos/" + data["repo"] + "/", 1)[1]
    routes = data["routes"]
    if path.endswith("/check-runs") and data["head"] not in path:
        result = {"check_runs": []}
    elif path == "pulls":
        result = []
    else:
        result = routes[path]
    return Response(json.dumps(result).encode())
urllib.request.urlopen = fake
sys.argv = [sys.argv[1], "select", "--number", "7"]
runpy.run_path(sys.argv[0], run_name="__main__")
"""
        env = dict(os.environ, GITHUB_REPOSITORY=REPO, GH_TOKEN="fixture", FIXTURE=json.dumps(fixture))
        script = str(ROOT / "approved_book.py")
        result = subprocess.run([sys.executable, "-c", bootstrap, script], env=env,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["head"], HEAD)
        fixture["routes"]["issues/7/comments"][0]["body"] = "/release-book " + "f" * 40
        env["FIXTURE"] = json.dumps(fixture)
        result = subprocess.run([sys.executable, "-c", bootstrap, script], env=env,
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approval", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
