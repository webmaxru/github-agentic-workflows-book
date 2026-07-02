---
on:
  issues:
    types: [opened]
  workflow_dispatch:
permissions:
  contents: read
  issues: read
engine: copilot
network:
  allowed:
    - defaults
    - github
safe-outputs:
  add-comment:
    max: 1
observability:
  otlp:
    endpoint: ${{ secrets.OTLP_ENDPOINT }}
    headers:
      Authorization: ${{ secrets.OTLP_TOKEN }}
---

# Repo Assistant — observable triage

You are the **Repo Assistant**. Triage the new issue with a single, concise
comment summarizing it and any missing information.

This example is about **operating** the workflow, not the triage itself. It
exports distributed traces to an OpenTelemetry (OTLP) backend via the
`observability:` block, so runs show up in your tracing tool alongside their
token usage and timing. Combined with `gh aw logs` and `gh aw audit`, that gives
you a full picture of what the agent did and why.
