# Chapter 3 — "Anatomy & the Compile Model" — Concept Brief

- **Chapter:** `ch03-anatomy-and-compile-model` (Part I — The Individual)
- **Objective (from `toc.yml`):** Read any workflow's frontmatter + Markdown, run the
  compile-and-iterate loop, and understand what the generated `.lock.yml` contains.
- **Targets:** `gh aw` **v0.81.6** (Public Preview).
- **Prepared by:** theory-researcher · **Date:** 2026-07-02
- **Docs inspected (all fetched 2026-07-02):** `github.github.com/gh-aw` — About Workflows (overview),
  How They Work, Reference/Workflow Structure, Reference/Compilation Process, Guides/Editing Workflows,
  Reference/Glossary, Setup/CLI Commands.
- **Depends on:** ch02, which already shipped one workflow and introduced the authoring loop at a high
  level (`init → new → compile → run`) and *previewed* the compile step. This brief **opens the hood**:
  it deepens the compile model, the contents of the lock file, the determinism boundary, and the
  compile/status/run/iterate loop. It does **not** re-teach installation or the first-workflow scenario.
- **Scope:** conceptual grounding only. Exact CLI flags and frontmatter field syntax belong to
  `gh-aw-explorer`; every `Implemented in gh-aw by:` line names capabilities **for the explorer to
  confirm** against v0.81.6.

---

## Concepts covered

1. **Natural language as reviewable source** — a prose-plus-frontmatter Markdown file *is* the source
   of truth for the automation: version-controlled, diffable, and reviewed in a pull request exactly
   like code. Sometimes framed as "prompts as programs" / "natural language as source code."
2. **The compile model** — the `.md` source is turned into a deterministic `.lock.yml` artifact by a
   compiler (`gh aw compile`); the mental model is a *build step*, and the chapter explains **why** a
   compile step exists at all (portability, review, determinism, security hardening, SHA pinning).
3. **The determinism boundary** — the compiled GitHub Actions workflow is deterministic infrastructure;
   the single **agent step** is where non-determinism and judgment live. Understanding which parts are
   fixed vs. model-driven is the key mental model of the whole system.
4. **Two artifacts, one intent** — you author the `.md` and commit **both** the `.md` and the
   `.lock.yml`. Each has a job: you *edit the Markdown*, the *lock runs*, and you never hand-edit the
   lock.
5. **The authoring loop** — write → compile → (status) → run → iterate, a tight feedback cycle
   analogous to the code compile/test loop, with a fast path (edit the body, no recompile) and a slow
   path (change frontmatter, recompile).

---

## 1. Natural language as reviewable source

**Definition.** In gh-aw the unit of automation is a single Markdown file with two parts: a YAML
**frontmatter** block "enclosed between `---` markers" that carries configuration, and a **Markdown
body** of "natural language instructions for the AI." [1][2] That file is committed to
`.github/workflows/`, so the *intent itself* — written as prose — becomes the reviewable source of
truth, diffed and approved in a pull request the same way source code is. Instead of encoding logic as
`if issue has label X, do Y`, "you write 'analyze this issue and provide helpful context', and the AI
decides what's helpful based on the specific issue content." [3]

**The problem it solves.** Traditional automation hides its real intent inside verbose, opaque config
(hand-written Actions YAML, brittle `if/then` ladders) that few teammates can read or review well.
Making the *prose* the artifact lowers the barrier — automation is "written in markdown instead of
complex YAML" [3] — and, crucially, keeps the behavior **auditable**: a reviewer reads the same English
the agent will act on. This is the "prompts as programs" / "natural language as source code" idea,
stated in vendor terms as "the editable source of truth." [4]

**Key distinctions.**
- *Frontmatter vs. body.* Frontmatter is machine-facing configuration (triggers, permissions, tools);
  the body is human-facing natural-language instructions. The file "separat[es] technical
  configuration from natural language instructions." [1]
- *Source vs. what-runs.* The `.md` is source; it is **not** what GitHub executes directly (that's the
  compiled lock — Concepts 2 and 4).
- *Reviewable ≠ deterministic.* Prose being reviewable does not make the agent's *response*
  deterministic; it makes the *instruction* inspectable (contrast with Concept 3).

