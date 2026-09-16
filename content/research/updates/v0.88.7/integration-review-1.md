# Global integration review - gh-aw v0.88.7

**Reviewed:** 16 September 2026
**Scope:** Final cross-chapter integration, not repeated individual reviews.

## Evidence and identity

Read all five accepted scope reports, all 14 impact decisions, brief/TOC/outline,
consolidated verification notes/receipt/audit, and selected current cross-references.
Reviewed fingerprint matching the receipt:

`2def13bdcd4ae16868df77fa6a14f361018accca6b2974948fb466be607f10e9`

This is snapshot identity, not an attestation/signature. FRAMEWORK is v0.88.7;
VERSION remains 1.1 pending packaging.

## Coverage

| Chapters | Accepted report |
| --- | --- |
| 01-05 | foundations-review.md |
| 06-08 | capabilities-review.md |
| 09-11 | patterns-memory-review.md |
| 12 | pilot-review.md |
| 13-14 | governance-fleets-review.md |

All prior scope findings are closed; every mapped update is accounted for. No
chapter was omitted, added or renamed. One integration defect prevents acceptance.

## GI-1 - MEDIUM - Broken tagged reference for follow-up CI

**Location:** `content/chapters/continuous-review-and-testing.html:213`.

The Human validation prerequisite links to `reference/triggering-ci.md`.
The target contains `triggering-ci.mdx`, not the Markdown filename. The explanation
is valid, but its supporting link targets a nonexistent path. Internal-link layout
checks do not cover this external tagged-reference defect.

**Fix / owner:** Author or orchestrator: use
https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/triggering-ci.mdx
and preserve the caveat. No workflow/credential change is needed.

## GI-2 - LOW - Clarify historical source label

**Location:** `content/chapters/continuous-triage-and-docs.html:234`.

The table says "checks on the unchanged sources, 15 September 2026" despite the
later triage-body revision. The date and focused caption provide context, but
"unchanged" is ambiguous beside the current recipe.

**Suggestion / owner:** Label historical checks on the then-current, pre-revision
sources. Preserve dates/warnings/outcomes. This does not independently block
acceptance or invalidate fresh compilation.

## Cross-chapter consistency

The shared model is otherwise coherent: human merge is book policy; repository
authority differs from workspace/tool actions; main/detector inference is
probabilistic; controls reduce rather than eliminate exposure; portable intent
does not imply interchangeable engines; admission/concurrency/budgets are distinct;
cost scopes and forecasts are not total bill caps; reuse/APM/plugins/formats and
lifecycles are separate; compilation, context, runtime and approval are not conflated.

Fourteen slugs, six-slot structures and dependency progression agree. Complete
examples map to sources; historical reports/outline remain historical.

## Boundary

Technical evidence is 24/24 canonical and 16/16 embedded PASS with exact strict/
version metadata, locks, zero exits and no environment/cleanup errors. Policy
controls discriminate without forced strictness; non-MD inputs are bound.
Draft layout reports 84 slots, 1,059 internal references, 92 highlighted blocks and
desktop/mobile coverage, not the final 1.2 build.

Must-fix GI-1. After correction, confirm unchanged compilation inputs and obtain a
narrow integration re-review at the new fingerprint. No compilation/runtime rerun
requested; packaging/attestation/publication are not completed by this review.

Verdict: REVISE
