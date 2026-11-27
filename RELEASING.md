# Releasing *GitHub Agentic Workflows: An Interactive Book*

A release is a Git tag `content-vX.Y` on the merge commit of an **owner-approved, content-only pull request**, with a GitHub Release carrying the book's PDF. Nothing else publishes: not a push, a tag, a label or a manual merge.

```text
/update-book ─► /release-content ─► content PR ─► Book release preflight (green)
        ─► owner approval of the exact head ─► Release approved book: merge
        ─► tag, draft release + PDF, publish ─► GitHub Pages: aw.isainative.dev
```

The sections below explain each step. [Scenarios](#scenarios-what-to-do-when) walks through the situations you will actually meet, with commands. The tooling behind this page is documented in [`scripts/README.md`](scripts/README.md): [version and evidence contracts](scripts/README.md#version-and-evidence-contracts), [prepare and validate an edition](scripts/README.md#prepare-and-validate-an-edition), [CI and publication boundary](scripts/README.md#ci-and-publication-boundary) and [resume an interrupted update](scripts/README.md#resume-an-interrupted-update).

## Prepare the edition

Run [`/update-book`](.github/prompts/update-book.prompt.md) to follow a gh-aw release, or make the chapter edits yourself. Then run [`/release-content`](.github/prompts/release-content.prompt.md): it inspects the real prose changes, adds the CHANGELOG entry, bumps the edition and regenerates the site and PDF. Review the result and open a content PR against `main`.

Only reader-visible chapter prose and meaningful TOC changes justify a new edition. Research, framework metadata, examples, build scripts and styling alone do not.

| Increment | When to use it |
| --- | --- |
| Major (`2.0`) | Structural rewrite or reordering of the book. |
| Minor (`1.3`) | New chapters, sections or material, for example a framework refresh. |
| Patch (`1.2.1`) | Corrections and clarifications. |

The edition lives in [`content/VERSION`](content/VERSION) as `major.minor` or `major.minor.patch`, and the tag is `content-v<edition>`. It is separate from [`content/FRAMEWORK_VERSION`](content/FRAMEWORK_VERSION), the exact gh-aw release the examples are verified against.

**Book release preflight** (the **Check book update** workflow) is the gate. It tests the release tooling, checks the edition, CHANGELOG and review evidence, compiles every example with the exact pinned gh-aw compiler, regenerates the site and builds the PDF. For a content PR:

- Change only `content/` (`VERSION`, `FRAMEWORK_VERSION`, `CHANGELOG.md`, `release-review.json`, `toc.yml`, `outline.md`, `playbook-brief.md`, `chapters/`, `research/`), `examples/` and the generated site files (`site/*.html`, `site/chapters/*.html`, `llms*.txt`, `sitemap.xml`, `robots.txt`, `site.webmanifest`). Anything else is tooling and belongs in a separate PR with no version bump.
- Set `content/VERSION` above the latest published `content-v*` release and above the version already on `main`. Changing chapters without a bump fails with `bump content/VERSION monotonically above X.Y`; bumping without a chapter or TOC change fails with `No reader-visible content changed since …; keep edition X.Y`.
- Add exactly one nonempty `## [X.Y] - YYYY-MM-DD` section to `content/CHANGELOG.md`.
- Record a review. Save the editorial report with one standalone `Verdict: ACCEPT` line, then bind it to the current source:

  ```sh
  python scripts/release_content.py record-review --report content/research/updates/<target>/review.md --verdict ACCEPT
  ```

  This writes `content/release-review.json`. It covers the chapters, TOC, framework version and examples, so **any later edit to those makes it stale** (`Stale review evidence: fingerprint does not match the current source/report`). Record it after the last content edit; changing `VERSION` or the CHANGELOG afterwards is fine. The record attests that an editorial review took place. It does not replace the review, and the controller does not judge whether the evidence supports the claims. You do.
- Include a real chapter or TOC change. The controller refuses a PR with no reader-visible change (`No reader-visible content change since the published edition`).

## Authorize and publish

For someone else's non-draft PR, **webmaxru** submits an **Approve** review on its current head. For an owner-authored PR, post exactly `/release-book <full lowercase 40-character head SHA>` in a new PR conversation comment. An older SHA, another user's comment, or approval superseded by requested changes or dismissal does not count. Deleting the command withdraws it. A new commit needs new approval.

The controller, **Release approved book**, runs on `main` with its own trusted validators. It reacts to the review or comment, to the completion of **Check book update**, to a scan of open PRs every six hours, and to **Run workflow → pull-request**. None of those triggers grants approval. It requires a non-draft, same-repository PR against `main` whose files are all on the content allowlist, **Book release preflight** passing (from GitHub Actions) and every other latest check green. It repeats the preflight on the PR's test merge, then merges with a **merge commit** that is conditional on the approved head, and aborts if the head, the base or the published-edition baseline moved in the meantime.

Publication runs in the same controller run, because a merge made with `GITHUB_TOKEN` does not trigger other workflows. It validates the merge commit again, creates the tag `content-vX.Y` there, creates a **draft** release with `gh-aw-book-vX.Y.pdf`, publishes it, and marks it Latest only if no newer stable release exists. Then it deploys the website from the same validated build to [aw.isainative.dev](https://aw.isainative.dev/), without the gated PDF.

The repository has no branch protection or ruleset, so nothing enforces this gate: **manual merges bypass it**.

## Recovery and corrections

Pushing a tag no longer publishes. If the merge succeeded but publication failed, run the controller for that PR number; it recovers the exact merged revision and never overwrites anything:

| State found | What recovery does |
| --- | --- |
| Release complete | Nothing to publish (no-op). The website is redeployed if `main` is still the released commit. |
| Tag but no release, or draft without the PDF | Creates or completes the draft, uploads the PDF, publishes. |
| Draft with the PDF | Publishes it. |
| Incomplete or ambiguous PDF upload | Stops without changes and tells you to inspect the release. |

A correction needs a **new version**, not a rebuild. Never move a tag or replace a published PDF. See [scenarios 11–13](#11-the-release-failed-after-the-merge).

## Scenarios: what to do when

Commands use the [GitHub CLI](https://cli.github.com/) (`gh`) from a clone of this repository and work in bash and PowerShell. `N` is the pull request number and `content-vX.Y` a tag. Replace `content-v1.2` in examples with the latest published tag shown by `gh release list`.

### What triggers what

| Event | What happens | Release? |
| --- | --- | --- |
| PR opened or pushed | **Check book update** runs the tests, edition checks, example compilation, site and PDF build. Its **Book release preflight** job is the gate. | No |
| Owner **Approve** review, or an owner `/release-book <SHA>` comment | **Release approved book** re-checks everything and merges the approved head. | Yes, in the same run |
| Check run finishes, or the six-hourly scan | The controller looks for an approved PR it missed. It never approves anything itself. | Only if a valid approval exists |
| **Release approved book → Run workflow** with `pull-request` | Same re-check for one PR, or recovery if that PR is already merged. | Only if a valid approval exists |
| Push a tag, add a label, press **Merge** | Nothing in the release flow. | **No** |
| Push to `main` touching `site/`, `scripts/`, `assets/` or the deploy workflows | **Deploy book to GitHub Pages** redeploys, but only if `content/` and `examples/` equal the last published edition. | No |
| Every two weeks | **gh-aw book update scout** files an advisory issue "[gh-aw update scan] …" when gh-aw has moved. It never edits files. | No |

The website and the PDF come from the same release. Only the controller's merge produces a tag, the PDF and a new edition on the site.

### 1. Routine update (your own PR)

1. Run `/update-book` (for a gh-aw release, see the scout issue) or make your chapter edits, then `/release-content`. Do the editorial review and write its report.
2. Check locally what CI will check (see also [Before you open any PR](#before-you-open-any-pr)):

   ```sh
   python scripts/release_content.py changes --base content-v1.2
   python scripts/release_content.py record-review --report content/research/updates/<target>/review.md --verdict ACCEPT
   python scripts/release_content.py check --base content-v1.2    # prints "status": "PASS" and the new tag
   ```

3. Push and open the PR against `main`:

   ```sh
   git push -u origin content/my-update
   gh pr create --base main --title "Update for gh-aw vX.Y.Z" --body "See content/CHANGELOG.md."
   ```

4. Wait for **Book release preflight** (`gh pr checks N --watch`). Read the CHANGELOG entry and the editorial report yourself.
5. Authorize **the exact head**. You wrote the PR, so GitHub will not let you approve it. Comment instead:

   ```sh
   gh pr comment N --body "/release-book $(gh pr view N --json headRefOid --jq .headRefOid)"
   ```

6. Watch it go through, normally within a few minutes:

   ```sh
   gh run list --workflow release-approved-book.yml -L 3
   gh run watch <run-id>
   gh release view content-vX.Y
   ```

**Result:** the PR is merged, `content-vX.Y` is a tag on the merge commit, the release has `gh-aw-book-vX.Y.pdf`, it is Latest if it is the highest stable edition, and the website shows the new edition.

### 2. Someone else's PR on a branch in this repository

A collaborator with write access opens a content PR. This is the normal case for contributions.

1. Read the diff. The PR must be non-draft, target `main`, change only content files and pass **Book release preflight**. A contributor usually does not know about the version bump, the CHANGELOG section and the review record, so preflight fails until they exist. Add them to the contributor's branch yourself, after reviewing the edit:

   ```sh
   gh pr checkout N
   # edit content/VERSION and content/CHANGELOG.md; write the editorial report
   python scripts/release_content.py record-review --report content/research/updates/<target>/review.md --verdict ACCEPT
   git add -A && git commit -m "Prepare content-vX.Y" && git push
   ```

2. When preflight is green, submit an **Approve** review on the current head and stop there:

   ```sh
   gh pr review N --approve
   ```

**Do not press Merge.** A manual merge publishes nothing (scenario 9). The pushes in step 1 change the head, so approve after them, not before. `record-review` must run after the contributor's last chapter edit.

### 3. A pull request from a fork

The controller only merges PRs whose head branch is in this repository, so a fork PR is refused. Re-create it on a branch here and keep the contributor's commits:

```sh
gh pr checkout N
git switch -c content/from-pr-N
git push -u origin content/from-pr-N
gh pr create --base main --head content/from-pr-N --title "<title>" --body "Supersedes #N"
```

You now own the new PR, so continue with scenario 1: add the version bump, CHANGELOG and review record, then comment `/release-book <SHA>`. Close the original PR with a thank-you.

### 4. A new push after approval, requested changes or a dismissed review

An approval counts only for the head it was given on. A push after approval, a **Request changes** review or a dismissed review voids it. Nothing merges until you approve again: a new **Approve** review, or a new `/release-book <SHA>` with the new head SHA. An old SHA in an old comment is ignored.

### 5. The branch is behind `main`

This is not a problem by itself: the controller checks the PR's test merge with `main`, and merges the exact approved head. If `main` moved so that the PR no longer merges cleanly, or if a different edition was published meanwhile, the controller stops with `PR head or base changed after preflight` or `Published edition baseline changed after preflight`; a later run starts again from the current state. To resolve conflicts, update the branch and approve the new head again:

```sh
gh pr update-branch N
```

### 6. Approved, but the PR is still open

Look at the latest **Release approved book** run for the reason. The scheduled scan prints one line per open PR, `PR #N: <reason>`, in the `select` job log. Typical causes: failing preflight, a head that moved after approval, a conflict with `main`, or a run that never started. Fix that, or run the controller for this PR:

```sh
gh workflow run release-approved-book.yml -f pull-request=N
```

If the run died within a second with no steps, see [Runs that fail without starting](#10-runs-that-fail-without-starting).

### 7. Tooling, docs and workflow changes

A PR that touches only files outside the content allowlist (`scripts/`, `site/` generator code, `.github/`, `assets/`, `README.md`, `RELEASING.md`, tests) is **tooling-only**. It needs no version bump and never releases. Preflight passes, but the controller refuses to merge it (`PR does not change a chapter or TOC`). Merge it yourself when the checks are green. A push that touches a deploy path redeploys the website, but only while `main` has no unreleased content (scenario 9 explains the gate).

### 8. Mixed content and tooling

A PR that changes both content and tooling fails with `PR contains paths outside the content-only allowlist`. Split it into two PRs: tooling first (merged by you), then the content PR.

### 9. A manual merge by mistake

Pressing **Merge** on a content PR, or merging from the command line, bypasses the controller. The repository has no branch protection or ruleset, so GitHub allows it. The effects:

- **No tag, no release, no PDF.**
- The website does not change. It is deployed by the release, and the push-triggered **Deploy book to GitHub Pages** refuses to run while `content/` or `examples/` differ from the last published edition (its `published-source` job fails).
- The same gate also blocks later tooling-only website deploys until the content is released.
- The edition the PR carried is now on `main` unreleased. Another PR must advance beyond it, so the version number is stranded.

Fix it in one of two ways.

**If you had approved the exact head and merged with a merge commit** ("Create a merge commit"), the controller can still recover that merged PR. This is the case when you approve and press **Merge** before the controller runs:

```sh
gh workflow run release-approved-book.yml -f pull-request=N
```

It re-checks the approval, the checks and the merge parents, and publishes if `main` is still the merge commit. If it says `Recovery requires a merge commit containing the approved head`, the PR was squashed, rebased or merged on a different head. Use a catch-up PR.

**Otherwise, open a catch-up PR.** For example, if `main` carries edition `1.3` but the latest tag is `content-v1.2`:

1. Branch from `main`. The catch-up must contain a **real chapter or TOC change** (a correction, a clarified paragraph, an added cross-reference). A PR that only bumps the version and CHANGELOG is rejected: `No reader-visible content changed since …; keep edition 1.3`.
2. Set `content/VERSION` to `1.3.1`. Reusing `1.3` fails with `bump content/VERSION monotonically above 1.3 (found 1.3)`.
3. Add a dated `## [1.3.1] - YYYY-MM-DD` section. Move the stranded `1.3` entries under it so the notes describe everything readers get.
4. Write a review report and run `record-review` after the last chapter edit.
5. Check it: `python scripts/release_content.py check --base content-v1.2` prints `"status": "PASS"` and `"tag": "content-v1.3.1"`.
6. Open the PR and authorize it as in scenario 1.

### 10. Runs that fail without starting

If **Release approved book** or **Check book update** runs end in about a second with no steps and the annotation *"The job was not started because recent account payments have failed or your spending limit needs to be increased"*, GitHub Actions is blocked by billing, not by this repository. Fix **Settings → Billing and plans**, then run `gh workflow run release-approved-book.yml -f pull-request=N` for each affected PR.

### 11. The release failed after the merge

The PR is merged but the release is missing or incomplete. Run the controller for the merged PR:

```sh
gh workflow run release-approved-book.yml -f pull-request=N
```

Recovery follows [the table above](#recovery-and-corrections). If the tag does not exist yet, `main` must still be the merge commit; otherwise it stops with `Cannot create a release for an outdated main commit`, and you release the content again as a new patch edition through scenario 9. If the tag already exists, recovery completes the draft or PDF for the exact merged revision even after later commits, and leaves the current website alone. If it stops with `has an incomplete or ambiguous upload`, open the release on GitHub, delete the incomplete asset or restore the correct PDF from that tag, and run the command again. Never move a tag or overwrite a published PDF.

### 12. Only the website deploy failed

The release is published and complete but [aw.isainative.dev](https://aw.isainative.dev/) still shows the old edition. Redeploy `main`:

```sh
gh workflow run deploy-pages.yml
```

It succeeds when `main`'s `content/` and `examples/` equal the latest published edition, which is the case after a complete release. The same command works if you only need to redeploy after a tooling change.

### 13. A published release is wrong, or the site must go back

Do not edit the release or move its tag. Fix `main` through scenario 1 and release a new patch edition, for example `1.2.1`. To pull a mistaken edition back, revert its content in a new PR with a higher version; the controller refuses to create an older edition after a newer one. There is no workflow that deploys the website from an old tag: the site always follows `main`.

### 14. Choosing the version

Follow the table in [Prepare the edition](#prepare-the-edition). When unsure, ask what a reader of the last edition would notice: a restructured book is major, new chapters or material are minor, corrections are patch. The version must exceed every published `content-v*` release and the version on `main`; the check tells you if it does not.

### 15. Control center alerts

If you use the book control center, each alert has a fix on this page:

| Alert | Cause and fix |
| --- | --- |
| `PR #N is ready for your approval` | Preflight is green. Approve the head (scenario 2) or comment `/release-book <SHA>` (scenario 1). |
| `PR #N release preflight is failing` | Open the failed **Check book update** run. Fix the PR, or re-run failed jobs if the failure was transient. |
| `PR #N was approved but is still open` | Scenario 6. |
| `PR #N changed after your approval` | Scenario 4. Approve the new head. |
| `<workflow> failed` | Open the run. Re-run failed jobs, or use scenario 10 (billing), 11 (release) or 12 (deploy). |
| `<run> has been queued for N days` | An orphaned run, such as GitHub's own `pages build and deployment`. `gh run cancel <run-id>`; the site keeps serving. |
| `Edition X on main has no release yet`, `N content file(s) changed since content-vX.Y without a release` | Scenario 9: content reached `main` without the controller. |
| `Latest GitHub Pages build errored` or `Site is not responding` | Scenario 12. |

### Before you open any PR

```sh
python -m unittest discover -s scripts/tests
python scripts/release_content.py check --base content-v1.2    # content PR: "status": "PASS"; unchanged book: "changed": false
python site/generate.py                                          # regenerate the site
python scripts/build_pdf.py                                      # needs Playwright Chromium; CI does this too
python scripts/release_content.py check-generated                # after the PDF exists
```

Examples are compiled by CI with the pinned compiler. To do it locally, use `python scripts/verify_examples.py --compiler <absolute-path-to-gh-aw>` as described in [`scripts/README.md`](scripts/README.md#prepare-and-validate-an-edition).
