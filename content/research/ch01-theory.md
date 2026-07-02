# Chapter 1 — "What Are Agentic Workflows?" — Concept Brief

- **Chapter:** `ch01-what-are-agentic-workflows` (Part I — The Individual)
- **Objective (from `toc.yml`):** Explain what an agentic workflow is, why the outer loop matters, and when to reach for gh-aw instead of plain GitHub Actions.
- **Targets:** `gh aw` **v0.81.6** (Public Preview).
- **Prepared by:** theory-researcher · **Date:** 2026-07-02
- **Docs inspected:** `github.github.com/gh-aw` — landing / Introduction, How They Work, Security Architecture — plus `githubnext.com/projects/continuous-ai`, the launch blog (`github.blog`), and the primary Repo Assist impact report (`github.com/githubnext/repo-assist-impact`).
- **Depends on:** nothing. This is the **foundational thesis chapter**: it *owns* the vocabulary (agentic workflow, inner/outer loop, Continuous AI, gh-aw-vs-Actions, safe-by-default) that every later chapter leans on. ch02's brief already treats these as an "on-ramp recap," so the definitions here must be the canonical, deep ones.
- **Scope:** conceptual grounding only. CLI syntax and frontmatter fields belong to `gh-aw-explorer`; every `Implemented in gh-aw by:` line names capabilities **for the explorer to confirm** against v0.81.6.

---

## Concepts covered

1. **Agentic workflow** — the precise definition: AI-powered, intent-driven repository automation authored as natural-language Markdown + YAML frontmatter, run by a coding agent in GitHub Actions on repository events, with every write mediated. Distinguished from a chatbot, an IDE assistant, a plain GitHub Actions job, and a fully autonomous unsupervised agent.
2. **Inner loop vs. outer loop** — the book's spine. Inner loop = fast, interactive coding in your editor; outer loop = the repository's ongoing collaborative life (issues, PRs, reviews, releases) that continues after you stop typing. Why CI/CD automated the *deterministic* outer-loop work but left the *judgment* work to humans.
3. **Continuous AI** — GitHub Next's umbrella concept: applying AI to the outer loop as a "third leg" alongside CI and CD. Its lineage, intent, and defining characteristics.
4. **gh-aw vs. plain GitHub Actions** — gh-aw *compiles to* Actions but adds three things Actions alone doesn't have: an agentic engine, a natural-language authoring surface, and a security model (safe outputs + sandbox). Actions is deterministic; gh-aw adds *governed judgment*. It is additive, not a replacement.
5. **Safe-by-default / human-in-the-loop (concept only)** — the agent proposes; humans review; writes are mediated. The read-only agent never touches repository state directly. Depth is deferred to Chapters 6–7; introduced here so the thesis lands honestly.

---

## 1. Agentic workflow

**Definition.** An agentic workflow is intent-driven repository automation that you author in plain Markdown — describing the outcome you want in natural language — with a block of YAML frontmatter that declares *when* it runs, *what* it may access, and *which* outputs it may produce; a coding agent then interprets that intent and carries out multi-step work inside GitHub Actions, and any change it wants to make to the repository is applied only through a mediated boundary. In GitHub's own words, they are "automated, intent-driven repository workflows that run in GitHub Actions, authored in plain Markdown and executed with coding agents." [5] The official glossary is precise about the "agentic" part: these are "workflows that have agency — the ability to make autonomous decisions [that] use AI to understand context, make decisions, and generate content by interpreting natural language instructions flexibly … combin[ing] deterministic GitHub Actions infrastructure with AI-driven decision-making." [2]

**The problem it solves.** A large class of genuinely useful repository work — triaging a new issue, keeping docs aligned with code, investigating a CI failure, drafting a test — is *repetitive* yet *not expressible as fixed rules*, so it has historically fallen to overloaded humans or gone undone. Traditional automation can't express it because "traditional workflows execute pre-programmed steps with fixed if/then logic … they do exactly what you tell them, every time, in the same way." [2] Agentic workflows fill exactly that gap: they "extend continuous automation to more subjective, repetitive tasks that traditional CI/CD struggle to express." [5] GitHub's mental model for fit is deliberately simple: "if repetitive work in a repository can be described in words, it might be a good fit for an agentic workflow." [5]

