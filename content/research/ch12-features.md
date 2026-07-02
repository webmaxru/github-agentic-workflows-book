# Chapter 12 — "Observability & Debugging" — Research & Verification Note

- **Chapter:** `ch12-observability-and-debugging` (Part III). **Targets:** `gh aw` **v0.81.6**.
- **Prepared inline by orchestrator.** Date: 2026-07-02.
- **Verification artifact:** `examples/ch12/repo-assistant-observable.md` (with `observability.otlp`)
  → `gh aw compile --approve` → `✓ (102.5 KB)`, 0/0, EXIT 0. Lock gitignored.

## Concept (theory)
- **Observability = precondition for trust.** Can't govern/budget/secure what you can't see. Agentic
  runs are inspectable: 1 non-deterministic job, everything captured as artifacts (prompts, outputs,
  patches, logs). Src: introduction/architecture/ Observability section.

## Verified CLI facts (source: `gh aw logs --help`, `gh aw audit --help` run live v0.81.6)
- **`gh aw logs`**: "Download and analyze agentic workflow logs and artifacts… overview table with
  aggregate metrics including duration, token usage, and cost." Default = compact usage artifact only.
  `--artifacts all` or `--artifacts agent,firewall`. Sets: activation, agent, all, detection,
  experiment, firewall, github-api, mcp, usage. Artifacts: safe_output.jsonl, agent_output/,
  agent-stdio.log, aw-{branch}.patch, workflow-logs/, summary.json. Accepts workflow-id or filename.
- **`gh aw audit <run>`**: "audit… by downloading artifacts and logs, detecting errors, analyzing MCP
  tool usage, and generating a concise report." 1 run → detailed MD report; 2+ → diff (first=base).
  Accepts run ID / run URL / job URL (±step). Job URL w/o step → "finds and extracts the first failing
  step's output." Firewall Analysis section (per-domain allow/deny, from ch07).
- **`gh aw status`**: fleet/workflow health.
- **OTel:** `observability.otlp: {endpoint, headers}` exports distributed traces to OTLP backend
  (frontmatter). References secrets → review gate → `--approve`.
- Run step summaries in Actions UI (rich Markdown).

## Example shape (verified)
Triage workflow + `observability.otlp` block. Worked example = 3-command debug flow (logs overview →
audit run → --artifacts all) tracing a failure to denied egress + token blow-up; fix via network.allowed.
Next: ch13 governance/FinOps (cap the cost you can now see).
