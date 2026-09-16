# Patterns and Memory - Scoped Review

**Reviewed:** 2026-09-16
**Framework target:** gh-aw v0.88.7
**Scope:** Chapters 09-11, seven standalone workflows under `examples/ch09`-`ch11`,
and `examples/ch11/shared/triage-policy.md`.

This is a read-only editorial and technical review. No files were changed, commands
compiled, approvals granted, metadata advanced, or publication actions taken.

## Summary and evidence

The batch substantially satisfies its learning objectives and addresses the fixed-target
impact map. Chapters 10 and 11 have no must-fixes identified. Chapter 09 has one MEDIUM
must-fix: its executable daily-sweep prompt requests more acknowledged triage work than
its comment limit permits. Preserve the narrow authority rather than increasing limits.

Reviewed the content/example instructions, TOC objectives, historical notes, impact rows,
theory-delta C/E/F/G, framework-delta F02/F05/F08/F10/F11/F12/F13, and APM integration
handoff. Technical evidence includes `verification.json`, `verification-notes.md`,
`embedded-verification.json`, `verification-audit.json`, `final-verification-receipt.json`,
and `max-stack-verification.json`.

The recorded gate is 24/24 canonical and 16/16 complete embedded workflows PASS, including
all scoped workflows and five complete scoped embeds, with exact version, literal strict
metadata, nonempty locks, exit zero, and no environment/cleanup errors. Two Ch10 stack
contexts pass. Retained context/excerpt and help checks were reused after input matching.
Complete embeds and the shared fragment were compared with their sources, including bodies.

This establishes source compatibility, not consistency between requested work and permitted
effects. No runtime or deployment success follows from compilation.

## R1 - MEDIUM - Daily triage exceeds its one-comment-per-run contract

**Locations:**
- `examples/ch09/continuous-triage.md:19-24,32-37`
- `content/chapters/continuous-triage-and-docs.html:83,151,162-167`

The source asks the daily sweep to triage "the few clearest ones the same way." The
preceding issue-event instructions define that as posting one triage comment and applying
fitting labels for each issue. However, `safe-outputs.add-comment.max: 1` permits only
one comment in the run.

The HTML correctly says limits remain per-run, but that does not repair the copied
workflow's conflicting task. An agent following the multiple-issue instruction cannot
complete acknowledgment for every selected issue.

**Evidence:** The [v0.88.7 comment-output reference](https://github.com/github/gh-aw/blob/v0.88.7/docs/src/content/docs/reference/safe-outputs.md#comment-creation-add-comment)
defines the limit. The [target handler](https://github.com/github/gh-aw/blob/v0.88.7/actions/setup/js/add_comment.cjs#L552-L575)
tracks processed comments and skips subsequent requests with `MAX_COUNT_REACHED`.
The retained compiled configuration contains `add_comment.max: 1`.

This is a source/prompt inconsistency, not a claim that a live sweep failed.

**Fix / owner:** Chapter author: retain the limits and select **at most one clearly
eligible issue per run**, complete its comment/label triage, and leave remaining
candidates for later runs. Preserve no-work behavior when none qualifies. Synchronize
the complete HTML copy and surrounding description.

Do not increase limits, widen permissions, or weaken strict mode. Code verifier: refresh
affected source/embedded proof; return the revision for scoped review.

No CRITICAL or HIGH findings were identified.

## Chapter decisions and retained material

**Chapter 09:** The mini-product concept precedes recipe composition. Issues-enabled
practice/deployment requirements, book Issues being disabled, labels, authentication,
repository policy, and source-versus-deployment validation are separated. Admission is
not concurrency/spending enforcement; urgent triage is not slowed by a global cooldown.
Staged costs and successful no-work, completed escalation, and incomplete work are
distinguished. Docs-only intent is not represented as a mechanical file boundary.
R1 is the remaining operating-contract gap.

**Chapter 10:** The quality-loop objective is met. Human merge is book policy;
COMMENT-only reviews and draft creation are explicit constraints. Conclusion filtering
is target-valid, not falsely baseline-verified; the diagnostic is not a functioning
CI-Doctor or no-write workflow. Stack defaults/opt-out cost and unchanged role/fork
boundaries are explained without runtime claims. Tests-only intent is distinguished
from file controls. Unsupported Codex enforcement is not fixed by widening shell access.

**Chapter 11:** Distribution and persistence remain distinct. Same-checkout edits,
reviewed pinned/vendored updates, configuration composition, runtime prompt loading,
and inlining are separated. The shared fragment is fully copyable with correct delimiters.
Native skills, experimental plugins, and independently versioned APM are not conflated.
APM 0.28.0, pins, `apm.lock.yaml`, frozen installation, and the non-bundled/non-runnable
bridge are bounded without host-lock replay or transitive-freeze guarantees. Cache
inactivity, artifact retention, repository-local memory, filtering, stale-data removal,
and non-mutating validators are correct. The trivial validator is not represented as
JSON-schema validation or a security guarantee.

## Completion boundary

The six-part structure, slugs, Repo Assistant progression, and Team-to-Organization
transition remain intact. Historical reports retain provenance; framework-pin adoption
and pending prose-edition preparation do not block this scoped review. Warning surfaces
are not approvals; runtime, scanners, installation, telemetry, and secrets remain untested.

Must-fix before batch acceptance: close R1, synchronize source/embed, refresh affected
strict verification, and obtain renewed review. No additional chapter rework requested.

Verdict: REVISE