**Key distinctions.** An agentic workflow is:
- **not a chatbot or an IDE assistant** — those are interactive, on-demand, and human-driven turn by turn; an agentic workflow is *standing*, *event- or schedule-triggered*, and runs unattended in the repository. The impact report draws the same line: "Unlike one-shot AI coding assistants, Repo Assist runs autonomously on a schedule and in response to events." [6]
- **not a plain GitHub Actions job** — Actions runs deterministic scripted steps; an agentic workflow adds an AI engine that reasons over context. It also differs from *shelling a coding-agent CLI into a hand-written Actions YAML*, which "often grants these agents more permission than is required," whereas gh-aw runs "with read-only access by default and rel[ies] on safe outputs." [5] (Full contrast is Concept 4.)
- **not a fully autonomous, unsupervised agent** — it "create[s] an agent-only sub-loop that's able to be autonomous because agents are acting under defined terms," but "humans stay in the broader loop … pull requests are never merged automatically, and humans must always review and approve." [5]

**Common misconceptions.**
- *"It's a smarter chatbot in my repo."* No — the interaction model is inverted: it wakes on an event, does one job unattended, and proposes a result for review.
- *"It replaces my CI/CD."* No — it is designed "to augment existing CI/CD rather than replace it," and its use cases "largely do not overlap with deterministic CI/CD workflows." [5]
- *"It runs wild once installed."* No — it acts within boundaries you declare, and its writes are mediated and reviewed (Concept 5).
- *"Any repetitive task is a fit."* Only tasks *describable in words* where exact reproducibility isn't required; build/test/release stay in deterministic CI/CD. [5]

**Implemented in gh-aw by:** the **agentic workflow file** (`.github/workflows/<name>.md` = YAML frontmatter + natural-language Markdown body); the AI **engine** (default **GitHub Copilot**; also Claude, Codex, Gemini) that interprets the prompt [2]; **triggers** (`on:`) that bind it to repository events; **safe-outputs** that mediate its writes; all running as **coding agents in GitHub Actions**, authored/compiled with the `gh aw` CLI (`gh aw compile` → `.lock.yml`). *(explorer to confirm exact field/engine names for v0.81.6.)*

---

## 2. Inner loop vs. outer loop

**Definition.** The **inner loop** is the fast, interactive, individual work you do at your desk — editing, running, and debugging code in your editor, minute to minute. The **outer loop** is the repository's slower, collaborative life that surrounds and outlives any one editing session: issues filed, pull requests opened and reviewed, discussions, releases, CI results, and docs that drift out of date. CI/CD already automated the *deterministic* parts of that outer loop (integrate, build, test, deploy); what remained were the *judgment* tasks — reading an unstructured issue, deciding what a change should be, keeping prose honest — which stayed manual because no fixed rule captures them. *(Terminology note: "inner loop / outer loop" is this book's framing. GitHub Next frames the same split as AI "for collaboration, not just individual productivity." [4] The book adopts the widely-used inner/outer-loop labels to name it.)*

**The problem it solves.** Individual AI productivity (the inner loop) has advanced quickly, but GitHub Next observes that it "can shift burdens to other team members, or to later stages in software projects" — faster code generation produces more to review, triage, document, and maintain. [4] Continuous AI is therefore "about the collective impact of AI on software projects," using AI "to enhance collaboration in software projects, not just individual productivity." [4] The outer loop matters because that is where a team's real throughput is won or lost — and, empirically, where it stalls: the Repo Assist study frames repositories as "human-agent software factories" and shows "throughput is gated by human decision-making." [6]

**Key distinctions.**
- **Inner vs. outer:** inner = interactive, synchronous, one person, in the editor; outer = standing, asynchronous, collaborative, in the repository. Agentic workflows target the *outer* loop.
- **Deterministic outer-loop work vs. judgment outer-loop work:** CI/CD owns the first (reproducible pipelines that "do exactly what you tell them, every time" [2]); agentic workflows address the second ("more subjective, repetitive tasks that traditional CI/CD struggle to express" [5]).
- **Individual productivity vs. collaboration:** the distinction GitHub Next draws directly — "not just individual productivity." [4]

