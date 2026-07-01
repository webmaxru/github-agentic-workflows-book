---
name: playbook-orchestration
description: The wave-based workflow that coordinates the book's agent team (architect, theory-researcher, gh-aw-explorer, chapter-author, code-verifier, chapter-reviewer, frontend-builder) to produce the GitHub Agentic Workflows interactive book end to end. Use to plan and run the production pipeline for one or more chapters.
---

# Playbook Orchestration

This skill describes **how the book's agents work together** to build the GitHub Agentic Workflows
(gh-aw) interactive book. It is the orchestration layer: who is dispatched, in what order, with
what hand-offs and checkpoints. (This is a starting scaffold — refine as the project evolves.)

## The team
| Agent | Role |
|-------|------|
| `playbook-architect` | Designs TOC, chapter specs, navigation, wave plan |
| `theory-researcher` | Produces cited concept briefs from the gh-aw docs |
| `gh-aw-explorer` | Installs & explores the `gh aw` CLI + schema; feature notes + examples |
| `chapter-author` | Weaves theory + capability into chapter content |
| `code-verifier` | Compiles every example workflow; reports pass/fail |
| `chapter-reviewer` | Reviews chapters; ACCEPT/REVISE + ranked findings |
| `frontend-builder` | Builds the interactive HTML shell and wires content in |

## Pipeline (per the case-study methodology: draft → review → revise, in waves)

### Phase 0 — Architecture
1. Dispatch `playbook-architect` → TOC, chapter table, section breakdowns, wave plan.
2. Dispatch `frontend-builder` → scaffold the site shell + nav driven by the TOC.
3. Checkpoint: commit TOC + shell.

### Phase 1 — Environment
4. Run the `gh-aw-environment-setup` skill (via `gh-aw-explorer`) → the `gh aw` CLI installed and
   explorable (`gh aw version`).

### Waves (repeat per wave; start with ONE pilot chapter, then widen)
For each chapter in the wave, run **research in parallel**, then author, verify, review:
5. **Research (parallel):**
   - `theory-researcher` → concept brief (`content/research/<ch>-theory.md`)
   - `gh-aw-explorer` → feature notes + draft example workflows (`content/research/<ch>-features.md`)
6. **Author:** `chapter-author` → chapter draft, pulling both briefs together.
7. **Verify:** `code-verifier` → compile every example workflow; loop with author/explorer until all
   PASS (or SKIPPED-needs-secret with a clear marker).
8. **Review:** `chapter-reviewer` → ACCEPT or REVISE; on REVISE, route must-fixes to `chapter-author`.
9. **Integrate:** `frontend-builder` → wire the accepted chapter into the site nav.
10. Checkpoint: commit the chapter (draft + examples + review verdict).

### Integration pass (after all waves)
11. `chapter-reviewer` reads across chapters for cross-chapter consistency (terminology, ordering,
    duplicate/contradictory claims).
12. `chapter-author` applies cross-cutting fixes; `frontend-builder` finalizes nav/cross-links.

## Wave ordering guidance
- **Wave 0:** one pilot chapter (e.g. "What is an agentic workflow?") to validate the whole pipeline.
- **Wave 1:** chapters with the most existing source material (lowest risk).
- **Wave 2:** the hardest chapters (security model, safe-outputs, MCP, multi-workflow composition).
- **Wave 3:** integration chapters needing cross-references to earlier ones.

## Orchestration principles
- **One chapter, one author per wave** — keep scope inside an agent's context budget; split if too big.
- **Checkpoint discipline** — draft → review → revise → commit at each chapter.
- **Batch reviews** in later waves (one reviewer over several chapters) to cut dispatch overhead.
- **Fix the primitives, not the symptom** — when a recurring gap appears, update the relevant agent
  definition / instructions rather than hand-patching each chapter.
- **Verify before ship** — no chapter is "done" until its examples compile (PASS) and the reviewer ACCEPTs.
