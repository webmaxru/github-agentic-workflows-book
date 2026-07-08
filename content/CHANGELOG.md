# Changelog — Book Content

All notable changes to the **book content** — the chapters and their source under
[`content/`](./) — are recorded here. This log tracks the *content edition* only. The site
generator, PDF renderer, analytics beacon, and other tooling evolve with the repository's commit
history and are deliberately **not** part of this version line.

The current content version lives in [`content/VERSION`](./VERSION). Each version is published as a
GitHub Release tagged `content-vMAJOR.MINOR` with the matching single-file PDF edition attached, so
every published state of this living book stays reproducible and downloadable.

Versioning follows [Semantic Versioning](https://semver.org/) applied to prose:

- **MAJOR** — a structural rewrite, or reordering of parts/chapters.
- **MINOR** — new chapters, sections, or substantive new material.
- **PATCH** — corrections, clarifications, and small edits that add no new material.

## [1.1] - 2026-07-08

Added Agent Package Manager (APM) coverage so the fleet chapters explain how shared agentic
components are distributed and governed as supply-chain dependencies.

### Added

- **Chapter 11 — Reuse & Memory:** APM dependencies via `shared/apm.md`, showing how imported shared
  components are declared and resolved like packaged dependencies.
- **Chapter 13 — Governance & FinOps:** APM supply-chain governance with `apm-policy.yml`, covering
  provenance and policy for third-party agentic components.

## [1.0] - 2026-07-03

Initial release of the complete book: fourteen chapters across three parts, each anchored to a
concept and carrying a verified, compilable example workflow, following the Repo Assistant from a
single triage workflow to a governed multi-repo fleet.

### Added

- **Part I — The Individual:** Chapters 1–5 — what agentic workflows are, your first workflow,
  anatomy & the compile model, triggers, and engines.
- **Part II — The Team:** Chapters 6–10 — safe outputs, defense in depth, tools & MCP, continuous
  triage & docs, and continuous review & testing.
- **Part III — The Organization:** Chapters 11–14 — reuse & memory, observability & debugging,
  governance & FinOps, and fleets & adoption.
