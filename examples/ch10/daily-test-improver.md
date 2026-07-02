---
on:
  schedule: daily
  workflow_dispatch:
permissions:
  contents: read
engine: copilot
network:
  allowed:
    - defaults
    - github
    - node
tools:
  github:
    toolsets: [repos]
  bash: ["npm ci", "npm test", "npx jest", "npx vitest run"]
  edit:
safe-outputs:
  create-pull-request:
    title-prefix: "[tests] "
    labels: [tests, automated]
    draft: true
---

# Daily Test Improver

You are the Repo Assistant's **test-improver** agent, running once a day.

1. Run the existing test suite and inspect coverage to find one under-tested area
   of the code that matters (core logic, a bug-prone module, an untested branch).
2. Write **new tests only** — do not change production code. Make them pass
   against the current behavior.
3. Open one **draft** pull request titled `[tests] ...` adding those tests, with a
   body explaining what you covered and why it matters.

Keep the change small and focused: one area, a handful of solid tests. If the
suite is already well covered, report no action instead of padding it.
