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
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">
  <meta name=\"description\" content=\"{esc(description)}\">
  <meta name=\"color-scheme\" content=\"light dark\">
  <title>{esc(title)} | {esc(PLAYBOOK_TITLE)}</title>
  <script>(function(){{try{{var t=localStorage.getItem('aw-theme');if(t&&t!=='system'){{document.documentElement.setAttribute('data-theme',t);}}}}catch(e){{}}}})();</script>
  <link rel=\"icon\" href=\"data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2032%2032'%3E%3Crect%20width='32'%20height='32'%20rx='7'%20fill='%234f46e5'/%3E%3Ctext%20x='16'%20y='22'%20font-family='monospace'%20font-size='16'%20font-weight='bold'%20text-anchor='middle'%20fill='white'%3Eaw%3C/text%3E%3C/svg%3E\">
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
  <link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,500;0,7..72,600;0,7..72,700;1,7..72,400&display=swap\">
  <link rel=\"preconnect\" href=\"https://cdnjs.cloudflare.com\">
  <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css\" crossorigin=\"anonymous\" referrerpolicy=\"no-referrer\">
  <link rel=\"stylesheet\" href=\"{prefix}assets/style.css\">
  <script defer src=\"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js\" crossorigin=\"anonymous\" referrerpolicy=\"no-referrer\"></script>
  <script defer src=\"{prefix}assets/app.js\"></script>"""


_NUM_WORDS = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"]
_TAG_RE = re.compile(r"<[^>]+>")


def part_number_word(number: Any) -> str:
    try:
        n = int(number)
    except (TypeError, ValueError):
        return ""
    return _NUM_WORDS[n] if 0 < n < len(_NUM_WORDS) else str(n)


def reading_minutes(slug: str) -> int | None:
    """Rough reading estimate (~200 wpm) from the authored fragment, or None if unauthored."""
    path = CONTENT_CHAPTERS_DIR / f"{slug}.html"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    text = _COMMENT_RE.sub(" ", text)
    text = _TAG_RE.sub(" ", text)
    words = len(text.split())
    if words == 0:
        return None
    return max(1, round(words / 200))


def theme_toggle() -> str:
    return '''<div class="theme-toggle" role="group" aria-label="Reading theme">
        <button type="button" class="theme-opt" data-theme-value="light" aria-pressed="false" title="Light"><span aria-hidden="true">\u2600</span><span class="visually-hidden">Light theme</span></button>
        <button type="button" class="theme-opt" data-theme-value="sepia" aria-pressed="false" title="Sepia"><span aria-hidden="true">\u25d1</span><span class="visually-hidden">Sepia theme</span></button>
        <button type="button" class="theme-opt" data-theme-value="dark" aria-pressed="false" title="Dark"><span aria-hidden="true">\u263e</span><span class="visually-hidden">Dark theme</span></button>
      </div>'''


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





