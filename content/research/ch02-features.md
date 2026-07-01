# Chapter 2 — Feature Reference Notes: "The 10-Minute Win: Your First Workflow"

> Empirical feature notes for the `chapter-author`. Every field and command below was exercised
> against the real CLI and cross-checked with the official docs.

- **Inspected `gh aw` version:** `v0.81.6` (`gh aw version` → `gh aw version v0.81.6`)
- **Compiler baked into the lock:** `"compiler_version":"v0.81.6"`, `"strict":true`, `"agent_id":"copilot"`,
  `"engine_versions":{"copilot":"1.0.65"}`
- **Primary docs:** [Quick Start](https://github.github.com/gh-aw/setup/quick-start/) ·
  [CLI Commands](https://github.github.com/gh-aw/setup/cli/) ·
  [Engines](https://github.github.com/gh-aw/reference/engines/) ·
  [Safe Outputs](https://github.github.com/gh-aw/reference/safe-outputs/)
- **Worked example:** `examples/ch02/repo-assistant-triage.md` (compiles clean — see
  [Verification](#verification))

## Theory anchors (Chapter 2)

The chapter establishes three concepts first; each feature below links back to one of them.

| Anchor | One-line idea |
|--------|---------------|
| **Triage-as-judgment** | Reading a new issue and deciding "what is this / what next" is a *judgment* task — exactly what a coding agent is good at, and a safe first job because the stakes are a comment, not a code change. |
| **The authoring loop** | You write intent in Markdown, `compile` it to a real Actions workflow, and `run` it — `init → new → compile → run`. |
| **Safe-by-default** | The agent is read-only; every write to GitHub is *requested* and executed by separate, permission-scoped jobs (`safe-outputs`), and strict mode is on unless you opt out. |

---

## Feature: `gh aw init`

- **Command:** `gh aw init`
- **Implements concept:** the authoring loop (bootstraps a repo so you *can* author/compile/run) +
  safe-by-default (marks generated lock files).
- **Purpose:** One-time, non-interactive repository setup for agentic workflows. It does **not**
  prompt for an engine or configure secrets.
- **What it scaffolds (verified from `gh aw init --help`, v0.81.6):**
  - Configures `.gitattributes` to mark `*.lock.yml` as generated.
  - Creates the dispatcher skill `.github/skills/agentic-workflows/SKILL.md` and the workflow-designer
    skill `.github/skills/agentic-workflow-designer/SKILL.md`.
  - Creates the custom agent `.github/agents/agentic-workflows.md`.
  - Configures `.vscode/settings.json`.
  - By default (no `--no-mcp`): writes `.github/workflows/copilot-setup-steps.yml` and `.github/mcp.json`
    (gh-aw MCP server config).
- **Syntax / useful flags:**
  ```bash
  gh aw init                     # defaults
  gh aw init --engine claude     # skip Copilot-specific artifacts
  gh aw init --no-mcp            # skip MCP config files
  gh aw init --no-skill          # skip dispatcher skill
  gh aw init --create-pull-request  # land the setup as a PR
  ```
- **When to use:** the very first time you turn a repo into a gh-aw repo.
- **When not to:** on a repo already initialized (it's idempotent but noisy); it is *not* how you add
  a workflow — use `gh aw new` or `gh aw add`.

---

## Feature: `gh aw new <name>`

- **Command:** `gh aw new <workflow-id>`
- **Implements concept:** the authoring loop (the *create* step).
- **Purpose:** Creates one new agentic-workflow Markdown file, pre-populated with a heavily commented
  template of every frontmatter option, at `.github/workflows/<workflow-id>.md`. The `workflow-id`
  is the file basename without `.md`.
- **Syntax / useful flags:**
  ```bash
  gh aw new repo-assistant                 # create .github/workflows/repo-assistant.md
  gh aw new repo-assistant.md              # same (the .md is stripped)
  gh aw new repo-assistant --engine copilot  # seed the template with a specific engine
  gh aw new repo-assistant --force         # overwrite if it exists
  gh aw new                                # interactive wizard (also -i / --interactive)
  ```
- **When to use:** starting a workflow from scratch and you want the annotated template as a guide.
- **When not to:** when a community/official workflow already does the job — prefer `gh aw add`
  (or `gh aw add-wizard`) to pull a pre-baked one, e.g.
  `gh aw add-wizard githubnext/agentics/daily-repo-status`
  ([Quick Start](https://github.github.com/gh-aw/setup/quick-start/)).
- **Note for the chapter:** the annotated template is verbose by design. Our worked example is a
  hand-written *minimal* file (below), which is the better teaching artifact for a "10-minute win."

---

## Feature: `gh aw compile`

- **Command:** `gh aw compile [workflow]...`
- **Implements concept:** the authoring loop (the *compile* step) + safe-by-default (strict validation).
- **Purpose:** Compiles Markdown workflow(s) into the GitHub Actions lock file that actually runs:
  `<file>.md` → `<file>.lock.yml`. With no argument it compiles every file in `.github/workflows/`.
  You never hand-edit the `.lock.yml`; you re-compile.
- **Strict mode is the default.** It REFUSES unsafe choices: top-level write permissions (route writes
  through `safe-outputs:`), unpinned actions, wildcard network egress, and deprecated fields. It PROVIDES
  safe defaults when you omit keys: no `engine:` → Copilot; no `permissions:` → read-only; no `network:` →
  the curated egress allowlist (= `network: defaults`). Empirically verified against v0.81.6: a file with
  only `on:` + `safe-outputs:` (no engine/permissions/network) compiles with 0 errors / 0 warnings. So the
  smallest valid workflow is a trigger + body, with any writes routed through `safe-outputs:`.
- **Syntax / useful flags:**
  ```bash
  gh aw compile                                   # all workflows in .github/workflows
  gh aw compile examples/ch02/repo-assistant-triage.md  # a single file by path
  gh aw compile --no-emit                         # validate only, no lock file written
  gh aw compile --strict                          # force strict even if a file set strict:false
  gh aw compile --watch <id>                      # recompile on change
  ```
- **Offline:** compilation is local and works without network or secrets — this is what lets us
  compile-verify every example in the book.
- **When to use:** after every frontmatter or body change, before committing, and in CI as a gate.
- **When not to:** you do not compile to *execute* — compiling never calls an engine or touches GitHub.

---

## Feature: `gh aw run` — **live-run / secret step (not compile-verified)**

- **Command:** `gh aw run [workflow]...`
- **Implements concept:** the authoring loop (the *run* step).
- **Purpose:** Triggers a compiled workflow on **GitHub Actions** via its `workflow_dispatch` trigger.
  It only works on a real repo with the workflow pushed, and it requires the engine secret to be set.
  **We mark this as a live-run/secret step: it is not something the book compile-verifies.**
- **Requirements (why it's not offline):**
  - The workflow must already be compiled and support `workflow_dispatch`.
  - It runs on GitHub's servers against a live repository (`-r/--repo` to target one).
  - The engine needs its secret configured (for Copilot, `COPILOT_GITHUB_TOKEN`; see the engine note).
- **Syntax / useful flags:**
  ```bash
  gh aw run repo-assistant-triage           # dispatch on the current branch
  gh aw run repo-assistant-triage --dry-run # validate without triggering a real run
  gh aw run repo-assistant-triage --push    # commit & push workflow files first, then run
  gh aw run                                 # interactive: pick a dispatchable workflow
  ```
- **When to use:** to kick off a workflow by hand (initial smoke test, on-demand re-run) rather than
  waiting for its natural trigger (here, "issue opened").
- **When not to:** to test compilation or frontmatter — use `gh aw compile` (offline, free). Also note
  our example's real trigger is `issues: [opened]`; `gh aw run` is only for manual dispatch.

---

## Feature: the Copilot engine (default)

- **Frontmatter key:** `engine: copilot`
- **Implements concept:** triage-as-judgment (the engine is the "judgment" that reads the issue and
  decides the category and comment).
- **Purpose:** Selects which coding agent runs the workflow. gh-aw supports Copilot, Claude, Codex,
  and Gemini; **Copilot is the default** ([Engines](https://github.github.com/gh-aw/reference/engines/)).
  If you already have GitHub Copilot, it needs no extra account setup, which is why it's the natural
  first-workflow engine.
- **Verified from the compiled lock (`repo-assistant-triage.lock.yml`, v0.81.6):**
  - Metadata: `"agent_id":"copilot"`, `"engine_versions":{"copilot":"1.0.65"}`.
  - Env: `GH_AW_INFO_ENGINE_ID: "copilot"`, `GH_AW_INFO_ENGINE_NAME: "GitHub Copilot CLI"`.
  - Secret used at run time: `COPILOT_GITHUB_TOKEN` — a validate step checks it and points to
    [engines#github-copilot-default](https://github.github.com/gh-aw/reference/engines/#github-copilot-default).
    This confirms the secret is only needed for the **live run**, never for compilation.
- **Syntax:**
  ```yaml
  engine: copilot          # explicit (recommended in a teaching example)
  # engine may be omitted entirely — copilot is the default
  ```
- **When to use:** first workflows and Copilot-licensed teams; keep it explicit in examples so readers
  see which engine ran.
- **When not to:** when you need a specific non-Copilot model/provider — set `engine: claude|codex|gemini`
  (each needs its own secret: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`).

---

## Feature: first look at `safe-outputs` (Chapter 6 owns the depth)

- **Frontmatter key:** `safe-outputs:`
- **Implements concept:** safe-by-default.
- **Purpose:** Declares the GitHub writes a workflow is allowed to conclude with. The agent runs
  **read-only** and *requests* actions as structured output; separate, permission-scoped jobs perform
  them. This gives least privilege, prompt-injection defense, auditability, and per-operation caps
  ([Safe Outputs](https://github.github.com/gh-aw/reference/safe-outputs/)).
- **Two types used in the worked example (verified names & defaults):**
  - `add-comment` — "Post comments on issues, PRs, or discussions" (default max: 1).
  - `add-labels` — "Add labels to issues or PRs" (default max: 3); `allowed:` restricts to a specific
    label set or glob patterns — a good habit that blocks the agent from inventing labels.
- **Syntax (as used):**
  ```yaml
  safe-outputs:
    add-comment:
      max: 1
    add-labels:
      allowed: [bug, enhancement, question, documentation]
      max: 1
  ```
- **Why it matters here:** it's what makes issue triage *safe-by-default* — the worst case is one
  comment and one allow-listed label, never a code or settings change.
- **When to use:** any time a workflow should write to GitHub. In strict mode this is the *only*
  sanctioned way to write.
- **When not to:** read-only/report-to-logs workflows don't need writes — but note that if you omit
  `safe-outputs:` entirely, gh-aw auto-enables `create-issue` with conservative defaults. Deeper
  configuration (targets, dedup, cross-repo, staged mode) is **Chapter 6**.

---

## Worked example

- **Path:** `examples/ch02/repo-assistant-triage.md`
- **Scenario:** Repo Assistant triages a newly opened issue — posts one triage comment and applies at
  most one allow-listed label, all through `safe-outputs`.
- **Frontmatter keys used (all stable, none preview):**

  | Key | Value | Role |
  |-----|-------|------|
  | `on` | `issues: { types: [opened] }` | smallest trigger for the scenario |
  | `permissions` | `contents: read`, `issues: read` | read-only agent (strict-clean) |
  | `engine` | `copilot` | the default engine, made explicit |
  | `network` | `defaults` | explicit for clarity; if omitted, strict applies this same curated egress allowlist |
  | `safe-outputs` | `add-comment: {max: 1}`, `add-labels: {allowed: [...], max: 1}` | the only writes |

- **Body:** a short natural-language brief plus one line naming the capability it demonstrates
  ("This workflow demonstrates **safe-outputs**: the agent runs read-only … applied from separate,
  permission-scoped jobs.").

### Verification

Command run (offline, no secrets):

```bash
gh aw compile examples/ch02/repo-assistant-triage.md
```

Exact success output (exit code 0):

```text
✓ examples\ch02\repo-assistant-triage.md (100.3 KB)
✓ Compiled 1 workflow(s): 0 error(s), 0 warning(s)
```

Corroborating checks:
- Compiled lock metadata: `"compiler_version":"v0.81.6"`, `"strict":true`, `"agent_id":"copilot"`.
- Agent job permissions in the lock: `contents: read` (read-only — writes are in separate safe-output jobs).
- `git check-ignore examples/ch02/repo-assistant-triage.lock.yml` → exit 0 (the lock file is gitignored,
  as required).

---

## Preview / unstable fields flagged (version-awareness)

- **None used** in this example — every key (`on`, `permissions`, `engine`, `network`, `safe-outputs`
  with `add-comment` / `add-labels`) is stable in `v0.81.6` and compiled with **0 warnings**.
- **Defaults to record for readers:**
  - Strict mode is **on by default**; there is no need to write `strict: true`. Setting write
    permissions at the top level or using deprecated fields will fail strict compilation.
  - `engine:` may be omitted (Copilot is the default); we keep it explicit for teaching.
- **Adjacent surfaces that ARE experimental (not used here, mention only if relevant later):**
  `gh aw forecast` is labelled `[EXPERIMENTAL]` in the CLI; among safe-outputs, `merge-pull-request`
  and `dispatch-repository` are marked experimental. Keep these out of Chapter 2.
