---
name: GitHub Agentic Workflows — An Interactive Book
description: A calm reading application — a modern electronic book with light, sepia, and dark reading themes, optimized for long-form technical reading.
colors:
  paper: "#e9edf4"
  surface: "#ffffff"
  surface-2: "#f1f4fa"
  ink: "#181d29"
  muted: "#4f5768"
  faint: "#626b80"
  line: "#dce1ec"
  line-strong: "#c5cddd"
  iris: "#4f46e5"
  iris-strong: "#3a30bf"
  signal: "#147a4c"
  signal-bright: "#1f9d55"
  dawn: "#b0651a"
  leader: "#0c766e"
  warn: "#b0430c"
  code-bg: "#10162a"
  code-ink: "#e7ecfb"
  code-caption: "#b9c3dc"
  code-hairline: "rgba(148, 163, 184, 0.22)"
  code-badge-ink: "#ffe1c2"
typography:
  display:
    fontFamily: "Literata, Georgia, Times New Roman, serif"
    fontSize: "clamp(2.1rem, 4.6vw, 3rem)"
    fontWeight: 700
    lineHeight: 1.14
    letterSpacing: "-0.015em"
  cover:
    fontFamily: "Literata, Georgia, Times New Roman, serif"
    fontSize: "clamp(2.7rem, 7vw, 4.6rem)"
    fontWeight: 700
    lineHeight: 1.04
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Literata, Georgia, Times New Roman, serif"
    fontSize: "clamp(1.5rem, 3vw, 2rem)"
    fontWeight: 600
    lineHeight: 1.14
    letterSpacing: "-0.015em"
  title:
    fontFamily: "Literata, Georgia, Times New Roman, serif"
    fontSize: "1.28rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Literata, Georgia, Times New Roman, serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.72
    letterSpacing: "normal"
  ui:
    fontFamily: "Hanken Grotesk, Segoe UI, system-ui, sans-serif"
    fontSize: "0.9rem"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "normal"
  label:
    fontFamily: "Hanken Grotesk, Segoe UI, system-ui, sans-serif"
    fontSize: "0.72rem"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.08em"
  mono:
    fontFamily: "JetBrains Mono, ui-monospace, SFMono-Regular, Consolas, monospace"
    fontSize: "0.9rem"
    fontWeight: 500
    lineHeight: 1.6
    letterSpacing: "normal"
rounded:
  xs: "6px"
  sm: "8px"
  md: "12px"
  lg: "20px"
  pill: "999px"
  circle: "50%"
spacing:
  xs: "0.4rem"
  sm: "0.6rem"
  md: "1rem"
  lg: "1.6rem"
  xl: "2.75rem"
  sidebar: "20rem"
  reading-column: "720px"
components:
  button-primary:
    backgroundColor: "{colors.iris}"
    textColor: "#ffffff"
    typography: "{typography.ui}"
    rounded: "{rounded.pill}"
    padding: "0.72rem 1.35rem"
  button-quiet:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.ui}"
    rounded: "{rounded.pill}"
    padding: "0.72rem 1.35rem"
  theme-toggle:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.faint}"
    rounded: "{rounded.pill}"
    padding: "0.2rem"
  toc-row:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "0.95rem 0.6rem"
  callout:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "1.05rem 1.2rem"
  code-figure:
    backgroundColor: "{colors.code-bg}"
    textColor: "{colors.code-ink}"
    rounded: "{rounded.md}"
    padding: "1rem 1.1rem"
  tag:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.muted}"
    typography: "{typography.mono}"
    rounded: "{rounded.pill}"
    padding: "0.16rem 0.55rem"
---

# Design System: GitHub Agentic Workflows — An Interactive Book

## 1. Overview

**Creative North Star: "The Reader."**

