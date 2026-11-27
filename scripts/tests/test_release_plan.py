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
            self.response(200, "[]"),
        ]
        self.assertIsNone(release.github_release("owner/book", "content-v1.1"))
        self.assertEqual(run.call_count, 3)
        run.side_effect = [self.response(404, "{}", 1), self.response(404, "{}", 1)]
        with self.assertRaisesRegex(release.ReleaseError, "failed"):
            release.github_release("owner/book", "content-v1.1")

    @patch.object(release.subprocess, "run")
    def test_a_draft_is_found_although_the_tag_lookup_hides_it(self, run):
        draft = '{"tag_name":"content-v1.1","draft":true,"assets":[]}'
        run.side_effect = [
            self.response(404, "{}", 1),
            self.response(200, '{"full_name":"owner/book"}'),
            self.response(200, f'[{{"tag_name":"content-v1.0","draft":false}},{draft}]'),
        ]
        found = release.github_release("owner/book", "content-v1.1")
        self.assertTrue(found["draft"])
        run.side_effect = [
            self.response(404, "{}", 1),
            self.response(200, '{"full_name":"owner/book"}'),
            self.response(200, '{"not":"a list"}'),
        ]
        with self.assertRaisesRegex(release.ReleaseError, "unexpected response shape"):
            release.github_release("owner/book", "content-v1.1")

    @patch.object(release.subprocess, "run")
    def test_invalid_json_is_not_treated_as_missing_release(self, run):
        run.return_value = self.response(200, "not JSON")
        with self.assertRaisesRegex(release.ReleaseError, "invalid JSON"):
            release.github_get("repos/owner/book/releases/tags/content-v1.1")


class ReleasePlanTests(RepositoryTest):
    def metadata(self, assets=(), draft=False):
        return {
            "tag_name": "content-v1.1",
            "draft": draft,
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
    def test_incomplete_matching_assets_require_a_new_version(self, api):
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
                self.assertIn("Ship the fix as a new version", str(raised.exception))

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
    def test_duplicate_matching_assets_are_not_complete(self, api):
        api.return_value = self.metadata(["gh-aw-book-v1.1.pdf", "gh-aw-book-v1.1.pdf"])
        with self.assertRaisesRegex(release.ReleaseError, "incomplete or ambiguous"):
            release.release_plan(self.root, "owner/book", env={})

    @patch.object(release, "github_release")
    def test_published_release_missing_its_pdf_fails(self, api):
        api.return_value = self.metadata(["unrelated-upload.txt"])
        with self.assertRaisesRegex(release.ReleaseError, "published without its PDF.*new version"):
            release.release_plan(self.root, "owner/book", env={})

    @patch.object(release, "github_release")
    def test_any_existing_draft_blocks_publication_even_without_a_tag(self, api):
        for with_tag in (True, False):
            if not with_tag:
                self.git("tag", "-d", "content-v1.1")
            for assets in ([], ["gh-aw-book-v1.1.pdf"]):
                api.return_value = self.metadata(assets, draft=True)
                with self.subTest(tag=with_tag, assets=assets), self.assertRaisesRegex(release.ReleaseError, "draft"):
                    release.release_plan(self.root, "owner/book", env={}, expected_source=self.base)

    @patch.object(release, "github_release")
    def test_only_a_fresh_tag_can_be_planned_for_creation(self, api):
        self.put("content/VERSION", "1.2\n")
        self.put("content/chapters/one.html", "<p>Next edition.</p>")
        self.accept()
        self.commit()
        api.return_value = None
        plan = release.release_plan(self.root, "owner/book", base=self.base, env={})
        self.assertEqual(plan["action"], "create")
        self.assertEqual(plan["source_sha"], self.git("rev-parse", "HEAD"))
        self.assertEqual(plan["comparison_base"], self.base)
        self.git("tag", "content-v1.2")
        with self.assertRaisesRegex(release.ReleaseError, "exists without a release"):
            release.release_plan(self.root, "owner/book", env={}, expected_source=plan["source_sha"])

    @patch.object(release, "github_release")
    def test_new_source_must_contain_the_requested_edition(self, api):
        self.accept()
        self.put("content/VERSION", "1.2\n")
        self.commit()
        self.put("content/VERSION", "1.3\n")
        api.return_value = None
        with self.assertRaisesRegex(release.ReleaseError, "selected source contains 1.2"):
            release.release_plan(self.root, "owner/book", env={})

    @patch.object(release, "github_release")
    def test_complete_release_must_have_its_exact_tag_and_source(self, api):
        self.accept()
        self.commit()
        head = self.git("rev-parse", "HEAD")
        api.return_value = self.metadata(["gh-aw-book-v1.1.pdf"])
        with self.assertRaisesRegex(release.ReleaseError, "different source"):
            release.release_plan(self.root, "owner/book", env={}, expected_source=head)
        self.git("tag", "-d", "content-v1.1")
        with self.assertRaisesRegex(release.ReleaseError, "tag is unavailable"):
            release.release_plan(self.root, "owner/book", env={}, expected_source=head)
        self.git("tag", "content-v1.1")
        self.assertEqual(release.release_plan(self.root, "owner/book", env={}, expected_source=head)["action"], "skip")


if __name__ == "__main__":
    unittest.main()
