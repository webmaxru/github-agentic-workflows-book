---
description: Shared triage policy — tools, labels, and safe outputs reused across Repo Assistant workflows
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

When you triage an issue, follow this policy so every repository behaves the same way:

- Categorize the issue and summarize it in one sentence.
- Note any missing information the reporter should add.
- Apply at most three labels from the allowed set; skip anything ambiguous.
- Post exactly one triage comment. Be concise and kind.
