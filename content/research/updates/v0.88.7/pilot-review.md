# Chapter 12 pilot - scoped re-review

**Target:** gh-aw v0.88.7
**Reviewed:** 16 September 2026

This read-only re-review covers only findings 1-2 from `pilot-review-1.md`, their
source/embedded revisions, and the four verification-status replacements. It does
not reopen the full review.

## Findings closed

### 1. HIGH - Inference model: CLOSED

**Current location:** `content/chapters/observability-and-debugging.html:14`.

Before introducing CLI syntax, the chapter now explicitly distinguishes inspectable
orchestration from separate, probabilistic inference by both the main agent and
default threat detector. The tagged citation supports this distinction. The
instruction to inspect both outcomes alongside available artifacts connects the
concept to investigation without treating detection as deterministic proof of safety.

### 2. MEDIUM - Evidence-completeness promise: CLOSED

**Current locations:** `examples/ch12/repo-assistant-observable.md:29-34`; matching
embedded paragraph at `observability-and-debugging.html:187-192`.

The replacement describes complementary evidence about observable activity and
reported outcomes, bounded by collection, redaction and retention. It removes the
unsupported completeness promise and conditions trace export on runtime
configuration. YAML remains unchanged.

The status replacements at chapter lines **8, 158, 202 and 215** accurately describe
fresh compilation. Historical preflight results remain explicitly historical rather
than being attributed to revised source.

## Verification and consistency

`pilot-revision-verification.json` and `pilot-revision-diagnostics.md` establish
**2/2 strict compilation PASS**, overall PASS and exit zero, nonempty locks, exact
`compiler_version: v0.88.7`, boolean `strict: true`, and no environment/cleanup
errors. Source and embedded compilation hashes agree; status tagging did not change
those inputs.

All eight command blocks and 24 recipes remain unchanged, supporting reuse of the
earlier help-only evidence. Each compilation retains one warning naming
`OTLP_ENDPOINT` and `OTLP_TOKEN`; no approval or live operation occurred. Runtime,
optional validation/scanners/Docker checks and telemetry delivery remain unverified.

The six slots and 18 earlier evidence files are preserved. No new substantive issue
was introduced by these fixes.

**Final chapter SHA-256 recorded by the verifier:**
`68453b41dbaeaeb8f2ea605d6f4a0b336edbf2314072384cea8ddbd390a0651d`

**No unresolved pilot must-fixes remain.** Acceptance is for Chapter 12 only, not
global acceptance, secret approval, runtime authorization or publication permission.
Other chapters remain queued as previously acknowledged.

Verdict: ACCEPT
