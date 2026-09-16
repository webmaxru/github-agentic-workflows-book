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
- Validate examples at **compile time** with the fixed target and strict mode, using
  `scripts/verify_examples.py`; pass `--compiler` for an isolated executable and `--version`
  for an update target not yet recorded as the validated baseline. Do not require a live run.
- If an example is used to demonstrate `gh aw run` (manual dispatch), its `on:` block MUST include a
  `workflow_dispatch:` trigger — `gh aw run` only works with workflows that declare one (verified via
  `gh aw run --help`, v0.81.6).

## Verification
- Every standalone example must be compiled by `code-verifier` and reach **PASS**, emitting
  a `.lock.yml`, before it ships. A runtime needs-secret marker cannot waive compilation.
- Stage examples and relative shared imports in temporary git repositories, never in the
  book's actual `.github/workflows`. Shared fragments are not standalone workflow targets.
- Keep repository-policy demonstrations in a `strict-policy/` fixture directory with
  `aw.json` directly beside the Markdown. The verifier stages that directory as
  `.github/workflows`, omits CLI `--strict`, and requires effective strict metadata;
  forcing the flag would mask a broken policy example. Record a no-policy control
  separately when establishing the behavior.
- Required regular nonignored Markdown/JSON/YAML/TXT and example-local ignore files
  are fixture inputs and are bound into review fingerprints, not just the workflow Markdown.
- Framework updates require the **entire** corpus to pass, including unchanged workflows.
- Require the emitted lock's exact compiler version and effective strict metadata, overall
  report PASS, and exit zero. Zero workflow failures do not waive setup/cleanup errors.
- Preserve stderr approval warnings. `--validate`/scanner/deployment-context/runtime checks
  are additional evidence, not synonyms for the canonical strict-compilation gate.
- Update matching embedded chapter snippets whenever an example changes.
- Record the **`gh aw` version** the example was verified against.
- Require strict compilation so examples model production-grade, security-first workflows.

## Versioning
- gh-aw is in public preview and evolves quickly; flag any use of preview/unstable fields or flags.
