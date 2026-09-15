---
description: Kick off authoring a single book chapter end-to-end through the agent team.
---

# New Chapter

Produce one complete, reviewed chapter of the GitHub Agentic Workflows interactive book.

**Chapter:** <chapter number + title>
**Learning objective:** <what the reader can do afterward>
**gh-aw capabilities to cover:** <list, or "decide from the architect's spec">

Use the validated `content/FRAMEWORK_VERSION` or the exact target saved by an active
`update-book` run. Do not resolve a newer framework independently. For changes to existing
chapters, use `update-book.prompt.md` instead of restarting chapter architecture.

Run the per-chapter pipeline from the `playbook-orchestration` skill:

1. Confirm/create the chapter spec with `playbook-architect` (objective, sections, dependencies).
2. In parallel:
   - `theory-researcher` → cited concept brief.
   - `gh-aw-explorer` → feature notes + minimal example workflows (explore the installed
     `gh aw` CLI + schema; record the version).
3. `chapter-author` → write the chapter weaving theory + capability, following
   `.github/instructions/playbook-content.instructions.md`.
4. `code-verifier` → strictly compile every example workflow with the pinned target until
   PASS. Loop fixes back. Missing runtime credentials do not waive compilation.
5. `chapter-reviewer` → ACCEPT/REVISE with ranked findings; route must-fixes to the author.
6. `frontend-builder` → wire the accepted chapter into the site navigation.
7. Checkpoint: commit chapter content, examples, and the review verdict.

Do not ship the chapter until all examples compile and the reviewer returns ACCEPT.
Release preparation, global review evidence, and publication are separate orchestrator steps.
