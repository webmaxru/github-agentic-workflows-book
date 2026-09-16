---
on:
  workflow_dispatch:
tools:
  repo-memory:
    file-glob: ["**/*.json"]
    allowed-extensions: [".json"]
    validation:
      script: |
        if (!fs.existsSync(memoryRoot)) throw new Error("Missing memory root");
      timeout-minutes: 1
safe-outputs:
  noop:
---

Report no work. This compile-only probe demonstrates deterministic memory validation.
