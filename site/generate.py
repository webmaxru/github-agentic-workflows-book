"""Generate the static GitHub Agentic Workflows book site from content/toc.yml."""
from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
CHAPTERS_DIR = SITE / "chapters"
CONTENT_CHAPTERS_DIR = ROOT / "content" / "chapters"
TOC_PATH = ROOT / "content" / "toc.yml"

PLAYBOOK_TITLE = "GitHub Agentic Workflows: An Interactive Book"
PLAYBOOK_INTRO = (
    "A progressive guide that starts with agentic-workflow concepts and builds toward "
    "GitHub Agentic Workflows authoring, compilation, MCP tools, safe outputs, and CI hosting."
)


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"&", " and ", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "section"


def load_toc() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    with TOC_PATH.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    chapters = data.get("chapters") or []
    if not isinstance(chapters, list):
        raise ValueError(f"'chapters' in {TOC_PATH} must be a list, found {type(chapters).__name__}")
    parts = data.get("parts") or []
    if not isinstance(parts, list):
        raise ValueError(f"'parts' in {TOC_PATH} must be a list, found {type(parts).__name__}")
    return chapters, parts


def section_ids(chapter: dict[str, Any]) -> list[tuple[str, str]]:
    """Ordered [(section_id, title), ...] using the same slugify + -2/-3 dedup as the slots."""
    used: set[str] = set()
    result: list[tuple[str, str]] = []
    for title in chapter.get("sections", []):
        base = slugify(title)
        section_id = base
        counter = 2
        while section_id in used:
            section_id = f"{base}-{counter}"
            counter += 1
        used.add(section_id)
        result.append((section_id, title))
    return result


def split_part_title(part_title: str, number: Any) -> tuple[str, str]:
    """Split \"Part I \u2014 The Individual (one workflow)\" into (\"Part I\", \"The Individual ...\")."""
    for separator in ("\u2014", " - ", ":"):
        if separator in part_title:
            left, right = part_title.split(separator, 1)
            return left.strip(), right.strip()
    fallback = f"Part {number}" if number is not None else "Part"
    return fallback, part_title.strip()


def group_parts(
    chapters: list[dict[str, Any]], parts: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Group chapters under their parts (TOC order). Any ungrouped chapters get a trailing group."""
    by_id = {chapter["id"]: chapter for chapter in chapters}
    grouped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for offset, part in enumerate(parts, start=1):
        number = part.get("number", offset)
        eyebrow, title = split_part_title(str(part.get("title", "")), number)
        part_chapters: list[dict[str, Any]] = []
        for chapter_id in part.get("chapters", []):
            chapter = by_id.get(chapter_id)
            if chapter is not None:
                part_chapters.append(chapter)
                seen.add(chapter_id)
        grouped.append({"number": number, "eyebrow": eyebrow, "title": title, "chapters": part_chapters})
    leftovers = [chapter for chapter in chapters if chapter["id"] not in seen]
    if leftovers:
        grouped.append({"number": None, "eyebrow": "More", "title": "Additional chapters", "chapters": leftovers})
    return grouped


# --- Authored-content fragments (content/chapters/<slug>.html) -----------------
# Authored prose lives OUTSIDE the generated pages so regeneration never destroys it.
# Each fragment is a flat series of <section data-slot="<section-id>"> ... </section>
# blocks whose ids match section_ids() exactly.

_SECTION_TOKEN_RE = re.compile(r"<(/?)\s*section\b[^>]*>", re.IGNORECASE)
_SLOT_ATTR_RE = re.compile(r"""data-slot\s*=\s*"([^"]+)"|data-slot\s*=\s*'([^']+)'""", re.IGNORECASE)
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def scaffold_fragment(chapter: dict[str, Any], sections: list[tuple[str, str]]) -> str:
    """First-run scaffold: one empty, id-labelled slot per section so authors see exact ids."""
    lines = [
        f"<!-- Authored content for Chapter {chapter['number']}: {chapter['title']}",
        f"     Slug: {chapter['slug']}  |  This file is the source of truth for prose.",
        '     site/generate.py NEVER overwrites it. Fill each <section data-slot="...">',
        "     with inner HTML; keep the data-slot ids unchanged (they map 1:1 to page slots). -->",
        "",
    ]
    for section_id, title in sections:
        lines.append(f'<section data-slot="{esc(section_id)}" data-title="{esc(title)}">')
        lines.append(f'  <!-- Author: write content for "{title}" here -->')
        lines.append("</section>")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def parse_fragment(text: str) -> dict[str, str]:
    """Extract {section_id: raw inner HTML} from a fragment, honouring nested tags."""
    slots: dict[str, str] = {}
    stack: list[tuple[str | None, int]] = []
    for match in _SECTION_TOKEN_RE.finditer(text):
        is_closing = match.group(1) == "/"
        if is_closing:
            if stack:
                slot_id, content_start = stack.pop()
                if slot_id is not None and slot_id not in slots:
                    slots[slot_id] = text[content_start:match.start()]
        else:
            attr = _SLOT_ATTR_RE.search(match.group(0))
            slot_id = (attr.group(1) or attr.group(2)) if attr else None
            stack.append((slot_id, match.end()))
    return slots


