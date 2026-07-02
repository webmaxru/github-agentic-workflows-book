# Chapter 10 — "Continuous Review, Testing & CI-Doctor" — Research & Verification Note

- **Chapter:** `ch10-continuous-review-and-testing` (Part II close). **Targets:** `gh aw` **v0.81.6**.
- **Prepared inline by orchestrator.** Date: 2026-07-02.
- **Verification artifacts (2):**
  - `examples/ch10/continuous-review.md` → `✓ (101.8 KB)`, 0/0, EXIT 0.
  - `examples/ch10/daily-test-improver.md` → `✓ (103.8 KB)`, 0/0, EXIT 0.

## Concept (theory)
- Quality has a LOOP (propose→review→test→merge→fix). CI automates deterministic checks; Continuous-X
  fills the JUDGEMENT gaps. Unbreakable rule: **humans keep the merge** (agent proposes, human disposes).
- Adopters: clash-verge-rev review agent cloned 215+ repos; backend.ai-webui test-improver + e2e-healer;
  camunda CI cost analysis.

## Patterns (compositions; safe outputs enforce the human-in-loop rule)
- **Review:** `pull_request` → `submit-pull-request-review` with `allowed-events: [COMMENT]` (docs:
  "prevents the agent from submitting APPROVE reviews regardless… recommended default… without
  creating a persistent merge-blocking state") + `create-pull-request-review-comment`.
- **Testing:** `schedule` → scoped `bash` (run suite) + `edit` → `create-pull-request` (draft). Tests only.
- **CI-Doctor:** `workflow_run: {workflows:[CI], types:[completed], conclusion:[failure], branches:[main]}`
  → read logs → `add-comment`/`create-issue`. Uses ch04 conclusion filtering; hardened cross-repo.
- **Refactoring:** `schedule`/command → draft `create-pull-request` (behavior-preserving). Ship after Testing.

## When-not
- Don't auto REQUEST_CHANGES (merge-blocking from fallible model). Don't let tester edit prod code.
- Don't auto-merge agent PRs. Don't refactor a repo without good tests.

## Next
Part III opens: ch11 reuse (imports) + memory.
