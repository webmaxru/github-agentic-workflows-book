# Consolidated post-editorial technical refresh — PASS

**One refresh only:** the current 24 canonical workflows and 16 complete embedded
workflows were recompiled against the adopted **v0.88.7** framework pin.
Both helper runs returned **overall PASS and CLI exit 0**, with nonempty locks
and exact `compiler_version: v0.88.7` / literal `strict: true` metadata.

This is current technical proof, **not editorial acceptance, deployment
approval or a review attestation**. Runtime and optional scanners remain
**NOT RUN**. No permissions, frame pin, content edition, or global settings were
changed by this verifier.

## Current compiler and invocation

The actual `content/FRAMEWORK_VERSION` is **v0.88.7**, matching the selected
binary's reported **`gh aw version v0.88.7`**. `content/VERSION` remains **1.1**.
Canonical run: **2026-09-16 04:07:31.944–04:09:03.103 UTC**.

```powershell
python scripts\verify_examples.py --root 'C:\Users\masalnik\scoop\buckets\copilot-worktrees\github-agentic-workflows-book\webmaxru-turbo-happiness\build\r-wfus9ybk' --compiler 'C:\Users\masalnik\.copilot\session-state\e9e760c4-bdb3-46e7-b867-b7f4d7e28a28\files\tools\gh-aw\v0.88.7\gh-aw.exe' --version v0.88.7 --report content\research\updates\v0.88.7\verification.json
```

Compiler SHA-256:
`8d88047c1e162f16a01e1920124092c80a8bdf98c1635357067a0ac34c00d4c7`.
Verifier:
`8006500fdffe068d0f9117f3130fa92b2a25d1daa6b24161673c2bea22bb9638`.
Shared input/fingerprint helper:
`b182add4d0cfc65560c949baad249d4e84ff065433fd09bebb2af6c97fc9599e`.
All remained unchanged during the run.

## Canonical results

**Every row: PASS, compiler v0.88.7, exit 0, nonempty lock, metadata strict true;
runtime NOT RUN.** Policy mode omits CLI `--strict` and stages adjacent `aw.json`.

| Source under `examples/` | Mode | Result | Warning |
|---|---|---|---|
| `ch02/repo-assistant-triage.md` | CLI strict | PASS | None |
| `ch04/repo-assistant-cooldown.md` | CLI strict | PASS | None |
| `ch04/repo-assistant-issue-shorthand.md` | CLI strict | PASS | None |
| `ch04/repo-assistant-triggers.md` | CLI strict | PASS | None |
| `ch05/repo-assistant-claude.md` | CLI strict | PASS | Restricted secret |
| `ch06/repo-assistant-open-pr.md` | CLI strict | PASS | None |
| `ch07/no-network.md` | CLI strict | PASS | None |
| `ch07/repo-assistant-hardened.md` | CLI strict | PASS | None |
| `ch07/strict-policy/opt-out.md` | Repository policy | PASS | None |
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
| `ch13/strict-policy/opt-out.md` | Repository policy | PASS | None |
| `ch14/fleet-triage.md` | CLI strict | PASS | None |

The full input inventory is **30 files**: 24 standalone Markdown workflows,
2 shared Markdown fragments, and 4 non-MD inputs. The shared fragments passed
through source and embedded importers. All four JSON/YAML/TXT inputs remain
bound in the helper inventory and normalized fingerprints.

## Specific review-fix proof

| Revised input | Fresh result | Preserved contract |
|---|---|---|
| Ch08 `repo-assistant-tools.md` | PASS; new footer compiled | Entire YAML, task prefix, read-only permissions and maximum one comment unchanged |
| Ch09 `continuous-triage.md` | PASS; revised source and complete embed match | Entire YAML, permissions, maximum one comment and maximum three labels unchanged |

**Ch08:** only the explanatory footer differs from the pre-editorial source.
The intended triage comment is a mediated repository-write request; GitHub reads
and web fetches have separate tool/network boundaries. The fresh lock records:

- frontmatter hash:
  `cbb0a71d9c13a2fbc21fc21120525e8b1e75e581a5de4aec46cbdcbd7e1c337b`
- new body hash:
  `4e5350277e5676809a12396f9426918620b5a2d1086533edc3bc6d478ec29c9f`
- exact source-byte SHA-256:
  `a89a91ea296afb5b5d273905693596d778830b4dcd1bff708409fc907e894a23`

Ch08 has a configuration excerpt, not a complete embedded copy of this source.
That excerpt remains unchanged and matches the freshly compiled configuration.

