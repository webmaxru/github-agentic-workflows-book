#!/usr/bin/env python3
"""Single source of truth for the book's **content** version and changelog.

The book is a living document: its prose (the chapters under ``content/``) is versioned
independently of the site generator, PDF renderer, and other tooling. The current version is a
single line in ``content/VERSION``; the human-readable history lives in ``content/CHANGELOG.md``.

This module is imported by:
  * ``site/generate.py``    — to surface the version across the web edition and build the
                              version-history page,
  * ``scripts/build_pdf.py`` — to stamp the version into the PDF footer,
and is used as a CLI by ``.github/workflows/release-content.yml`` to cut GitHub Releases:

    python scripts/content_version.py version          # -> 1.1
    python scripts/content_version.py tag              # -> content-v1.1
    python scripts/content_version.py notes            # release notes for the current version
    python scripts/content_version.py notes 1.0        # release notes for a specific version

Keeping the parser here (rather than in the site generator) means the release workflow never has
to import the site build, and every consumer reads the same format.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_PATH = ROOT / "content" / "VERSION"
CHANGELOG_PATH = ROOT / "content" / "CHANGELOG.md"

# Git tag / GitHub Release naming for a content version, e.g. "content-v1.1".
TAG_PREFIX = "content-v"

# "## [1.1] - 2026-07-08"  ->  version + date
_HEADER_RE = re.compile(r"^##\s+\[(?P<version>[^\]]+)\]\s*-\s*(?P<date>.+?)\s*$")
# "### Added"
_GROUP_RE = re.compile(r"^###\s+(?P<title>.+?)\s*$")
# "- item" / "* item"
_ITEM_RE = re.compile(r"^\s*[-*]\s+(?P<item>.+?)\s*$")


@dataclass
class ChangeGroup:
    """A labelled group of bullet items within one version (e.g. "Added")."""

    title: str
    items: list[str] = field(default_factory=list)


@dataclass
class Release:
    """One content version parsed from the changelog."""

    version: str
    date: str
    summary: str
    groups: list[ChangeGroup]
    body: str  # raw markdown between this header and the next — used as release notes

    @property
    def tag(self) -> str:
        return f"{TAG_PREFIX}{self.version}"


def read_version() -> str:
    """Return the current content version string (e.g. "1.1")."""
    try:
        text = VERSION_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "0.0"
    # Tolerate an accidental leading "v".
    return text.lstrip("vV").strip() or "0.0"


def tag_for(version: str) -> str:
    return f"{TAG_PREFIX}{version}"


def _read_changelog() -> str:
    try:
        return CHANGELOG_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def parse_changelog() -> list[Release]:
    """Parse ``content/CHANGELOG.md`` into an ordered list of releases (newest first)."""
    lines = _read_changelog().splitlines()

    # Find each "## [version] - date" header and the line range of its body.
    headers: list[tuple[int, str, str]] = []
    for idx, line in enumerate(lines):
        match = _HEADER_RE.match(line)
        if match:
            headers.append((idx, match.group("version").strip(), match.group("date").strip()))

    releases: list[Release] = []
    for pos, (start, version, dt) in enumerate(headers):
        end = headers[pos + 1][0] if pos + 1 < len(headers) else len(lines)
        body_lines = lines[start + 1 : end]
        body = "\n".join(body_lines).strip("\n")

        summary_parts: list[str] = []
        groups: list[ChangeGroup] = []
        current: ChangeGroup | None = None
        summary_done = False
        for raw in body_lines:
            line = raw.rstrip()
            if not line.strip():
                if summary_parts:
                    summary_done = True
                continue
            group_match = _GROUP_RE.match(line)
            if group_match:
                summary_done = True
                current = ChangeGroup(title=group_match.group("title").strip())
                groups.append(current)
                continue
            item_match = _ITEM_RE.match(line)
            if item_match:
                summary_done = True
                item = item_match.group("item").strip()
                if current is None:
                    current = ChangeGroup(title="")
                    groups.append(current)
                current.items.append(item)
                continue
            # A non-blank line that is neither a group heading nor a new bullet: treat it as a
            # wrapped continuation of the previous bullet (changelog items often soft-wrap), or
            # as part of the intro summary if we haven't reached the bullets yet.
            if current is not None and current.items:
                current.items[-1] = f"{current.items[-1]} {line.strip()}"
            elif not summary_done:
                summary_parts.append(line.strip())

        releases.append(
            Release(
                version=version,
                date=dt,
                summary=" ".join(summary_parts).strip(),
                groups=groups,
                body=body,
            )
        )
    return releases


def release_for(version: str) -> Release | None:
    for release in parse_changelog():
        if release.version == version:
            return release
    return None


def notes_for(version: str) -> str:
    """Return the changelog body (markdown) for ``version``, suitable as release notes."""
    release = release_for(version)
    return release.body if release else ""


def _cli(argv: list[str]) -> int:
    command = argv[0] if argv else "version"
    if command == "version":
        print(read_version())
        return 0
    if command == "tag":
        version = argv[1] if len(argv) > 1 else read_version()
        print(tag_for(version))
        return 0
    if command == "notes":
        version = argv[1] if len(argv) > 1 else read_version()
        notes = notes_for(version)
        if not notes:
            print(f"No changelog entry found for version {version!r}.", file=sys.stderr)
            return 1
        print(notes)
        return 0
    print(f"Unknown command: {command!r}. Use one of: version, tag, notes.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))
