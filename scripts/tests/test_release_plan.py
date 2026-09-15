import subprocess
import unittest
from unittest.mock import patch

from helpers import RepositoryTest

import release_content as release


class ApiTests(unittest.TestCase):
    def response(self, status, body, exit_code=0):
        return subprocess.CompletedProcess(
            ["gh"], exit_code, f"HTTP/2.0 {status}\r\nContent-Type: application/json\r\n\r\n{body}",
            "" if exit_code == 0 else "Request failed.",
        )

    @patch.object(release.subprocess, "run")
    def test_explicit_404_is_distinguished_from_api_or_network_failures(self, run):
        run.return_value = self.response(404, '{"message":"Not Found"}', 1)
        self.assertIsNone(release.github_get("repos/owner/book/releases/tags/content-v1.1", allow_not_found=True))
        for status in (401, 403, 429, 500):
            run.return_value = self.response(status, '{"message":"failure"}', 1)
            with self.subTest(status=status), self.assertRaisesRegex(release.ReleaseError, "failed"):
                release.github_get("repos/owner/book/releases/tags/content-v1.1", allow_not_found=True)
        run.return_value = subprocess.CompletedProcess(["gh"], 1, "", "Network unavailable")
        with self.assertRaisesRegex(release.ReleaseError, "Network unavailable"):
            release.github_get("repos/owner/book/releases/tags/content-v1.1", allow_not_found=True)

    @patch.object(release.subprocess, "run")
    def test_missing_release_requires_confirmed_repository_access(self, run):
        run.side_effect = [
            self.response(404, "{}", 1),
            self.response(200, '{"full_name":"owner/book"}'),
        ]
        self.assertIsNone(release.github_release("owner/book", "content-v1.1"))
        self.assertEqual(run.call_count, 2)
        run.side_effect = [self.response(404, "{}", 1), self.response(404, "{}", 1)]
        with self.assertRaisesRegex(release.ReleaseError, "failed"):
            release.github_release("owner/book", "content-v1.1")

    @patch.object(release.subprocess, "run")
    def test_invalid_json_is_not_treated_as_missing_release(self, run):
        run.return_value = self.response(200, "not JSON")
        with self.assertRaisesRegex(release.ReleaseError, "invalid JSON"):
            release.github_get("repos/owner/book/releases/tags/content-v1.1")


