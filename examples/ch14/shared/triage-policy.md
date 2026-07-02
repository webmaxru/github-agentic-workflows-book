---
description: Central triage policy — the org's single source of truth for issue triage
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

## Central triage policy

Every repository in the fleet triages the same way by importing this file:

- Categorize the issue and summarize it in one sentence.
- Note any missing information the reporter should add.
- Apply at most three labels from the allowed set; skip anything ambiguous.
- Post exactly one triage comment. Be concise and kind.