**Common misconceptions.**
- *"It's just a config file with a description field."* No — the Markdown body is the program's logic,
  expressed in natural language, and the agent interprets it at run time. [3]
- *"Prose can't be reviewed like code."* It can, and should be: the `.md` lives in version control and
  goes through PR review like any source file. [4][5]
- *"More prose = more precision."* Not necessarily; the docs advise "clear, specific instructions" and
  to "start simple and iterate," which is the loop of Concept 5. [2]

**Implemented in gh-aw by:** the **workflow file format** — a single `.md` in `.github/workflows/`
containing **YAML frontmatter** (between `---`) plus a **natural-language Markdown body**; the file is
committed and reviewed in pull requests. *(explorer to confirm the exact frontmatter/body split and
file-location rules for v0.81.6.)*

---

## 2. The compile model

**Definition.** A dedicated compiler turns the `.md` source into a complete, runnable GitHub Actions
workflow: "The `gh aw compile` command transforms a markdown workflow file into a complete GitHub
Actions `.lock.yml` by embedding frontmatter and setting up runtime loading of the markdown body." [6]
The official mental model is explicit: "Think of it like compiling code — you write human-friendly
markdown, the compiler produces machine-ready YAML." [7] Compilation is defined as "translating Markdown
workflows (`.md` files) into GitHub Actions YAML format (`.lock.yml` files), including validation, import
resolution, tool configuration, and security hardening." [8]

**The problem it solves.** A raw prose file cannot run on GitHub's infrastructure, and hand-writing the
hardened Actions YAML it would need is verbose, error-prone, and easy to get *insecurely* wrong. A
compile step buys four things at once: **portability** (the output is ordinary GitHub Actions YAML that
runs on existing infrastructure [9]), **review** (validation catches errors and unsafe choices before
they ship), **determinism** (the same source yields the same hardened artifact — Concept 3), and
**pinning/hardening** (the compiler applies security hardening and pins every action to an immutable
commit SHA — "tags can be moved, SHAs cannot" [6]). Compilation is local and fast — "Simple workflows
compile in ~100ms" [6] — which is what makes the loop of Concept 5 feel like a normal build.

**Key distinctions.**
- *Compile ≠ run.* Compilation validates, hardens, and emits YAML; it never calls an engine or touches
  GitHub. (Running is `gh aw run` / a live trigger — Concept 5.)
- *Five phases.* The compiler "runs five compilation phases (parsing, validation, job construction,
  dependency resolution, and YAML generation)." [6] The author needs the *idea* of a build pipeline, not
  the phase internals.
- *Compile ≠ hidden.* Compilation is the opposite of a black box: it *adds* inspectable structure
  (security hardening, an embedded dependency manifest, SHA-pinned actions) that a reader can audit. [6][8]

**Common misconceptions.**
- *"The Markdown runs directly."* No — the compiled `.lock.yml` runs; the `.md` is source. [4]
- *"Compiling is a packaging nicety."* It is the security and portability boundary: validation +
  hardening + action pinning happen here. [6][8]
- *"I should tweak the YAML the compiler produced."* Never hand-edit the lock; change the `.md` and
  recompile (Concept 4). [1]

**Implemented in gh-aw by:** **`gh aw compile`** (`.md` → `.lock.yml`), a local, offline, five-phase
compiler that validates, resolves imports, hardens, and **pins actions to SHAs**; `--watch` recompiles
on change; `gh aw validate` runs the compiler + linters without emitting files. *(explorer to confirm
flags/defaults — e.g. strict-by-default, `--no-emit`, `--watch` — for v0.81.6.)*

---

## 3. The determinism boundary

**Definition.** An agentic workflow is a hybrid: it "combine[s] deterministic GitHub Actions
infrastructure with AI-driven decision-making, adapting [its] behavior based on the specific situation
[it] encounter[s]." [2] The compiled `.lock.yml` is the deterministic half — a fixed set of GitHub
Actions jobs that always run the same way — and inside it, exactly **one step is non-deterministic**:
the **agent job**, where the engine reads context and exercises judgment. The determinism boundary is
the line between "fixed, compiled infrastructure" and "the model's runtime decision."

