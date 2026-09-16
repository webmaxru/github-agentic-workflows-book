# Governance and Fleets - Scoped Re-review

**Target:** gh-aw v0.88.7
**Date:** 2026-09-16
**Scope:** Close or reopen GF-1/GF-2 only. The prior Chapters 13-14 assessment carries forward.

## GF-1 - MEDIUM - CLOSED

**Location:** `content/chapters/fleets-and-adoption.html:58,64`.
**Owner:** Chapter author; fix complete.

The package-precedence statement now directly cites tagged
`add_command.go#L36-L41`. The ref-advancement table caption cites tagged
`update_command.go#L35-L46`.

These exact contracts were inspected during the original review. They support
added-package precedence and the distinct tag, branch, and commit-SHA update behavior.
The correction preserves the accurate warning: a source pin does not freeze an explicit
update, and consumer changes still require review.

## GF-2 - MEDIUM - CLOSED

**Location:** `content/chapters/fleets-and-adoption.html:206`.
**Owner:** Chapter author; fix complete.

The visible callout now reports completed strict compilation of current source and
embedded workflow, including the shared fragment through its importer, exit zero,
nonempty locks, exact v0.88.7 metadata, and strict true. It identifies the existing
canonical and embedded reports.

The stale pending handoff is gone. Network-resolution qualifications, credential and
repository prerequisites, and unverified installation/dispatch/fleet boundaries remain.
Technical results are not presented as prior editorial or deployment approval.

## Verification and consistency

The three revised prose/caption lines satisfy both fixes without altering the teaching
model or rollout guidance. No new issue is introduced.

Existing strict-compilation evidence remains applicable on the author-confirmed unchanged
source, shared, embedded, and dependency inputs. No compilation or new research was
performed during this re-review. No files, metadata, or attestations were changed.

**Remaining must-fixes: none.** Acceptance is limited to Chapters 13-14 at the reviewed
state. It does not cover the separate Chapter 09 change, constitute whole-book acceptance,
or authorize publication.

Verdict: ACCEPT
