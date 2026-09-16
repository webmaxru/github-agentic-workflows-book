# Completed workflow corpus — v0.88.7 verification

**Technical result: PASS.** The frozen corpus contains **24 standalone
workflows**, **2 shared fragments**, and **4 non-Markdown inputs**. All 24
workflows passed with exit zero and nonempty locks whose metadata confirms
exactly **`compiler_version: v0.88.7`** and literal **`strict: true`**.

The **16 complete embedded workflows** also passed, including their shared
fragments and the policy-dependent Chapter 13 copy. Their text and compiled
frontmatter/body hashes match the corresponding source workflows.

This is compile-time proof for the captured chapter/example snapshot, **not
editorial ACCEPT, deployment approval, publication, or a global review
attestation**. Parent-managed TOC/brief alignment remains separate.

## Compiler, invocation and gates

Actual version output: **`gh aw version v0.88.7`**.
Canonical run: **2026-09-16 02:17:43.469–02:19:06.306 UTC**.
Overall report **PASS**, CLI exit **0**, **24 passed / 0 failed**.

```powershell
python scripts\verify_examples.py --root 'C:\Users\masalnik\scoop\buckets\copilot-worktrees\github-agentic-workflows-book\webmaxru-turbo-happiness\build\w-_2w7tx26' --compiler 'C:\Users\masalnik\.copilot\session-state\e9e760c4-bdb3-46e7-b867-b7f4d7e28a28\files\tools\gh-aw\v0.88.7\gh-aw.exe' --version v0.88.7 --report content\research\updates\v0.88.7\verification.json
```

- Compiler SHA-256:
  `8d88047c1e162f16a01e1920124092c80a8bdf98c1635357067a0ac34c00d4c7`.
- `scripts/verify_examples.py` SHA-256:
  `8006500fdffe068d0f9117f3130fa92b2a25d1daa6b24161673c2bea22bb9638`.
- `scripts/release_content.py` SHA-256:
  `b182add4d0cfc65560c949baad249d4e84ff065433fd09bebb2af6c97fc9599e`.
- The canonical and embedded helpers both reported **`environment_errors: []`**
  and no `cleanup_pending`. Overall status and CLI exit were checked separately
  from workflow failure counts.
- Ordinary workflows use `compile --strict`. The policy fixtures use
  `compile <workflow>` **without `--strict`**, but must still emit strict metadata.
- Helper repository context was the explicitly recorded `book-default`:
  `https://github.com/webmaxru/github-agentic-workflows-book.git`.
  Configuring a scratch origin did not fetch or execute a remote workflow.
- Scratch repositories and verification-process `TEMP`/`TMP`/`TMPDIR` were
  project-local and ignored. No real `.github/workflows` probe was added.

## Per-source results

**Every row: gh-aw v0.88.7; nonempty lock emitted; metadata strict true;
compiler exit 0; runtime NOT RUN.** “Policy” means no CLI strict override.

| Source under `examples/` | Mode | Compile | Warning |
|---|---|---|---|
| `ch02/repo-assistant-triage.md` | CLI strict | PASS | None |
| `ch04/repo-assistant-cooldown.md` | CLI strict | PASS | None |
| `ch04/repo-assistant-issue-shorthand.md` | CLI strict | PASS | None |
| `ch04/repo-assistant-triggers.md` | CLI strict | PASS | None |
| `ch05/repo-assistant-claude.md` | CLI strict | PASS | Restricted secret |
| `ch06/repo-assistant-open-pr.md` | CLI strict | PASS | None |
| `ch07/no-network.md` | CLI strict | PASS | None |
| `ch07/repo-assistant-hardened.md` | CLI strict | PASS | None |
| `ch07/strict-policy/opt-out.md` | Policy | PASS | None |
| `ch08/mcp-shape.md` | CLI strict | PASS | None |
| `ch08/playwright-cli.md` | CLI strict | PASS | None |
| `ch08/repo-assistant-tools.md` | CLI strict | PASS | None |
| `ch09/continuous-docs.md` | CLI strict | PASS | None |
| `ch09/continuous-triage.md` | CLI strict | PASS | None |
| `ch10/continuous-review.md` | CLI strict | PASS | None |
| `ch10/daily-test-improver.md` | CLI strict | PASS | None |
| `ch10/workflow-run-conclusion.md` | CLI strict | PASS | None |
| `ch11/repo-assistant-shared.md` | CLI strict | PASS | None |
| `ch11/repo-memory-validation.md` | CLI strict | PASS | Memory-validator review |
| `ch12/repo-assistant-observable.md` | CLI strict | PASS | Restricted secrets |
| `ch13/models-policy.md` | CLI strict | PASS | None |
| `ch13/repo-assistant-budgeted.md` | CLI strict | PASS | None |
| `ch13/strict-policy/opt-out.md` | Policy | PASS | None |
| `ch14/fleet-triage.md` | CLI strict | PASS | None |

