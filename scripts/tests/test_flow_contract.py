"""Book release flow contract v1: the workflow surface that must be identical in every book repo.

Stdlib only. Text-level checks on .github/workflows/*.yml and RELEASING.md, so the same file
runs unchanged in all four repositories. Per-book differences (format, version scheme, tag
format, content allowlist, evidence rules, deploy target) are allowed behind this surface and
are listed in RELEASING.md under "Per-book settings".
"""
import os
import re
import unittest
from pathlib import Path


def repo_root():
    if os.environ.get("BOOK_REPO_ROOT"):
        return Path(os.environ["BOOK_REPO_ROOT"]).resolve()
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".github" / "workflows").is_dir():
            return parent
    raise RuntimeError("repository root not found")


ROOT = repo_root()
WF = ROOT / ".github" / "workflows"


def text(name):
    path = WF / name
    if not path.is_file():
        raise AssertionError(f".github/workflows/{name} is missing")
    return path.read_text(encoding="utf-8")


def top_level(body, key):
    """Return the raw text of a top-level `key:` block (up to the next top-level key)."""
    match = re.search(rf"^{re.escape(key)}:(.*?)(?=^\S|\Z)", body, re.M | re.S)
    return match.group(1) if match else ""


class FlowContract(unittest.TestCase):
    def test_workflow_files_and_names(self):
        for name, title in {
            "ci.yml": "Book CI",
            "book-approval-signal.yml": "Book approval signal",
            "approved-book.yml": "Release approved book",
            "release.yml": "Release book",
        }.items():
            self.assertRegex(text(name), rf"(?m)^name:\s*[\"']?{re.escape(title)}[\"']?\s*$", name)
        deploys = [n for n in ("deploy-swa.yml", "deploy-pages.yml") if (WF / n).is_file()]
        self.assertEqual(len(deploys), 1, f"exactly one deploy workflow expected, found {deploys}")

    def test_ci_has_the_required_aggregate_check(self):
        body = text("ci.yml")
        self.assertRegex(body, r"(?m)^\s+pull_request:")
        self.assertRegex(body, r"(?m)^\s+push:")
        self.assertRegex(body, r"(?m)^\s+name:\s*[\"']?Book release preflight[\"']?\s*$")

    def test_signal_workflow_relays_reviews(self):
        body = text("book-approval-signal.yml")
        self.assertIn("pull_request_review", top_level(body, "on"))

    def test_controller_surface(self):
        body = text("approved-book.yml")
        on = top_level(body, "on")
        self.assertIn("workflow_run:", on)
        self.assertRegex(on, r"Book approval signal")
        self.assertRegex(on, r"Book CI")
        self.assertIn("issue_comment:", on)
        self.assertRegex(on, r"cron:\s*[\"']17,47 \* \* \* \*[\"']")
        dispatch = on[on.index("workflow_dispatch:"):]
        self.assertRegex(dispatch, r"(?m)^\s+pr:\s*$")
        self.assertRegex(body, r"(?m)^permissions:\s*\{\}\s*$")
        self.assertRegex(top_level(body, "concurrency"), r"group:\s*approved-book")
        self.assertRegex(top_level(body, "concurrency"), r"cancel-in-progress:\s*false")
        self.assertIn("refs/heads/main", body, "controller jobs must run only from main")
        self.assertRegex(body, r"/release-book ")

    def test_release_workflow_is_dispatch_only_with_fixed_inputs(self):
        body = text("release.yml")
        on = top_level(body, "on")
        self.assertIn("workflow_dispatch:", on)
        for forbidden in ("push:", "pull_request", "workflow_call:", "release:", "schedule:"):
            self.assertNotIn(forbidden, on, f"release.yml must be dispatch-only, found {forbidden}")
        for name in ("pr", "head_sha", "base_sha", "merge_sha", "tag"):
            self.assertRegex(on, rf"(?m)^\s+{name}:\s*$", f"missing input {name}")
        self.assertRegex(body, r"(?m)^permissions:\s*\{\}\s*$")
        self.assertRegex(top_level(body, "concurrency"), r"group:\s*book-publish")
        self.assertRegex(top_level(body, "concurrency"), r"cancel-in-progress:\s*false")
        self.assertIn("refs/heads/main", body, "release jobs must run only from main")
        self.assertNotIn("--clobber", body)

    def test_production_deploy_serves_released_content_only(self):
        name = "deploy-swa.yml" if (WF / "deploy-swa.yml").is_file() else "deploy-pages.yml"
        body = text(name)
        self.assertRegex(body, r"(?m)^\s+published-source:\s*$", "missing the published-source gate job")
        self.assertRegex(body, r"needs:\s*(\[[^\]]*published-source[^\]]*\]|published-source)")
        self.assertNotIn("--clobber", body)

    def test_pinned_runner_and_action_majors_in_contract_workflows(self):
        majors = {
            "actions/checkout": "7",
            "actions/setup-python": "7",
            "actions/upload-artifact": "7",
            "actions/download-artifact": "8",
        }
        names = ["ci.yml", "book-approval-signal.yml", "approved-book.yml", "release.yml"]
        names += [n for n in ("deploy-swa.yml", "deploy-pages.yml") if (WF / n).is_file()]
        for name in names:
            body = text(name)
            self.assertNotRegex(body, r"runs-on:\s*ubuntu-latest", f"{name}: pin ubuntu-24.04")
            for action, ref, comment in re.findall(r"uses:\s*(actions/[\w-]+)@(\S+)(?:\s+#\s*(\S+))?", body):
                if action not in majors:
                    continue
                version = comment.lstrip("v") if re.fullmatch(r"[0-9a-f]{40}", ref) else ref.lstrip("v")
                self.assertEqual(version.split(".")[0], majors[action], f"{name}: {action} must be v{majors[action]}")

    def test_main_push_deploy_is_gated_and_dispatch_takes_a_tag(self):
        name = "deploy-swa.yml" if (WF / "deploy-swa.yml").is_file() else "deploy-pages.yml"
        on = top_level(text(name), "on")
        self.assertIn("workflow_dispatch:", on)
        self.assertRegex(on, r"(?m)^\s+(ref|sha):\s*$", "dispatch must take the released ref or sha")

    def test_docs_state_the_contract_and_the_retry_commands(self):
        body = (ROOT / "RELEASING.md").read_text(encoding="utf-8")
        self.assertIn("Book release flow contract v1", body)
        self.assertIn("Per-book settings", body)
        self.assertIn("gh workflow run approved-book.yml -f pr=", body)
        self.assertIn("gh workflow run release.yml", body)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("RELEASING.md", readme)


if __name__ == "__main__":
    unittest.main()
