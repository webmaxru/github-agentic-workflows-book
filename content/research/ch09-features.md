# Chapter 9 — "Continuous Triage & Docs" — Research & Verification Note

- **Chapter:** `ch09-continuous-triage-and-docs` (Part II payoff). **Targets:** `gh aw` **v0.81.6**.
- **Prepared inline by orchestrator.** Date: 2026-07-02.
- **Verification artifacts (2):**
  - `examples/ch09/continuous-triage.md` → `✓ (102.1 KB)`, 0/0, EXIT 0.
  - `examples/ch09/continuous-docs.md` → `✓ (104.0 KB)`, 0/0, EXIT 0.

## Concept (theory)
- "Continuous X" pattern = one recurring judgement task → standing workflow = **mini-product**
  (owner-task, cadence, bounded outputs, def of done). CI/CD = deterministic; Continuous X = judgement.
- Lineage: GitHub Next "Agent Factory" + `githubnext/agentics` samples.
- Real adopters (from book brief): backend.ai-webui (daily test-improver, e2e-healer),
  euparliamentmonitor (20+ agents), clash-verge-rev review agent cloned across 215+ repos.

## Patterns (compositions of verified caps ch4–8 — no new syntax)
- **Continuous Triage:** reactive (`issues`) + proactive (`schedule: daily`) + `reaction: eyes`;
  `tools.github toolsets:[issues]` (dup detection); writes via `add-comment` + `add-labels`(allowed).
- **Continuous Docs:** trigger on the CAUSE of drift — `push: {branches:[main], paths:[src/**,lib/**]}`
  + `schedule: weekly`; `tools.github toolsets:[repos]` + `edit:`; proposes `create-pull-request`
  (draft) + `create-issue` fallback. Human stays on merge decision.

## Failure modes (taught)
- Over-eager triager (noise) → cap max, allowed labels, skip ambiguous.
- Confidently-wrong docs PR → draft + issue fallback + human merge.
- Runaway schedule → stop-after + budget (ch13).

## Next
ch10 = Continuous Review, Testing, CI-Doctor, Refactoring (close the quality loop).
