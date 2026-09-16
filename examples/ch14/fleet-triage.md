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

# Repo Assistant — fleet triage

This example demonstrates governed policy reuse with repository-scoped memory.
Use the imported triage policy's tools, labels, and safe outputs.

Apply the shared policy to the triggering issue.

The `source:` value is synthetic, unexercised origin metadata, not proof of an
installation from a real publisher. The import is a local vendored fragment.

The `tracker-id` helps locate body-bearing outputs such as triage comments; it
does not mark label operations. Updating a real fleet requires reviewed consumer
dependency changes, recompilation, and deployment, not just a central edit.
