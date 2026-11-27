# Releasing *GitHub Agentic Workflows: An Interactive Book*

A release is a Git tag `content-vX.Y` on the squash-merge commit of an **owner-approved, content-only pull request**, with a GitHub Release carrying the book's PDF. Nothing else publishes: not a push, a tag, a label or a manual merge.

```text
/update-book ─► /release-content ─► content PR ─► Book CI: "Book release preflight" (green)
        ─► owner approval of the exact head ─► Release approved book: squash merge, dispatch
        ─► Release book: tag, draft release + PDF, publish
        ─► Deploy book to GitHub Pages: aw.isainative.dev
```

This repository is one of four books that run the same release system, so the rules are written once as a [contract](#book-release-flow-contract-v1) and everything specific to this book is listed under [Per-book settings](#per-book-settings). [Scenarios](#scenarios-what-to-do-when) walks through the situations you will actually meet, with commands. The tooling behind this page is documented in [`scripts/README.md`](scripts/README.md): [version and evidence contracts](scripts/README.md#version-and-evidence-contracts), [prepare and validate an edition](scripts/README.md#prepare-and-validate-an-edition), [CI and publication boundary](scripts/README.md#ci-and-publication-boundary) and [resume an interrupted update](scripts/README.md#resume-an-interrupted-update).

## Book release flow contract v1

Every book repository follows the same release flow. A repository conforms when `tests/test_flow_contract.py` passes and each rule below is covered by a test in that repository's own suite.

1. **Workflow surface (same names everywhere).**
   `ci.yml` named "Book CI" with the aggregate job "Book release preflight"; `book-approval-signal.yml` named "Book approval signal"; `approved-book.yml` named "Release approved book"; `release.yml` named "Release book"; one deploy workflow, `deploy-swa.yml` or `deploy-pages.yml`.
2. **Controller.**
   Triggers: `workflow_run` of "Book approval signal" and "Book CI", `issue_comment`, schedule `17,47 * * * *`, and `workflow_dispatch` with the input `pr`. Jobs run only from `main`. Workflow `permissions: {}` with least privilege per job. Concurrency group `approved-book`, no cancel. Validators always run from `main`, never from the pull request.
3. **Eligibility.**
   The pull request is open, not a draft, from the same repository, targets `main`, is mergeable, and its head contains the current `main`. Its files are content-only under the book's allowlist. "Book release preflight" is green on the exact head, and the version, CHANGELOG and evidence checks pass.
4. **Authorization.**
   Someone else's pull request: an owner Approve review on the current head. The owner's own pull request: an owner comment `/release-book <40-character head SHA>`. A later push, a CHANGES_REQUESTED review, a dismissed review or an edited or deleted comment revokes it. A non-owner never authorizes.
5. **Merge.**
   A squash merge conditioned on the approved head SHA. The controller then dispatches `release.yml`, because merges made with `GITHUB_TOKEN` trigger no workflows.
6. **Release.**
   `release.yml` is dispatch-only, with the inputs `pr`, `head_sha`, `base_sha`, `merge_sha` and `tag`, and the concurrency group `book-publish`. Steps: plan, build from the merge commit, annotated tag, draft release, upload assets, publish, deploy the released tag, smoke test. Never clobber assets and never move a tag. A complete release is a no-op. A partial release or a provenance mismatch fails with no writes. Latest goes only to the highest stable version, and prereleases are never Latest. A fix is a new version.
7. **Deploy.**
   Production serves only released editions. A push to `main` deploys only when the content equals the latest published release (the `published-source` job). The release deploys its own tag. A manual dispatch takes a released ref or sha, which is the rollback path.
8. **No other publisher.**
   A tag push, a label or a branch name never publishes. A manual merge to `main` bypasses the controller; the fix is a catch-up pull request with a higher version.
9. **Pins.**
   Runner `ubuntu-24.04`. `actions/checkout@v7`, `actions/setup-python@v7`, `actions/upload-artifact@v7`, `actions/download-artifact@v8` (a full commit SHA with a trailing `# v7.x.y` version comment is acceptable).

### Per-book settings

Everything that may differ between the four books. The workflow names, triggers, inputs and rules above do not.

| Setting | This book |
| --- | --- |
| Format and build | Static HTML book generated from `content/` by `site/generate.py`. A single-file PDF is built by `scripts/build_pdf.py` (Playwright Chromium). Every example workflow is compiled with the exact gh-aw compiler pinned in `content/FRAMEWORK_VERSION`. |
| Version file, scheme, tag | `content/VERSION`: `major.minor` or `major.minor.patch`. Tag `content-vX.Y` (`content-vX.Y.Z` for a patch). Independent of `content/FRAMEWORK_VERSION`, the gh-aw release the examples are verified against. |
| Content allowlist | Defined once, in `scripts/approved_book.py` (`CONTENT_PATHSPECS`, `OWNER_FILES`, `OWNER_PREFIXES`, `SITE_FILES`): `content/` (`VERSION`, `FRAMEWORK_VERSION`, `CHANGELOG.md`, `release-review.json`, `toc.yml`, `outline.md`, `playbook-brief.md`, `chapters/`, `research/`), `examples/`, and the generated site files (`site/*.html`, `site/chapters/*.html`, `llms*.txt`, `sitemap.xml`, `robots.txt`, `site.webmanifest`). Anything else is tooling and goes in a separate PR with no version bump. |
| Evidence rules | Exactly one nonempty `## [X.Y] - YYYY-MM-DD` section in `content/CHANGELOG.md`; `content/VERSION` strictly above the latest published `content-v*` release and above `main`; a real chapter or TOC change; `content/release-review.json`, written by `python scripts/release_content.py record-review` from an editorial report with a standalone `Verdict: ACCEPT` line and bound to a fingerprint of the chapters, TOC, framework version and examples. All checked by `release_content.py check` inside **Book release preflight**. |
| Release artifacts | GitHub Release `content-vX.Y` with `gh-aw-book-vX.Y.pdf`. Latest only for the highest stable edition. |
| Deploy target and domain | GitHub Pages from the `gh-pages` branch (legacy branch source), workflow `deploy-pages.yml`, custom domain [aw.isainative.dev](https://aw.isainative.dev/) (`site/CNAME`). The smoke test reads `<meta name="book-content-version">` from the live page. The PDF is not deployed. |
| `published-source` gate | `scripts/deploy_gate.py` compares `content/` and `examples/` at `HEAD` with the latest published release tag. The path list lives in `scripts/approved_book.py`, not in the workflow YAML. |
| Rollback | `gh workflow run deploy-pages.yml -f ref=content-vX.Y` with a published tag (or the commit of one). Only editions that carry `content/VERSION` can be redeployed, so `content-v1.2` and later; the legacy tags `content-v1.0` and `content-v1.1` predate release metadata. |
| Catch-up PR rules | A manual merge strands the edition on `main`. The catch-up PR needs a real chapter or TOC change and a **patch** bump above the stranded edition (`1.3` becomes `1.3.1`), with the stranded CHANGELOG entries moved under it. See [scenario 9](#9-a-manual-merge-by-mistake). |
| Upstream scouting | The scheduled gh-aw workflow `scan-gh-aw-updates` (every two weeks) files an advisory issue "[gh-aw update scan] …" when gh-aw has moved. It never edits files and is not part of the release flow. |
| Tests | `python -m unittest discover -s scripts/tests`, which includes `scripts/tests/test_flow_contract.py` and an end-to-end rehearsal of the whole flow (`test_release_flow_e2e.py`). |

Where this book is stricter than the contract requires:

- **Squash only.** The controller refuses to publish a merge that is not a squash of exactly the approved head (one parent, the head's tree).
- **The command is exact.** `/release-book <SHA>` must be a whole comment from the owner, never edited. A later owner review of any kind also revokes an approval, and any reviewer's CHANGES_REQUESTED or a dismissal is a barrier.
- **The preflight is repeated by trusted code.** The controller re-runs it on the approved head, with validators from `main`, before it merges, and `release.yml` builds the merge commit again before it publishes.
- **A release deploys through `deploy-pages.yml`**, so the same gate, build, publish and smoke test run for a release, a rollback and a push to `main`.
- **Only the highest stable edition is Latest and deployed.** An older edition is never created after a newer one; finishing an interrupted older draft publishes it without Latest and without a deploy.

## Prepare the edition

Run [`/update-book`](.github/prompts/update-book.prompt.md) to follow a gh-aw release, or make the chapter edits yourself. Then run [`/release-content`](.github/prompts/release-content.prompt.md): it inspects the real prose changes, adds the CHANGELOG entry, bumps the edition and regenerates the site and PDF. Review the result and open a content PR against `main`.

Only reader-visible chapter prose and meaningful TOC changes justify a new edition. Research, framework metadata, examples, build scripts and styling alone do not.

| Increment | When to use it |
| --- | --- |
| Major (`2.0`) | Structural rewrite or reordering of the book. |
| Minor (`1.3`) | New chapters, sections or material, for example a framework refresh. |
| Patch (`1.2.1`) | Corrections and clarifications. |

The edition lives in [`content/VERSION`](content/VERSION) and the tag is `content-v<edition>`.

**Book release preflight** (the aggregate job of **Book CI**) is the gate. It tests the release tooling, checks the edition, CHANGELOG and review evidence, compiles every example with the exact pinned gh-aw compiler, regenerates the site and builds the PDF. For a content PR:

- Change only the [content allowlist](#per-book-settings). Tooling belongs in a separate PR with no version bump.
- Set `content/VERSION` above the latest published `content-v*` release and above the version already on `main`. Changing chapters without a bump fails with `bump content/VERSION monotonically above X.Y`; bumping without a chapter or TOC change fails with `No reader-visible content changed since …; keep edition X.Y`.
- Add exactly one nonempty `## [X.Y] - YYYY-MM-DD` section to `content/CHANGELOG.md`.
- Record a review. Save the editorial report with one standalone `Verdict: ACCEPT` line, then bind it to the current source:

  ```sh
  python scripts/release_content.py record-review --report content/research/updates/<target>/review.md --verdict ACCEPT
  ```

  This writes `content/release-review.json`. It covers the chapters, TOC, framework version and examples, so **any later edit to those makes it stale** (`Stale review evidence: fingerprint does not match the current source/report`). Record it after the last content edit; changing `VERSION` or the CHANGELOG afterwards is fine. The record attests that an editorial review took place. It does not replace the review, and the controller does not judge whether the evidence supports the claims. You do.
- Include a real chapter or TOC change. The controller refuses a PR with no reader-visible change (`No reader-visible content change since the published edition`).
- Keep the branch up to date with `main`. A head that does not contain the current `main` is never merged ([scenario 5](#5-the-branch-is-behind-main)).

## Authorize and publish

For someone else's non-draft PR, **webmaxru** submits an **Approve** review on its current head. For an owner-authored PR, post exactly `/release-book <full lowercase 40-character head SHA>` in a new PR conversation comment. An older SHA, another user's comment, an edited comment, or approval superseded by requested changes or dismissal does not count. Deleting the command withdraws it. A new commit needs new approval.

The controller, **Release approved book** (`approved-book.yml`), runs on `main` with its own trusted validators. It reacts to the review (relayed by **Book approval signal**) or the comment, to the completion of **Book CI**, to a scan of open PRs every 30 minutes (`17,47 * * * *`), and to **Run workflow → pr**. None of those triggers grants approval. It requires a non-draft, same-repository PR against `main` whose files are all on the content allowlist, whose head contains the current `main`, with **Book release preflight** passing on the exact head (from GitHub Actions) and every other latest check green. It repeats the preflight on the approved head, then **squash-merges** conditionally on that head's SHA, and aborts if the head, the base or the published-edition baseline moved in the meantime.

A merge made with `GITHUB_TOKEN` does not trigger other workflows, so the controller's last job dispatches **Release book** (`release.yml`) with `pr`, `head_sha`, `base_sha`, `merge_sha` and `tag`. That workflow runs on `main` and:

1. **plans** read-only: it proves the merge is the approved PR's squash on `main`, that the tag matches `content/VERSION`, and what is already published decides `create`, `upload`, `publish` or `skip`;
2. **builds** exactly the merge commit (site, examples, PDF);
3. creates the **annotated tag** `content-vX.Y` there, a **draft** release with `gh-aw-book-vX.Y.pdf`, and **publishes** it, marking it Latest only if no newer stable release exists;
4. **deploys the released tag** through **Deploy book to GitHub Pages** to [aw.isainative.dev](https://aw.isainative.dev/), without the gated PDF, and smoke-tests the live page.

The repository has no branch protection or ruleset, so nothing enforces this gate: **manual merges bypass it**.

## Recovery and corrections

Pushing a tag never publishes. If the merge succeeded but publication failed, run the controller for that PR number; it recovers the exact merged revision, re-derives the five release inputs and never overwrites anything:

```sh
gh workflow run approved-book.yml -f pr=N
```

| State found | What **Release book** does |
| --- | --- |
| Release complete | Nothing to publish (no-op). The released tag is redeployed if it is the newest edition. |
| Tag but no release | Creates the draft with the PDF, publishes. |
| Draft without the PDF | Uploads the PDF, publishes. |
| Draft with the PDF | Publishes it. |
| Published but without the PDF, a tag at another commit, or a merge that is not the approved head | Fails and writes nothing. A fix is a new version. |

A correction needs a **new version**, not a rebuild. Never move a tag or replace a published PDF. See [scenarios 11–13](#11-the-release-failed-after-the-merge).

## Scenarios: what to do when

Commands use the [GitHub CLI](https://cli.github.com/) (`gh`) from a clone of this repository and work in bash and PowerShell. `N` is the pull request number and `content-vX.Y` a tag. Replace `content-v1.2` in examples with the latest published tag shown by `gh release list`.

### What triggers what

| Event | What happens | Release? |
| --- | --- | --- |
| PR opened or pushed | **Book CI** runs the tests, edition checks, example compilation, site and PDF build. Its **Book release preflight** job is the gate. | No |
| Owner **Approve** review, or an owner `/release-book <SHA>` comment | **Release approved book** re-checks everything, squash-merges the approved head and dispatches **Release book**. | Yes, started by the controller |
| **Book CI** finishes, or the scan every 30 minutes | The controller looks for an approved PR it missed. It never approves anything itself. | Only if a valid approval exists |
| **Release approved book → Run workflow** with `pr` | Same re-check for one PR, or recovery if that PR is already merged. | Only if a valid approval exists |
| **Release book → Run workflow** | Same plan and provenance checks for five explicit inputs. Retry or recovery only. | Only for the exact approved merge |
| Push a tag, add a label, press **Merge** | Nothing in the release flow. | **No** |
| Push to `main` touching `site/`, `scripts/`, `assets/` or the deploy workflows | **Deploy book to GitHub Pages** redeploys, but only if `content/` and `examples/` equal the latest published edition. | No |
| **Deploy book to GitHub Pages → Run workflow** with `ref` | Deploys that published tag. The rollback path. | No |
| Every two weeks | **gh-aw book update scout** (`scan-gh-aw-updates`) files an advisory issue "[gh-aw update scan] …" when gh-aw has moved. It never edits files. | No |

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
   gh run list --workflow approved-book.yml -L 3
   gh run list --workflow release.yml -L 3
   gh run watch <run-id>
   gh release view content-vX.Y
   ```

**Result:** the PR is squash-merged, `content-vX.Y` is an annotated tag on the squash commit, the release has `gh-aw-book-vX.Y.pdf`, it is Latest if it is the highest stable edition, and the website shows the new edition.

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

An approval counts only for the head it was given on. A push after approval, a **Request changes** review, a dismissed review, or an edited or deleted `/release-book` comment voids it. Nothing merges until you approve again: a new **Approve** review, or a new `/release-book <SHA>` with the new head SHA. An old SHA in an old comment is ignored.

### 5. The branch is behind `main`

A head that does not contain the current `main` is not eligible and is never merged. The controller logs `The head does not contain the current main; update the branch and approve again.` (or `main moved since the pull request was last evaluated` when `main` moved a moment ago). Update the branch, wait for preflight on the new head, then authorize the new head:

```sh
gh pr update-branch N          # or: git merge origin/main && git push
gh pr checks N --watch
gh pr review N --approve       # your own PR: comment /release-book <new head SHA> instead
```

Updating the branch changes the head, so an earlier approval no longer counts. If `main` moved so that the PR conflicts, resolve the conflicts locally first. If a different edition was published meanwhile, the controller stops with `Published edition baseline changed after preflight` or `Proposed edition is not newer than the latest published edition`; raise `content/VERSION` and the CHANGELOG section above it.

### 6. Approved, but the PR is still open

Look at the latest **Release approved book** run for the reason. The scan prints one line per open PR, `PR #N: <reason>`, in the `select` job log. Typical causes: failing preflight, a head that moved after approval, a head behind `main`, a conflict with `main`, or a run that never started. Fix that, or run the controller for this PR:

```sh
gh workflow run approved-book.yml -f pr=N
```

If the run died within a second with no steps, see [Runs that fail without starting](#10-runs-that-fail-without-starting).

### 7. Tooling, docs and workflow changes

A PR that touches only files outside the content allowlist (`scripts/`, `site/` generator code, `.github/`, `assets/`, `README.md`, `RELEASING.md`, tests) is **tooling-only**. It needs no version bump and never releases. Preflight passes, but the controller refuses to merge it (`PR does not change a chapter or TOC`). Merge it yourself when the checks are green. A push that touches a deploy path redeploys the website, but only while `main` has no unreleased content (scenario 9 explains the gate).

### 8. Mixed content and tooling

A PR that changes both content and tooling fails with `PR contains paths outside the content-only allowlist`. Split it into two PRs: tooling first (merged by you), then the content PR.

### 9. A manual merge by mistake

Pressing **Merge** on a content PR, or merging from the command line, bypasses the controller. The repository has no branch protection or ruleset, so GitHub allows it. The effects:

- **No tag, no release, no PDF.**
- The website does not change. It is deployed by the release, and the push-triggered **Deploy book to GitHub Pages** refuses to run while `content/` or `examples/` differ from the latest published edition (its `published-source` job fails).
- The same gate also blocks later tooling-only website deploys until the content is released.
- The edition the PR carried is now on `main` unreleased. Another PR must advance beyond it, so the version number is stranded.

Fix it in one of two ways.

**If you had approved the exact head and merged with "Squash and merge"** (and `main` had not moved past the head), the controller can still recover that merged PR, because the squash has the approved head's tree:

```sh
gh workflow run approved-book.yml -f pr=N
```

It re-checks the approval, the checks and the squash provenance, and releases if `main` is still the merge commit. If it says `The merge is not a squash of exactly the approved head`, the PR was merged with a merge commit, rebased, or squashed onto a different base. Use a catch-up PR.

**Otherwise, open a catch-up PR.** For example, if `main` carries edition `1.3` but the latest tag is `content-v1.2`:

1. Branch from `main`. The catch-up must contain a **real chapter or TOC change** (a correction, a clarified paragraph, an added cross-reference). A PR that only bumps the version and CHANGELOG is rejected: `No reader-visible content changed since …; keep edition 1.3`.
2. Set `content/VERSION` to `1.3.1`. Reusing `1.3` fails with `bump content/VERSION monotonically above 1.3 (found 1.3)`.
3. Add a dated `## [1.3.1] - YYYY-MM-DD` section. Move the stranded `1.3` entries under it so the notes describe everything readers get.
4. Write a review report and run `record-review` after the last chapter edit.
5. Check it: `python scripts/release_content.py check --base content-v1.2` prints `"status": "PASS"` and `"tag": "content-v1.3.1"`.
6. Open the PR and authorize it as in scenario 1.

### 10. Runs that fail without starting

If **Release approved book**, **Release book** or **Book CI** runs end in about a second with no steps and the annotation *"The job was not started because recent account payments have failed or your spending limit needs to be increased"*, GitHub Actions is blocked by billing, not by this repository. Fix **Settings → Billing and plans**, then run `gh workflow run approved-book.yml -f pr=N` for each affected PR.

### 11. The release failed after the merge

The PR is merged but the release is missing or incomplete. Run the controller for the merged PR; it verifies the squash against the approved head and dispatches **Release book** again:

```sh
gh workflow run approved-book.yml -f pr=N
```

Alternatively open the failed **Release book** run and choose **Re-run failed jobs**: the inputs are unchanged and every check runs again. To dispatch **Release book** yourself with the five inputs, derive them from the merged PR (`base_sha` is the parent of the squash commit, `tag` is `content-v` plus `content/VERSION` at the merge):

```sh
gh pr view N --json headRefOid,mergeCommit --jq '.headRefOid, .mergeCommit.oid'    # head_sha, merge_sha
git fetch origin main && git rev-parse <merge_sha>^                                # base_sha
git show <merge_sha>:content/VERSION                                               # edition, so tag content-v<edition>
gh workflow run release.yml -f pr=N -f head_sha=<head_sha> -f base_sha=<base_sha> -f merge_sha=<merge_sha> -f tag=content-vX.Y
```

Recovery follows [the table above](#recovery-and-corrections). If the tag does not exist yet, `main` must still be the merge commit; otherwise it stops with `Cannot create a release for an outdated main commit`, and you release the content again as a new patch edition through scenario 9. If the tag already exists, recovery completes the draft or PDF for the exact merged revision even after later commits. If it stops with `published without its PDF asset`, the release is partial: do not edit or replace anything, and ship the fix as a new version. If it stops with `already exists at a different commit`, never move the tag; investigate the tag and ship a new version.

### 12. Only the website deploy failed

The release is published and complete but [aw.isainative.dev](https://aw.isainative.dev/) still shows the old edition. Redeploy the release, or `main`:

```sh
gh workflow run deploy-pages.yml -f ref=content-vX.Y
gh workflow run deploy-pages.yml
```

The second form deploys `main`, which succeeds when `main`'s `content/` and `examples/` equal the latest published edition, as they do after a complete release. The same command works if you only need to redeploy after a tooling change. You can also re-run the failed `pages` job of the **Release book** run.

### 13. A published release is wrong, or the site must go back

Do not edit the release or move its tag. Fix `main` through scenario 1 and release a new patch edition, for example `1.2.1`. To put an earlier edition back on the website immediately (the rollback path), deploy its published tag:

```sh
gh workflow run deploy-pages.yml -f ref=content-v1.2
```

The workflow accepts only a published, non-draft, non-prerelease `content-vX.Y` tag (or its commit) that is on `main` and carries `content/VERSION`, so `content-v1.2` and later. Branches, unreleased commits and the legacy tags `content-v1.0` and `content-v1.1` are refused. A rollback changes only the website; the next release or push to `main` deploys the newest edition again. The controller refuses to create an older edition after a newer one.

### 14. Choosing the version

Follow the table in [Prepare the edition](#prepare-the-edition). When unsure, ask what a reader of the last edition would notice: a restructured book is major, new chapters or material are minor, corrections are patch. The version must exceed every published `content-v*` release and the version on `main`; the check tells you if it does not.

### 15. Control center alerts

If you use the book control center, each alert has a fix on this page:

| Alert | Cause and fix |
| --- | --- |
| `PR #N is ready for your approval` | Preflight is green. Approve the head (scenario 2) or comment `/release-book <SHA>` (scenario 1). |
| `PR #N release preflight is failing` | Open the failed **Book CI** run. Fix the PR, or re-run failed jobs if the failure was transient. |
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
