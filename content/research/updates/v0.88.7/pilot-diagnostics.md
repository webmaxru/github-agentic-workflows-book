# Chapter 12 pilot verification — technical PASS

**Target: gh-aw v0.88.7. No compiler, metadata, environment, cleanup, or
help-parser errors. No source fixes applied.**

This is a technical pilot result for `chapter-reviewer`, not editorial ACCEPT,
deployment/secret approval, publication, or a global review attestation.
Runtime and optional validation/scanner checks remain **NOT RUN**.

## Canonical full-corpus gate

Executed from the book worktree:

```powershell
python scripts\verify_examples.py --compiler 'C:\Users\masalnik\.copilot\session-state\e9e760c4-bdb3-46e7-b867-b7f4d7e28a28\files\tools\gh-aw\v0.88.7\gh-aw.exe' --version v0.88.7 --report content\research\updates\v0.88.7\pilot-verification.json
```

- Actual version output: **`gh aw version v0.88.7`**.
- Run: **2026-09-15 23:33:55.586–23:34:41.289 UTC**; CLI exit **0**.
- Overall report **PASS**, **14 passed / 0 failed**, **14 nonempty locks**.
- Each emitted lock header independently confirmed
  **`compiler_version: "v0.88.7"`** and literal **`strict: true`**.
- The hardened verifier's metadata checks were present before the run. Its
  SHA-256 stayed stable through both source and embedded compilation:
  `783491d5c44e14dba37a0ffbabd91174ea02faadc370d7a386ab094c9d057273`.
- Isolated compiler SHA-256:
  `8d88047c1e162f16a01e1920124092c80a8bdf98c1635357067a0ac34c00d4c7`.
- All 14 compiler processes exited zero. Overall PASS and CLI exit zero were
  required separately; zero failed workflows alone was not accepted.

**Runtime: NOT RUN for every row.** Locks were emitted, checked, and removed
with the isolated repositories; none were added to the real workflows tree.

| Example under `examples/` | Compile | `gh aw` | Lock | Lock strict | Warnings |
|---|---|---|---|---|---|
| `ch02/repo-assistant-triage.md` | PASS | v0.88.7 | Yes | true | 0 |
| `ch04/repo-assistant-triggers.md` | PASS | v0.88.7 | Yes | true | 0 |
| `ch05/repo-assistant-claude.md` | PASS | v0.88.7 | Yes | true | 1: secret review |
| `ch06/repo-assistant-open-pr.md` | PASS | v0.88.7 | Yes | true | 0 |
| `ch07/repo-assistant-hardened.md` | PASS | v0.88.7 | Yes | true | 0 |
| `ch08/repo-assistant-tools.md` | PASS | v0.88.7 | Yes | true | 0 |
| `ch09/continuous-docs.md` | PASS | v0.88.7 | Yes | true | 0 |
| `ch09/continuous-triage.md` | PASS | v0.88.7 | Yes | true | 0 |
| `ch10/continuous-review.md` | PASS | v0.88.7 | Yes | true | 0 |
| `ch10/daily-test-improver.md` | PASS | v0.88.7 | Yes | true | 0 |
| `ch11/repo-assistant-shared.md` | PASS | v0.88.7 | Yes | true | 0 |
| `ch12/repo-assistant-observable.md` | PASS | v0.88.7 | Yes | true | 1: secret review |
| `ch13/repo-assistant-budgeted.md` | PASS | v0.88.7 | Yes | true | 0 |
| `ch14/fleet-triage.md` | PASS | v0.88.7 | Yes | true | 0 |

Independent discovery matched the report exactly: **14 standalone workflows
and 2 shared fragments**, with no omissions or duplicates.

| Fragment under `examples/` | Importer | Status / lock |
|---|---|---|
| `ch11/shared/triage-policy.md` | `ch11/repo-assistant-shared.md` | PASS as v0.88.7 import; importer lock emitted |
| `ch14/shared/triage-policy.md` | `ch14/fleet-triage.md` | PASS as v0.88.7 import; importer lock emitted |

Fragments are dependencies, not skipped standalone lock targets.

## New Chapter 12 block: source-equivalent and independently compiled

`content/chapters/observability-and-debugging.html:158-190`, code block **9**,
is a complete workflow and **matches**
`examples/ch12/repo-assistant-observable.md`.

Comparison decoded HTML entities, normalized line endings to LF, and normalized
outer whitespace only. No fields, comments, or prompt text were rewritten.
The exact diff is empty. The source and independently compiled embedded copy
also have identical lock `frontmatter_hash` and `body_hash`.

The inventory covered all **14 chapters / 67 code blocks** and found **3 complete
workflows**. All three were re-extracted unchanged and compiled through the
current verifier, with a generated temporary `--root` and a separate report:

| Embedded workflow | Source consistency | Compile | `gh aw` | Nonempty lock / strict |
|---|---|---|---|---|
| `observability-and-debugging.html:158-190` | MATCH to ch12 source | PASS | v0.88.7 | Yes / true |
| `what-are-agentic-workflows.html:83-105` | Historical annotated/abridged ch02 variant; unchanged since preflight | PASS | v0.88.7 | Yes / true |
| `your-first-workflow.html:142-178` | MATCH to ch02 source | PASS | v0.88.7 | Yes / true |

Embedded verifier: **overall PASS, exit 0, 3 passed / 0 failed**, run
**23:33:56.172–23:34:06.794 UTC**. Runtime: **NOT RUN** for all three.
The Chapter 1 difference is retained in the new inventory, not silently relabeled
as an exact copy. It is not a new pilot change.