def slot_is_filled(inner: str) -> bool:
    """A slot counts as authored only if it holds more than whitespace and comments."""
    if not inner:
        return False
    return bool(_COMMENT_RE.sub("", inner).strip())


def root_head(title: str, description: str, prefix: str = "") -> str:
    return f"""<meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <meta name=\"description\" content=\"{esc(description)}\">
  <title>{esc(title)} | {esc(PLAYBOOK_TITLE)}</title>
  <link rel=\"preconnect\" href=\"https://cdnjs.cloudflare.com\">
  <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css\" crossorigin=\"anonymous\" referrerpolicy=\"no-referrer\">
  <link rel=\"stylesheet\" href=\"{prefix}assets/style.css\">
  <script defer src=\"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js\" crossorigin=\"anonymous\" referrerpolicy=\"no-referrer\"></script>
  <script defer src=\"{prefix}assets/app.js\"></script>"""


def chapter_url(chapter: dict[str, Any], prefix: str = "chapters/") -> str:
    return f"{prefix}{chapter['slug']}.html"


def build_chapter_nav(grouped: list[dict[str, Any]], current_id: str | None = None, prefix: str = "chapters/") -> str:
    blocks: list[str] = []
    for offset, part in enumerate(grouped, start=1):
        label_id = f"navpart-{part['number'] if part['number'] is not None else offset}"
        items: list[str] = []
        for chapter in part["chapters"]:
            is_current = chapter["id"] == current_id
            aria = ' aria-current="page"' if is_current else ""
            cls = ' class="is-current"' if is_current else ""
            href = chapter_url(chapter, prefix)
            items.append(
                f'''            <li><a{cls}{aria} href="{esc(href)}"><span class="chapter-number">{esc(chapter["number"]):0>2}</span><span>{esc(chapter["title"])}</span></a></li>'''
            )
        blocks.append(
            f'''        <div class="nav-part">
          <p class="nav-part-title" id="{esc(label_id)}">{esc(part["eyebrow"])} \u00b7 {esc(part["title"])}</p>
          <ol class="nav-chapters" aria-labelledby="{esc(label_id)}">
{chr(10).join(items)}
          </ol>
        </div>'''
        )
    return "\n".join(blocks)


def render_chapter_card(chapter: dict[str, Any]) -> str:
    features = chapter.get("features") or []
    feature_html = ""
    if features:
        items = "\n".join(f"                <li>{esc(feature)}</li>" for feature in features)
        feature_html = f'''
            <details class="component-list">
              <summary>gh-aw features</summary>
              <ul>
{items}
              </ul>
            </details>'''
    return f'''          <article class="chapter-card">
            <p class="eyebrow">Chapter {esc(chapter["number"])}</p>
            <h3><a href="{esc(chapter_url(chapter))}">{esc(chapter["title"])}</a></h3>
            <p>{esc(chapter["objective"])}</p>{feature_html}
          </article>'''


