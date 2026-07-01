---
name: gh-aw-environment-setup
description: Installs the GitHub Agentic Workflows CLI (`gh aw`) so the book's agents can explore, author, and compile real workflows. Use before any capability exploration or workflow verification.
---

# gh-aw Environment Setup

Provides a reproducible environment in which the book's agents can **install, explore, and compile
real GitHub Agentic Workflows** with the `gh aw` CLI. Used by `gh-aw-explorer` and `code-verifier`.

## Requirements
- **GitHub CLI (`gh`)** installed and authenticated (`gh auth status`).
- The **`gh aw` extension** (GitHub Agentic Workflows). No language runtime is required to author
  or compile workflows — they are markdown compiled to GitHub Actions.

## Setup (Windows / PowerShell)
```powershell
# Verify GitHub CLI first
gh --version
gh auth status

# Install the gh aw extension
gh extension install github/gh-aw
# (alternative) curl -sL https://raw.githubusercontent.com/github/gh-aw/main/install-gh-aw.sh | bash

# Verify
gh aw version
```

> Each PowerShell tool call runs in a fresh process — re-run `gh auth status` / `gh aw version`
> when you need to confirm state in a new command.

## Record the version you study
```powershell
gh aw version
```
Always note the inspected `gh aw` version in research/verification artifacts — gh-aw is in public
preview and moves fast.

## Exploration starting points
```powershell
gh aw --help
gh aw compile --help
gh aw new --help
gh aw mcp inspect --help
```
Read the frontmatter / `safe-outputs` / trigger schema in the official docs and the repo's
`.github/aw/*.md` reference files to document real fields and flags, and study the sample
workflows for usage patterns.

## Credentials
Running a workflow for real needs an **engine** secret (e.g. a Copilot / Anthropic / OpenAI /
Google key) configured as a **GitHub Actions secret** — never in code or committed files. For the
book, prefer **compile-time validation** (`gh aw compile --strict` / `--validate`), which needs no
secrets and stays deterministic, over live runs.

## Reproducibility
Pin what you used so others can reproduce:
```powershell
gh aw version   # record in research/verification notes
```

## References
- Docs: https://github.github.com/gh-aw/
- Repo & samples: https://github.com/github/gh-aw
- CLI reference: https://github.com/github/gh-aw/blob/main/.github/aw/cli-commands.md
