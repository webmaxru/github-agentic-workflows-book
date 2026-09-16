# Chapter 12 revision verification — PASS

**Narrow scope:** revised Chapter 12 source and its matching embedded copy only.
No whole-corpus/chapter inventory or CLI recipe execution was repeated.
This is technical verification, not editorial ACCEPT, whole-book acceptance,
final-edition evidence, or deployment/secret approval.

## Actual compilation

Run: **2026-09-16 00:13:54.925–00:14:02.431 UTC**.
Actual version: **`gh aw version v0.88.7`**.
Overall report **PASS**, CLI exit **0**, **2 passed / 0 failed**.

| Actual input | Result | `gh aw` | Nonempty lock | Lock strict | Runtime |
|---|---|---|---|---|---|
| `examples/ch12/repo-assistant-observable.md` | PASS | v0.88.7 | Yes | true | NOT RUN |
| `content/chapters/observability-and-debugging.html:159-192` | PASS | v0.88.7 | Yes | true | NOT RUN |

The machine report's fixture IDs are respectively
`examples/source/repo-assistant-observable.md` and
`examples/embedded/repo-assistant-observable.md`.
Each compiler exited zero; both lock headers name exactly `v0.88.7` and
literal `strict: true`. Their complete lock metadata agrees.

Both locks retain the prior pilot's frontmatter hash
`0f942b2daa673f2866c66f9c371d7593db2c11a9b73186924091f46035ed12c9`,
confirming unchanged YAML. Their new body hash is
`4447a9caa0eda4967f97321fd2191447666430b5997abb8b2f64f2eb7f457a67`,
different from the prior pilot and confirming the revised body was compiled.

Exact invocation, from the book worktree:

```powershell
python scripts\verify_examples.py --root 'C:\Users\masalnik\scoop\buckets\copilot-worktrees\github-agentic-workflows-book\webmaxru-turbo-happiness\build\pr-rmzsp1_n' --compiler 'C:\Users\masalnik\.copilot\session-state\e9e760c4-bdb3-46e7-b867-b7f4d7e28a28\files\tools\gh-aw\v0.88.7\gh-aw.exe' --version v0.88.7 --report content\research\updates\v0.88.7\pilot-revision-verification.json
```

The generated, ignored fixture held those two inputs and had its own Git
repository with no origin. The hardened verifier staged compilation under its
short `build/v` root. Report context:
`{"url":"https://github.com/webmaxru/github-agentic-workflows-book.git","source":"book-default"}`.
**`environment_errors: []`; no `cleanup_pending`.** Origin setup did not fetch
or execute a remote workflow. Temporary verification files were removed.

Compiler SHA-256:
`8d88047c1e162f16a01e1920124092c80a8bdf98c1635357067a0ac34c00d4c7`.
Verifier SHA-256:
`783491d5c44e14dba37a0ffbabd91174ea02faadc370d7a386ab094c9d057273`.
Both remained unchanged through this check.

## Warnings and CLI-proof reuse

**No compiler errors or technical blockers.** Each input emitted **one**
safe-update warning naming **two** restricted secrets:

```text
.github\workflows\repo-assistant-observable.md: warning: safe update mode detected unapproved changes

New restricted secret(s):
  - OTLP_ENDPOINT
  - OTLP_TOKEN
```

Full stderr, including `SECURITY REVIEW REQUIRED`, is preserved in
`pilot-revision-verification.json`. No `--approve` or secret values were
supplied; security review remains required before deployment.

The **8 command-bearing blocks** match the prior pilot's inspected blocks
exactly after HTML decoding. All **24 unique recipe texts** also match the
saved `pilot-cli-verification.json` inventory. Its help-only proof and raw
`pilot-cli-help.json` were reused, **not rerun**. No operational logs/audit,
pruning, runtime, optional validation, Docker/scanner, or telemetry checks occurred.

## Authorized status-only annotation changes

