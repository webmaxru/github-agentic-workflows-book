# Book release canvas

This project-scoped Copilot extension turns repository evidence into a release-control Canvas for documentation-led publications.

## Open it

After the extension is loaded, ask Copilot to open the **Book release canvas**, or call the canvas with:

```text
canvasId: book-release-canvas
instanceId: book-release
```

The default configuration is `.book-release-canvas.json`. An alternate repo-relative file can be passed as `configPath` when opening the Canvas.

## Reuse it

Copy the extension directory and `.book-release-canvas.json` into another repository. Configure:

- publication version and content paths;
- documentation source areas and their evidence;
- demo dependencies and proof artifacts;
- release gates;
- agent roles; and
- the challenge/business proof displayed in the Canvas.

All configured paths are constrained to the repository. The extension binds its server to loopback only, requests no secret, and stores human demo decisions under the user's Copilot extension artifacts instead of editing committed evidence.

## Actions

- `refresh_release` — rescan git and configured evidence.
- `get_release_snapshot` — return the complete structured state.
- `set_demo_status` — persist a human `ready`, `needs-refresh`, or `blocked` decision.

## Test

```powershell
npm run test:canvas
```