Both shared fragments, `ch11/shared/triage-policy.md` and
`ch14/shared/triage-policy.md`, passed through their respective importers. They
are dependency inputs, not skipped standalone lock targets.

## Policy positives and the separate no-policy control

Both canonical policy rows record:

- `compilation_mode: repository-policy`;
- the original adjacent `aw.json` path and
  `staged_path: .github/workflows/aw.json`;
- JSON `strict: true`, with LF-normalized SHA-256
  `ac435ce17af7e52534d887ad321a7dd2ad128e449e95427aac8c4fa5e35fc4bd`;
- a nonempty emitted lock with exact target version and literal `strict: true`.

The Chapter 13 embedded policy copy was also compiled **without CLI `--strict`**,
using the JSON excerpt above it as the adjacent policy. It passed the same gate.

The Chapter 7 and Chapter 13 `opt-out.md` files have identical source bytes. One
separate control case reused those bytes but omitted **both `aw.json` and
`--strict`**. It exited **0**, emitted a nonempty v0.88.7 lock, and generated
**`GH_AW_COMPILED_STRICT: "false"`**. Thus the policy-positive result was not
merely a forced-CLI-strict result.

The control's raw metadata omits `strict`; it does not contain literal `false`.
The pinned `pkg/workflow/lock_schema.go:42` defines
`Strict bool` with `json:"strict,omitempty"`, and the generated lifecycle flag
independently confirms the effective false value. This interpretation is
**control-only**: missing/false metadata still fails every positive strict gate.
The control is not a shippable example and does not waive compilation failure.

The initial control validator incorrectly expected a literal false JSON field.
Its failed assertion is retained in `policy-control-attempt-1.json`; its compiler
had succeeded. The confirmed control was rerun with the documented encoding and
explicit generated effective-strict evidence, and passed. No core helper or
source change was needed.

## Non-Markdown staging and fingerprint binding

All **30** input paths are recorded in `verification.json.inputs`:
26 Markdown files, 2 JSON files, 1 YAML file, and 1 TXT file. Independent discovery
matched that inventory with no omissions or duplicate workflow targets.

| Non-Markdown input | Evidence |
|---|---|
| `examples/ch07/strict-policy/aw.json` | Adjacent policy staged; no-CLI-strict positive PASS |
| `examples/ch13/strict-policy/aw.json` | Adjacent policy staged; no-CLI-strict positive PASS |
| `examples/ch13/apm-policy.excerpt.yml` | Staged byte-for-byte in the ordinary Chapter 13 context; manuscript excerpt matches |
| `examples/ch13/verification-notes.txt` | Staged byte-for-byte in the ordinary Chapter 13 context; included in input fingerprints |

An independent physical staging check confirmed all four locations and bytes.
In a separate private clone, a reversible text change to **each** non-MD input
changed the shared review fingerprint; restoring the bytes restored the original
fingerprint. LF/CRLF normalization intentionally preserved the fingerprint.
No authored or canonical snapshot input was mutated for these tests.

## Complete embedded workflow results

**All rows: MATCH to source, compile PASS, v0.88.7, nonempty lock, strict true,
exit zero, runtime NOT RUN.**

