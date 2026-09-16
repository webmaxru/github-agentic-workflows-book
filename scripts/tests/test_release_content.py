import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from helpers import RepositoryTest, SourceTest

import release_content as release


class ChangeTests(RepositoryTest):
    def test_committed_staged_unstaged_and_untracked_sources_are_included(self):
        for name in ("committed", "staged", "unstaged"):
            self.put(f"content/chapters/{name}.html", f"<p>{name}</p>")
        self.commit()
        base = self.git("rev-parse", "HEAD")
        self.put("content/chapters/committed.html", "<p>A committed edit</p>")
        self.commit()
        self.put("content/chapters/staged.html", "<p>A staged edit</p>")
        self.git("add", "content/chapters/staged.html")
        self.put("content/chapters/unstaged.html", "<p>An unstaged edit</p>")
        self.put("content/chapters/untracked.html", "<p>An untracked chapter</p>")
        delta = release.changes(self.root, base)
        self.assertTrue(delta["changed"])
        self.assertEqual(
            delta["changes"],
            [
                {"status": "modified", "path": "content/chapters/committed.html"},
                {"status": "modified", "path": "content/chapters/staged.html"},
                {"status": "modified", "path": "content/chapters/unstaged.html"},
                {"status": "added", "path": "content/chapters/untracked.html"},
            ],
        )

    def test_metadata_research_examples_tooling_and_toc_comments_are_not_releases(self):
        self.put("content/VERSION", "1.2\n")
        self.put("content/CHANGELOG.md", "A notes-only correction.\n")
        self.put("content/FRAMEWORK_VERSION", "v0.88.7\n")
        self.put("content/research/new.md", "Research.\n")
        self.put("content/brief.md", "Planning.\n")
        self.put("scripts/new.py", "print('tooling')\n")
        self.put("examples/ch01/one.md", "---\non: workflow_dispatch\n---\nChanged example.")
        self.put("content/toc.yml", "# New comment\nchapters: [{slug: one, id: one}]\ntitle: Book\n")
        self.assertFalse(release.changes(self.root, "content-v1.1")["changed"])

    def test_meaningful_toc_changes_are_releasable(self):
        self.put("content/toc.yml", "title: Book\nchapters: [{id: one, slug: renamed}]\n")
        self.assertEqual(
            release.changes(self.root, self.base)["changes"],
            [{"status": "modified", "path": "content/toc.yml"}],
        )

    def test_net_working_tree_is_compared_not_overridden_index_bytes(self):
        path = self.root / "content/chapters/one.html"
        original = path.read_bytes()
        path.write_bytes(b"<p>Staged, then undone locally.</p>")
        self.git("add", "content/chapters/one.html")
        path.write_bytes(original)
        self.assertFalse(release.changes(self.root, self.base)["changed"])

    def test_tracked_edited_rename_and_delete(self):
        self.put("content/chapters/deleted.html", "<p>Remove me.</p>")
        self.commit()
        base = self.git("rev-parse", "HEAD")
        self.git("mv", "content/chapters/one.html", "content/chapters/renamed.html")
        self.put("content/chapters/renamed.html", "<p>A chapter.\nA second line.</p>\nMore.\n")
        (self.root / "content/chapters/deleted.html").unlink()
        delta = release.changes(self.root, base)
        self.assertEqual(delta["changes"], [
            {"status": "deleted", "path": "content/chapters/deleted.html"},
            {"status": "renamed", "path": "content/chapters/renamed.html",
             "previous_path": "content/chapters/one.html"},
        ])

    def test_untracked_rename_and_move_out_of_releasable_sources(self):
        (self.root / "content/chapters/one.html").rename(self.root / "content/chapters/moved.html")
        self.assertEqual(release.changes(self.root, self.base)["changes"], [
            {"status": "renamed", "path": "content/chapters/moved.html",
             "previous_path": "content/chapters/one.html"},
        ])
        (self.root / "content/chapters/moved.html").rename(self.root / "content/removed.html")
        self.assertEqual(release.changes(self.root, self.base)["changes"], [
            {"status": "deleted", "path": "content/chapters/one.html"},
        ])

    def test_missing_base_fails_explicitly_and_cli_requires_base(self):
        with self.assertRaisesRegex(release.ReleaseError, "Cannot resolve"):
            release.changes(self.root, "content-v99.0")
        self.assertEqual(self.cli("release_content.py", "changes").returncode, 2)
        result = self.cli("release_content.py", "changes", "--base", "missing-tag")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Cannot resolve", result.stderr)

    def test_json_output_is_repeatable(self):
        self.put("content/chapters/untracked.html", "<p>New</p>")
        first = self.cli("release_content.py", "changes", "--base", self.base)
        second = self.cli("release_content.py", "changes", "--base", self.base)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertTrue(json.loads(first.stdout)["changed"])


