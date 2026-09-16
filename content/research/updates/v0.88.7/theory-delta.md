# Conceptual delta: gh-aw v0.81.6 → fixed v0.88.7

**Brief date:** 2026-09-16. **Scope:** author handoff, not chapter prose or acceptance.

Delta classifications reuse [framework-delta.md](framework-delta.md) and
[impact.json](impact.json), inspected by the explorer on 2026-09-15. Below, **F**
links retain that assessment's tagged implementation/CLI evidence; **S** links
identify cached tagged originals re-inspected for this brief on 2026-09-16.
No fresh release archaeology, CLI execution, or live fetch was performed.
Where reference prose conflicts, retain the explorer's implementation/CLI resolution.

**Reuse unchanged theory:** the [historical briefs](../../) remain dated evidence.
Keep Continuous AI and inner/outer loops, reviewable source versus generated lock,
reactive/proactive automation, propose–validate–apply, capability versus exposure,
pattern composition, DRY versus persistence, and observability-before-trust.
Preserve **Individual → Team → Organization**, the Repo Assistant, chapter IDs and
section structure. Corrections below qualify that theory; they do not require new chapters.

## Concepts covered

- A — Orchestration versus inference.
- B — Layered least privilege and human-merge policy.
- C — Admission versus enforcement.
- D — Portable intent versus engine-specific contracts.
- E — Reviewed dependency distribution.
- F — State/evidence lifecycle and honest completion.
- G — Scoped budgets, forecasts, defaults and policy.

## A. Deterministic orchestration ≠ deterministic inference

**Chapters:** `ch02-your-first-workflow`, `ch03-anatomy-and-compile-model`,
`ch07-defense-in-depth`, `ch12-observability-and-debugging`.

**Definition/problem.** Compiled orchestration specifies job ordering, permissions
and gates so reviewers can inspect execution boundaries. Both the main agent and
default threat detector perform AI inference; an inspectable graph does not make
their judgments deterministic. [S1]

**Delta/distinctions.** Confining probabilistic reasoning to the main agent is an
**erratum**; external detection becoming the default implementation is a **change**.
Compilation invokes no engine, but dependency resolution and validators can need
network access or write local artifacts; reproducibility also depends on compiler,
dependency and repository context, not Markdown alone. [F01] [F07]

**Implemented in gh-aw by:** compiler/lock graph, engine execution, threat-detection
gate and implementation selection.

## B. Least privilege bounds authority, not all harm

**Chapters:** `ch01-what-are-agentic-workflows`, `ch06-safe-outputs`,
`ch07-defense-in-depth`, `ch10-continuous-review-and-testing`.

**Definition/problem.** Least privilege limits what compromised reasoning can
authorize; defense in depth adds complementary barriers. Permission-separated safe
outputs mediate proposed effects, but authorized content can still be harmful or
wrong, and detection is an additional analysis layer rather than proof of safety. [S1] [S2]

**Delta/distinctions.** The new default runtime profile is rootless and network-isolated;
this strengthens substrate isolation, not absolute safety. [F06] Keep draft PRs,
COMMENT-only reviews and **human merge as book policy**, not product impossibility:
opt-in merge capabilities exist, including an experimental gated merge output
that refuses default-branch merges. A tests-only prompt is not enforced file scope. [S2] [F05]

**Implemented in gh-aw by:** safe outputs, draft/review constraints, file protections,
strict validation, runtime profiles, firewall and threat detection.

## C. Admission/noise controls ≠ budget reservation or concurrency

**Chapters:** `ch04-triggers`, `ch09-continuous-triage-and-docs`,
`ch10-continuous-review-and-testing`, `ch13-governance-and-finops`.

**Definition/problem.** Admission decides whether an event merits agent work,
reducing redundant activity. It does not itself serialize competing executions or
enforce a resource ceiling; concurrency and proxy budget enforcement have separate
scopes. [S3] [S5]

