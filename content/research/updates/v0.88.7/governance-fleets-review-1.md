# Governance and Fleets - Scoped Editorial Review

**Target:** gh-aw v0.88.7
**Reviewed:** 2026-09-16
**Scope:** Chapters 13-14, all Chapter 13 example inputs, and Chapter 14's workflow
and shared fragment. Not whole-book acceptance or publication authorization.

## Summary and evidence

The chapters teach the substantive governance and fleet concepts correctly.
Chapter 13 has no must-fix. Chapter 14 needs two narrow editorial corrections:
precise citations for installation/update behavior and removal of a stale visible
verification handoff. Neither requires redesigning examples or weakening controls.

Read the instructions, TOC/impact rows, historical briefs, theory E/G, framework
F04/F10/F13-F15, integration notes, final evidence, and cached tagged references.
No commands, compilation, installation, edits, metadata, attestations, or delegation.

## GF-1 - MEDIUM - Cite the actual package-precedence and ref-advancement contracts

**Location:** `content/chapters/fleets-and-adoption.html:58,62-75`.

The described behavior is supported, but the links do not establish two important claims:
the CLI guide's `#add` section does not state that added-package `aw.json` settings
take precedence over consumer settings, and the general CLI reference does not
explain branch versus commit-SHA source advancement.

These exceptions to consumer-governance and pinning assumptions need direct citations,
not removal or qualification into uncertainty.

**Evidence:** Captured target `add --help` states precedence; the tagged contract is in
[add_command.go:36-41](https://github.com/github/gh-aw/blob/v0.88.7/pkg/cli/add_command.go#L36-L41).
The tag/branch/SHA rules are explicit in
[update_command.go:35-46](https://github.com/github/gh-aw/blob/v0.88.7/pkg/cli/update_command.go#L35-L46),
consistent with F15.

**Fix / owner:** Chapter author: place those version-bound citations beside the
precedence statement and advancement table. Preserve the warnings that an installed
SHA does not freeze an explicit update and that `--no-release-bump` permits core
`actions/*` bumps. No new research or installation experiment needed.

## GF-2 - MEDIUM - Visible verification handoff is stale

**Location:** `content/chapters/fleets-and-adoption.html:206`.

The rendered callout says "fresh verification of the revised files is required before
acceptance." The preceding sentence reports only preflight compilation. The nearby
final-verification statement is an HTML comment and does not correct the visible status.

**Evidence:** `verification.json` records the current fleet source passing with exit
zero, nonempty lock, exact target metadata and strict true. The matching embed passes
in `embedded-verification.json`; shared-fragment copies and inputs match in the audit.
Only the provenance comment, not this paragraph, was tagged after verification.

**Fix / owner:** Chapter author: replace the pending sentence with the completed
source-and-embedded strict result. Retain no-engine invocation, possible network
resolution, and unverified installation/credentials/dispatch/fleet-operation limits.
Do not claim editorial or publication approval.

## Technical and teaching assessment

Final evidence supports 24/24 canonical and 16/16 embedded PASS, proper exit/lock/version/
strict gates, and no environment/cleanup errors. Policy fixtures and the policy embed
pass without a CLI strict override; the identical no-policy control records effective
false via `GH_AW_COMPILED_STRICT`. Omitting optional false metadata is documented
serialization, not a positive-gate exception.

All scoped complete workflows, shared fragment, JSON and APM YAML excerpts match their
sources. Explanatory bodies carry scoped-budget, synthetic-provenance, tracker and
memory limits. The audit retains unchanged compilation inputs through status tagging.

**Chapter 13:** Preserves 200/2000. Correctly marks 1000/5000/400 fallbacks as unchanged
baseline/target behavior. Separates main inference, detection, compute, step/job timeouts,
and non-atomic historical admission. Compiler defaults, runtime variables/gates and
strict policy have distinct enforcement points. Recompile/deploy and protection against
bypassing the compiler remain necessary. Models, auto, forecasts and billing prerequisites
are accurately scoped. APM 0.28.0 preview-policy/discovery, constraints/locks, glob denies,
context preparation, scanning and proxy limits are correct; no installation, homoglyph,
injection-proof or air-gap guarantee is invented.

**Chapter 14:** Preserves the maturity arc and imports. Distinguishes four formats and
uses `includes`; explains mapping/wildcard restrictions, collisions, resources and
add/wizard differences. Consumer updates are deliberate mutations, not propagation.
Synthetic provenance, tracker limits, repository memory, staged/real outputs and rollout
are bounded. Fleet statistics remain historical; v0.81.6 is not incorrectly included
in the blocked v0.82.8-v0.85.3 range.

## Closure boundary

Both chapters retain six sections, theory-before-syntax and useful Builder/Leader
guidance. No orphan capability or narrative rewrite is needed. Current framework
coverage v0.88.7 and intentionally pending prose-edition preparation are not blockers.

Close GF-1 and GF-2, then return the small citation/prose diff for scoped re-review.
Preserve passing example inputs and historical evidence. Any example or embedded-input
change requires corresponding verification.

Verdict: REVISE