**Common misconceptions.**
- *"The outer loop is just CI/CD."* CI/CD automates the *deterministic* slice; the judgment slice (triage, docs, review) was left to humans — that's the gap this book is about.
- *"This is about making me type faster."* No — it's about the repository's collaborative throughput, which is a team-level, outer-loop concern. [4]
- *"Outer-loop automation means humans step back."* The opposite: outcomes correlate with *how often humans act* on the agent's output. [6]

**Implemented in gh-aw by:** the whole product is *oriented at the outer loop* — event- and schedule-driven **triggers** (`on:` issues, pull_request, schedule, …) that run **coding agents in GitHub Actions** at outer-loop moments, under the **Continuous AI** umbrella (Concept 3). *(explorer to confirm the trigger surface for v0.81.6; ch04 owns triggers in depth.)*

---

## 3. Continuous AI

**Definition.** **Continuous AI** is GitHub Next's name for "all uses of automated AI to support software collaboration on any platform." [4] It is deliberately named to parallel CI/CD: "Just as CI/CD transformed software development by automating integration and deployment, Continuous AI covers the ways in which AI can be used to automate and enhance collaboration workflows." [4] Crucially, it is "a category, rather than any single tool" — "not a term GitHub owns, nor a technology GitHub builds," but a frontier GitHub Next is "introducing to the industry." [4] The launch blog positions gh-aw as the concrete way to practice it: agentic workflows are introduced "as a third leg to augment CI/CD: Continuous AI." [4][5]

**The problem it solves.** As AI enters software collaboration, teams need a *shared frame* for governing it the way CI/CD gave the industry a shared frame for integration and deployment. Continuous AI supplies that frame — a vocabulary, a set of design principles, and named patterns — while insisting on control: "Teams and organisations must be in control of the Continuous AI they use: the models and automations used, how they are invoked, and how they integrate with their workflows." [4] GitHub Next expects it to be durable, "a story that runs for 30+ years at GitHub, just like CI/CD." [4]

**Key distinctions.**
- **Continuous AI (the category) vs. gh-aw (a tool):** Continuous AI is the umbrella idea; gh-aw is one implementation of it. [4]
- **Continuous AI vs. CI/CD:** additive third leg, not a replacement — it augments deterministic pipelines rather than overlapping them. [5]
- **Defining task characteristics (GitHub Next's list):** Continuous AI tasks are *automatable, repetitive, collaborative, integrated, auditable, event-triggered,* and admit *many variants.* [4] Named examples include **Continuous Documentation, Continuous Triage, Continuous Code Improvement, Continuous Summarization, Continuous Fault Analysis, Continuous Quality,** and **Continuous Accessibility.** [4]
- **Lineage:** a GitHub Next project first published **June 2025** (the "Introducing Continuous AI" post, Jun 19 2025), authored by Eddie Aftandilian, Peli de Halleux, Russell Horton, and Don Syme. [4]

**Common misconceptions.**
- *"Continuous AI is a GitHub product."* No — it's an open, industry-wide *category*; most Continuous AI tech is expected to be third-party/OSS. [4]
- *"It means fully autonomous agents."* No — it "more often centres on scripted 'agent-like' AI workflows … not fully autonomous, but rather involve human oversight and control." [4]
- *"It's individual-productivity tooling."* No — its whole point is *collaboration* ("not just individual productivity"). [4]

**Implemented in gh-aw by:** gh-aw is GitHub's vehicle for practicing Continuous AI — "GitHub Agentic Workflows hosts coding agents in GitHub Actions … This enables Continuous AI." [2] Concretely, the named "**Continuous X**" patterns become individual **agentic workflows** (trigger + engine + safe-outputs). *(explorer to confirm the pattern/gallery names for v0.81.6; Part II's pattern library owns these in depth.)*

---

## 4. gh-aw vs. plain GitHub Actions