**Delta/distinctions.** New cooldown measures from completion of a run whose agent
started, including failure; skipped agents do not reset it. **History lookup failure
fails open.** Stack filtering now defaults to the top PR. Preserve reactive versus
proactive framing; the claim that every recompile resets a stop deadline is an
erratum, not a new scheduling principle. [S3] [F02]

**Implemented in gh-aw by:** enhanced trigger filters, cooldown, stack filtering,
stop-time preservation/refresh, Actions concurrency and AWF credit enforcement.

## D. Portable intent ≠ interchangeable security contracts

**Chapters:** `ch02-your-first-workflow`, `ch05-engines`,
`ch07-defense-in-depth`, `ch08-tools-and-mcp`, `ch10-continuous-review-and-testing`.

**Definition/problem.** Portable intent lets teams reuse a task description and
governed-output pattern without promising identical runtime behavior. Repository
authority, provider authentication, billing entitlement, tools, models and network
paths require separate review when selecting an engine. [S4] [F04]

**Delta/distinctions.** “Change the engine and secret” is an overclaim. The target
rejects strict Codex command allowlists that Codex cannot enforce; choose a supporting
engine rather than silently widening shell access. [F08] Direct provider egress is
now explicit opt-in, distinct from inference through the AWF proxy. MCP process,
container and remote transports also have different trust boundaries. [F07] [F08]

**Implemented in gh-aw by:** engine capability diagnostics, authentication/billing
configuration, tools/MCP gateway, network policies and inference proxy.

## E. Reuse distributes reviewed dependencies, not automatic updates

**Chapters:** `ch03-anatomy-and-compile-model`, `ch11-reuse-and-memory`,
`ch13-governance-and-finops`, `ch14-fleets-and-adoption`.

**Definition/problem.** Reuse makes shared intent reviewable and maintainable across
consumers. Imports compose workflow configuration/context; native skills install
task guidance; experimental Agent Plugins integrate through engines; APM is an
independently versioned package-management integration—not another name for these
gh-aw mechanisms. [S5] [F10]

**Delta/distinctions.** Native skills/plugins and composable packages expand
distribution. Pinned/vendored consumers still require deliberate dependency updates,
recompilation and deployment; a central edit does not propagate automatically.
Configuration composition is not runtime prompt loading or complete lock inlining.
Skill resolution can preserve an unpinned ref with a warning; plugin resolution
failure is fatal. Keep APM policy guarantees independently evidenced. [S5] [F10] [F15]

**Implemented in gh-aw by:** imports/inlining, skills, Agent Plugins, package
manifests, source tracking/reviewed consumer updates and APM integration.

## F. Persistence and observability have lifecycles

**Chapters:** `ch07-defense-in-depth`, `ch09-continuous-triage-and-docs`,
`ch11-reuse-and-memory`, `ch12-observability-and-debugging`.

**Definition/problem.** Persistence carries selected state across runs, while
observability preserves evidence for diagnosis and accountability. Repository memory,
cache entries, uploaded artifacts and downloaded audit data have different retention,
filtering and deletion boundaries—not a permanent, complete transcript. [F11] [F12] [S6]

**Delta/distinctions.** Memory filters now precede validation/persistence and can
remove stale files after policy changes; custom validators add reviewed data
contracts. Cache inactivity eviction is not guaranteed lifetime; artifact retention
is not cache lifetime; shared policy does not share repository memory. [F11]
Redaction/minimal packaging reduce exposure, not eliminate leakage. Logs/audit
storage/API budgets limit evidence collection, not inference. `noop` means no work;
`report_incomplete` now fails conclusion rather than reporting success. [S6] [F07] [F12]

**Implemented in gh-aw by:** repo/cache memory, persistence filters/validation,
artifact packaging/redaction, logs/audit/OTLP and explicit completion outcomes.

## G. Scoped budgets and forecasts ≠ a complete bill cap

