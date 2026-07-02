---
on:
  issues:
    types: [opened, reopened]
  schedule: daily
  workflow_dispatch:
permissions:
  contents: read
  issues: read
engine: copilot
network:
  allowed:
    - defaults
    - github
imports:
  - shared/triage-policy.md
tools:
  repo-memory: true
---

# Repo Assistant — triage with a shared policy and memory

You triage issues using the **shared triage policy** imported into this workflow
(its tools, allowed labels, and safe outputs come from that one file, reused
across every repo that imports it).

Before you triage, read your **repo memory** for notes on recurring patterns in
this repository (common duplicates, frequently-missing info). Apply the shared
policy to the triggering issue. Afterward, if you noticed a new recurring
pattern, append a short note to memory so future runs — and future repos that
share this policy — benefit from what you learned.
