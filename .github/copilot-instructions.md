# GitHub Agentic Workflows — Interactive Book

This repository builds an **interactive HTML book** that teaches
[GitHub Agentic Workflows (gh-aw)](https://github.github.com/gh-aw/). The book
starts from **high-level agentic concepts** (grounded in the official gh-aw docs) and descends into
the **gh-aw capabilities** — frontmatter, triggers, engines, tools, safe-outputs, the security
model, and the `gh aw` CLI — linking each capability back to the concept it implements. The build
installs the real `gh aw` CLI so the product is studied empirically, not described from memory.

The book is itself produced with the **agentic methodology it teaches**: a team of specialized
Copilot primitives (custom agents + skills + instructions) collaborate in waves of
draft → verify → review → integrate.

## The primitives (the "team")

### Custom agents — `.github/agents/`
| Agent | Responsibility |
|-------|----------------|
| `playbook-architect` | Designs TOC, chapter specs, navigation, and the wave plan |
| `theory-researcher` | Cited concept briefs from the gh-aw docs (theory sections) |
| `gh-aw-explorer` | Installs & explores the `gh aw` CLI + schema; feature notes + examples |
| `chapter-author` | Weaves theory + capability into chapter content |
| `code-verifier` | Compiles every example workflow; reports PASS/FAIL |
| `chapter-reviewer` | Reviews chapters; ACCEPT/REVISE + ranked findings |
| `frontend-builder` | Builds the interactive HTML shell and wires content in |

### Skills — `.github/skills/`
- `playbook-orchestration` — the wave-based workflow coordinating the whole team.
- `gh-aw-environment-setup` — reproducible `gh aw` CLI install/exploration.

### Instructions — `.github/instructions/`
- `playbook-content.instructions.md` — content/style/structure/citation rules (`content/**`).
- `gh-aw-workflow-examples.instructions.md` — gh-aw example-workflow conventions (`examples/**/*.md`).

### Prompts — `.github/prompts/`
- `new-chapter.prompt.md` — kick off one chapter end-to-end through the team.

## How they work together
See `.github/skills/playbook-orchestration/SKILL.md`. In short:
`architect` sets the outline → `frontend-builder` scaffolds the shell → per chapter,
`theory-researcher` + `gh-aw-explorer` research in parallel → `chapter-author` drafts →
`code-verifier` proves the examples compile → `chapter-reviewer` gates quality → `frontend-builder`
integrates. Work proceeds in waves (pilot chapter first), with a checkpoint commit per chapter.

## Project conventions
- **Theory before syntax.** Every capability is anchored to a concept introduced first.
- **Verify before ship.** A chapter is done only when its examples compile (or are clearly marked
  `SKIPPED-needs-secret`) and the reviewer returns ACCEPT.
- **No secrets in code.** Engine keys live in GitHub Actions secrets; examples validate at compile time.
- **Version-aware.** Record the inspected `gh aw` version in research/verification artifacts.
- **Content ⟂ presentation.** Authors write content; `frontend-builder` owns chrome/nav/theming.

## gh-aw reference (verified)
- Install: `gh extension install github/gh-aw` (or the `install-gh-aw.sh` script) · initialize with
  `gh aw init` · verify with `gh aw version`.
- Workflows are markdown + YAML frontmatter in `.github/workflows/*.md`, compiled to `*.lock.yml`
  by `gh aw compile`. Engines: Copilot, Claude, Codex, Gemini. Writes route through `safe-outputs:`.
- Docs: https://github.github.com/gh-aw/
- Repo & samples: https://github.com/github/gh-aw
  (see the `.github/aw/*.md` reference files: `cli-commands`, `safe-outputs`, `triggers`, `syntax`, …)
