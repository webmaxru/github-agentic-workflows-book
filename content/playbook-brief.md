# Book Brief — GitHub Agentic Workflows

The single source-of-truth scope for the book. The `playbook-architect` reads this to design the
chapter map; every other agent treats it as the north star.

## Subject
**GitHub Agentic Workflows (gh-aw)** — the product that lets you write AI-powered, agentic
automations for a GitHub repository as **natural-language Markdown workflows with YAML frontmatter**,
compiled into GitHub Actions (`*.lock.yml`) by the `gh aw` CLI extension.

- Docs: https://github.github.com/gh-aw/
- Repo & source of truth for behavior: https://github.com/github/gh-aw

## Goal
Teach a developer — new to gh-aw but comfortable with GitHub, GitHub Actions, and YAML — to go from
"what is an agentic workflow?" to confidently authoring, compiling, securing, and shipping their own
gh-aw workflows. The book descends from **high-level agentic concepts** into the **concrete gh-aw
capabilities** that implement them, always anchoring theory before syntax.

## Language & format
- Workflow examples are **Markdown files with YAML frontmatter** (`.github/workflows/*.md`),
  compiled with `gh aw compile`. Examples are verified at **compile time** (no secrets/live runs
  required unless explicitly demonstrating a run).
- Prose targets the official docs terminology; behavior claims are grounded by the
  `gh-aw-explorer` inspecting the real `gh aw` CLI and frontmatter schema.

## Topics in scope (indicative — the architect refines these into chapters)
- What agentic workflows are and when to use them vs. plain GitHub Actions.
- The gh-aw workflow model: Markdown + frontmatter, compilation to `.lock.yml`.
- Installing and using the `gh aw` CLI (`init`, `new`, `compile`, `run`, `logs`, `audit`, `status`).
- Triggers (`on:`) and the agentic **engines** (Copilot, Claude, Codex, Gemini).
- **MCP server integration** (`tools:`) — giving workflows real capabilities.
- **Safe Outputs** (`safe-outputs:`) — how writes (issues, PRs, comments) are gated safely.
- **Permissions & network** hardening; **Strict Mode**.
- **Shared Components** (`imports:`) and **Repo Memory**.
- Authoring, debugging (`gh aw logs`, `gh aw audit`), and CI hosting patterns.

## Out of scope
- Building or teaching Microsoft Agent Framework, LangChain, or other agent SDKs.
- Provider/model internals beyond how gh-aw selects and configures an engine.
- Deep GitHub Actions tutorials (assumed as reader background, not taught from scratch).

## Non-negotiables
- **Theory before API.** Anchor every capability to a concept introduced first.
- **Verify before ship.** Every example must `gh aw compile` cleanly (or be clearly marked as
  needing a live run/secret).
- **No secrets in content.** Engine keys live in Actions secrets, never in the book.
- **Version-aware.** Record the inspected `gh aw` version in research/verification artifacts.
