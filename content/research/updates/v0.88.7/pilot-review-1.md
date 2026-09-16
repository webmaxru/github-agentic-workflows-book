# Chapter 12 pilot editorial/technical review

**Target:** gh-aw v0.88.7
**Review date:** 16 September 2026
**Scope:** Chapter 12 only; read-only review, not whole-book acceptance or deployment authorization.

## Scope and evidence

Reviewed `content/chapters/observability-and-debugging.html` and
`examples/ch12/repo-assistant-observable.md` against the applicable content/example
instructions; `framework-delta.md` F07/F12, Chapter 12 impact row and verification
limits; `impact.json`; and `theory-delta.md` concepts A/F and scope. Historical
Chapter 12 research and preflight evidence were treated as dated records, not relabeled.

Fresh evidence examined: `pilot-diagnostics.md`, `pilot-verification.json`,
`pilot-embedded-verification.json`, `pilot-embedded-inventory.json`,
`pilot-cli-verification.json`, captured `pilot-cli-help.json`, and the verification
summary. Cross-checks included cached v0.88.7 threat-detection, artifact, audit and
OpenTelemetry references, tagged CLI command definitions, and the incomplete-work
handler/commit.

The technical gate passes for the reviewed inputs: **14/14 canonical workflows and
3/3 complete embedded workflows**, verifier exit zero, nonempty locks, exact
`compiler_version: v0.88.7`, and boolean `strict: true`, without environment or
cleanup errors. Chapter 12's embedded block matches its source after documented
normalization; emitted frontmatter/body hashes agree. Four help captures, 24 recipe
checks and 22 help-only probes pass. These are not operational command tests.

Chapter 12 emits **one warning naming two restricted secrets**, `OTLP_ENDPOINT` and
`OTLP_TOKEN`; neither values nor approval were supplied. Runtime, optional
validation/scanners/Docker checks, and telemetry delivery remain unverified.

## Severity-ranked findings

### 1. HIGH - The replacement inference model is not taught

**Location:** `content/chapters/observability-and-debugging.html:13`, with consequences
for the detection-artifact explanation at line 67 and inspection guidance at line 98.

The chapter removes the old "one non-deterministic job" assertion, but never states
its essential replacement: **both the main agent and the default threat detector
perform separate AI inference**. "Reviewable job plan" is correct but insufficient.
Readers subsequently encounter the threat-detection gate among routine signals
without learning that its judgment is also fallible.

**Evidence:** `theory-delta.md` section A explicitly assigns this distinction to
Chapter 12; `framework-delta.md` F07 records AI analysis in `detection`. The
[tagged threat-detection reference](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/threat-detection.md)
confirms default AI-powered analysis.

**Fix / owner:** **Chapter author.** Add a short explanation before the CLI material
distinguishing deterministic orchestration from separate, probabilistic main-agent
and detector judgments. Connect it to investigation: inspect both outcomes; a
detector verdict is supporting evidence, not deterministic proof of safety.
This is a local pilot requirement, not a demand to finish Chapter 3 now.

### 2. MEDIUM - The complete example reintroduces an evidence-completeness promise

**Location:** `examples/ch12/repo-assistant-observable.md:32-33`, reproduced at
`observability-and-debugging.html:189-190`.

The example says combining telemetry, logs and audit gives "a full picture of what
the agent did and why." That unqualified promise contradicts the chapter's otherwise
careful account of omitted, redacted, unavailable and pruned evidence. A configured
collector does not recover evidence that was never captured.

**Evidence:** Chapter lines 64-67, 85 and 209; `theory-delta.md` section F; the tagged
artifact reference's deliberate omission of raw external-detection logs.

**Fix / owner:** **Chapter author.** Qualify the example's explanatory body as
providing complementary evidence for investigation, subject to collection and
retention limits. Synchronize the embedded copy. Keep the YAML configuration
unchanged; adjust "unchanged workflow" and verification-provenance wording where
necessary. Preserve historical reports rather than rewriting them to cover revised source.

## What should be retained

The six original slots, Repo Assistant narrative, Leader retention guidance and
Builder "start narrow, then widen" path remain useful. The overview, audit and
corroboration sequence teaches an investigation rather than merely listing commands.

The CLI explanations correctly distinguish usage-only logs from audit's default
comprehensive artifact selection; per-workflow counts from date windows; MB/cache
deletion controls from core-API used-request thresholds and negative reserves; and
both from model budgets. Repository context, cached-report limitations and
non-offline downloads are appropriately explicit.

The chapter also correctly separates `noop` from incomplete work, labels the metrics
and failure scenario illustrative, requires investigation before allowlisting egress,
and distinguishes strict compilation from runtime success and secret approval.
These qualifications should survive revision.

## Cross-chapter followups and completion

All 14 impact decisions are accounted for: Chapter 12 is this pilot; Chapters 1-11
and 13-14 remain queued. Their age alone does not block it. Final integration must
align Chapter 3's inference/offline claims, Chapter 7's detection/egress boundaries,
Chapter 11's evidence lifecycle, Chapter 13's budget scopes, and current-facing
framework statements. Historical inspected versions must remain intact.

**Pilot must-fixes are limited to findings 1-2:** add the missing conceptual
distinction, qualify and synchronize the example text, then obtain renewed
verification evidence and scoped review for changed inputs. No metadata advance,
global acceptance, deployment, or publication follows from this report.

Verdict: REVISE
