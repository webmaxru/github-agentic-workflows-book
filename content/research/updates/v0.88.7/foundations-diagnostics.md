# Foundations snapshot verification — PASS

**Scope:** frozen Ch01–Ch05 HTML and the five named source workflows only.
Other authors' paths were intentionally excluded. This is foundation-batch
technical proof, **not whole-book acceptance or final-edition verification**.

## Required gates

| Gate | Result |
|---|---|
| Canonical sources | **5/5 PASS**, overall PASS, CLI exit **0** |
| Complete embedded workflows | **4/4 PASS**, overall PASS, CLI exit **0** |
| Configuration excerpts matched to complete contexts | **12/12 PASS** |
| Ch03 excerpts matched to exact retained lock ranges | **6/6 PASS** |
| Retained/derived positive model, Pi, default and turn-limit contexts | **9/9 PASS**, overall PASS, CLI exit **0** |
| Ch04 fresh / ordinary / refresh / independent-fresh phases | **4/4 PASS**, every CLI exit **0** |
| Command/help checks | **PASS**; no operational init/new/add/run/list/status/install execution |
| Final reference audit | **14/14 PASS**; resolved supplemental harness issue retained below |

All newly compiled locks were nonempty and their metadata independently confirmed
**`compiler_version: "v0.88.7"`** and literal **`strict: true`**.
Overall PASS and CLI exit zero were required independently of failure counts.
All final compilation reports have **`environment_errors: []`** and no
`cleanup_pending`. **Runtime, optional validation/scanners, scheduler execution,
credentials and model availability: NOT RUN / NOT VERIFIED.**

## Canonical source results

| Example under `examples/` | Compile | `gh aw` | Lock / strict | Warning |
|---|---|---|---|---|
| `ch02/repo-assistant-triage.md` | PASS | v0.88.7 | Yes / true | None |
| `ch04/repo-assistant-triggers.md` | PASS | v0.88.7 | Yes / true | None |
| `ch04/repo-assistant-cooldown.md` | PASS | v0.88.7 | Yes / true | None |
| `ch04/repo-assistant-issue-shorthand.md` | PASS | v0.88.7 | Yes / true | None |
| `ch05/repo-assistant-claude.md` | PASS | v0.88.7 | Yes / true | Restricted-secret review |

The ch02 source matches the prior immutable input. Ch04 triggers and ch05 Claude
retain their prior frontmatter hashes. Claude's exact YAML, pins and task prefix
(lines 1–32) are unchanged; only its explanatory footer differs.

Canonical run: **2026-09-16 01:04:10.019–01:04:26.052 UTC**.
Actual version output: **`gh aw version v0.88.7`**.

```powershell
python scripts\verify_examples.py --root 'C:\Users\masalnik\scoop\buckets\copilot-worktrees\github-agentic-workflows-book\webmaxru-turbo-happiness\build\f-26nilw1o' --compiler 'C:\Users\masalnik\.copilot\session-state\e9e760c4-bdb3-46e7-b867-b7f4d7e28a28\files\tools\gh-aw\v0.88.7\gh-aw.exe' --version v0.88.7 --report content\research\updates\v0.88.7\foundations-verification.json
```

The short snapshot contained only the selected five examples under `examples/`,
plus copies of the five selected chapters. Supplemental contexts were outside
that canonical `examples/` tree and did not inflate its count.
The hardened verifier hash remained
`783491d5c44e14dba37a0ffbabd91174ea02faadc370d7a386ab094c9d057273`;
compiler hash remained
`8d88047c1e162f16a01e1920124092c80a8bdf98c1635357067a0ac34c00d4c7`.

## Embedded/source and excerpt consistency

All complete blocks match their sources after HTML decoding, LF normalization
and outer-whitespace normalization only. No prompt/configuration text was fixed.

| Complete block in `content/chapters/` | Source | Compile / lock metadata |
|---|---|---|
| `what-are-agentic-workflows.html:86-122` | ch02 triage | PASS / v0.88.7 / strict true |
| `your-first-workflow.html:165-201` | ch02 triage | PASS / v0.88.7 / strict true |
| `triggers.html:149-195` | ch04 triggers | PASS / v0.88.7 / strict true |
| `triggers.html:204-239` | ch04 cooldown | PASS / v0.88.7 / strict true |

Ch01 now reproduces the full ch02 source; the historical abridged-copy difference
is not carried into this snapshot. Ch04's four configuration excerpts match the
three corresponding complete source workflows, including the separate
issue-shorthand source. Ch02, Ch03 and Ch05 configuration excerpts likewise match
their source or retained positive-probe context. Excerpts were not mislabeled as
standalone workflows.

Ch03's six generated excerpts match the retained
`compat-v0.88.7-neutral/examples/ch02/repo-assistant-triage.lock.yml` exactly,
including indentation, at lines **1; 37–38; 300; 862–865; 1546–1555; 1722–1731**.
That lock's metadata is v0.88.7 / strict true. No generated excerpt was invented,
rewritten, or presented as a complete workflow.

The historical ch02 preflight summary and ch05 strict+validate stderr excerpt
also match their retained records. Ch03's APM caveat is backed by the retained
compile-only capture: `microsoft/apm-action@v1.10.0`, APM `0.28.0`, strict target
metadata, and `dynamic_resolution_failed` in the manifest. That integration was
not recompiled or installed in this batch.

## Ch04 compile-time behavior

Both scheduled sources used the explicit seed
`webmaxru/github-agentic-workflows-book` and identical repository-relative
workflow identities across phases. These are observed compile outputs, not
promises of dispatch time or collision-free schedules.

