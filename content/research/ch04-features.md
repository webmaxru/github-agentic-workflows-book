# Chapter 4 — "Triggers" — Research & Verification Note

- **Chapter:** `ch04-triggers` (Part I). **Targets:** `gh aw` **v0.81.6** (verified via `gh aw version`).
- **Prepared inline by orchestrator** (repo rule: no parallel blocking subagents). Date: 2026-07-02.
- **Verification artifact:** `examples/ch04/repo-assistant-triggers.md` →
  `gh aw compile` → `✓ (102.8 KB)`, `0 error(s), 0 warning(s)`, EXIT 0. Lock gitignored.

## Concept (theory)
- Trigger = the outer loop's **clock**. Two shapes: **reactive** (event payload = the work) and
  **proactive** (schedule is the prompt). Choosing a trigger is also a security + cost decision.

## Verified capability facts (source: official docs)
- `on:` = standard GitHub Actions triggers + gh-aw enhancements (reactions, cost control, filtering).
  Src: reference/triggers/.
- Events: `issues:`, `pull_request:` (fork-blocked by default; `forks:` allowlist), `issue_comment:`/
  `pull_request_review_comment:`/`discussion_comment:`, `schedule:`, `workflow_dispatch:` (+inputs),
  `workflow_run:` (repo-ID+fork checks injected; scope `branches:`), `deployment_status:`,
  `repository_dispatch:`, `slash_command:`, `label_command:`.
- Schedules: human-friendly + **fuzzy** (`daily`, `daily around 14:00`, `daily between 9:00 and 17:00`),
  or cron list. Compiler assigns deterministic scattered time by file path → avoids load spikes.
  Src: reference/schedule-syntax/.
- Shorthands (`on: issue opened`, `on: push to main`, `on: daily`) expand to Actions syntax and
  auto-add `workflow_dispatch`.
- Enhancements: `reaction:` (emoji on triggering item), `status-comment:`, `stop-after:` (+30d etc.,
  disables triggering after deadline; recompiling resets), `manual-approval:`, `skip-if-match:`/`-no-match:`.
- Safe defaults: PR forks blocked; `roles:` default `[admin, maintainer, write]` (allowlist, exact
  match, no hierarchy); unsafe triggers (push/issues/pull_request) auto-enforce permission checks.
- `pull_request`/comment events → agent has both PR branch and default branch.

## Example shape (verified)
`issues:[opened,reopened]` + `schedule: daily` + `workflow_dispatch` + `reaction: eyes` +
`stop-after: "+30d"`; read-only perms; `engine: copilot`; `network: defaults`; writes via safe-outputs.
Body branches on `${{ github.event_name }}` (reactive triage vs proactive stale sweep).
