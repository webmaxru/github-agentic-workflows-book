import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from helpers import ROOT

import approved_book as policy
import deploy_gate as gate


class FakeApi:
    def __init__(self, releases):
        self.releases = releases

    def pages(self, suffix):
        assert suffix == "releases"
        return self.releases


def release(tag, draft=False, prerelease=False):
    return {"tag_name": tag, "draft": draft, "prerelease": prerelease}


class GateTests(unittest.TestCase):
    """The gate runs against a real git history: legacy tag, two editions, then non-content work."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "--quiet", "--initial-branch=main")
        self.git("config", "core.autocrlf", "false")
        self.write("content/chapters/a.html", "legacy")
        self.commit("legacy")
        self.git("tag", "content-v1.0")
        self.write("content/VERSION", "1.1\n")
        self.write("content/chapters/a.html", "first edition")
        self.commit("edition 1.1")
        self.git("tag", "-a", "-m", "release", "content-v1.1")
        self.v11 = self.git("rev-parse", "HEAD")
        self.write("site/generate.py", "# tooling only")
        self.commit("tooling")
        self.head = self.git("rev-parse", "HEAD")
        self.api = FakeApi([release("content-v1.0"), release("content-v1.1")])

    def git(self, *args):
        result = subprocess.run(
            ["git", "-c", "core.hooksPath=disabled-hooks", "-C", str(self.root), *args],
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def commit(self, message):
        self.git("add", "--all")
        self.git("-c", "user.name=Book Tests", "-c", "user.email=book-tests@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", message)

    def gate(self, ref=None):
        return gate.gate(self.api, self.root, ref)

    def test_push_to_main_deploys_when_content_equals_the_latest_release(self):
        self.assertEqual(self.gate(), {"mode": "main", "tag": "content-v1.1", "sha": self.head})

    def test_push_to_main_is_refused_when_book_content_is_ahead_of_the_release(self):
        for name in ("content/chapters/b.html", "examples/new.md"):
            with self.subTest(name=name):
                self.write(name, "unreleased")
                self.commit("unreleased content")
                with self.assertRaisesRegex(policy.PolicyError, "differs from the latest published release"):
                    self.gate()
                self.git("reset", "--quiet", "--hard", "HEAD~1")

    def test_content_paths_come_from_the_trusted_allowlist(self):
        self.assertEqual(gate.CONTENT_PATHSPECS, policy.CONTENT_PATHSPECS)
        self.assertEqual(set(policy.CONTENT_PATHSPECS), {"content", "examples"})

    def test_drafts_prereleases_and_unknown_tags_are_not_the_latest_release(self):
        self.api.releases += [release("content-v1.2", draft=True),
                              release("content-v1.3", prerelease=True),
                              release("nightly")]
        self.assertEqual(self.gate()["tag"], "content-v1.1")
        self.assertEqual(gate.published_tags(self.api), ["content-v1.0", "content-v1.1"])

    def test_the_latest_release_is_the_highest_version_not_the_newest_listed(self):
        self.api.releases.insert(0, release("content-v1.10"))
        self.git("tag", "content-v1.10")
        self.assertEqual(gate.published_tags(self.api)[-1], "content-v1.10")
        self.assertEqual(self.gate()["tag"], "content-v1.10")

    def test_nothing_deploys_without_a_published_release_or_a_local_tag(self):
        self.api.releases = [release("content-v1.1", draft=True)]
        with self.assertRaisesRegex(policy.PolicyError, "No published"):
            self.gate()
        self.api.releases = [release("content-v1.1"), release("content-v1.2")]
        with self.assertRaisesRegex(policy.PolicyError, "not available locally"):
            self.gate()

    def test_a_git_failure_is_an_error_not_a_pass(self):
        def failing(root, *args):
            return (128, "") if args[:2] == ("diff", "--quiet") else gate.run_git(root, *args)

        with self.assertRaisesRegex(policy.PolicyError, "Could not compare"):
            gate.gate(self.api, self.root, None, failing)

    def test_rollback_takes_a_released_tag_or_its_commit(self):
        self.assertEqual(self.gate("content-v1.1"),
                         {"mode": "tag", "tag": "content-v1.1", "sha": self.v11})
        self.assertEqual(self.gate(self.v11), {"mode": "tag", "tag": "content-v1.1", "sha": self.v11})

    def test_rollback_refuses_anything_unreleased(self):
        self.write("content/chapters/a.html", "second edition")
        self.write("content/VERSION", "1.2\n")
        self.commit("edition 1.2")
        self.git("tag", "-a", "-m", "release", "content-v1.2")
        v12 = self.git("rev-parse", "HEAD")
        for ref, message in (("content-v1.2", "not a published release"),
                             ("main", "not a release tag"),
                             ("HEAD", "not a release tag"),
                             (v12, "not the commit of a published release"),
                             (self.head, "not the commit of a published release"),
                             ("content-v9.9", "not a published release")):
            with self.subTest(ref=ref), self.assertRaisesRegex(policy.PolicyError, message):
                self.gate(ref)
        self.api.releases.append(release("content-v1.2", draft=True))
        with self.assertRaisesRegex(policy.PolicyError, "not a published release"):
            self.gate("content-v1.2")
        self.api.releases[-1] = release("content-v1.2", prerelease=True)
        with self.assertRaisesRegex(policy.PolicyError, "not a published release"):
            self.gate("content-v1.2")

    def test_rollback_refuses_legacy_tags_without_release_metadata(self):
        with self.assertRaisesRegex(policy.PolicyError, "predates release metadata"):
            self.gate("content-v1.0")

    def test_rollback_refuses_a_tag_that_is_not_on_main(self):
        self.git("checkout", "--quiet", "-b", "side", self.v11)
        self.write("content/chapters/a.html", "side")
        self.commit("side edition")
        self.git("tag", "-a", "-m", "release", "content-v1.5")
        self.git("checkout", "--quiet", "main")
        self.api.releases.append(release("content-v1.5"))
        with self.assertRaisesRegex(policy.PolicyError, "not on main"):
            self.gate("content-v1.5")

    def test_cli_prints_json_and_reports_policy_errors_with_exit_code_one(self):
        class Api(FakeApi):
            def __init__(self, *args):
                super().__init__(self.releases_for_test)

        Api.releases_for_test = self.api.releases
        env = {"GITHUB_REPOSITORY": "owner/book", "GH_TOKEN": "fixture"}
        for argv, code in ((["gate", "--root", str(self.root)], 0),
                           (["gate", "--root", str(self.root), "--ref", "main"], 1)):
            out, err = io.StringIO(), io.StringIO()
            with patch.object(sys, "argv", ["deploy_gate.py", *argv]), patch.dict(os.environ, env), \
                    patch.object(gate, "GitHub", Api), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(gate.main(), code, err.getvalue())
            if code == 0:
                self.assertEqual(json.loads(out.getvalue())["mode"], "main")
            else:
                self.assertIn("ERROR:", err.getvalue())


class SmokeTests(unittest.TestCase):
    PAGE = '<html><head><meta name="book-content-version" content="{}"></head></html>'

    def test_passes_once_the_live_site_serves_the_deployed_edition(self):
        answers = [(200, self.PAGE.format("1.1")), (200, self.PAGE.format("1.2"))]
        sleeps = []
        result = gate.smoke("https://book.example/", "1.2", attempts=5, delay=3,
                            fetch=lambda url: answers.pop(0), sleep=sleeps.append)
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(sleeps, [3])

    def test_retries_network_errors_and_then_fails_loudly(self):
        def broken(url):
            raise OSError("connection refused")

        with self.assertRaisesRegex(policy.PolicyError, "does not serve edition 1.2.*connection refused"):
            gate.smoke("https://book.example", "1.2", attempts=3, fetch=broken, sleep=lambda _: None)

    def test_a_page_without_the_edition_marker_or_a_non_200_fails(self):
        for answer in ((200, "<html></html>"), (503, self.PAGE.format("1.2"))):
            with self.subTest(answer=answer), self.assertRaises(policy.PolicyError):
                gate.smoke("https://book.example", "1.2", attempts=2,
                           fetch=lambda url, a=answer: a, sleep=lambda _: None)

    def test_the_generator_emits_the_marker_the_smoke_test_reads(self):
        source = (ROOT.parent / "site" / "generate.py").read_text(encoding="utf-8")
        self.assertIn('name="book-content-version"', source)


if __name__ == "__main__":
    unittest.main()
