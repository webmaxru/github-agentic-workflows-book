"""Generate the static GitHub Agentic Workflows book site from content/toc.yml."""
from __future__ import annotations

import html
import json
import re
from datetime import date
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

# --- Site identity & discovery metadata --------------------------------------
# Production origin (custom domain served by GitHub Pages at the root path).
SITE_ORIGIN = "https://aw.isainative.dev"
SITE_SHORT_NAME = "gh-aw Book"
HOME_DESCRIPTION = (
    "Learn GitHub Agentic Workflows (gh-aw): write your repository's outer loop in "
    "Markdown, compile it to hardened GitHub Actions, and run safe, reviewed Continuous AI."
)
AUTHOR_NAME = "Maxim Salnikov"
AUTHOR_URL = "https://www.linkedin.com/in/webmax/"
AUTHOR_GITHUB = "https://github.com/webmaxru"
REPO_URL = "https://github.com/webmaxru/github-agentic-workflows-book"
OG_IMAGE_URL = f"{SITE_ORIGIN}/og-image.png"
OG_IMAGE_ALT = "GitHub Agentic Workflows \u2014 An Interactive Book by Maxim Salnikov"
THEME_COLOR_LIGHT = "#e9edf4"
THEME_COLOR_DARK = "#0d1220"
GH_AW_DOCS = "https://github.github.com/gh-aw/"
GH_AW_REPO = "https://github.com/github/gh-aw"

# AI / LLM agent crawlers welcomed explicitly in robots.txt (default policy: allow).
AI_AGENTS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User",
    "anthropic-ai", "PerplexityBot", "Perplexity-User", "Google-Extended",
    "Applebot-Extended", "CCBot", "cohere-ai", "Amazonbot", "meta-externalagent",
]


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


def abs_url(path: str = "") -> str:
    """Absolute URL against the production origin; `path` is root-relative (no leading slash)."""
    path = path.lstrip("/")
    return f"{SITE_ORIGIN}/{path}" if path else f"{SITE_ORIGIN}/"


def json_ld_script(data: Any) -> str:
    """Serialize JSON-LD, neutralizing characters that could break out of the <script>."""
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    raw = raw.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return f'<script type="application/ld+json">{raw}</script>'


def author_node() -> dict[str, Any]:
    return {
        "@type": "Person",
        "@id": f"{SITE_ORIGIN}/#author",
        "name": AUTHOR_NAME,
        "url": AUTHOR_URL,
        "sameAs": [AUTHOR_URL, AUTHOR_GITHUB],
        "worksFor": {"@type": "Organization", "name": "Microsoft"},
    }


def home_json_ld(chapter_count: int) -> str:
    website = {
        "@type": "WebSite",
        "@id": f"{SITE_ORIGIN}/#website",
        "url": abs_url(),
        "name": PLAYBOOK_TITLE,
        "description": HOME_DESCRIPTION,
        "inLanguage": "en",
        "publisher": {"@id": f"{SITE_ORIGIN}/#author"},
    }
    book = {
        "@type": "Book",
        "@id": f"{SITE_ORIGIN}/#book",
        "name": PLAYBOOK_TITLE,
        "url": abs_url(),
        "author": {"@id": f"{SITE_ORIGIN}/#author"},
        "inLanguage": "en",
        "bookFormat": "https://schema.org/EBook",
        "genre": "Software engineering",
        "about": "GitHub Agentic Workflows (gh-aw)",
        "numberOfPages": chapter_count,
        "image": OG_IMAGE_URL,
        "isPartOf": {"@id": f"{SITE_ORIGIN}/#website"},
    }
    return json_ld_script({"@context": "https://schema.org", "@graph": [website, author_node(), book]})


def chapter_json_ld(chapter: dict[str, Any], part_title: str) -> str:
    url = abs_url(f"chapters/{chapter['slug']}.html")
    article = {
        "@type": "TechArticle",
        "@id": f"{url}#article",
        "headline": chapter["title"],
        "name": chapter["title"],
        "description": chapter["objective"],
        "url": url,
        "inLanguage": "en",
        "author": {"@id": f"{SITE_ORIGIN}/#author"},
        "publisher": {"@id": f"{SITE_ORIGIN}/#author"},
        "isPartOf": {"@id": f"{SITE_ORIGIN}/#book"},
        "image": OG_IMAGE_URL,
    }
    if part_title:
        article["articleSection"] = part_title
    features = chapter.get("features") or []
    if features:
        article["keywords"] = ", ".join(features)
    crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": abs_url()}]
    position = 2
    if part_title:
        crumbs.append({"@type": "ListItem", "position": position, "name": part_title, "item": abs_url() + "#contents"})
        position += 1
    crumbs.append({"@type": "ListItem", "position": position, "name": chapter["title"], "item": url})
    breadcrumb = {"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": crumbs}
    return json_ld_script({"@context": "https://schema.org", "@graph": [article, author_node(), breadcrumb]})


