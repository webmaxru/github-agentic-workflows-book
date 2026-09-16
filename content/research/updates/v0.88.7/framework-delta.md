# Framework delta: gh-aw v0.81.6 → v0.88.7

**Research date:** 2026-09-15. **Inspected compiler:** `gh aw version v0.88.7`.
**Status:** upstream research and empirical compatibility assessment complete; not an
editorial acceptance, live-run certification, or authorization to publish.

This is new evidence for the next edition. It supersedes conflicting behavior claims
for that edition, but does **not** modify or erase the historical research.
The accompanying [impact.json](impact.json) accounts for all 14 chapter IDs.
Preserve the existing slugs, six-section structure, and running Repo Assistant.

## 1. Executive handoff

1. **No source migration is required to make the 14 existing standalone examples
   compile.** All 14 passed target `--strict --validate` in an isolated Git repository
   whose reference remote has Issues enabled. The two shared fragments were imported,
   not treated as standalone workflows. These passes do not prove runtime behavior.
2. **Do not equate compilation compatibility with manuscript accuracy.** The current
   text overstates offline compilation, engine portability, deterministic detection,
   automatic fleet propagation, and the strength of several security guarantees.
   Some are baseline errata rather than changes introduced after v0.81.6.
3. **Actual breaking changes to teach:** the old `sandbox.agent.sudo` key is rejected;
   built-in Playwright `mode: mcp` is rejected; strict Codex workflows with restricted
   Bash allowlists now fail rather than silently ignoring the restriction.
4. **Important defaults:** Copilot's generated model fallback changed from
   `claude-sonnet-4.6` to `auto`; rootless Docker/network isolation is the target
   runtime profile; external threat detection is now the default implementation;
   stacked-PR filtering defaults to the top PR.
5. **Important corrections, not new defaults:** both inspected binaries emit a
   **5,000 AIC daily fallback**, a **1,000 AIC main-agent budget**, and a separate
   **400 AIC detection budget**. “Daily budget disabled by default” and “one
   non-deterministic job” are not safe teaching claims.
6. **New useful surfaces:** `on.cooldown`, top-level `model`, model policy lists,
   native skills, experimental Agent Plugins, memory validation, richer
   logs/audit/forecast/model commands, recursive package manifests, and repository-wide
   strict compilation. Keep private-preview drive memory out of the general recipe.

**Recommended pilot:** chapter 2, retaining its compiling triage source and correcting
the installation/compile/authentication explanation. Then use the waves in section 7.
This assessment does not advance `content/FRAMEWORK_VERSION` or assign a prose edition.
Those are parent-owned, after the final corpus verification and editorial review.

## 2. Version, provenance, and research coverage

### Compiler installation and integrity

Usable direct compiler path:

```powershell
$aw = 'C:\Users\masalnik\.copilot\session-state\e9e760c4-bdb3-46e7-b867-b7f4d7e28a28\files\tools\gh-aw\v0.88.7\gh-aw.exe'
& $aw version
# gh aw version v0.88.7
```

