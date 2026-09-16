---
on:
  schedule: hourly
  workflow_dispatch:
  cooldown: 4h
  stop-after: "+30d"
permissions:
  contents: read
  issues: read
engine: copilot
network: defaults
safe-outputs:
  create-issue:
    title-prefix: "[maintenance-digest] "
    max: 1
---

# Repo Assistant — maintenance digest with cooldown

You are the **Repo Assistant** on a proactive maintenance pass. This separate
workflow demonstrates `on.cooldown`: scheduled and manual runs share a
four-hour admission interval. It does not handle urgent issue-open events.

Read open issues in this repository and look for issues with no activity in the
last 30 days that clearly need a maintainer's decision. Ignore existing
maintenance-digest issues as candidates.

If there are actionable candidates not already covered by an open
maintenance-digest issue, request **at most one** new issue summarizing them.
Use a title beginning with `[maintenance-digest] `, link to each candidate,
and suggest a next step for a human. Do not close, label, or comment on the
candidate issues. If there is nothing new to report, report no work.

Cooldown is best-effort admission, not a concurrency lock or a spending cap.
History lookup failure fails open. The relative stop deadline is preserved
on ordinary recompilation; renewing it requires `--refresh-stop-time`.