**The problem it solves.** Teams need to reason about *what is guaranteed* vs. *what is judgment*.
Traditional workflows "do exactly what you tell them, every time, in the same way" [2]; agentic
workflows deliberately add a step that does **not** — it interprets natural language "flexibly" and
"respond[s] flexibly to different scenarios without requiring explicit programming for each case." [3]
Drawing the boundary explicitly lets you place guarantees where they belong: scheduling, permissions,
job wiring, and (critically) *writes* stay deterministic and reviewable, while only the reasoning is
model-driven. The compiled pipeline enforces this — "AI reasoning (read-only) is separated from write
operations" [6] — so the unpredictable step is boxed in by predictable ones.

**Key distinctions.**
- *Deterministic scaffold vs. non-deterministic agent.* Everything the compiler emits (activation,
  detection, safe-output, conclusion jobs; SHA-pinned actions) is fixed; the agent's *output* is not.
- *Reproducible artifact vs. reproducible behavior.* The **compile** is reproducible — identical
  configuration yields identical hardened output, verified by a deterministic **frontmatter hash**
  "across the Go and JavaScript compiler implementations." [10] The **run** is not: the same prompt can
  yield different agent responses. Compile-time determinism is a property of Concept 2; run-time
  non-determinism is the essence of this concept.
- *Fixed inputs to the agent.* Even the agent step's *scaffolding* is deterministic (which tools,
  which permissions, which network egress); only the model's reasoning over those fixed inputs varies.

**Common misconceptions.**
- *"The whole thing is unpredictable because there's AI in it."* No — only the agent step is;
  triggers, permissions, and the write path are compiled, fixed, and auditable. [2][6]
- *"Deterministic compilation means deterministic answers."* No — a stable artifact does not imply a
  stable agent response; those are different layers. [2][10]
