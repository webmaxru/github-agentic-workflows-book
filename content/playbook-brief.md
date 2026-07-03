# Book Brief — GitHub Agentic Workflows

The single source-of-truth scope for the book. The `playbook-architect` reads this to design the
chapter map; every other agent treats it as the north star.

## Subject
**GitHub Agentic Workflows (gh-aw)** — the product that lets you write AI-powered, agentic
automations for a GitHub repository as **natural-language Markdown workflows with YAML frontmatter**,
compiled into GitHub Actions (`*.lock.yml`) by the `gh aw` CLI extension. It is GitHub Next's first
step toward **Continuous AI** — the "third leg" of repository automation alongside CI and CD.

- Docs: https://github.github.com/gh-aw/
- Repo & source of truth for behavior: https://github.com/github/gh-aw
- Continuous AI (the umbrella idea): https://githubnext.com/projects/continuous-ai/

## The promise (what the reader walks away with)
By the end, a reader can look at their own repository, spot three tasks a tireless teammate could
own overnight, and **ship a governed agentic workflow that does them** — safely, cheaply, and
reviewably. We sell that outcome from page one, then earn it capability by capability.

The hook is a genuine shift, not a feature tour: CI/CD automates *deterministic* work; gh-aw
automates the *judgment* work that used to need a human — triaging an issue, drafting a fix, keeping
docs honest — while keeping people in control through review gates. That **"inner loop vs. outer
loop"** reframing is the spine of the whole book, and it is what makes gh-aw different from plain
GitHub Actions.

## Who it's for — two readers, one book
| Track | Reader | What they came for |
| --- | --- | --- |
| **Builder** | Developer / staff engineer comfortable with GitHub, Actions, and YAML | Author, compile, secure, debug, and ship workflows. |
| **Leader** | Team lead / EM / decision-maker | Why it matters, governance, cost/FinOps, rollout at scale. |

Every chapter serves both audiences with **"Builder"** and **"Leader"** margin callouts, so no one
wades through a page that isn't for them. Theory is always anchored before syntax — but theory is
framed as *the problem a real team feels*, never abstraction for its own sake.

## Narrative spine — the reader's journey
The book is a **maturity arc**: the reader grows from one workflow to a team practice to an
org-wide fleet. Stakes and audience rise part by part, so momentum never stalls.

- **Part I — The Individual (one workflow).** The 10-minute win, then the model underneath it:
  Markdown + frontmatter → `gh aw compile` → `.lock.yml`, the CLI authoring loop, triggers, engines.
- **Part II — The Team (safe, reviewed, patterned).** Safe Outputs and the security-you-get-for-free,
  then MCP tools, then a **Pattern Library** framed as **"Continuous X"** — Continuous Triage, Docs,
  Review, CI-Doctor, Testing, Refactoring — where each pattern is a mini-project that ships a real
  outcome.
- **Part III — The Organization (fleet at scale).** Shared components and repo memory, governance
  and policy, cost/FinOps, multi-repo fleets, and the enterprise adoption playbook.

Every capability enters the story **because the narrative needs it next**, never as a spec dump.
The `playbook-architect` owns the exact chapter map; this arc is what it must honor.

## The running example — one repo that grows up
A single **running example** threads the entire book: a repository assistant ("Repo Assistant") that
starts life as one triage workflow and matures into a governed, multi-repo fleet. Each new capability
joins the story as the assistant needs it, so the reader always meets *why* before *how* — and sees
compounding value instead of disconnected snippets.

## Real stakes — proof it works
Motivation comes from real adopters, not hypotheticals. Chapters open or close with short
**case-study boxes** drawn from verified users:
- **Customer voices** from the Public Preview launch — Home Assistant, CNCF, Carvana, Marks &
  Spencer, and Hud.io.
- **Adopter repositories** shipping real `.md`→`.lock.yml` workflows — e.g. `backend.ai-webui`
  (daily test-improver, e2e-healer), `euparliamentmonitor` (20+ agents), `clash-verge-rev` (a review
  agent cloned across 215+ repos), and `camunda` (CI cost analysis).
- **"Continuous X" patterns** distilled from the official *Agent Factory* series
  (https://github.github.com/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/).

## What makes it engaging (devices every chapter uses)
- **Outcome-first.** Lead with the result the reader wants; introduce syntax only to reach it.
- **The 10-minute win.** A real, shippable workflow lands before any deep theory.
- **Progressive disclosure.** One idea per step; the running example carries the through-line.
- **"When *not* to use this."** Honest guidance and pitfalls on every capability.
- **Security & cost notes inline.** Safe Outputs, permissions, network, and AI-credit impact are
  called out where each capability appears — never bolted on at the end.
- **Lineage sidebars.** Short "why this exists" notes (Continuous AI, the outer loop) for readers who
  want the *why behind the why*.
- **Captioned, compile-verified code.** Every workflow example states what it demonstrates and is
  proven to compile.

## Language & format
- Workflow examples are **Markdown files with YAML frontmatter** (`.github/workflows/*.md`),
  compiled with `gh aw compile`. Examples are verified at **compile time** (no secrets/live runs
  required unless explicitly demonstrating a run).
- Prose targets the official docs terminology; behavior claims are grounded by the
  `gh-aw-explorer` inspecting the real `gh aw` CLI and frontmatter schema, against a recorded version
  (current known latest: **v0.81.6**, Public Preview).

## Topics in scope (indicative — the architect refines these into chapters)
- **The thesis:** what agentic workflows are, the outer loop, and Continuous AI vs. plain Actions.
- **The model & loop:** Markdown + frontmatter → `.lock.yml`; the `gh aw` CLI (`init`, `new`,
  `compile`, `run`, `logs`, `audit`, `status`).
- **Triggers & engines:** `on:` events and the agentic engines (Copilot, Claude, Codex, Gemini).
- **Safe Outputs (`safe-outputs:`):** how agent writes (issues, PRs, comments) are gated safely.
- **The security model:** permissions, network firewall, Strict Mode, and sandbox isolation.
- **Tools & MCP (`tools:`):** giving workflows real, governed capabilities.
- **The Continuous-X pattern library:** triage, docs, review, CI-doctor, testing, refactoring.
- **Reuse & memory:** shared components (`imports:`), agent dependencies via APM (`shared/apm.md`), and repo memory.
- **Trust & operate:** reviewing, debugging (`gh aw logs` / `gh aw audit`), human-in-the-loop.
- **Scale for leaders:** governance and policy, cost & FinOps (AI Credits, token efficiency),
  agent-dependency governance (APM: pinning, allowlists, isolation), multi-repo fleets, and an
  enterprise adoption playbook.

## Out of scope
- Building or teaching Microsoft Agent Framework, LangChain, or other agent SDKs.
- Provider/model internals beyond how gh-aw selects and configures an engine.
- Deep GitHub Actions tutorials (assumed as reader background, not taught from scratch).

## Non-negotiables
- **Motivate before you mechanize.** Every capability opens with the real problem it solves — and,
  where possible, a real adopter who felt it.
- **Theory before API.** Anchor every capability to a concept introduced first.
- **Serve both readers.** Each chapter earns its keep for Builders *and* Leaders.
- **Verify before ship.** Every example must `gh aw compile` cleanly (or be clearly marked as
  needing a live run/secret).
- **No secrets in content.** Engine keys live in Actions secrets, never in the book.
- **Version-aware.** Record the inspected `gh aw` version in research/verification artifacts.