**Ch09:** the source and complete embedded workflow contain the at-most-one
clearly eligible issue per sweep instruction, completion of its comment/labels,
deferral of other issues, skipping ambiguity and no action when none qualifies.
The new source/embedded lock body hash is
`ca4bab5c43af79d42ab27c927a64781d7e488f72a836e718e95616eee3bcc3fb`,
matching the focused triage-revision proof. The unchanged frontmatter hash is
`79257831ec311bf101a9a0bc0f5f341442302ea537026c801323cf0957a2c74b`.
Exact source-byte SHA-256:
`a05e69080e9b28135c5832074c68650ecc6b6d69f91a18dd7ad9aaa69cd1898c`.

No agent behavior was exercised; these are fresh compilation and source-
consistency results, not measurements of instruction following.

## Embedded and policy gates

All **16 complete embedded workflows** passed and match their current sources.
Their fresh frontmatter/body hashes agree with canonical metadata. Both full
shared-fragment copies and the embedded policy JSON remain equivalent to source.
Per-copy mappings, final line locations and input hashes are in
`embedded-inventory.json` and `verification-audit.json`.

Both canonical policy fixtures and the policy-dependent Ch13 embed compiled
**without a CLI strict override**, retaining adjacent
`.github/workflows/aw.json`. All emitted literal strict-true metadata.
The existing separate no-policy control is reused only after matching the exact
policy MD/JSON inputs and compiler. Its effective strict mode was false
(`GH_AW_COMPILED_STRICT: "false"`); the optional false metadata field is omitted
by the target encoding. No positive gate accepts missing/false strict metadata.

The canonical and embedded reports both retain **`environment_errors: []`** and
no `cleanup_pending`. Context is the recorded sanitized `book-default` origin:
`https://github.com/webmaxru/github-agentic-workflows-book.git`.
This reference context is not deployment certification.

## Reuse without probe reruns

`reused-evidence.json` binds unchanged policy control, Ch10 max-stack context,
non-MD staging/fingerprint and supplied reference/context evidence. The 38
configuration/reference excerpts were matched to their unchanged configurations
or retained contexts; no compiler-probe or research pass was repeated.

Of the prior 96 command entries, 95 are unchanged. The sole replacement is
Ch07's bare-ID audit recipe adding explicit `--repo owner/repo`, already supported
by the captured v0.88.7 audit help. No help or operational probes were rerun.
Ch14's citation/status edits do not change compilation inputs.

MCP remains an explicitly non-runnable endpoint illustration. Playwright
compilation does not establish browser availability. APM 0.28 policy/bridge and
native-skill material retain their actual supplied probe/reference scope:
no installations, provider access, full dependency-graph replay or live
enforcement is claimed.

## Unwaived warnings

Exact per-example stdout/stderr remains in the reports. Canonical warnings are:
`ANTHROPIC_API_KEY` for Ch05; added `repo-memory:default` validation script for
Ch11; and `OTLP_ENDPOINT` / `OTLP_TOKEN` for Ch12. The Ch12 embedded warning is
also retained. No `--approve`, secret validation, permission widening or
deployment/security approval occurred.

## Annotation, input and history audit

After PASS, only **two stale Ch08 verification-provenance annotations** were
replaced. They now point to the consolidated result and explicitly distinguish
the archived pre-editorial reports. Their exact before/after strings are in
`verification-audit.json`.

A byte-level audit allowed only those two replacements. All 30 compilation
input hashes, all 16 embedded hashes, all pre/code blocks and all six slots per
chapter remain unchanged by tagging. No concepts, commands, YAML, task prompts
or other chapter prose were edited.

- Current Ch08 chapter SHA-256:
  `95cdf6d91e8f65640c86820e179b385016b2b9085017eb99541ab3c6c8c5a9bf`
- Current Ch09 chapter SHA-256:
  `48aeeac596b341f76dd2fc565da7a8e467a09d27d869e43416353db82ab662ee`
- Current post-tag snapshot fingerprint:
  `2def13bdcd4ae16868df77fa6a14f361018accca6b2974948fb466be607f10e9`

The old global reports/receipt are preserved byte-for-byte in
`history/pre-editorial-revision-2026-09-16T031312Z/`; its archive index records
the nine original hashes. All 70 pre-existing evidence files were preserved.
The new receipt binds this current source snapshot, not the pre-revision bodies.

**No unresolved compiler or technical source-consistency blocker.** Owned scratch
fixtures were removed after preserving the 49 exact canonical/embedded input
entries. No runtime, scanner, approval, attestation, edition change, commit,
push or operational command occurred.