## Chapter 12 CLI checks — help only

Captured the exact isolated target's `logs --help`, `audit --help`,
`status --help`, and `compile --help`: **4/4 exit zero**.

Inventoried **24 unique chapter command recipes** and matched their flags to
that captured help. In addition, **22 logs/audit recipe probes** were invoked
with **`--help` present**, each returning exit zero and byte-for-byte identical
stdout/stderr to its captured subcommand help. No operational handler was run.
The exact argument vectors, output hashes, and raw-output references are saved.

| Checked surface | Target-help result |
|---|---|
| Multiple logs targets and cross-repository paths | Documented usage/examples; count applies per workflow |
| `--count`, `--start-date`, `--exclude-staged` | Supported; default count 10 per workflow; `-1w` documented |
| `--runtime`, `--evals`, `--graders` | Supported record filters |
| `--artifacts` | `all` and `agent,firewall` documented; default `usage` |
| `--audit` on logs | Supported cached `audit.json` generation from downloaded runs |
| `--max-storage`, `--prune-older-runs` | MB budget, zero unlimited; oldest-run removal documented |
| `--max-github-api-rate-limit`, `--timeout` | Used core requests / negative reserve; timeout in minutes |
| Audit `--repo`, run/job URLs, baseline/comparison arguments | Documented; bare-ID example explicitly requires `--repo` |
| `compile --strict` | Supported and actually used for the isolated compilation gate |
| Old `--no-staged` spelling | Not advertised; chapter correctly uses documented `--exclude-staged` |
| Prose mentions of `--validate` and `--approve` | Definitions checked in compile help only; neither flag invoked |

**Limits:** help/parser acceptance is not live behavior proof. In particular,
`--runtime` accepts a string; accepting `docker` does not prove available matching
runs or Docker functionality. Placeholder URLs/repositories were not resolved.
No logs, audit, status query, artifact download, cache pruning/deletion,
remote workflow execution, or scanner operation was performed. No inference,
telemetry delivery, endpoint reachability, or authentication was tested.

## Approval warnings remain unwaived

The Chapter 12 source and embedded copy each emitted **one** safe-update warning.
Exact diagnostic heading and secret-name list from the source compilation:

```text
.github\workflows\repo-assistant-observable.md: warning: safe update mode detected unapproved changes

New restricted secret(s):
  - OTLP_ENDPOINT
  - OTLP_TOKEN
```

Full stderr, including **`SECURITY REVIEW REQUIRED`** and all remediation text,
is retained in both compilation reports. The chapter's selected preflight
warning lines remain accurate; the unchanged historical report is preserved.

The whole-corpus run also retained the ch05 warning for `ANTHROPIC_API_KEY`.
Thus the canonical run has **2 warnings total**, not 2 compiler failures.
No `--approve` was used, no secret values were supplied/read/echoed, and no
security approval was granted.

**Owner/action:** chapter-reviewer should retain the chapter's distinction
between compile PASS and reviewed secret/telemetry deployment. A separately
authorized deployment review must assess the intended collector and credentials.
There is no compile typo or source fix to hand back.

## Repository context, environment, and preservation

| Gate | `repository_context.source` | Sanitized URL |
|---|---|---|
| Canonical corpus | `source-origin` | `https://github.com/webmaxru/github-agentic-workflows-book.git` |
| Generated embedded corpus | `book-default` | `https://github.com/webmaxru/github-agentic-workflows-book.git` |

Both reports retain **`environment_errors: []`** and have **no
`cleanup_pending`**. The helper staged under its checkout's ignored `build/v`
and cleaned its run directories. Origin configuration did not fetch or change
the real repository's remote. The six preflight schedule-context warnings are
absent in this fresh run; their historical output was not edited.

Verification-process `TEMP`, `TMP`, and `TMPDIR` were worktree-local `build/pt`.
No real workflow probe or `.github/aw/logs` directory was created.
Postflight checks matched **40 input hashes** and **all 5 preflight artifact
hashes**, confirmed no added/deleted example/chapter/real-workflow files, and
confirmed all **six Chapter 12 section slots** retained in order.

Among manuscript/example inputs, only the already-authored Chapter 12 manuscript
differed from preflight. All 16 example files remained unchanged. This verifier
made **zero source edits**. The worktree's pre-existing tooling/generated-site
changes were not altered. The personal extension and framework baseline remain
**v0.81.6**, and the content edition remains **1.1**.

## Fresh evidence and handoff

All files below are new under `content/research/updates/v0.88.7/`:

- `pilot-verification.json` — canonical results, exact compiler output, lock metadata.
- `pilot-embedded-verification.json` — three embedded compilation results and metadata.
- `pilot-embedded-inventory.json` — locations, source equivalence/diffs, extraction hashes, invocation.
- `pilot-cli-help.json` — exact target version and raw subcommand help.
- `pilot-cli-verification.json` — recipe/flag inventory and 22 help-only probes.
- `pilot-inputs.json` — input/compiler fingerprints and preservation baseline.
- `pilot-verification-summary.json` — gate audit, exit statuses, contexts, and evidence hashes.
- `pilot-diagnostics.md` — this review-ready handoff.

**No technical verification blocker remains for the Chapter 12 pilot.**
Proceed to `chapter-reviewer`; no editorial/global review attestation or metadata
advance was performed. No commits, pushes, publication, or runtime runs occurred.
