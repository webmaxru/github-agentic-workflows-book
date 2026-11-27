import contextlib
import io
import json
import os
import sys
import unittest
from unittest.mock import patch

from helpers import ROOT  # noqa: F401  (puts scripts/ on sys.path)

import approved_book as policy
import publish_release as publish

SHA_A = "a" * 40
SHA_B = "b" * 40
TAG_OBJECT = "c" * 40


def release(tag, draft=False, prerelease=False):
    return {"tag_name": tag, "draft": draft, "prerelease": prerelease}


class LatestDecisionTests(unittest.TestCase):
    def test_only_the_highest_stable_version_becomes_latest(self):
        releases = [release("content-v1.0"), release("content-v1.1")]
        self.assertTrue(publish.latest_decision("content-v1.2", "create", releases))
        self.assertTrue(publish.latest_decision("content-v1.1", "upload", releases))
        self.assertFalse(publish.latest_decision("content-v1.0", "upload", releases))
        self.assertTrue(publish.latest_decision("content-v1.10", "create", releases + [release("content-v1.9")]))
        self.assertFalse(publish.latest_decision("content-v1.9", "upload", releases + [release("content-v1.10")]))

    def test_drafts_and_prereleases_never_count_against_or_for_latest(self):
        releases = [release("content-v1.1"), release("content-v2.0", prerelease=True),
                    release("content-v1.5", draft=True), release("nightly")]
        self.assertTrue(publish.latest_decision("content-v1.2", "create", releases))

    def test_creating_an_older_edition_after_a_newer_one_is_refused(self):
        with self.assertRaisesRegex(policy.PolicyError, "older edition"):
            publish.latest_decision("content-v1.0", "create", [release("content-v1.1")])

    def test_the_same_version_under_another_tag_is_a_duplicate(self):
        with self.assertRaisesRegex(policy.PolicyError, "already identifies"):
            publish.latest_decision("content-v1.2", "create", [release("content-v1.2.0")])

    def test_a_missing_or_malformed_tag_is_refused(self):
        for tag in ("", None, "v1.2", "main"):
            with self.subTest(tag=tag), self.assertRaises(policy.PolicyError):
                publish.latest_decision(tag, "create", [])


class FakeApi:
    repo = "owner/book"

    def __init__(self, refs=None, tags=None):
        self.refs = refs or {}
        self.tags = tags or {}
        self.writes = []

    def get(self, suffix, missing=False):
        if suffix.startswith("git/ref/tags/"):
            return self.refs.get(suffix.removeprefix("git/ref/tags/"))
        if suffix.startswith("git/tags/"):
            return self.tags[suffix.removeprefix("git/tags/")]
        raise AssertionError(suffix)

    def request(self, path, method="GET", data=None, missing=False):
        self.writes.append((method, path, data))
        if path.endswith("/git/tags"):
            return {"sha": TAG_OBJECT}
        return {}


class EnsureTagTests(unittest.TestCase):
    def test_a_new_tag_is_annotated_and_points_at_the_merge_commit(self):
        api = FakeApi()
        self.assertEqual(publish.ensure_tag(api, "content-v1.2", SHA_A),
                         {"tag": "content-v1.2", "sha": SHA_A, "created": True})
        (_, tag_path, tag), (_, ref_path, ref) = api.writes
        self.assertTrue(tag_path.endswith("/git/tags") and ref_path.endswith("/git/refs"))
        self.assertEqual((tag["tag"], tag["object"], tag["type"]), ("content-v1.2", SHA_A, "commit"))
        self.assertIn("tagger", tag)
        self.assertEqual(ref, {"ref": "refs/tags/content-v1.2", "sha": TAG_OBJECT})

    def test_an_existing_tag_at_the_same_commit_is_a_no_op(self):
        for refs, tags in (({"content-v1.2": {"object": {"type": "commit", "sha": SHA_A}}}, {}),
                           ({"content-v1.2": {"object": {"type": "tag", "sha": TAG_OBJECT}}},
                            {TAG_OBJECT: {"object": {"type": "commit", "sha": SHA_A}}})):
            api = FakeApi(refs, tags)
            with self.subTest(refs=refs):
                self.assertFalse(publish.ensure_tag(api, "content-v1.2", SHA_A)["created"])
                self.assertEqual(api.writes, [])

    def test_a_tag_is_never_moved(self):
        api = FakeApi({"content-v1.2": {"object": {"type": "commit", "sha": SHA_B}}})
        with self.assertRaisesRegex(policy.PolicyError, "never moved"):
            publish.ensure_tag(api, "content-v1.2", SHA_A)
        self.assertEqual(api.writes, [])

    def test_malformed_tag_or_commit_is_refused_before_any_write(self):
        api = FakeApi()
        for tag, sha in (("v1.2", SHA_A), ("content-v1.2", "abc"), ("content-v1.2", None)):
            with self.subTest(tag=tag, sha=sha), self.assertRaises(policy.PolicyError):
                publish.ensure_tag(api, tag, sha)
        self.assertEqual(api.writes, [])

    def test_a_tag_that_does_not_name_a_commit_is_refused(self):
        api = FakeApi({"content-v1.2": {"object": {"type": "tree", "sha": SHA_A}}})
        with self.assertRaisesRegex(policy.PolicyError, "does not point to a commit"):
            publish.ensure_tag(api, "content-v1.2", SHA_A)


class CliTests(unittest.TestCase):
    def cli(self, *argv, releases=(), api=None):
        class Api(FakeApi):
            def pages(self, suffix):
                return list(releases)

        out, err = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", ["publish_release.py", *argv]), \
                patch.dict(os.environ, {"GITHUB_REPOSITORY": "owner/book", "GH_TOKEN": "fixture"}), \
                patch.object(publish, "GitHub", lambda *args: api or Api()), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            return publish.main(), out.getvalue(), err.getvalue()

    def test_latest_prints_a_json_boolean_the_workflow_can_read(self):
        code, out, _ = self.cli("latest", "--tag", "content-v1.2", "--plan-action", "create",
                                releases=[release("content-v1.1")])
        self.assertEqual((code, json.loads(out)), (0, {"latest": True}))
        code, out, _ = self.cli("latest", "--tag", "content-v1.0", "--plan-action", "upload",
                                releases=[release("content-v1.1")])
        self.assertEqual((code, json.loads(out)), (0, {"latest": False}))

    def test_policy_failures_exit_non_zero_with_an_error_line(self):
        code, out, err = self.cli("latest", "--tag", "content-v1.0", "--plan-action", "create",
                                  releases=[release("content-v1.1")])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("ERROR:", err)

    def test_tag_refuses_to_move_an_existing_tag(self):
        api = FakeApi({"content-v1.2": {"object": {"type": "commit", "sha": SHA_B}}})
        code, _, err = self.cli("tag", "--tag", "content-v1.2", "--sha", SHA_A, api=api)
        self.assertEqual(code, 1)
        self.assertIn("never moved", err)
        self.assertEqual(api.writes, [])


if __name__ == "__main__":
    unittest.main()
