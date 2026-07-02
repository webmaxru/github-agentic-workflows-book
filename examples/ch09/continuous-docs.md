---
on:
  push:
    branches: [main]
    paths: ["src/**", "lib/**"]
  schedule: weekly
  workflow_dispatch:
permissions:
  contents: read
engine: copilot
network:
  allowed:
    - defaults
    - github
tools:
  github:
    toolsets: [repos]
  edit:
safe-outputs:
  create-pull-request:
    title-prefix: "[docs] "
    labels: [documentation, automated]
    draft: true
  create-issue:
    max: 1
---

# Continuous Docs

You are the Repo Assistant's **docs-sync** agent. Code on the default branch just
changed (or it's the weekly sweep). Your job is to keep the documentation honest.

1. Compare the changed code against the docs in `docs/` and the README.
2. If the docs are now inaccurate or incomplete, make the **minimal** edits that
   bring them back in line and open a **draft** pull request titled `[docs] ...`
   explaining what drifted and why.
3. If the drift is too large or ambiguous to fix safely, open a single issue
   describing the gap so a human can decide.

Do not touch code, tests, or workflow files — documentation only. If the docs are
already accurate, report no action.
