# Capabilities batch editorial/technical review

**Target:** gh-aw v0.88.7
**Reviewed:** 16 September 2026
**Scope:** Chapters 06-08 only; read-only review.

## Scope and evidence

Reviewed the three chapters, relevant TOC entries, seven standalone sources, adjacent
Chapter 7 policy, and excerpt contexts. Applied impact decisions, theory B/D, framework
F05-F09/F14 and the Chapter 8 integration handoff, with targeted tagged-reference/help
checks rather than new release archaeology.

Technical evidence remains valid for the reviewed inputs: 24/24 canonical and 16/16
complete embeds passed, with exact version, literal strict metadata, nonempty locks,
zero exits and no environment/cleanup errors. Relevant hashes agree.

Two policy sources and one embed passed without CLI strict. The identical no-policy
control separately emitted effective `GH_AW_COMPILED_STRICT: "false"`; optional false
metadata omission is not accepted as a positive strict result. The audit/receipt
account for verification-only annotations. Current framework metadata is v0.88.7;
historical records retain their pre-advance metadata.

## 1. MEDIUM - Ch08 source overstates safe-output mediation

**Location:** `examples/ch08/repo-assistant-tools.md:38-41`, especially
"every action still lands through `safe-outputs:`."

The footer conflates tool execution with mediated repository writes. The same source
asks for GitHub searches and page fetches; those read/network operations use their
tool interfaces, not deferred safe-output handlers. The chapter separates these
boundaries, but the reusable source does not.

**Evidence:** Source steps 28-33; `tools-and-mcp.html:126`; tagged Safe Outputs
describes structured write requests handled by permission-controlled jobs. Theory D
distinguishes transport and authority.

**Fix / owner:** Chapter 8 author: limit the footer claim to the intended triage
comment/repository-write request and explain the separate read/fetch tool/network
boundaries. Keep YAML and task instructions. Correct current-source/preflight provenance
and obtain fresh source-specific compilation rather than relabeling history.

## 2. MEDIUM - Ch08 reintroduces eliminated-exfiltration wording

**Location:** `content/chapters/tools-and-mcp.html:125`.

Broad egress is said to "reopen the exfiltration leg you closed in Chapter 7."
Chapter 7 correctly teaches constrained, not eliminated, exposure. Allowed destinations
remain reachable; permitted requests or comments can disclose information.

**Evidence:** `defense-in-depth.html:20-22,56-58`; F07 warns that allowed hosts can
remain data sinks and a firewall is not a no-leakage guarantee.

**Fix / owner:** Chapter 8 author: describe broader egress as increasing remaining
exposure or weakening a constrained boundary. Retain review of destinations and
transmitted data before widening; no configuration expansion.

## 3. MEDIUM - Ch07 audit recipe omits explicit repository context

**Location:** `content/chapters/defense-in-depth.html:105`.

"In the run's repository context" precedes `gh aw audit <run-id>`, suggesting working
directory alone supplies context. The target's bare-ID recipe explicitly supplies
`--repo owner/repo`; the shown command has neither that flag nor a full run URL.

**Evidence:** Captured target audit help in `pilot-cli-help.json` labels the bare-ID
example "--repo required"; F12 and the accepted Chapter 12 use explicit context.

**Fix / owner:** Chapter 7 author: use `gh aw audit <run-id> --repo owner/repo` or a
full run URL, explain placeholders, and preserve investigation-before-allowlisting.
Help/source evidence suffices; do not execute an operational audit to repair wording.

## Mapped coverage

**Ch06:** Substantively sound. Least privilege and propose/validate/apply precede
syntax. Repository authority is separate from workspace edits and harmlessness.
Labels/provisioning, per-run caps, fallbacks, staged costs/overrides, draft policy
and COMMENT-only constraints are clear. Prompt scope differs from publication file
controls. The complete source matches; good-first-fix remains prompt policy, manual
dispatch lacks an issue, CI restrictions are not exclusive, and PR failure can
fall back to an issue. No must-fix identified.

**Ch07:** Correct central model, one recipe correction. Default rootless Docker and
exceptional host access are distinct; egress, proxy, mediated tools and other jobs
are separated. Detector inference/budget, artifact limits, strict policy requiring
regenerated deployment, and compatibility range/minimum are accurate. Diagnostic
sources remain compile-only rather than whole-workflow offline/no-write promises.
The noop automatic-issue-fallback warning should remain.

**Ch08:** Strong structure with residual boundary overclaims. Capability/exposure
precedes engine/transport syntax. Bash restrictions are preserved by choosing a
supporting engine. Process/container/HTTP trust differs. Playwright CLI/version
semantics and 0.1.18 versus stale references are correct, without runtime browser
claims. Illustrative MCP says not to run it; Slack authentication/transport is
date-scoped and registry TLS failure is not represented as package absence.

## Completion

The chapters preserve six slots, progression, Repo Assistant and useful reader
callouts. Full sources versus excerpts are clear. Runtime/scanner/credential/approval
limits and warnings remain unwaived.

Must-fixes are 1-3 only. Correct the source footer and two passages, refresh affected
source evidence, and return scoped deltas for re-review. Preserve historical reports.
No global acceptance, metadata/attestation change, runtime or publication authorization.

Verdict: REVISE