**Definition.** gh-aw does not replace GitHub Actions — it **compiles to** it. You author intent in a Markdown `.md` file; `gh aw compile` turns it into an ordinary, security-hardened GitHub Actions workflow (`.lock.yml`) that GitHub runs. "The `.md` file is the editable source of truth, while `.lock.yml` is the compiled GitHub Actions workflow with security hardening. Commit both files." [2] What gh-aw *adds* on top of Actions is three things Actions alone lacks: (1) an **agentic engine** that reasons over context instead of following fixed if/then steps, (2) a **natural-language authoring surface** (Markdown intent instead of hand-written YAML logic), and (3) a **security model** (read-only-by-default agent + safe outputs + sandbox/firewall). Actions gives you deterministic execution; gh-aw layers *governed judgment* on top.

**The problem it solves.** Two naive alternatives both fail. Hand-writing Actions YAML can't express judgment tasks — it "do[es] exactly what you tell [it], every time, in the same way." [2] Dropping a raw coding-agent CLI into a hand-written Actions job *can* reason, but "often grants these agents more permission than is required for a specific task." [5] gh-aw resolves the tension by keeping Actions as the substrate — "agentic workflows run on GitHub Actions because that is where GitHub provides the necessary infrastructure for permissions, logging, auditing, sandboxed execution, and rich repository context" [5] — while adding the engine, the Markdown surface, and the guardrails so agents run "with read-only access by default and rel[y] on safe outputs … providing tighter constraints, clearer review points, and stronger overall control." [5]

**Key distinctions.**
- **Deterministic vs. adaptive:** traditional Actions = fixed steps; agentic workflows "use AI to understand context, make decisions, and generate content … adapting their behavior based on the specific situation they encounter." [2]
- **Additive, not a replacement:** gh-aw is "designed to augment existing CI/CD rather than replace it"; use cases "largely do not overlap." [5] Keep build/test/release in deterministic Actions.
- **gh-aw vs. "agent CLI inside raw Actions YAML":** same engine power, but gh-aw adds least-privilege defaults, the safe-outputs boundary, and clearer review points. [5]
- **Two artifacts, one source of truth:** you edit the `.md`; the `.lock.yml` is generated and runs. [2]

**Common misconceptions.**
- *"gh-aw is a competitor to / replacement for Actions."* No — it *is* Actions underneath; it compiles to a normal workflow file. [2]
- *"It's a hosted black box."* No — it runs as a standard, inspectable Actions workflow inside your own repository. [2][5]
- *"Adding AI means giving up Actions' guarantees."* No — you keep Actions' permissions, logging, auditing, and sandboxing, and gain guardrails on top. [5]

**Implemented in gh-aw by:** **`gh aw compile`** (`.md` → `.lock.yml`, compiling to Actions) [2]; the **`engine:`** field (the agentic engine) [2]; the **natural-language Markdown body** (authoring surface); and the **safe-outputs + read-only permissions + sandbox/firewall** security layer [1][3] — every piece additive to the existing GitHub Actions substrate. *(explorer to confirm exact commands/fields for v0.81.6; ch03 owns the compile model, ch05 the engines.)*

---

## 5. Safe-by-default / human-in-the-loop *(concept only — depth in ch06/ch07)*

**Definition.** In gh-aw the agent runs **read-only by default** and has **no direct write access** to your repository. Anything it wants to change — post a comment, add a label, open a PR — is expressed as a *proposed output* that is validated and then applied by a *separate, narrowly-scoped job*, not by the agent process itself. The official architecture is explicit: the SafeOutputs subsystem "enforc[es] permission isolation by ensuring that agent execution never has direct write access to external state … even a fully compromised agent cannot directly modify repository state." [3] On the landing page: "The agent can read repository state, but it cannot push commits or write to issues directly," and "requested actions are validated against your configured safe outputs policy before anything is applied." [1] Humans remain the deciders: "pull requests are never merged automatically, and humans must always review and approve." [5]

