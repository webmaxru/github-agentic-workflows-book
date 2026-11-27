import re
import unittest
from pathlib import Path
from unittest.mock import MagicMock

import yaml

from helpers import ROOT as SCRIPTS  # noqa: F401  (puts scripts/ on sys.path)

import approved_book as policy

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
CONTRACT = ("ci.yml", "book-approval-signal.yml", "approved-book.yml", "release.yml", "deploy-pages.yml")
MAIN = "github.ref == 'refs/heads/main'"


def text(name):
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def load(name):
    return yaml.load(text(name), Loader=yaml.BaseLoader)


def commands(job):
    return "\n".join(step.get("run", "") for step in job.get("steps", []))


def listed(value):
    return [value] if isinstance(value, str) else list(value or [])


class WorkflowTests(unittest.TestCase):
    def test_every_workflow_parses_and_workflow_run_names_resolve(self):
        names = {path.name: load(path.name).get("name") for path in sorted(WORKFLOWS.glob("*.yml"))}
        self.assertTrue(all(names.values()), names)
        for name in names:
            for upstream in load(name)["on"].get("workflow_run", {}).get("workflows", []):
                self.assertIn(upstream, names.values(), f"{name} waits for a workflow that does not exist")
        self.assertEqual(load("approved-book.yml")["on"]["workflow_run"]["workflows"],
                         ["Book approval signal", "Book CI"])

    def test_old_workflow_names_and_inputs_are_gone_from_tooling_and_docs(self):
        stale = ("validate-book.yml", "release-approved-book", "book-review-signal.yml",
                 "release-content.yml", "Check book update", "-f pull-request=", "pull-request:")
        scanned = [ROOT / "README.md", ROOT / "RELEASING.md"]
        for folder in (ROOT / ".github", ROOT / "scripts"):
            scanned += [path for path in folder.rglob("*")
                        if path.is_file() and path.suffix in {".yml", ".md", ".py", ".ps1"}
                        and "__pycache__" not in path.parts
                        and not path.name.startswith("scan-gh-aw-updates")
                        and path.name != Path(__file__).name]
        for path in scanned:
            body = path.read_text(encoding="utf-8", errors="replace")
            for old in stale:
                self.assertNotIn(old, body, f"{path.relative_to(ROOT)} still mentions {old}")

    def test_ci_is_reusable_runs_on_pull_requests_and_pushes_and_names_the_aggregate_check(self):
        workflow = load("ci.yml")
        self.assertEqual(workflow["name"], "Book CI")
        for trigger in ("pull_request", "push", "workflow_call"):
            self.assertIn(trigger, workflow["on"])
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        job = workflow["jobs"]["validate"]
        self.assertEqual(job["name"], "Book release preflight")
        run = commands(job)
        for required in ("unittest discover", "release_content.py --root source check",
                         "gh extension install github/gh-aw --pin", "verify_examples.py",
                         "site/generate.py", "scripts/build_pdf.py", "check-generated"):
            self.assertIn(required, run)
        self.assertNotIn("record-review", run)
        self.assertIn("APPINSIGHTS_CONNECTION_STRING", str(job["steps"]))

    def test_browser_install_and_pdf_render_have_separate_bounds(self):
        steps = load("ci.yml")["jobs"]["validate"]["steps"]
        install = next(step for step in steps if "playwright install" in step.get("run", ""))
        render = next(step for step in steps if "scripts/build_pdf.py" in step.get("run", ""))
        self.assertNotIn("--with-deps", install["run"])
        self.assertEqual(install["timeout-minutes"], "5")
        self.assertEqual(render["timeout-minutes"], "5")
        self.assertEqual(render["working-directory"], "source")

    def test_both_publishers_require_validation_and_consume_its_artifact(self):
        for name, publisher in (("deploy-pages.yml", "deploy"), ("release.yml", "release")):
            with self.subTest(workflow=name):
                workflow = load(name)
                self.assertEqual(workflow["permissions"], {})
                jobs = workflow["jobs"]
                self.assertEqual(jobs["validate"]["uses"], "./.github/workflows/ci.yml")
                self.assertIn("validate", listed(jobs[publisher]["needs"]))
                self.assertEqual(jobs[publisher]["permissions"]["contents"], "write")
                steps = jobs[publisher]["steps"]
                self.assertTrue(any(step.get("uses", "").startswith("actions/download-artifact@") for step in steps))
                self.assertFalse(any("scripts/build_pdf.py" in step.get("run", "") for step in steps))

    def test_release_is_dispatch_only_with_the_five_inputs(self):
        release = load("release.yml")
        self.assertEqual(release["name"], "Release book")
        self.assertEqual(set(release["on"]), {"workflow_dispatch"})
        inputs = release["on"]["workflow_dispatch"]["inputs"]
        self.assertEqual(set(inputs), {"pr", "head_sha", "base_sha", "merge_sha", "tag"})
        self.assertTrue(all(item["required"] == "true" for item in inputs.values()))
        self.assertEqual(release["concurrency"], {"group": "book-publish", "cancel-in-progress": "false"})

    def test_release_uses_explicit_source_and_never_clobbers_or_moves_a_tag(self):
        jobs = load("release.yml")["jobs"]
        self.assertEqual(jobs["validate"]["with"]["source-ref"], "${{ inputs.merge_sha }}")
        self.assertIn("comparison", jobs["validate"]["with"]["comparison-base"])
        self.assertEqual(jobs["validate"]["with"]["require-content-change"], "true")
        run = commands(jobs["release"])
        for token in ("publish_release.py tag", "--verify-tag", "--draft", "--draft=false"):
            self.assertIn(token, run)
        for forbidden in ("--clobber", "--target", "git tag", "--force"):
            self.assertNotIn(forbidden, run)
        for name in ("release.yml", "deploy-pages.yml", "approved-book.yml"):
            self.assertNotIn("--clobber", text(name))
        order = [run.index(token) for token in ("publish_release.py tag", "gh release create",
                                                "gh release upload", "--draft=false")]
        self.assertEqual(order, sorted(order), "tag, draft, upload, publish must run in that order")

    def test_complete_recovery_skips_build_publication_and_pages(self):
        jobs = load("release.yml")["jobs"]
        for name in ("validate", "release"):
            self.assertEqual(jobs[name]["if"], MAIN + " && needs.plan.outputs.action == 'create'")
        self.assertIn("release", jobs["pages"]["needs"])
        self.assertEqual(jobs["pages"]["if"], MAIN + " && needs.release.result == 'success' "
                         "&& needs.release.outputs.latest == 'true'")

    def test_pages_uses_the_latest_decision_of_the_successful_publish_step(self):
        jobs = load("release.yml")["jobs"]
        self.assertNotIn("latest", jobs["plan"]["outputs"])
        self.assertEqual(jobs["release"]["outputs"]["latest"], "${{ steps.publish.outputs.latest }}")
        steps = jobs["release"]["steps"]
        publish = next(step["run"] for step in steps if step.get("id") == "publish")
        self.assertLess(publish.index("publish_release.py latest"), publish.index('gh release edit'))
        self.assertLess(publish.index('--latest="$latest"'), publish.index('"latest=$latest" >> "$GITHUB_OUTPUT"'))
        for step in steps:
            if "gh release " in step.get("run", ""):
                self.assertNotIn("if", step, "a new publication must create the draft, upload, then publish")
                self.assertNotIn("continue-on-error", step)

    def test_release_deploys_its_own_tag_through_the_gated_deploy_workflow(self):
        pages = load("release.yml")["jobs"]["pages"]
        self.assertEqual(pages["uses"], "./.github/workflows/deploy-pages.yml")
        self.assertEqual(pages["with"], {"published-tag": "${{ needs.plan.outputs.tag }}"})
        self.assertEqual(pages["permissions"], {"contents": "write", "pages": "write"})

    def test_controller_triggers_permissions_and_concurrency(self):
        controller = load("approved-book.yml")
        self.assertEqual(controller["name"], "Release approved book")
        self.assertEqual(set(controller["on"]), {"workflow_run", "issue_comment", "workflow_dispatch", "schedule"})
        self.assertEqual(controller["on"]["schedule"], [{"cron": "17,47 * * * *"}])
        self.assertEqual(list(controller["on"]["workflow_dispatch"]["inputs"]), ["pr"])
        self.assertEqual(controller["permissions"], {})
        self.assertEqual(controller["concurrency"], {"group": "approved-book", "cancel-in-progress": "false"})
        signal = load("book-approval-signal.yml")
        self.assertEqual(signal["name"], "Book approval signal")
        self.assertEqual(signal["permissions"], {})
        self.assertIn("pull_request_review", signal["on"])

    def test_controller_chain_is_preflight_then_merge_then_dispatch(self):
        jobs = load("approved-book.yml")["jobs"]
        self.assertIn("preflight", listed(jobs["merge"]["needs"]))
        self.assertEqual(jobs["preflight"]["uses"], "./.github/workflows/ci.yml")
        self.assertEqual(jobs["preflight"]["with"]["require-content-change"], "true")
        self.assertEqual(jobs["preflight"]["with"]["source-ref"], "${{ needs.select.outputs.head }}")
        self.assertIn("source-sha == needs.select.outputs.head", jobs["merge"]["if"])
        self.assertIn("approved_book.py merge", commands(jobs["merge"]))
        self.assertIn("approved_book.py dispatch", commands(jobs["dispatch"]))
        self.assertIn("merge", listed(jobs["dispatch"]["needs"]))
        # Recovery of an already merged pull request skips the merge but still dispatches the release.
        self.assertIn("needs.select.outputs.merge-sha != ''", jobs["dispatch"]["if"])
        self.assertIn("merge-sha == ''", jobs["merge"]["if"])

    def test_the_dispatch_script_sends_exactly_the_inputs_release_declares(self):
        api = MagicMock(repo="owner/book")
        policy.dispatch(api, 7, "a" * 40, "b" * 40, "c" * 40, "content-v1.2")
        path, method, body = api.request.call_args.args
        self.assertEqual((method, body["ref"]), ("POST", "main"))
        self.assertTrue(path.endswith(f"/actions/workflows/{policy.RELEASE_WORKFLOW}/dispatches"))
        self.assertTrue((WORKFLOWS / policy.RELEASE_WORKFLOW).is_file())
        self.assertEqual(set(body["inputs"]), set(load("release.yml")["on"]["workflow_dispatch"]["inputs"]))

    def test_owner_comment_triggers_only_for_the_owner_and_the_release_command(self):
        condition = load("approved-book.yml")["jobs"]["select"]["if"]
        self.assertIn("github.event.comment.user.login == 'webmaxru'", condition)
        self.assertIn("startsWith(github.event.comment.body, '/release-book ')", condition)
        self.assertIn("github.event.action != 'deleted'", condition)

    def test_every_job_runs_only_from_main(self):
        for name in ("approved-book.yml", "release.yml", "deploy-pages.yml"):
            jobs = load(name)["jobs"]

            def guarded(job_name):
                job = jobs[job_name]
                if MAIN in job.get("if", ""):
                    return True
                return "always()" not in job.get("if", "") and any(guarded(n) for n in listed(job.get("needs")))

            for job_name in jobs:
                with self.subTest(workflow=name, job=job_name):
                    self.assertTrue(guarded(job_name), f"{name}:{job_name} must only run from main")

    def test_validators_and_controller_code_never_come_from_pull_request_code(self):
        for name in ("approved-book.yml", "release.yml", "deploy-pages.yml", "book-approval-signal.yml"):
            body = text(name)
            self.assertNotIn("pull_request_target", body)
            self.assertNotRegex(body, r"python\s+source/", f"{name} must not execute pull request code")
            self.assertNotRegex(body, r"github\.event\.pull_request\.head", f"{name} must not use the PR head")
            for job_name, job in load(name)["jobs"].items():
                for step in job.get("steps", []):
                    if step.get("uses", "").startswith("actions/checkout@"):
                        with_ = step.get("with", {})
                        if with_.get("path") == "source":
                            continue
                        # No ref means the event commit, which the main guard makes a commit of main.
                        explicit = with_.get("ref") == "main"
                        self.assertTrue(explicit or MAIN in job.get("if", ""),
                                        f"{name}:{job_name} control code must come from main")
        # ci.yml checks the book source out separately from the trusted validators and runs only the latter.
        source = text("ci.yml")
        self.assertIn("path: tooling", source)
        self.assertNotRegex(source, r"python\s+source/scripts/(release_content|approved_book|verify_examples)")
        self.assertIn("python tooling/scripts/release_content.py", source)

    def test_deploy_gate_is_published_source_and_the_script_owns_the_content_paths(self):
        jobs = load("deploy-pages.yml")["jobs"]
        self.assertIn("published-source", listed(jobs["validate"]["needs"]))
        self.assertIn("published-source", listed(jobs["deploy"]["needs"]))
        self.assertIn("deploy_gate.py gate", commands(jobs["published-source"]))
        body = text("deploy-pages.yml")
        self.assertNotIn("git diff", body)
        self.assertNotRegex(body, r"\bcontent examples\b|\bexamples/\*\*")
        self.assertEqual(jobs["validate"]["with"]["source-ref"], "${{ needs.published-source.outputs.sha }}")
        self.assertIn('test "$VALIDATED_SHA" = "$SOURCE_SHA"', commands(jobs["deploy"]))

    def test_manual_deploy_takes_a_released_ref_and_the_release_can_call_it(self):
        workflow = load("deploy-pages.yml")
        triggers = workflow["on"]
        self.assertEqual(list(triggers["workflow_dispatch"]["inputs"]), ["ref"])
        self.assertEqual(triggers["workflow_dispatch"]["inputs"]["ref"]["required"], "false")
        self.assertEqual(list(triggers["workflow_call"]["inputs"]), ["published-tag"])
        self.assertEqual(triggers["workflow_call"]["inputs"]["published-tag"]["required"], "true")
        self.assertIn('--ref "$REF"', commands(workflow["jobs"]["published-source"]))
        self.assertIn('--require-latest', commands(workflow["jobs"]["published-source"]))
        self.assertIn('--ref "$RELEASE_TAG" --require-latest', commands(workflow["jobs"]["deploy"]))

    def test_main_tip_is_asserted_only_when_deploying_main(self):
        run = commands(load("deploy-pages.yml")["jobs"]["deploy"])
        self.assertRegex(run, r'if \[\[ "\$DEPLOY_MODE" == "main" \]\]; then[^\n]*\n(\s*#[^\n]*\n)?[^\n]*commits/main')

    def test_legacy_pages_build_is_explicit_checked_and_smoke_tested(self):
        deploy = load("deploy-pages.yml")["jobs"]["deploy"]
        self.assertEqual(deploy["permissions"], {"contents": "write", "pages": "write"})
        self.assertEqual(deploy["concurrency"], {"group": "deploy-gh-pages", "cancel-in-progress": "false"})
        run = commands(deploy)
        self.assertIn("publish_pages.py", run)
        self.assertIn('build --commit "$DEPLOY_SHA"', run)
        self.assertIn("gh-aw-book.pdf", run)
        self.assertIn("deploy_gate.py smoke", run)
        self.assertLess(run.index("gh-aw-book.pdf"), run.index("git push"))

    def test_contract_pins_are_applied_to_every_contract_workflow(self):
        majors = {"actions/checkout": "7", "actions/setup-python": "7",
                  "actions/upload-artifact": "7", "actions/download-artifact": "8"}
        for name in CONTRACT:
            body = text(name)
            self.assertNotRegex(body, r"runs-on:\s*ubuntu-(latest|slim)", name)
            for action, ref in re.findall(r"uses:\s*(actions/[\w-]+)@(\S+)", body):
                if action in majors:
                    self.assertEqual(ref.lstrip("v").split(".")[0], majors[action], f"{name}: {action}")


if __name__ == "__main__":
    unittest.main()