def root_head(
    *,
    page_title: str,
    description: str,
    canonical_url: str,
    og_type: str,
    og_title: str,
    json_ld: str = "",
    prefix: str = "",
) -> str:
    robots = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    return f"""<meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{esc(page_title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="author" content="{esc(AUTHOR_NAME)}">
  <link rel="canonical" href="{esc(canonical_url)}">
  <meta name="robots" content="{robots}">
  <meta name="googlebot" content="{robots}">
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" media="(prefers-color-scheme: light)" content="{THEME_COLOR_LIGHT}">
  <meta name="theme-color" media="(prefers-color-scheme: dark)" content="{THEME_COLOR_DARK}">
  <script>(function(){{try{{var t=localStorage.getItem('aw-theme');if(t&&t!=='system'){{document.documentElement.setAttribute('data-theme',t);}}}}catch(e){{}}}})();</script>
  <link rel="icon" href="/favicon.ico" sizes="32x32">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="{esc(PLAYBOOK_TITLE)}">
  <meta property="og:locale" content="en_US">
  <meta property="og:title" content="{esc(og_title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical_url)}">
  <meta property="og:image" content="{esc(OG_IMAGE_URL)}">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{esc(OG_IMAGE_ALT)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(og_title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{esc(OG_IMAGE_URL)}">
  <meta name="twitter:image:alt" content="{esc(OG_IMAGE_ALT)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,500;0,7..72,600;0,7..72,700;1,7..72,400&display=swap">
  <link rel="preconnect" href="https://cdnjs.cloudflare.com">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css" crossorigin="anonymous" referrerpolicy="no-referrer">
  <link rel="stylesheet" href="{prefix}assets/style.css">
  <script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
  <script defer src="{prefix}assets/app.js"></script>
  {json_ld}"""


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
  {root_head(
      page_title=PLAYBOOK_TITLE,
      description=HOME_DESCRIPTION,
      canonical_url=abs_url(),
      og_type="website",
      og_title=PLAYBOOK_TITLE,
      json_ld=home_json_ld(chapter_count),
      prefix="",
  )}
</head>
<body class="home">
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <header class="reader-bar" role="banner">
    <div class="reader-bar-inner">
      <a class="brand" href="index.html"><span class="brand-mark">aw</span> gh-aw \u00b7 the book</a>
      <nav class="reader-nav" aria-label="Primary">
        <a href="#contents">Contents</a>
        <a href="https://github.com/webmaxru/github-agentic-workflows-book" target="_blank" rel="noopener">Book repo \u2197</a>
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
      <p class="colophon-author">By <strong>Maxim Salnikov</strong> \u00b7 Microsoft</p>
      <p class="colophon-meta"><a href="https://www.linkedin.com/in/webmax/" target="_blank" rel="noopener">LinkedIn</a> \u00b7 <a href="https://github.com/webmaxru/github-agentic-workflows-book" target="_blank" rel="noopener">Book repository on GitHub \u2197</a></p>
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
  {root_head(
      page_title=f"{chapter['title']} | {PLAYBOOK_TITLE}",
      description=chapter["objective"],
      canonical_url=abs_url(f"chapters/{chapter['slug']}.html"),
      og_type="article",
      og_title=chapter["title"],
      json_ld=chapter_json_ld(chapter, part_title),
      prefix="../",
  )}
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
        <p>By <strong>Maxim Salnikov</strong> \u00b7 Microsoft \u00b7 <a href="https://www.linkedin.com/in/webmax/" target="_blank" rel="noopener">LinkedIn</a> \u00b7 <a href="https://github.com/webmaxru/github-agentic-workflows-book" target="_blank" rel="noopener">Book repository on GitHub \u2197</a></p>
      </footer>
    </div>
  </div>
