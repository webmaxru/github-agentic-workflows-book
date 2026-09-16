---
on:
  workflow_dispatch:
model: auto
models:
  allowed: ["claude-*"]
  blocked: ["claude-opus-*"]
safe-outputs:
  noop:
---

Report no work. This compile-only probe demonstrates model access policy, not a price cap.
