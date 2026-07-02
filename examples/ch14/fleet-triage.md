---
on:
  issues:
    types: [opened, reopened]
  workflow_dispatch:
permissions:
  contents: read
  issues: read
engine: copilot
network:
  allowed:
    - defaults
    - github
source: "my-org/agentic-workflows/workflows/triage.md@v1.2.0"
tracker-id: repo-assistant-triage
imports:
  - shared/triage-policy.md
tools:
  repo-memory: true
---

# Repo Assistant — fleet triage (installed from the central repo)

You triage issues in this repository using the **central triage policy** shared
across the whole fleet (its tools, labels, and safe outputs are imported).

Apply the shared policy to the triggering issue. Every asset you create is tagged
with this workflow's `tracker-id`, so an org admin can find all of the Repo
Assistant's work across every repository with a single GitHub search.

This workflow was installed from the org's central `agentic-workflows` repository
(see `source:`), pinned to a released version. Updating the fleet means bumping
that one version — every repo picks up the change on its next update.
