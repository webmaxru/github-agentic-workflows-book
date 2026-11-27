"""Exercise the real cleanup client against a loopback API; no live artifact mutations."""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import helpers
import artifact_storage as storage
from approved_book import GitHub, GitHubError, PolicyError
from release_content import ReleaseError

REPO = "owner/book"
SHA = "a" * 40
TAG = "content-v1.2"
DIGEST = "sha256:" + hashlib.sha256(b"PDF").hexdigest()


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.routes = {}
        self.requests = []
        self.deleted = []
        self.delete_status = {}
        self.before_get = None
        case = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                case.requests.append(("GET", self.path))
                if case.before_get:
                    case.before_get(self.path)
                status, body = case.routes.get(self.path, (404, {"message": "missing fixture"}))
                self.send_response(status)
                self.end_headers()
                self.wfile.write(json.dumps(body).encode())

            def do_DELETE(self):
                case.requests.append(("DELETE", self.path))
                status, body = case.delete_status.get(self.path, (204, None))
                if status == 204:
                    case.deleted.append(int(self.path.rsplit("/", 1)[1]))
                self.send_response(status)
                self.end_headers()
                if status != 204:
                    self.wfile.write(json.dumps(body).encode())

            def log_message(self, *_):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)
        self.api = GitHub(REPO, "test", f"http://127.0.0.1:{self.server.server_port}")
        self.ref = "refs/heads/feature/one"
        self.new = self.producer(20)
        self.old = self.producer(10)
        self.replacement = self.artifact(self.new, 200, "2026-11-27T12:00:00Z")
        self.previous = self.artifact(self.old, 100, "2026-11-27T11:00:00Z")
        self.get("actions/runs/20", self.new)
        self.get("actions/runs/10", self.old)
        self.get("actions/artifacts/200", self.replacement)
        self.get("actions/artifacts/100", self.previous)
        self.pages("actions/runs/20/artifacts", "artifacts", [self.replacement])
        self.pages("actions/artifacts", "artifacts", [self.previous, self.replacement])
        self.steps("Upload book preview")

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def get(self, suffix, body, status=200):
        self.routes[f"/repos/{REPO}/{suffix}"] = (status, body)

    def pages(self, suffix, key, values):
        # A full first page requires a second, even when it is empty.
        batches = [values[i:i + 100] for i in range(0, len(values), 100)]
        if not values or len(values) % 100 == 0:
            batches.append([])
        for page, batch in enumerate(batches, 1):
            self.get(f"{suffix}?per_page=100&page={page}", {key: batch})

    def producer(self, number, **overrides):
        return {"id": number, "repository": {"full_name": REPO},
                "head_repository": {"full_name": REPO},
                "path": ".github/workflows/ci.yml", "head_sha": SHA,
                "workflow_id": 7, "head_branch": "feature/one", "run_attempt": 1,
                "event": "workflow_dispatch", "status": "completed", "conclusion": "success",
                **overrides}

    def artifact(self, run, number, created, ref=None, **overrides):
        return {"id": number, "name": storage.preview_name(REPO, ref or self.ref, run["id"], 1),
                "created_at": created, "size_in_bytes": 1000, "expired": False,
                "workflow_run": {key: run[key] for key in ("id", "head_sha", "head_branch")},
                **overrides}

    def steps(self, *names, conclusion="success"):
        self.pages("actions/runs/20/attempts/1/jobs", "jobs", [
            {"status": "completed", "conclusion": conclusion,
             "steps": [{"name": name, "conclusion": conclusion} for name in names]}])

    def test_namespace_binds_book_full_ref_run_and_attempt(self):
        name = storage.preview_name(REPO, self.ref, 20, 1)
        self.assertEqual(storage.preview_ref(name, REPO, 20, 1), self.ref)
        self.assertIsNone(storage.preview_ref(name, "owner/other", 20, 1))
        self.assertIsNone(storage.preview_ref(name, REPO, 20, 2))
        self.assertNotEqual(name, storage.preview_name(REPO, "refs/tags/feature/one", 20, 1))

    def test_replaces_only_older_preview_and_preserves_every_other_namespace(self):
        newer = self.artifact(self.producer(30), 300, "2026-11-27T13:00:00Z")
        others = [
            self.artifact(self.old, 101, "2026-11-27T10:00:00Z", ref="refs/heads/other"),
            self.artifact(self.old, 102, "2026-11-27T10:00:00Z", name="validated-release"),
            self.artifact(self.old, 103, "2026-11-27T10:00:00Z", name="validated-pages"),
            self.artifact(self.old, 104, "2026-11-27T10:00:00Z", name="validated-book-diagnostics"),
            self.artifact(self.old, 105, "2026-11-27T10:00:00Z", name="unrelated-0-0"),
        ]
        self.pages("actions/artifacts", "artifacts", others + [self.previous, newer, self.replacement])
        self.assertEqual(storage.previews(self.api, 20, 1)["deleted"], [100])
        self.assertEqual(self.deleted, [100])

    def test_pagination_is_exhausted_before_deleting(self):
        diagnostics = [dict(self.previous, id=i + 1000, name="diagnostic") for i in range(100)]
        self.pages("actions/artifacts", "artifacts", diagnostics + [self.previous])
        storage.previews(self.api, 20, 1)
        self.assertEqual(self.deleted, [100])
        page = ("GET", f"/repos/{REPO}/actions/artifacts?per_page=100&page=2")
        self.assertLess(self.requests.index(page), next(i for i, req in enumerate(self.requests)
                                                       if req[0] == "DELETE"))

    def test_successful_upload_with_missing_replacement_fails_and_retains_previous(self):
        self.pages("actions/runs/20/artifacts", "artifacts", [])
        with self.assertRaisesRegex(PolicyError, "replacement artifact is missing"):
            storage.previews(self.api, 20, 1)
        self.assertEqual(self.deleted, [])

    def test_skipped_or_nonexistent_upload_without_replacement_is_a_validation_only_noop(self):
        self.pages("actions/runs/20/artifacts", "artifacts", [])
        for steps in ([], [{"name": "Upload book preview", "conclusion": "skipped"}]):
            with self.subTest(steps=steps):
                self.pages("actions/runs/20/attempts/1/jobs", "jobs", [
                    {"status": "completed", "conclusion": "success", "steps": steps}])
                result = storage.previews(self.api, 20, 1)
                self.assertEqual(result["deleted"], [])
                self.assertIn("validation only", result["reason"])
        self.assertEqual(self.deleted, [])

    def test_failed_upload_never_retires_previous(self):
        self.steps("Upload book preview", conclusion="failure")
        with self.assertRaisesRegex(PolicyError, "successful"):
            storage.previews(self.api, 20, 1)
        self.assertEqual(self.deleted, [])

    def test_failed_or_rerunning_replacement_is_refused(self):
        for overrides in ({"conclusion": "failure"}, {"status": "in_progress"}, {"run_attempt": 2},
                          {"workflow_id": None}, {"head_sha": ""}, {"id": 21}):
            with self.subTest(overrides=overrides):
                self.get("actions/runs/20", {**self.new, **overrides})
                with self.assertRaises(PolicyError):
                    storage.previews(self.api, 20, 1)
        self.assertEqual(self.deleted, [])

    def test_missing_or_ambiguous_replacement_artifact_identity_is_refused(self):
        for artifacts in ([dict(self.replacement, id=None)],
                          [self.replacement, dict(self.replacement, id=201)]):
            with self.subTest(artifacts=artifacts):
                self.pages("actions/runs/20/artifacts", "artifacts", artifacts)
                with self.assertRaises(PolicyError):
                    storage.previews(self.api, 20, 1)
        self.assertEqual(self.deleted, [])

    def test_active_foreign_and_mismatched_producers_are_preserved(self):
        for overrides in ({"status": "queued"}, {"status": "in_progress"}, {"workflow_id": 8},
                          {"path": ".github/workflows/release.yml"},
                          {"head_repository": {"full_name": "fork/book"}},
                          {"head_sha": "b" * 40}, {"event": "pull_request"}):
            with self.subTest(overrides=overrides):
                self.get("actions/runs/10", {**self.old, **overrides})
                self.assertEqual(storage.previews(self.api, 20, 1)["deleted"], [])
        self.assertEqual(self.deleted, [])

    def test_recheck_preserves_a_producer_that_becomes_active(self):
        seen = 0

        def mutate(path):
            nonlocal seen
            if path.endswith("/runs/10"):
                seen += 1
                if seen == 2:
                    self.get("actions/runs/10", {**self.old, "status": "in_progress", "run_attempt": 2})

        self.before_get = mutate
        storage.previews(self.api, 20, 1)
        self.assertEqual(self.deleted, [])

    def test_replacement_disappearance_fails_closed(self):
        self.get("actions/artifacts/200", {}, 404)
        with self.assertRaises(GitHubError):
            storage.previews(self.api, 20, 1)
        self.assertEqual(self.deleted, [])

    def test_artifact_id_mismatch_fails_closed(self):
        self.get("actions/artifacts/200", dict(self.replacement, id=999))
        with self.assertRaisesRegex(PolicyError, "changed"):
            storage.previews(self.api, 20, 1)
        self.assertEqual(self.deleted, [])

    def test_reverse_completions_preserve_later_upload_even_with_lower_run_id(self):
        later = self.artifact(self.old, 100, "2026-11-27T13:00:00Z")
        self.pages("actions/artifacts", "artifacts", [later, self.replacement])
        storage.previews(self.api, 20, 1)
        self.assertEqual(self.deleted, [])
        # Now the older-started run completes with the later upload: it can replace run 20.
        self.pages("actions/runs/10/artifacts", "artifacts", [later])
        self.pages("actions/runs/10/attempts/1/jobs", "jobs", [
            {"status": "completed", "conclusion": "success",
             "steps": [{"name": "Upload book preview", "conclusion": "success"}]}])
        self.get("actions/artifacts/100", later)
        storage.previews(self.api, 10, 1)
        self.assertEqual(self.deleted, [200])

    def publication(self, **overrides):
        self.release = {"tag_name": TAG, "draft": False, "prerelease": False,
                        "assets": [{"name": "gh-aw-book-v1.2.pdf", "state": "uploaded",
                                    "size": 3, "digest": DIGEST}], **overrides}
        self.get(f"releases/tags/{TAG}", self.release)
        self.get(f"git/ref/tags/{TAG}", {"object": {"type": "tag", "sha": "b" * 40}})
        self.get("git/tags/" + "b" * 40, {"object": {"type": "commit", "sha": SHA}})

    def stage(self, kind="release"):
        self.new = self.producer(20, path=".github/workflows/release.yml", head_branch="main",
                            status="in_progress", conclusion=None)
        self.get("actions/runs/20", self.new)
        self.staged = self.artifact(self.new, 201, "2026-11-27T12:00:00Z", name=f"validated-{kind}")
        self.get("actions/artifacts/201", self.staged)
        self.pages("actions/runs/20/artifacts", "artifacts", [
            self.staged, dict(self.staged, id=202, name="diagnostics")])
        self.steps("Verify published PDF integrity", "Smoke test the live site")
        self.publication()

    def clean_stage(self, **kwargs):
        with patch.dict(os.environ, GITHUB_RUN_ID="20"):
            return storage.staging(self.api, 20, kwargs.pop("kind", "release"),
                                   TAG, kwargs.pop("sha", SHA), kwargs.pop("digest", DIGEST))

    def test_staging_cleanup_requires_confirmed_publication_and_exact_integrity(self):
        self.stage()
        self.assertEqual(self.clean_stage()["deleted"], [201])
        self.assertEqual(self.deleted, [201])

    def test_failed_incomplete_or_unverified_publication_retains_recovery(self):
        self.stage()
        for change in ({"draft": True}, {"prerelease": True}, {"assets": []},
                       {"assets": [dict(self.release["assets"][0], state="new")]},
                       {"assets": [dict(self.release["assets"][0], digest="sha256:" + "0" * 64)]},
                       {"assets": [dict(self.release["assets"][0], digest=None)]}):
            with self.subTest(change=change):
                self.publication(**change)
                with self.assertRaises((PolicyError, ReleaseError)):
                    self.clean_stage()
        self.assertEqual(self.deleted, [])

    def test_failed_consumer_and_missing_proof_preserve_staging(self):
        self.stage()
        self.steps("Verify published PDF integrity", conclusion="failure")
        with self.assertRaises(PolicyError):
            self.clean_stage()
        self.steps("Verify published PDF integrity")
        with self.assertRaises(PolicyError):
            self.clean_stage(digest="")
        with self.assertRaises(PolicyError):
            self.clean_stage(sha="c" * 40)
        self.assertEqual(self.deleted, [])

    def test_pages_cleanup_requires_successful_smoke_and_only_removes_pages_transfer(self):
        self.stage("pages")
        self.steps("Smoke test the live site", conclusion="failure")
        with self.assertRaises(PolicyError):
            self.clean_stage(kind="pages", sha=None, digest=None)
        self.steps("Smoke test the live site")
        self.clean_stage(kind="pages", sha=None, digest=None)
        self.assertEqual(self.deleted, [201])

    def test_verify_compares_published_asset_to_local_validated_pdf(self):
        self.publication()
        with tempfile.TemporaryDirectory() as folder:
            pdf = Path(folder) / "book.pdf"
            pdf.write_bytes(b"PDF")
            self.assertEqual(storage.verify(self.api, TAG, SHA, asset_file=pdf)["digest"], DIGEST)
            pdf.write_bytes(b"BAD")
            with self.assertRaisesRegex(PolicyError, "digest differs"):
                storage.verify(self.api, TAG, SHA, asset_file=pdf)

    def test_delete_error_is_not_reported_as_success_in_cli(self):
        self.delete_status[f"/repos/{REPO}/actions/artifacts/100"] = (403, {"message": "forbidden"})
        env = {**os.environ, "GITHUB_REPOSITORY": REPO, "GH_TOKEN": "test",
               "GITHUB_API_URL": self.api.api_url}
        result = subprocess.run(
            [sys.executable, str(helpers.ROOT / "artifact_storage.py"), "previews",
             "--run-id", "20", "--attempt", "1"], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("ERROR: GitHub API", result.stderr)
        self.assertNotIn('"deleted"', result.stdout)
        self.assertEqual(self.deleted, [])


if __name__ == "__main__":
    unittest.main()
