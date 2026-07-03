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

## APM governance layer (source: reference/dependencies/ + learn.github.com well-architected governing-agentic-workflows)
- APM treats agent skills as packages with the same governance primitives as code deps.
- **Pinning + scanning:** every package pinned to exact commit SHA in `apm.lock.yaml` (no drift between
  reviewed vs. run); install-time content scan for hidden Unicode threats (homoglyphs, bidi override
  chars, zero-width joiners) that could inject invisible prompt instructions.
- **Org policy `apm-policy.yml`** (in org `.github` repo): `enforcement: block`, `dependencies.allow/deny`,
  `require_pinned_constraint: true`. Inheritance enterprise→org→repo is TIGHTEN-ONLY (child can narrow
  allowlist / add deny / escalate enforcement, cannot relax parent). Mirrors cost-defaults percolation.
- **Isolation:** `imports: - uses: shared/apm.md with: { isolated: true }` → agent sees only the skill's
  packaged instructions; repo-level AGENTS.md / copilot-instructions.md cannot override it.
- **Air-gapped:** corporate scanning proxy via `PROXY_REGISTRY_URL/TOKEN` + `PROXY_REGISTRY_ONLY=1`
  (blocks direct GitHub fetch; lockfile records proxy host).
- Ties to ch07 threat model (skills = executable context = injection vector) and ch11 (APM = import layer).

## Example shape (verified)
4 cost brakes: max-ai-credits:200 + max-daily-ai-credits:2000 + timeout-minutes:10 + stop-after:+30d.
Prose shows `gh aw env update --org` + `GH_AW_POLICY_ALLOW_CREATE_PULL_REQUEST=false`. Next: ch14 fleets/adoption.
