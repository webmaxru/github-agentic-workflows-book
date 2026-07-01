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


def load_chapters() -> list[dict[str, Any]]:
    with TOC_PATH.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    chapters = data.get("chapters") or []
    if not isinstance(chapters, list):
        raise ValueError(f"'chapters' in {TOC_PATH} must be a list, found {type(chapters).__name__}")
    return chapters


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


def build_chapter_nav(chapters: list[dict[str, Any]], current_id: str | None = None, prefix: str = "chapters/") -> str:
    items: list[str] = []
    for chapter in chapters:
        is_current = chapter["id"] == current_id
        aria = ' aria-current="page"' if is_current else ""
        cls = ' class="is-current"' if is_current else ""
        href = chapter_url(chapter, prefix)
        items.append(
            f'''          <li><a{cls}{aria} href="{esc(href)}"><span class="chapter-number">{esc(chapter["number"]):0>2}</span><span>{esc(chapter["title"])}</span></a></li>'''
        )
    return "\n".join(items)


def render_index(chapters: list[dict[str, Any]]) -> str:
    cards: list[str] = []
    for chapter in chapters:
        features = chapter.get("features") or []
        feature_html = ""
        if features:
            feature_html = "\n".join(f"              <li>{esc(feature)}</li>" for feature in features)
            feature_html = f'''
            <details class="component-list">
              <summary>gh-aw features</summary>
              <ul>
{feature_html}
              </ul>
            </details>'''
        cards.append(f'''        <article class="chapter-card">
          <p class="eyebrow">Chapter {esc(chapter["number"])}</p>
          <h2><a href="{esc(chapter_url(chapter))}">{esc(chapter["title"])}</a></h2>
          <p>{esc(chapter["objective"])}</p>{feature_html}
        </article>''')

    if cards:
        chapters_block = f'''      <div class="chapter-grid">
{chr(10).join(cards)}
      </div>'''
    else:
        chapters_block = '''      <p class="pending-note"><strong>No chapters yet.</strong> The learning path is being designed. Populate <code>content/toc.yml</code> (via <code>playbook-architect</code>) and re-run <code>site/generate.py</code> to scaffold chapter pages.</p>'''

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
    </div>
  </header>

  <main id="main-content" class="container" tabindex="-1">
    <section class="intro-panel" aria-labelledby="start-heading">
      <h2 id="start-heading">Start with the learning path</h2>
      <p>Use the chapter grid to move from foundational agentic-workflow vocabulary into hands-on gh-aw workflow authoring. Chapter authors can add content inside each prepared section without changing the site chrome.</p>
    </section>

    <section aria-labelledby="chapters-heading">
      <h2 id="chapters-heading">Chapters</h2>
{chapters_block}
    </section>
  </main>

  <footer class="site-footer">
    <div class="container">
      <p>Generated from <code>content/toc.yml</code>. Content and presentation are intentionally separated.</p>
    </div>
  </footer>
</body>
</html>
'''


def render_chapter(chapters: list[dict[str, Any]], index: int) -> str:
    chapter = chapters[index]
    prev_chapter = chapters[index - 1] if index > 0 else None
    next_chapter = chapters[index + 1] if index < len(chapters) - 1 else None

    section_nav: list[str] = []
    sections: list[str] = []
    used_ids: set[str] = set()
    for title in chapter.get("sections", []):
        base = slugify(title)
        section_id = base
        counter = 2
        while section_id in used_ids:
            section_id = f"{base}-{counter}"
            counter += 1
        used_ids.add(section_id)
        section_nav.append(f'              <li><a href="#{esc(section_id)}">{esc(title)}</a></li>')
        sections.append(f'''        <section class="chapter-section" data-section="{esc(section_id)}">
          <h2 id="{esc(section_id)}"><a class="anchor-link" href="#{esc(section_id)}" aria-label="Link to {esc(title)} section">{esc(title)}</a></h2>
          <div class="section-content" data-content-slot="{esc(section_id)}">
            <p class="pending-note"><strong>Content pending.</strong> This section is reserved for the chapter author. Add authored content inside this <code>.section-content</code> block.</p>
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
          <ol>
{build_chapter_nav(chapters, chapter["id"], "")}
          </ol>
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
        <p>Generated from <code>content/toc.yml</code>. Replace only section content blocks when authoring.</p>
      </footer>
    </div>
  </div>
</body>
</html>
'''


def main() -> None:
    chapters = load_chapters()
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    (SITE / "index.html").write_text(render_index(chapters), encoding="utf-8")
    for index, _chapter in enumerate(chapters):
        output = CHAPTERS_DIR / f"{chapters[index]['slug']}.html"
        output.write_text(render_chapter(chapters, index), encoding="utf-8")
    print(f"Generated {1 + len(chapters)} HTML files in {SITE}")


if __name__ == "__main__":
    main()
