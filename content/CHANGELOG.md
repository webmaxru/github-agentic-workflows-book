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

## [1.2] - 2026-09-16

Updated all fourteen chapters for [gh-aw v0.88.7](https://github.com/github/gh-aw/releases/tag/v0.88.7),
covering the changes since the book's v0.81.6 framework baseline while retaining its
Individual, Team, and Organization progression.

### Added

- **Engines and admission controls:** Pi, model selection and override precedence, cooldown,
  stacked-PR filtering, and explicit stop-time refresh guidance.
- **Runtime and tool capabilities:** rootless runtime profiles, independent AI threat
  detection, explicit egress boundaries, Playwright CLI, and transport-specific MCP guidance.
- **State, operations, and policy:** memory filtering and validation, bounded log downloads
  and cached audits, incomplete-work outcomes, model policy, forecasts, and repository strictness.
- **Compile-checked examples:** ten additional workflow/configuration fixtures bring the
  corpus to 24, with 16 complete embedded workflow copies. Policy examples prove effective
  strictness without a CLI override; compilation does not certify runtime integrations.

### Changed

- **Reuse and fleets:** distinguish imports, native skills, experimental plugins, independently
  versioned APM 0.28.0 integration, and package manifests; explain deliberate consumer updates
  rather than automatic propagation.
- **Reader prerequisites:** make authentication, labels, Issues support, review, and runtime
  requirements explicit, and separate book policy from optional product capabilities.

### Fixed

- **Claims and operating contracts:** qualify offline compilation, deterministic inference,
  safety, reversibility, retention, and file-scope promises. Daily triage now selects at most
  one issue to respect its one-comment-per-run limit.
- **Budget defaults:** correct the existing 5,000-AIC daily fallback and separate main-agent,
  detector, admission, compute, and timeout scopes rather than promising a complete bill cap.
- **Integration accuracy:** correct APM lock/policy/isolation/scanning/proxy descriptions,
  replace the unverified Slack command with an explicitly illustrative MCP configuration,
  and use version-bound references for consequential behavior.

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