class ReleasePlanTests(RepositoryTest):
    def metadata(self, assets=()):
        return {
            "tag_name": "content-v1.1",
            "assets": [
                {"id": number, "name": name, "state": "uploaded", "size": 524288,
                 "content_type": "application/pdf",
                 "browser_download_url":
                     f"https://github.com/owner/book/releases/download/content-v1.1/{name}"}
                for number, name in enumerate(assets, start=1)
            ],
        }

    @patch.object(release, "github_release")
    def test_complete_legacy_release_is_an_idempotent_noop(self, api):
        api.return_value = self.metadata(["gh-aw-book-v1.1.pdf"])
        plan = release.release_plan(self.root, "owner/book", env={})
        self.assertEqual(plan["action"], "skip")
        self.assertNotIn("source_sha", plan)

    @patch.object(release, "github_release")
    def test_incomplete_matching_assets_fail_with_manual_recovery_instructions(self, api):
        for state, size in (
            ("starter", 0), ("starter", 1024), ("failed", 1024),
            ("uploaded", 0), ("uploaded", -1), ("uploaded", None),
            ("uploaded", "524288"), ("uploaded", True), (None, 524288),
        ):
            with self.subTest(state=state, size=size):
                metadata = self.metadata(["gh-aw-book-v1.1.pdf"])
                metadata["assets"][0].update(state=state, size=size)
                api.return_value = metadata
                with self.assertRaisesRegex(release.ReleaseError, "incomplete or ambiguous") as raised:
                    release.release_plan(self.root, "owner/book", env={})
                self.assertIn("state='uploaded' and a positive integer size", str(raised.exception))
                self.assertIn("restore the correct tagged PDF", str(raised.exception))
                self.assertIn("No asset was deleted or overwritten", str(raised.exception))

    @patch.object(release, "github_release")
    def test_missing_asset_state_or_size_is_not_assumed_complete(self, api):
        for field in ("state", "size"):
            with self.subTest(field=field):
                metadata = self.metadata(["gh-aw-book-v1.1.pdf"])
                del metadata["assets"][0][field]
                api.return_value = metadata
                with self.assertRaisesRegex(release.ReleaseError, "incomplete or ambiguous"):
                    release.release_plan(self.root, "owner/book", env={})

    @patch.object(release, "github_release")
    def test_duplicate_matching_assets_require_manual_recovery(self, api):
        api.return_value = self.metadata(["gh-aw-book-v1.1.pdf", "gh-aw-book-v1.1.pdf"])
        with self.assertRaisesRegex(release.ReleaseError, "incomplete or ambiguous"):
            release.release_plan(self.root, "owner/book", env={})

    @patch.object(release, "github_release")
    def test_legacy_source_cannot_be_repaired_with_current_metadata(self, api):
        self.accept()
        self.commit()
        api.return_value = self.metadata()
        with self.assertRaisesRegex(release.ReleaseError, "Legacy tags are never rebuilt"):
            release.release_plan(self.root, "owner/book", env={})

    @patch.object(release, "github_release")
    def test_tag_without_edition_metadata_cannot_borrow_current_build_inputs(self, api):
        for name in ("VERSION", "CHANGELOG.md", "FRAMEWORK_VERSION"):
            (self.root / "content" / name).unlink()
        self.commit()
        self.git("tag", "--force", "content-v1.1")
        self.put("content/VERSION", "1.1\n")
        self.put("content/CHANGELOG.md", "## [1.1] - 2026-07-08\n\nHistorical metadata.\n")
        self.put("content/FRAMEWORK_VERSION", "v0.88.7\n")
        self.accept()
        self.commit()
        api.return_value = self.metadata()

        with self.assertRaisesRegex(release.ReleaseError, "Legacy tags are never rebuilt"):
            release.release_plan(self.root, "owner/book", env={})

    @patch.object(release, "github_release")
    def test_repair_selects_tag_commit_and_pin_not_current_checkout(self, api):
        self.accept()
        self.commit()
        source = self.git("rev-parse", "HEAD")
        self.git("tag", "--force", "content-v1.1")
        self.put("content/FRAMEWORK_VERSION", "v0.88.7\n")
        self.put("content/chapters/one.html", "<p>Unreleased, different source.</p>")
        self.commit()
        api.return_value = self.metadata(["unrelated-upload.txt"])
        api.return_value["assets"][0].update(state="starter", size=0)
        plan = release.release_plan(self.root, "owner/book", env={})
        self.assertEqual(plan["action"], "upload")
        self.assertEqual(plan["source_sha"], source)
        self.assertEqual(plan["framework_version"], "v0.81.6")
        self.assertEqual(plan["comparison_base"], "content-v1.1")
        self.assertTrue(plan["tag_exists"])

    @patch.object(release, "github_release")
    def test_new_release_uses_the_same_event_base_even_after_tag_creation(self, api):
        self.put("content/VERSION", "1.2\n")
        self.put("content/chapters/one.html", "<p>Next edition.</p>")
        self.accept()
        self.commit()
        api.return_value = None
        plan = release.release_plan(self.root, "owner/book", base=self.base, env={})
        self.assertEqual(plan["action"], "create")
        self.assertEqual(plan["source_sha"], self.git("rev-parse", "HEAD"))
        self.assertEqual(plan["comparison_base"], self.base)
        self.assertFalse(plan["tag_exists"])
        self.git("tag", "content-v1.2")
        replay = release.release_plan(self.root, "owner/book", env={})
        self.assertTrue(replay["tag_exists"])
        self.assertEqual(replay["source_sha"], plan["source_sha"])
        self.assertEqual(replay["comparison_base"], "content-v1.2")

    @patch.object(release, "github_release")
    def test_tag_version_mismatch_is_rejected(self, api):
        self.accept()
        self.put("content/VERSION", "1.0\n")
        self.commit()
        self.git("tag", "--force", "content-v1.1")
        self.put("content/VERSION", "1.1\n")
        api.return_value = self.metadata()
        with self.assertRaisesRegex(release.ReleaseError, "selected source contains 1.0"):
            release.release_plan(self.root, "owner/book", env={})


if __name__ == "__main__":
    unittest.main()
