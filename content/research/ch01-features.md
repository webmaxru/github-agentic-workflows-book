# Chapter 1 — "What Are Agentic Workflows?" — Feature Reference Notes

- **Chapter:** `ch01-what-are-agentic-workflows` (Part I — The Individual)
- **Targets:** `gh aw` **v0.81.6** (Public Preview). Verified via `gh aw version` → `gh aw version v0.81.6`.
- **Prepared by:** gh-aw-explorer (produced inline by orchestrator after subagent-batch stall; facts
  drawn from the verified compile loop in `/memories/repo/gh-aw-book.md` + the ch02 verification).
- **Date:** 2026-07-02.
- **Role of this chapter:** thesis / vocabulary chapter. It introduces *concepts*; it does **not** teach
  syntax. So these notes deliberately stay at the "name the capability, link it to the concept, defer
  the depth" level. Each capability below is confirmed to exist in v0.81.6; deep syntax lives in the
  chapter that owns it (ch02–ch08).

---

## Capability → concept map (what ch01 may name, and where depth lives)

| Capability (v0.81.6) | Implements concept | Depth owned by | Verified how |
|---|---|---|---|
| **workflow file** = `.github/workflows/<name>.md` (YAML frontmatter + NL Markdown body) | 1 Agentic workflow; 4 vs. Actions | ch03 | ch02 example is exactly this shape; compiles 0/0 |
| **`gh aw compile`** (`.md` → `.lock.yml`, compiles *to* Actions, offline) | 4 gh-aw vs. Actions | ch02 (intro), ch03 (model) | `gh aw compile examples/ch02/...md` → `✓ 0 error(s)`, emits `.lock.yml` |
| **`engine:`** field; **Copilot is the default** (also Claude, Codex, Gemini) | 1 Agentic workflow | ch05 | Omitting `engine:` compiles; lock metadata shows `"agent_id":"copilot"` |
| **triggers `on:`** (issues, pull_request, schedule, workflow_dispatch, …) | 2 Inner vs. outer loop | ch04 | ch02 uses `on: issues: [opened]` + `workflow_dispatch`; compiles |
| **`safe-outputs:`** (writes via separate scoped jobs; read-only agent) | 5 Safe-by-default / HITL | ch06, ch07 | ch02 uses `add-comment`, `add-labels`; lock has a `safe_outputs` job separate from `agent` |
| **coding agents in GitHub Actions** (the runtime substrate) | 1, 2, 3, 4 | Part I | lock is a normal Actions workflow with `jobs:` graph |
| **strict mode** (default; refuses unsafe choices, supplies safe defaults) | 5 Safe-by-default (preview) | ch07 | lock metadata `"strict":true`; top-level `permissions: {}` |

**Author rule (from content conventions):** no orphan features. ch01 may *name* each capability only to
anchor a concept, and must forward-link the depth to the owning chapter. It must not show frontmatter
syntax tables or CLI flag lists — those belong to ch02+.

---

## Confirmed product facts ch01 can state (all verified on v0.81.6)

1. **Two artifacts, one source of truth.** You author a `.md`; `gh aw compile` produces a
   `.lock.yml` that is an ordinary, security-hardened GitHub Actions workflow. gh-aw *compiles to*
   Actions — it does not replace it. (Metadata header confirms `"compiler_version":"v0.81.6"`.)
2. **Copilot is the default engine.** No engine account setup beyond Copilot is needed for a first
   workflow. Lock metadata records `"agent_id":"copilot"`, `"engine_versions":{"copilot":"..."}`.
3. **Read-only by default; writes are mediated.** The compiled lock carries a top-level
   `permissions: {}` and routes writes through a *separate* `safe_outputs` job — the agent job never
   holds write scope. This is the concrete embodiment of "safe by default" (preview only in ch01).
4. **It runs as normal GitHub Actions.** The lock is inspectable YAML with a standard `on:` + `jobs:`
   graph — nothing hosted or hidden. Reinforces "gh-aw vs. Actions: additive, not a replacement."
5. **Continuous AI is the umbrella.** gh-aw is GitHub's vehicle for practicing Continuous AI; the
   named "Continuous X" patterns (Continuous Triage, Documentation, …) become individual workflows.
   (Concept-level only; the pattern library is Part II.)

---

## Worked-example anchor (reuses the ch02 example — no new example to verify)

ch01's "worked example" is a **reading**, not a new workflow: it walks the already-verified
`examples/ch02/repo-assistant-triage.md` top-to-bottom to show all five concepts embodied in one file
(outer-loop `on:` trigger, read-only `permissions:`, `engine: copilot`, mediated `safe-outputs:`, and a
plain-language Markdown body). No new example file is introduced, so there is **nothing new for the
code-verifier here** — the artifact it points at is already compile-verified (0 error(s), 0 warning(s),
100.5 KB) and gains a `workflow_dispatch` trigger so ch02's `gh aw run` demo is real.

---

## Notes / cautions for the author

- Keep every capability mention a *preview* with a forward-link; ch01's job is vocabulary, not syntax.
- Use the **verified** Repo Assist numbers from the theory brief (15 repos / 651 issues net / median
  9×) — never the outdated landing-page blurb (13/578/8×).
- Do not introduce `.lock.yml` internals here (jobs graph, SHA pins, metadata header) — that is ch03's
  worked example. ch01 may say only "it compiles to an ordinary, hardened Actions workflow."
