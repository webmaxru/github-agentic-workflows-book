# Final whole-book technical verification — PASS

**Target: gh-aw v0.88.7.** This is the explicitly requested final technical run,
not editorial ACCEPT, deployment/secret approval, publication, or a global
review attestation. `content/VERSION` remains **1.1** and
`content/FRAMEWORK_VERSION` remains **v0.81.6** for the parent to advance later.

## Fresh results and exact compiler

| Gate | Result |
|---|---|
| Canonical corpus | **24/24 PASS**, overall PASS, CLI exit **0** |
| Complete embedded workflows | **16/16 PASS**, overall PASS, CLI exit **0** |
| Repository-policy positives | **2 canonical + 1 embedded PASS without CLI `--strict`** |
| Separate no-policy control | **PASS**: exit 0, emitted lock, effective strict **false** |
| New Ch10 max-stack complete contexts | **2/2 PASS**, exit 0, strict target locks |
| Shared fragments / non-MD inputs | **2 fragments / 4 non-MD files accounted for** |

Every **positive** compilation emitted a nonempty lock with exact
`compiler_version: v0.88.7` and literal `strict: true`. The control is deliberately
separate and cannot waive this requirement. Overall status, exit zero and
environment/cleanup results were checked independently of workflow failure counts.

Actual version output: **`gh aw version v0.88.7`**.
Canonical run: **2026-09-16 03:13:12.797–03:14:32.348 UTC**.
Embedded run: **03:13:13.116–03:14:06.271 UTC**.

```powershell
python scripts\verify_examples.py --root 'C:\Users\masalnik\scoop\buckets\copilot-worktrees\github-agentic-workflows-book\webmaxru-turbo-happiness\build\q-_d8_vcwo' --compiler 'C:\Users\masalnik\.copilot\session-state\e9e760c4-bdb3-46e7-b867-b7f4d7e28a28\files\tools\gh-aw\v0.88.7\gh-aw.exe' --version v0.88.7 --report content\research\updates\v0.88.7\verification.json
```

Compiler SHA-256:
`8d88047c1e162f16a01e1920124092c80a8bdf98c1635357067a0ac34c00d4c7`.
Verifier SHA-256:
`8006500fdffe068d0f9117f3130fa92b2a25d1daa6b24161673c2bea22bb9638`.
Shared input/fingerprint helper SHA-256:
`b182add4d0cfc65560c949baad249d4e84ff065433fd09bebb2af6c97fc9599e`.
The installer fix remains at
`93adeb252d8cc07d8d5541190568fb8e6bfceddfac5434ef991fb848553fb877`;
no installation was repeated.

## Per-example canonical results

All rows used **v0.88.7**, emitted a **nonempty lock**, recorded **strict true**
in metadata, and exited **0**. Runtime: **NOT RUN** for every row.

| Source under `examples/` | Compilation mode | Result | Warning |
|---|---|---|---|
| `ch02/repo-assistant-triage.md` | CLI strict | PASS | None |
| `ch04/repo-assistant-cooldown.md` | CLI strict | PASS | None |
| `ch04/repo-assistant-issue-shorthand.md` | CLI strict | PASS | None |
| `ch04/repo-assistant-triggers.md` | CLI strict | PASS | None |
| `ch05/repo-assistant-claude.md` | CLI strict | PASS | Restricted secret |
| `ch06/repo-assistant-open-pr.md` | CLI strict | PASS | None |
| `ch07/no-network.md` | CLI strict | PASS | None |
| `ch07/repo-assistant-hardened.md` | CLI strict | PASS | None |
| `ch07/strict-policy/opt-out.md` | Repository policy; no CLI override | PASS | None |
| `ch08/mcp-shape.md` | CLI strict | PASS | None |
| `ch08/playwright-cli.md` | CLI strict | PASS | None |
| `ch08/repo-assistant-tools.md` | CLI strict | PASS | None |
| `ch09/continuous-docs.md` | CLI strict | PASS | None |
| `ch09/continuous-triage.md` | CLI strict | PASS | None |
| `ch10/continuous-review.md` | CLI strict | PASS | None |
| `ch10/daily-test-improver.md` | CLI strict | PASS | None |
| `ch10/workflow-run-conclusion.md` | CLI strict | PASS | None |
| `ch11/repo-assistant-shared.md` | CLI strict | PASS | None |
| `ch11/repo-memory-validation.md` | CLI strict | PASS | New-validator review |
| `ch12/repo-assistant-observable.md` | CLI strict | PASS | Restricted secrets |
| `ch13/models-policy.md` | CLI strict | PASS | None |
| `ch13/repo-assistant-budgeted.md` | CLI strict | PASS | None |
| `ch13/strict-policy/opt-out.md` | Repository policy; no CLI override | PASS | None |
| `ch14/fleet-triage.md` | CLI strict | PASS | None |

Independent discovery matched the complete **30-input** set: 24 standalone
workflows, 2 shared Markdown fragments, and 4 non-Markdown inputs. The shared
triage policies passed through their Ch11/Ch14 source and embedded importers;
they are dependencies, not skipped standalone targets.

## Embedded workflows and dependencies

All **16 complete workflow blocks** match their sources after documented
HTML/LF/outer-whitespace normalization. Fresh source and embedded metadata agree
on frontmatter/body hashes, version and strictness. The two full shared-fragment
copies also match. Current post-annotation line locations and per-copy results
are in `verification-audit.json` and `embedded-inventory.json`.

The complete copies cover Ch01/02 triage; both Ch04 workflows; Ch06 draft PR;
Ch07 hardened triage; both Ch09 workflows; both Ch10 workflows; Ch11 reuse;
Ch12 observability; all three Ch13 workflows; and Ch14 fleet triage.
The embedded Ch13 policy diagnostic retained adjacent `aw.json` and compiled
without CLI `--strict`, rather than having the policy masked by a forced flag.

