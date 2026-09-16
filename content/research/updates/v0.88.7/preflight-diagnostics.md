# v0.88.7 existing-book compatibility preflight

**Canonical result: PASS — 14/14 standalone workflows, 0 failures, 14 nonempty
locks. Both shared fragments passed through their importing workflows.**

This is preparation for the next edition, **not publication, editorial ACCEPT,
or final post-author verification**. `content/FRAMEWORK_VERSION` remains
`v0.81.6`; `content/VERSION` remains `1.1`. No example, chapter, baseline, verifier,
or real `.github/workflows` file was edited by this preflight. No minimal fixes,
`--fix`, `--approve`, workflow runs, commits, pushes, or publication commands were
used. Runtime status for every item below is **NOT RUN**; no engine secrets were
used. Compilation does not establish runtime behavior or security approval.

## Reproduction and evidence

Working directory:

```text
C:\Users\masalnik\scoop\buckets\copilot-worktrees\github-agentic-workflows-book\webmaxru-turbo-happiness
```

Exact canonical invocation:

```powershell
python scripts\verify_examples.py --compiler 'C:\Users\masalnik\.copilot\session-state\e9e760c4-bdb3-46e7-b867-b7f4d7e28a28\files\tools\gh-aw\v0.88.7\gh-aw.exe' --version v0.88.7 --report content\research\updates\v0.88.7\preflight-verification.json
```

- Actual compiler output: `gh aw version v0.88.7`; equality with the explicit
  `--version v0.88.7` was checked before compilation.
- Isolated executable SHA-256:
  `8d88047c1e162f16a01e1920124092c80a8bdf98c1635357067a0ac34c00d4c7`.
  This matches the already-installed binary recorded in `impact.json`.
- Run: **2026-09-15 21:57:13.582–21:57:54.837 UTC**; verifier exit **0**.
- Python **3.12.10**, Git **2.53.0.windows.4**, GitHub CLI **2.98.0**.
- The personal extension was observed as `gh aw version v0.81.6` and was not
  replaced. All accepted compilations used the absolute isolated executable.
- Every target was compiled as
  `<isolated-compiler> compile --strict .github\workflows\<filename>.md`
  in a fresh project-local temporary Git repository. The helper required exit
  zero **and** an emitted, nonempty `.lock.yml`; no `--no-emit` or waiver was used.
- For verification processes, `TEMP`, `TMP`, and `TMPDIR` were explicitly set to
  the absolute worktree-local `build\verify-examples\preflight-os-temp` directory.
  `PYTHONDONTWRITEBYTECODE=1` and `PYTHONIOENCODING=utf-8` were also set.
  `build/` was confirmed gitignored. Generated repositories and locks were
  removed after inspection; none were added to the book's real workflows.
- The canonical helper's full JSON stdout was suppressed in the shell only to
  avoid a large terminal dump; `--report` saved its unmodified results, including
  every compiler stdout/stderr string. Nothing was piped to a log file.

New evidence in this directory:

| Artifact | Purpose |
|---|---|
| `preflight-verification.json` | Canonical 14-workflow results and exact compiler output |
| `preflight-inputs.json` | Exact command, versions, binary/report hashes, 37 input-file hashes, and both import edges |
| `preflight-embedded-inventory.json` | Complete embedded-block locations, source mapping, exact diffs, extraction hashes, and supplemental attempt history |
| `preflight-embedded-verification.json` | Separate strict compilation results for the two unchanged complete embedded workflows |
| `preflight-diagnostics.md` | This author/tooling handoff |

The worktree already contained tooling/research changes. The input hashes bind
this evidence to the actual snapshot, not merely to HEAD
`95e9e56b4e193ed41568ce4004f3498fdcd86f26`. Earlier research was not overwritten.
No upstream release-delta research was performed here.

The postflight audit matched **all 37 input-file hashes and all 3 recorded
machine-report/inventory hashes**, confirmed the executable hash, and found no
added or deleted examples, chapters, or real workflow files. It also re-extracted
the embedded blocks to confirm their recorded hashes and confirmed that the
preflight's temporary repositories had been removed.

## Per-example verification

All locks below were emitted in isolated repositories, checked as nonempty,
then removed by temporary-directory cleanup. **Runtime: NOT RUN for every row.**