| Chapter HTML and lines | Corresponding source under `examples/` |
|---|---|
| `continuous-review-and-testing.html:108-144` | `ch10/continuous-review.md` |
| `continuous-review-and-testing.html:149-185` | `ch10/daily-test-improver.md` |
| `continuous-triage-and-docs.html:131-170` | `ch09/continuous-triage.md` |
| `continuous-triage-and-docs.html:175-216` | `ch09/continuous-docs.md` |
| `defense-in-depth.html:140-184` | `ch07/repo-assistant-hardened.md` |
| `fleets-and-adoption.html:128-161` | `ch14/fleet-triage.md` |
| `governance-and-finops.html:148-191` | `ch13/repo-assistant-budgeted.md` |
| `governance-and-finops.html:206-217` | `ch13/models-policy.md` |
| `governance-and-finops.html:224-232` | `ch13/strict-policy/opt-out.md` + adjacent JSON |
| `observability-and-debugging.html:159-192` | `ch12/repo-assistant-observable.md` |
| `reuse-and-memory.html:197-229` | `ch11/repo-assistant-shared.md` |
| `safe-outputs.html:113-151` | `ch06/repo-assistant-open-pr.md` |
| `triggers.html:149-195` | `ch04/repo-assistant-triggers.md` |
| `triggers.html:204-239` | `ch04/repo-assistant-cooldown.md` |
| `what-are-agentic-workflows.html:86-122` | `ch02/repo-assistant-triage.md` |
| `your-first-workflow.html:165-201` | `ch02/repo-assistant-triage.md` |

Comparison decoded HTML and normalized LF/outer whitespace only. The two entire
shared-fragment blocks also match their sources and were compiled through the
embedded importers. Original basenames/import paths were preserved; the repeated
ch02 copy was isolated in a separate fixture context.

## Excerpts, commands and limitations

- **38/38** current excerpt/context checks passed: source configuration, policy
  JSON, APM YAML, retained complete skill/APM/model contexts, six exact Ch03 lock
  ranges, and package schema syntax.
- The explicitly negative `sudo` excerpt matches the retained v0.88.7 rejection
  **`Unknown property: sudo`**. It is not part of the positive workflow corpus.
- The package excerpt was checked in a schema-only envelope with a name; omitted
  README, child manifests and payloads were not installed or resolved.
- **96/96** command-spelling/flag checks passed using captured help. The only new
  help-topic calls were `env get --help`, `gh help variable set`, and
  `add-wizard --help`. No operational env, variable, model, forecast, log, audit,
  install, update, wizard or workflow-run handler was executed.
- A missing dedicated retained `add-wizard` help entry caused an initial
  evidence-gap result, preserved in `cli-verification-attempt-1.json`. Capturing
  target help closed the gap; no actual CLI rejection or source defect occurred.

Compilation does not prove browser/MCP availability, validator execution,
package installation, policy deployment, engine access, telemetry delivery,
forecast accuracy or scheduler behavior. Previously recorded foundation/pilot
evidence remains historical; it was not rewritten to cover changed sources.

## Unwaived warnings

The canonical run emitted **three warnings**, all preserved verbatim:

1. Ch05: restricted secret `ANTHROPIC_API_KEY`.
2. Ch11 memory-validation fixture:
   `Memory validation script changes: repo-memory:default (added)`.
3. Ch12: restricted secrets `OTLP_ENDPOINT` and `OTLP_TOKEN`.

The embedded Ch12 copy retains its warning too. These are successful strict
compilations, **not security approvals**. No `--approve` or secret values were
supplied. Owners should review the intended credential/validator/data-flow use
before a separately authorized deployment.

## Integrity and handoff

`verification-inputs.json` records raw and LF-normalized hashes.
`verification-audit.json` confirms the **30 example inputs and 14 chapter files**
stayed unchanged during this verification. **No source or annotation edit was
made in this scope.** Parent-managed metadata is recorded separately; no global
review fingerprint/acceptance assertion or framework-pin advance was performed.

All **37 earlier evidence files** were hash-checked unchanged. Exact canonical
and embedded compilation inputs—**49 entries including dependencies**—are
retained in `verified-inputs-archive.json` for reproduction after scratch cleanup.
Only this verification's own scratch repositories were removed.

Primary results: `verification.json`, `embedded-verification.json`,
`embedded-inventory.json`, and this note. Supporting proof:
`policy-control-verification.json`, `staging-verification.json`,
`dependency-fingerprint-verification.json`, `excerpt-verification.json`,
`cli-verification.json`, `verification-inputs.json`, `verification-audit.json`,
and the exact-input archive. The two initial supplemental attempts remain
separately named and are explained above.

**No unresolved compiler or source-consistency blocker.** Parent/editorial review,
TOC/brief integration, final metadata decisions, and any publication remain
separate. No commit, push, global attestation or live operation occurred.