def render_index(grouped: list[dict[str, Any]]) -> str:
    part_blocks: list[str] = []
    for offset, part in enumerate(grouped, start=1):
        heading_id = f"part-{part['number'] if part['number'] is not None else offset}"
        cards = "\n".join(render_chapter_card(chapter) for chapter in part["chapters"])
        if not cards:
            continue
        part_blocks.append(f'''      <section class="part-block" aria-labelledby="{esc(heading_id)}">
        <header class="part-header">
          <p class="eyebrow">{esc(part["eyebrow"])}</p>
          <h2 id="{esc(heading_id)}">{esc(part["title"])}</h2>
        </header>
        <div class="chapter-grid">
{cards}
        </div>
      </section>''')

    if part_blocks:
        parts_html = "\n".join(part_blocks)
    else:
        parts_html = '''      <p class="pending-note"><strong>No chapters yet.</strong> Populate <code>content/toc.yml</code> (via <code>playbook-architect</code>) and re-run <code>site/generate.py</code> to scaffold chapter pages.</p>'''

    return f'''<!doctype html>
<html lang="en">
<head>
  {root_head("Home", PLAYBOOK_INTRO)}
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <header class="site-header" role="banner">
    <div class="container hero">
      <p class="eyebrow">Interactive HTML book</p>
      <h1>{esc(PLAYBOOK_TITLE)}</h1>
      <p class="lead">{esc(PLAYBOOK_INTRO)}</p>
      <nav class="hero-links" aria-label="About this book">
        <a href="orchestration.html">How this book was built \u2192</a>
        <a href="https://github.com/github/gh-aw" target="_blank" rel="noopener">gh-aw on GitHub \u2197</a>
      </nav>
    </div>
  </header>

  <main id="main-content" class="container" tabindex="-1">
    <section class="intro-panel reading-guide" aria-labelledby="how-to-read">
      <h2 id="how-to-read">How to read this book</h2>
      <p>Every chapter follows one running example \u2014 the <strong>Repo Assistant</strong> \u2014 from a single workflow to an organization-wide fleet. The 14 chapters are grouped into three parts that scale up in scope. Two tracks run through the book; follow the call-outs that match your role.</p>
      <div class="track-grid">
        <aside class="callout callout--builder" aria-label="Builder track">
          <p class="callout-title">Builder track</p>
          <p>You author, compile, and run workflows. Read the parts in order and work every <em>Worked example</em>; watch for <strong>Builder</strong> call-outs with hands-on detail.</p>
        </aside>
        <aside class="callout callout--leader" aria-label="Leader track">
          <p class="callout-title">Leader track</p>
          <p>You care about safety, cost, governance, and adoption. Skim the <em>Concept</em> and <em>When to use</em> sections and follow the <strong>Leader</strong> call-outs; Parts II\u2013III are written for you.</p>
        </aside>
      </div>
    </section>

    <section aria-labelledby="chapters-heading">
      <h2 id="chapters-heading" class="visually-hidden">Chapters by part</h2>
{parts_html}
    </section>
  </main>

  <footer class="site-footer">
    <div class="container">
      <p>Generated from <code>content/toc.yml</code> by <code>site/generate.py</code>. Prose lives in <code>content/chapters/*.html</code>; the shell owns presentation. <a href="orchestration.html">See how the fleet built this \u2197</a></p>
    </div>
  </footer>
</body>
</html>
'''


def render_chapter(
    chapters: list[dict[str, Any]],
    grouped: list[dict[str, Any]],
    index: int,
    slots: dict[str, str],
) -> str:
    chapter = chapters[index]
    prev_chapter = chapters[index - 1] if index > 0 else None
    next_chapter = chapters[index + 1] if index < len(chapters) - 1 else None

    section_nav: list[str] = []
    sections: list[str] = []
    for section_id, title in section_ids(chapter):
        section_nav.append(f'              <li><a href="#{esc(section_id)}">{esc(title)}</a></li>')
        inner = slots.get(section_id, "")
        if slot_is_filled(inner):
            content_html = inner.strip()
        else:
            content_html = (
                '<p class="pending-note"><strong>Content pending.</strong> Reserved for the chapter author. '
                f'Fill the <code>data-slot="{esc(section_id)}"</code> block in '
                f'<code>content/chapters/{esc(chapter["slug"])}.html</code>.</p>'
            )
        sections.append(f'''        <section class="chapter-section" data-section="{esc(section_id)}">
          <h2 id="{esc(section_id)}"><a class="anchor-link" href="#{esc(section_id)}" aria-label="Link to {esc(title)} section">{esc(title)}</a></h2>
          <div class="section-content" data-content-slot="{esc(section_id)}">
{content_html}
          </div>
        </section>''')

    prev_link = (
        f'<a class="pager-link" rel="prev" href="{esc(prev_chapter["slug"])}.html">← Chapter {esc(prev_chapter["number"])}: {esc(prev_chapter["title"])}</a>'
        if prev_chapter else '<span class="pager-link is-disabled">← No previous chapter</span>'
    )
    next_link = (
        f'<a class="pager-link" rel="next" href="{esc(next_chapter["slug"])}.html">Chapter {esc(next_chapter["number"])}: {esc(next_chapter["title"])} →</a>'
        if next_chapter else '<span class="pager-link is-disabled">No next chapter →</span>'
    )

    features = chapter.get("features") or []
    features_html = ""
    if features:
        features_html = "\n".join(f"            <li>{esc(feature)}</li>" for feature in features)
        features_html = f'''
          <aside class="metadata-card" aria-labelledby="features-heading">
            <h2 id="features-heading">gh-aw features</h2>
            <ul class="tag-list">
{features_html}
            </ul>
          </aside>'''

    depends = chapter.get("depends_on") or []
    depends_html = ""
    if depends:
        id_to_chapter = {item["id"]: item for item in chapters}
        depends_items = []
        for dep_id in depends:
            dep = id_to_chapter.get(dep_id)
            if dep:
                depends_items.append(f'            <li><a href="{esc(dep["slug"])}.html">Chapter {esc(dep["number"])}: {esc(dep["title"])}</a></li>')
            else:
                depends_items.append(f"            <li>{esc(dep_id)}</li>")
        depends_html = f'''
          <aside class="metadata-card" aria-labelledby="depends-heading">
            <h2 id="depends-heading">Prerequisites</h2>
            <ul>
{chr(10).join(depends_items)}
            </ul>
          </aside>'''

    return f'''<!doctype html>
<html lang="en">
<head>
  {root_head(chapter["title"], chapter["objective"], "../")}
</head>
<body class="chapter-page">
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <button class="sidebar-toggle" type="button" aria-controls="chapter-sidebar" aria-expanded="false">☰ Chapters</button>

  <div class="page-shell">
    <aside id="chapter-sidebar" class="sidebar" aria-label="Book chapters">
      <div class="sidebar-inner">
        <a class="site-title" href="../index.html">{esc(PLAYBOOK_TITLE)}</a>
        <nav class="chapter-nav" aria-label="Chapter navigation">
{build_chapter_nav(grouped, chapter["id"], "")}
        </nav>
      </div>
    </aside>

    <div class="content-shell">
      <header class="chapter-header">
        <nav class="breadcrumb" aria-label="Breadcrumb"><a href="../index.html">Home</a> / Chapter {esc(chapter["number"])}</nav>
        <p class="eyebrow">Chapter {esc(chapter["number"])}</p>
        <h1>{esc(chapter["title"])}</h1>
        <p class="lead">{esc(chapter["objective"])}</p>
      </header>

      <main id="main-content" class="chapter-main" tabindex="-1">
        <div class="chapter-meta">
          <nav class="metadata-card" aria-labelledby="section-nav-heading">
            <h2 id="section-nav-heading">On this page</h2>
            <ol>
{chr(10).join(section_nav)}
            </ol>
          </nav>{features_html}{depends_html}
        </div>

{chr(10).join(sections)}

        <nav class="pager" aria-label="Chapter pagination">
          {prev_link}
          {next_link}
        </nav>
      </main>

      <footer class="site-footer chapter-footer">
        <p>Presentation generated by <code>site/generate.py</code>. Prose is injected from <code>content/chapters/{esc(chapter["slug"])}.html</code>.</p>
      </footer>
    </div>
  </div>
</body>
</html>
'''