- *"You can't put guardrails around a non-deterministic step."* You can, and gh-aw does: the
  non-deterministic agent runs read-only and its proposed writes pass through separate, deterministic
  jobs (previewed in ch02's "safe by default"; owned by ch06/ch07). [6]

**Implemented in gh-aw by:** the compiled **`.lock.yml`** job graph (deterministic activation/agent/
detection/safe-output/conclusion jobs) with **SHA-pinned actions**; the **agent job** (the chosen
**engine**) as the single model-driven step; the **frontmatter hash** as the compile-determinism
signal. *(explorer to confirm the job names and the read-only agent boundary in a real v0.81.6 lock.)*

---

## 4. Two artifacts, one intent

**Definition.** One authored intent produces two committed files: "The `.md` file is the editable
source of truth, while `.lock.yml` is the compiled GitHub Actions workflow with security hardening.
Commit both files." [4] The lock is machine-generated and carries an explicit "This file was
automatically generated by gh-aw. **DO NOT EDIT.**" header [1]; at run time "GitHub Actions executes the
lock file using a coding agent while referencing the markdown for instructions." [8] You edit the `.md`;
the `.lock.yml` runs.

**The problem it solves.** Readers new to the model ask "which file do I change, and why are there two?"
The answer: the `.md` is where humans express and review intent; the `.lock.yml` is what the platform
can actually execute, with hardening and an auditable dependency manifest baked in. Committing **both**
gives reviewers transparency — they can diff the human intent *and* the exact machine artifact that will
run (including its "Secrets used" and "Custom actions used" manifests [1]) — while a clear "source vs.
generated" split prevents the anti-pattern of hand-tuning generated YAML that the next compile would
overwrite.

**Key distinctions.**
- *Edit target vs. run target.* Edit the `.md`; the `.lock.yml` runs. Never hand-edit the lock —
  "run `gh aw compile` or `gh aw update-actions` to regenerate." [6]
- *Generated ≠ ignored.* gh-aw commits the lock (and `gh aw init` configures `.gitattributes` to mark
  `*.lock.yml` as *generated* so diffs collapse) — that is **not** the same as gitignoring it. Best
  practice: "Always commit `.md` files" and "Also commit `.lock.yml` files for transparency." [11]
  *(Author caution: this book's own `examples/` may gitignore example lock files as a repo-hygiene
  choice for the code-verifier; do **not** teach readers to gitignore locks in their real repos — the
  gh-aw norm is commit-both.)*
- *Runtime coupling.* The lock doesn't inline the whole prompt to run it — it "load[s] the markdown
  body at runtime," so the two files stay linked at execution time. [7]

**Common misconceptions.**
- *"The lock file is a throwaway build output I shouldn't commit."* Commit it — it's how reviewers see
  the hardened, SHA-pinned artifact that will actually run. [4][11]
- *"If I hand-fix the lock, I'm done."* The next `gh aw compile` overwrites hand edits; fix the `.md`. [1]
- *"Two files means two sources of truth."* There is one source (`.md`); the lock is a *derived*
  artifact. [4][8]

**Implemented in gh-aw by:** the paired **`<name>.md` (source)** and **`<name>.lock.yml` (generated,
`DO NOT EDIT`)** in `.github/workflows/`; the lock's **header metadata + dependency manifest** ("Secrets
used", "Custom actions used"); `gh aw init`'s **`.gitattributes`** generated-marking; **commit both**.
*(explorer to confirm the lock header fields and the `.gitattributes` behavior on v0.81.6.)*

---

## 5. The authoring loop

**Definition.** Authoring a workflow is an iterative feedback cycle: **write** intent in the `.md`,
**compile** it to a lock, optionally check **status**, **run** it, observe, then **iterate** on the
prose. The docs frame the practice directly: "Start simple and iterate with clear, specific
instructions. Test workflows using `gh aw compile --watch` and `gh aw run`, monitor costs with
`gh aw logs`." [2] It is the agentic analogue of the classic code compile → test → refine loop.

**The problem it solves.** You rarely get the instructions right on the first try, so the model has to
support cheap iteration. gh-aw provides a **fast path and a slow path**: "the YAML frontmatter … is
compiled into the lock file and requires recompilation when changed, and the markdown body … is loaded
at runtime and takes effect on the next run. This lets you iterate on instructions quickly while keeping
security-sensitive configuration behind compilation." [12] In practice: tweak the *prose* → no recompile
needed; change *configuration* → recompile. The rule of thumb is "Edit the markdown body for instruction
changes. Recompile after any frontmatter change." [12]

**Key distinctions.**
- *Fast path vs. slow path.* Body edits take effect on the next run with no recompile; frontmatter
  edits "always require recompilation because they affect security-sensitive configuration." [12]
- *Compile vs. status vs. run.* `gh aw compile` produces the lock (offline); `gh aw status` "check[s]
  the current state of all workflows" (enabled/disabled, schedules, labels; with `--ref`, latest run
  status) [13]; `gh aw run` "execute[s] workflows immediately in GitHub Actions" [13]. (`gh aw list`
  is the quick, no-API sibling showing name/engine/**compilation status**. [13])
- *Loop, not one-shot.* The loop assumes repeated passes; `compile --watch` exists precisely to tighten
  it. [2]

**Common misconceptions.**
- *"Every change needs a recompile."* No — only frontmatter changes do; body/instruction edits don't. [12]
- *"`status` runs the workflow."* No — `status` only reports state; `run` triggers execution. [13]
- *"Iterating means editing the lock."* No — iterate on the `.md`; recompile if you touched
  frontmatter (Concept 4). [12]

**Implemented in gh-aw by:** **`gh aw compile`** (and `--watch`) for the build step; **`gh aw status`**
(and `gh aw list`) to observe compiled/enabled state; **`gh aw run`** to trigger; the **frontmatter-vs-
body recompilation rule** (recompile on frontmatter change; edit body freely). *(explorer to confirm
`status`/`list` columns and the `run` dispatch requirements for v0.81.6; note `run` is a live/secret
step, not compile-verified — per ch02.)*

---

## Theory → gh-aw capability handoff *(for `gh-aw-explorer` to confirm on v0.81.6)*

| Concept | Capability the chapter should link to |
|---|---|
| 1 — Natural language as reviewable source | **workflow file format**: `.md` = YAML **frontmatter** (`---`) + natural-language **Markdown body**; committed & PR-reviewed |
| 2 — The compile model | **`gh aw compile`** (`.md` → `.lock.yml`), five-phase local compiler; validation + hardening + **action SHA pinning**; `--watch`, `gh aw validate` |
| 3 — The determinism boundary | compiled **`.lock.yml`** deterministic job graph (SHA-pinned) vs. the single non-deterministic **agent job** (engine); **frontmatter hash** = compile determinism |
| 4 — Two artifacts, one intent | paired **`.md` (source)** + **`.lock.yml` (generated, `DO NOT EDIT`)**; lock header + dependency manifest; `.gitattributes` generated-mark; **commit both** |
| 5 — The authoring loop | **`gh aw compile`**(`--watch`) → **`gh aw status`** / `gh aw list` → **`gh aw run`** → iterate; recompile-on-frontmatter vs. edit-body-freely |

**Concept → chapter-section map** *(from `toc.yml` → ch03)*

| `toc.yml` section | Concept(s) it should carry |
|---|---|
| "Concept: natural language as reviewable source" | **1** |
| "In gh-aw: frontmatter + Markdown to `gh aw compile` to `.lock.yml`" | **2** + **4** (structure → compile → two artifacts) |
| "The authoring loop: compile, status, run, iterate" | **5** (with **3** framing "what's fixed vs. model-driven") |
| "Worked example: reading a compiled `.lock.yml` side by side" | **2/3/4** made concrete (header, jobs, SHA pins, embedded prompt) |
| "Recap & what's next" | recap all five; hand off to ch04 (Triggers) |

**Author guidance:** every capability above must be introduced only *after* the concept it implements
(no orphan features), per the content conventions. Keep the *depth* of the security jobs (detection,
safe-output isolation) as forward-links to ch06/ch07 — here they serve only to illustrate the
**determinism boundary** (Concept 3), not to teach hardening.

---

## Numbers used (statistic hygiene)

Every numeric claim in this brief, with its exact primary source and fetch date. No aggregated or
derived figures.

| Figure | Exact source wording | Primary URL | Fetched |
|---|---|---|---|
| **five** compilation phases | "The process runs five compilation phases (parsing, validation, job construction, dependency resolution, and YAML generation)." | https://github.github.com/gh-aw/reference/compilation-process/ | 2026-07-02 |
| **~100ms / ~500ms / ~2s** compile times | "Simple workflows compile in ~100ms; workflows with imports in ~500ms; workflows that resolve action SHAs dynamically in ~2s." | https://github.github.com/gh-aw/reference/compilation-process/ | 2026-07-02 |
| **v0.81.6** target version | Inspected CLI version recorded in ch02 verification (`gh aw version` → `v0.81.6`). | `content/research/ch02-features.md` (code-verifier artifact) | 2026-07-01 |
| **~100 KB** compiled lock (worked-example anchor, optional) | Empirical: `repo-assistant-triage.lock.yml` reported `✓ … (100.3 KB)` on `gh aw compile`. | `content/research/ch02-features.md` (verification) | 2026-07-01 |

*No external / third-party statistics are used in this chapter; all figures are gh-aw primary or the
book's own verified measurements.*

---

## Sources

Primary pages actually consulted (all fetched **2026-07-02** unless noted):

- **[1]** Reference — Workflow Structure ("Each workflow consists of: 1. YAML Frontmatter … 2. Markdown:
  Natural language instructions for the AI"; lock header "This file was automatically generated by
  gh-aw. DO NOT EDIT."; "Secrets used" / "Custom actions used" manifest) —
  https://github.github.com/gh-aw/reference/workflow-structure/
- **[2]** Introduction — How They Work (frontmatter "between `---` markers" + "markdown … natural
  language task descriptions"; "do exactly what you tell them, every time, in the same way"; "combine
  deterministic GitHub Actions infrastructure with AI-driven decision-making"; Best Practices: "Start
  simple and iterate … Test workflows using `gh aw compile --watch` and `gh aw run`") —
  https://github.github.com/gh-aw/introduction/how-they-work/
- **[3]** Reference — Glossary, *Agentic* / *Agentic Workflow* ("instead of 'if issue has label X, do
  Y', you write 'analyze this issue and provide helpful context'"; "Written in markdown instead of
  complex YAML") —
  https://github.github.com/gh-aw/reference/glossary/
- **[4]** Introduction — How They Work, *Regenerating the Lock File* ("The `.md` file is the editable
  source of truth, while `.lock.yml` is the compiled GitHub Actions workflow with security hardening.
  Commit both files.") —
  https://github.github.com/gh-aw/introduction/how-they-work/
- **[5]** Introduction — About Workflows (overview) (agentic workflows "Adapt behavior: Respond flexibly
  to different scenarios without requiring explicit programming for each case"; frontmatter "configures
  when the workflow runs and what it can do … markdown body contains your natural language
  instructions") —
  https://github.github.com/gh-aw/introduction/overview/
- **[6]** Reference — Compilation Process ("transforms a markdown workflow file into a complete GitHub
  Actions `.lock.yml` by embedding frontmatter and setting up runtime loading of the markdown body";
  "five compilation phases"; Action Pinning "pinned to commit SHAs … tags can be moved, SHAs cannot";
  "AI reasoning (read-only) is separated from write operations"; Performance "~100ms / ~500ms / ~2s";
  "Compilation is only required when changing frontmatter configuration") —
  https://github.github.com/gh-aw/reference/compilation-process/
- **[7]** Introduction — About Workflows (overview) ("Think of it like compiling code — you write
  human-friendly markdown, the compiler produces machine-ready YAML"; the lock "embeds the frontmatter
  and loads the markdown body at runtime") —
  https://github.github.com/gh-aw/introduction/overview/
- **[8]** Reference — Glossary, *Compilation* / *Workflow Lock File (.lock.yml)* ("Translating Markdown
  workflows (`.md` files) into GitHub Actions YAML format (`.lock.yml` files), including validation,
  import resolution, tool configuration, and security hardening"; "At runtime, GitHub Actions executes
  the lock file … while referencing the markdown for instructions"; "Both `.md` and `.lock.yml` files
  should be committed") —
  https://github.github.com/gh-aw/reference/glossary/
- **[9]** Reference — Glossary, *GitHub Actions* ("Agentic workflows compile to GitHub Actions YAML
  format, leveraging existing infrastructure for execution, permissions, and secrets") —
  https://github.github.com/gh-aw/reference/glossary/
- **[10]** Reference — Glossary, *Frontmatter Hash* ("A deterministic SHA-256 hash of a workflow's
  frontmatter configuration … Identical configurations produce identical hashes across the Go and
  JavaScript compiler implementations, enabling change detection, tamper verification, and
  reproducibility checks") —
  https://github.github.com/gh-aw/reference/glossary/
- **[11]** Reference — Workflow Structure, *Best Practices* ("Commit source files: Always commit `.md`
  files"; "Commit generated files: Also commit `.lock.yml` files for transparency") —
  https://github.github.com/gh-aw/reference/workflow-structure/
- **[12]** Guides — Editing Workflows ("the YAML frontmatter … requires recompilation when changed, and
  the markdown body … is loaded at runtime and takes effect on the next run"; "Changes to the YAML
  frontmatter always require recompilation"; Rule of Thumb: "Edit the markdown body for instruction
  changes. Recompile after any frontmatter change.") —
  https://github.github.com/gh-aw/guides/editing-workflows/
- **[13]** Setup — CLI Commands (`gh aw status` "Check current state of all workflows" / "List workflows
  with state, enabled/disabled status, schedules, and labels. With `--ref`, includes latest run
  status"; `gh aw run` "Execute workflows immediately in GitHub Actions"; `gh aw list` "name, engine,
  compilation status"; `gh aw compile --watch`) —
  https://github.github.com/gh-aw/setup/cli/

Internal book artifacts referenced (version-awareness / empirical anchors):
- `content/research/ch02-features.md` — inspected **v0.81.6**; compiled-lock metadata
  (`"compiler_version":"v0.81.6"`), lock size `100.3 KB`, agent job `contents: read` (verified
  2026-07-01).

---

## Artifact

Written to: `content/research/ch03-theory.md`
