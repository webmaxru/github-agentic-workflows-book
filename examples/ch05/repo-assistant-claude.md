---
on:
  issues:
    types: [opened]
  workflow_dispatch:
engine:
  id: claude
  version: "2.1.70"
  model: claude-sonnet-4.5
permissions:
  contents: read
  issues: read
network: defaults
safe-outputs:
  add-comment:
    max: 1
  add-labels:
    allowed: [bug, enhancement, question, documentation]
    max: 1
---

# Repo Assistant — triage a new issue (Claude engine)

You are the **Repo Assistant**. A new issue was just opened in this repository.

Read the triggering issue's title and body, then:

1. Post **one** short, friendly triage comment that restates the request in a
   sentence, names the category (bug, feature, question, or docs) and why, and
   lists any missing information the reporter should add.
2. Apply **at most one** label from the allowed set that best matches the issue.

The *instructions above are identical* to the Copilot version of this workflow.
Only the `engine:` block changed — this demonstrates that the workflow's intent
and its safe-outputs boundary are **engine-neutral**: you swap the agent's brain
by changing one field (and its secret), not by rewriting the workflow.
