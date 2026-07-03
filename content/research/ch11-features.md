# Chapter 11 — "Reuse & Memory" — Research & Verification Note

- **Chapter:** `ch11-reuse-and-memory` (Part III opener). **Targets:** `gh aw` **v0.81.6**.
- **Prepared inline by orchestrator.** Date: 2026-07-02.
- **Verification artifact:** `examples/ch11/repo-assistant-shared.md` (imports `shared/triage-policy.md`
  + `repo-memory: true`) → `gh aw compile` → `✓ (108.1 KB)`, 0/0, EXIT 0. Lock gitignored.

## Concept (theory)
- DRY across a fleet: two kinds of sameness → (1) shared config/intent → `imports`; (2) shared
  knowledge over time → memory. Shared component = a governance surface (govern once, apply everywhere).

## Verified capability facts (source: reference/imports/, reference/repo-memory/, reference/frontmatter/)
- `imports:` composes shared tools/steps/mcp/prompts. **Shared component = file WITHOUT `on:`**
  (validated, not compiled, only imported).
- Path resolution: relative (default, rel to importing wf dir), repo-root (`.github/…`), cross-repo
  (`owner/repo/path@ref` pinned tag/branch/SHA, cached in `.github/aw/imports/`).
- Parameterized: `import-schema` (typed params) + caller `uses`/`with`. `#Section` refs; `?` optional.
- Merge: tools deep-merge (allowed arrays concat+dedupe); safe-outputs each type once (main wins);
  network allowed union; permissions validation-only (main must declare imported perms).
- `inlined-imports: true` embeds imports into lock (self-contained; for cross-org workflow_call / rulesets).
- **APM (Agent Package Manager)** rides the import mechanism: import `shared/apm.md` (vendored from
  `microsoft/apm` via `gh aw add microsoft/apm/.github/workflows/shared/apm.md --dir shared`) and pass
  `with: packages: [...]`. Adds a dedicated `apm` job that packs packages into a bundle artifact; agent
  job unpacks for deterministic startup. Manages skills/prompts/instructions/agents/hooks/plugins;
  resolves full dependency tree. Package ref formats: `owner/repo` | `owner/repo/path` | `owner/repo#ref`.
  `apm.lock` pins every package to an exact commit SHA (reproducible; lock diffs reviewable in PRs).
  Token fallback GH_AW_PLUGINS_TOKEN → GH_AW_GITHUB_TOKEN → GITHUB_TOKEN. Governance detail → ch13.
  Source: reference/dependencies/ (https://github.github.com/gh-aw/reference/dependencies/).
- **repo-memory:** `tools: repo-memory: true` → Git-branch storage, UNLIMITED retention, versioned,
  `/tmp/gh-aw/repo-memory-default/`, auto-commit/push (GraphQL signed commits). vs **cache-memory:**
  Actions cache, 7-day, fast, not versioned. Comparison table verified.

## Example shape (verified)
Shared `triage-policy.md` (no `on:`; tools.github + safe-outputs) imported by thin workflow that adds
`repo-memory: true`. Merged into one self-contained lock at compile. Next: ch12 observability.
