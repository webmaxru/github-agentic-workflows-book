---
name: gh-aw-environment-setup
description: Set up an exact, isolated GitHub Agentic Workflows compiler for capability exploration and whole-book example verification; never install a moving latest version mid-update.
---

# gh-aw Environment Setup

Use the real compiler, with the **same exact version** for research, authors' probes, and
verification. Installing or recording an arbitrary local version is not pinning.

## Resolve the version before installation

- For the current book, read the exact tag in `content/FRAMEWORK_VERSION`.
- For an incremental update, use the fixed target saved by `update-book` under
  `content/research/updates/<target>/impact.json`. The baseline file is advanced only after
  the whole example corpus passes against that target.
- Do not resolve `latest` in an installer or during a later wave. Do not follow upstream
  `main` when confirming behavior of a released target.

## Windows: isolated, checksum-verified compiler

From the repository root:

```powershell
# Defaults to content\FRAMEWORK_VERSION; does not replace the personal gh extension.
.\scripts\install-gh-aw.ps1

# An update explicitly selects its already-resolved target.
.\scripts\install-gh-aw.ps1 -Version v0.88.7
```

The installer prints the exact executable path. Pass it explicitly to every probe and to
the verifier. `-InstallDir <absolute-path>` supports a session-owned tools directory.
Downloads are checked before activation, and the installed binary must report the requested
version. Do not bypass checksum, version, authentication, or organization-policy failures.

```powershell
& <absolute-gh-aw-executable> version
& <absolute-gh-aw-executable> compile --help
python scripts\verify_examples.py --compiler <absolute-gh-aw-executable>

# Before advancing the baseline, supply the saved update target explicitly:
python scripts\verify_examples.py --compiler <absolute-gh-aw-executable> --version v0.88.7 --report <verification-json>
```

Keep binaries, raw downloaded sources, and generated locks out of git. The helper's default
cache is worktree-local and ignored. Never overwrite a personal compiler used by another
session merely to make this task's commands shorter.

## Fresh CI runner: pinned gh extension

On a dedicated runner with `gh` available:

```bash
version="$(cat content/FRAMEWORK_VERSION)"
gh extension install github/gh-aw --pin "$version"
gh aw version
python scripts/verify_examples.py
```

An existing mismatched extension is a blocker until an explicitly scoped replacement is
performed. The verifier checks the actual version; a printed installation command is not
evidence that the requested version ran.

## Explore and verify

Read `--help` from the selected executable for commands/flags before using them. Inspect
the tagged workflow/frontmatter schema, safe outputs, triggers, engines, and sample workflows.
Record the exact tag, source URLs, and actual commands in new versioned research.

`scripts/verify_examples.py` stages each standalone example and its shared imports in an
isolated temporary git repository, invokes strict compilation, and requires an emitted
`.lock.yml` whose metadata confirms the compiler version and effective strict mode.
It does not add temporary workflows to the book's real `.github/workflows`.
Run the complete corpus for a framework update, not only modified examples. Require both
overall report PASS and exit zero; setup/cleanup failures retain diagnostics but fail the run.
The report records the sanitized repository context used by the fixture.

The canonical gate is **strict source compilation**, not optional `--validate`, image/
scanner checks, or live execution. Repository features (for example, Issues support),
Docker availability, and runtime credentials are separate prerequisites. A skipped optional
validator is not evidence that a deployment environment supports the feature. Preserve
stderr approval warnings as well as structured output; never auto-approve secret exposure.

## Credentials and reproducibility

- Compilation is not a live workflow execution. Never run `gh aw run` during verification.
- Engine secrets are needed only for actual runs and belong in Actions secrets, not files.
- Missing runtime credentials do not excuse an invalid frontmatter/compile failure.
- Preserve historical versioned evidence. Do not search-and-replace old compiler versions
  to imply they were reverified.
- Read-only `gh` requests may still require repository authentication; report blocked
  access explicitly rather than treating an API error as an empty release history.

## References

- Releases: https://github.com/github/gh-aw/releases
- Docs: https://github.github.com/gh-aw/
- Tagged source: `https://github.com/github/gh-aw/tree/<exact-tag>`
- GitHub CLI pinning: https://cli.github.com/manual/gh_extension_install
