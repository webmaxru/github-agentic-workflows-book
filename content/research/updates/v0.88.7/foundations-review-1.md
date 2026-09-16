# Foundations batch editorial/technical review

**Target:** gh-aw v0.88.7
**Reviewed:** 16 September 2026
**Scope:** Chapters 01-05 only; read-only review.

## Scope and evidence

Reviewed the five foundation HTML chapters, their TOC objectives, the shared
Chapter 2 triage source, all three Chapter 4 sources, and Chapter 5's Claude source.
Applied the chapter impact rows, `framework-delta.md`, and `theory-delta.md`;
historical briefs remain dated evidence. No release archaeology or compilation
was repeated.

Evidence examined includes `foundations-diagnostics.md`, canonical and embedded
verification reports, `foundations-snapshot-audit.json`, and supporting excerpt,
context, behavior, CLI and reference checks. The advertised Windows installer was
inspected because it is a Chapter 2 prerequisite.

The workflow technical gates stand: **5/5 sources**, **4/4 complete embeds**,
**12/12 configuration excerpts**, **6/6 generated-lock excerpts**, and **9/9
supplemental contexts** passed their stated checks. Compilation reports show exit
zero, nonempty locks, exact v0.88.7 metadata and boolean strict mode, without
environment/cleanup errors. The resolved Claude-prefix comparison failure was a
supplemental harness issue, not a source or compiler failure.

The post-PASS Chapter 4 comment changed no compiled input. Historical evidence
remains preserved. These results do not, however, establish that the advertised
installer works or eliminate the prose issues below.

## Severity-ranked findings

### 1. HIGH - Ch02's isolated Windows installation route mishandles target version output

**Location:** `content/chapters/your-first-workflow.html:58-66`; referenced
implementation at `scripts/install-gh-aw.ps1:93-102`.

The chapter promises that the script returns a verified executable path. Its version
check assigns only the native command's **stdout** to `$versionOutput`, then requires
that captured text to contain the target version.

The retained target evidence contains a successful **stderr-only** response:
`pilot-cli-help.json:10-12` records exit zero, empty stdout, and
`gh aw version v0.88.7` on stderr. PowerShell assignment does not capture that error
stream. Consequently, the helper rejects this valid response before reaching its
executable-path output. This is a concrete compatibility defect in the advertised
route, not an observed installer execution during this review.

**Evidence:** The script's stream handling; the captured target response;
`foundations-cli-verification.json` explicitly records `installer_executed: false`.
Its signature checks establish the parameter and output statement, not successful
installation.

**Fix / owner:** **Book tooling owner, coordinated with the Chapter 2 author.**
Capture both output streams for version validation while independently retaining
exit status, exact-version checks and checksum verification. Add a bounded regression
check covering stderr-only success, wrong version and nonzero exit. Alternatively,
withdraw the helper route until corrected. Do not weaken the version gate or silently
fall back to the personal extension.

### 2. MEDIUM - Ch02 still treats triage outputs as inherently reversible

**Location:** `your-first-workflow.html:20,142,275`.

The motivation calls comments and labels "trivially reversible"; the selection
guidance calls them "easily undone" and treats triage as automatically satisfying
the low-stakes requirement. This conflates editing/deleting a GitHub object with
reversing its consequences. A published disclosure, for example, is not undone by
deleting the comment.

The chapter's later qualification is good, but the opening and selection guidance
undermine it. Readers should choose a suitably low-risk triage context, not infer
low risk solely from the output type.

**Evidence:** Chapter 1 explicitly explains that an authorized comment can reveal
private context (`what-are-agentic-workflows.html:53`); Chapter 2 itself denies
harmless-content guarantees at line 138. This is the authority-versus-harm
distinction in theory delta section B.

**Fix / owner:** **Chapter 2 author.** Qualify these passages: comments and labels
are manageable starting operations when the selected information and downstream
effects are low-risk. Retain the energetic first-win framing and existing detailed
caveat; no workflow/YAML change is required.

### 3. LOW - Foundation navigation summaries retain superseded shorthand

**Locations:** `content/toc.yml:110`; `anatomy-and-compile-model.html:216`;
`triggers.html:281`.

The TOC objective and Chapter 3 handoff still promise running at "exactly the right
moments-and no others," whereas Chapter 4's revised objective properly distinguishes
triggers from admission and disclaims punctual execution. Chapter 4's handoff also
lists only Copilot, Claude, Codex and Gemini immediately before Chapter 5 teaches
five built-ins.

**Evidence:** `triggers.html:7,64,95-97`; `engines.html:7,31-45`; updated Chapter 5
TOC objective.

**Fix / owner:** **Chapter 3/4 authors and TOC owner.** Align the summaries with
event selection/admission, and include Pi or say "five built-in engines." This is
bounded consistency cleanup, not independently a reason to reject the batch.

## Chapter-by-chapter assessment

- **Ch01 - F05/F07:** The mapped corrections are successfully taught. Human review
  and merge are explicitly book policy, not product incapability. Read-only
  repository authority is distinguished from local workspace edits, automatic
  authorized comments/labels, and harmful content. The complete Chapter 2 source
  now replaces the abridged variant. Existing adopter statistics are retained
  rather than presented as newly measured.
- **Ch02 - F01/F04:** Apart from findings 1-2, the authoring path is substantially
  improved. It distinguishes pinned extension and isolated invocation, explains PAT
  account permission and entitlement, makes organization billing opt-in with
  policy/recompile/deployment prerequisites, and separates issue-trigger testing
  from manual dispatch. Compilation, optional validation and runtime claims are
  appropriately bounded.
- **Ch03 - F01/F07:** The chapter meets its objective through actual generated
  evidence. Main-agent and detector inference are introduced before the graph.
  Reproducibility includes dependencies, environment, repository context and
  existing lock state. Runtime prompt loading, explicit inlining and deliberate
  consumer updates are separated. Actual pin excerpts and the independently
  versioned APM counterexample avoid an unsupported universal immutability promise.
- **Ch04 - F02:** Reactive/proactive theory leads naturally into admission controls.
  Cooldown's completion-based interval, skipped-agent behavior and fail-open
  limitation are explicit. Separating cooled-down maintenance from urgent triage
  is useful design guidance. Stack defaults, nested roles, shorthand expansion and
  stop-time preservation/refresh agree with the supplied evidence. Scratch
  cron/deadline checks are not represented as scheduler execution.
- **Ch05 - F03/F04/F08:** Five built-ins, restored model precedence, `auto`, real
  compiler defaults and retained Claude pins are accurately distinguished.
  Authentication, Pi's separate detector credential, and engine-specific Bash
  enforcement make portability concrete. The corrected footer no longer claims
  identical prompts or a controlled engine experiment.

## Consistency and completion

The five chapters preserve their six slots, dependency order, Repo Assistant
narrative and Builder/Leader usefulness. No new unsupported live outcome or
statistic was identified. Warning preservation and compile-versus-runtime
distinctions should remain unchanged.

**Must-fixes: findings 1 and 2.** Close these with bounded installer evidence and
prose corrections, then return the changed material for scoped review. Resolve
finding 3 during batch cleanup.

This is not global acceptance, a metadata advance, secret approval or runtime
authorization. The accepted Chapter 12 pilot and other queued chapter gates remain
outside this decision. Keeping the global framework baseline at v0.81.6 pending
final integration is not a foundation blocker.

Verdict: REVISE
