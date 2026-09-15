---
name: playbook-orchestration
description: The wave-based workflow that coordinates the book's agent team (architect, theory-researcher, gh-aw-explorer, chapter-author, code-verifier, chapter-reviewer, frontend-builder) to produce the GitHub Agentic Workflows interactive book end to end. Use to plan and run the production pipeline for one or more chapters.
---

# Playbook Orchestration

This skill describes **how the book's agents work together** to build the GitHub Agentic Workflows
(gh-aw) interactive book. It is the orchestration layer: who is dispatched, in what order, with
what hand-offs and checkpoints. Use bootstrap mode for a new book and maintenance mode for
an existing edition.

## Choose the mode first

- **Bootstrap:** only when the user explicitly asks to build/restructure the whole book.
  Use `run-playbook.prompt.md` and the architecture/shell pipeline below.
- **Maintenance:** the normal path for a new gh-aw release. Use `update-book.prompt.md`;
  resolve a fixed upstream target, map the full delta to existing chapters, and update only
  affected material. Do not restart architecture or scaffold over authored content.
- **Release preparation:** `release-content.prompt.md` packages already reviewed changes.
  It does not replace upstream research. Stop at a PR; publication follows human review.

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
   PASS. Missing engine secrets can justify skipping a live run, never compilation.
8. **Review:** `chapter-reviewer` → ACCEPT or REVISE; on REVISE, route must-fixes to `chapter-author`.
9. **Integrate:** `frontend-builder` → wire the accepted chapter into the site nav.
10. Checkpoint: commit the chapter (draft + examples + review verdict).

### Integration pass (after all waves)
11. `chapter-reviewer` reads across chapters for cross-chapter consistency (terminology, ordering,
    duplicate/contradictory claims).
12. `chapter-author` applies cross-cutting fixes; `frontend-builder` finalizes nav/cross-links.

## Maintenance pipeline

1. Read `content/FRAMEWORK_VERSION` (validated baseline), `content/VERSION` (prose edition),
   the latest published content tag, git status, and any saved update target.
2. Resolve the latest stable gh-aw tag **once**, unless an exact target was supplied. Record
   its commit, release URL/date, and baseline in `content/research/updates/<target>/`.
   Reuse an active target on resume; do not upgrade it halfway through a wave. Track plan
   status through researching, researched, authoring, verified, accepted, and prepared.
   Prepared plans are finished PR handoffs, not active targets to reuse forever.
3. `gh-aw-explorer` assesses the entire baseline-to-target interval, including changes in
   intervening prereleases that reached the target. Read tagged docs/schema and verify
   behavior with the exact binary. Produce cited feature deltas and an impact map with
   an explicit update/unchanged/add decision for every chapter.
4. Pin a task-isolated compiler using `gh-aw-environment-setup`. `playbook-architect` is
   needed only for real TOC changes. `theory-researcher` is needed for changed/new concepts,
   not to recreate still-valid theory briefs.
5. Start with one low-risk affected chapter, then process bounded waves through author,
   verifier, reviewer, and integration. Preserve chapter slugs and historical evidence.
   Keep source examples and embedded snippets consistent; checkpoint accepted work only.
6. `code-verifier` compiles **all** standalone examples, including unchanged ones, with
   `scripts/verify_examples.py` and the exact target. Require strict PASS and emitted locks;
   no live runs. Shared fragments are import dependencies, not standalone workflows.
7. After the corpus passes, advance `content/FRAMEWORK_VERSION` and refresh current-facing
   target statements. Do not relabel old research as newly verified.
8. `chapter-reviewer` performs the editorial/cross-chapter review and saves an actual
   report with exactly one standalone `Verdict: ACCEPT` or `Verdict: REVISE` line.
   After ACCEPT, the orchestrator runs
   `scripts/release_content.py record-review --report <report> --verdict ACCEPT`.
   The resulting `content/release-review.json` is bound to source and report digests.
   Covered changes invalidate acceptance and require renewed review.
9. `frontend-builder` regenerates the existing site/PDF. Run the `release-content` prompt
   to choose an appropriate prose edition, update notes, and prepare a PR. The reusable
   validation workflow gates publishing; human review and merge remain the release boundary.
   Mark the plan prepared with its edition and PR URL, without claiming publication.

No reader-visible changes means no new prose edition. A version bump for research, framework
metadata, tooling, or styling alone is not a release.

## Wave ordering guidance
- **Wave 0:** one pilot chapter (e.g. "What is an agentic workflow?") to validate the whole pipeline.
- **Wave 1:** chapters with the most existing source material (lowest risk).
- **Wave 2:** the hardest chapters (security model, safe-outputs, MCP, multi-workflow composition).
- **Wave 3:** integration chapters needing cross-references to earlier ones.

## Orchestration principles
- **One chapter, one author per wave** — keep scope inside an agent's context budget; split if too big.
- **Explicit ownership** — bind verified agent IDs to roles/chapter paths; parallel completion
  order is not an identity map. Do not send a role-specific follow-up to an unbound ID.
- **Checkpoint discipline** — draft → review → revise → commit at each chapter.
- **Batch reviews** in later waves (one reviewer over several chapters) to cut dispatch overhead.
- **Fix the primitives, not the symptom** — when a recurring gap appears, update the relevant agent
  definition / instructions rather than hand-patching each chapter.
- **Verify before ship** — no chapter is "done" until its examples compile (PASS) and the reviewer ACCEPTs.
- **Independent versions** — `content/VERSION` describes the book; `content/FRAMEWORK_VERSION`
  describes verified framework coverage. Never substitute a tool/package version for either.
- **Publication boundary** — agents prepare a PR; they do not merge or publish without separate
  authorization. A successful HTML/PDF build alone is not editorial or compiler acceptance.
