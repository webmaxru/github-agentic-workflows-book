# Chapter 13 — "Governance & FinOps" — Research & Verification Note

- **Chapter:** `ch13-governance-and-finops` (Part III). **Targets:** `gh aw` **v0.81.6**.
- **Prepared inline by orchestrator.** Date: 2026-07-02.
- **Verification artifact:** `examples/ch13/repo-assistant-budgeted.md` →
  `gh aw compile` → `✓ (101.7 KB)`, 0/0, EXIT 0. Lock gitignored.

## Concept (theory)
- Agentic work = VARIABLE cost (per-run inference), unlike fixed CI compute → needs a budget. At org
  scale = policy surface (which workflows/capabilities/spend/model). FinOps + governance apply.

## Verified capability facts (source: reference/frontmatter/, guides/governance/)
- **max-ai-credits:** AIC budget, ENABLED by default, defaults 1000 (1k). Steering warnings at
  80/90/95/99%. K/M suffixes. `-1` disables enforcement+steering.
- **max-daily-ai-credits:** rolling 24h cap across recent runs of same workflow. DISABLED by default;
  `-1` disables. Exceeded → warns, creates issue, skips agent job, conclusion reports. Skipped for
  workflow_call/repository_dispatch/workflow_dispatch w/ aw_context.
- **timeout-minutes:** default 20. **max-turns:** default 500. **stop-after** (ch04).
- AI Credits (AIC) = model-normalized cost unit. Token efficiency = tighter prompt/tools/scopes.
- **gh aw env** manages `GH_AW_DEFAULT_*` vars at repo/org/ent scope via YAML `default_` keys
  (default_max_ai_credits "5M", default_max_daily_ai_credits, default_max_turns, default_timeout_minutes,
  default_model_copilot, …). `gh aw env get/update --dry-run/--yes`.
- **Percolation/precedence:** frontmatter > repo var > org var > enterprise var > compiler fallback.
- **Runtime policy vars `GH_AW_POLICY_*`:** capability gates without recompiling. E.g.
  `GH_AW_POLICY_ALLOW_CREATE_PULL_REQUEST=false` → safe-outputs server refuses to start for PR workflows,
  org-wide. Set via `gh variable set --org`.
- **Rollout pattern:** enterprise baseline → org where needed → repo exceptions → rare frontmatter overrides.

## Example shape (verified)
4 cost brakes: max-ai-credits:200 + max-daily-ai-credits:2000 + timeout-minutes:10 + stop-after:+30d.
Prose shows `gh aw env update --org` + `GH_AW_POLICY_ALLOW_CREATE_PULL_REQUEST=false`. Next: ch14 fleets/adoption.
