# Slack MCP and APM: bounded integration handoff

**Inspected 2026-09-16:** gh-aw **v0.88.7**; installed APM CLI **0.28.0**.
APM is independently versioned: [release v0.28.0][apm-release], published
2026-08-06, source commit `e041462f4a48086dbee3da145c07d71b8a3b84fd`.
The APM skill and its command, manifest/lockfile, and troubleshooting references
were read before APM operations.

**Concept links:** [capability versus exposure](../../ch08-features.md#concept-theory),
[governed reuse](../../ch11-features.md#concept-theory), and
[agent-context supply-chain governance](../../ch13-features.md#concept-theory).
This closes the scoped gaps in F08/F10/F14 of [framework-delta.md](framework-delta.md);
it does not certify runtime integrations.

## Chapter 8: remove the guessed Slack installation command

The current `npx -y @slack/mcp-server`, `SLACK_BOT_TOKEN`,
`send_message`/`get_channel_history` combination has **no verified package version
or tool contract** here. Registry requests failed TLS negotiation—not a 404—so
do not assert the package is nonexistent either. Nothing was installed.

[Slack's official documentation][slack], read on the inspection date, describes
JSON-RPC over **Streamable HTTP** at `https://mcp.slack.com/mcp`, confidential OAuth
with user authorization, and no SSE/Dynamic Client Registration. This does not
establish compatibility with the chapter's npm/bot-token recipe or unattended Actions
authentication.

**Smallest honest edit:** retain Slack as an optional use case; replace its
copy-ready command with explicitly illustrative MCP configuration. The
[target gh-aw transport schema][gh-mcp] supports this independently of Slack:

```yaml
# Frontmatter excerpt: illustrative HTTPS MCP, NOT a working Slack integration.
mcp-servers:
  example:
    url: https://mcp.example.invalid/mcp
    allowed: [lookup_reference]
network:
  allowed: [defaults, mcp.example.invalid]
```

The complete `mcp-shape.md` fixture strictly compiles. Endpoint and tool name are
deliberate placeholders; provider authentication and a real tool catalog remain
required. Do not describe remote HTTP transport as a locally isolated server
container, or expose an unreviewed write tool merely to demonstrate MCP.

## Chapter 11: use the real, separately pinned APM bridge

The [gh-aw v0.88.7 reference][gh-apm] supports a **local vendored shared component**
plus `imports` → `uses`/`with` → `packages`. It is not built-in APM dependency
installation during `gh aw compile`.

We inspected and compiled the [canonical component at APM v0.28.0][shared].
It uses **apm-action v1.10.0**, not the v1.5.0 named in gh-aw's older description.
Its default APM CLI input is 0.21.0; override it explicitly. `target` is also
explicit below rather than relying on conflicting target-inference prose.

```yaml
# Frontmatter excerpt from apm-bridge-pinned.md.
imports:
  - uses: shared/apm-pinned.md
    with:
      apm-version: "0.28.0"   # bare CLI version, applied to pack AND restore
      target: copilot
      packages:
        - microsoft/apm-sample-package#fb2851683be0e0e7711421d518bd8dba23b0b1f6
```

`apm-pinned.md` is the canonical `shared/apm.md` with only its two apm-action
references resolved to [commit `d723bb64…`][action-pin] for v1.10.0. Keep the
conventional filename `shared/apm.md` when vendoring if preferred; update the import
accordingly. The unchanged canonical component also compiled, but its apm-action
reference remained a version tag, so do not claim every action became SHA-pinned
automatically.

The [sample package and its commit exist][sample]. This is a **direct** dependency
pin: its manifest contains an unpinned transitive dependency. Compilation neither
installs that graph nor proves repeatable transitive resolution.

For a normal APM project, the separate [manifest contract][manifest] is:

```yaml
# apm.yml, NOT gh-aw frontmatter
name: example-context
version: 1.0.0
dependencies:
  apm:
    - microsoft/apm-sample-package#fb2851683be0e0e7711421d518bd8dba23b0b1f6
```

Use `#ref` for APM packages, versus `@ref` for remote gh-aw imports. Replace the
unverified `anthropics/...#v2.0` example rather than treating an illustrative tag as
an established release.

**Correct the lock claim:** the filename is **`apm.lock.yaml`**, not `apm.lock`.
It records resolved commits, transitive dependencies, deployment paths and hashes.
`apm install --frozen` rejects missing/out-of-sync locks; `apm audit` checks
installed integrity ([lock specification][lock]). That is not a security approval.
Do not assume the shared component's isolated inline-package path replays the
host repository's committed lock; show that the chosen install actually consumes it.

The compiled bridge contains `apm-prep` and `apm` jobs plus an agent restore step.
Resolution, installation and packing occur **when Actions runs those jobs**, not
during local gh-aw compilation.

## Chapter 13: narrow the governance promises

- **Policy is preview/version-sensitive.** In APM 0.28.0, configured `extends`
  chains merge tighten-only; do not promise automatic discovery at every
  repo/org/enterprise level. The [implementation][discovery] derives the owner
  from the remote and tries `.github-private` before `.github` and other
  candidates. Policy-fetch failure defaults can warn rather than block
  ([policy reference][policy]).
- **Remove the misleading `deny: ["*"]` line.** The [matcher][matcher] gives `*`
  single-segment semantics and `**` cross-segment semantics. The nonempty
  allowlist already rejects unmatched sources. Replacing `*` with `**` would
  deny approved sources too: matching denies take precedence. A pure-source
  diagnostic confirmed these three cases.
- Keep `dependencies.require_pinned_constraint: true`, but explain it requires
  **bounded constraints**, not necessarily exact SHAs. Locking remains separate.
- **`isolated: true` belongs to apm-action**, not a per-skill gh-aw import option.
  The [action contract][action] ignores host `apm.yml` and clears known `.github`
  primitive directories; the shared bridge enables it for packing. This is
  context-preparation isolation—not a general agent sandbox or proof that
  repository instructions cannot influence a model.
- [APM content scanning][security] detects specified hidden Unicode; critical
  findings block deployment, some warnings do not. **Homoglyph detection is
  explicitly excluded.** Remove that claim and blanket prompt-injection guarantees.
- `PROXY_REGISTRY_ONLY=1` restricts direct VCS fallback/replay, but policy-file
  fetching still uses GitHub APIs ([proxy contract][proxy]). It does not make
  the entire workflow air-gapped.

## What was actually validated

Three full diagnostic workflows emitted strict v0.88.7 locks: illustrative MCP,
canonical APM bridge, and SHA-pinned-action bridge. The final bridge's pack/restore
steps both carry APM **0.28.0**. APM cases emitted review warnings for
`GH_AW_PLUGINS_TOKEN`/`microsoft/apm-action`, plus an outdated App-action notice;
warnings were preserved, not approved away.

Only APM CLI version/help and `config get auto-integrate` were invoked. **No APM
install/update/compile or policy bypass was performed.** No engine/integration
credentials were supplied; no live MCP connection or workflow run occurred.
No full-graph installation, policy enforcement, or provider authentication success
is claimed.

**Evidence root:** session `files/integrations-v0.88.7/`. Fixtures:
`probe/.github/workflows/{mcp-shape,apm-bridge,apm-bridge-pinned}.md` and `shared/`.
Results: `compile-results.json`, `compile-pinned-result.json`,
`final-compiled-invariants.json`, `policy-matcher-result.json`. Compile invocation:

```powershell
# In the isolated diagnostic repository; $aw is the verified session compiler.
& $aw compile .github/workflows/apm-bridge-pinned.md --strict --no-check-update `
  --schedule-seed webmaxru/github-agentic-workflows-book --json
```

Parent/authors should preserve MCP/APM coverage with these qualifications, then
route any adopted complete example through the verifier. No book manifest,
chapter, example, tooling, or test file was edited in this follow-up.

[apm-release]: https://github.com/microsoft/apm/releases/tag/v0.28.0
[slack]: https://docs.slack.dev/ai/slack-mcp-server/
[gh-mcp]: https://github.com/github/gh-aw/blob/v0.88.7/pkg/parser/schemas/main_workflow_schema.json
[gh-apm]: https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/dependencies.md
[shared]: https://github.com/microsoft/apm/blob/e041462f4a48086dbee3da145c07d71b8a3b84fd/.github/workflows/shared/apm.md
[action-pin]: https://github.com/microsoft/apm-action/commit/d723bb64ed70c135bbaf87d126b721dd2dae0439
[action]: https://github.com/microsoft/apm-action/blob/v1.10.0/action.yml
[sample]: https://github.com/microsoft/apm-sample-package/blob/fb2851683be0e0e7711421d518bd8dba23b0b1f6/apm.yml
[manifest]: https://github.com/microsoft/apm/blob/v0.28.0/docs/src/content/docs/reference/manifest-schema.md
[lock]: https://github.com/microsoft/apm/blob/v0.28.0/docs/src/content/docs/reference/lockfile-spec.md
[policy]: https://github.com/microsoft/apm/blob/v0.28.0/docs/src/content/docs/enterprise/policy-reference.md
[discovery]: https://github.com/microsoft/apm/blob/v0.28.0/src/apm_cli/policy/discovery.py
[matcher]: https://github.com/microsoft/apm/blob/v0.28.0/src/apm_cli/policy/matcher.py
[security]: https://github.com/microsoft/apm/blob/v0.28.0/docs/src/content/docs/enterprise/security.md
[proxy]: https://github.com/microsoft/apm/blob/v0.28.0/docs/src/content/docs/enterprise/registry-proxy.md
