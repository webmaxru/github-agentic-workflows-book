# Chapter 2 — "The 10-Minute Win: Your First Workflow" — Concept Brief

- **Chapter:** `ch02-your-first-workflow` (Part I — The Individual)
- **Objective (from `toc.yml`):** Install the `gh aw` CLI and ship a first working Repo Assistant that triages a new issue end to end.
- **Targets:** `gh aw` **v0.81.6** (Public Preview).
- **Prepared by:** theory-researcher · **Date:** 2026-07-01
- **Docs inspected:** `github.github.com/gh-aw` — Introduction (landing), How They Work, Security Architecture, Quick Start, FAQ — plus `githubnext.com/projects/continuous-ai`.
- **Depends on:** ch01, which owns the deep **outer-loop / Continuous AI** framing. This brief only gives a short on-ramp recap (Concept 5) and does **not** re-teach it.
- **Scope:** conceptual grounding only. CLI syntax and frontmatter fields belong to `gh-aw-explorer`; every `Implemented in gh-aw by:` line names capabilities **for the explorer to confirm** against v0.81.6.

---

## Concepts covered

1. **Issue triage as "judgment work"** — why triaging a new issue is a task that used to need a human, and why it's the ideal first agentic win (vs. deterministic CI/CD).
2. **The "overnight teammate" mental model** — an agentic workflow as a tireless teammate that owns one small recurring task; sets up the book's running example, the **Repo Assistant**.
3. **The authoring loop (conceptual)** — write intent in natural-language Markdown, then a compile step produces a normal, reviewable GitHub Actions workflow that runs on GitHub's infrastructure.
4. **"Safe by default" (preview)** — the agent gets no raw write access; its proposed writes (a comment, a label) are mediated. Introduced here; Chapter 6 owns the depth.
5. **On-ramp recap of the outer loop** — 2–3 sentences so the chapter stands alone without re-teaching ch01.

---

## 1. Issue triage as "judgment work"

**Definition.** Triaging a new issue — reading it, deciding whether it's a bug, feature request, or question, applying labels, asking for a missing reproduction, and routing it to the right area or person — is *judgment work*: it means inferring intent from unstructured natural language and choosing a context-dependent action rather than following a fixed rule. There is no lookup table that maps every possible issue to the "correct" response, which is precisely why the task historically needed a human maintainer.

**The problem it solves.** Maintainers are buried under unlabeled, under-specified issues; the backlog grows faster than any human can read it, and well-intentioned reports go stale. Triage is the canonical *first* agentic win because it is high-volume, low-stakes (a comment or a label is trivially reversible), and every action is human-reviewable — so the cost of an imperfect call is small and the throughput gain is large.

**Key distinctions.** Contrast with deterministic CI/CD: build, test, and release pipelines must be exactly reproducible and "do exactly what you tell them, every time, in the same way." [1] Triage is the opposite kind of task — one "where exact reproducibility doesn't matter, such as triaging issues, drafting documentation, researching dependencies, or proposing code improvements for human review." [2] So agentic workflows are **additive to** CI/CD, not a replacement for it. GitHub Next names this exact pattern **"Continuous Triage: Label, summarize, and respond to issues using natural language."** [3]

**Common misconceptions.**
- *"This replaces my CI."* No — agentic workflows are "100% additive"; deterministic pipelines stay unchanged. [2]
- *"The agent has to be right every time."* No — because outputs are low-stakes and reviewed, occasional misses are acceptable; the value is throughput on judgment tasks, not perfection.
- *"Triage means the bot decides unilaterally."* Continuous AI "often ... involve[s] human oversight and control"; the agent proposes, humans dispose. [3]

**Implemented in gh-aw by:** the AI **engine** (default: GitHub Copilot) interpreting the natural-language Markdown prompt; an **issue trigger** (`on:` issue events) that delivers the new-issue event; and the triage actions expressed as **safe outputs** (e.g. `add-comment`, `add-labels`). *(explorer to confirm exact trigger/field names for v0.81.6.)*

---

## 2. The "overnight teammate" mental model

**Definition.** An agentic workflow is best pictured as a tireless teammate that owns one small, recurring responsibility: it wakes on an event or a schedule, does its one job, proposes the result for review, and goes back to sleep. The book's running example — the **Repo Assistant** — is exactly this. It is modeled on GitHub Next's real "Repo Assist," a repository assistant that "label[s] issues, answer[s] questions, propose[s] fixes, and make[s] engineering improvements — all while the maintainer stays in control through pull request review." [4]

**The problem it solves.** Small, genuinely useful, repetitive collaboration tasks — triage, doc nits, stale-issue nudges — rarely rise to the top of a human's queue, so they simply don't get done. A dedicated teammate scoped to just that task closes the gap. GitHub frames the payoff directly: **"Wake up to ready-to-review repository improvements."** [1] An impact study of Repo Assist across 15 open-source repositories reported a **net reduction of 651 open issues and a median 9× increase in issue-closure and PR-merge velocity**, and identified the single most important factor as *how often human maintainers chose to act* on the agent's output. [4]

