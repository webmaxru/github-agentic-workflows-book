# Chapter 14 — "Fleets & Adoption" — Research & Verification Note

- **Chapter:** `ch14-fleets-and-adoption` (Part III capstone). **Targets:** `gh aw` **v0.81.6**.
- **Prepared inline by orchestrator.** Date: 2026-07-02.
- **Verification artifact:** `examples/ch14/fleet-triage.md` (imports shared policy, `source:`,
  `tracker-id:`, `repo-memory`) → `gh aw compile` → `✓ (109.9 KB)`, 0/0, EXIT 0. Lock gitignored.

## Concept (theory)
- Beyond one repo → coordinate/scale across dozens: org-wide rollout, code-quality across 100s repos,
  aggregate issue tracking into single control plane. Fleet = managed practice = Parts I+II governed
  & multiplied. Maturity arc: Individual → Team → Organization.
- Measured impact (githubnext/repo-assist-impact, verified in repo memory): 15 repos, 651 issues net
  reduction, median 9× velocity; thesis "throughput gated by human decision-making." Adopters (brief):
  Home Assistant, CNCF, Carvana, M&S, Hud.io; clash-verge-rev review agent cloned 215+ repos.

## Verified capability facts (source: guides/using-at-scale/, reference/frontmatter/)
- Two distribution layers: (1) developer-facing — `gh aw add`/`add-wizard` install from another repo,
  `gh aw update` pulls upstream preserving local edits; `imports:` for shared components; `source:`
  records origin. (2) org governance — central `agentic-workflows` repo as source of truth, versioned
  exact tags (@v1.2.0)/moving major (@v1)/SHA pins, import-schema params, `private: true`.
- Cross-repo: safe outputs `target-repo`/`allowed-repos`; GitHub Apps preferred (rotation, fine-grained).
- Patterns: **CentralRepoOps** (central control repo dispatches/aggregates), **OrchestratorOps**
  (parallel worker dispatch large-scale), BatchOps/WorkQueueOps (large repos).
- **Safe Rollout:** report-only/staged → production with evidence; staged mode (ch06) as shadow eval.
- `tracker-id:` tags every asset with hidden marker → fleet-wide GitHub search.

## Example shape (verified)
Thin fleet workflow: local shared import + `source: my-org/…@v1.2.0` + `tracker-id` + repo-memory.
Embodies all 14 chapters in one lock. Capstone recap delivers the book's page-one promise.