**The problem it solves.** A coding agent necessarily ingests untrusted content — the text of a brand-new issue, a comment, a PR body — and can be steered by prompt injection or hostile input. If that same agent also held write credentials, a poisoned prompt could damage the repository directly. Mediating every write is what makes it *safe* to let a standing agent act unattended in the outer loop; the guardrails are precisely what "make it practical to run agents continuously, not just as one-off experiments." [5] The Repo Assist data shows the human-in-the-loop gate working in practice: the agent opens **draft** PRs, and "684 of 877 RA PRs (78%) were marked ready by a maintainer" before any merge — a deliberate human approval step. [6]

**Key distinctions.**
- **Read-only agent + separated writes ≠ broad `write` permissions.** Writes go through "pre-approved, reviewable GitHub operations" (safe outputs), or explicit `write` scopes (not recommended). [5][2]
- **Propose vs. dispose.** The agent *proposes* a structured request; a downstream, scoped job *disposes* (applies) it after validation. [3]
- **Autonomy in a bounded sub-loop, humans in the broader loop.** Autonomous within declared terms; never merging on its own. [5]

**Common misconceptions.**
- *"The AI is clicking buttons in my repo."* No — it emits a structured request that a separate, permission-scoped job carries out. [3]
- *"Read-only means it can't do anything useful."* It can comment, label, and (later) open issues/PRs — all through the safe-output boundary. [1][2]
- *"Safe outputs are just a permissions toggle."* They're a *mediation boundary* (validation/sanitization + separate scoped jobs + threat detection); the full mechanism is Chapters 6–7's subject, previewed only here. [3]

**Implemented in gh-aw by:** **read-only-by-default permissions** + the **`safe-outputs:`** block (writes performed in separate scoped jobs) + a **threat-detection** gate, with the broader **sandbox/firewall/strict-mode** layers around it. [1][3] *(Depth — sanitization, permission separation, threat detection, network firewall, strict mode — deferred to Chapters 6–7. explorer to confirm the introductory safe-output names for v0.81.6.)*

---

## When agentic workflows fit — and when they don't *(grounding for the chapter's "fit / not-fit" section)*

**They fit when** the task is: describable in words ("if repetitive work in a repository can be described in words, it might be a good fit" [5]); *subjective/judgment-based and repetitive* ("more subjective, repetitive tasks that traditional CI/CD struggle to express" [5]); and where *exact reproducibility isn't the point* — triage, docs, reports, code review, test/coverage improvement. [4][5] Best practice is to "start with low-risk outputs such as comments, drafts, or reports before enabling pull request creation." [5]

**They don't fit when** the work is deterministic and must be identical every time — *build, test, release* pipelines. "Don't use agentic workflows as a replacement for GitHub Actions YAML workflows for CI/CD"; their use cases "largely do not overlap with deterministic CI/CD." [5] They also depend on human engagement to deliver value — where maintainers don't act on outputs, throughput stalls. [6]

---

## Worked-example grounding — reading the Repo Assistant's first mission

The chapter's worked example reads the running example's first workflow, `examples/ch02/repo-assistant-triage.md`, as a concrete embodiment of all five concepts: its **frontmatter** binds it to an outer-loop event (`on: issues: opened`), grants **read-only** access (`permissions: contents/issues: read`), names the **engine** (`engine: copilot`), and declares its mediated writes (`safe-outputs: add-comment`, `add-labels`); its **Markdown body** states the intent in plain language ("You are the Repo Assistant … triage it"). Reading it top-to-bottom lets the author show *agentic workflow* (Concept 1), *outer-loop trigger* (Concept 2), *Continuous Triage as Continuous AI* (Concept 3), *compiles-to-Actions* (Concept 4), and *safe-by-default* (Concept 5) in one artifact. The Repo Assistant is modeled on GitHub Next's real **Repo Assist**, whose impact report supplies the chapter's motivating numbers (below).

---

## Numbers used — verified against the ORIGINAL primary source *(statistic hygiene)*