| Example path | Compile | `gh aw` | Lock emitted | Compiler warning |
|---|---|---|---|---|
| `examples/ch02/repo-assistant-triage.md` | PASS | v0.88.7 | Yes | None |
| `examples/ch04/repo-assistant-triggers.md` | PASS | v0.88.7 | Yes | Schedule context |
| `examples/ch05/repo-assistant-claude.md` | PASS | v0.88.7 | Yes | Restricted-secret review |
| `examples/ch06/repo-assistant-open-pr.md` | PASS | v0.88.7 | Yes | None |
| `examples/ch07/repo-assistant-hardened.md` | PASS | v0.88.7 | Yes | None |
| `examples/ch08/repo-assistant-tools.md` | PASS | v0.88.7 | Yes | None |
| `examples/ch09/continuous-docs.md` | PASS | v0.88.7 | Yes | Schedule context |
| `examples/ch09/continuous-triage.md` | PASS | v0.88.7 | Yes | Schedule context |
| `examples/ch10/continuous-review.md` | PASS | v0.88.7 | Yes | None |
| `examples/ch10/daily-test-improver.md` | PASS | v0.88.7 | Yes | Schedule context |
| `examples/ch11/repo-assistant-shared.md` | PASS | v0.88.7 | Yes | Schedule context |
| `examples/ch12/repo-assistant-observable.md` | PASS | v0.88.7 | Yes | Restricted-secret review |
| `examples/ch13/repo-assistant-budgeted.md` | PASS | v0.88.7 | Yes | Schedule context |
| `examples/ch14/fleet-triage.md` | PASS | v0.88.7 | Yes | None |

Independent filesystem discovery found exactly **16 Markdown files: 14
standalone workflows and 2 files under `shared/`**. The canonical report's
workflow and fragment sets match exactly, with no omitted or duplicate targets.

| Shared fragment | Importing workflow | Integration result | `gh aw` | Lock |
|---|---|---|---|---|
| `examples/ch11/shared/triage-policy.md` | `examples/ch11/repo-assistant-shared.md:15-16` | PASS as import | v0.88.7 | Importer emitted; no standalone fragment lock |
| `examples/ch14/shared/triage-policy.md` | `examples/ch14/fleet-triage.md:16-17` | PASS as import | v0.88.7 | Importer emitted; no standalone fragment lock |

Both fragments lack an `on:` trigger and are dependency inputs, not skipped
standalone targets. Their original chapter-relative paths were preserved.

## Compiler failures and actionable warnings

**There are no canonical compiler failures or compiler errors to diagnose.**
The following are real warnings on successful strict compilations, not waived
errors. Eight workflows each reported one warning.

### W1 — six fuzzy schedules lack repository context in the fixture

Exact warning:

```text
⚠ Fuzzy schedule scattering without repository context. Workflows with the same name in different repositories may collide. Ensure you are in a git repository with a configured remote.
```

Affected: ch04 triggers, both ch09 workflows, ch10 daily-test-improver, ch11
shared, and ch13 budgeted.

**Diagnosis:** the canonical helper initializes isolated Git repositories
without a remote, so these compilations cannot prove repository-specific
schedule scattering. This is not a frontmatter rejection.

**Owners/action:** parent/tooling agent can consider a deterministic repository
context for future fixtures; chapter-author should not reuse old
“0 warnings” transcripts as this target's observed output. No remote, seed,
or example was changed in this preflight.

### W2 — two examples require restricted-secret security review

Exact diagnostic headings and secret-name lists:

```text
.github\workflows\repo-assistant-claude.md: warning: safe update mode detected unapproved changes

New restricted secret(s):
  - ANTHROPIC_API_KEY
```

```text
.github\workflows\repo-assistant-observable.md: warning: safe update mode detected unapproved changes

New restricted secret(s):
  - OTLP_ENDPOINT
  - OTLP_TOKEN
```

The complete compiler messages, including remediation options and
`SECURITY REVIEW REQUIRED`, are retained verbatim in the canonical JSON.

**Diagnosis:** fresh fixtures have no prior approval manifest. The Claude engine
is selected at `examples/ch05/repo-assistant-claude.md:6-9`; the OTLP secret
references are explicit at
`examples/ch12/repo-assistant-observable.md:17-21`. The compiler emitted locks
but requested review of these restricted references. No secret values were
read, printed, provided, or approved.

**Owners/action:** chapter-author and chapter-reviewer should explain this
target's review requirement and have the intended credential/telemetry use
reviewed before deployment. This preflight does not approve an actual OTLP
destination or credential configuration. Do not hide the warnings with
`--approve` merely to reproduce a historical clean transcript.

### I1 — Copilot billing tip, not a warning or error

