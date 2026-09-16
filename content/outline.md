# Book Outline — GitHub Agentic Workflows

**Status:** The original architecture was designed by `playbook-architect` against
**gh aw v0.81.6 (Public Preview)**. Its fourteen-chapter maturity arc and slugs are retained.
Current validated framework coverage is recorded in [FRAMEWORK_VERSION](FRAMEWORK_VERSION);
maintenance deltas and their evidence live under `content/research/updates/`.
The current machine-readable chapter contract is [content/toc.yml](toc.yml), which drives
`site/generate.py`.

## Learning progression

The book is a **maturity arc** told through one running example — the **"Repo Assistant"**, a
repository teammate that starts as a single triage workflow and grows into a governed, multi-repo
fleet. The spine is the **inner loop vs. outer loop** reframing: CI/CD automates *deterministic*
work; gh-aw automates the *judgment* work (triaging, drafting, keeping docs honest) on repo events,
with humans on the review gate. Every capability enters **theory-first** — anchored to a concept and
to the problem a real team feels — and only then to syntax, so no feature is an orphan. **Part I**
grows the reader from zero to one shipped workflow; **Part II** makes that workflow more constrained, tooled, and
patterned into a team practice; **Part III** scales the practice into an org-wide, observed, budgeted
fleet. Each chapter serves both a **Builder** (author/secure/debug/ship) and a **Leader** (why it
matters, governance, cost, rollout) through margin callouts.

## Chapter map

| # | Part | Lean | Title | Objective (reader can…) | gh-aw capabilities | Depends on |
|---|------|------|-------|-------------------------|--------------------|------------|
| 1 | I | Both | What Are Agentic Workflows? | Explain the outer loop and when to reach for gh-aw over plain Actions | Continuous AI; inner/outer loop; NL Markdown workflows; gh-aw vs Actions | — |
| 2 | I | Builder | The 10-Minute Win: Your First Workflow | Install `gh aw` and ship a Repo Assistant that triages an issue | `gh aw init/new/compile/run`; Copilot engine; safe-outputs (previewed) | 1 |
| 3 | I | Builder | Anatomy & the Compile Model | Read frontmatter+Markdown, run the compile loop, understand `.lock.yml` | file format; `gh aw compile`; `.lock.yml`; `gh aw status`; authoring loop | 2 |
| 4 | I | Builder | Triggers: When Workflows Wake Up | Choose events and bounded admission controls | triggers (`on:`); schedule; cooldown; stack filtering; stop-time refresh; command; `workflow_run` | 3 |
| 5 | I | Builder | Engines: Choosing the Agent's Brain | Select among five built-ins without assuming identical runtime contracts | `engine:`; Copilot/Claude/Codex/Gemini/Pi; CLI/model selection; identity/tool portability | 4 |
| 6 | II | Both | Safe Outputs: Acting Without Overreach | Let the assistant write through constrained mediated outputs | `safe-outputs:`; issue/comment/draft PR outputs; label provisioning; staged execution | 4, 5 |
| 7 | II | Both | Defense in Depth: Permissions, Firewall & Strict Mode | Reduce authority/exposure and explain residual risks | permissions; firewall; strict mode; runtime profiles; independent AI detection | 6 |
| 8 | II | Builder | Tools & MCP: Real Capabilities, Governed | Add capabilities with transport/engine-specific boundaries | tools; MCP gateway/transports; Bash enforcement; Playwright CLI | 7 |
| 9 | II | Both | Continuous Triage & Docs: Reading the Room | Ship the Triage and Docs patterns as mini-products | Continuous Triage; Continuous Docs; scheduled+event triggers; agentics samples | 6, 8 |
| 10 | II | Both | Continuous Review, Testing & CI-Doctor | Close the quality loop with review/test/heal patterns | Review; Testing; CI-Doctor; Refactoring; `pull_request` triggers | 9 |
| 11 | III | Builder | Reuse & Memory: Shared Components and Repo Knowledge | Reuse reviewed context and manage persistence lifecycles | imports; skills/plugins; independent APM integration; memory filtering/validation; deliberate updates | 10 |
| 12 | III | Both | Trust & Operate: Observability and Debugging | Investigate outcomes with bounded, incomplete evidence | logs/audit budgets; cached audits; OpenTelemetry; incomplete outcomes; HITL review | 11 |
| 13 | III | Leader | Governance & FinOps: Policy and Cost at Scale | Apply scoped budgets/policy without promising a total bill cap | agent/detector/admission budgets; models/forecasts; strict policy; defaults; APM governance | 12 |
| 14 | III | Leader | Fleets & Adoption: From One Repo to the Org | Roll out reviewed consumer/package updates across a fleet | multi-repo fleets; package includes/mappings; update semantics; adoption playbook | 13 |

