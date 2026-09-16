# Foundations batch - scoped re-review

**Target:** gh-aw v0.88.7
**Reviewed:** 16 September 2026
**Scope:** Chapters 01-05 only.

Re-reviewed only the three findings preserved in `foundations-review-1.md`, their
current corrections, the installer regression tests, and
`installer-verification.json`. The earlier full editorial review was not repeated.

## Findings closed

### 1. HIGH - Windows installer version capture: CLOSED

**Current locations:** `scripts/install-gh-aw.ps1:93-104`; advertised route at
`content/chapters/your-first-workflow.html:58-66`.

The installer now captures both native output streams and immediately saves the
native exit code. It rejects nonzero exit independently of version text, still
requires the exact requested version, and verifies the checksum before replacing
the destination executable.

The regression code exercises an actual native Python executable, not merely a
PowerShell function masquerading as the compiler. The recorded **7/7 PASS** includes
stderr-only success, wrong-version rejection, nonzero-exit rejection, and
preservation/cleanup checks.

The real pinned installation also records exit zero, v0.88.7, the expected
executable SHA-256
`8d88047c1e162f16a01e1920124092c80a8bdf98c1635357067a0ac34c00d4c7`,
exactly one absolute executable-path result, and no remaining download staging
directories. The personal extension remains v0.81.6. This closes the previously
unsupported installation route without weakening its checks.

### 2. MEDIUM - Intrinsic reversibility claim: CLOSED

**Current locations:** `your-first-workflow.html:20,142,275`.

All three passages now make suitability conditional on low-risk information and
downstream effects. The opening explicitly distinguishes editing/deleting an output
from undoing disclosure or consequences already initiated. The selection guidance
and recap reinforce that distinction while retaining a useful first-workflow narrative.

This now agrees with Chapter 1's bounded-authority model; no YAML or task change
was needed.

### 3. LOW - Navigation summaries: CLOSED

**Current locations:** `content/toc.yml:110`; `anatomy-and-compile-model.html:216`;
`triggers.html:281`.

The TOC and Chapter 3 handoff now describe event selection and admission without
promising punctual or exclusive execution. Chapter 4's engine handoff includes Pi
and therefore agrees with Chapter 5's five-built-in inventory.

## Retained evidence and decision boundary

The prior strict source, embedded-workflow, configuration-excerpt, generated-lock,
model-context and scratch behavior evidence remains applicable to the unchanged
compilation inputs. It is reused evidence, not a newly claimed compilation. The
changed prose has received renewed editorial review.

**No unresolved foundation must-fixes remain, and no new substantive issue was
introduced by these corrections.** Restricted-secret warnings and runtime/scanner
verification limits remain unwaived.

Acceptance covers only the revised foundation batch. It is not global acceptance,
metadata advancement, secret approval, runtime authorization or publication
permission. The accepted Chapter 12 pilot and other queued batch gates remain
outside this decision. No files, attestations or commits were created during this
read-only review.

Verdict: ACCEPT
