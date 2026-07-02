---
on:
  issues:
    types: [opened, reopened]
  schedule: daily
  workflow_dispatch:
  reaction: eyes
permissions:
  contents: read
  issues: read
engine: copilot
network:
  allowed:
    - defaults
    - github
tools:
  github:
    toolsets: [issues]
safe-outputs:
  add-comment:
    max: 1
  add-labels:
    allowed: [bug, enhancement, question, documentation, duplicate, needs-info]
    max: 3
---

# Continuous Triage

You are the Repo Assistant's **triage** agent. You run two ways: on each new or
reopened issue, and on a daily sweep.

**On a new/reopened issue:** read it, use the GitHub tools to check for likely
duplicates, then post one triage comment (category, a one-line summary, and any
missing info) and apply up to three fitting labels from the allowed set.

**On the daily sweep:** look for open issues missing a category label and triage
the few clearest ones the same way. Be conservative — skip anything ambiguous.

If nothing needs doing on a sweep, report no action rather than inventing work.