The four non-MD inputs are:

- `examples/ch07/strict-policy/aw.json`
- `examples/ch13/strict-policy/aw.json`
- `examples/ch13/apm-policy.excerpt.yml`
- `examples/ch13/verification-notes.txt`

They remain in the helper's input inventory and LF-normalized fingerprints.
The earlier physical-staging and private-clone fingerprint-change checks were
reused only after confirming identical input bytes and identical helper hashes.
Those checks established byte-exact staging, a fingerprint change for each
non-MD input change, and intentional LF/CRLF normalization.

## Policy and max-stack controls

The two policy source rows identify their adjacent original JSON and
`staged_path: .github/workflows/aw.json`. Both JSON inputs have normalized SHA-256
`ac435ce17af7e52534d887ad321a7dd2ad128e449e95427aac8c4fa5e35fc4bd`.
Both produce literal strict-true metadata with **no CLI strict override**.

The Ch07/Ch13 `opt-out.md` source bytes are identical. The fresh, separately
recorded control omitted both `aw.json` and CLI `--strict`. It exited zero,
emitted a nonempty v0.88.7 lock, and recorded
`GH_AW_COMPILED_STRICT: "false"`. The optional raw metadata `strict` field is
omitted: the target defines `Strict bool` with `json:"strict,omitempty"`.
That documented false encoding is accepted **only for this expected non-strict
control**. No positive gate accepts missing/false strict metadata.

`max-stack-verification.json` adds the requested Ch10 complete context:
the original COMMENT-only review workflow and a private copy with only
`on.pull_request.max-stack: -1` added. Both compiled strictly with target locks.
The body hash and required-role declaration are unchanged; the generated
stack-position conditions appear in the default lock and not in the `-1` lock.
This is compiler-output evidence, **not live PR-stack admission or a spending
measurement**. No authored YAML or task prompt was changed.

## Reused evidence and unverified boundaries

All 30 example input bytes and all 14 pre-tag chapter texts matched the prior
whole-corpus snapshot exactly. Consequently, `reused-evidence.json` binds reuse
of **96 captured-help checks**, **38 excerpt/context checks**, the **six exact
Ch03 generated-lock ranges**, and the Ch04 fresh/ordinary/refresh/same-seed
schedule checks. No unchanged 22-probe help batch or release archaeology was
rerun.

APM remains independently scoped to **0.28.0**. Its policy excerpt is not gh-aw
frontmatter; the bridge/native-skill excerpts rely on their actual retained
complete fixtures, dependencies and tagged references. Omitted package payloads,
the native skill, and the APM bridge were not installed or presented as complete
vendored book recipes. The MCP endpoint remains an explicitly non-runnable
illustration; Playwright compilation is not a browser test.

Runtime, optional `--validate`/scanners, Docker capability, credentials, model
availability, validator execution, persistence, telemetry delivery, installations,
forecast measurements and operational interfaces remain **NOT RUN / NOT
VERIFIED**. No permissions were widened and no `--approve` was used.

## Warnings remain part of PASS

Exact stdout/stderr is retained per example. The final canonical run emitted
three warnings:

1. Ch05: restricted secret **`ANTHROPIC_API_KEY`**.
2. Ch11: **`Memory validation script changes: repo-memory:default (added)`**.
3. Ch12: restricted secrets **`OTLP_ENDPOINT`**, **`OTLP_TOKEN`**.

The embedded Ch12 copy also retains its warning. These are successful strict
compilations, not approvals of credentials, validator code or data exposure.
Human deployment/security review remains required.

## Authorized verification annotation audit

After PASS, **11 exact verification-status/provenance replacements across
8 chapters** were applied. They replace pending/verifier handoffs and stale
gate descriptions with factual results and current evidence paths. In
particular, Ch13 no longer claims the runner forces CLI `--strict` for policy
fixtures. The book no longer says fresh corpus verification or the final
`verification.json` result is merely pending/planned.

These changes are **not conceptual prose, command, YAML or task-prompt edits**.
Byte-level reconstruction matched only the planned replacements. All 30
compilation input bytes, 16 embedded workflow hashes, shared/policy inputs,
all pre/code blocks and all six slots per chapter remain unchanged.

`verification-audit.json` records every exact before/after annotation and every
chapter's pre/post SHA-256. Eight chapter hashes intentionally changed; this is
not an “all inputs unchanged” claim. The post-tag technical snapshot fingerprint
is `84244a31f0a03b71f6a6b4e07247ab6f0ca0730cc2ce89da88a3c0bd5369f83e`;
it is **not a review attestation**.

## Evidence preservation and handoff

The earlier whole-corpus result set was copied byte-for-byte to
`history/whole-corpus-2026-09-16T021743Z/`; `archive-index.json` records all
14 original hashes. Existing preflight, pilot, foundation and research evidence
was preserved. The final input manifest binds **52 prior evidence files**.

Fresh primary reports are `verification.json`, `verification-notes.md`,
`embedded-verification.json`, `embedded-inventory.json`,
`policy-control-verification.json`, `max-stack-verification.json`,
`verification-inputs.json`, `verification-audit.json`, and `reused-evidence.json`.
`verified-inputs-archive.json` preserves the **51 exact input entries** needed
to reproduce canonical, embedded/dependency and Ch10-context compilations after
the owned temporary repositories are removed.

**No unresolved compiler or technical source-consistency blocker.**
No source fix was needed; only the authorized verification annotations changed.
No frame/edition advance, global attestation, commit, push, publication or live
operation was performed. The parent owns the framework-baseline decision and
the remaining editorial/global review and edition build.