**Key distinctions.** One workflow = one teammate = one job. This differs from a general chat assistant you prompt ad hoc in your editor (inner loop): the teammate is *standing*, *event-driven*, and *narrowly scoped*. It also differs from a fully autonomous agent — the teammate *proposes* rather than acting with free rein; Continuous AI "centres on scripted 'agent-like' AI workflows ... not fully autonomous." [3]

**Common misconceptions.**
- *"One workflow should do everything."* Prefer narrow scope: start with one or two workflows and expand "as patterns emerge." [2]
- *"A teammate acting overnight is inherently risky."* Its authority is bounded by design (see Concept 4).
- *"It's magical autonomy."* It's a bounded, reviewable task-owner, not an unsupervised actor.

**Implemented in gh-aw by:** a single **agentic workflow file** (`.github/workflows/<name>.md` — YAML frontmatter + Markdown) with event/schedule **triggers**, running coding agents in **GitHub Actions**; the Repo Assistant is scaffolded/added through the `gh aw` CLI (e.g. `gh aw new`, or adding a sample workflow). *(explorer to confirm the scaffold command for v0.81.6.)*

---

## 3. The authoring loop (conceptual)

**Definition.** You author the workflow's *intent* in plain natural-language Markdown — what you want done, written as prose — and a **compile step** turns that intent into an ordinary, human-readable GitHub Actions workflow that runs on GitHub's own infrastructure. The Markdown is the editable **source of truth**; the compiled workflow is what actually runs, and you never hand-edit it. [5]

**The problem it solves.** Writing robust Actions YAML by hand is verbose and error-prone, while dropping a raw coding agent into a workflow gives you neither structure nor guardrails. Authoring intent in Markdown lowers the barrier — "Simple Markdown Files: Write automation in plain markdown instead of complex YAML" [1] — and the compile step re-adds the rigor: the generated workflow is a normal, reviewable Actions file you can read, diff, and commit. That combination is why shipping a first workflow is genuinely a ~10-minute task. [6]