Only the following **four replacements** were made in
`content/chapters/observability-and-debugging.html`, **after PASS**.
All other chapter bytes—including the new main-agent/detector explanation—
remain identical to the author's revision.

**Line 8 — objective status:**

```diff
-The revised example awaits fresh strict compilation;
+The revised source and matching embedded workflow passed strict v0.88.7 compilation;
```

**Line 158 — complete-workflow caption:**

```diff
-complete workflow; fresh verification pending; runtime NOT RUN
+complete workflow; strict v0.88.7 compilation PASS; runtime NOT RUN
```

**Line 202 — temporary pending/provenance paragraph:**

```diff
-<p><strong>Revised example: verification pending.</strong> The YAML is unchanged, but the explanatory prompt has changed, so earlier preflight and pilot hashes do not verify this revision. Fresh strict compilation of the source and embedded copy is pending. Final-edition evidence is planned for <code>verification.json</code> and <code>verification-notes.md</code> under <code>content/research/updates/v0.88.7/</code>.</p>
+<p><strong>Revised example: strict compilation PASS.</strong> The revised standalone source and matching embedded copy each passed with exit code 0 and a nonempty lock whose metadata confirms <code>compiler_version: v0.88.7</code> and <code>strict: true</code>. Each compilation emitted one safe-update warning naming <code>OTLP_ENDPOINT</code> and <code>OTLP_TOKEN</code>; no approval was granted. Fresh evidence is recorded in <code>content/research/updates/v0.88.7/pilot-revision-verification.json</code>. This is Chapter 12 revision verification only, not whole-book acceptance or final-edition evidence; runtime remains <strong>NOT RUN</strong>.</p>
```

**Line 215 — recap status:**

```diff
-The earlier OTLP source passed strict v0.88.7 preflight with a restricted-secret review warning. The revised prompt awaits fresh verification; runtime remains <strong>NOT RUN</strong>.
+The revised OTLP source and matching embedded copy passed strict v0.88.7 compilation with a restricted-secret review warning; runtime remains <strong>NOT RUN</strong>.
```

Historical preflight provenance and warning excerpts were deliberately left
historical, not relabeled as fresh results.

## Post-tag input integrity and final chapter identity

A byte-level audit reproduced the final HTML with **only those four replacements**.
All pre/code blocks, the source Markdown, line endings, and all six section slots
were unchanged by tagging. There was no conceptual, command, YAML, or prompt edit.

| SHA-256 identity | Before status tags | After status tags |
|---|---|---|
| Source compilation input, exact file bytes | `70d7c20b2a47ce1797319ba6f659796ff59a047bac1dc4613bf8679d7eda8605` | Same |
| Embedded compilation input, HTML-decoded/LF/one trailing newline | `aa2ef29036be7b01e408cb72fd7349c14a6596fbde4a94630787528c824cc3a4` | Same |
| Chapter HTML, exact file bytes | `4abf6ff5bb94a7f78d7585cd5e27ad903b49ed27435fe31cd1e9d97de78d16fb` | `68453b41dbaeaeb8f2ea605d6f4a0b336edbf2314072384cea8ddbd390a0651d` |

The source normalized like the extracted block also hashes to `aa2ef290…`;
the source/embedded byte-hash difference is line-ending normalization.
**The chapter intentionally changed; only its compilation inputs stayed unchanged
through annotation editing.** This is not a claim that all inputs are unchanged
from the earlier pilot.

All **18 earlier research/evidence files** were hash-checked unchanged.
The new machine report was not edited after compilation; its SHA-256 is
`f9eec70704a5c980b1977f0965e069a77553f16020519d51d0ad10928232b31c`.
Framework baseline **v0.81.6** and content edition **1.1** were not advanced.
No review attestation, commit, push, publication, or live operation was performed.

**Handoff:** no technical blocker; return the final chapter hash and these
fresh Ch12-only results to the same reviewer for scoped editorial review.