> ⚠️ **Discrepancy flagged — use the report figures, not the landing-page blurb.** The "Related Posts" blurb on `githubnext.com/projects/continuous-ai/` summarizes Repo Assist as **"13 open source repositories … 578 issues closed, median 8× … 10× in PR merge velocity."** That blurb is an **outdated summary**. The **primary report's Executive Summary** (verified via both the GitHub blob view *and* the raw file) states **15 repositories / 651 issues net / median 9×** (both issue-closure and PR-merge). **Cite the report, not the blurb.** (This is the exact trap the ch-brief warned about — the earlier fabricated "13/578/8×" must not be reused.)

| Figure (as stated) | Exact quote | Primary source | Fetched |
|---|---|---|---|
| **15 open source repositories** | "across 15 open source repositories that adopted it in 2026" | Repo Assist impact report, Executive Summary — https://github.com/githubnext/repo-assist-impact/blob/main/report.md | 2026-07-02 (verified via blob + `raw.githubusercontent.com/githubnext/repo-assist-impact/main/report.md`) |
| **651 issues net** (reduction) | "The agent reduced open issue counts in every repository - 651 issues net." | Repo Assist impact report, Executive Summary — *same URL* | 2026-07-02 |
| **median 9×** (issue-closure *and* PR-merge velocity) | "Issue closure and PR merge velocity both increased by a median of 9× … (from 0.13 to 3.61 issues/week, and 0.34 to 5.63 PRs/week)" | Repo Assist impact report, Executive Summary + "Velocity" section — *same URL* | 2026-07-02 |
| **throughput gated by humans** (qualitative) | "demonstrates how throughput is gated by human decision-making" | Repo Assist impact report, Executive Summary — *same URL* | 2026-07-02 |
| **78% of draft PRs human-approved** (supports Concept 5) | "684 of 877 RA PRs (78%) were marked ready by a maintainer" | Repo Assist impact report, "Draft-to-Ready Approval" — *same URL* | 2026-07-02 |
| *(context, optional — defer to ch05/ch13)* **~2 premium requests/run** | "each workflow run typically incurs two premium requests: one for the agentic work and one for a guardrail check through safe outputs" | Launch blog, "Practical guidance for teams" — https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/ | 2026-07-02 |

Report metadata: *The Impact of Automated Repository Maintenance Assistance*, dated **May 14, 2026**, GitHub Next (lead author Don Syme et al.). Note the report's own headline uses "651 issues net"; per-repository appendix tables give finer breakdowns (e.g. all-15 net change −579 incl. new inflow, −511 excluding the large `dotnet/fsharp` outlier). For the chapter, quote the report's **headline** figures verbatim (15 / 651 net / median 9×) and attribute to the Executive Summary.

---

## Theory → gh-aw capability handoff *(for `gh-aw-explorer` to confirm on v0.81.6)*

| Concept | Capability the chapter should link to |
|---|---|
| 1 — Agentic workflow | **workflow file** (frontmatter + Markdown) + **engine** (default **Copilot**) + **triggers** (`on:`) + **safe-outputs**, run as **coding agents in GitHub Actions**; authored via `gh aw` CLI |
| 2 — Inner vs. outer loop | outer-loop **triggers** (`on:` issues / pull_request / schedule) running **coding agents in GitHub Actions** (whole-product orientation, not one feature) |
| 3 — Continuous AI | gh-aw as the vehicle for **Continuous AI**; the named **"Continuous X" patterns** implemented as workflows (trigger + engine + safe-outputs) |
| 4 — gh-aw vs. Actions | **`gh aw compile`** (`.md` → `.lock.yml`, compiles *to* Actions) + **`engine:`** + **natural-language Markdown** + **safe-outputs/permissions/sandbox** — additive to Actions |
| 5 — Safe by default / HITL | **read-only** default **permissions** + **`safe-outputs:`** (writes in separate scoped jobs) + **threat detection**; deep model deferred to ch06/ch07 |

**Author guidance:** every capability above must be introduced *after* the concept it implements (no orphan features), per the content conventions. Keep Concept 5 a preview and link forward to Chapter 6 ("Safe Outputs") and Chapter 7 ("Defense in Depth"). Because this is the entry-point chapter, define each term crisply enough that ch02–ch14 can reference it as settled vocabulary.

---

## Sources

Primary pages actually fetched (all fetched **2026-07-02**):

