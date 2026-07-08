---
description: Cut a new versioned release of the book's CONTENT — bump the version, update the changelog, verify, and publish the GitHub Release with the PDF attached.
---

# Release Content

Publish a new **content version** of the GitHub Agentic Workflows interactive book. Versioning
applies to the **prose under `content/` only** — never the site generator, PDF tooling, analytics,
or any other part of the repo.

**What changed:** <one-line summary of the content edits, or "read the diff since the last release">
**Version bump:** <major | minor | patch, or an explicit `x.y` — decide from the rules below if unset>

## Versioning model (read first)
- **Source of truth:** `content/VERSION` — a single line, e.g. `1.1`.
- **History / release notes:** `content/CHANGELOG.md` — Keep-a-Changelog style; the release notes
  are generated from this file.
- **Shared helper:** `scripts/content_version.py` (`version` / `tag` / `notes`) — the stdlib-only
  parser used by the site generator, the PDF builder, and the release workflow.
- **Tag & Release:** each version ships as a GitHub Release tagged `content-vX.Y` with the matching
  single-file PDF (`gh-aw-book-vX.Y.pdf`) attached, so every past state stays reproducible.
- **Automation:** `.github/workflows/release-content.yml` cuts the release automatically when
  `content/VERSION` changes on `main`. It is idempotent (skips if the release exists) and
  self-healing (re-attaches the PDF if it went missing). You normally just prepare the bump — the
  workflow publishes.

**SemVer for prose** — pick the bump:
- **MAJOR** — structural rewrite or reordering of the book.
- **MINOR** — new chapters, sections, or material.
- **PATCH** — corrections and clarifications only.

## Steps
1. **Confirm the scope.** Show what content changed since the last release:
   `git diff $(python scripts/content_version.py tag)..HEAD -- content/`. Summarize it for the
   reader. If nothing under `content/` changed, **stop** — there is nothing to release.
2. **Pick the new version** `x.y` from the bump rules. The current version is
   `python scripts/content_version.py version`.
3. **Update `content/CHANGELOG.md`.** Add a new section at the very top (keep older entries intact):
   ```
   ## [x.y] - YYYY-MM-DD      (today's date)
   One-line summary of this release.

   ### Added / ### Changed / ### Fixed
   - **Bold lead:** what changed and why it matters to the reader.
   ```
4. **Bump `content/VERSION`** to `x.y` (single line, nothing else).
5. **Verify locally — all must pass:**
   - `python scripts/content_version.py version` → `x.y`; `python scripts/content_version.py notes x.y`
     prints your new notes.
   - `python site/generate.py` → clean build; the header version pill and `site/versions.html` show
     `vx.y`.
   - `python scripts/build_pdf.py` → the PDF running footer reads `vx.y`.
6. **Commit** the bump plus the regenerated site output: `content/VERSION`, `content/CHANGELOG.md`,
   and the changed `site/**` files. Message: `Release content vx.y`. Include the trailer
   `Co-authored-by: Copilot App <223556219+Copilot@users.noreply.github.com>`.
7. **Publish:**
   - **Preferred — merge to `main`.** Open a PR and merge it. The deploy workflow republishes the
     site (now showing `vx.y`) and `release-content.yml` builds the versioned PDF, pulls the notes
     from the changelog, and creates `content-vx.y` as Latest. Re-runs are safe (idempotent).
   - **Manual fallback** (only if you must publish without merging). Write the notes to a file
     **from Python** (capturing `python` stdout into a PowerShell variable mangles em-dashes on
     Windows), then:
     ```
     python scripts/content_version.py notes x.y   # write output to notes.md
     gh release create content-vx.y \
       "gh-aw-book-vx.y.pdf#GitHub Agentic Workflows — vx.y (PDF)" \
       --title "Content vx.y" --notes-file notes.md --target <content-commit-sha>
     ```
8. **Confirm.** `gh release list` shows `content-vx.y` as **Latest** with the PDF asset attached,
   and the online **Version history** page (`versions.html`) lists it.

**Guardrails:** never bump the version for non-content changes; never attach a PDF that predates the
content it claims to represent (that's why the first release, `content-v1.0`, ships notes-only —
the PDF feature postdated it).
