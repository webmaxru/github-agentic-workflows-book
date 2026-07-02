---
target: site/index.html
total_score: 34
p0_count: 0
p1_count: 0
timestamp: 2026-07-02T20-36-40Z
slug: site-index-html
---
# Critique — site/index.html (home)

gh aw v0.81.6 · register: brand · Design Health: 34/40 (Good)
Evidence: light+dark desktop renders, CDP mobile emulation (390px), deterministic detector.

## Design Health Score (Nielsen, /40)
1 Visibility of status — 3
2 Match to real world — 4
3 User control & freedom — 3
4 Consistency & standards — 4
5 Error prevention — 3
6 Recognition over recall — 4
7 Flexibility & efficiency — 3
8 Aesthetic & minimalist — 4
9 Error recovery — 3 (N/A surface)
10 Help & documentation — 3
Total 34/40 — Good.

## Anti-Patterns Verdict
- AI-slop: PASS (does not read as AI-made). Concept-driven diptych, 3 real type voices, blueprint paper bg (not cream/sand).
- Side-stripe borders: PRESENT (Builder/Leader callouts, border-left iris/teal) — impeccable absolute ban, but committed identity in DESIGN.md. LLM-only (detector missed; CSS not resolved).
- Gradient text: none (brand badge is gradient bg + white text, allowed).
- Glassmorphism: none. Hero-metric template: none. Identical card grids: no (TOC rows + 2 track cards).
- Eyebrow motif: hero + 3 part labels (uppercase mono tracked) — borderline recurring.
- Numbered markers 01–14: detector advisory; assessed LEGITIMATE (real chapter sequence).
- Text overflow: NONE (measured mobile scrollWidth==clientWidth==390; earlier clip was a screenshot artifact).
- Detector false positive: single-font ("only jetbrains mono") — 3 fonts render; CSS unresolved.

## Priority Issues
- [P2] Em-dash cadence: 10 em-dashes on one page (detector-confirmed); against the project's anti-AI-slop voice. Fix: vary punctuation.
- [P2] Side-stripe callouts: border-left accent = impeccable ban; committed identity. Fix: full border + tint / top accent, or add to ignore.md.
- [P2] Mobile top-nav: below 560px only external "gh-aw ↗" remains; internal "How it was built" disappears (footer retains it). Fix: keep internal links / menu.
- [P3] Recurring uppercase mono eyebrow (hero + 3 parts) — defensible but consider a distinct cadence.
- [P3] Numbered chapter markers — legitimate; candidate for ignore.md.

## What's Working
- Compile diptych (source .md → gh aw compile → .lock.yml): genuine concept-driven signature.
- Three-voice typography executed with real hierarchy; editorial, not SaaS.
- Blueprint-grid paper bg + dual light/dark themes; distinctive and on-brand.
- Strong positioning line; clear Builder/Leader dual-track guidance.

## Persona Red Flags
- Jordan (first-timer): assumes CI/CD literacy ("outer loop", MCP, safe-outputs) — acceptable for dev audience.
- Casey (mobile): layout clean; but mobile nav collapses to external link only; primary CTA reachable.
- Riley (stress): robust static page; long titles fit; pre scrolls.
- Builder (project): primary CTA → Ch01 concept, not the 10-min win (Ch02) an eager builder may want.
- Leader (project): value prop (safe by default, reviewed writes) surfaced well.

## Minor Observations
- Chapter titles are spans-in-links, not headings: SR "navigate by heading" surfaces parts only (fine for a TOC).
- Consider "back to top" on the long page.
- a11y strengths: skip-link, focus-visible, reduced-motion, figure aria-label, decorative seam aria-hidden.
