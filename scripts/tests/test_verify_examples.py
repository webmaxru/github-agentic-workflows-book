import io
import json
import os
import shutil
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from helpers import RepositoryTest, SourceTest

import verify_examples as verify


STUB = r'''
import json
import pathlib
import subprocess
import sys

if sys.argv[1:] == ["version"]:
    print("gh-aw version v0.81.6 (test compiler)")
    raise SystemExit(0)
if sys.argv[1] != "compile":
    print("compilation is required", file=sys.stderr)
    raise SystemExit(9)
assert "--validate" not in sys.argv, "canonical verification must not require Issues/scanners"
forced_strict = "--strict" in sys.argv
if not pathlib.Path(".git").is_dir():
    raise SystemExit("not an isolated git repository")
workflow = pathlib.Path(sys.argv[-1])
text = workflow.read_text(encoding="utf-8")
print("repository=" + str(pathlib.Path.cwd()))
print("origin=" + subprocess.check_output(
    ["git", "config", "--local", "--get", "remote.origin.url"], text=True
).strip())
print("arguments=" + json.dumps(sys.argv[1:]))
policy = pathlib.Path(".github/workflows/aw.json")
if forced_strict:
    effective_strict = True
else:
    assert policy.is_file(), "repository policy was not staged beside the workflow"
    assert workflow.parent == policy.parent, "policy fixture was not self-contained"
    effective_strict = json.loads(policy.read_text())["strict"] is True
if "EXPECT_FIXTURE_DATA" in text:
    assert pathlib.Path(".github/workflows/notes.txt").read_text() == "Fixture notes.\n"
    assert pathlib.Path(".github/workflows/policy.excerpt.yml").read_bytes() == b"allow: []\r\n"
    assert not pathlib.Path(".github/workflows/ignored.txt").exists()
assert not list(pathlib.Path(".github/workflows").rglob("*.lock.yml")), "generated locks were staged"
if "EXPECT_POLICY" in text:
    assert pathlib.Path(".github/workflows/shared/policy.md").read_text() == "Original shared bytes.\n"
if "FAIL" in text or not text.startswith("---\n"):
    print("frontmatter: invalid field at line 2", file=sys.stderr)
    raise SystemExit(7)
if "NOLOCK" not in text:
    metadata = {
        "schema_version": "v4", "compiler_version": "v0.81.6",
        "strict": effective_strict, "agent_id": "copilot",
    }
    if "WRONG_VERSION" in text:
        metadata["compiler_version"] = "v0.88.7"
    if "NON_STRICT" in text or "INEFFECTIVE_POLICY" in text:
        metadata["strict"] = False
    header = "# gh-aw-metadata: " + json.dumps(metadata) + "\n"
    if "MISSING_HEADER" in text:
        header = ""
    if "LATE_HEADER" in text:
        header = "# Another comment comes first.\n" + header
    if "MALFORMED_HEADER" in text:
        header = '# gh-aw-metadata: {"strict": true,\n'
    body = "name: Fixture workflow\non: workflow_dispatch\njobs:\n  agent:\n"
    body += "    runs-on: ubuntu-latest\n    steps:\n      - run: echo fixture\n"
    workflow.with_suffix(".lock.yml").write_text(header + body, encoding="utf-8")
print("compiled actual source")
'''