class ReviewTests(SourceTest):
    def test_fingerprint_is_identical_for_lf_and_windows_crlf(self):
        before = release.fingerprint(self.root)
        for name in ("content/chapters/one.html", "content/toc.yml", "content/FRAMEWORK_VERSION",
                     "examples/ch01/one.md", "examples/ch01/shared/policy.md"):
            path = self.root / name
            path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.assertEqual(before, release.fingerprint(self.root))

    def test_fingerprint_excludes_edition_changelog_and_evidence(self):
        before = release.fingerprint(self.root)
        self.accept()
        self.put("content/VERSION", "99.0\n")
        self.put("content/CHANGELOG.md", "Edited release notes.")
        self.put("content/research/other.md", "More research.")
        self.put("site/generated.html", "Output.")
        self.assertEqual(before, release.fingerprint(self.root))

    def test_fingerprint_includes_names_shared_imports_and_framework(self):
        before = release.fingerprint(self.root)
        path = self.root / "content/chapters/one.html"
        path.rename(path.with_name("renamed.html"))
        self.assertNotEqual(before, release.fingerprint(self.root))
        before = release.fingerprint(self.root)
        self.put("examples/ch01/shared/policy.md", "Changed policy.")
        self.assertNotEqual(before, release.fingerprint(self.root))
        before = release.fingerprint(self.root)
        self.put("content/FRAMEWORK_VERSION", "v0.88.7\n")
        self.assertNotEqual(before, release.fingerprint(self.root))

    def test_non_markdown_inputs_are_bound_and_policy_deletion_invalidates_review(self):
        names = (
            "examples/ch01/strict-policy/aw.json",
            "examples/ch01/policy.excerpt.yml",
            "examples/ch01/context.yaml",
            "examples/ch01/verification-notes.txt",
        )
        for name in names:
            self.put(name, '{"strict": true}\n' if name.endswith(".json") else "Original fixture text.\n")
        for name in names:
            with self.subTest(name=name):
                self.accept()
                self.put(name, '{"strict": false}\n' if name.endswith(".json") else "Changed fixture text.\n")
                with self.assertRaisesRegex(release.ReleaseError, "fingerprint"):
                    release.check_review(self.root)
        self.accept()
        (self.root / "examples/ch01/strict-policy/aw.json").unlink()
        with self.assertRaisesRegex(release.ReleaseError, "fingerprint"):
            release.check_review(self.root)

    def test_non_markdown_text_fingerprints_normalize_windows_line_endings(self):
        names = ("examples/ch01/aw.json", "examples/ch01/policy.yml", "examples/ch01/policy.yaml",
                 "examples/ch01/notes.txt")
        for name in names:
            self.put(name, '{"strict": true}\n' if name.endswith(".json") else "Text line.\nNext line.\n")
        before = release.fingerprint(self.root)
        for name in names:
            path = self.root / name
            path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.assertEqual(before, release.fingerprint(self.root))

    def test_ignored_inputs_locks_and_build_outputs_do_not_change_fingerprint(self):
        self.put(".gitignore", "build/\nexamples/ch01/ignored.txt\n")
        before = release.fingerprint(self.root)
        self.put("examples/ch01/ignored.txt", "Ignored local notes.")
        self.put("examples/ch01/one.lock.yml", "Generated workflow.")
        self.put("examples/ch01/shared/fragment.lock.yml", "Generated import output.")
        self.put("examples/ch01/build/output.md", "Not an authored workflow.")
        self.put("examples/ch01/dist/binary.bin", "Not a source dependency.")
        self.assertEqual(before, release.fingerprint(self.root))
        self.put("examples/ch01/one.lock.yml", "Changed generated workflow.")
        self.assertEqual(before, release.fingerprint(self.root))

    def test_unsupported_or_binary_example_inputs_are_explicit_errors(self):
        unknown = self.put("examples/ch01/dependency.bin", "A type outside the supported text contract.")
        with self.assertRaisesRegex(release.ReleaseError, "Unsupported example input type"):
            release.fingerprint(self.root)
        unknown.unlink()
        text = self.root / "examples/ch01/notes.txt"
        text.write_bytes(b"\xffnot UTF-8")
        with self.assertRaisesRegex(release.ReleaseError, "not valid UTF-8"):
            release.fingerprint(self.root)
        text.write_bytes(b"contains\0binary")
        with self.assertRaisesRegex(release.ReleaseError, "NUL byte"):
            release.fingerprint(self.root)

    def test_example_links_and_escape_paths_are_rejected_before_reading(self):
        target = self.put("examples/ch01/aw.json", '{"strict": true}\n')
        original = Path.is_symlink
        with patch.object(Path, "is_symlink", lambda path: path == target or original(path)):
            with self.assertRaisesRegex(release.ReleaseError, "symlinks or junctions"):
                release.example_source_bytes(self.root, target)
        outside = self.put("outside.json", '{"strict": true}\n')
        with self.assertRaisesRegex(release.ReleaseError, "escapes examples"):
            release.example_source_bytes(self.root, outside)

    def test_record_review_accepts_windows_relative_report_path(self):
        self.put("content/research/review.md", "Verdict: ACCEPT\n")
        result = self.cli(
            "release_content.py", "record-review",
            "--report", "content\\research\\review.md", "--verdict", "ACCEPT",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        evidence = release.check_review(self.root)
        self.assertEqual(evidence["report_path"], "content/research/review.md")

    def test_single_canonical_verdict_marker_is_required(self):
        reports = (
            "A nonempty report without a verdict.",
            "Verdict: ACCEPT or REVISE\n",
            "Verdict: ACCEPT\nVerdict: ACCEPT\n",
            "Verdict: ACCEPT\nVerdict: REVISE\n",
            "Verdict: ACCEPT\nVerdict: UNKNOWN\n",
            "Verdict: ACCEPT\n> Verdict: REVISE\n",
            "Verdict: ACCEPT\n**Verdict**: REVISE\n",
            " Verdict: ACCEPT\n",
            "**Verdict: ACCEPT**\n",
            "# Verdict: ACCEPT\n",
            "verdict: ACCEPT\n",
            "Verdict: ACCEPT \n",
        )
        for report in reports:
            with self.subTest(report=report):
                self.put("content/research/review.md", report)
                with self.assertRaisesRegex(release.ReleaseError, "exactly one canonical standalone"):
                    release.review_record(self.root, "content/research/review.md", "ACCEPT")

    def test_accept_and_revise_can_only_record_a_matching_report(self):
        for verdict in ("ACCEPT", "REVISE"):
            with self.subTest(verdict=verdict):
                self.put("content/research/review.md", f"# Review\n\nVerdict: {verdict}")
                record = release.review_record(self.root, "content/research/review.md", verdict)
                self.assertEqual(record["verdict"], verdict)
                opposite = "REVISE" if verdict == "ACCEPT" else "ACCEPT"
                with self.assertRaisesRegex(release.ReleaseError, "does not match"):
                    release.review_record(self.root, "content/research/review.md", opposite)

    def test_check_rejects_contradictory_marker_even_with_an_updated_report_digest(self):
        evidence = self.accept()
        self.put("content/research/review.md", "Verdict: REVISE\n\nChanges are required.\n")
        evidence["report_sha256"] = hashlib.sha256(
            release.source_bytes(self.root, "content/research/review.md")
        ).hexdigest()
        self.put("content/release-review.json", json.dumps(evidence))
        with self.assertRaisesRegex(release.ReleaseError, "Report verdict REVISE does not match"):
            release.check_review(self.root)

    def test_cli_rejects_contradiction_without_overwriting_existing_evidence(self):
        self.accept()
        path = self.root / "content/release-review.json"
        before = path.read_bytes()
        self.put("content/research/review.md", "Verdict: REVISE\n")
        result = self.cli(
            "release_content.py", "record-review",
            "--report", "content/research/review.md", "--verdict", "ACCEPT",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not match", result.stderr)
        self.assertEqual(path.read_bytes(), before)

    def test_missing_or_revise_review_is_rejected(self):
        with self.assertRaisesRegex(release.ReleaseError, "Missing or invalid"):
            release.check_review(self.root)
        evidence = self.accept()
        evidence["verdict"] = "REVISE"
        self.put("content/release-review.json", json.dumps(evidence))
        with self.assertRaisesRegex(release.ReleaseError, "ACCEPT"):
            release.check_review(self.root)

    def test_stale_manuscript_and_framework_are_rejected(self):
        self.accept()
        self.put("content/chapters/one.html", "<p>Post-review edit.</p>")
        with self.assertRaisesRegex(release.ReleaseError, "fingerprint"):
            release.check_review(self.root)
        self.accept()
        self.put("content/FRAMEWORK_VERSION", "v0.88.7\n")
        with self.assertRaisesRegex(release.ReleaseError, "framework_version"):
            release.check_review(self.root)

    def test_deleted_or_modified_report_is_rejected(self):
        self.accept()
        self.put("content/research/review.md", "Verdict: ACCEPT\n\nChanged report after attestation.")
        with self.assertRaisesRegex(release.ReleaseError, "report_sha256"):
            release.check_review(self.root)
        (self.root / "content/research/review.md").unlink()
        with self.assertRaisesRegex(release.ReleaseError, "Required source"):
            release.check_review(self.root)

    def test_report_crlf_normalization_and_path_escape(self):
        self.accept()
        path = self.root / "content/research/review.md"
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        release.check_review(self.root)
        with self.assertRaises(release.ReleaseError):
            release.review_record(self.root, "../outside.md", "ACCEPT")
        with self.assertRaises(release.ReleaseError):
            release.review_record(self.root, "content/release-review.json", "ACCEPT")


class CheckTests(RepositoryTest):
    def test_unchanged_edition_passes_without_fake_bump(self):
        self.accept()
        result = release.check(self.root, self.base)
        self.assertEqual(result["version"], "1.1")
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["changed"])

    def test_prose_changes_require_monotonic_bump_and_matching_notes(self):
        self.put("content/chapters/one.html", "<p>New material.</p>")
        self.accept()
        with self.assertRaisesRegex(release.ReleaseError, "monotonically"):
            release.check(self.root, self.base)
        self.put("content/VERSION", "1.1.0\n")
        with self.assertRaisesRegex(release.ReleaseError, "monotonically"):
            release.check(self.root, self.base)
        self.put("content/VERSION", "1.2\n")
        with self.assertRaisesRegex(release.ReleaseError, "changelog entry"):
            release.check(self.root, self.base)
        self.put("content/CHANGELOG.md", "## [1.2] - 2026-09-15\n\nAdded new material.\n")
        self.assertEqual(release.check(self.root, self.base)["status"], "PASS")

    def test_metadata_only_version_bump_and_downgrade_are_rejected(self):
        self.accept()
        for version in ("1.2", "1.1.0", "1.0"):
            with self.subTest(version=version):
                self.put("content/VERSION", version + "\n")
                with self.assertRaisesRegex(release.ReleaseError, "No reader-visible"):
                    release.check(self.root, self.base)

    def test_empty_comment_only_heading_only_and_duplicate_notes_are_rejected(self):
        self.accept()
        for body in ("", "<!-- Notes later -->", "### Added\n", "---\n"):
            with self.subTest(body=body):
                self.put("content/CHANGELOG.md", "## [1.1] - 2026-07-08\n\n" + body)
                with self.assertRaisesRegex(release.ReleaseError, "nonempty"):
                    release.check(self.root, self.base)
        self.put("content/CHANGELOG.md", "## [1.1] - date\n\nFirst.\n\n## [1.1] - date\n\nSecond.")
        with self.assertRaisesRegex(release.ReleaseError, "exactly one"):
            release.check(self.root, self.base)

    def test_exact_framework_tags_only(self):
        self.accept()
        for version in ("", "latest", "0.88.7", "v0.88", "v00.88.7", "v0.88.7-rc.1"):
            with self.subTest(version=version):
                self.put("content/FRAMEWORK_VERSION", version + "\n")
                with self.assertRaisesRegex(release.ReleaseError, "Invalid framework"):
                    release.check(self.root, self.base)

    def test_legacy_tag_name_is_comparison_only_not_a_default_version(self):
        (self.root / "content/VERSION").unlink()
        self.commit()
        self.git("tag", "content-v1.0")
        legacy_sha = self.git("rev-parse", "HEAD")
        self.put("content/VERSION", "1.0\n")
        self.put("content/CHANGELOG.md", "## [1.0] - 2026-07-03\n\nInitial.\n")
        self.accept()
        checked = release.check(self.root, "content-v1.0")
        self.assertEqual(checked["baseline_version_source"], "legacy-content-tag")
        with self.assertRaisesRegex(release.ReleaseError, "no content/VERSION"):
            release.check(self.root, legacy_sha)

    def test_original_edition_tag_can_predate_both_version_and_changelog(self):
        for name in ("VERSION", "CHANGELOG.md"):
            (self.root / "content" / name).unlink()
        self.commit()
        self.git("tag", "--force", "content-v1.1")
        legacy_sha = self.git("rev-parse", "HEAD")
        self.put("content/VERSION", "1.1\n")
        self.put("content/CHANGELOG.md", "## [1.1] - 2026-07-08\n\nHistorical metadata.\n")
        self.accept()

        checked = release.check(self.root, "content-v1.1")
        self.assertEqual(checked["status"], "PASS")
        self.assertEqual(checked["version"], "1.1")
        self.assertEqual(checked["baseline_version_source"], "legacy-content-tag")
        self.assertFalse(checked["changed"])
        with self.assertRaisesRegex(release.ReleaseError, "no content/VERSION"):
            release.check(self.root, legacy_sha)

    def test_event_comparison_is_not_affected_by_new_release_tag(self):
        self.put("content/chapters/one.html", "<p>Next edition.</p>")
        self.put("content/VERSION", "1.2\n")
        self.put("content/CHANGELOG.md", "## [1.2] - date\n\nNew edition.\n")
        self.accept()
        self.commit()
        self.git("tag", "content-v1.2")
        event_path = self.put("build/push.json", json.dumps({"before": self.base}))
        env = {"GITHUB_EVENT_NAME": "push", "GITHUB_EVENT_PATH": str(event_path)}
        checked = release.check(self.root, env=env)
        self.assertEqual(checked["base"], self.base)
        self.assertEqual(checked["base_reason"], "push-before")
        self.assertTrue(checked["changed"])
        event_path = self.put(
            "build/pr.json", json.dumps({"pull_request": {"base": {"sha": self.base}}})
        )
        env = {"GITHUB_EVENT_NAME": "pull_request", "GITHUB_EVENT_PATH": str(event_path)}
        self.assertEqual(release.select_base(self.root, env=env), (self.base, "pull-request-base"))

    def test_manual_base_uses_reachable_version_tags_or_fails_explicitly(self):
        self.assertEqual(
            release.select_base(self.root, env={}),
            ("content-v1.1", "latest-reachable-content-tag"),
        )
        self.git("tag", "--delete", "content-v1.1")
        with self.assertRaisesRegex(release.ReleaseError, "No reachable"):
            release.select_base(self.root, env={})
        with self.assertRaisesRegex(release.ReleaseError, "GITHUB_EVENT_PATH"):
            release.select_base(self.root, env={"GITHUB_EVENT_NAME": "push"})


if __name__ == "__main__":
    unittest.main()