The thirteen Copilot source workflows emit an informational
`permissions.copilot-requests` tip. It distinguishes Actions-token inference
from the `COPILOT_GITHUB_TOKEN` PAT path and states the organization billing
prerequisite. It did not affect PASS/FAIL or the eight-warning count.
No permission change was made to silence it.

## Embedded manuscript inventory and source consistency

Read all **14 chapter HTML files** and all **62 `<pre><code>` blocks**.
There are **2 complete Markdown workflows**: opening/closing frontmatter
delimiters, an `on:` field, and a nonempty body. The other **60** blocks are
frontmatter/body excerpts, commands, generated-lock excerpts, or other
configuration; they are not silently counted as full standalone workflows.
Non-research Markdown elsewhere under `content/` contains no fenced workflows.

Both complete blocks name `examples/ch02/repo-assistant-triage.md` in their
captions. HTML entities were decoded and only outer whitespace/line endings
normalized before comparison and separate compilation.

| Embedded block | Source comparison | Supplemental compile | `gh aw` | Lock emitted | Runtime |
|---|---|---|---|---|---|
| `content/chapters/what-are-agentic-workflows.html:83-105` (block 1) | DIFFERS: annotations and abbreviated prompt | PASS | v0.88.7 | Yes | NOT RUN |
| `content/chapters/your-first-workflow.html:142-178` (block 8) | MATCH after normalization | PASS | v0.88.7 | Yes | NOT RUN |

**Author-ready finding E1:** Chapter 1's frontmatter differs only by explanatory
inline comments, but its shorter prompt omits the source's detailed triage
instructions, vague/empty-issue fallback, and safe-output explanation. This is
**behavioral/presentation drift, not a syntax incompatibility**. Owner:
chapter-author. During authorized authoring, either label it clearly as an
annotated, abridged variant or align it with the source. Compilation does not
prove those two prompts behave identically. Chapter 2 has no source drift.

**Copyability note E2:** the shared-fragment excerpt at
`content/chapters/reuse-and-memory.html:98-109` omits the opening `---` and
abbreviates the description/body of
`examples/ch11/shared/triage-policy.md`. It is not a complete standalone
workflow. The actual fragment passed through its importer. Owner:
chapter-author; make the excerpt boundary explicit if readers are expected to
copy it as a complete fragment. No delimiter was inserted for this preflight.

For the supplemental check, the unchanged complete blocks were copied to
`examples/embedded/ch01.md` and `ch02.md` **inside a generated, ignored
temporary corpus**, never the book's `examples/` tree. The same verifier ran
with `--root <temporary-corpus>`, the same absolute compiler, explicit
`--version v0.88.7`, and a separate `--report`. The inventory records the exact
argument vector and hashes needed to reconstruct those two inputs.
The successful supplemental run was **22:01:57.394–22:02:02.965 UTC**,
exit **0**, **2/2 PASS**, **2 nonempty locks**, **0 warnings**.
These two tests are separate from, and do not inflate, the canonical 14 count.

## Supplemental harness failure retained, then resolved without edits

The first, optional embedded-block attempt used an excessively nested
project-local root. The helper exited **1 during cleanup**, before saving its
report. Its exact verifier error was:

```text
ERROR: [WinError 145] The directory is not empty: 'C:\Users\masalnik\scoop\buckets\copilot-worktrees\github-agentic-workflows-book\webmaxru-turbo-happiness\build\verify-examples\preflight-os-temp\embedded-corpus-q0bzyy2j\build\verify-examples\run-5oshg3ax\0\.github\workflows'
```

A remaining generated lock's full path measured **260 characters**. This is
consistent with a Windows nested-path/cleanup limitation, not evidence of a
workflow schema error. No per-example result from that attempt was accepted:
an emitted file alone could not substitute for the missing run report.
Its failure is retained in the inventory's `earlier_supplemental_attempt`.

The blocks were re-extracted unchanged and reverified using a shorter
`build\e-<random>` root and shorter basenames. That attempt produced the
separate successful report above. The failed attempt's own residual directory
was then removed using Windows extended-length paths; both supplemental
corpora and the canonical scratch repositories are gone.

**Tooling handoff:** parent/tooling agent should consider long-path-safe
cleanup and retaining a report even when cleanup fails. No verifier/tooling
fix was applied here. The requested canonical run succeeded on its first
attempt and its report was never overwritten.

## Handoff boundary

No source migration is required merely to make the current 14-workflow corpus
compile with v0.88.7. This does **not** settle release-delta accuracy, the warning
reviews, or the embedded prompt difference. Keep the baseline at v0.81.6 until
the parent requests and accepts final post-author verification. All status tags
are in these new research reports; no example bodies were edited.
