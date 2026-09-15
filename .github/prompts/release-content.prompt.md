---
description: Prepare a content-only book release with fresh editorial evidence, an edition bump, changelog, and verified HTML/PDF output; leave publishing behind a reviewed PR.
---

# Release Content

Prepare a new **content edition** of the GitHub Agentic Workflows book. This prompt packages
reviewed material; it does not discover upstream changes or update chapters. For a framework
refresh, first run `.github/prompts/update-book.prompt.md`.

**What changed:** <content-change summary, or inspect the pending content diff>
**Baseline release:** <last published content-v tag; resolve it if unset>
**Version bump:** <major | minor | patch | explicit x.y or x.y.z>
**Publication boundary:** open a PR and stop; a human reviews and merges it.

## Sources of truth

- `content/VERSION`: the book's content edition, independent of framework/tooling versions.
- `content/FRAMEWORK_VERSION`: the exact gh-aw tag the current book has been verified against.
- `content/CHANGELOG.md`: per-edition reader-facing notes, preserved for older editions.
- `content/release-review.json`: actual editorial ACCEPT, bound to manuscript/example/TOC/
  framework inputs and its referenced review report. It is not an identity signature.
- `scripts/content_version.py`: version/tag/notes parsing.
- `scripts/release_content.py`: source-change, release, and fresh-review guards.
- `scripts/verify_examples.py`: strict, isolated, pinned whole-corpus compilation.

## Steps

1. **Resolve the actual baseline.** Read the latest published `content-v*` release and its
   commit, not the proposed new edition's nonexistent tag. Ensure the baseline is locally
   available. Read git status and preserve unrelated work.
2. **Confirm reader-visible changes**, including committed, staged, unstaged, untracked,
   moved, and deleted source files:
   ```powershell
   python scripts\release_content.py changes --base <baseline-tag>
   ```
   The release scope is authored chapter content and meaningful TOC changes. VERSION,
   CHANGELOG, framework/evidence metadata, research, the brief, examples alone, generated
   HTML, analytics, and tooling do not justify a new prose edition. If there are no
   reader-visible changes, stop without a bump.
3. **Require real acceptance.** Read the verification and editorial reports; never infer
   ACCEPT from a successful build. The report must contain exactly one standalone
   `Verdict: ACCEPT` line consistent with the attestation. Any changes to covered inputs
   require renewed review.
   Use the current `content/FRAMEWORK_VERSION` for all compilation; do not install "latest".
4. **Choose the edition from the actual scope:**
   - MAJOR: structural rewrite or reordering.
   - MINOR: new chapters, sections, or substantive material (`1.1` -> `1.2`).
   - PATCH: corrections/clarifications only (`1.1` -> `1.1.1`).
   Book versions must be well-formed and increase; they never mirror gh-aw's version number.
5. **Add a changelog entry** above the existing entries and update `content/VERSION`:
   ```markdown
   ## [1.2] - YYYY-MM-DD

   One-line reader-facing summary, including the verified gh-aw target when it changed.

   ### Added
   - **Topic:** what the reader can now learn or do.

   ### Fixed
   - **Correction:** what changed and why it matters.
   ```
   Use today's date and only headings/items that apply. Never rewrite old release history.
6. **Run the complete local gate** (provide `--compiler <absolute-executable>` when using
   the Windows isolated installer):
   ```powershell
   python -m unittest discover -s scripts\tests
   python scripts\release_content.py check --base <baseline-tag>
   python scripts\verify_examples.py
   python site\generate.py
   python scripts\build_pdf.py
   python scripts\release_content.py check-generated
   ```
   The compiler must match `content/FRAMEWORK_VERSION` exactly. Every standalone example
   must compile; live execution may be omitted, compile failures may not. Inspect the
   generated site's version history, framework coverage, and PDF edition stamps.
7. **Commit only this release's files:** reviewed chapter/TOC/example changes, versioned
   research and review evidence, framework baseline, changelog/edition, and regenerated
   tracked `site` output. Do not commit PDFs, binaries, raw downloads, secrets, or unrelated
   work. Suggested message: `Prepare content v<edition> for gh-aw <target>`, with trailer:
   `Co-authored-by: Copilot App <223556219+Copilot@users.noreply.github.com>`.
8. **Open a PR using the available PR-creation tool.** Describe the baseline/target,
   reader-visible changes, verification, and editorial verdict. Wait for the validation
   workflow and leave the PR for human review. Do not merge, create a release/tag, or
   dispatch publishing as part of preparation.

## After the human merges

`validate-book.yml` builds and gates the exact artifacts consumed by both publishing
workflows. `deploy-pages.yml` publishes that site/PDF without rebuilding;
`release-content.yml` creates `content-v<edition>` with the matching
`gh-aw-book-v<edition>.pdf` and changelog notes. Verify both workflow outcomes, the release
asset, and the live version-history page before calling the edition published.

An existing complete release is a no-op. A missing-asset repair must use the original tagged
source; never attach a newly built HEAD PDF to an older tag. Legacy releases that predate
the build/version metadata need an explicit historical recovery procedure, not invented
defaults. Manual publication is a separate, explicitly authorized operation, not a shortcut
around the review and compilation gates.
