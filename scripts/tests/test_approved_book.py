import contextlib
import base64
import io
import json
import os
import subprocess
import sys
import unittest
from copy import deepcopy
from unittest.mock import patch

from helpers import ROOT

import approved_book as policy

HEAD = "a" * 40
BASE = "b" * 40
MERGE = "c" * 40
PR_MERGE = "d" * 40
REPO = "webmaxru/github-agentic-workflows-book"


class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.pr = {
            "number": 7, "state": "open", "draft": False, "changed_files": 2,
            "user": {"login": "webmaxru"},
            "head": {"sha": HEAD, "repo": {"full_name": REPO}},
            "base": {"sha": BASE, "ref": "main"}, "merge_commit_sha": PR_MERGE,
        }
        self.files = [{"filename": "content/chapters/one.html"},
                      {"filename": "content/VERSION"}]
        self.comments = [{"id": 1, "user": {"login": "webmaxru"},
                          "body": "/release-book " + HEAD}]
        self.review = [{"id": 1, "user": {"login": "webmaxru"}, "state": "APPROVED",
                        "commit_id": HEAD, "submitted_at": "2026-01-01T00:00:00Z"}]
        self.check = {"id": 1, "name": "Book release preflight", "status": "completed",
                      "conclusion": "success", "app": {"slug": "github-actions"}}

    def eligible(self):
        return policy.eligibility(self.pr, self.files, self.review, self.comments, REPO)

    def test_owner_command_must_be_exact_current_and_from_owner(self):
        self.assertEqual(self.eligible()["head"], HEAD)
        for body in ("/release-book " + "b" * 40, "/release-book " + HEAD[:12],
                     "please /release-book " + HEAD):
            self.comments[0]["body"] = body
            with self.subTest(body=body), self.assertRaises(policy.PolicyError):
                self.eligible()
        self.comments[0]["body"] = "/release-book " + HEAD
        self.comments[0]["user"]["login"] = "other"
        with self.assertRaises(policy.PolicyError):
            self.eligible()

    def test_new_owner_command_supersedes_old_and_owner_cannot_self_review(self):
        self.comments.append({"id": 2, "user": {"login": "webmaxru"},
                              "body": "/release-book " + "e" * 40})
        with self.assertRaises(policy.PolicyError):
            self.eligible()
        self.comments.clear()
        with self.assertRaises(policy.PolicyError):
            self.eligible()

    def test_non_author_approval_is_latest_and_bound_to_head(self):
        self.pr["user"]["login"] = "book-bot"
        self.assertEqual(self.eligible()["head"], HEAD)
        self.review.append({**self.review[0], "id": 2, "state": "DISMISSED",
                            "submitted_at": "2026-01-02T00:00:00Z"})
        with self.assertRaises(policy.PolicyError):
            self.eligible()
        self.review[-1]["state"] = "APPROVED"
        self.review[-1]["commit_id"] = "f" * 40
        with self.assertRaises(policy.PolicyError):
            self.eligible()

    def test_rejects_mixed_infra_renames_forks_drafts_and_incomplete_pages(self):
        for filename in (".github/workflows/release.yml", "scripts/build_pdf.py",
                         "site/generate.py", "site/assets/app.js", "package.json"):
            self.files[1]["filename"] = filename
            with self.subTest(filename=filename), self.assertRaises(policy.PolicyError):
                self.eligible()
        self.files[1] = {"filename": "content/VERSION", "previous_filename": "scripts/old.py"}
        with self.assertRaises(policy.PolicyError):
            self.eligible()
        self.files[1] = {"filename": "content/VERSION"}
        for key in ("draft", "fork", "partial", "wrong_base"):
            pr = deepcopy(self.pr)
            files = deepcopy(self.files)
            if key == "draft":
                pr["draft"] = True
            elif key == "fork":
                pr["head"]["repo"]["full_name"] = "other/book"
            elif key == "partial":
                files.pop()
            else:
                pr["base"]["ref"] = "other"
            with self.subTest(key=key), self.assertRaises(policy.PolicyError):
                policy.eligibility(pr, files, self.review, self.comments, REPO)

    def test_checks_must_be_completed_successful_and_from_actions(self):
        policy.checks_pass([self.check], [])
        for change in ({"conclusion": "failure"}, {"status": "in_progress"},
                       {"app": {"slug": "other"}}):
            check = {**self.check, **change}
            with self.subTest(change=change), self.assertRaises(policy.PolicyError):
                policy.checks_pass([check], [])
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

    def test_cli_select_and_merge_enforce_head_and_base(self):
        writes = []
        pr = self.pr
        files = self.files
        comments = self.comments
        check = self.check

        test_merge_parents = [BASE, HEAD]

        def request(api, path, method="GET", data=None):
            if method == "PUT":
                writes.append(data)
                return {"merged": True, "sha": MERGE}
            route = path.split("?", 1)[0].split(f"/repos/{REPO}/", 1)[1]
            if route == "pulls/7":
                return pr
            if route == "pulls/7/files":
                return files
            if route == "pulls/7/reviews":
                return []
            if route == "issues/7/comments":
                return comments
            if route == "contents/content/VERSION":
                return {"encoding": "base64", "content": base64.b64encode(b"1.2\n").decode()}
            if route == "releases":
                return [{"tag_name": "content-v1.1", "draft": False, "prerelease": False}]
            if route.endswith("/check-runs"):
                return {"check_runs": [check] if HEAD in route else []}
            if route.endswith("/statuses"):
                return []
            if route == f"commits/{MERGE}":
                return {"parents": [{"sha": BASE}, {"sha": HEAD}]}
            if route == f"commits/{PR_MERGE}":
                return {"parents": [{"sha": sha} for sha in test_merge_parents]}
            self.fail(f"unexpected route {route}")

        def run(*args):
            out = io.StringIO()
            with patch.object(sys, "argv", ["approved_book.py", *args]), \
                    patch.dict(os.environ, {"GITHUB_REPOSITORY": REPO, "GH_TOKEN": "fixture"}), \
                    patch.object(policy.GitHub, "request", request), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = policy.main()
            return code, out.getvalue()

        code, output = run("select", "--number", "7")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["head"], HEAD)
        test_merge_parents[0] = "f" * 40
        self.assertEqual(run("select", "--number", "7")[0], 1)
        test_merge_parents[0] = BASE
        self.assertEqual(run("merge", "--number", "7", "--head", "f" * 40, "--base", BASE,
                             "--comparison", "content-v1.1")[0], 1)
        self.assertFalse(writes)
        self.assertEqual(run("merge", "--number", "7", "--head", HEAD, "--base", BASE,
                             "--comparison", "content-v1.0")[0], 1)
        self.assertFalse(writes)
        code, output = run("merge", "--number", "7", "--head", HEAD, "--base", BASE,
                           "--comparison", "content-v1.1")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["merge_sha"], MERGE)
        self.assertEqual(writes, [{"sha": HEAD, "merge_method": "merge"}])
        pr.update(state="closed", merged=True, merge_commit_sha=MERGE)
        code, output = run("select", "--number", "7")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["merge_sha"], MERGE)
        self.assertEqual(run("verify-merged", "--number", "7", "--merge-sha", MERGE,
                             "--base", BASE)[0], 0)
        self.assertEqual(run("verify-merged", "--number", "7", "--merge-sha", "e" * 40,
                             "--base", BASE)[0], 1)
        comments.clear()
        self.assertEqual(run("verify-merged", "--number", "7", "--merge-sha", MERGE,
                             "--base", BASE)[0], 1)
        self.assertEqual(len(writes), 1)

    def test_select_script_in_separate_process_with_api_fixtures(self):
        fixture = {
            "pr": self.pr, "files": self.files, "comments": self.comments,
            "checks": [self.check], "head": HEAD, "base": BASE, "repo": REPO,
        }
        bootstrap = r"""
import io, json, os, runpy, sys, urllib.parse, urllib.request
data = json.loads(os.environ["FIXTURE"])
class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): self.close()
def fake(request, timeout=30):
    path = urllib.parse.urlsplit(request.full_url).path.split("/repos/" + data["repo"] + "/", 1)[1]
    routes = {
        "pulls/7": data["pr"], "pulls/7/files": data["files"],
        "pulls/7/reviews": [], "issues/7/comments": data["comments"],
        "contents/content/VERSION": {"encoding": "base64", "content": "MS4yCg=="},
        "releases": [{"tag_name": "content-v1.1", "draft": False, "prerelease": False}],
    }
    if path.endswith("/check-runs"):
        result = {"check_runs": data["checks"] if data["head"] in path else []}
    elif path.endswith("/statuses"):
        result = []
    elif path.startswith("commits/"):
        result = {"parents": [{"sha": data["base"]}, {"sha": data["head"]}]}
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
        fixture["comments"][0]["body"] = "/release-book " + "f" * 40
        env["FIXTURE"] = json.dumps(fixture)
        result = subprocess.run([sys.executable, "-c", bootstrap, script], env=env,
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approval", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
