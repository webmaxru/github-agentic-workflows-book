"""End-to-end rehearsal of the book release flow against a loopback GitHub API.

A real temporary git repository stands behind tests/github_fake.py (pull request, reviews, checks,
releases, tags, workflow dispatches); the real CLIs run as subprocesses exactly as the workflows
call them: approved_book.py select/merge/dispatch/verify-merged, release_content.py release-plan,
publish_release.py latest/tag, deploy_gate.py gate, and the gh release commands (through a shim).
The dispatched inputs are checked against what release.yml really declares.
"""

import json
import os
import re
import subprocess
import sys
import unittest

import yaml

import helpers
from github_fake import FakeGitHub

SCRIPTS = helpers.ROOT
WORKFLOWS = SCRIPTS.parent / ".github" / "workflows"
SHIM = SCRIPTS / "tests" / "gh_shim.py"
REPOSITORY = "webmaxru/github-agentic-workflows-book"
OWNER, CONTRIBUTOR = "webmaxru", "contributor"
PDF = "gh-aw-book-v1.2.pdf"
RELEASE_CONTENT = (
    "import sys; sys.path.insert(0, sys.argv[1]); import release_content as r; "
    "r.GH = [sys.executable, sys.argv[2]]; raise SystemExit(r.main(sys.argv[3:]))"
)


