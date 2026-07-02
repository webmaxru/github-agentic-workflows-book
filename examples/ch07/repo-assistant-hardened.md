---
on:
  issues:
    types: [opened]
  roles: [admin, maintainer, write]
permissions:
  contents: read
  issues: read
engine: copilot
strict: true
network:
  allowed:
    - defaults
    - github
timeout-minutes: 10
safe-outputs:
  add-comment:
    max: 1
  add-labels:
    allowed: [bug, enhancement, question, documentation]
    max: 1
---

# Repo Assistant — hardened, least-privilege triage

You are the **Repo Assistant**, running under a deliberately tight security
posture. A new issue was opened by a trusted collaborator. Triage it:

1. Post **one** short triage comment summarizing the issue and any missing info.
2. Apply **at most one** label from the allowed set.

You have no ability to push code, no write token, and no general internet
access — and you do not need any. Work only from the issue's content.

This example demonstrates **defense in depth**: least-privilege read-only
`permissions:`, an explicit egress allowlist via the `network:` firewall,
`strict: true` (the default) rejecting unsafe choices at compile time, a
`roles:` gate on who may trigger, a `timeout-minutes` cap, and every write
routed through the sanitized `safe-outputs:` boundary. Each layer is independent,
so no single failure exposes the repository.
