# Running the Book Fleet Autonomously

This folder holds launchers that run the book's **agent fleet** unattended in the backend.

The autonomy model has three layers:

| Layer | What it is | How it activates |
|-------|------------|------------------|
| **Instructions** | `.github/copilot-instructions.md`, `.github/instructions/*` | Auto-loaded into every agent |
| **Skills + agents** | `.github/skills/*/SKILL.md`, `.github/agents/*.agent.md` | Auto-discovered; the orchestrator invokes them on demand |
| **Driver** | `.github/prompts/run-playbook.prompt.md` | The one prompt you launch; it orchestrates everything |

You only ever launch the **driver**. It reads the `playbook-orchestration` skill and dispatches the
seven agents in waves, using the session `todos` / `inbox_entries` tables as a shared, resumable
state board.

## Launch (headless / programmatic)

`copilot -p` runs a single prompt to completion and exits — ideal for a backend fleet.
`--allow-all-tools` lets it install the `gh aw` extension, compile workflows, and commit without prompts.

```powershell
# from the repo root
copilot -p "$(Get-Content -Raw .github/prompts/run-playbook.prompt.md)" --allow-all-tools
```

```bash
# bash equivalent
copilot -p "$(cat .github/prompts/run-playbook.prompt.md)" --allow-all-tools
```

Or use the wrapper in this folder:

```powershell
./scripts/run-fleet.ps1
```

## Parallelism (fleet mode)
The driver enables parallel subagents so independent work runs concurrently — e.g. theory +
capability research for a chapter, or several chapters in the same wave. Interactively you can also
toggle this with `/fleet`. In headless mode the driver requests it itself.

## Resumability
State lives in `todos` + git checkpoints (one commit per chapter). Re-launching the driver is
idempotent: it skips `done` todos and resumes from the first ready item. If the process dies
mid-wave, just run it again.

## Safety notes
- `--allow-all-tools` grants the same access you have. Prefer running the fleet inside a sandbox
  (`copilot --cloud`, or `/sandbox enable`) or a container if you want isolation.
- Engine keys for real workflow runs go in GitHub Actions secrets; the book's examples validate at
  compile time (`gh aw compile`), so a full run needs no secrets unless you want examples to
  execute real workflows.