class ExampleTests(RepositoryTest):
    def setUp(self):
        super().setUp()
        self.stub = self.put("build/compiler.py", STUB)
        self.compiler = [sys.executable, str(self.stub)]
        self.put(".github/workflows/live.yml", "A real book workflow; never touch.\n")
        self.scratch = self.root / "build" / "v"
        setting = patch.object(verify, "SCRATCH_ROOT", self.scratch)
        setting.start()
        self.addCleanup(setting.stop)

    def run_verifier(self, version="v0.81.6"):
        return verify.verify_examples(self.root, self.compiler, version)

    def test_every_standalone_is_compiled_and_shared_fragments_retained(self):
        self.put("examples/ch01/shared/policy.md", "Original shared bytes.\n")
        source = "---\non: workflow_dispatch\nimports:\n  - shared/policy.md\n---\nEXPECT_POLICY\n"
        self.put("examples/ch01/one.md", source)
        self.put("examples/ch02/nested/two.md", "---\non: workflow_dispatch\n---\nNested.\n")
        self.put("examples/ch02/shared/policy.md", "A distinct chapter policy.\n")
        before = self.git("status", "--short")
        report = self.run_verifier()
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual(report["passed"], 2)
        self.assertEqual(len(report["fragments"]), 2)
        self.assertTrue(all(item["lock_emitted"] for item in report["results"]))
        for item in report["results"]:
            self.assertEqual(item["compilation_mode"], "cli-strict")
            self.assertEqual(item["lock_metadata"]["compiler_version"], "v0.81.6")
            self.assertIs(item["lock_metadata"]["strict"], True)
        self.assertEqual((self.root / "examples/ch01/one.md").read_text(), source)
        self.assertEqual(self.git("status", "--short"), before)
        self.assertEqual(
            [path.name for path in (self.root / ".github/workflows").iterdir()], ["live.yml"]
        )
        self.assertFalse(list((self.root / "examples").rglob("*.lock.yml")))
        self.assertFalse(list(self.scratch.iterdir()))
        for item in report["results"]:
            repo = Path(item["stdout"].splitlines()[0].removeprefix("repository="))
            self.assertFalse(repo.exists())

    def test_failure_is_exact_and_remaining_workflows_still_run(self):
        self.put("examples/ch01/one.md", "---\non: invalid\n---\nFAIL\n")
        self.put("examples/ch02/two.md", "---\non: workflow_dispatch\n---\nValid.\n")
        report = self.run_verifier()
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["failed"], 1)
        self.assertEqual(report["passed"], 1)
        self.assertEqual(report["results"][0]["exit_code"], 7)
        self.assertEqual(report["results"][0]["stderr"], "frontmatter: invalid field at line 2\n")
        self.assertFalse(list(self.scratch.iterdir()))

    def policy_fixture(self, policy='{"strict": true}\n', body=""):
        self.put(
            "examples/ch02/strict-policy/opt-out.md",
            "---\non: workflow_dispatch\nstrict: false\n---\n" + body + "\n",
        )
        if policy is not None:
            self.put("examples/ch02/strict-policy/aw.json", policy)

    def test_repository_policy_is_loaded_without_cli_strict_and_copies_local_data(self):
        self.policy_fixture(body="EXPECT_FIXTURE_DATA")
        self.put("examples/ch02/strict-policy/notes.txt", "Fixture notes.\n")
        self.put("examples/ch02/strict-policy/policy.excerpt.yml", "allow: []\r\n")
        self.put("examples/ch02/strict-policy/ignored.txt", "Do not stage ignored input.")
        self.put("examples/ch02/strict-policy/.gitignore", "ignored.txt\n")
        self.put("examples/ch02/strict-policy/stale.lock.yml", "An old generated lock.")
        self.put("examples/ch02/strict-policy/build/generated.md", "A build artifact, not a workflow.")
        before = self.git("status", "--short")
        report = self.run_verifier()
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual(report["passed"], 2)
        ordinary, policy = report["results"]
        self.assertEqual(ordinary["compilation_mode"], "cli-strict")
        self.assertIn('"--strict"', ordinary["stdout"])
        self.assertEqual(policy["compilation_mode"], "repository-policy")
        self.assertNotIn("--strict", policy["stdout"])
        self.assertIs(policy["lock_metadata"]["strict"], True)
        self.assertEqual(policy["repository_policy"]["path"], "examples/ch02/strict-policy/aw.json")
        self.assertEqual(policy["repository_policy"]["staged_path"], ".github/workflows/aw.json")
        self.assertEqual(len(policy["repository_policy"]["sha256"]), 64)
        self.assertTrue(policy["repository_policy"]["strict"])
        self.assertIn("examples/ch02/strict-policy/notes.txt", report["inputs"])
        self.assertIn("examples/ch02/strict-policy/policy.excerpt.yml", report["inputs"])
        self.assertNotIn("examples/ch02/strict-policy/ignored.txt", report["inputs"])
        self.assertFalse(any(name.endswith(".lock.yml") for name in report["inputs"]))
        self.assertFalse(any("/build/" in name for name in report["inputs"]))
        self.assertEqual(before, self.git("status", "--short"))

    def test_missing_or_ignored_policy_fails_without_a_strict_flag_fallback(self):
        self.policy_fixture(policy=None)
        for ignored in (False, True):
            with self.subTest(ignored=ignored):
                if ignored:
                    self.put("examples/ch02/strict-policy/aw.json", '{"strict": true}\n')
                    self.put("examples/ch02/strict-policy/.gitignore", "aw.json\n")
                report = self.run_verifier()
                self.assertEqual(report["status"], "FAIL")
                self.assertEqual((report["passed"], report["failed"]), (1, 1))
                item = report["results"][1]
                self.assertEqual(item["compilation_mode"], "repository-policy")
                self.assertIn("missing or ignored", item["error"])
                self.assertNotIn("exit_code", item)

    def test_malformed_or_non_strict_repository_policy_fails_before_compilation(self):
        self.policy_fixture()
        for policy in ('{broken JSON', '[]', '{}', '{"strict": false}', '{"strict": "true"}', '{"strict": 1}'):
            with self.subTest(policy=policy):
                self.put("examples/ch02/strict-policy/aw.json", policy)
                report = self.run_verifier()
                self.assertEqual(report["status"], "FAIL")
                item = report["results"][1]
                self.assertEqual(item["compilation_mode"], "repository-policy")
                self.assertIn("policy", item["error"])
                self.assertNotIn("exit_code", item)

    def test_repository_policy_cannot_pass_with_non_strict_lock_metadata(self):
        self.policy_fixture(body="INEFFECTIVE_POLICY")
        report = self.run_verifier()
        self.assertEqual(report["status"], "FAIL")
        item = report["results"][1]
        self.assertEqual(item["compilation_mode"], "repository-policy")
        self.assertEqual(item["exit_code"], 0)
        self.assertTrue(item["lock_emitted"])
        self.assertIn("strict must be boolean true", item["metadata_error"])
        self.assertNotIn("--strict", item["stdout"])

    def test_nested_policy_workflows_cannot_fall_back_to_cli_strict(self):
        self.put("examples/ch02/strict-policy/nested/opt-out.md", "---\nstrict: false\n---\nProbe.\n")
        self.put("examples/ch02/strict-policy/aw.json", '{"strict": true}\n')
        report = self.run_verifier()
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["results"][1]["compilation_mode"], "repository-policy")
        self.assertIn("directly adjacent", report["results"][1]["error"])

    def test_invalid_frontmatter_is_never_silently_skipped(self):
        self.put("examples/ch01/one.md", "Not frontmatter, but still a standalone example.\n")
        report = self.run_verifier()
        self.assertEqual(report["failed"], 1)
        self.assertEqual(report["results"][0]["path"], "examples/ch01/one.md")

    def test_zero_exit_without_lock_is_failure(self):
        self.put("examples/ch01/one.md", "---\non: workflow_dispatch\n---\nNOLOCK\n")
        report = self.run_verifier()
        self.assertEqual(report["failed"], 1)
        self.assertEqual(report["results"][0]["exit_code"], 0)
        self.assertIn("without emitting", report["results"][0]["error"])

    def test_zero_exit_invalid_lock_headers_fail_without_losing_compiler_output(self):
        cases = {
            "missing": ("MISSING_HEADER", "first lock line"),
            "late": ("LATE_HEADER", "first lock line"),
            "malformed": ("MALFORMED_HEADER", "Malformed gh-aw lock metadata JSON"),
            "wrong-version": ("WRONG_VERSION", "compiler_version mismatch"),
            "non-strict": ("NON_STRICT", "strict must be boolean true"),
        }
        for name, (marker, _) in cases.items():
            self.put(f"examples/ch02/{name}.md", f"---\non: workflow_dispatch\n---\n{marker}\n")
        report = self.run_verifier()
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual((report["passed"], report["failed"]), (1, len(cases)))
        for item in report["results"][1:]:
            name = Path(item["path"]).stem
            self.assertEqual(item["status"], "FAIL")
            self.assertEqual(item["exit_code"], 0)
            self.assertTrue(item["lock_emitted"])
            self.assertIn(cases[name][1], item["metadata_error"])
            self.assertEqual(item["metadata_error"], item["error"])
            self.assertIn("compiled actual source", item["stdout"])
            self.assertEqual(item["stderr"], "")

    def test_metadata_error_is_preserved_in_the_cli_report(self):
        self.put("examples/ch01/one.md", "---\non: workflow_dispatch\n---\nWRONG_VERSION\n")
        actual_verify = verify.verify_examples
        destination = self.root / "build" / "metadata-result.json"
        output = io.StringIO()
        with (
            patch.object(verify, "verify_examples", side_effect=lambda root, compiler, version:
                         actual_verify(root, self.compiler, version)),
            redirect_stdout(output),
        ):
            code = verify.main([
                "--root", str(self.root), "--compiler", sys.executable, "--report", str(destination),
            ])
        self.assertEqual(code, 1)
        saved = json.loads(destination.read_text())
        self.assertEqual(saved, json.loads(output.getvalue()))
        self.assertIn("compiler_version mismatch", saved["results"][0]["metadata_error"])
        self.assertIn("compiled actual source", saved["results"][0]["stdout"])

    def test_version_mismatch_fails_before_staging_and_reports_all_workflows(self):
        self.put("examples/ch02/two.md", "---\non: workflow_dispatch\n---\nSecond.\n")
        report = self.run_verifier("v0.88.7")
        self.assertEqual(report["failed"], 2)
        self.assertIn("expected v0.88.7, found v0.81.6", report["error"])
        self.assertFalse(self.scratch.exists())

    def test_compiler_version_failure_and_missing_executable_propagate(self):
        self.stub.write_text("import sys\nprint('version failed', file=sys.stderr)\nsys.exit(3)\n")
        report = self.run_verifier()
        self.assertEqual(report["failed"], 1)
        self.assertIn("exit 3", report["error"])
        self.assertIn("version failed", report["error"])
        report = verify.verify_examples(
            self.root, [str(self.root / "missing-compiler")], "v0.81.6"
        )
        self.assertEqual(report["failed"], 1)

    def test_cli_requires_absolute_compiler_and_does_not_default_missing_pin(self):
        result = self.cli("verify_examples.py", "--compiler", "relative.exe")
        self.assertEqual(result.returncode, 1)
        self.assertIn("absolute", result.stderr)
        (self.root / "content/FRAMEWORK_VERSION").unlink()
        result = self.cli("verify_examples.py", "--compiler", sys.executable)
        self.assertEqual(result.returncode, 1)
        self.assertIn("FRAMEWORK_VERSION", result.stderr)

    def test_cli_failure_writes_report_and_exits_nonzero(self):
        report = self.root / "build/result.json"
        result = self.cli(
            "verify_examples.py", "--compiler", sys.executable, "--report", str(report)
        )
        self.assertEqual(result.returncode, 1)
        saved = json.loads(report.read_text())
        self.assertEqual(saved["status"], "FAIL")
        self.assertEqual(saved["failed"], 1)

    def test_source_remote_is_sanitized_and_configured_without_fetching(self):
        raw = "https://x-access-token:test-secret@github.com/acme/book.git?token=test-query#private"
        self.git("remote", "add", "origin", raw)
        with patch.object(verify.subprocess, "run", wraps=subprocess.run) as commands:
            report = self.run_verifier()
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual(report["repository_context"], {
            "url": "https://github.com/acme/book.git", "source": "source-origin",
        })
        self.assertIn("origin=https://github.com/acme/book.git", report["results"][0]["stdout"])
        for secret in ("test-secret", "test-query", "x-access-token", "#private"):
            self.assertNotIn(secret, json.dumps(report))
        self.assertEqual(self.git("config", "--local", "--get", "remote.origin.url"), raw)
        git_commands = [call.args[0] for call in commands.call_args_list if call.args[0][0] == "git"]
        self.assertTrue(any("remote" in command and "add" in command for command in git_commands))
        self.assertFalse(any(
            verb in command for command in git_commands for verb in ("fetch", "pull", "push", "clone")
        ))

    def test_missing_or_non_github_origin_uses_an_explicit_real_book_context(self):
        for origin in (None, "https://private-token@other.invalid/acme/book?secret=hidden"):
            with self.subTest(origin=origin):
                if origin is not None:
                    self.git("remote", "add", "origin", origin)
                report = self.run_verifier()
                self.assertEqual(report["status"], "PASS", report)
                self.assertEqual(report["repository_context"], {
                    "url": verify.BOOK_REMOTE, "source": "book-default",
                })
                self.assertIn(f"origin={verify.BOOK_REMOTE}", report["results"][0]["stdout"])
                self.assertNotIn("private-token", json.dumps(report))
                self.assertNotIn("other.invalid", json.dumps(report))

    def test_nested_sources_do_not_nest_the_compiler_scratch_directory(self):
        nested = self.root / "deeply" / "nested" / "input" / "corpus"
        shutil.copytree(self.root / "examples", nested / "examples")
        report = verify.verify_examples(nested, self.compiler, "v0.81.6")
        self.assertEqual(report["status"], "PASS", report)
        repo = Path(report["results"][0]["stdout"].splitlines()[0].removeprefix("repository="))
        self.assertTrue(repo.is_relative_to(self.scratch))
        self.assertFalse(repo.is_relative_to(nested))
        self.assertFalse((nested / "build").exists())

    def test_temporary_directory_setup_failure_reports_every_workflow(self):
        self.put("examples/ch02/two.md", "---\non: workflow_dispatch\n---\nSecond.\n")
        error = OSError(28, "No space left on device", str(self.scratch))
        with patch.object(verify, "TemporaryDirectory", side_effect=error):
            report = self.run_verifier()
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["failed"], 2)
        self.assertEqual(report["environment_errors"][0]["phase"], "setup")
        self.assertEqual(report["environment_errors"][0]["error"], str(error))
        self.assertTrue(all(item["error"] == str(error) for item in report["results"]))

    def test_scratch_directory_creation_failure_is_reported(self):
        self.put("build/v", "A file blocks scratch-directory creation.")
        report = self.run_verifier()
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["failed"], 1)
        self.assertEqual(report["environment_errors"][0]["phase"], "setup")
        self.assertEqual(report["environment_errors"][0]["error_type"], "FileExistsError")
        self.assertEqual(self.scratch.read_text(), "A file blocks scratch-directory creation.")

    def prepared_directory(self):
        self.scratch.mkdir(parents=True, exist_ok=True)
        directory = TemporaryDirectory(prefix="", dir=self.scratch)
        self.addCleanup(directory.cleanup)
        return directory

    def test_cleanup_error_preserves_passes_but_fails_the_report_and_recovers_safely(self):
        directory = self.prepared_directory()
        error = OSError(145, "The directory is not empty", directory.name)
        sibling = self.scratch / "unrelated-run"
        sibling.mkdir()
        (sibling / "keep.txt").write_text("Do not touch this invocation.")
        with (
            patch.object(verify, "TemporaryDirectory", return_value=directory),
            patch.object(directory, "cleanup", side_effect=error),
        ):
            report = self.run_verifier()
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual((report["passed"], report["failed"]), (1, 0))
        self.assertEqual(report["results"][0]["status"], "PASS")
        self.assertIn("compiled actual source", report["results"][0]["stdout"])
        self.assertEqual(report["environment_errors"][0]["phase"], "cleanup")
        self.assertEqual(report["environment_errors"][0]["error"], str(error))
        self.assertTrue(report["cleanup_recovered"])
        self.assertFalse(Path(directory.name).exists())
        self.assertEqual((sibling / "keep.txt").read_text(), "Do not touch this invocation.")

    def test_failed_cleanup_retry_records_both_errors_and_the_exact_pending_path(self):
        directory = self.prepared_directory()
        first = OSError(145, "The directory is not empty", directory.name)
        retry = PermissionError(13, "Cleanup access denied", directory.name)
        with (
            patch.object(verify, "TemporaryDirectory", return_value=directory),
            patch.object(directory, "cleanup", side_effect=first),
            patch.object(verify, "_cleanup_run_directory", side_effect=retry),
        ):
            report = self.run_verifier()
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["passed"], 1)
        self.assertEqual([item["phase"] for item in report["environment_errors"]], ["cleanup", "cleanup-retry"])
        self.assertEqual([item["error"] for item in report["environment_errors"]], [str(first), str(retry)])
        self.assertEqual(report["cleanup_pending"], directory.name)
        self.assertTrue(Path(directory.name).is_dir())

    def test_cli_writes_collected_results_even_when_cleanup_fails(self):
        directory = self.prepared_directory()
        error = OSError(145, "The directory is not empty", directory.name)
        actual_verify = verify.verify_examples
        output = io.StringIO()
        destination = self.root / "build" / "cleanup-result.json"
        with (
            patch.object(verify, "TemporaryDirectory", return_value=directory),
            patch.object(directory, "cleanup", side_effect=error),
            patch.object(verify, "verify_examples", side_effect=lambda root, compiler, version:
                         actual_verify(root, self.compiler, version)),
            redirect_stdout(output),
        ):
            code = verify.main([
                "--root", str(self.root), "--compiler", sys.executable, "--report", str(destination),
            ])
        self.assertEqual(code, 1)
        saved = json.loads(destination.read_text())
        self.assertEqual(saved, json.loads(output.getvalue()))
        self.assertEqual(saved["status"], "FAIL")
        self.assertEqual(saved["results"][0]["status"], "PASS")
        self.assertEqual(saved["environment_errors"][0]["error"], str(error))

    def test_report_write_failure_still_preserves_results_on_stdout(self):
        self.put("build/report-blocker", "A file, not an output directory.")
        actual_verify = verify.verify_examples
        output = io.StringIO()
        with (
            patch.object(verify, "verify_examples", side_effect=lambda root, compiler, version:
                         actual_verify(root, self.compiler, version)),
            redirect_stdout(output),
        ):
            code = verify.main([
                "--root", str(self.root), "--compiler", sys.executable,
                "--report", str(self.root / "build" / "report-blocker" / "result.json"),
            ])
        self.assertEqual(code, 1)
        saved = json.loads(output.getvalue())
        self.assertEqual(saved["status"], "FAIL")
        self.assertEqual(saved["results"][0]["status"], "PASS")
        self.assertEqual(saved["environment_errors"][-1]["phase"], "report-write")

    def test_cleanup_refuses_paths_outside_the_exact_scratch_parent(self):
        outside = self.root / "outside"
        outside.mkdir()
        with self.assertRaisesRegex(verify.ReleaseError, "Refusing to clean"):
            verify._cleanup_run_directory(outside, self.scratch)
        self.assertTrue(outside.is_dir())

    @unittest.skipUnless(os.name == "nt", "Windows long-path cleanup")
    def test_specific_cleanup_handles_files_beyond_windows_max_path(self):
        run = self.scratch / "long"
        nested = run / ("a" * 100) / ("b" * 100)
        Path(verify._long_path(nested)).mkdir(parents=True)
        lock = nested / "workflow.lock.yml"
        self.assertGreater(len(str(lock)), 260)
        with open(verify._long_path(lock), "w") as output:
            output.write("name: long-path fixture\n")
        verify._cleanup_run_directory(run, self.scratch)
        self.assertFalse(run.exists())


