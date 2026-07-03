# Book Outline — GitHub Agentic Workflows

**Status:** Designed by `playbook-architect`. Targets **gh aw v0.81.6 (Public Preview)**.
Mirrored into the machine-readable [content/toc.yml](toc.yml) that drives `site/generate.py`.

## Learning progression

The book is a **maturity arc** told through one running example — the **"Repo Assistant"**, a
repository teammate that starts as a single triage workflow and grows into a governed, multi-repo
fleet. The spine is the **inner loop vs. outer loop** reframing: CI/CD automates *deterministic*
work; gh-aw automates the *judgment* work (triaging, drafting, keeping docs honest) on repo events,
with humans on the review gate. Every capability enters **theory-first** — anchored to a concept and
to the problem a real team feels — and only then to syntax, so no feature is an orphan. **Part I**
grows the reader from zero to one shipped workflow; **Part II** makes that workflow safe, tooled, and
patterned into a team practice; **Part III** scales the practice into an org-wide, observed, budgeted
fleet. Each chapter serves both a **Builder** (author/secure/debug/ship) and a **Leader** (why it
matters, governance, cost, rollout) through margin callouts.

## Chapter map

| # | Part | Lean | Title | Objective (reader can…) | gh-aw capabilities | Depends on |
|---|------|------|-------|-------------------------|--------------------|------------|
| 1 | I | Both | What Are Agentic Workflows? | Explain the outer loop and when to reach for gh-aw over plain Actions | Continuous AI; inner/outer loop; NL Markdown workflows; gh-aw vs Actions | — |
| 2 | I | Builder | The 10-Minute Win: Your First Workflow | Install `gh aw` and ship a Repo Assistant that triages an issue | `gh aw init/new/compile/run`; Copilot engine; safe-outputs (previewed) | 1 |
| 3 | I | Builder | Anatomy & the Compile Model | Read frontmatter+Markdown, run the compile loop, understand `.lock.yml` | file format; `gh aw compile`; `.lock.yml`; `gh aw status`; authoring loop | 2 |
| 4 | I | Builder | Triggers: When Workflows Wake Up | Choose `on:` events so the assistant runs at the right moments | triggers (`on:`); issues/PR; schedule; `workflow_dispatch`; command; `workflow_run` | 3 |
| 5 | I | Builder | Engines: Choosing the Agent's Brain | Select and configure Copilot/Claude/Codex/Gemini | `engine:`; Copilot/Claude/Codex/Gemini; model selection | 4 |
| 6 | II | Both | Safe Outputs: Acting Without Overreach | Let the assistant write via the sanitized `safe-outputs` boundary | `safe-outputs:`; create-issue; add-comment; create-pull-request; add-labels | 4, 5 |
| 7 | II | Both | Defense in Depth: Permissions, Firewall & Strict Mode | Harden a workflow to least privilege with egress control | `permissions:`; `network:` firewall; strict mode; sandboxing; threat model | 6 |
| 8 | II | Builder | Tools & MCP: Real Capabilities, Governed | Add governed capabilities via `tools:` and MCP servers | `tools:`; MCP servers; MCP gateway; built-in tools; tool permissions | 7 |
| 9 | II | Both | Continuous Triage & Docs: Reading the Room | Ship the Triage and Docs patterns as mini-products | Continuous Triage; Continuous Docs; scheduled+event triggers; agentics samples | 6, 8 |
| 10 | II | Both | Continuous Review, Testing & CI-Doctor | Close the quality loop with review/test/heal patterns | Review; Testing; CI-Doctor; Refactoring; `pull_request` triggers | 9 |
| 11 | III | Builder | Reuse & Memory: Shared Components and Repo Knowledge | Factor shared intent via `imports:` and add persistent memory | `imports:`; shared components; APM dependencies (`shared/apm.md`); memory/persistence; AGENTS.md | 10 |
| 12 | III | Both | Trust & Operate: Observability and Debugging | Inspect, debug, and audit runs to trust the fleet | `gh aw logs`; `gh aw audit`; OpenTelemetry; run summaries; HITL review | 11 |
| 13 | III | Leader | Governance & FinOps: Policy and Cost at Scale | Cap, meter, and gate agentic spend and set org policy | `max-ai-credits`; AI Credits; token efficiency; governance/policy; APM supply-chain governance (`apm-policy.yml`) | 12 |
| 14 | III | Leader | Fleets & Adoption: From One Repo to the Org | Scale into a governed multi-repo fleet with a rollout playbook | multi-repo fleets; dispatcher pattern; cross-repo composition; adoption playbook | 13 |

**Parts (maturity arc):** **Part I — The Individual** (chs 1–5) · **Part II — The Team** (chs 6–10) ·
**Part III — The Organization** (chs 11–14).

## Wave plan

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
