---
description: Conventions for GitHub Agentic Workflows example workflows used in the book.
applyTo: "examples/**/*.md"
---

# gh-aw Workflow Example Conventions

Applies to all example agentic workflows in the book (under `examples/`). Goal: every example is
**minimal, compilable, version-aware, and secret-free**.

## Format
- An example is a **markdown workflow**: YAML **frontmatter** + a natural-language body.
- Author against the real schema (`on:`, `engine:`, `permissions:`, `network:`, `tools:`,
  `safe-outputs:`, `imports:`, `strict:`). Confirm fields by exploration — do not invent keys.

## Style
- **Minimal**: smallest workflow that demonstrates the capability; no unrelated frontmatter.
- Keep the main agent job **read-only**; route every GitHub write through `safe-outputs:`.
- Prefer the smallest trigger (`on:`) that matches the scenario; limit `network:` and tool access
  to what the example actually needs.
- Add a short line in the body stating which concept/capability the example demonstrates.

## Secrets & live runs
- **Never hardcode or commit secrets.** Engine keys are GitHub Actions secrets, referenced by name.
- Validate examples at **compile time** — do not require a live run. Use `gh aw compile --validate`
  / `--strict`; clearly mark anything that would need a real run or a secret.
- If an example is used to demonstrate `gh aw run` (manual dispatch), its `on:` block MUST include a
  `workflow_dispatch:` trigger — `gh aw run` only works with workflows that declare one (verified via
  `gh aw run --help`, v0.81.6).

## Verification
- Every example must be compiled by `code-verifier` and reach **PASS** (compiles to `.lock.yml`,
  or documented `SKIPPED-needs-secret`) before it ships in a chapter.
- Record the **`gh aw` version** the example was verified against.
- Prefer `strict: true` so examples model production-grade, security-first workflows.

## Versioning
- gh-aw is in public preview and evolves quickly; flag any use of preview/unstable fields or flags.