def render_index(grouped: list[dict[str, Any]]) -> str:
    chapter_count = sum(len(part["chapters"]) for part in grouped)
    part_count = sum(1 for part in grouped if part["chapters"])
    total_min = sum((ch.get("_reading_min") or 0) for part in grouped for ch in part["chapters"])
    first_slug = next((ch["slug"] for part in grouped for ch in part["chapters"]), None)
    start_href = f"chapters/{first_slug}.html" if first_slug else "#contents"

    part_blocks: list[str] = []
    for offset, part in enumerate(grouped, start=1):
        chs = part["chapters"]
        if not chs:
            continue
        heading_id = f"part-{part['number'] if part['number'] is not None else offset}"
        word = part_number_word(part["number"])
        part_label = f"Part {word}" if word else str(part.get("eyebrow", "")).strip()
        base, _, paren = str(part["title"]).partition("(")
        base = base.strip()
        note = paren.rstrip(") ").strip()
        note_html = f'\n            <span class="toc-part-note">{esc(note)}</span>' if note else ""

        rows: list[str] = []
        for ch in chs:
            minutes = ch.get("_reading_min")
            time_html = (
                f'<span class="toc-time">{minutes} min</span>'
                if minutes else '<span class="toc-time toc-time--empty" aria-hidden="true">\u00b7</span>'
            )
            rows.append(f'''            <li class="toc-row">
              <a class="toc-link" href="{esc(chapter_url(ch))}">
                <span class="toc-num">{esc(ch["number"]):0>2}</span>
                <span class="toc-text">
                  <span class="toc-title">{esc(ch["title"])}</span>
                  <span class="toc-obj">{esc(ch["objective"])}</span>
                </span>
                {time_html}
              </a>
            </li>''')

        part_blocks.append(f'''        <section class="toc-part" aria-labelledby="{esc(heading_id)}">
          <header class="toc-part-head">
            <span class="toc-part-kicker">{esc(part_label)}</span>
            <h3 id="{esc(heading_id)}" class="toc-part-title">{esc(base)}</h3>{note_html}
          </header>
          <ol class="toc-list">
{chr(10).join(rows)}
          </ol>
        </section>''')

    if part_blocks:
        contents_html = "\n".join(part_blocks)
    else:
        contents_html = '''        <p class="pending-note"><strong>No chapters yet.</strong> Populate <code>content/toc.yml</code> (via <code>playbook-architect</code>) and re-run <code>site/generate.py</code> to scaffold chapter pages.</p>'''

    reading_line = f"about {total_min} minutes" if total_min else f"{chapter_count} chapters"
    scope_line = f"{chapter_count} chapters across {part_count} parts" if part_count else f"{chapter_count} chapters"

    return f'''<!doctype html>
<html lang="en">
<head>
  {root_head("Home", PLAYBOOK_INTRO)}
</head>
<body class="home">
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <header class="reader-bar" role="banner">
    <div class="reader-bar-inner">
      <a class="brand" href="index.html"><span class="brand-mark">aw</span> gh-aw \u00b7 the book</a>
      <nav class="reader-nav" aria-label="Primary">
        <a href="#contents">Contents</a>
        <a href="orchestration.html">How it was built</a>
        <a href="https://github.com/github/gh-aw" target="_blank" rel="noopener">gh-aw \u2197</a>
      </nav>
      {theme_toggle()}
    </div>
  </header>

  <main id="main-content" tabindex="-1">
    <section class="cover" aria-labelledby="cover-title">
      <div class="cover-inner">
        <p class="cover-series">An interactive book on Continuous AI</p>
        <h1 id="cover-title" class="cover-title">GitHub Agentic Workflows</h1>
        <p class="cover-sub">Write your repository's outer loop in plain Markdown. Compile it to a hardened, SHA-pinned GitHub Actions workflow, and let a coding agent do the triage, docs, and review work \u2014 safely, and reviewed by default.</p>
        <div class="cover-actions">
          <a class="btn btn-primary" href="{esc(start_href)}">Start reading</a>
          <a class="btn btn-quiet" href="#contents">Browse the contents</a>
        </div>
        <dl class="cover-meta">
          <div class="cover-meta-item">
            <dt>Length</dt>
            <dd>{esc(scope_line)}</dd>
          </div>
          <div class="cover-meta-item">
            <dt>Reading time</dt>
            <dd>{esc(reading_line)}</dd>
          </div>
          <div class="cover-meta-item">
            <dt>Edition</dt>
            <dd><span class="mono">gh aw v0.81.6</span> \u00b7 Public Preview</dd>
          </div>
        </dl>
      </div>
    </section>

    <section class="guide" aria-labelledby="guide-title">
      <div class="reading-column">
        <h2 id="guide-title">How to read this book</h2>
        <p class="guide-lead">One running example, the <strong>Repo Assistant</strong>, grows from a single triage workflow into a governed multi-repo fleet. The chapters build in three parts that widen in scope. Two kinds of reader travel the same pages, guided by margin notes.</p>
        <div class="tracks">
          <p class="track"><span class="track-dot track-dot--builder" aria-hidden="true"></span><span><strong>Builders</strong> author, compile, and run. Read in order, work every <em>Worked example</em>, and follow the Builder notes.</span></p>
          <p class="track"><span class="track-dot track-dot--leader" aria-hidden="true"></span><span><strong>Leaders</strong> weigh safety, cost, and adoption. Skim the concept and <em>when to use</em> sections and follow the Leader notes; Parts Two and Three are written for you.</span></p>
        </div>
      </div>
    </section>

    <section id="contents" class="contents" aria-labelledby="contents-title">
      <div class="contents-inner">
        <div class="contents-head">
          <h2 id="contents-title">Contents</h2>
          <p class="contents-note">{esc(scope_line)}</p>
        </div>
{contents_html}
      </div>
    </section>
  </main>

  <footer class="colophon">
    <div class="colophon-inner">
      <p>This book is a proof of its own thesis: written by a fleet of GitHub Copilot agents, with every workflow example compiled and every claim checked against the real <span class="mono">gh aw</span> CLI.</p>
      <p class="colophon-meta">Generated from <span class="mono">content/toc.yml</span> by <span class="mono">site/generate.py</span>. <a href="orchestration.html">See how the fleet built this \u2197</a></p>
    </div>
  </footer>
</body>
</html>
'''


def part_label_for(grouped: list[dict[str, Any]], chapter_id: str) -> str:
    for part in grouped:
        for chapter in part["chapters"]:
            if chapter["id"] == chapter_id:
                return str(part.get("title", ""))
    return ""


def render_chapter(
    chapters: list[dict[str, Any]],
    grouped: list[dict[str, Any]],
    index: int,
    slots: dict[str, str],
) -> str:
    chapter = chapters[index]
    prev_chapter = chapters[index - 1] if index > 0 else None
    next_chapter = chapters[index + 1] if index < len(chapters) - 1 else None
    part_title = part_label_for(grouped, chapter["id"])

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
        <div class="sidebar-top">
          <a class="site-title" href="../index.html">{esc(PLAYBOOK_TITLE)}</a>
          {theme_toggle()}
        </div>
        <nav class="chapter-nav" aria-label="Chapter navigation">
{build_chapter_nav(grouped, chapter["id"], "")}
        </nav>
      </div>
    </aside>

    <div class="content-shell">
      <header class="chapter-header">
        <nav class="breadcrumb" aria-label="Breadcrumb"><a href="../index.html">Home</a> / Chapter {esc(chapter["number"])}</nav>
        <p class="fm"><span class="fm-k">chapter:</span> <span class="fm-v">{esc(chapter["number"]):0>2}</span><span class="fm-sep">\u00b7</span><span class="fm-k">part:</span> <span class="fm-v">{esc(part_title)}</span></p>
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

    for chapter in chapters:
        chapter["_reading_min"] = reading_minutes(chapter["slug"])

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