</body>
</html>
'''


def _strip_text(fragment_html: str) -> str:
    """Reduce an authored HTML fragment to plain readable text for llms-full.txt."""
    text = _COMMENT_RE.sub(" ", fragment_html)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def render_404() -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Page not found | {esc(PLAYBOOK_TITLE)}</title>
  <meta name="robots" content="noindex, follow">
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" media="(prefers-color-scheme: light)" content="{THEME_COLOR_LIGHT}">
  <meta name="theme-color" media="(prefers-color-scheme: dark)" content="{THEME_COLOR_DARK}">
  <link rel="icon" href="/favicon.ico" sizes="32x32">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="stylesheet" href="/assets/style.css">
</head>
<body class="home">
  <main id="main-content" style="max-width:44rem;margin:0 auto;padding:16vh 1.5rem 10rem;text-align:center">
    <p style="font-family:var(--font-mono);color:var(--muted);letter-spacing:.08em">404</p>
    <h1 style="font-size:clamp(2rem,6vw,3rem);line-height:1.1;margin:.4em 0">This page wandered off the outer loop</h1>
    <p style="color:var(--muted);font-size:1.1rem">The page you asked for doesn't exist or has moved. Head back to the book and pick up where you left off.</p>
    <p style="margin-top:2rem"><a class="btn btn-primary" href="/">Back to the book</a></p>
  </main>
</body>
</html>
"""


def write_discovery_files(chapters: list[dict[str, Any]]) -> None:
    """Write crawl/agent discovery files into the shipped site dir, kept in sync each build."""
    today = date.today().isoformat()

    # Custom domain for GitHub Pages.
    (SITE / "CNAME").write_text("aw.isainative.dev\n", encoding="utf-8")

    # Serve every file verbatim (skip Jekyll processing on GitHub Pages).
    (SITE / ".nojekyll").write_text("", encoding="utf-8")

    # robots.txt — allow everyone, welcome AI agents explicitly, reference the sitemap.
    robots = [f"# robots.txt for {abs_url()}", "User-agent: *", "Allow: /", "",
              "# AI / LLM agents are welcome to read, index, and cite this book."]
    for agent in AI_AGENTS:
        robots += [f"User-agent: {agent}", "Allow: /", ""]
    robots += [f"Sitemap: {abs_url('sitemap.xml')}", ""]
    (SITE / "robots.txt").write_text("\n".join(robots), encoding="utf-8")

    # sitemap.xml — home + every chapter.
    entries = [(abs_url(), "1.0", "weekly")]
    entries += [(abs_url(f"chapters/{ch['slug']}.html"), "0.8", "monthly") for ch in chapters]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, priority, changefreq in entries:
        sm += ["  <url>",
               f"    <loc>{esc(loc)}</loc>",
               f"    <lastmod>{today}</lastmod>",
               f"    <changefreq>{changefreq}</changefreq>",
               f"    <priority>{priority}</priority>",
               "  </url>"]
    sm.append("</urlset>")
    (SITE / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")

    # site.webmanifest
    manifest = {
        "name": PLAYBOOK_TITLE,
        "short_name": SITE_SHORT_NAME,
        "description": HOME_DESCRIPTION,
        "id": "/",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": THEME_COLOR_DARK,
        "theme_color": THEME_COLOR_DARK,
        "lang": "en",
        "dir": "ltr",
        "categories": ["education", "developer", "books", "technology"],
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    (SITE / "site.webmanifest").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # llms.txt (llmstxt.org): title, summary blockquote, intro, then Markdown link sections.
    llms = [f"# {PLAYBOOK_TITLE}", "",
            f"> {HOME_DESCRIPTION}", "",
            ("An interactive, compile-verified HTML book on GitHub Agentic Workflows (gh-aw) \u2014 "
             "Continuous AI for a repository's outer loop. It progresses from concepts to authoring, "
             "compiling, triggers, engines, safe outputs, security, tools/MCP, the \"Continuous X\" "
             "patterns, reuse, observability, governance/FinOps, and fleet adoption. "
             f"Written by {AUTHOR_NAME}."),
            "",
            "## Start here",
            f"- [Home & table of contents]({abs_url()}): Overview, reading guide, and the full chapter list.",
            "",
            "## Chapters"]
    for ch in chapters:
        ch_url = abs_url(f"chapters/{ch['slug']}.html")
        llms.append(f"- [Chapter {ch['number']}: {ch['title']}]({ch_url}): {ch['objective']}")
    llms += ["",
             "## Reference",
             f"- [GitHub Agentic Workflows documentation]({GH_AW_DOCS}): Official gh-aw docs.",
             f"- [gh-aw repository]({GH_AW_REPO}): Source, schema, and sample workflows.",
             f"- [Book repository]({REPO_URL}): Source and generator for this book.",
             ""]
    (SITE / "llms.txt").write_text("\n".join(llms), encoding="utf-8")

    # llms-full.txt: full readable text of every chapter, concatenated for agents.
    full = [f"# {PLAYBOOK_TITLE}", "",
            f"> {HOME_DESCRIPTION}", "",
            f"Source: {abs_url()} | Author: {AUTHOR_NAME} | Generated: {today}", ""]
    for ch in chapters:
        ch_url = abs_url(f"chapters/{ch['slug']}.html")
        full += [f"## Chapter {ch['number']}: {ch['title']}", "",
                 f"URL: {ch_url}", f"Objective: {ch['objective']}", ""]
        fragment = CONTENT_CHAPTERS_DIR / f"{ch['slug']}.html"
        if fragment.exists():
            body = _strip_text(fragment.read_text(encoding="utf-8"))
            if body:
                full += [body, ""]
    (SITE / "llms-full.txt").write_text("\n".join(full), encoding="utf-8")

    # 404.html — helpful, noindex, links home.
    (SITE / "404.html").write_text(render_404(), encoding="utf-8")


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

    write_discovery_files(chapters)
    print_report(reports)


if __name__ == "__main__":
    main()