**Key distinctions.** Two artifacts, one source of truth: the `.md` you write versus the compiled `.lock.yml` that GitHub runs — and you "commit both files." [5] The loop is conceptual and iterative: *express intent → compile → run → observe → refine the prose.* Editing the Markdown body changes behavior on the next run; changing configuration means recompiling (the precise mechanics are the explorer's). The mental model is the classic one: **intent goes in, an elaboration/compile step happens, a concrete workflow comes out.**

**Common misconceptions.**
- *"The Markdown is the thing that runs."* No — the compiled GitHub Actions workflow runs; the Markdown is source. [5]
- *"Compiling hides what happens."* The opposite: the compiled workflow is fully inspectable, and it's where security hardening is made explicit. [5]
- *"It's a hosted black box."* It runs as a standard GitHub Actions workflow inside your own repository. [1]

**Implemented in gh-aw by:** the `gh aw` CLI authoring loop — **`gh aw init`** (prepare the repo), **`gh aw new`** (scaffold a workflow), **`gh aw compile`** (`.md` → `.lock.yml`), and **`gh aw run`** (trigger it), with **`gh aw status`** to observe. *(explorer to confirm the exact commands/flags and default behavior for v0.81.6.)*

---

## 4. "Safe by default" (preview)

**Definition.** In gh-aw the agent does **not** get raw write access to your repository. By default the agent step runs **read-only**; anything it wants to change — post a comment, add a label — is expressed as a *proposed output* that is validated and then applied by a **separate, narrowly-scoped step**, not by the agent process itself. The agent proposes; a mediated boundary disposes. [7][2]

**The problem it solves.** A coding agent necessarily reads untrusted content (the text of a brand-new issue) and can be manipulated by prompt injection or hostile input. If that same agent held write credentials, a poisoned prompt could damage the repo directly. Mediating every write means that "even a fully compromised agent cannot directly modify repository state." [7] That property is exactly what makes it safe to let an "overnight teammate" act while you sleep.

**Key distinctions.** A read-only agent plus separated writes is *not* the same as granting the workflow broad `write` permissions. The docs are explicit: writes "require explicit safe outputs — limited, specific operations that are sanitized and applied in separate jobs — or explicit general `write` permissions (not recommended)." [2] The set of allowed actions is a **policy you declare**, not a capability the model can expand at will. [8]

**Common misconceptions.**
- *"The AI is clicking buttons in my repo."* No — it emits a structured request that a downstream, scoped step carries out. [7]
- *"Read-only means it can't do anything useful."* It can comment, label, and (later) open issues/PRs — all through the safe-output boundary. [8]
- *"Safe outputs are just a permission toggle."* They're a *mediation boundary* (validation/sanitization + a separate scoped job); the full mechanism — sanitization and threat detection — is **Chapter 6 / Chapter 7's** subject, previewed only here.

**Implemented in gh-aw by:** read-only-by-default agent **permissions** + the **`safe-outputs:`** block (for a first workflow, `add-comment` and `add-labels`), with writes performed in separate scoped jobs. *(Depth — sanitization, permission separation, threat detection — deferred to Chapter 6. explorer to confirm the first-workflow safe-output names.)*

---

## 5. On-ramp recap of the outer loop *(recap only — do not re-teach ch01)*

**Recap (2–3 sentences).** As Chapter 1 established, the *inner loop* is the fast, interactive coding you do in your editor, while the *outer loop* is the repository's ongoing collaborative life — issues, PRs, reviews, releases — that keeps moving after you close the laptop. GitHub Next's **Continuous AI** is the idea of applying AI to that outer loop the way CI/CD automated integration and deployment [3]; **gh-aw is how you do it**, by running coding agents on repository events inside GitHub Actions. [5] Your first workflow is simply the smallest slice of that outer loop — one new issue, triaged — handed to a standing agent.

**Implemented in gh-aw by:** *(introduced in ch01)* event- and schedule-driven **triggers** that run **coding agents in GitHub Actions**, under the **Continuous AI** umbrella.

---

## Theory → gh-aw capability handoff *(for `gh-aw-explorer` to confirm on v0.81.6)*

| Concept | Capability the chapter should link to |
|---|---|
| 1 — Triage as judgment work | AI **engine** (default **Copilot**) interpreting Markdown; **issue trigger** (`on:`); triage **safe-outputs** (`add-comment`, `add-labels`) |
| 2 — Overnight teammate (Repo Assistant) | one **agentic workflow file** (frontmatter + Markdown) + **triggers** on GitHub Actions; scaffolded via `gh aw new` / sample add |
| 3 — Authoring loop | `gh aw init` → `gh aw new` → `gh aw compile` (`.md` → `.lock.yml`) → `gh aw run`; observe with `gh aw status` |
| 4 — Safe by default (preview) | **read-only** default permissions + **`safe-outputs:`** (`add-comment`, `add-labels`); full model deferred to ch06/ch07 |
| 5 — Outer-loop recap | (ch01) event/schedule **triggers** running **coding agents in GitHub Actions**; **Continuous AI** |

**Author guidance:** every capability above must be introduced only *after* the concept it implements (no orphan features), per the content conventions. Keep Concept 4 a preview and link forward to Chapter 6 ("Safe Outputs") and Chapter 7 ("Defense in Depth").

---

## Sources

Primary pages actually consulted (fetched 2026-07-01):

- **[1]** GitHub Agentic Workflows — landing / Introduction ("Wake up to ready-to-review repository improvements"; "augment your existing, deterministic CI/CD"; "Simple Markdown Files") — https://github.github.com/gh-aw/
- **[2]** FAQ — Determinism ("100% additive"; "where exact reproducibility doesn't matter, such as triaging issues …") and Guardrails ("read-only by default"; writes "require explicit safe outputs") — https://github.github.com/gh-aw/reference/faq/
- **[3]** GitHub Next — Continuous AI ("Continuous Triage: Label, summarize, and respond to issues"; task characteristics incl. *event-triggered*; "not fully autonomous ... human oversight and control") — https://githubnext.com/projects/continuous-ai/
- **[4]** GitHub Next — *The Impact of Automated Repository Maintenance Assistance* (Repo Assist impact report, 2026-05-14): "across 15 open source repositories… 651 issues net" reduction; "Issue closure and PR merge velocity both increased by a median of 9×"; "throughput is gated by human decision-making" — https://github.com/githubnext/repo-assist-impact/blob/main/report.md (verified 2026-07-01)
- **[5]** How They Work ("Traditional workflows ... do exactly what you tell them, every time, in the same way"; `.md` is "the editable source of truth, while `.lock.yml` is the compiled GitHub Actions workflow"; "Commit both files"; Copilot is the default engine) — https://github.github.com/gh-aw/introduction/how-they-work/
- **[6]** Quick Start ("Estimated time: 10 minutes"; "install something that will run automatically, recurringly, in the context of your repository") — https://github.github.com/gh-aw/setup/quick-start/
- **[7]** Security Architecture — Safe Outputs / permission isolation ("the agent never has direct write access to external state"; "even a fully compromised agent cannot directly modify repository state") — https://github.github.com/gh-aw/introduction/architecture/
- **[8]** How They Work — Safe Outputs ("Pre-approved actions the AI can request without write permissions") — https://github.github.com/gh-aw/introduction/how-they-work/

Deeper references (quoted within the pages above; for the author to cite directly if they go deeper):
- Repo Assist impact report — https://github.com/githubnext/repo-assist-impact/blob/main/report.md
- Don Syme, "Start Your Day With Code That's Better" (the "wake up to better repos" framing) — https://dsyme.net/2026/03/08/start-your-day-with-code-thats-better/
- Don Syme, "Repo Assist: Crunching the Technical Debt with GitHub Agentic Workflows" — https://dsyme.net/2026/02/25/repo-assist-a-repository-assistant/

---

## Artifact

Written to: `content/research/ch02-theory.md`