| Source | Fresh stop time (UTC) | Ordinary recompile | Explicit refresh (UTC) | Cron in all four phases |
|---|---|---|---|---|
| triggers | `2026-10-16 01:14:54` | Preserved exactly | `2026-10-16 01:15:03` | `20 3 * * *` |
| cooldown | `2026-10-16 01:14:55` | Preserved exactly | `2026-10-16 01:15:03` | `14 */1 * * *` |

A separate fresh repository resolved new deadlines at `01:15:07` and `01:15:09`
on 16 October, while retaining those cron strings. Fresh deadlines fell within
the measured compile windows plus 30 days. Source/frontmatter/body hashes stayed
unchanged across the phases.

Generated cooldown plumbing includes `pre_activation` permission `actions: read`,
`GH_AW_COOLDOWN_SECONDS: "14400"`, `check_cooldown`, and its activation condition.
The shorthand generated `issues.types: [opened]` **and** `workflow_dispatch`.
No scheduler, history lookup, fail-open path, cooldown admission or live dispatch
was exercised.

## Models, Pi, turn limits and warning preservation

Four exact retained positive fixtures were recompiled: `defaults.md`,
`model-top-level.md`, `model-precedence.md`, and `pi-engine.md`. Five additional
diagnostic contexts set top-level `max-turns: 7`, one for each built-in engine.
All nine passed and emitted strict target locks.

- Top-level model: compiled `agent_model` **`auto`**.
- Per-engine precedence: compiled **`claude-sonnet-4.6`**, not the top-level `auto`.
- Compiled CLI defaults matched the target constants: Copilot **1.0.80**,
  Claude **2.1.247**, Codex **0.150.1**, Gemini **0.55.1**, Pi **0.84.3**.
- The tagged engine reference confirms the cross-engine proxy invocation cap,
  fallback **500**, Claude-only deprecated nested alias, and main-agent AIC
  fallback **1000**. Configuration compilation does not test runtime enforcement.
- Retained generated output confirms Copilot's `auto` fallback after runtime
  model variables. The Pi reference and actual warning confirm separate Copilot
  authentication for default detection.

Canonical Claude retains **one** warning naming `ANTHROPIC_API_KEY`.
The context report additionally preserves Anthropic, Codex/OpenAI and Gemini
restricted-secret warnings, plus the Pi authentication warning:

```text
.github\workflows\pi-engine.md: warning: Threat detection for engine: pi runs on the GitHub Copilot CLI. This workflow does not grant permissions.copilot-requests: write, so detection requires a COPILOT_GITHUB_TOKEN secret. Without that secret, threat detection will fail with "No authentication information found".
```

Exact stdout/stderr is retained per example. **No `--approve`, engine secret,
credential validation or runtime success claim.** Deployment/security review is
still required; warnings were not converted into waivers.

## Snapshot, tagging and resolved tooling note

`foundations-inputs.json` records the **10 frozen input hashes**.
`foundations-snapshot-audit.json` records their in-scope live pre/post hashes.
All five source MD byte hashes and all four embedded compilation-input hashes
remain unchanged. Every in-scope pre/code block and all six slots per chapter
remain unchanged by verification tagging.

The only manuscript edit was Ch04's existing author-handoff **HTML comment**:
it now records the three-source/two-embed PASS, strict target metadata, new
foundation evidence paths and scratch-only behavior PASS, explicitly excluding
whole-book/final-edition acceptance and runtime execution. Its exact before/after
text is in the snapshot audit. No visible prose, commands, YAML or prompt changed.

- Ch04 snapshot HTML SHA-256:
  `6d7aa97fe5c1c1078de27da429b7eab3acc1eef10ff89a0a4e0d6daefcda4753`.
- Ch04 post-tag HTML SHA-256:
  `64e57438658ac09aa6fdf55f133e0a70007904538b7adc0c8074d92216204292`.

**Resolved supplemental harness issue:** the first reference audit falsely
failed the Claude-prefix check by searching the old file for the replacement
footer marker. `foundations-reference-attempt-1.json` preserves that result.
The corrected exact comparison of lines 1–32 passed; the actual diff is only
footer lines 33–36. `foundations-reference-verification.json` contains the
correction and all **14 PASS** checks. This was not a compiler/core-verifier
failure, and no source correction or compile waiver was applied.

The three helper runs used recorded `book-default` context with sanitized origin
`https://github.com/webmaxru/github-agentic-workflows-book.git`; behavior checks
used that explicit scratch origin and explicit schedule seed. Verification-process
temporary paths stayed under ignored `build/`; owned fixtures were removed.
The **17 earlier completed preflight/pilot reports** were hash-checked unchanged.
No out-of-scope unchanged-input claim is made.

## Evidence and reviewer handoff

Primary reports: `foundations-verification.json`,
`foundations-embedded-verification.json`, and this diagnostic.
Supporting reports: `foundations-inputs.json`, `foundations-inventory.json`,
`foundations-context-verification.json`, `foundations-context-inventory.json`,
`foundations-behavior-verification.json`, `foundations-cli-verification.json`,
`foundations-reference-verification.json`, the retained first reference attempt,
and `foundations-snapshot-audit.json`. `foundations-compiled-inputs.json` preserves
the exact 5 canonical, 4 embedded and 9 diagnostic input texts and byte hashes,
so removal of scratch repositories does not discard reproduction inputs.

**No unresolved author or compiler blocker.** Hand the scoped snapshot proof to
the foundation reviewer. Final full-corpus verification remains for after all
authors finish. No global metadata advance, global review attestation, commit,
push, publication or live operation was performed.
