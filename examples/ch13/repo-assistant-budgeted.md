---
on:
  issues:
    types: [opened]
  schedule: daily
  workflow_dispatch:
  stop-after: "+30d"
permissions:
  contents: read
  issues: read
engine: copilot
network:
  allowed:
    - defaults
    - github
max-ai-credits: 200
max-daily-ai-credits: 2000
timeout-minutes: 10
safe-outputs:
  add-comment:
    max: 1
  add-labels:
    allowed: [bug, enhancement, question, documentation]
    max: 1
---

# Repo Assistant — budgeted triage

You are the **Repo Assistant**. Triage the new issue with one concise comment and
at most one label. Keep it efficient: read only what you need, and don't spend
effort re-deriving context you already have.

On a scheduled or manual run without an issue target, report no work rather than
inventing a target.

This example demonstrates **scoped budgets and policy**. The main agent has a
`max-ai-credits: 200` budget; the rolling historical admission threshold is
`max-daily-ai-credits: 2000`. Neither is a total bill cap or an atomic reservation.
`timeout-minutes: 10` bounds the agentic step, not every job, and
`stop-after: "+30d"` supplies an admission deadline.

Threat detection and Actions compute are separate. Explicit frontmatter budgets
are not replaced by organization defaults. Compile-time policy and supported
runtime capability gates have different enforcement points.