def declared_inputs(name):
    document = yaml.load((WORKFLOWS / name).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    return set(document["on"]["workflow_dispatch"]["inputs"])


class Rehearsal(helpers.RepositoryTest):
    def setUp(self):
        super().setUp()
        self.git("branch", "-M", "main")
        self.git("checkout", "--quiet", "-b", "book-update")
        self.put("content/VERSION", "1.2\n")
        self.put("content/CHANGELOG.md",
                 "## [1.2] - 2026-07-09\n\nA revised chapter.\n\n## [1.1] - 2026-07-08\n\nExisting edition.\n")
        self.put("content/chapters/one.html", "<p>A revised chapter.</p>\n")
        self.accept()
        self.commit()
        self.head = self.git("rev-parse", "HEAD")
        self.git("checkout", "--quiet", "main")

        self.fake = FakeGitHub(self.root, REPOSITORY, {"release.yml": declared_inputs("release.yml")})
        self.fake.publish("content-v1.1", ["gh-aw-book-v1.1.pdf"])
        self.addCleanup(self.fake.stop)
        self.addCleanup(lambda: self.assertEqual(self.fake.errors, []))
        self.env = {**os.environ, "GITHUB_API_URL": self.fake.start(),
                    "GITHUB_REPOSITORY": REPOSITORY, "GH_TOKEN": "test-token"}
        self.work = self.root / "build" / "work"
        self.work.mkdir(parents=True)
        self.summary = self.work / "summary.md"
        self.env["GITHUB_STEP_SUMMARY"] = str(self.summary)

    # ------------------------------------------------------------------ plumbing
    def run_script(self, script, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *args], cwd=self.root,
                              env=self.env, capture_output=True, text=True, encoding="utf-8")

    def json_of(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def refused(self, result, pattern):
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertRegex(result.stderr, pattern)

    def gh(self, *args):
        return subprocess.run([sys.executable, str(SHIM), *args], cwd=self.work, env=self.env,
                              capture_output=True, text=True, encoding="utf-8")

    def release_content(self, root, *args):
        return subprocess.run(
            [sys.executable, "-c", RELEASE_CONTENT, str(SCRIPTS), str(SHIM), "--root", str(root), *args],
            cwd=root, env=self.env, capture_output=True, text=True, encoding="utf-8")

    def open_pr(self, author=CONTRIBUTOR, approved=True, **options):
        self.fake.open_pr(7, self.head, author, **options)
        self.fake.check(self.head)
        if approved and author != OWNER:
            self.fake.review(OWNER, "APPROVED")

    def select(self):
        return self.json_of(self.run_script("approved_book.py", "select"))

    def not_selected(self, reason):
        result = self.run_script("approved_book.py", "select")
        self.assertEqual(self.json_of(result), {})
        self.assertRegex(result.stderr, reason)
        self.assertEqual(self.fake.writes, [])
        self.assertNotIn("PUT", [method for method, _ in self.fake.requests])

    def advance(self, branch, files):
        """A new commit on ``branch``; returns the new tip."""
        self.git("checkout", "--quiet", branch)
        for name, text in files.items():
            self.put(name, text)
        self.commit()
        tip = self.git("rev-parse", "HEAD")
        self.git("checkout", "--quiet", "main")
        return tip

    def controller(self):
        """What approved-book.yml does: select, squash-merge, dispatch. Returns release.yml's inputs."""
        selected = self.select()
        merged = self.json_of(self.run_script(
            "approved_book.py", "merge", "--number", str(selected["number"]), "--head", selected["head"],
            "--base", selected["base"], "--comparison", selected["comparison"]))
        self.json_of(self.run_script(
            "approved_book.py", "dispatch", "--number", str(merged["number"]), "--head", merged["head"],
            "--base", merged["base"], "--merge-sha", merged["merge_sha"], "--tag", merged["tag"]))
        self.git("reset", "--quiet", "--hard")
        return self.fake.dispatches[-1]["inputs"]

    def verify(self, inputs, **override):
        values = {**inputs, **override}
        return self.run_script(
            "approved_book.py", "verify-merged", "--number", values["pr"], "--head", values["head_sha"],
            "--base", values["base_sha"], "--merge-sha", values["merge_sha"], "--tag", values["tag"])

    def source(self, inputs):
        path = self.root / "build" / f"source-{inputs['merge_sha'][:8]}"
        if not path.exists():
            self.git("worktree", "add", "--quiet", "--detach", str(path), inputs["merge_sha"])
        return path

    def plan(self, inputs):
        verified = self.json_of(self.verify(inputs))
        return self.release_content(
            self.source(inputs), "release-plan", "--repo", REPOSITORY, "--base", verified["comparison"],
            "--expected-source", inputs["merge_sha"])

    def latest(self, tag, action):
        return self.json_of(self.run_script("publish_release.py", "latest", "--tag", tag,
                                            "--plan-action", action))["latest"]

    def tag(self, inputs):
        return self.run_script("publish_release.py", "tag", "--tag", inputs["tag"], "--sha", inputs["merge_sha"])

    def prepare_assets(self, inputs):
        notes = self.release_content(self.source(inputs), "notes")
        self.assertEqual(notes.returncode, 0, notes.stderr)
        (self.work / "release-notes.md").write_text(notes.stdout, encoding="utf-8")
        (self.work / PDF).write_bytes(b"%PDF-1.7 rehearsal\n")

    LABEL = f"{PDF}#GitHub Agentic Workflows — v1.2 (PDF)"

    def create_draft(self):
        return self.gh("release", "create", "content-v1.2", "--repo", REPOSITORY, "--verify-tag",
                       "--draft", "--title", "Content v1.2", "--notes-file", "release-notes.md")

    def upload(self):
        return self.gh("release", "upload", "content-v1.2", self.LABEL, "--repo", REPOSITORY)

    def publish(self, latest="true"):
        return self.gh("release", "edit", "content-v1.2", "--repo", REPOSITORY, "--draft=false",
                       f"--latest={latest}")

    def gate(self, *args):
        return self.run_script("deploy_gate.py", "gate", "--root", str(self.root), *args)


class ControllerEligibility(Rehearsal):
    def test_an_approved_current_head_is_selected(self):
        self.open_pr()
        selected = self.select()
        self.assertEqual((selected["number"], selected["head"], selected["base"]), (7, self.head, self.base))
        self.assertEqual((selected["comparison"], selected["tag"]), ("content-v1.1", "content-v1.2"))

    def test_a_head_behind_main_is_never_merged_until_updated_and_approved_again(self):
        self.open_pr()
        self.advance("main", {"scripts/unrelated.txt": "main moved on\n"})
        self.not_selected("does not contain the current main")
        self.assertIn("PR #7: The head does not contain the current main",
                      self.summary.read_text(encoding="utf-8"))
        self.assertIn("update the branch from main, then approve the new head",
                      self.summary.read_text(encoding="utf-8"))
        refused = self.run_script("approved_book.py", "select", "--number", "7")
        self.refused(refused, "does not contain the current main")
        self.assertIn("::warning::PR #7:", refused.stderr)
        self.assertEqual(self.fake.writes, [])

        self.git("checkout", "--quiet", "book-update")
        self.git("-c", "user.name=Book Tests", "-c", "user.email=book-tests@example.invalid",
                 "-c", "commit.gpgsign=false", "merge", "--quiet", "--no-edit", "main")
        updated = self.git("rev-parse", "HEAD")
        self.git("checkout", "--quiet", "main")
        self.fake.pr["head"] = updated
        self.fake.check(updated)
        self.summary.unlink()
        self.not_selected("approval")
        self.assertFalse(self.summary.exists())
        self.fake.review(OWNER, "APPROVED", updated)
        self.assertEqual(self.select()["head"], updated)
        self.assertFalse(self.summary.exists())
        self.assertEqual(self.fake.writes, [])

    def test_a_push_after_approval_revokes_it(self):
        self.open_pr()
        pushed = self.advance("book-update", {"content/chapters/one.html": "<p>Changed after approval.</p>\n"})
        self.fake.pr["head"] = pushed
        self.fake.check(pushed)
        self.not_selected("approval")
        self.fake.review(OWNER, "APPROVED", pushed)
        self.assertEqual(self.select()["head"], pushed)

    def test_changes_requested_and_dismissal_are_barriers(self):
        self.open_pr()
        self.fake.review("reviewer", "CHANGES_REQUESTED")
        self.not_selected("approval")
        self.fake.review(OWNER, "APPROVED")
        self.assertEqual(self.select()["number"], 7)

        self.fake.dismiss_reviews()
        self.not_selected("approval")
        self.fake.review(OWNER, "APPROVED")
        self.assertEqual(self.select()["number"], 7)

    def test_only_the_owner_authorizes_someone_elses_pull_request(self):
        self.open_pr(approved=False)
        self.fake.review("another-maintainer", "APPROVED")
        self.not_selected("approval")
        self.fake.review(OWNER, "COMMENTED")
        self.not_selected("approval")

    def test_the_owners_own_pull_request_needs_an_exact_unedited_command(self):
        self.open_pr(author=OWNER)
        self.not_selected("approval")
        self.fake.comment(CONTRIBUTOR, f"/release-book {self.head}")
        self.not_selected("approval")
        self.fake.comment(OWNER, f"/release-book {'0' * 40}")
        self.not_selected("approval")
        edited = self.fake.comment(OWNER, f"/release-book {self.head}")
        edited["updated_at"] = self.fake.now()
        self.not_selected("approval")
        self.fake.comment(OWNER, f"/release-book {self.head}")
        self.assertEqual(self.select()["number"], 7)

        pushed = self.advance("book-update", {"content/chapters/one.html": "<p>Changed after the command.</p>\n"})
        self.fake.pr["head"] = pushed
        self.fake.check(pushed)
        self.not_selected("approval")

    def test_forks_drafts_and_unmergeable_pull_requests_are_refused(self):
        for options, reason in (({"same_repo": False}, "same-repository"), ({"draft": True}, "non-draft"),
                                ({"mergeable": False}, "not mergeable")):
            with self.subTest(**options):
                self.open_pr(**options)
                self.not_selected(reason)

    def test_the_preflight_must_be_green_on_the_exact_head(self):
        self.fake.open_pr(7, self.head, CONTRIBUTOR)
        self.fake.review(OWNER, "APPROVED")
        self.not_selected("preflight")
        self.fake.check(self.base)
        self.not_selected("preflight")
        self.fake.check(self.head, conclusion="failure")
        self.not_selected("preflight")
        self.fake.checks[self.head] = []
        self.fake.check(self.head, slug="some-other-app")
        self.not_selected("preflight")
        self.fake.check(self.head)
        self.assertEqual(self.select()["number"], 7)

    def test_files_outside_the_content_allowlist_are_refused(self):
        self.open_pr()
        pushed = self.advance("book-update", {"scripts/release_content.py": "# tooling edited in a content PR\n"})
        self.fake.pr["head"] = pushed
        self.fake.check(pushed)
        self.fake.review(OWNER, "APPROVED", pushed)
        self.not_selected(r"mixes book content with tooling \(scripts/release_content\.py\)")


class ControllerMerge(Rehearsal):
    def test_main_moving_after_selection_still_blocks_the_merge(self):
        self.open_pr()
        selected = self.select()
        advanced = self.advance("main", {"scripts/unrelated.txt": "merged during preflight\n"})
        result = self.run_script(
            "approved_book.py", "merge", "--number", "7", "--head", selected["head"],
            "--base", selected["base"], "--comparison", selected["comparison"])
        self.refused(result, "does not contain the current main")
        self.assertIn("::warning::PR #7:", result.stderr)
        self.assertIn("update the branch from main, then approve the new head",
                      self.summary.read_text(encoding="utf-8"))
        self.assertEqual(self.fake.writes, [])
        self.assertFalse(self.fake.dispatches)
        self.assertEqual(self.git("rev-parse", "main"), advanced)

    def test_the_squash_merge_is_conditioned_on_the_approved_head(self):
        self.open_pr()
        selected = self.select()
        pushed = self.advance("book-update", {"content/chapters/one.html": "<p>Pushed during the merge.</p>\n"})
        self.fake.before_merge = lambda: self.fake.pr.update(head=pushed)
        self.refused(self.run_script(
            "approved_book.py", "merge", "--number", "7", "--head", selected["head"],
            "--base", selected["base"], "--comparison", selected["comparison"]), "409")
        self.assertEqual(self.fake.writes, [])
        self.assertEqual(self.git("rev-parse", "main"), self.base)

    def test_the_merge_is_a_squash_of_exactly_the_approved_head(self):
        self.open_pr()
        self.fake.review(OWNER, "COMMENTED")
        inputs = self.controller()
        self.assertEqual(self.git("rev-parse", "main"), inputs["merge_sha"])
        self.assertEqual(self.git("rev-parse", f"{inputs['merge_sha']}^{{tree}}"),
                         self.git("rev-parse", f"{self.head}^{{tree}}"))
        self.assertEqual(self.git("rev-list", "--parents", "-n", "1", inputs["merge_sha"]).split()[1:],
                         [self.base])

    def test_merge_rechecks_the_owner_command_after_selection(self):
        self.open_pr(author=OWNER)
        command = self.fake.comment(OWNER, f"/release-book {self.head}")
        selected = self.select()
        merge_args = ("approved_book.py", "merge", "--number", "7", "--head", selected["head"],
                      "--base", selected["base"], "--comparison", selected["comparison"])
        self.fake.comment(OWNER, "Ready for review")
        self.fake.comment(OWNER, f"/release-book {self.head}\n")
        command["updated_at"] = self.fake.now()
        self.refused(self.run_script(*merge_args), "approval")
        self.assertEqual(self.fake.writes, [])
        self.assertEqual(self.git("rev-parse", "main"), self.base)

        self.fake.comment(OWNER, f"/release-book {self.head}")
        self.fake.comment(OWNER, "/release-book not-a-sha")
        self.assertEqual(self.json_of(self.run_script(*merge_args))["head"], selected["head"])

    def test_the_controller_dispatches_release_yml_with_exactly_the_declared_inputs(self):
        self.open_pr()
        inputs = self.controller()
        self.assertEqual(self.fake.dispatches[0]["workflow"], "release.yml")
        self.assertEqual(self.fake.dispatches[0]["ref"], "main")
        self.assertEqual(set(inputs), declared_inputs("release.yml"))
        self.assertEqual(inputs, {"pr": "7", "head_sha": self.head, "base_sha": self.base,
                                  "merge_sha": inputs["merge_sha"], "tag": "content-v1.2"})


class ReleaseFlow(Rehearsal):
    def test_a_pull_request_becomes_a_released_and_deployable_edition(self):
        self.open_pr()
        inputs = self.controller()

        # Merged but unreleased: production must not move.
        self.refused(self.gate(), "differs from the latest published release content-v1.1")
        self.refused(self.gate("--ref", "content-v1.2"), "not a published release")

        verified = self.json_of(self.verify(inputs))
        self.assertEqual((verified["head"], verified["merge_sha"], verified["comparison"]),
                         (self.head, inputs["merge_sha"], "content-v1.1"))
        source = self.source(inputs)
        checked = self.release_content(source, "check", "--base", "content-v1.1")
        self.assertEqual(checked.returncode, 0, checked.stderr)

        plan = json.loads(self.plan(inputs).stdout)
        self.assertEqual((plan["action"], plan["tag"], plan["asset"]), ("create", "content-v1.2", PDF))
        self.assertEqual(plan["source_sha"], inputs["merge_sha"])
        self.assertTrue(self.latest("content-v1.2", plan["action"]))

        created = self.json_of(self.tag(inputs))
        self.assertEqual(created["created"], True)
        self.assertEqual(self.git("cat-file", "-t", "refs/tags/content-v1.2"), "tag")
        self.assertEqual(self.git("rev-parse", "refs/tags/content-v1.2^{commit}"), inputs["merge_sha"])
        self.prepare_assets(inputs)
        self.assertEqual(self.create_draft().returncode, 0)
        self.assertEqual(self.upload().returncode, 0)
        self.refused(self.gate("--ref", "content-v1.2"), "not a published release")

        latest = self.latest(inputs["tag"], plan["action"])
        self.assertEqual(self.publish(str(latest).lower()).returncode, 0)
        self.assertEqual(self.fake.latest_tag, "content-v1.2")
        writes = list(self.fake.writes)
        again = json.loads(self.plan(inputs).stdout)
        self.assertEqual(again["action"], "skip")
        self.assertFalse(self.latest(inputs["tag"], again["action"]))
        self.assertEqual(self.fake.writes, writes)
        self.assertNotIn("CLOBBER", " ".join(self.fake.writes))

        # The release deploys its own tag; afterwards main may deploy while it equals the release.
        deployed = self.json_of(self.gate("--ref", "content-v1.2", "--require-latest"))
        self.assertEqual(deployed, {"mode": "tag", "tag": "content-v1.2", "sha": inputs["merge_sha"]})
        self.assertEqual(self.json_of(self.gate()), {"mode": "main", "tag": "content-v1.2",
                                                     "sha": inputs["merge_sha"]})

        # Unreleased book content on main is refused; tooling-only changes are fine.
        self.advance("main", {"scripts/notes.txt": "tooling change\n"})
        self.assertEqual(self.json_of(self.gate())["mode"], "main")
        self.advance("main", {"content/chapters/one.html": "<p>Unreleased edit.</p>\n"})
        self.refused(self.gate(), "differs from the latest published release content-v1.2")

        # Rollback takes a released tag or its commit, never a branch or an unreleased commit.
        self.assertEqual(self.json_of(self.gate("--ref", "content-v1.1"))["tag"], "content-v1.1")
        self.assertEqual(self.json_of(self.gate("--ref", self.base))["tag"], "content-v1.1")
        self.refused(self.gate("--ref", "content-v1.1", "--require-latest"), "not the highest published")
        for ref, reason in (("main", "not a release tag or commit"), (self.head, "not the commit of a published release"),
                            ("content-v9.9", "not a published release")):
            with self.subTest(ref=ref):
                self.refused(self.gate("--ref", ref), reason)

    def test_forged_provenance_fails_with_no_writes(self):
        self.open_pr()
        inputs = self.controller()
        writes = list(self.fake.writes)
        forged_tree = self.git("rev-parse", f"{self.base}^{{tree}}")
        forged = self.git("-c", "user.name=Forger", "-c", "user.email=forger@example.invalid",
                          "commit-tree", forged_tree, "-p", self.base, "-m", "Not the approved head")
        other = self.advance("book-update", {"content/chapters/one.html": "<p>Never approved.</p>\n"})
        for override, reason in (
            ({"merge_sha": forged}, "does not match the requested source"),
            ({"head_sha": other}, "approved head"),
            ({"base_sha": forged}, "merge base"),
            ({"tag": "content-v1.3"}, "does not match the approved edition"),
            ({"pr": "8"}, "404"),
        ):
            with self.subTest(**override):
                self.refused(self.verify(inputs, **override), reason)
        planned = self.release_content(
            self.source(inputs), "release-plan", "--repo", REPOSITORY, "--base", "content-v1.1",
            "--expected-source", forged)
        self.assertEqual(planned.returncode, 1)
        self.assertEqual(self.fake.writes, writes)

    def test_an_existing_tag_is_never_moved(self):
        self.open_pr()
        inputs = self.controller()
        self.git("tag", "content-v1.2", self.base)
        self.refused(self.tag(inputs), "tags are never moved")
        self.assertEqual(self.git("rev-parse", "refs/tags/content-v1.2"), self.base)
        planned = self.plan(inputs)
        self.assertEqual(planned.returncode, 1)
        self.assertIn("different source", planned.stderr)
        self.assertEqual(self.fake.writes, [f"squash-merge #7 at {self.head}", "dispatch release.yml"])

    def test_tag_only_and_every_draft_fail_without_writes(self):
        self.open_pr()
        inputs = self.controller()
        self.json_of(self.tag(inputs))
        tag_object = self.git("rev-parse", "refs/tags/content-v1.2")
        writes = list(self.fake.writes)
        self.refused(self.plan(inputs), "exists without a release")
        self.refused(self.tag(inputs), "refusing to reuse")
        for assets in ([], [PDF]):
            with self.subTest(assets=assets):
                self.fake.publish("content-v1.2", assets, draft=True)
                self.refused(self.plan(inputs), "draft")
                self.fake.releases.pop()
        self.assertEqual(self.git("rev-parse", "refs/tags/content-v1.2"), tag_object)
        self.assertEqual(self.fake.writes, writes)

    def test_a_published_release_without_its_pdf_fails_with_no_writes(self):
        self.open_pr()
        inputs = self.controller()
        self.json_of(self.tag(inputs))
        self.fake.publish("content-v1.2", ["unrelated-upload.txt"])
        writes = list(self.fake.writes)
        planned = self.plan(inputs)
        self.assertEqual(planned.returncode, 1)
        self.assertIn("published without its PDF", planned.stderr)
        self.assertEqual(self.fake.writes, writes)

    def test_latest_goes_only_to_the_highest_stable_version(self):
        self.open_pr()
        inputs = self.controller()
        self.git("tag", "content-v9.0", self.base)  # an unrelated bare tag never competes
        self.fake.publish("content-v2.0", draft=True)
        self.assertTrue(self.latest("content-v1.2", "create"))  # a draft never counts
        self.fake.releases[-1]["prerelease"], self.fake.releases[-1]["draft"] = True, False
        self.assertTrue(self.latest("content-v1.2", "create"))  # nor does a prerelease
        self.fake.releases[-1]["prerelease"] = False
        self.assertFalse(self.latest("content-v1.2", "create"))
        writes = list(self.fake.writes)
        self.refused(self.tag(inputs), "older edition after a newer release")
        self.assertEqual(self.fake.writes, writes)

    def test_newer_stable_edition_appearing_during_upload_stays_latest(self):
        self.open_pr()
        inputs = self.controller()
        plan = self.json_of(self.plan(inputs))
        self.json_of(self.tag(inputs))
        self.prepare_assets(inputs)
        self.assertEqual(self.create_draft().returncode, 0)
        self.assertEqual(self.upload().returncode, 0)
        self.fake.publish("content-v1.3")
        latest = self.latest(inputs["tag"], plan["action"])
        self.assertFalse(latest)
        self.assertEqual(self.publish(str(latest).lower()).returncode, 0)
        self.assertEqual(self.fake.latest_tag, "content-v1.3")
        self.refused(self.gate("--ref", inputs["tag"], "--require-latest"), "not the highest published")
        self.assertEqual(self.json_of(self.gate("--ref", inputs["tag"]))["tag"], inputs["tag"])


if __name__ == "__main__":
    unittest.main()
