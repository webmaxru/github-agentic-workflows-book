# AW Release Truth Canvas

This project-scoped Copilot extension shows release evidence for the
GitHub Agentic Workflows book only. It is not the cross-book Book control
center, which is a separate user-scoped extension.

## Open it

After the extension is loaded, ask Copilot to open the **AW Release Truth
Canvas**, or call the canvas with:

```text
canvasId: book-release-canvas
instanceId: book-release
```

The default configuration is `.book-release-canvas.json`. An alternate repo-relative file can be passed as `configPath` when opening the Canvas.

## Scope

This canvas reads `.book-release-canvas.json` and evidence from this repository.
Do not copy it into other book repositories; the cross-book Book control center
is the shared view for all four books. All configured paths are constrained to
the repository. The extension binds its server to loopback only, requests no
secret, and stores human demo decisions under the user's Copilot extension
artifacts instead of editing committed evidence.

## Actions

- `refresh_release` — rescan git and configured evidence.
- `get_release_snapshot` — return the complete structured state.
- `set_demo_status` — persist a human `ready`, `needs-refresh`, or `blocked` decision.

## Test

```powershell
npm run test:canvas
```
