# Product

## Register

brand

## Users

Two readers, one book — every chapter earns its keep for both.

- **Builder** — a developer or staff engineer already comfortable with GitHub, Actions,
  and YAML. Context: sitting in their own repository, deciding whether GitHub Agentic
  Workflows is worth adopting and how far it goes. Job to be done: author, compile,
  secure, debug, and ship a real workflow — and understand the model well enough to
  trust it running in CI.
- **Leader** — a team lead, engineering manager, or decision-maker. Context: weighing
  whether and how to roll agentic automation across a team or an org. Job to be done:
  understand why the *outer loop* matters, what the governance / security / cost surface
  looks like, and how adoption scales from one repo to a fleet.

Both are served on the same page through **Builder** and **Leader** margin callouts, so
neither wades through material written for the other. The reader's overarching job:
look at their own repository, spot three tasks a tireless teammate could own overnight,
and ship a governed agentic workflow that does them — safely, cheaply, reviewably.

## Product Purpose

An interactive, multi-page HTML book that teaches **GitHub Agentic Workflows (gh-aw)** —
GitHub Next's first step toward *Continuous AI*, the "third leg" of repository automation
beside CI and CD. It runs a deliberate maturity arc across 14 chapters and three parts —
**The Individual** (one workflow) → **The Team** (safe, reviewed, patterned) → **The
Organization** (a governed fleet) — always anchoring a concept before its syntax, and
threading a single running example (the "Repo Assistant") that grows from one triage
workflow into a multi-repo fleet.

Success is behavioral, not page-views: a reader finishes able to ship a governed agentic
workflow on their own repository. The book is also a **proof of its own thesis** — it is
produced by a fleet of GitHub Copilot primitives (agents, skills, instruction files, a
driver prompt) orchestrated in waves, with every behavior claim grounded in the real
`gh aw` CLI and every workflow example proven to compile. The site's own craft is
therefore part of the argument: it must look and read like something built by the
disciplined method it teaches.

## Brand Personality

Three words: **engineered, candid, and human.**

- **Voice:** outcome-first and plain-spoken. Lead with the result the reader wants, then
  introduce only the syntax needed to reach it. No hype, no vendor gloss, no "10x" claims.
- **Proof over persuasion:** credibility comes from verified evidence — compile-checked
  code, a recorded `gh aw` version, real adopter case studies — not adjectives.
- **Honest about limits:** every capability carries a "when *not* to use this." Trust is
  earned by naming the failure modes, not hiding them.
- **The core metaphor is felt everywhere:** *authored intent compiles to governed
  infrastructure.* Human Markdown on one side, a hardened, SHA-pinned lock file on the
  other. The prose is the human voice; the mono / terminal voice is the compiled one.

Emotional goal: the reader should feel **capable and in control** — never overwhelmed,
never sold to. Confidence grounded in proof.

## Anti-references

What this book's surface must never become:

- **Generic AI-generated docs / SaaS slop.** If a reader could glance at it and say
  "AI made that," it has failed. The bar is a distinctive, deliberately-made artifact.
- **Marketing landing-page tropes:** gradient-text hero headlines, the hero-metric
  template (giant number + tiny label + gradient accent), decorative glassmorphic cards,
  endless identical icon+heading+text feature grids. This is a book, not a pitch deck.
- **Reflexive editorial-magazine costume:** display-serif italics, drop caps, and a tiny
  tracked uppercase eyebrow stamped above *every* section as scaffolding. Small uppercase
  labels here are structural only — the "Part One/Two/Three" dividers in the table of
  contents and metadata-card headers — never a decorative reflex above every heading.
- **Sterile default-template docs** (an untouched Docusaurus / GitBook look): no point of
  view, sans-only, gray-on-white, forgettable.
- **Hype or overreach in the copy itself:** anthropomorphizing the agent as magic, hiding
  the security / cost trade-offs, or burying the "when not to." The design and the writing
  must both stay grounded.

## Design Principles

1. **Practice what you preach.** The book argues for high-craft, verified, governed
   agentic work — so the book itself must be high-craft and demonstrably correct. Every
   rough edge undermines the thesis; the site's polish *is* an argument for the method.
2. **Motivate before you mechanize; theory before API.** Every capability opens with the
   real problem a team feels, and every piece of syntax is anchored to a concept
   introduced first. Never a spec dump.
3. **Serve both readers on every page.** Builders and Leaders read the same chapters;
   structure and callouts must let each find their track without friction, and neither
   should hit a page that isn't for them.
4. **Show verified proof, not claims.** Outcome-first framing, compile-checked examples,
   real adopter evidence, and an honest "when not to use this." Persuade with evidence,
   not adjectives.
5. **Make the compile metaphor legible — in the content, not the chrome.** Authored Markdown
   intent → `gh aw compile` → governed `.lock.yml`. This source→compiled duality is the spine
   of the *writing* and lives in the dark code figures (real `.md` sources and `.lock.yml`
   output) and chapter frontmatter strips. The surface itself is a calm reading application:
   it should keep that duality vivid where it's read, and otherwise get out of the way.

## Accessibility & Inclusion

- **Target: WCAG 2.1 AA**, in all three reading themes — Light, Sepia, and Dark. The reader
  chooses (persisted in `localStorage`), with the OS `prefers-color-scheme` as the default;
  every palette must hold contrast.
- **Built for long-form reading:** serif body at a comfortable size and line-height,
  prose line length capped around 65–75ch, a clear heading hierarchy, and generous rhythm.
- **Keyboard and screen-reader first:** a visible skip link, strong `:focus-visible`
  rings, semantic landmarks, and accessible names on interactive controls (copy buttons,
  the sidebar toggle, the "requires a secret" badge).
- **Contrast discipline for the technical voices:** muted metadata, code, and terminal
  text must clear AA against their (often tinted or dark) backgrounds — the mono
  "compiled" voice must never degrade into decorative low-contrast gray.
- **Motion is optional:** the cover entrance and orchestration animations must fully
  respect `prefers-reduced-motion: reduce` (already honored) and never gate content
  visibility on a transition.
