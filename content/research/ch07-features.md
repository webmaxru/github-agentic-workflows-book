# Chapter 7 — "Defense in Depth" — Research & Verification Note

- **Chapter:** `ch07-defense-in-depth` (Part II). **Targets:** `gh aw` **v0.81.6**.
- **Prepared inline by orchestrator.** Date: 2026-07-02.
- **Verification artifact:** `examples/ch07/repo-assistant-hardened.md` →
  `gh aw compile` → `✓ (101.8 KB)`, `0 error(s), 0 warning(s)`, EXIT 0. Lock gitignored.

## Concept (theory)
- **Lethal trifecta** (widely-cited AI-security framing): danger = untrusted content + private data
  access + external communication. Break it from several directions = **defense in depth**.
- gh-aw quote: "implements a defense-in-depth security architecture that protects against untrusted
  MCP servers and compromised agents." (introduction/architecture/)

## Verified capability facts (source: introduction/architecture/, reference/network/, reference/frontmatter/)
- **Three trust layers:** Substrate (VM/kernel/container, AWF firewall, MCP sandbox — holds even if
  user component fully compromised), Configuration (schema validation, SHA pinning, scanners
  actionlint/zizmor/poutine, role/permission checks, compile-time), Plan (content sanitization,
  threat detection, secret redaction, SafeOutputs permission separation, staged execution).
- **permissions:** agent runs read-only; writes deferred to separate scoped jobs. Omit → read-only.
- **network firewall (AWF):** `{}` = no network; `defaults` = basic infra (default); `{allowed:[...]}`
  = allowlist. Ecosystem identifiers (python/node/github/…). blocked > allowed. Squid+iptables,
  prevents exfiltration, logs all activity. `(redacted)` in output = domain not allowed.
- **strict mode DEFAULT:** rejects top-level write perms, wildcard domains, unpinned actions,
  deprecated fields; explicit network config. `strict: false` CANNOT run on public repos.
- **Auto Plan-layer defenses:** content sanitization (@mention neutralize, non-HTTPS/untrusted URL
  redact, limits 0.5MB/65k, control chars); threat detection job (AI scans buffered output for secret
  leaks/malicious patches/policy; blocking "safe" verdict before safe outputs); secret redaction
  (`if: always()` scrub of /tmp/gh-aw). Public repos: `min-integrity: approved` auto-applied.
- Audit: `gh aw audit <run-id>` → Firewall Analysis (per-domain allow/deny).

## Example shape (verified)
Hardened triage: `roles:` gate + read-only perms + `strict: true` + tight `network.allowed:[defaults,
github]` + `timeout-minutes: 10` + safe-outputs. 5 configured controls + 3 auto layers. Next: ch08
adds capabilities (tools/MCP) without reopening doors.