**Parts (maturity arc):** **Part I — The Individual** (chs 1–5) · **Part II — The Team** (chs 6–10) ·
**Part III — The Organization** (chs 11–14).

## Original bootstrap wave plan

This is the initial production plan, not the maintenance procedure. For an existing book,
use `update-book.prompt.md`, the fixed-target impact map, and the accepted pilot before
widening. Independent authors can work in parallel; verification and review still gate
integration. Do not recreate stubs or scaffold over completed chapters.

Waves order **authoring** by risk and available source material; they are distinct from the reader's
part structure. Each chapter runs the standard pipeline: `theory-researcher` + `gh-aw-explorer` (in
parallel) → `chapter-author` → `code-verifier` → `chapter-reviewer` → `frontend-builder`.

| Wave | Chapters (ids) | Dispatch note |
|------|----------------|---------------|
| **0 — Pilot** | `ch02-your-first-workflow` | Single pilot that exercises **every** pipeline stage, including `code-verifier` (a real `.md → .lock.yml` compile). `ch01`'s thesis is stubbed as a one-paragraph on-ramp for the pilot, then fully authored in Wave 1. |
| **1 — Core model & loop** (most source, lowest risk) | `ch01-what-are-agentic-workflows`, `ch03-anatomy-and-compile-model`, `ch04-triggers`, `ch05-engines` | Richest official-docs + launch-blog coverage; low compile risk. Locks in the model, CLI, triggers, and engines that later waves build on. |
| **2 — The hard middle** (security & capability) | `ch06-safe-outputs`, `ch07-defense-in-depth`, `ch08-tools-and-mcp` | The security-heavy core: the sanitized write boundary, the defense-in-depth perimeter (permissions/firewall/strict mode), and governed tools/MCP — the groundwork that makes multi-workflow composition safe. Grounded in the security-architecture blog + `gh-aw-firewall`/`gh-aw-mcpg`. |
| **3 — Integration & scale** (needs cross-refs) | `ch09-continuous-triage-and-docs`, `ch10-continuous-review-and-testing`, `ch11-reuse-and-memory`, `ch12-observability-and-debugging`, `ch13-governance-and-finops`, `ch14-fleets-and-adoption` | Author last: each cross-references earlier capabilities. Order within the wave: patterns → reuse/memory → observe/debug → govern/FinOps → fleets/adoption. Grounded in the *Agent Factory* series, verified adopter repos, the token-efficiency blog, AI Credits, and `gh-aw-fleet`. |

**Pilot justification (one line):** `ch02` is the only candidate that drives a real `gh aw compile`,
so a green pilot proves the entire draft → verify → review → integrate loop — including the novel
compile/verify stage — before the team scales.

## Design guarantees

- **Theory before syntax.** `depends_on` forms a valid DAG (ch1→2→3→{4→5}→6→7→8→9→10→11→12→13→14);
  every capability is anchored to a concept introduced no later than the chapter that uses it.
- **Right-sized.** Each chapter is one focused topic with the fixed 6-section arc; the security model
  is split into safe-outputs (6), the defense-in-depth perimeter (7), and tools/MCP (8), and the
  six "Continuous X" patterns are split across chapters 9 and 10.
- **Dual audience.** The *Lean* column marks Builder- vs. Leader-weighted chapters; every chapter
  still carries both margin tracks.
- **Coverage.** Thesis/outer loop/Continuous AI (1); file format & CLI (2–3, 12); triggers (4);
  engines (5); safe-outputs (6); permissions/firewall/strict mode/sandbox (7); tools & MCP (8);
  Continuous-X patterns (9–10); imports & memory (11); observability (12); governance & FinOps (13);
  multi-repo fleets & enterprise adoption (14).
