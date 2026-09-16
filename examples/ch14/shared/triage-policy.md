---
description: Shared triage policy — a local vendored fleet policy
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

## Shared triage policy

This fragment shares triage instructions and safe-output limits with its
importing workflow. It does not distribute updates or share repository memory.

- Categorize the issue and summarize it in one sentence.
- Note any missing information the reporter should add.
- Apply at most three labels from the allowed set; skip anything ambiguous.
- Post exactly one triage comment. Be concise and kind.
