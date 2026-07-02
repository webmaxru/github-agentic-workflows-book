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

# Repo Assistant — budgeted, policy-compliant triage

You are the **Repo Assistant**. Triage the new issue with one concise comment and
at most one label. Keep it efficient: read only what you need, and don't spend
effort re-deriving context you already have.

This example is about **cost and policy**, not the triage. It caps spend three
ways — a per-run `max-ai-credits` budget, a rolling `max-daily-ai-credits` limit
across the day's runs, and a `timeout-minutes` wall clock — and it stops
triggering after 30 days. Organization-wide defaults and capability policies are
layered on top of these per-workflow guardrails.