def print_report(reports: list[dict[str, Any]]) -> None:
    total_files = 1 + len(reports)
    scaffolded = sum(1 for r in reports if r["scaffolded"])
    total_slots = sum(r["total"] for r in reports)
    filled_slots = sum(r["filled"] for r in reports)
    complete = sum(1 for r in reports if r["total"] and r["filled"] == r["total"])
    pending = sum(1 for r in reports if r["filled"] == 0)

    print(f"Generated {total_files} HTML files (1 index + {len(reports)} chapters) in {SITE}")
    if scaffolded:
        print(f"Scaffolded {scaffolded} new fragment(s) in {CONTENT_CHAPTERS_DIR} (existing fragments left untouched)")
    else:
        print(f"No new fragments scaffolded; all authored content in {CONTENT_CHAPTERS_DIR} preserved")
    print("")
    print("Content status (authored / total slots):")
    for r in reports:
        chapter = r["chapter"]
        if r["filled"] == 0:
            state = "pending"
        elif r["filled"] == r["total"]:
            state = "complete"
        else:
            state = "partial"
        note = "  [scaffold created]" if r["scaffolded"] else ""
        label = f"Ch{int(chapter['number']):02d} {chapter['slug']}"
        dots = "." * max(3, 44 - len(label))
        print(f"  {label} {dots} {r['filled']}/{r['total']} {state}{note}")
    print("")
    print(f"Totals: {filled_slots}/{total_slots} slots authored \u00b7 {complete} complete \u00b7 {pending} pending.")
    print("Serve locally: python -m http.server -d site 8000")


def main() -> None:
    chapters, parts = load_toc()
    grouped = group_parts(chapters, parts)
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    CONTENT_CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)

    (SITE / "index.html").write_text(render_index(grouped), encoding="utf-8")

    reports: list[dict[str, Any]] = []
    for index, chapter in enumerate(chapters):
        sections = section_ids(chapter)
        fragment_path = CONTENT_CHAPTERS_DIR / f"{chapter['slug']}.html"
        scaffolded = False
        if not fragment_path.exists():
            fragment_path.write_text(scaffold_fragment(chapter, sections), encoding="utf-8")
            scaffolded = True
        slots = parse_fragment(fragment_path.read_text(encoding="utf-8"))
        filled = sum(1 for section_id, _ in sections if slot_is_filled(slots.get(section_id, "")))
        output = CHAPTERS_DIR / f"{chapter['slug']}.html"
        output.write_text(render_chapter(chapters, grouped, index, slots), encoding="utf-8")
        reports.append({"chapter": chapter, "total": len(sections), "filled": filled, "scaffolded": scaffolded})

    print_report(reports)


if __name__ == "__main__":
    main()
