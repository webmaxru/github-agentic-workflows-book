# Chapter 8 — "Tools & MCP" — Research & Verification Note

- **Chapter:** `ch08-tools-and-mcp` (Part II). **Targets:** `gh aw` **v0.81.6**.
- **Prepared inline by orchestrator.** Date: 2026-07-02.
- **Verification artifact:** `examples/ch08/repo-assistant-tools.md` →
  `gh aw compile` → `✓ (100.8 KB)`, `0 error(s), 0 warning(s)`, EXIT 0. Lock gitignored.

## Concept (theory)
- Agents need **tools** to act beyond text. **MCP** (Model Context Protocol) = open standard exposing
  capabilities via "servers" (GitHub, DB, browser). Tension: capability vs exposure — every tool is
  attack surface (feeds trifecta legs). Grant fewest tools, tightest scope; sandbox the rest.

## Verified capability facts (source: reference/tools/, introduction/architecture/)
- `tools:` = "which GitHub API calls, browser automation, and AI capabilities are available."
- Built-ins: `github:` (toolsets: [repos, issues, ...] — this IS the GitHub MCP server, read),
  `bash:` (defaults to safe cmds echo/ls/cat/grep/…; `bash: []` disable; `bash: ["echo","git status"]`;
  `bash: [":*"]` all-caution; wildcards `git:*`), `edit:`, `web-fetch:`, `web-search:` (Codex opt-in),
  `playwright:`, `cache-memory:`, `repo-memory:` (ch11), `qmd:` (exp), `agentic-workflows:` (needs actions:read).
- Custom `mcp-servers:` — options: `command`+`args` (process), `container` (Docker), `url`+`headers`
  (HTTP), `registry`, `env` (secrets), `allowed` (tool restriction). Example: slack MCP w/ allowed:
  [send_message, get_channel_history].
- **MCP gateway sandbox:** servers run in ISOLATED containers (substrate separation); gateway spawns,
  AWF mediates egress; compromised server can't access other components' memory/state. `allowed:`
  enforced at gateway. Per-container network allowlists.
- Adding an MCP server with `env` secret → secret-review gate (like ch05); `--approve`.

## Example shape (verified)
Read-only agent + `tools: github: {toolsets:[issues,repos]}` (GitHub MCP) + `web-fetch:` +
`network:[defaults,github]` + one `add-comment`. Added reach, not write authority. Custom
`mcp-servers:` shown in prose. Next: Part II payoff — Continuous X patterns (ch09).
