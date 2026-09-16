---
on:
  workflow_dispatch:
tools:
  playwright:
network:
  allowed: [defaults, playwright]
safe-outputs:
  noop:
---

Report no work. This compile-only probe demonstrates CLI-only browser provisioning.
