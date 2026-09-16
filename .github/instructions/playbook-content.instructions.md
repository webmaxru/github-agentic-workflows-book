---
description: Content, style, structure, and citation conventions for GitHub Agentic Workflows book chapters.
applyTo: "content/**"
---

# Book Content Conventions

These rules apply to all book chapter content under `content/`. They keep chapters consistent,
accurate, and teachable across authors.

## Audience & voice
- Reader: a developer **new to GitHub Agentic Workflows** but comfortable with GitHub, GitHub
  Actions, and YAML.
- Voice: clear, direct, second-person ("you"). Explain *why* before *how*. No marketing fluff.

## Chapter structure (same skeleton every chapter)
1. **Objective** — one sentence: what the reader will be able to do afterward.
2. **Concept / theory** — the idea and the problem it solves (grounded in the theory brief).
3. **In gh-aw** — the capability/capabilities that implement the concept, with syntax and explanation.
4. **When to use / when not to** — guidance and common pitfalls.
5. **Worked example** — a minimal, verified, compilable example workflow.
6. **Recap & next** — bullets + link to the next chapter / prerequisites.

## Theory ↔ capability linkage
- Every gh-aw capability introduced **must** reference the concept it implements.
- No "orphan features": if a capability appears, the concept behind it was introduced first (here or earlier).

## Citations & accuracy
- Cite non-obvious claims with a source URL; prefer the **official gh-aw docs** and the official repo.
- No unsourced statistics or unfalsifiable superlatives.
- Only use frontmatter fields / CLI flags that `gh-aw-explorer` verified and `code-verifier` compiled.
- Record the **inspected `gh aw` version** the chapter targets.
- During maintenance, take the fixed target from the update plan; `content/FRAMEWORK_VERSION`
  remains the validated baseline until whole-corpus compilation passes. Preserve historical
  research and save fresh evidence under `content/research/updates/<target>/`.

## Code in content
- Every example workflow must be **verified** (see `gh-aw-workflow-examples.instructions.md`). Mark
  examples that require a live run or secret clearly.
- Caption each code block with what it demonstrates.
- Keep complete embedded workflows consistent with their `examples/` sources. Missing engine
  credentials can justify omitting a live run, not skipping strict compilation.
- Every complete copyable workflow has a corresponding file under `examples/`. An
  intentionally abridged/annotated variant is clearly captioned and has its own source
  if its behavior differs; do not silently present it as the full recipe. Label partial
  configuration blocks as excerpts and verify them in a complete workflow context.

## Edition maintenance
- Preserve chapter slugs, section slots, and valid theory unless the impact map justifies a change.
- `content/VERSION` versions reader-visible prose; framework, research, review, and tooling
  metadata alone do not justify a new edition.
- The release review is an actual ACCEPT/REVISE report plus a source-bound record in
  `content/release-review.json`. A successful build or a copied old verdict is not acceptance.
- Do not change reviewed manuscript/example/framework inputs after recording acceptance
  without renewed verification and review.

## HTML/markup
- Semantic, accessible HTML: real headings (`h1`–`h3`), landmarks, alt text, captioned `<pre><code>`.
- Keep **content decoupled from presentation** — no inline layout/styling that belongs to the shell
  (`frontend-builder` owns chrome, nav, and theming).
- Short paragraphs; prefer lists and tables for "when to use" comparisons.
