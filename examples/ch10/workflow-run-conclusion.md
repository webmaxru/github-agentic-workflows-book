---
on:
  workflow_run:
    workflows: [CI]
    types: [completed]
    branches: [main]
    conclusion: [failure]
safe-outputs:
  noop:
---

Report no work. This compile-only probe demonstrates CI failure filtering.