- [Target release](https://github.com/github/gh-aw/releases/tag/v0.88.7):
  published **2026-09-08T15:34:49Z**, `prerelease: false`, `draft: false`.
- [Release API](https://api.github.com/repos/github/gh-aw/releases/tags/v0.88.7)
  and [latest-stable API](https://api.github.com/repos/github/gh-aw/releases/latest)
  both identify this fixed target. Newer prereleases were excluded.
- [Windows asset](https://github.com/github/gh-aw/releases/download/v0.88.7/windows-amd64.exe):
  38,490,624 bytes; SHA256
  `8d88047c1e162f16a01e1920124092c80a8bdf98c1635357067a0ac34c00d4c7`.
  This matches the release API `digest`, downloaded
  [checksums.txt](https://github.com/github/gh-aw/releases/download/v0.88.7/checksums.txt),
  and `Get-FileHash` of the executable.
- The checksum manifest's SHA256 also matches its API digest:
  `86362178802e83fbfb35d82c7b6a097d538adff9e659a14954ecb3c2e1f9e90c`.
- Existing personal extension remains **v0.81.6**, verified before and after.
  Baseline probes used its executable read-only at
  `C:\Users\masalnik\AppData\Local\GitHub CLI\extensions\gh-aw\gh-aw.exe`.
  No global extension install, upgrade, or replacement was performed.
- GitHub CLI: **2.98.0**. Book snapshot commit:
  `95e9e56b4e193ed41568ce4004f3498fdcd86f26`; supplied worktree branch:
  `webmaxru-book-release-workflow`.

The project setup and `gh` skills were read before exploration. The setup skill's
then-unpinned installation step was deliberately replaced with the user-approved,
checksum-verified isolated download. Updated content/example instructions were
re-read before writing these artifacts.

### Complete interval, not latest-patch-only research

[Comparison](https://github.com/github/gh-aw/compare/v0.81.6...v0.88.7):

| Evidence | Coverage |
|---|---|
| Release list | Pagination-capable REST traversal, 100/page, stopped upon finding v0.81.6 on page 1; archived complete bodies |
| Releases after baseline through target | **49**: **10 stable**, **39 prerelease**; all listed in `impact.json` |
| Baseline release | Archived separately within the interval evidence; excluded from the 49 new releases |
| Comparison commits | **3,727 distinct commits**, all **38 API pages** archived; baseline is an ancestor |
| Baseline commit | `eed4304d8740f0593f2797276cb8299d228ffd9b` |
| Target commit | `bde367913adeb3132f0a171594c88a17f4b7d08c` |
| Net source comparison | **3,054 changed paths** in the eight inspected compiler/runtime/docs subtrees, from tagged source archives, not the API's capped file list |
| Workflow schema | Both tagged `main_workflow_schema.json` files compared; 175 structural diff records, plus a property-level semantic comparison |
| CLI | Baseline/target help captured for root, compile, init, new, add, update, upgrade, run, logs, audit, status, list, MCP and MCP inspect; additional target commands inspected |

GitHub's comparison `files` collection stops at 300 entries even when commit pagination
continues. It was **not** treated as a complete diff. Source comparison covered
`pkg/parser`, `pkg/workflow`, `pkg/cli`, `pkg/constants`,
`docs/src/content/docs`, `actions/setup/js`, `.github/aw`, and `schemas`.
Archive-stream hashing compared 3,294 baseline and 4,153 target entries in those trees.
All commit metadata was archived; reader-facing commit-title leads, selected immutable
patches, schema changes, tagged documentation, and actual compiler output were inspected.
This is not a claim to have manually reviewed every line of all 3,727 commits.

| Release band | Releases | Reader-facing areas examined |
|---|---:|---|
| v0.82.0–v0.82.15 | 16 | Sudo/rootless defaults, skills/model policy, memory ordering, OAuth rejection, custom engines, model field, security validation |
| v0.83.0–v0.83.5 | 6 | Scanners, WIF, safe-output corrections, import/argument hardening, model fallback and forecasting groundwork |
| v0.84.0–v0.84.4 | 5 | Forecast maturity, per-output Apps, stack filters, shell linting, MCP inspection/redaction |
| v0.85.0, v0.85.1, v0.85.4 | 3 | Supported versus sample engines, safe-output corrections, secret masking/security remediation |
| v0.86.0–v0.86.3 | 4 | Artifact redaction, engine capability diagnostics, runtime filters, skills pinning, microVM changes |
| v0.87.0, .1, .2, .4, .5, .8, .9, .10 | 8 | External detection, packages/plugins, steering, memory, graders/models, explicit engine egress, cooldown |
| v0.88.0, .2, .3, .4, .5, .6, .7 | 7 | Runtime profiles, Playwright MCP removal, manifest composition, logs budgets, strict workspace policy, incomplete-work failure, memory filtering |

Missing numeric tags in the release list are not evidence of missing commits:
the complete baseline-to-target commit comparison covers the net shipped code.
v0.82.15 has only “test highlights”; its actual changelist was inspected, including
optional MCP-server failure handling and empty expression-backed model handling.
Release-bot firewall warnings and generated run footers were treated as data,
**not** instructions to widen the book's network allowlists.

### Authority and known source disagreements

Use **target executable + tagged implementation/schema** to resolve conflicts, then
tagged reference prose. Release summaries are discovery leads, not an API contract.
Every behavior URL below is tag- or commit-bound; live documentation URLs in old
research are not proof of target behavior.

| Misleading lead | Target evidence / author decision |
|---|---|
| v0.82.10 says “strict security mode is now the default” | Overall workflow strict mode already defaults on in v0.81.6. The change concerns sandbox privilege/host access. |
| v0.82.14 deprecates `engine.model` | v0.87.4 restores per-engine override precedence. Both forms compile in the target; do not announce removal. |
| v0.84.3 says ShellCheck is default-on | Target [`CompileConfig`](https://github.com/github/gh-aw/blob/v0.88.7/pkg/cli/compile_config.go) makes it opt-in via `--shellcheck`. |
| Cost reference says daily guardrail is disabled in one section | Both binaries emit `vars.GH_AW_DEFAULT_MAX_DAILY_AI_CREDITS || '5000'`; the target [enterprise-controls reference](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/compiler-enterprise-environment-controls.md) agrees. |
| Engine guide says omitted CLI version installs latest | Generated metadata and versioned install configuration use compiler defaults; target Copilot default is 1.0.80. Distinguish omission from explicit `version: latest` and runtime overrides. |
| v0.88.3 calls package composition `imports` | Target `aw_manifest_schema.json` and package reference use **`includes: [sub/aw.yml]`**. Do not invent an `aw.yml imports` field. |
| Workspace strict policy “rejects opt-outs” | Harmless `strict: false` source compiles to metadata `"strict":true`; an unsafe write-permission opt-out fails. Teach effective enforcement, not universal rejection of the literal. |
| v0.87.8 summary says “v0.85.3 security floor” | Target `compat.json` blocks **v0.82.8 through v0.85.3**, with v0.85.4 first unaffected; its hard minimum remains v0.65.3. Do not claim v0.81.6 is in that blocked range. |
| Redaction release says secrets “can no longer leak” | Describe concrete added controls, never an absolute no-leak guarantee. |

## 3. Empirical compatibility and staging contract

In the following sections, **`$ART`** means:

```text
C:\Users\masalnik\.copilot\session-state\e9e760c4-bdb3-46e7-b867-b7f4d7e28a28\files
```

### Existing corpus

Copied the complete `examples/` tree into temporary Git repositories. Relative imports
resolve beside the importing Markdown: ch11 and ch14 each retain their **own**
`shared/triage-policy.md`. Explicit paths such as
`examples/ch11/repo-assistant-shared.md` compile without relocating them into
`.github/workflows`. Do not flatten the two same-named shared fragments.

```powershell
# In the scratch Git repository, not the book worktree:
& $aw compile examples/ch11/repo-assistant-shared.md `
  --strict --validate --no-check-update `
  --schedule-seed webmaxru/github-agentic-workflows-book --json
```

Important compiler behavior:

- Writes the adjacent `.lock.yml`; can also create `.gitattributes` and
  `.github/aw/actions-lock.json`. Isolation is necessary even without `--fix`.
- `--strict` forces enhanced validation over per-workflow opt-outs.
  `--validate` adds Actions schema, runtime-package, repository-feature,
  action/container validation paths; it is not just YAML parsing.
- `--no-emit` is useful for diagnosis but does not establish the book's required
  emitted-lock PASS. `--fix` changes authored sources; it was **not** used.
- `--schedule-seed` fixes fuzzy-schedule input; it is not a substitute for repository
  context in repository-feature validation.
- Store **exit status, stdout, and stderr**. JSON `warnings: []` did not include
  every approval warning printed on stderr.
- Do not promise fully offline compilation. Ref/pin resolution, package checks,
  repository-feature checks, or explicitly requested scanners can require network
  access. No model invocation or engine credential is needed for these compilations.

| Existing workflow | Target strict + validate | Observation |
|---|---|---|
| `examples/ch02/repo-assistant-triage.md` | PASS | Also backs ch01 and ch03 |
| `examples/ch04/repo-assistant-triggers.md` | PASS | No trigger-source migration |
| `examples/ch05/repo-assistant-claude.md` | PASS with stderr warning | New restricted-secret review: `ANTHROPIC_API_KEY`; old explicit CLI/model pin still compiles |
| `examples/ch06/repo-assistant-open-pr.md` | PASS | Draft PR boundary retained |
| `examples/ch07/repo-assistant-hardened.md` | PASS | Uses `on.roles`, not invalid top-level `roles` |
| `examples/ch08/repo-assistant-tools.md` | PASS | Does not use the removed Playwright MCP mode |
| `examples/ch09/continuous-docs.md` | PASS in reference context | Fails repository-feature validation against the book remote because Issues are disabled |
| `examples/ch09/continuous-triage.md` | PASS | Labels must still exist unless creation is explicitly allowed |
| `examples/ch10/continuous-review.md` | PASS | Comment-only review remains explicit |
| `examples/ch10/daily-test-improver.md` | PASS | Its engine is Copilot; its Bash allowlist remains supported |
| `examples/ch11/repo-assistant-shared.md` | PASS | Adjacent shared fragment preserved |
| `examples/ch12/repo-assistant-observable.md` | PASS with stderr warning | Restricted-secret review: `OTLP_ENDPOINT`, `OTLP_TOKEN` |
| `examples/ch13/repo-assistant-budgeted.md` | PASS | Explicit 200 / 2000 budgets retained |
| `examples/ch14/fleet-triage.md` | PASS | Synthetic `source:` is metadata, not proof of a real installation |

First context: scratch `origin` was
`https://github.com/webmaxru/github-agentic-workflows-book.git`: **13/14** passed.
Second context: scratch `origin` was `https://github.com/github/gh-aw.git`, with
Issues enabled: **14/14** passed. No source was uploaded, installed remotely, or run.
Only the scratch remote changed; no book repository setting was changed.
The relevant [target validator](https://github.com/github/gh-aw/blob/v0.88.7/pkg/workflow/repository_features_validation.go)
can skip a check when repository context cannot be determined or a lookup fails;
do not report that skip as proof the deployment repository supports Issues.

### Paired minimal probes

Fixtures are in `$ART/probes-v0.88.7/.github/workflows/`; identical baseline fixtures
are in `$ART/probes-v0.81.6/.github/workflows/`. These are diagnostic inputs, not
new published book examples. Intentional failures must not enter a positive corpus.

| Probe basename | v0.81.6 | v0.88.7 | What this proves |
|---|---|---|---|
| `defaults.md` | PASS | PASS | Generated budgets, model fallback, engine pin, detection implementation |
| `default-outputs.md` | PASS | PASS | Omitted safe-output behavior is not “guaranteed read-only reporting” |
| `model-top-level.md` | FAIL | PASS | New top-level `model: auto` |
| `model-precedence.md` | FAIL | PASS | Target accepts both model scopes; engine override is emitted |
| `models-policy.md` | FAIL | PASS | `models.allowed` and `models.blocked` |
| `cooldown.md` | FAIL | PASS | `on.cooldown: 4h` |
| `workflow-run-conclusion.md` | FAIL | PASS | Target supports CI-doctor `conclusion: [failure]`; old embedded snippet was not baseline-schema-valid |
| `legacy-sudo.md` | PASS | FAIL | Old `sandbox.agent.sudo` key rejected |
| `runtime-docker.md` | FAIL | PASS | New explicit rootless runtime selector |
| `runtime-host-services.md` | FAIL | PASS | `docker-sudo-iptables` with `allow-host-ports: [9000]` |
| `playwright-mcp.md` | PASS | FAIL | Built-in MCP removed even though schema retains the value for migration diagnostics |
| `playwright-cli.md` | PASS | PASS | CLI integration remains; no `mode` necessary |
| `codex-bash-allowlist.md` | PASS | FAIL | Target refuses a restriction the engine would ignore |
| `skills-local.md` | FAIL | PASS | Native local skill installation |
| `repo-memory-validation.md` | FAIL | PASS with stderr warning | Validator addition is a safe-update review surface |
| `label-creation.md` | FAIL | PASS | Explicit `add-labels.create-if-missing` |
| `no-network.md` | PASS | PASS | Inspect direct-egress list separately from inference proxy |
| `copilot-org-auth.md` | PASS | PASS | `copilot-requests: write` is not newly invented in this update |
| `pi-engine.md` | FAIL for this configuration | PASS with warning | Baseline requires explicit `tools.github.mode: gh-proxy`; do **not** infer Pi never existed |

Additional target probes:

- `$ART/probes-workspace-strict/.github/workflows/aw.json` contains
  `{"strict":true}`. `opt-out.md` declares `strict: false` but emits
  `"strict":true` without CLI `--strict`; `unsafe-opt-out.md` fails for
  `contents: write`. This proves effective repository-wide enforcement.
- `$ART/probes-package-v0.88.7/aw.yml` uses `includes: [sub/aw.yml]`;
  `sub/workflows/package-worker.md` passes strict + validate. This proves manifest
  validation/compilation, **not** an exercised remote package installation.

## 4. Author-ready capability notes

All notes below inspect **v0.88.7**. “Baseline erratum” means the correction must not
be marketed as a newly introduced feature. Concepts for ch04–ch14 are in the
historical combined feature/concept briefs, since separate theory files do not exist
for those chapters.

### F01. Compiler contract and authoring loop

**Implements concept:** [reviewable source, compilation, two artifacts](../../ch03-theory.md#concepts-covered)
and [authoring loop](../../ch02-theory.md#concepts-covered).

**Syntax:** `compile [workflow]... --strict --validate --json`,
`compile --no-emit`, `compile --watch`, opt-in `compile --fix`;
`fix --list-codemods`, `fix <workflow>` (dry-run), `fix <workflow> --write`.
New optional scanner flags include `--shellcheck`, `--yamllint`, `--grype`,
`--syft`, and `--grant`; `--models` warns about model inventory mismatches.
`--force-refresh-container-pins` refreshes container pin state. `--dir` also respects
`GH_AW_WORKFLOWS_DIR`. Do not run watch mode in unattended verification.

The `.md` → `.lock.yml` architecture and strict-by-default behavior are unchanged.
Generated pins, dependencies, defaults, schemas and job steps are not unchanged.
The target triage lock still uses metadata schema `v4`, now records compiler
`v0.88.7` and Copilot `1.0.80`, and is about 118.5 KB in this environment.
Do not copy the historical 100 KB lock excerpts or hard-code a universal six-job graph.
The model can run in detection as well as the main agent job; deterministic
orchestration is **not** the same as deterministic detection.

**Use / avoid:** compile after configuration changes and before review; inspect emitted
artifacts. Do not use compile as a live test or call it universally offline,
API-free, side-effect-free, or a constant “~100 ms” operation. Reproducibility depends
on compiler version, dependency resolution, configuration, repository/schedule context
and relevant existing lock state, not solely on Markdown bytes.

**Minimal verified example:** `examples/ch02/repo-assistant-triage.md`;
`$ART/probes-v0.88.7/.github/workflows/defaults.md`.
**Sources:** [target CLI reference](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/setup/cli.md),
[compilation process](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/compilation-process.md),
[validation implementation](https://github.com/github/gh-aw/blob/v0.88.7/pkg/workflow/compiler.go),
[scanner configuration](https://github.com/github/gh-aw/blob/v0.88.7/pkg/cli/compile_config.go).

### F02. Trigger admission, cooldown, and stacked PRs

**Implements concept:** [the outer loop's clock; reactive versus proactive work](../../ch04-features.md#concept-theory).

**Verified syntax:**

```yaml
on:
  schedule: hourly
  workflow_dispatch:
  cooldown: 4h
```

`cooldown` is new. It takes a literal Go duration, at least five minutes, not an
Actions expression. It measures from completion of the most recent completed run
whose `agent` job started, including failed agent runs. Skipped agents do not reset
it. It adds `actions: read` to pre-activation. **History lookup failure fails open**:
this is a noise/cost control, not a guaranteed spend cap.

`on.pull_request.max-stack` and `on.pull_request_review.max-stack` now default to
**1** (top-most PR); positive N admits the top N layers; `-1` disables stack
filtering. Non-stacked PRs are unaffected. `on.workflow_run.conclusion: [failure]`
now compiles, unlike the same embedded ch10 snippet on the baseline.

`on.stop-after` gained expression support during the interval. Correct the old
“every recompile resets the deadline” statement: the compile CLI explicitly
preserves existing stop times unless refreshing is requested with
`--refresh-stop-time`. Keep `on.roles` nested; do not introduce top-level `roles`.
Schedule scattering considers repository seed as well as workflow identity.

**Use / avoid:** use cooldown/stack limits to reduce redundant work; keep real
budgets and concurrency controls. Do not describe cooldown as a lock, or a deadline
as guaranteed suppression of every possible dispatch path.

**Minimal verified examples:** existing ch04 workflow; probes `cooldown.md` and
`workflow-run-conclusion.md`. `max-stack` and stop-after expressions are
tagged-schema/reference findings; add a verifier-owned fixture before teaching a
new complete workflow around them.
**Sources:** [triggers](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/triggers.md),
[schedule syntax](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/schedule-syntax.md),
[cooldown commit](https://github.com/github/gh-aw/commit/91c53ccc9e0c408546b384ad2e8cb3484b5e15d8),
[stop-after commit](https://github.com/github/gh-aw/commit/88a72b0e38ffefbcea25be22863f5842d7c8b500).

### F03. Engines, model selection, and honest portability

**Implements concept:** [engine-neutral intent](../../ch05-features.md#concept-theory).

**Syntax:** simple `engine: copilot|claude|codex|gemini|pi`; object form
`engine: {id: ..., version: ..., model: ...}`; top-level `model: auto`.
The target reference lists **five built-in engines**. OpenCode, Aider, Crush,
Cursor, DeepSeek Harness, Kiro, and Pydantic integrations are samples without a
gh-aw compatibility/maintenance commitment. Imported engines use object-form
`engine.id` plus an owner-maintained pinned definition, not an arbitrary scalar
`engine: custom`.

Top-level `model` is new, but **`engine.model` is valid at the target and takes
per-engine precedence**. The interval first deprecated it and then restored that
override. The existing Claude example still compiles unchanged.
Omitted Copilot model now emits fallback `auto`, rather than the baseline
`claude-sonnet-4.6`. Dynamic selection changes predictability and cost comparisons.
Do not reclassify an unchanged prompt as a controlled model experiment.

Baseline errata: omission does not justify saying every engine CLI installs an
unbounded latest release. Target compiled defaults include Copilot 1.0.80, Claude
2.1.247, Codex 0.150.1, Gemini 0.55.1, and Pi 0.84.3, subject to configured overrides.
The book's explicit Claude 2.1.70 pin compiles; that alone is not a recommendation
that it remains the best operational pin.

**Use / avoid:** choose by supported tools, identity, model availability, and budget.
Intent is portable; authentication, tool enforcement, network, and model names need
review. Top-level `max-turns` works across engines; the deprecated nested
`engine.max-turns` is not the general cross-engine form.

**Minimal verified examples:** existing ch05 workflow; `model-top-level.md`,
`model-precedence.md`, `pi-engine.md`. Pi's target probe warns that its threat
detector uses Copilot and needs Copilot authentication; another provider key alone
does not prove a complete Pi run will work.
**Sources:** [engines](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/engines.md),
[version constants](https://github.com/github/gh-aw/blob/v0.88.7/pkg/constants/version_constants.go),
[Copilot fallback change](https://github.com/github/gh-aw/commit/6058f2272599aed5fe00cbd9d572ca89298cf3ea),
[override restoration](https://github.com/github/gh-aw/commit/b588b670994c62e6ac5c2b642e15098bcfedc4f7).

### F04. Authentication and billing are explicit configuration

**Implements concept:** [least privilege and safe defaults](../../ch02-theory.md#concepts-covered),
[budget/policy separation](../../ch13-features.md#concept-theory).

**Syntax:** `permissions: {contents: read, copilot-requests: write}` for enabled
organization billing, or a `COPILOT_GITHUB_TOKEN` secret for seat billing.
`permissions.copilot-requests: none` suppresses the org-billing tip when intentionally
using a PAT. The compiler does **not** auto-add org billing to arbitrary source.
Org policy must allow centralized Copilot CLI billing, and the updated lock must be
deployed. The chapter's current example does not declare this permission, so its
unchanged live path requires the PAT.

The interval adds activation rejection of OAuth `gho_` tokens in
`COPILOT_GITHUB_TOKEN` / `GH_AW_GITHUB_TOKEN`; do not tell readers to reuse an
interactive CLI OAuth session token. Claude supports key/WIF paths, Gemini has
Google WIF, and Codex accepts `CODEX_API_KEY` or `OPENAI_API_KEY`. Treat new cloud
identity examples as optional, runtime-credential-dependent material.

**Use / avoid:** distinguish repository read/write authority, provider authentication,
and billing permission. Never imply a compiler PASS validates a provider secret,
an account entitlement, model availability, or organization billing policy.

**Minimal verified examples:** `copilot-org-auth.md`; existing ch02/ch05 workflows.
**Sources:** [authentication](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/auth.mdx),
[billing](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/billing.md),
[v0.82.5](https://github.com/github/gh-aw/releases/tag/v0.82.5).

### F05. Safe outputs: preserve the boundary, refine its claims

**Implements concept:** [propose, validate, apply](../../ch06-features.md#concept-theory).

The existing `add-comment`, allowlisted `add-labels`, and draft
`create-pull-request` configurations remain valid. New useful syntax includes:

```yaml
safe-outputs:
  add-labels:
    allowed: [needs-triage]
    create-if-missing: true
    max: 1
```

At the target, absent/false `create-if-missing` rejects nonexistent labels.
An `allowed` list bounds accepted labels; it does not by itself provision them.
Omitting real output types can still enable the automatic issue fallback: even the
minimal probe declaring only `safe-outputs.noop` emitted `create_issue`. Those
compile-only probes are not production examples of disabling all writes.
Per-output `github-app` overrides, issue/PR permission controls, dynamic reviewers,
review `commit-id`, stacked PRs, and PR steering expand the boundary.
`safe-outputs.steer: true` is separate from `create-pull-request.stacked`.
Do not conflate the transient pre-created-PR feature's release name with final syntax.

`submit-pull-request-review.allowed-events: [COMMENT]` remains important:
omitting it allows APPROVE and REQUEST_CHANGES too. Human merge is **the book's
chosen policy**, not a universal lack of auto-merge/merge capabilities in gh-aw.
For a file-scope guarantee, use appropriate `allowed-files`/protected-file controls,
not merely the prompt “do not edit production code.”

New `approve-workflow-run` is experimental and authorizes a fork's workflow run;
it is **not** PR approval or merge permission. Keep it out of beginner recipes.
External-tracker outputs for Jira, Linear and Azure DevOps are available in the
target schema; introduce only with separately verified credentials/tool fixtures.

**Use / avoid:** narrowly scoped mediated writes, small caps, staged previews for
rollout. Staged mode still runs the agent and can incur costs; it is not compile-only
validation or proof that no activation/status activity happens. Never promise that
sanitization makes all model output safe.

**Minimal verified examples:** existing ch06/ch09/ch10 workflows; `label-creation.md`.
New advanced PR/App/tracker configurations are optional handoff leads, not
compile-certified complete book examples.
**Sources:** [safe outputs](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/safe-outputs.md),
[PR outputs](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/safe-outputs-pull-requests.md),
[staged mode](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/staged-mode.md),
[target schema](https://github.com/github/gh-aw/blob/v0.88.7/pkg/parser/schemas/main_workflow_schema.json).

### F06. Runtime profiles replace legacy sandbox privilege fields

**Implements concept:** [substrate isolation and defense in depth](../../ch07-features.md#concept-theory).

**Syntax:**

```yaml
sandbox:
  agent:
    runtime: docker
```

The baseline accepts `sandbox.agent.sudo: true`; the target rejects that key.
During the interval sudo first defaulted false, then the configuration became runtime
profiles. At the target, omission means **`docker`**, rootless AWF with network
isolation. Deliberate host/service access uses `runtime: docker-sudo-iptables`;
`allow-host-ports` is valid only with that profile. Do not mechanically translate
every old `sudo` workflow into privileged host access.

`cloud-hypervisor` is preview and needs suitable KVM/runner support. `gvisor` and
`docker-sbx` are deprecated in target documentation. Disabling the agent sandbox
requires `strict: false` plus the explicit
`features.dangerously-disable-sandbox-agent: true` flag; do not recommend it as a
workaround for ordinary compile errors.

**Use / avoid:** default Docker for the book; special runtimes only for demonstrated
runner requirements. Compiling on Windows does not prove a Windows Actions runner,
Docker daemon, KVM device, or remote MCP process is operational.

**Minimal verified examples:** `runtime-docker.md`, `runtime-host-services.md`;
intentional negative `legacy-sudo.md`; existing ch07 remains valid unchanged.
**Sources:** [sandbox](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/sandbox.md),
[runtimes](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/agent-runtimes.md),
[sudo default commit](https://github.com/github/gh-aw/commit/73c496b9a44fd2f46d220b587e18a33e6d625c8e),
[v0.88.0](https://github.com/github/gh-aw/releases/tag/v0.88.0).

### F07. Network, detection, and artifact security changes

**Implements concept:** [break the lethal trifecta in multiple layers](../../ch07-features.md#concept-theory).

`network: defaults`, `network: {allowed: [defaults, github]}`, and `network: {}`
still compile. **Engine domain bundles are no longer added automatically**;
direct provider egress is an explicit opt-in. Inference normally goes through the
AWF API proxy. Do not “fix” every example by adding all provider or package-registry
domains, and do not describe `{}` as proving the entire workflow makes no network
requests: model inference and mediated tooling have separate paths.

`safe-outputs.threat-detection` remains the enable/configuration control. External
`threat-detect` became the default implementation; `features.gh-aw-detection: false`
selects the legacy inline implementation, **not** “disable detection.”
Target triage locks install threat-detect v0.5.1 and execute AI analysis in `detection`.
This invalidates the ch03/ch12 “exactly one non-deterministic job” explanation.

The interval hardens OAuth/token exclusion, git/URL/OTLP/MCP logging, summaries,
patches and artifact paths. v0.88.7 restricts agent packaging to known files and
moves Claude debug logs outside the agent data directory. Explain these concrete
changes; never repeat release-summary claims of impossible leakage.

For advanced data-flow governance, target schema supports
`tools.github.private-to-public-flows`: blanket `allow` is incompatible with strict
mode, while selective MCP-server exemptions are a distinct configuration.
Dynamic enclave delegation is an advanced, version-coupled surface (target
MCPG v0.4.18), not a beginner alternative to least privilege.

**Use / avoid:** keep strict mode, narrow egress and independent review. Allowed hosts
can still be data sinks; a firewall is not a proof that “a leaked secret has nowhere
to go.” Preserve redaction without calling logs complete or infallible.

**Minimal verified examples:** existing ch07/ch12, `no-network.md`, `defaults.md`.
Enclave/exemption configurations are tagged-source findings only, deliberately
excluded from the recommended example wave.
**Sources:** [network](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/network.md),
[detection](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/threat-detection.md),
[external detection change](https://github.com/github/gh-aw/commit/be23dc33e0e3a19f904018fc942a80fc9842fdac),
[artifacts](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/artifacts.md),
[enclaves](https://github.com/github/gh-aw/blob/v0.88.7/.github/aw/enclaves.md),
[security compatibility policy](https://github.com/github/gh-aw/blob/v0.88.7/.github/aw/compat.md).

### F08. Tools and MCP: actual enforcement is engine-dependent

**Implements concept:** [capability versus exposure](../../ch08-features.md#concept-theory).

**Syntax:** `tools.github.toolsets`, `tools.bash: ["echo", "git status"]`,
`tools.web-fetch`, and `mcp-servers.<id>` remain the relevant surfaces.
A strict target workflow with `engine: codex` and `tools.bash: ["echo"]`
fails with the explicit diagnostic that this engine silently ignores command
allowlisting at runtime. The same source passes the baseline.
Choose a supporting engine (Copilot, Claude, Gemini) when the restriction matters;
do not silently replace an allowlist with unrestricted shell.

The current ch08 workflow's GitHub toolsets and web-fetch compile without changes.
The inline Slack example, however, is an unpinned third-party package and has not
been covered by the existing workflow corpus. Replace or separately verify it
rather than relabeling it target-verified.

Target MCP servers can distinguish required from optional startup failures;
inspection now includes prompt discovery, pagination fixes, and redaction.
`mcp inspect --help` was inspected, **not** a live server connection.
Container, stdio and remote HTTP transports must not all be described as “a local,
separate isolated container per server.” Explain the chosen transport and trust
boundary. Native Jira/Linear read tools and mediated tracker outputs merit an
optional catalog note, not an unverified production recipe.

**Use / avoid:** least tool authority and pinned server dependencies; never present
engine-neutral intent as identical tool enforcement.
**Minimal verified examples:** existing ch08/ch10; negative `codex-bash-allowlist.md`.
**Sources:** [engine feature matrix](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/engines.md),
[tools](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/tools.md),
[MCP gateway](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/mcp-gateway.md),
[capability diagnostic change](https://github.com/github/gh-aw/releases/tag/v0.86.1).

### F09. Playwright is now a CLI integration

**Implements concept:** [governed tool access](../../ch08-features.md#concept-theory),
[quality-loop testing](../../ch10-features.md#concept-theory).

**Syntax:** `tools: {playwright: {}}` plus appropriate `network.allowed` entries.
The target installs `@playwright/cli`, skills, and requested browsers before the
agent runs; commands are `playwright-cli ...` through Bash. Omit `mode`; legacy
`mode: cli` remains accepted. `mode: mcp` fails compilation with migration guidance.
The schema deliberately retains the old enum value for that diagnostic: schema
acceptance alone is not sufficient.

Use `browsers: [chrome, firefox]` only if needed; Chromium is the default. The
`version` pin is for **`@playwright/cli`**, not a browser/MCP package version.
The focused target Playwright reference uses 0.1.18; do not reuse the stale
`tools.md` example pin 1.56.1 as though it names the CLI.
Existing MCP-specific prompt/tool names must also change, not only frontmatter.
If MCP is essential, define and pin a custom `mcp-servers` integration separately.

**Use / avoid:** CLI for ordinary browser work; no automatic MCP migration claim,
no live browser verification claim from compilation.
**Minimal verified example:** `playwright-cli.md`; negative `playwright-mcp.md`.
Existing ch08 does not need a workflow edit just because its prose lists Playwright.
**Sources:** [Playwright reference](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/playwright.md),
[removal commit](https://github.com/github/gh-aw/commit/7206a58068deaf2662682016ede08f095d359eaa).

### F10. Imports, native skills, and experimental plugins

**Implements concept:** [DRY configuration and governed agent context](../../ch11-features.md#concept-theory).

**Syntax:** `imports: [shared/triage-policy.md]` or `uses`/`with` parameterization
continues to work. New native `skills: [.github/skills/probe]` compiles; remote
forms use `owner/repo[/path]@ref`. Branch/tag skill refs are resolved to SHAs,
but failed resolution can retain an unpinned ref with a warning. Do not say all
native skill pins are fail-closed.

Experimental `plugins: [owner/repo[/path]@ref]` is different: branch/tag resolution
failure is fatal; supported engines include Copilot, Claude and Codex, with
engine-specific installation. It emits an experimental warning. Per-entry
`github-token` / `github-app` are mutually exclusive. This is not equivalent to
importing APM's shared workflow.

Nested import dependency/cycle handling and object-form import preservation were
fixed during the interval. Target shared components need **no trigger event**, not
necessarily literally no `on` block: import-safe on-options are allowed.
Default imports do not make every lock completely self-contained. Do not erase the
distinction between compile-time configuration, runtime prompt loading and
`inlined-imports`.

**Use / avoid:** share a stable policy; review source and pins. A pinned import or
vendored copy does **not** automatically take a central edit on its next compile.
Each consumer must deliberately update the pinned/vendored dependency and recompile.
APM's third-party policy/lock semantics require independent APM-version evidence;
target gh-aw docs linking a live APM page do not prove every APM claim in ch13.

**Minimal verified examples:** existing ch11/ch14; `skills-local.md`.
Plugins/APM integration are scoped follow-up leads, not runtime-verified here.
**Sources:** [imports](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/imports.md),
[skills/plugins](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/frontmatter.md),
[APM integration](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/dependencies.md),
[nested imports fix](https://github.com/github/gh-aw/releases/tag/v0.88.0).

### F11. Memory: validation, filtering, and persistence scope

**Implements concept:** [memory solves amnesia across runs](../../ch11-features.md#concept-theory).

**Verified syntax:**

```yaml
tools:
  repo-memory:
    file-glob: ["**/*.json"]
    allowed-extensions: [".json"]
    validation:
      script: |
        if (!fs.existsSync(memoryRoot)) throw new Error("Missing memory root");
      timeout-minutes: 1
```

Custom JavaScript validators receive `fs`, `path`, memory root/id/kind and a
restricted environment; they run before persistence and again in the protected push
path. Exceptions, false returns, nonzero exits, timeouts, or mutation reject the
update. A validator addition triggers safe-update review. A one-minute default
and 1–5 minute accepted timeout are documented.

v0.88.7 changes disallowed extensions/globs into **persistence filters** before
validation/upload/push. Ineligible files are removed/ignored, including stale branch
files after a policy change. Authors must warn about data disappearing from persistence,
not promise a failing run for every disallowed file. Slashless `*.json` matches
artifact-root files; `**/*.json` covers nested data.

Baseline errata: cache memory is evicted after **seven days unused**, not a
guaranteed seven-day lifetime; `retention-days` controls uploaded artifact retention,
not cache lifetime. Default repo memory is repository-scoped; importing the same
policy in another repository does not share its accumulated knowledge.

`tools.drive-memory` is **private preview**, explicitly enrollment-gated. Do not
configure it for the general book audience or count schema acceptance as service access.

**Use / avoid:** repo memory for durable versioned knowledge; cache for disposable
branch-scoped state; validators for data contracts. Never store secrets, treat memory
as trusted instructions, or promise automatic cross-repo learning.

**Minimal verified examples:** existing ch11/ch14; `repo-memory-validation.md`
(PASS with a new-validator approval warning).
**Sources:** [repo memory](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/repo-memory.md),
[cache memory](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/cache-memory.md),
[filtering commit](https://github.com/github/gh-aw/commit/6f063409a3d37f12a98c35a0cdcff27d2c0587d4),
[private-preview drive memory](https://github.com/github/gh-aw/blob/v0.88.7/.github/aw/drive-memory.md).

### F12. Logs, audit, graders, and honest completion

**Implements concept:** [observability is a precondition for trust](../../ch12-features.md#concept-theory).

**Inspected command syntax** (read/help only, not run here):

```text
gh aw logs workflow-a workflow-b --count 20
gh aw logs owner/repo/workflow-a --audit
gh aw logs --artifacts agent,firewall --exclude-staged
gh aw logs --max-storage 10240 --prune-older-runs
gh aw logs --max-github-api-rate-limit -2000 --timeout 30
gh aw audit 1234567890 --repo owner/repo
gh aw audit https://github.com/owner/repo/actions/runs/1234567890
```

Logs now accepts multiple workflow targets, including cross-repository paths;
the default count is still **10 per workflow**, not “all history” just because
dates are supplied. `--exclude-staged` replaces the old `--no-staged` spelling.
`--runtime`, `--evals`, and logs `--graders` filter richer run records.
`--audit` creates/reuses each cached run's `audit.json` from downloaded data;
it does not mean the overall logs invocation makes no API calls.

`--max-storage` is MB, zero unlimited; it prunes nonessential completed-run data,
preserving summaries/metadata where possible. `--prune-older-runs` can remove older
completed runs if still over budget. The API budget flag counts **used core API
requests**, or reserves a number when negative; it is not an AI-credit budget.
The target help requires `--repo` with a bare audit run ID; a complete URL carries
repository context. Do not invent an actual audit report from illustrative IDs.

`graders` and eval/trajectory metrics expand observability, but are not substitutes
for outcome/human review. v0.88.7 now calls `core.setFailed` when the agent reports
`report_incomplete`, while still allowing optional issue-reporting logic to proceed.
Teach `noop` (no work needed) versus inability to complete as different outcomes.

**Use / avoid:** small downloads first, retain stderr and failure-kind evidence,
then widen deliberately. Artifacts can be redacted, omitted or pruned; don't promise
an everlasting complete transcript. A denied domain should be investigated, not
automatically allowlisted.

**Minimal verified example:** `examples/ch12/repo-assistant-observable.md`;
command coverage is help/source inspection, **not** a live run/audit.
**Sources:** [CLI](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/setup/cli.md),
[audit reference](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/audit.md),
[incomplete-work failure](https://github.com/github/gh-aw/commit/17102565c7209c3dc26b04a396f4afd0e33fe477),
[v0.88.6](https://github.com/github/gh-aw/releases/tag/v0.88.6),
[v0.88.7](https://github.com/github/gh-aw/releases/tag/v0.88.7).

### F13. FinOps: budgets, model policy, and forecasting

**Implements concept:** [variable inference cost needs budgets and policy](../../ch13-features.md#concept-theory).

**Verified syntax:** existing `max-ai-credits: 200`, `max-daily-ai-credits: 2000`;
new `models: {allowed: ["claude-*"], blocked: ["claude-opus-*"]}` and
top-level `model: auto`. `blocked` is the final spelling, not the release summary's
`disallowed`. Model permission policy is not the same as a spend cap.

Record the empirically resolved defaults:

| Setting | v0.81.6 emitted default | v0.88.7 emitted default |
|---|---|---|
| Main-agent AIC | 1000 | 1000 |
| Daily workflow AIC fallback | 5000 | 5000 |
| Detection AIC | 400, separate | 400, separate |
| Copilot agent fallback model | `claude-sonnet-4.6` | `auto` |
| Default agentic step timeout | 20 minutes | 20 minutes, runtime-variable expression |
| Generated agent job timeout | No explicit value in the minimal baseline probe | 60 minutes |
| Generated detection job timeout | No explicit value in the minimal baseline probe | 10 minutes |

Do not present the main-agent cap as a complete bill cap: detection and Actions
compute are separate. The daily check is a rolling historical threshold before
agent admission, not a globally atomic accounting lock; internal dispatch paths can
bypass that check as documented, and API queries have a cost.
Dynamic `auto` pricing is accounted against the resolved concrete model by the
target firewall, rather than a fictitious fixed price for “auto.”

`gh aw models --json --refresh-observed=false` inspects catalog/alias data without
requesting observed-model refresh; the default is refresh-on.
`gh aw forecast <workflow> --period week --days 7 --sample 50 --json` is available.
The experimental label was removed during the interval, **not** the accuracy
disclosure: estimates come from historical samples and can be wrong. No forecast
or billing rates were empirically measured here.

**Use / avoid:** bound the individual agent, detector, time, and admission rate
separately; compare like configurations and price sources. Avoid hard-coded
next-edition model prices or claims of guaranteed monthly spend from per-run caps.

**Minimal verified examples:** existing ch13; `defaults.md`, `models-policy.md`,
`model-top-level.md`; model/forecast commands inspected via help.
**Sources:** [cost management](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/cost-management.md),
[enterprise default resolution](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/compiler-enterprise-environment-controls.md),
[detection budget](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/threat-detection.md),
[forecast promotion](https://github.com/github/gh-aw/releases/tag/v0.84.0),
[budget interpolation hardening](https://github.com/github/gh-aw/releases/tag/v0.88.2).

### F14. Repository strict policy versus defaults and runtime gates

**Implements concept:** [govern centrally; allow deliberate exceptions only where intended](../../ch13-features.md#concept-theory).

**Syntax:** `.github/workflows/aw.json`:

```json
{"strict": true}
```

This new repository setting only accepts true. It forces effective strict
compilation across workflows, even when a workflow declares `strict: false`.
The harmless opt-out probe emitted strict metadata; its write-permission variant
failed. This is a **compile-time** policy and does not repair previously deployed
locks until they are regenerated and deployed.

Do not conflate it with overridable `GH_AW_DEFAULT_*` values or runtime
`GH_AW_POLICY_*` capability gates. The target explicitly distinguishes resolution
times: model and timeout defaults can be emitted as `${{ vars.* }}` runtime
expressions, while `GH_AW_DEFAULT_MAX_TURNS` and some token/detection-model defaults
are read from the **compiler process environment**. Setting an Actions variable
does not automatically inject it into a developer's local compiler process.

**Use / avoid:** central strictness for a governed repo; defaults for tunable
preferences; runtime gates for supported capabilities. Avoid saying all enterprise
configuration changes affect all already-compiled workflows without recompilation.

**Minimal verified example:** `$ART/probes-workspace-strict/` fixtures.
**Sources:** [repo config schema](https://github.com/github/gh-aw/blob/v0.88.7/pkg/parser/schemas/repo_config_schema.json),
[strict policy commit](https://github.com/github/gh-aw/commit/25fb43e7898db2c8bcd6a9cdbadffed38242c03e),
[enterprise controls](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/compiler-enterprise-environment-controls.md).

### F15. Fleet distribution and package boundaries

**Implements concept:** [a fleet is a managed practice, not copies](../../ch14-features.md#concept-theory).

**Verified manifest syntax:**

```yaml
name: Central workflows
includes:
  - sub/aw.yml
```

Target packages can recursively include manifests, map inert distribution paths to
workflow destinations, and use trailing `/*` wildcard mappings. Cycles and
case-insensitive destination collisions are rejected. Package `aw.yml`, repository
`.github/workflows/aw.json`, workflow Markdown `imports`, and APM `apm.yml` are
**four distinct formats**. Root README requirements and path restrictions matter.

`gh aw add` versus `add-wizard` matters for packages with interactive `config`
steps; the interval intentionally made ordinary `add` reject that case rather than
silently leave TODO setup. The target can also merge packaged `aw.json` settings
into the destination with added-package precedence: installing a workflow package
can change project settings, not just copy one `.md`.

`update` preserves local edits by three-way merge by default, refreshes package
resources/skills/plugins, and can bump action majors. `--no-release-bump` still
permits core `actions/*` bumps; it is not “freeze every action.”
An explicit update also advances the recorded source according to its ref type:
tags seek a newer release (`--major` permits major upgrades), branches track their
latest commit, and commit-SHA sources seek the default branch's latest commit.
Thus a source pin constrains the installed revision, not an instruction that
`update` must leave it permanently frozen. Review the resulting source/lock diff.
`upgrade` performs codemods/action updates/compilation and can upgrade the extension;
`compile` does not apply codemods without `--fix`. These mutating operations were
not run on the book or on the personal extension.

**Use / avoid:** pinned distribution plus reviewed consumer updates and whole-fleet
verification. A central edit does not automatically change pinned consumers;
`source:` alone neither proves installation nor enforces all org policy.
`tracker-id` markers support searching body-bearing outputs, not a literal hidden
marker on every label operation.

**Minimal verified examples:** existing ch14; `$ART/probes-package-v0.88.7/`.
Remote install/update and fleet propagation are not runtime-certified.
**Sources:** [package manifest](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/aw-yml-package-manifest.md),
[package schema](https://github.com/github/gh-aw/blob/v0.88.7/pkg/parser/schemas/aw_manifest_schema.json),
[CLI](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/setup/cli.md),
[interactive-config migration](https://github.com/github/gh-aw/commit/f8a0b360e107fef803bb3565890c79f65bf837e7).

## 5. Chapter-by-chapter author handoff

Every chapter is marked **update**, but this is a targeted correction plan, **not**
a fourteen-chapter rewrite. No chapter is marked unchanged: each has at least one
reader-facing behavior, qualification, or recipe correction beyond a version stamp.
There is no evidence that a new chapter or changed slug is necessary.
Unchanged concepts/working sources are explicitly identified below.

| Chapter | Concrete author work | Preserve / example disposition |
|---|---|---|
| **ch01** What Are Agentic Workflows? | Qualify “PRs are never merged automatically” as this book's human-review policy, not a product impossibility; qualify mediated writes rather than unconditional safety. Use F05/F07. | Keep inner/outer loop, Continuous AI, case-study context and borrowed ch02 example. Do not refresh historical adopter statistics without separate evidence. |
| **ch02** Your First Workflow | Pin the edition's install target, distinguish the isolated compiler from global extension setup; replace “offline/no GitHub” with no engine invocation; make org-billing prerequisites and unchanged-example PAT path explicit. F01/F04. | Retain the existing triage source. Replace stale compiler output only with newly captured output. Low-risk pilot. |
| **ch03** Anatomy & Compile Model | Regenerate lock excerpts; replace “five deterministic jobs around one model job” with deterministic orchestration plus main and detection inference. Explain side effects, optional validators, context-dependent resolution; do not call `status` universally offline. F01/F07. | Preserve two-artifact/source-of-truth concept and borrowed ch02 workflow. Avoid an invented full lock. |
| **ch04** Triggers | Add cooldown with fail-open caveat, stack filtering, correct `on.roles` placement and slash-command spelling from schema; correct stop-time refresh/scattering explanations. F02. | Existing workflow passes. Keep reactive/proactive framing; require new fixtures for optional stack/expression demonstrations. |
| **ch05** Engines | Five target built-ins, samples versus supported integrations, `model`/`engine.model` precedence, `auto` fallback, real default CLI pins, top-level turn limits, authentication/tool portability caveats. F03/F04/F08. | Existing Claude workflow passes but has a review warning. Do not silently modernize its explicit pin without a separate reason and re-verification. |
| **ch06** Safe Outputs | Explain label existence versus allowed labels; retain explicit comment-only/draft constraints; distinguish staged execution from compilation; qualify “never overreach”; optionally introduce per-output Apps/PR steering after fixtures. F05. | Existing draft-PR workflow passes. Preserve propose/apply theory, but do not claim a live PR was created by compilation. |
| **ch07** Defense in Depth | Teach final runtime profiles, rootless Docker, explicit egress and external detection; remove “a compromised prompt is a non-event” / “secret has nowhere to go.” Explain workspace strict policy and targeted compatibility blocking. F06/F07/F14. | Existing hardened workflow passes. Keep layered threat model; no need to add privileged sandbox options to it. |
| **ch08** Tools & MCP | Playwright CLI migration, engine-specific Bash enforcement, transport-specific MCP isolation, pinned/custom-server verification; optional read-only tracker catalog. F08/F09. | Existing GitHub/web-fetch workflow passes. Do not mistake it for verification of the inline Slack snippet. |
| **ch09** Triage & Docs | Add deployment prerequisites (Issues enabled for issue fallback, existing labels), refresh compile claims and explain admission/budget/no-work behavior without promising “forever.” F02/F05/F12/F13. | Both source recipes pass in reference context. Keep pattern composition and prompts; no mandatory schema migration. |
| **ch10** Review & Testing | Correct the baseline CI-doctor `conclusion` claim using the passing target probe; explain top-of-stack filtering, unsupported Codex Bash restrictions, file-scope enforcement versus prompt requests. F02/F05/F08. | Both existing source recipes pass. Keep COMMENT-only reviews and human merge as chosen policy. |
| **ch11** Reuse & Memory | Fix automatic propagation/self-contained-lock/cross-repo-memory claims; distinguish native skills/plugins/APM; teach filtering-before-validation, nested globs, seven-days-unused cache semantics, and private-preview exclusion. F10/F11. | Existing imported workflow and both local fragments remain valid. Preserve DRY versus persistence distinction. |
| **ch12** Observability | Update logs flags, multi-target count limits, cached audit/storage budgets, bare-ID repo context, incomplete-work failure, OTLP/redaction/retention limits; remove “only one non-deterministic job” and invented actual report claims. F07/F12. | Existing OTLP workflow passes with two secret-review warnings. Any displayed run metrics remain explicitly illustrative. |
| **ch13** Governance & FinOps | Correct daily fallback to 5000 (baseline erratum), detector budget and Actions costs, step versus job timeout, compile-time versus runtime defaults; add model policy/models/forecast and workspace strictness. Keep APM claims version-scoped separately. F04/F13/F14. | Existing 200/2000 budget workflow passes. Do not equate these settings with a complete monthly bill cap. |
| **ch14** Fleets & Adoption | Add package format distinctions and reviewed settings/resource updates; explain pinned consumer upgrades, action-bump semantics, marker limits and current compatibility policy. F10/F14/F15. | Existing synthetic fleet workflow passes; preserve phased rollout/maturity arc, but label synthetic origin rather than claim an exercised installation. |

## 6. Verification limits and blockers

1. **Docker daemon unavailable.** `docker.exe` is installed, but `docker info`
   failed to connect to `dockerDesktopLinuxEngine`. Image validation is silently
   skippable without `--validate-images`; no image-existence, CVE/license/SBOM,
   Docker MCP, browser, or sandbox-runtime test is claimed. Native actionlint and
   ShellCheck were not found. Optional scanner flags were inspected, not executed.
2. **No live workflow, model, provider, MCP connection, cloud identity, OTLP export,
   forecast, or billing measurement.** `run`, `logs`, `audit`, and MCP inspection were
   explored through help only. Missing credentials do not waive compilation; they
   bound runtime claims.
3. **Book repository has Issues disabled.** Do not change its settings to make a
   teaching example pass. Parent/code-verifier must explicitly distinguish isolated
   source compilation from deployment-context validation.
4. **Approval warnings are real.** Claude, OTLP and the new memory validator require
   deliberate review. No automatic `--approve` was used to hide them. A JSON-only
   warning count is insufficient.
5. **Optional new capabilities need author/verifier fixtures before publication.**
   Remote plugins, App overrides, advanced PR steering, WIF, new tracker outputs,
   graders, and enclave policies were not promoted to fully verified worked examples.
   Drive memory is private preview and intentionally excluded.
6. **APM is independently versioned.** The gh-aw tag proves the integration reference,
   not every current APM lockfile/policy/isolation assertion. The current inline APM
   examples are not in the 14-workflow corpus; preserve scope or verify them separately.
7. **Research PASS is not release acceptance.** After author changes, parent/code-verifier
   must run the entire final corpus with the pinned target and review embedded
   workflows against their source files. Editorial review and source-bound acceptance
   still gate the edition; no PR, merge, or publication is requested here.

## 7. Prioritized update waves

| Wave | Chapters | Scope and exit evidence |
|---|---|---|
| **0 — low-risk pilot** | **ch02** | Retain passing workflow; correct pin/install/compile/auth prose. Recompile its source, synchronize embedded example, obtain actual review before scaling. |
| **1 — foundations** | ch01, ch03, ch04, ch05 | Correct boundaries and engine/default claims together; use exact lock/probe evidence. Preserve concept narrative. |
| **2 — security/tool contract** | ch06, ch07, ch08 | Highest-risk semantics: runtime migration, explicit egress, detection, Bash enforcement, Playwright, safe-write qualifications. No blanket privilege/network widening. |
| **3 — applied patterns** | ch09, ch10 | Keep working recipes; add prerequisites and align trigger/output enforcement claims with waves 1–2. |
| **4 — state and operations** | ch11, ch12 | Memory filtering/persistence, reuse/pins, skills/plugins scope, logs/audit/OTLP, incomplete-work failure. |
| **5 — organization** | ch13, ch14 | Budget/default timing, strict policy, model forecasting, packages and fleet update boundaries. |
| **6 — final integration, parent-owned** | All 14 | Full emitted-lock strict corpus PASS; embedded-source review; actual editorial ACCEPT. Only then advance framework coverage and prepare the prose edition. No publish/merge/PR in this phase. |

This order favors a small demonstrably compiling pilot, then fixes shared mental models
before patterns and fleet-level promises. Security and observability findings remain
high priority even though their source examples compile.

## 8. Commands and artifact ledger

Representative commands actually executed (read-only GitHub operations unless noted):

```powershell
gh --version
gh auth status --json hosts
gh aw version
gh api repos/github/gh-aw/releases/tags/v0.88.7
gh api 'repos/github/gh-aw/releases?per_page=100&page=1'
gh api repos/github/gh-aw/releases/latest
gh api 'repos/github/gh-aw/compare/v0.81.6...v0.88.7?per_page=100&page=1'
# Comparison requests continued through page=38.

gh release download v0.88.7 --repo github/gh-aw --pattern checksums.txt --dir $toolDir --skip-existing
gh release download v0.88.7 --repo github/gh-aw --pattern windows-amd64.exe --output "$toolDir\gh-aw.exe"
Get-FileHash "$toolDir\gh-aw.exe" -Algorithm SHA256
Get-FileHash "$toolDir\checksums.txt" -Algorithm SHA256
& $aw version
& $aw compile --help

# Official tagged source archives, stored only under session artifacts:
curl.exe --fail --location --silent --show-error https://api.github.com/repos/github/gh-aw/tarball/v0.88.7 --output "$upstream\source-v0.88.7.tar.gz"
curl.exe --fail --location --silent --show-error https://api.github.com/repos/github/gh-aw/tarball/v0.81.6 --output "$upstream\source-v0.81.6.tar.gz"

# In isolated scratch repositories, repeated for each explicit standalone path:
& $aw compile examples/ch02/repo-assistant-triage.md --strict --validate --no-check-update --schedule-seed webmaxru/github-agentic-workflows-book --json
& $aw compile .github/workflows/playwright-mcp.md --strict --validate --no-check-update --schedule-seed webmaxru/github-agentic-workflows-book --json
# Expected negative migration probe above; not a book example.

# In the workspace-policy scratch repo, intentionally without --strict:
& $aw compile opt-out --no-check-update --json
& $aw compile unsafe-opt-out --no-check-update --json
docker info --format '{{.ServerVersion}}'
```

The local compatibility phase did not call `init`, `add`, `update`, `upgrade`,
`fix --write`, `compile --fix`, or a workflow-dispatching command on the book.
Baseline and target help capture included `run --help`, not a run.

**Repository artifacts owned by this phase:**

- `content/research/updates/v0.88.7/framework-delta.md`
- `content/research/updates/v0.88.7/impact.json`

**Session evidence only** (do not copy raw downloads into the repository):

| Path below `$ART` | Contents |
|---|---|
| `tools/gh-aw/v0.88.7/` | Verified compiler and published checksums |
| `upstream-v0.88.7/release-interval.json` | Complete baseline/interval release bodies and excluded-newer tags |
| `upstream-v0.88.7/releases-page-1.json`, `latest-stable.json` | Raw release API evidence |
| `upstream-v0.88.7/compare-page-*.json`, `commits-interval.json` | All comparison commits and metadata |
| `upstream-v0.88.7/source-v*.tar.gz`, `github-gh-aw-*` | Tagged source archives and extracted sources |
| `upstream-v0.88.7/source-net-delta.json` | Uncapped changed-path inventory for inspected subtrees |
| `upstream-v0.88.7/schema-delta.json`, `schema-semantic-delta.json` | Baseline/target schema comparisons |
| `upstream-v0.88.7/selected-commits/` | Immutable selected commit metadata/patches |
| `cli-help-comparison.json`, `cli-new-command-help.json` | Captured real CLI help |
| `compat-v0.88.7-results.json` | First 13/14 context-dependent result |
| `compat-v0.88.7-neutral-results.json` | 14/14 source-compatibility result, including stderr |
| `compat-v0.88.7*/` | Unchanged copied sources and generated target locks |
| `probes-v0.81.6-results.json`, `probes-v0.88.7-results.json` | Paired 19-probe results |
| `probes-v0.81.6/`, `probes-v0.88.7/` | Minimal positive/negative fixtures and emitted locks |
| `probe-workspace-strict-result.json`, `probe-workspace-strict-unsafe-result.json` | Effective strictness observations |
| `probes-workspace-strict/`, `probes-package-v0.88.7/`, `probe-package-result.json` | Additional target policy/package probes |

Historical research, chapters and examples were not edited by this phase. Other
working-tree changes visible during research belong to the parent/tooling work and
were neither reverted nor incorporated into this phase's owned artifacts.
