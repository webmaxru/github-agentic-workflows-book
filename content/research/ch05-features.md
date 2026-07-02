# Chapter 5 — "Engines" — Research & Verification Note

- **Chapter:** `ch05-engines` (Part I). **Targets:** `gh aw` **v0.81.6** (verified via `gh aw version`).
- **Prepared inline by orchestrator.** Date: 2026-07-02.
- **Verification artifact:** `examples/ch05/repo-assistant-claude.md` →
  `gh aw compile --approve` → `✓ (105.0 KB)`, `0 error(s), 0 warning(s)`, EXIT 0. Lock gitignored.

## Concept (theory)
- **Engine-neutral by design.** Intent (Markdown) + safe-outputs boundary are portable; the model is
  a pluggable runtime detail. "You can switch later by changing only `engine:` and the corresponding
  secret." No vendor lock-in. Src: reference/engines/.

## Verified capability facts (source: reference/engines/, reference/frontmatter/)
- `engine:` selects the coding agent. Copilot is default (line can be omitted).
- Production engines + secrets:
  | engine | id | secret |
  | copilot (default) | copilot | copilot-requests: write (rec.) or COPILOT_GITHUB_TOKEN |
  | Claude | claude | ANTHROPIC_API_KEY |
  | Codex | codex | OPENAI_API_KEY |
  | Gemini | gemini | GEMINI_API_KEY |
  Experimental: crush, opencode, pi.
- Object form: `engine: {id, version, model, command, args, agent, api-target, env, bare, ...}`.
- **Pin version** for reproducible builds; unpinned `version: latest` → compiler WARNS (supply-chain risk).
  Verified live: `latest` emitted the warning; pinning `"2.1.70"` removed it.
- **Secret-review gate (safe-update mode):** switching engine introduces a new restricted secret
  (e.g. ANTHROPIC_API_KEY) → compiler flags it; `--approve` records intent. VERIFIED live.
- Choice guidance: Copilot broadest features (custom agents, autopilot/max-continuations); Claude
  `max-turns` for long reasoning; Codex/Gemini if already in tooling/budget.
- Feature deltas: `max-turns`=Claude; `max-continuations` & `engine.agent`=Copilot-only. Top-level
  `max-turns` (default 500) & `max-ai-credits` (default 1000) work across all engines.
- Compile is OFFLINE — no engine secret needed at compile; only at run time.

## Example shape (verified)
Same ch02 triage prose; only `engine:` changed to `{id: claude, version: "2.1.70", model:
claude-sonnet-4.5}`. Demonstrates portability: triggers/permissions/network/safe-outputs unchanged.
Ends Part I; next chapter opens the safe-outputs boundary (Part II).
