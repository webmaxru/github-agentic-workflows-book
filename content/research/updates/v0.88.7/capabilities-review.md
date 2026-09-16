# Capabilities batch - scoped re-review

**Target:** gh-aw v0.88.7
**Reviewed:** 16 September 2026
**Scope:** Chapters 06-08 only.

Re-reviewed only findings 1-3, their corrections and consolidated technical evidence.
The full three-chapter review was not repeated.

## Findings closed

### 1. MEDIUM - Source mediation claim: CLOSED

**Location:** `examples/ch08/repo-assistant-tools.md:38-42`.

The footer now identifies the intended triage comment as a repository-write request
mediated through safe outputs. GitHub reads and web fetches have their own tool/network
boundaries. It no longer claims every action passes through output handlers.

YAML, task instructions, read-only permissions and maximum-one-comment setting are
unchanged. HTML distinguishes unchanged configuration from the freshly compiled body.

### 2. MEDIUM - Eliminated-exfiltration claim: CLOSED

**Location:** `content/chapters/tools-and-mcp.html:129`.

Broader egress now increases remaining exposure. Destination/data review and narrow
domain selection remain, without claiming Chapter 7 eliminated communication risk.
No configuration widening accompanies the correction.

### 3. MEDIUM - Audit repository context: CLOSED

**Location:** `content/chapters/defense-in-depth.html:105`.

The recipe supplies `--repo owner/repo` and explains both placeholders. It matches
retained target help and preserves investigation before allowlisting. No operational audit.

## Verification and preservation

Current canonical/embedded reports, notes and receipt record 24/24 canonical and
16/16 complete embeds PASS, zero exits, nonempty locks, exact version and literal
strict-true positive metadata, without environment/cleanup errors.

The Chapter 8 revision has a new compiled body hash (`4e535027...`) and retains its
frontmatter hash. Its configuration excerpt, not a complete embed, remains consistent.
Policy contexts still omit CLI strict overrides. Retained checks were reused after
input matching. Two post-PASS annotations changed no compilation input; older global
proof was archived rather than relabeled.

Current technical receipt fingerprint:
`2def13bdcd4ae16868df77fa6a14f361018accca6b2974948fb466be607f10e9`.

No unresolved capabilities must-fixes remain and no new substantive issue was introduced.
Chapter 6's no-must-fix assessment carries forward.

Acceptance covers Chapters 06-08 only, not global acceptance, attestation, secret approval,
runtime authorization or publication. No files, metadata or compilation were changed
or executed during this re-review.

Verdict: ACCEPT