- **[1]** GitHub Agentic Workflows — landing / Introduction ("Wake up to ready-to-review repository improvements …"; "augment your existing, deterministic CI/CD with Continuous AI"; "Simple Markdown Files"; Guardrails: "Read-only token … cannot push commits or write to issues directly"; "Safe outputs gate … validated against your configured safe outputs policy before anything is applied") — https://github.github.com/gh-aw/
- **[2]** How They Work ("hosts coding agents in GitHub Actions … This enables Continuous AI"; "Agentic vs. Traditional Workflows" — traditional "do exactly what you tell them, every time, in the same way"; the "agency … make autonomous decisions … combine deterministic GitHub Actions infrastructure with AI-driven decision-making" glossary definition; ".md file is the editable source of truth, while .lock.yml is the compiled GitHub Actions workflow … Commit both files"; Copilot is the default engine; Safe outputs = "Pre-approved actions the AI can request without write permissions") — https://github.github.com/gh-aw/introduction/how-they-work/
- **[3]** Security Architecture — Safe Outputs / permission isolation ("agent execution never has direct write access to external state"; "even a fully compromised agent cannot directly modify repository state"; defense-in-depth layers: substrate / configuration / plan) — https://github.github.com/gh-aw/introduction/architecture/
- **[4]** GitHub Next — Continuous AI ("all uses of automated AI to support software collaboration"; "align with … CI/CD … Continuous AI covers the ways in which AI can be used to automate and enhance collaboration workflows"; "not a term GitHub owns, nor a technology GitHub builds … a category, rather than any single tool"; "AI for collaboration, not just individual productivity"; task characteristics incl. *event-triggered*; examples incl. *Continuous Triage/Documentation/…*; "not fully autonomous … human oversight and control"; "third leg to augment CI/CD"; "30+ years"; published Jun 2025; authors Aftandilian, de Halleux, Horton, Syme) — https://githubnext.com/projects/continuous-ai/
- **[5]** Launch blog — *Automate repository tasks with GitHub Agentic Workflows* (Don Syme & Peli de Halleux, Feb 13 2026): "automated, intent-driven repository workflows that run in GitHub Actions, authored in plain Markdown and executed with coding agents"; "describe the outcomes you want in plain Markdown … executes using a coding agent in GitHub Actions"; "augment existing CI/CD rather than replace it … do not overlap with deterministic CI/CD"; "run on GitHub Actions because that is where GitHub provides … permissions, logging, auditing, sandboxed execution, and rich repository context"; agent-CLI-in-raw-YAML "often grants … more permission than is required" vs. "read-only access by default and … safe outputs"; "pull requests are never merged automatically, and humans must always review and approve"; "if repetitive work … can be described in words, it might be a good fit"; "two premium requests" per Copilot run — https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/
- **[6]** GitHub Next — *The Impact of Automated Repository Maintenance Assistance* (Repo Assist impact report, May 14 2026): "across 15 open source repositories …"; "651 issues net"; "Issue closure and PR merge velocity both increased by a median of 9×"; "throughput is gated by human decision-making"; "Unlike one-shot AI coding assistants, Repo Assist runs autonomously on a schedule and in response to events"; "684 of 877 RA PRs (78%) were marked ready by a maintainer" — https://github.com/githubnext/repo-assist-impact/blob/main/report.md (cross-verified against raw: https://raw.githubusercontent.com/githubnext/repo-assist-impact/main/report.md)

Cross-references for the author (mentioned within the pages above; cite directly only if going deeper):
- Don Syme, "Repo Assist: Crunching the Technical Debt with GitHub Agentic Workflows" — https://dsyme.net/2026/02/25/repo-assist-a-repository-assistant/
- Don Syme, "Start Your Day With Code That's Better" (the "wake up to better repos" framing) — https://dsyme.net/2026/03/08/start-your-day-with-code-thats-better/
- GitHub Next — "Introducing Continuous AI" (lineage, Jun 19 2025) — https://githubnext.com/posts/dsyme-introducing-continuous-ai/

---

## Artifact

Written to: `content/research/ch01-theory.md`
