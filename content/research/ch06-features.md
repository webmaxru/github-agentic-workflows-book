# Chapter 6 — "Safe Outputs" — Research & Verification Note

- **Chapter:** `ch06-safe-outputs` (Part II opener). **Targets:** `gh aw` **v0.81.6**.
- **Prepared inline by orchestrator.** Date: 2026-07-02.
- **Verification artifact:** `examples/ch06/repo-assistant-open-pr.md` →
  `gh aw compile` → `✓ (105.0 KB)`, `0 error(s), 0 warning(s)`, EXIT 0. Lock gitignored.

## Concept (theory)
- You cannot prevent prompt injection → bound what a tricked model can DO. **Never give the model
  raw writes.** Propose-then-apply: agent read-only requests structured output; separate
  permission-scoped job validates + applies. Blast radius bounded by design (least privilege).

## Verified capability facts (source: reference/safe-outputs/)
- Direct quote: "Safe outputs enforce security through separation: agents run read-only and request
  actions via structured output, while separate permission-controlled jobs execute those requests.
  This provides least privilege, defense against prompt injection, auditability, and controlled
  limits per operation."
- Common outputs + default max: add-comment (1), add-labels (3, use `allowed`/`blocked`),
  create-issue (1), create-pull-request (1, `draft`, `title-prefix`, `labels`), update-issue (1).
  Many more: close-issue, create-discussion, create-pull-request-review-comment, push-to-pull-request-branch, etc.
- Auto-inject: no safe-outputs section → create-issue enabled (conservative). System types always on:
  noop, missing-tool, missing-data.
- Sanitization: XML-escaped, HTTPS only, domain allowlist, 0.5MB/65k line limits, control-char strip.
  `@mention` escaped unless verified collaborator; `max-bot-mentions` default 10.
- `staged: true` → preview only (skips writes, prints step-summary preview). Per-type or global.
- Maps to ch03 job graph: read-only `agent` job + separate `safe_outputs` job holding write scopes.

## Example shape (verified)
`create-pull-request` (draft) + `add-comment` with agent `permissions: contents:read, issues:read`
(READ-ONLY). Demonstrates highest-trust action (open PR) with zero agent write perms — write scopes
live only in generated safe_outputs job. Next: ch07 adds permissions/firewall/strict-mode layers.
