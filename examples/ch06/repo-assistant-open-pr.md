---
on:
  issues:
    types: [labeled]
  workflow_dispatch:
permissions:
  contents: read
  issues: read
engine: copilot
network: defaults
safe-outputs:
  create-pull-request:
    title-prefix: "[repo-assistant] "
    labels: [automated, ai-generated]
    draft: true
  add-comment:
    max: 1
---

# Repo Assistant — propose a fix as a pull request

You are the **Repo Assistant**. An issue in this repository was just labeled.
If (and only if) the label that was applied is `good-first-fix`, attempt a small,
self-contained fix.

1. Read the triggering issue and locate the relevant code.
2. Make the **smallest** change that addresses the issue. Do not refactor
   unrelated code, change public APIs, or touch CI/workflow files.
3. Open a **draft** pull request with a clear title and a body that explains the
   change and links the issue it closes.
4. Post one short comment on the original issue linking to the pull request.

If the issue is not a `good-first-fix`, or the fix is not small and safe, do not
open a PR — post a comment explaining why a human should take it instead.

This example demonstrates **safe-outputs**: the agent has **no write permissions**.
It runs read-only and *requests* a pull request and a comment; gh-aw's separate,
permission-scoped jobs validate and apply those requests. The agent never pushes
to your repository directly.