The surface is a **calm reading application** — a modern electronic book, not a docs site
or a landing page. Everything serves uninterrupted long-form reading: a serif reading face,
a single measured column, generous vertical rhythm, and three reader-chosen themes (Light,
Sepia, Dark) that persist across visits. The home page is a **title page + genuine table of
contents**, the way you open a real book — no marketing hero, no feature grid, no pitch.

The book's thesis — *authored Markdown intent compiles to a governed GitHub Actions
workflow* — is still the spine of the **content**, and it stays vivid where it belongs: in
the prose, in the dark code figures that show real `.md` sources and `.lock.yml` output, and
in the chapter frontmatter strips. But the **chrome** no longer dramatizes the compiler; it
gets out of the way so the writing can be read. The identity now comes from typography,
restful color, and reading ergonomics rather than from a signature hero device.

This system deliberately departs from the earlier "compile-diptych" visual identity (a
committed product decision, at the user's direction) to become a distraction-free reader.
It still refuses generic AI docs/SaaS slop, marketing tropes, and sterile default-template
docs — restraint here is a point of view about reading, not an absence of one.

**Key Characteristics:**
- A contrast-axis type system: Literata (reading) · Hanken Grotesk (interface) · JetBrains Mono (code).
- Three first-class reading themes — Light, Sepia, Dark — remembered per reader; a segmented toggle in the top bar and chapter sidebar.
- One measured reading column (~720px / ~65–75ch); the page background is quiet, the reading surface calm.
- Iris remains the single brand/interaction color; green, teal, amber, rust stay reserved semantic accents.
- Borders-first structure; shadow reserved for genuine lift and the dark code surfaces. Motion is a gentle cover entrance only.

## 2. Colors

A quiet, cool light palette with two alternate reading themes. Iris is the single
brand/interaction color; green, teal, amber, and rust are reserved semantic accents that
each mean exactly one thing.

### Primary
- **Iris** (`#4f46e5`): brand and interaction — links, primary buttons, the `aw` brand mark,
  active nav, TOC chapter numbers and part kickers, focus rings, inline-code text. **Iris
  Strong** (`#3a30bf`) is the hover/active deepening and inline-code text on its soft tint.
  Per theme, links resolve through `--link` / `--link-strong` so link contrast stays AA.

### Secondary (reserved semantic accents)
- **Signal Green** (`#147a4c` / bright `#1f9d55`): "verified / compiled OK" — success, tip
  callouts, the `›` code-figure caption glyph.
- **Leader Teal** (`#0c766e`): reserved exclusively for the **Leader** audience track (the
  reading-guide dot and Leader callouts), so the two-reader structure reads at a glance.
- **Dawn Amber** (`#b0651a`): the "measured impact / case study" accent — real-adopter
  evidence boxes. Warm, used sparingly.
- **Warn Rust** (`#b0430c`): caution — "when *not* to use this" lists, `needs-secret` code
  badges, warning callouts.

### Neutral
- **Ink** (`#181d29`): primary reading text and headings.
- **Muted** (`#4f5768`) and **Faint** (`#626b80`): secondary prose, metadata, reading-time
  labels. Both are tuned to clear AA on the light **paper** at label sizes — do not lighten
  them for "elegance."
- **Paper** (`#e9edf4`) / **Surface** (`#ffffff`) / **Surface-2** (`#f1f4fa`): the quiet page
  background, raised card/content surfaces, and the sidebar / subtle-fill tone.
- **Line** (`#dce1ec`) / **Line-Strong** (`#c5cddd`): hairline and emphasized borders — the
  primary structural device.
- **Code surface** (constant across themes): **Code BG** (`#10162a`) / **Code Ink**
  (`#e7ecfb`), plus **Code Caption** (`#b9c3dc`), **Code Hairline** (`rgba(148,163,184,.22)`),
  and **Code Badge Ink** (`#ffe1c2`). Code is always the dark "machine" surface, in every
  reading theme, so highlighting and the compiled voice stay consistent.

### The three reading themes
- **Light** (default): the palette above. `color-scheme: light`.
- **Sepia** (`:root[data-theme="sepia"]`): a warm paper mode — paper `#e2d7c0`, surface
  `#f5edda`, ink `#2a2114`, warm muted/faint browns, a deepened iris (`#4a3cae`) and link
  (`#3d2f90`) tuned so all reading text clears AA on the cream. `color-scheme: light`.
- **Dark** (`:root[data-theme="dark"]`, and the automatic `prefers-color-scheme: dark`
  fallback when the reader hasn't chosen): paper `#0d1220`, surface `#151d2e`, ink `#e8edf8`,
  iris lifted to `#8f88f8`, link `#a9a3fb`; green/teal/amber/rust all brightened for dark.
  `color-scheme: dark`.

All three ship AA — never tune one theme without checking the other two. The reader's choice
is stored in `localStorage` (`aw-theme`) and applied before first paint by a tiny inline head
script to avoid a flash; an explicit choice always overrides the OS preference.

## 3. Typography

Three families on a **contrast axis** (serif + sans + mono), each mapped to a role. This is
the committed identity — preserve the lanes; do not swap families on existing surfaces.

- **Reading — Literata** (body + all headings): a Google-designed e-book face used for prose
  and headings alike (headings simply heavier/larger — one family, multiple weights). Body
  `18px`/`1.72`, measure ~65–75ch. This is what makes it read as a *book*. H1
  `clamp(2.1rem, 4.6vw, 3rem)`; cover title `clamp(2.7rem, 7vw, 4.6rem)` (≤ the 6rem ceiling);
  H2 `clamp(1.5rem, 3vw, 2rem)`; H3 `1.28rem`. Heading tracking `-0.015em` (cover `-0.02em`).
- **Interface — Hanken Grotesk** (the UI voice): nav, buttons, labels, kickers, metadata,
  table headers, reading-time chips, breadcrumbs, the colophon. A humanist grotesque that
  contrasts cleanly against Literata.
- **Machine — JetBrains Mono** (the code voice): code blocks, inline code, frontmatter
  strips, code-figure filenames, the `aw` mark, tabular chapter numbers, `needs-secret`
  badges. Reserved for genuinely technical tokens.

Small uppercase labels (Hanken, `0.08em` tracking) appear as **structural part dividers in
the table of contents** ("Part One / Two / Three") and as metadata-card headers — a real
hierarchy, not a decorative eyebrow stamped above every section.

## 4. Elevation

**Borders-first, shadow-sparingly.** Structure is carried by hairline borders
(`{colors.line}`) on quiet surfaces, not drop shadows. Two shadow steps exist and are
reserved:

- `--shadow-sm` (`0 12px 30px -22px`): resting elevation of code figures / case-study boxes,
  the pressed theme-toggle chip, and hover-lift on buttons.
- `--shadow` (`0 26px 56px -34px`): button-primary hover and the mobile sidebar drawer — the
  few elements meant to sit clearly above the page.

Interaction elevation is a small **`translateY(-2px)` lift** plus a border shift toward iris,
not a heavy shadow bloom. All three themes deepen shadow appropriately.

## 5. Motion

Motion is calm and singular. The home **cover** rises and fades in on load (a short,
staggered `rise` on the title-page elements — one deliberate sequence, not a reflex applied
to every section). Hover feedback is limited to color, background, a `-2px` lift, and a 2px
`transform` nudge on TOC numbers — never animated layout properties. Theme changes crossfade
via a 0.3s background/color transition. Everything is fully disabled under
`prefers-reduced-motion: reduce`, which forces the cover to its final visible state.

## 6. Components

- **Reader bar** (`reader-bar`): a sticky, translucent (backdrop-blur) top bar — `aw` brand
  mark + wordmark, minimal nav (Contents / How it was built / gh-aw ↗), and the theme toggle.
  Wraps to two rows on narrow screens.
- **Theme toggle** (`theme-toggle` / `theme-opt`): a pill-shaped segmented control of three
  buttons (☀ Light / ◑ Sepia / ☾ Dark) with `aria-pressed` on the active one and
  visually-hidden labels. Present in the reader bar (home) and the chapter sidebar top.
- **Cover / title page** (`cover`): centered series line, large Literata title, plain-spoken
  subtitle, primary + quiet buttons (Start reading / Browse the contents), and a
  `cover-meta` row (Length / Reading time / Edition). This replaces the old marketing hero.
- **Reading guide** (`guide` + `tracks`): "How to read this book," with the Builder/Leader
  tracks shown as a **colored dot + text row** (no cards, no eyebrows).
- **Table of contents** (`contents` / `toc-part` / `toc-list`): the heart of the home page.
  Each part has a kicker ("Part One"), a Literata title, and a paren note; chapters are index
  **rows** (`toc-link`) with a mono number, Literata title, muted objective, and a
  right-aligned reading-time chip, separated by hairlines. A real book index, not a card grid.
- **Colophon** (`colophon`): a quiet footer stating the book is built by a Copilot fleet and
  generated from `content/toc.yml`.
- **Chapter shell**: a fixed `{spacing.sidebar}` (20rem) sticky nav column (with the site
  title + theme toggle up top) + a fluid `--surface` reading column, collapsing to a slide-in
  drawer with a floating toggle below 860px. Chapter headers carry a `key · value` mono
  frontmatter strip and a Literata title + lead.
- **Metadata cards** ("On this page" / features / prerequisites): bordered `surface-2` cards
  with Hanken uppercase headers and `01`-style leading-zero ordered counters.
- **Callouts** (`callout--builder | leader | warning | tip | note`): a bordered box with a
  ~7% tinted fill, a **full border** in the accent color, and a Hanken uppercase title with a
  small round dot. (The old 3px left-rule was removed — callouts now use full borders, and no
  side-stripe accent appears anywhere in the system.)
- **Case-study box** (`case-study`): dawn-amber bordered/tinted panel prefixed with a
  `◆ Measured` label — reserved for real-adopter evidence.
- **"When not to" list** (`when-not`): warn-rust bordered rows with a `✕` marker.
- **Code figures** (`figure.code`): a labelled dark terminal/file card (mono `figcaption`
  with a `›` prefix + copy button); `.needs-secret` adds a rust border and a
  `🔒 Requires a secret / live run` badge for examples that can't compile offline.
- **Cross-reference link** (`a.xref`): dashed iris underline with a `→` prefix.

## 7. Do's and Don'ts

**Do**
- Keep the three type voices in their lanes: Literata = reading, Hanken Grotesk = interface,
  JetBrains Mono = code. Let the serif/sans/mono contrast do the work.
- Treat reading ergonomics as the product: one measured column, generous rhythm, calm
  background, and a real theme choice the reader controls.
- Lead structure with hairline borders on quiet surfaces; add shadow only for genuine lift
  and the dark code surfaces.
- Reserve each accent for its one meaning (green = verified, teal = Leader, amber = measured
  proof, rust = caution). Iris carries everything else.
- Verify AA contrast in **all three** themes, and honor `prefers-reduced-motion` everywhere.

**Don't**
- Don't reintroduce a marketing hero, hero-metric template, gradient-text heading,
  glassmorphic card, or identical icon+heading feature grid.
- Don't add a side-stripe accent (`border-left`/`border-right` > 1px as color) to any card,
  callout, list item, or alert — the system uses full borders and tints instead.
- Don't stamp a tiny uppercase eyebrow above every section; small caps labels are only for
  the TOC part dividers and metadata-card headers.
- Don't drop reading text to Faint gray for "elegance," or place labels on tints/darks where
  they fall below AA in any theme.
- Don't box reading prose into cards, or default to Grid where flex-wrap suffices; the page
  should read as an edited book, not a dashboard.