**Chapters:** `ch05-engines`, `ch07-defense-in-depth`,
`ch13-governance-and-finops`, `ch14-fleets-and-adoption`.

**Definition/problem.** Budgets constrain defined resource paths; forecasts estimate
future usage from historical evidence. Main-agent inference, detection, Actions
compute and execution time are distinct, and the daily historical admission
threshold is not an atomic accounting reservation. [S1] [S7] [F13]

**Delta/distinctions.** Main-agent, detector and daily fallbacks are **unchanged** in
paired explorer evidence: “daily disabled by default” is an **erratum**, not a new
default. Changed surfaces include Copilot's `auto` fallback, model policy, forecast
maturity and repository-wide strict compilation; forecasts remain uncertain. [F03] [F13] [F14]
Overridable defaults resolve at different compiler/runtime stages. Repository strict
policy needs regenerated/deployed locks; supported runtime capability gates are
separate from defaults. [S5] [S7] [F14]

**Implemented in gh-aw by:** agent/detector credit budgets, daily guardrail, timeouts,
model policy/forecasting, repository strict policy and enterprise defaults/runtime gates.

## Author evidence boundary

Retain the [assessment limits](framework-delta.md#6-verification-limits-and-blockers):
no live runs/provider access, MCP/browser/OTLP execution or measured forecasts.
The book repository has **Issues disabled**; reference-context compilation does not
certify its issue-output deployment. Docker/scanners were unavailable; do not claim
runtime/image/scan coverage. Restricted-secret and memory-validator warnings require
deliberate review, not automatic approval. APM/remote-plugin integrations are not
runtime-certified; private-preview drive memory stays outside general recipes.
This brief neither changes examples nor supplies editorial acceptance.

## Sources

Tagged primary references actually re-inspected from the explorer's cached target
archive on **2026-09-16** (explorer fetch/inspection: **2026-09-15**):

- [S1 — Threat Detection][S1]
- [S2 — Safe Outputs: Pull Requests][S2]
- [S3 — Triggers][S3]
- [S4 — AI Engines][S4]
- [S5 — Frontmatter][S5]
- [S6 — Artifacts][S6]
- [S7 — Compiler Enterprise Environment Controls][S7]

**Artifact:** `content/research/updates/v0.88.7/theory-delta.md`.

[S1]: https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/threat-detection.md
[S2]: https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/safe-outputs-pull-requests.md
[S3]: https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/triggers.md
[S4]: https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/engines.md
[S5]: https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/frontmatter.md
[S6]: https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/artifacts.md
[S7]: https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/compiler-enterprise-environment-controls.md
[F01]: framework-delta.md#f01-compiler-contract-and-authoring-loop
[F02]: framework-delta.md#f02-trigger-admission-cooldown-and-stacked-prs
[F03]: framework-delta.md#f03-engines-model-selection-and-honest-portability
[F04]: framework-delta.md#f04-authentication-and-billing-are-explicit-configuration
[F05]: framework-delta.md#f05-safe-outputs-preserve-the-boundary-refine-its-claims
[F06]: framework-delta.md#f06-runtime-profiles-replace-legacy-sandbox-privilege-fields
[F07]: framework-delta.md#f07-network-detection-and-artifact-security-changes
[F08]: framework-delta.md#f08-tools-and-mcp-actual-enforcement-is-engine-dependent
[F10]: framework-delta.md#f10-imports-native-skills-and-experimental-plugins
[F11]: framework-delta.md#f11-memory-validation-filtering-and-persistence-scope
[F12]: framework-delta.md#f12-logs-audit-graders-and-honest-completion
[F13]: framework-delta.md#f13-finops-budgets-model-policy-and-forecasting
[F14]: framework-delta.md#f14-repository-strict-policy-versus-defaults-and-runtime-gates
[F15]: framework-delta.md#f15-fleet-distribution-and-package-boundaries
