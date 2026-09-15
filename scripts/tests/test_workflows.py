import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


class WorkflowTests(unittest.TestCase):
    def workflow(self, name):
        return yaml.load(
            (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8"),
            Loader=yaml.BaseLoader,
        )

    def test_validation_is_reusable_and_runs_on_pull_requests(self):
        workflow = self.workflow("validate-book.yml")
        self.assertIn("pull_request", workflow["on"])
        self.assertIn("workflow_call", workflow["on"])
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        steps = workflow["jobs"]["validate"]["steps"]
        commands = "\n".join(step.get("run", "") for step in steps)
        for required in ("unittest discover", "release_content.py --root source check",
                         "gh extension install github/gh-aw --pin", "verify_examples.py",
                         "site/generate.py", "scripts/build_pdf.py", "check-generated"):
            self.assertIn(required, commands)
        self.assertNotIn("record-review", commands)
        self.assertIn("APPINSIGHTS_CONNECTION_STRING", str(steps))

    def test_both_publishers_require_validation_and_consume_its_artifact(self):
        for name, publisher in (("deploy-pages.yml", "deploy"), ("release-content.yml", "release")):
            with self.subTest(workflow=name):
                workflow = self.workflow(name)
                self.assertEqual(workflow["permissions"], {"contents": "read"})
                jobs = workflow["jobs"]
                self.assertEqual(jobs["validate"]["uses"], "./.github/workflows/validate-book.yml")
                self.assertIn("validate", jobs[publisher]["needs"])
                self.assertEqual(jobs[publisher]["permissions"], {"contents": "write"})
                steps = jobs[publisher]["steps"]
                self.assertTrue(any(step.get("uses", "").startswith("actions/download-artifact@") for step in steps))
                self.assertFalse(any("scripts/build_pdf.py" in step.get("run", "") for step in steps))
                self.assertIn("examples/**", workflow["on"]["push"]["paths"])

    def test_release_repairs_use_explicit_source_and_never_clobber(self):
        jobs = self.workflow("release-content.yml")["jobs"]
        self.assertIn("source_sha", jobs["validate"]["with"]["source-ref"])
        self.assertIn("comparison_base", jobs["validate"]["with"]["comparison-base"])
        commands = "\n".join(step.get("run", "") for step in jobs["release"]["steps"])
        self.assertIn("--verify-tag", commands)
        self.assertIn("ACTUAL_SHA", commands)
        self.assertNotIn("--clobber", commands)
        self.assertNotIn("--target", commands)


if __name__ == "__main__":
    unittest.main()
