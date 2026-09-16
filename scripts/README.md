# Updating and Releasing the Book

The normal operation is **incremental maintenance**, not a new whole-book build.
Saved prompts coordinate the existing specialist agents; deterministic helpers and CI
enforce the release prerequisites.

The update/release helpers require **Python 3.12**, Git, and GitHub CLI; the CI gate
uses Python 3.12. The Windows installer/launcher require PowerShell 7.

| Operation | Saved prompt | Launcher |
| --- | --- | --- |
| Follow a framework release | `/update-book` | `.\scripts\run-fleet.ps1` |
| Package reviewed content | `/release-content` | `.\scripts\run-fleet.ps1 -Mode Release` |
| Build a new book from its brief | `/run-playbook` | `.\scripts\run-fleet.ps1 -Mode Bootstrap` |

The launcher now defaults to **Update**. Bootstrap is an explicit mode so ordinary
maintenance does not rebuild architecture or scaffold over existing chapters.

```powershell
# Preview without launching Copilot or requiring it to be installed.
.\scripts\run-fleet.ps1 -Mode Update -TargetVersion v0.88.7 -DryRun

# Run against a fixed target, or omit TargetVersion to resolve latest stable once.
.\scripts\run-fleet.ps1 -Mode Update -TargetVersion v0.88.7

# An explicitly selected custom prompt remains supported.
.\scripts\run-fleet.ps1 -PromptPath .github\prompts\new-chapter.prompt.md
```

`-PromptPath` cannot be combined with `-Mode`/`-TargetVersion`. The headless launcher uses
`copilot -p ... --allow-all-tools`, which grants broad tool access; use an interactive
Copilot session instead when you want per-action approvals. Prompts stop at a prepared PR.
They do not grant permission to merge, dispatch publishing, or create a release.

## Version and evidence contracts

- `content\VERSION`: reader-visible content edition, e.g. `1.2` or `1.2.1`.
- `content\FRAMEWORK_VERSION`: exact validated gh-aw tag, separate from the edition.
- `content\CHANGELOG.md`: content release notes; old entries remain unchanged.
- `content\research\updates\<target>\`: new cited delta, chapter decisions, compilation
  evidence, and actual editorial review. Earlier per-chapter research stays historical.
- `content\release-review.json`: current ACCEPT bound to the manuscript, TOC, examples,
  framework baseline, and review report. It is a process record, not an identity signature.

The update prompt records a target once, researches the entire baseline-to-target interval,
updates only affected chapters, verifies every example, and gets cross-chapter acceptance.
Only then does it advance the framework baseline and prepare the prose edition.

## Exact compiler, no live workflows

```powershell
# Use the book's validated framework version, or an explicitly saved update target.
.\scripts\install-gh-aw.ps1
.\scripts\install-gh-aw.ps1 -Version v0.88.7
```

The installer prints a checksum-verified executable path in an ignored worktree-local
cache. `-InstallDir` selects another isolated directory. It does not replace the personal
`gh aw` extension. Use that executable consistently:

```powershell
python scripts\verify_examples.py --compiler <absolute-gh-aw-executable> --version v0.88.7 --report <verification-json>
```

The verifier checks the actual compiler version, stages each standalone workflow with its
relative shared imports in a temporary git repository, requires strict compilation and a
lock with matching compiler/strict metadata, records all results, and fails on any error.
Require overall `status: PASS` and exit zero: cleanup/setup errors preserve results but
fail the run even if every workflow compiled. The report identifies the sanitized repository
context used for schedule scattering. Shared fragments are dependencies.
There are no live `gh aw run` calls and no engine secrets. Runtime credentials cannot
justify skipping compilation.

Optional `--validate`, container/scanner checks, and live execution have separate
environment requirements; they are not implied by this source-compilation gate. In
particular, an example using Issues needs Issues enabled in its deployment repository.
Restricted-secret review warnings remain in stderr and are never hidden with `--approve`.

For `examples\<chapter>\strict-policy\`, keep `aw.json` directly beside the workflow.
The verifier stages this self-contained directory as `.github\workflows` and omits
the CLI `--strict` flag, so the emitted `strict: true` must come from the repository
policy. A missing, ignored, malformed, or ineffective policy fails instead of falling
back to a forced CLI override. Ordinary workflows still use `--strict`.

Regular nonignored Markdown, JSON, YAML, TXT, and example-local `.gitignore` inputs
are staged and bound into review fingerprints; generated locks/build output are not.
The report records the compilation mode and policy digest. Unsupported binary/source
types fail explicitly rather than disappearing from the proof.

On a fresh Linux CI runner, the equivalent is a pinned extension:

```bash
gh extension install github/gh-aw --pin "$(cat content/FRAMEWORK_VERSION)"
python scripts/verify_examples.py
```

## Prepare and validate an edition

Resolve the last published content tag before changing the version:

```powershell
python scripts\release_content.py changes --base content-v1.1
```

This includes pending staged/unstaged/untracked edits, renames, and deletions, not just
`HEAD`. Only reader-visible chapter/TOC changes justify a prose edition. Research,
version/evidence metadata, examples alone, generated output, and tooling do not.

After a real reviewer returns ACCEPT, record the report. It must contain exactly one
standalone `Verdict: ACCEPT` line matching the supplied verdict:

```powershell
python scripts\release_content.py record-review --report content\research\updates\<target>\review.md --verdict ACCEPT
```

Then update `content\VERSION` and its changelog entry and run the local gate:

```powershell
python -m unittest discover -s scripts\tests
python scripts\release_content.py check --base <last-content-tag>
python scripts\verify_examples.py --compiler <absolute-gh-aw-executable>
python site\generate.py
python scripts\build_pdf.py
python scripts\release_content.py check-generated
```

The framework target defaults to `content\FRAMEWORK_VERSION` for the final gate. Covered
source changes invalidate the review record; obtain renewed verification/review rather
than simply regenerating a fingerprint. PDFs and compiler binaries are build artifacts,
not committed sources.

## CI and publication boundary

`validate-book.yml` runs on PRs and is reused by both publishing workflows. It checks the
helpers, release/evidence contract, pinned whole-corpus compilation, and HTML/PDF generation.
The PR still needs human review/merge; these workflows do not configure branch protection.

After merge, `deploy-pages.yml` publishes the current online/PDF edition and
`release-content.yml` publishes its matching tag, changelog notes, and versioned PDF.
Both consume the exact artifacts produced by validation instead of rebuilding afterward.
The release workflow also evaluates content/example/tooling pushes; a complete existing
release is a no-op, not a new tooling edition. Missing-asset repair must build the original tagged
source, never a different HEAD under an old edition label. Legacy tags without build/version
metadata require explicit historical recovery. A failed/empty existing upload is surfaced
for recovery, not mistaken for a complete PDF or silently overwritten.

## Resume an interrupted update

Read the saved impact map for the fixed target, existing evidence, git checkpoints, and
session todos. Reuse completed research and accepted waves only while their source inputs
still match. Do not resolve a new latest release on resume or overwrite historical evidence.
The plan moves through `researching`, `researched`, `authoring`, `verified`, `accepted`,
and `prepared`. Only unfinished states resume automatically. A prepared plan records its
edition, `prepared_fingerprint`, and PR URL; later fresh updates ignore it when resolving
a new upstream target. If the target and fingerprint still match, reuse the existing PR
without bumping again. Determine a default bump from the last published edition, not from
an already proposed version. Prose-only followups reuse framework research and preserve old
review reports under distinct edition/revision filenames.
If the fixed target is already covered and there are no reader-visible changes, stop without
creating an empty edition.