class RemoteUrlTests(unittest.TestCase):
    def test_https_ssh_and_scp_origins_become_credential_free_github_urls(self):
        for remote in (
            "https://github.com/acme/book.git",
            "git@github.com:acme/book.git",
            "git@GitHub.com:acme/book.git",
            "ssh://git@github.com/acme/book.git",
            "ssh://git:fake-secret@github.com:22/acme/book.git",
            "https://user:fake-secret@github.com/acme/book.git?token=fake-query#fragment",
        ):
            with self.subTest(remote=remote):
                self.assertEqual(verify._canonical_remote(remote), "https://github.com/acme/book.git")

    def test_unrecognized_origins_are_not_copied_into_staging_or_reports(self):
        for remote in (
            "file:///local/book", r"C:\local\book.git",
            "https://fake-secret@other.invalid/acme/book.git",
            "https://github.com/acme/book/private-token",
            "https://github.com/acme/book%2Fprivate-token",
            "https://fake-secret@[invalid/acme/book",
        ):
            with self.subTest(remote=remote):
                self.assertIsNone(verify._canonical_remote(remote))


class LockMetadataTests(SourceTest):
    def read_metadata(self, metadata):
        lock = self.put(
            "build/fixture.lock.yml",
            verify.LOCK_METADATA_PREFIX + json.dumps(metadata) + "\nname: Fixture workflow\n",
        )
        return verify._read_lock_metadata(lock, "v0.81.6")

    def test_current_metadata_is_returned_without_gating_unrelated_schema_fields(self):
        metadata = {
            "schema_version": "v4", "compiler_version": "v0.81.6",
            "strict": True, "agent_id": "copilot",
        }
        self.assertEqual(self.read_metadata(metadata), metadata)

    def test_strict_requires_a_literal_json_boolean_true(self):
        for value in (False, "true", "false", 1, 0, None):
            with self.subTest(value=value), self.assertRaisesRegex(verify.ReleaseError, "boolean true"):
                self.read_metadata({"compiler_version": "v0.81.6", "strict": value})
        with self.assertRaisesRegex(verify.ReleaseError, "boolean true"):
            self.read_metadata({"compiler_version": "v0.81.6"})

    def test_compiler_version_is_required_and_must_match_exactly(self):
        for value in ("v0.88.7", "0.81.6", "V0.81.6", "v0.81.6\n", None, 81):
            with self.subTest(value=value), self.assertRaisesRegex(verify.ReleaseError, "compiler_version"):
                self.read_metadata({"compiler_version": value, "strict": True})
        with self.assertRaisesRegex(verify.ReleaseError, "compiler_version"):
            self.read_metadata({"strict": True})

    def test_metadata_must_be_a_json_object(self):
        for value in ([], None, "v0.81.6", True):
            with self.subTest(value=value), self.assertRaisesRegex(verify.ReleaseError, "JSON object"):
                self.read_metadata(value)


if __name__ == "__main__":
    unittest.main()
