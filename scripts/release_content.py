#!/usr/bin/env python3
"""Deterministic content-edition checks and editorial review attestations.

``changes --base REF`` compares REF with the effective working tree, not just HEAD.
``check`` uses an explicit base, the PR base SHA, the push's before SHA, or the
highest-version reachable content tag (in that order). No remote tag lookup is
needed for a push/PR check. Legacy tag names can identify a comparison edition,
but never substitute for metadata when building an old release.

Review records attest to an editorial process, not a reviewer's identity. A human
or coordinating agent records the actual review verdict; builds only check it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

import content_version

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_PATH = "content/FRAMEWORK_VERSION"
REVIEW_PATH = "content/release-review.json"
TOC_PATH = "content/toc.yml"
EXAMPLE_TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt"}
EXAMPLE_ARTIFACT_DIRS = {"build", "dist", "node_modules", "__pycache__", ".git"}


class ReleaseError(ValueError):
    """A source or release precondition was not satisfied."""


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "--no-pager", "-C", str(root), *args], capture_output=True
    )
    if result.returncode:
        raise ReleaseError(
            f"git {' '.join(args)} failed: "
            f"{result.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return result.stdout


def resolve_ref(root: Path, ref: str) -> str:
    if not ref or ref.startswith("-"):
        raise ReleaseError("A nonempty, explicit Git ref is required.")
    try:
        return git(root, "rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()
    except ReleaseError as exc:
        raise ReleaseError(
            f"Cannot resolve base/source ref {ref!r}; fetch it or pass an existing ref."
        ) from exc


def normalize_text(data: bytes) -> bytes:
    """Use UTF-8 and LF on every platform, including lone CR line endings."""
    return data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def source_bytes(root: Path, name: str) -> bytes:
    path = root / name
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ReleaseError(f"Required source must be a regular file inside the repository: {name}")
    return normalize_text(path.read_bytes())


def _regular_example_file(root: Path, path: Path) -> None:
    examples = root / "examples"
    try:
        relative = path.relative_to(examples)
    except ValueError as exc:
        raise ReleaseError(f"Example input escapes examples/: {path}") from exc
    current = examples
    for part in ("", *relative.parts):
        current = current / part
        if current.is_symlink() or current.is_junction():
            raise ReleaseError(f"Example inputs cannot use symlinks or junctions: {path}")
    if not path.is_file() or not path.resolve().is_relative_to(examples.resolve()):
        raise ReleaseError(f"Example input must be a regular file inside examples/: {path}")


def example_input_paths(root: Path) -> list[Path]:
    """Inventory tracked/untracked text inputs, honoring Git ignores without writing an index."""
    try:
        git_dir = git(root, "rev-parse", "--absolute-git-dir").decode("utf-8").strip()
    except ReleaseError:
        git_dir = git(ROOT, "rev-parse", "--absolute-git-dir").decode("utf-8").strip()
    # An explicit work tree also supports standalone source snapshots inside an
    # ignored build directory: their own ignore files, not the parent's build rule, apply.
    listed = git(
        root, f"--git-dir={git_dir}", f"--work-tree={root}",
        "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", "examples",
    )
    paths = []
    for name in sorted({item.decode("utf-8") for item in listed.split(b"\0") if item}):
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or relative.parts[0] != "examples":
            raise ReleaseError(f"Invalid example input path: {name}")
        if name.lower().endswith(".lock.yml") or set(relative.parts[1:-1]) & EXAMPLE_ARTIFACT_DIRS:
            continue
        path = root / name
        if not path.exists() and not path.is_symlink():
            continue  # A tracked deletion changes the input set, rather than hashing old index bytes.
        _regular_example_file(root, path)
        if path.suffix not in EXAMPLE_TEXT_SUFFIXES and path.name != ".gitignore":
            raise ReleaseError(
                f"Unsupported example input type: {name}. Expected Markdown, JSON, YAML, TXT, or .gitignore."
            )
        paths.append(path)
    return paths


def example_source_bytes(root: Path, path: Path, *, normalize: bool = True) -> bytes:
    """Validate regular UTF-8 text; staging can retain the original line endings."""
    _regular_example_file(root, path)
    raw = path.read_bytes()
    try:
        normalized = normalize_text(raw)
    except UnicodeError as exc:
        raise ReleaseError(f"Example input is not valid UTF-8 text: {path}: {exc}") from exc
    if b"\0" in normalized:
        raise ReleaseError(f"Example input contains a NUL byte, not supported text: {path}")
    return normalized if normalize else raw


def validate_framework_version(version: str) -> str:
    try:
        return content_version.validate_framework_version(version)
    except ValueError as exc:
        raise ReleaseError(str(exc)) from exc


def read_framework_version(root: Path = ROOT) -> str:
    return validate_framework_version(source_bytes(root, FRAMEWORK_PATH).decode().strip())


def version_key(version: str) -> tuple[int, int, int]:
    parts = [int(part) for part in content_version.validate_version(version).split(".")]
    return tuple((parts + [0])[:3])


def _tag_version(ref: str) -> str | None:
    name = ref.removeprefix("refs/tags/")
    if not name.startswith(content_version.TAG_PREFIX):
        return None
    return content_version.validate_version(name[len(content_version.TAG_PREFIX) :])


def select_base(
    root: Path, explicit: str | None = None, env: Mapping[str, str] | None = None
) -> tuple[str, str]:
    if explicit is not None:
        resolve_ref(root, explicit)
        return explicit, "explicit"
    env = os.environ if env is None else env
    event_name = env.get("GITHUB_EVENT_NAME", "")
    if event_name in {"pull_request", "push"}:
        event_path = env.get("GITHUB_EVENT_PATH")
        if not event_path:
            raise ReleaseError(f"{event_name} comparison requires GITHUB_EVENT_PATH or --base.")
        try:
            event = json.loads(Path(event_path).read_text(encoding="utf-8"))
            ref = event["pull_request"]["base"]["sha"] if event_name == "pull_request" else event["before"]
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise ReleaseError(f"Cannot read the {event_name} comparison SHA; pass --base.") from exc
        if not isinstance(ref, str) or not re.fullmatch(r"[0-9a-fA-F]{40,64}", ref):
            raise ReleaseError(f"Invalid {event_name} comparison SHA; pass --base.")
        if set(ref) != {"0"}:
            resolve_ref(root, ref)
            return ref, "pull-request-base" if event_name == "pull_request" else "push-before"
        if event_name == "pull_request":
            raise ReleaseError("A pull request cannot have an all-zero base SHA.")

    tags = git(root, "tag", "--merged", "HEAD", "--list", "content-v*").decode().splitlines()
    versions = [(version_key(_tag_version(tag)), tag) for tag in tags]
    if not versions:
        raise ReleaseError("No reachable content-v tag is available; fetch tags or supply --base.")
    versions.sort()
    if len(versions) > 1 and versions[-1][0] == versions[-2][0]:
        raise ReleaseError("Several reachable tags identify the latest edition; supply --base.")
    return versions[-1][1], "latest-reachable-content-tag"


def _tree_files(root: Path, sha: str) -> set[str]:
    return {
        name.decode("utf-8")
        for name in git(root, "ls-tree", "-r", "-z", "--name-only", sha).split(b"\0")
        if name
    }


def _releasable(name: str) -> bool:
    return name == TOC_PATH or name.startswith("content/chapters/")


def _semantic_source(name: str, data: bytes) -> Any:
    text = normalize_text(data).decode("utf-8")
    if name != TOC_PATH:
        return text
    try:
        import yaml
    except ImportError as exc:
        raise ReleaseError("TOC comparison requires PyYAML: python -m pip install pyyaml") from exc
    try:
        toc = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ReleaseError(f"Invalid {TOC_PATH}: {exc}") from exc
    if not isinstance(toc, dict) or not isinstance(toc.get("chapters"), list):
        raise ReleaseError(f"{TOC_PATH} must contain a chapters list.")
    return json.dumps(toc, sort_keys=True, ensure_ascii=False, default=str)


def changes(root: Path, base: str) -> dict[str, Any]:
    sha = resolve_ref(root, base)
    old = {
        name: _semantic_source(name, git(root, "show", f"{sha}:{name}"))
        for name in sorted(_tree_files(root, sha))
        if _releasable(name)
    }
    names = {
        name.decode("utf-8")
        for name in git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0")
        if name and _releasable(name.decode("utf-8"))
    }
    current = {
        name: _semantic_source(name, source_bytes(root, name))
        for name in sorted(names)
        if (root / name).exists()
    }
    deleted = set(old) - set(current)
    added = set(current) - set(old)
    result: list[dict[str, str]] = []

    # Git detects edited tracked renames. Exact-content pairing also covers an
    # unstaged move whose destination is still untracked.
    diff = git(
        root, "diff", "--name-status", "-z", "--find-renames", sha,
        "--", "content/chapters", TOC_PATH,
    ).split(b"\0")
    index = 0
    while index < len(diff) and diff[index]:
        status = diff[index].decode()
        width = 3 if status.startswith(("R", "C")) else 2
        if status.startswith("R"):
            before, after = (part.decode("utf-8") for part in diff[index + 1 : index + 3])
            if before in deleted and after in added:
                result.append({"status": "renamed", "path": after, "previous_path": before})
                deleted.remove(before)
                added.remove(after)
        index += width
    for before in sorted(deleted.copy()):
        after = next((name for name in sorted(added) if current[name] == old[before]), None)
        if after is not None:
            result.append({"status": "renamed", "path": after, "previous_path": before})
            deleted.remove(before)
            added.remove(after)
    result.extend({"status": "deleted", "path": name} for name in deleted)
    result.extend({"status": "added", "path": name} for name in added)
    result.extend(
        {"status": "modified", "path": name}
        for name in old.keys() & current.keys()
        if old[name] != current[name]
    )
    return {
        "base": base,
        "base_sha": sha,
        "changed": bool(result),
        "changes": sorted(result, key=lambda item: (item["path"], item["status"])),
    }


def fingerprint(root: Path = ROOT) -> str:
    """Bind chapter/TOC/pin text and all supported nonignored example inputs, not build outputs."""
    chapters = sorted(
        path.relative_to(root).as_posix()
        for path in (root / "content" / "chapters").rglob("*")
        if path.is_file() and path.suffix == ".html"
    )
    if not chapters:
        raise ReleaseError("No chapter HTML sources were found.")
    examples = {path.relative_to(root).as_posix(): path for path in example_input_paths(root)}
    digest = hashlib.sha256()
    for name in sorted([*chapters, *examples, TOC_PATH, FRAMEWORK_PATH]):
        data = (
            example_source_bytes(root, examples[name]) if name in examples
            else source_bytes(root, name)
        )
        path_bytes = name.encode("utf-8")
        for part in (path_bytes, data):
            digest.update(len(part).to_bytes(8, "big"))
            digest.update(part)
    return digest.hexdigest()


def _report_name(root: Path, report: str) -> str:
    path = Path(report.replace("\\", "/"))
    path = path if path.is_absolute() else root / path
    try:
        name = path.absolute().relative_to(root).as_posix()
    except ValueError as exc:
        raise ReleaseError("The review report must be inside the repository.") from exc
    if ".." in PurePosixPath(name).parts or name == REVIEW_PATH:
        raise ReleaseError("Use a repository-relative review report, not the attestation itself.")
    source_bytes(root, name)
    return name


def review_record(root: Path, report: str, verdict: str) -> dict[str, Any]:
    """Record a process attestation only when the report's canonical verdict agrees."""
    if verdict not in {"ACCEPT", "REVISE"}:
        raise ReleaseError("Review verdict must be ACCEPT or REVISE.")
    name = _report_name(root, report)
    report_text = source_bytes(root, name)
    if not report_text.strip():
        raise ReleaseError("The referenced review report is empty.")
    markers = [
        line for line in report_text.decode("utf-8").splitlines()
        if re.search(r"\bVerdict[*_` \t]*:", line, flags=re.IGNORECASE)
    ]
    if len(markers) != 1 or not re.fullmatch(r"Verdict: (ACCEPT|REVISE)", markers[0]):
        raise ReleaseError(
            "The review report must contain exactly one canonical standalone line "
            "'Verdict: ACCEPT' or 'Verdict: REVISE', without additional verdict markers."
        )
    report_verdict = markers[0].removeprefix("Verdict: ")
    if report_verdict != verdict:
        raise ReleaseError(
            f"Report verdict {report_verdict} does not match the supplied verdict {verdict}."
        )
    return {
        "schema_version": 1,
        "verdict": verdict,
        "framework_version": read_framework_version(root),
        "fingerprint": fingerprint(root),
        "report_path": name,
        "report_sha256": hashlib.sha256(report_text).hexdigest(),
    }


def check_review(root: Path) -> dict[str, Any]:
    try:
        evidence = json.loads(source_bytes(root, REVIEW_PATH))
    except (OSError, ValueError) as exc:
        raise ReleaseError(
            f"Missing or invalid {REVIEW_PATH}; obtain an editorial review and record its verdict."
        ) from exc
    if not isinstance(evidence, dict) or evidence.get("schema_version") != 1:
        raise ReleaseError("Unsupported or invalid review attestation schema.")
    if evidence.get("verdict") != "ACCEPT":
        raise ReleaseError("Editorial review must have an explicit ACCEPT verdict.")
    if not isinstance(evidence.get("report_path"), str):
        raise ReleaseError("Review attestation is missing its report path.")
    expected = review_record(root, evidence["report_path"], "ACCEPT")
    for key in ("framework_version", "fingerprint", "report_path", "report_sha256"):
        if evidence.get(key) != expected[key]:
            raise ReleaseError(f"Stale review evidence: {key} does not match the current source/report.")
    return evidence


def _baseline_version(root: Path, ref: str, sha: str) -> tuple[str, str]:
    tag_version = _tag_version(ref)
    if "content/VERSION" in _tree_files(root, sha):
        version = content_version.validate_version(
            git(root, "show", f"{sha}:content/VERSION").decode("utf-8").strip()
        )
        if tag_version is not None and tag_version != version:
            raise ReleaseError(f"Tag {ref} disagrees with its content/VERSION ({version}).")
        return version, "content/VERSION"
    if tag_version is not None:
        name = ref.removeprefix("refs/tags/")
        if name in git(root, "tag", "--points-at", sha, "--list", name).decode().splitlines():
            return tag_version, "legacy-content-tag"
    raise ReleaseError(
        f"Baseline {ref!r} has no content/VERSION. Use an explicit legacy content-v tag "
        "for comparison; a missing version is never treated as 0.0."
    )


def release_notes(root: Path, version: str) -> str:
    releases = [
        release for release in content_version.parse_changelog(root / "content" / "CHANGELOG.md")
        if release.version == version
    ]
    if len(releases) != 1:
        raise ReleaseError(f"Expected exactly one changelog entry for content version {version}.")
    body = re.sub(r"<!--.*?-->", "", releases[0].body, flags=re.DOTALL)
    if not any(re.search(r"\w", line) for line in body.splitlines() if not line.lstrip().startswith("#")):
        raise ReleaseError(f"The changelog entry for {version} must contain nonempty release notes.")
    return releases[0].body


def check(
    root: Path = ROOT, base: str | None = None, env: Mapping[str, str] | None = None
) -> dict[str, Any]:
    version = content_version.read_version(root / "content" / "VERSION")
    framework = read_framework_version(root)
    ref, reason = select_base(root, base, env)
    delta = changes(root, ref)
    previous, version_source = _baseline_version(root, ref, delta["base_sha"])
    if delta["changed"]:
        if version_key(version) <= version_key(previous):
            raise ReleaseError(
                f"Reader-visible content changed since {ref}; bump content/VERSION "
                f"monotonically above {previous} (found {version})."
            )
    elif version != previous:
        raise ReleaseError(
            f"No reader-visible content changed since {ref}; keep edition {previous}. "
            "Metadata, examples, research, and tooling alone do not justify a new content edition."
        )
    release_notes(root, version)
    evidence = check_review(root)
    return {
        "status": "PASS",
        "version": version,
        "tag": content_version.tag_for(version),
        "framework_version": framework,
        "baseline_version": previous,
        "baseline_version_source": version_source,
        "base_reason": reason,
        "fingerprint": evidence["fingerprint"],
        **delta,
    }


def github_get(endpoint: str, *, allow_not_found: bool = False) -> dict[str, Any] | None:
    """Only an explicit HTTP 404 can be treated as absent; other failures stop."""
    result = subprocess.run(
        ["gh", "api", "--include", endpoint], capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    headers = list(re.finditer(r"^HTTP/\S+\s+([0-9]{3})\b", result.stdout, re.MULTILINE))
    status = int(headers[-1].group(1)) if headers else None
    if status == 404 and allow_not_found:
        return None
    if result.returncode or status != 200:
        raise ReleaseError(
            f"GitHub API request {endpoint!r} failed (HTTP {status or 'unavailable'}, "
            f"exit {result.returncode}). {result.stderr.strip()}"
        )
    payload = re.split(r"\r?\n\r?\n", result.stdout[headers[-1].start() :], maxsplit=1)
    try:
        data = json.loads(payload[1])
    except (IndexError, ValueError) as exc:
        raise ReleaseError("GitHub API returned an invalid JSON response.") from exc
    if not isinstance(data, dict):
        raise ReleaseError("GitHub API returned an unexpected response shape.")
    return data


def github_release(repository: str, tag: str) -> dict[str, Any] | None:
    release = github_get(f"repos/{repository}/releases/tags/{tag}", allow_not_found=True)
    if release is None:
        # An inaccessible private repository also returns 404. Confirm repository
        # access before interpreting the release response as "not yet published".
        repo = github_get(f"repos/{repository}")
        if repo.get("full_name", "").lower() != repository.lower():
            raise ReleaseError("Cannot confirm access to the requested release repository.")
    return release


def release_plan(
    root: Path, repository: str, base: str | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Read-only publication planning; existing tags always select their own source."""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ReleaseError("Expected a repository in owner/name form.")
    version = content_version.read_version(root / "content" / "VERSION")
    tag = content_version.tag_for(version)
    asset = f"gh-aw-book-v{version}.pdf"
    metadata = github_release(repository, tag)
    if metadata is not None:
        if metadata.get("tag_name") != tag or not isinstance(metadata.get("assets"), list):
            raise ReleaseError("The release API response does not match the requested tag/assets.")
        matching = [item for item in metadata["assets"] if item.get("name") == asset]
        if matching:
            if (
                len(matching) == 1
                and matching[0].get("state") == "uploaded"
                and type(matching[0].get("size")) is int
                and matching[0]["size"] > 0
            ):
                return {"action": "skip", "version": version, "tag": tag, "asset": asset}
            details = "; ".join(
                f"id={item.get('id')!r}, state={item.get('state')!r}, size={item.get('size')!r}"
                for item in matching
            )
            raise ReleaseError(
                f"Release {tag} has an incomplete or ambiguous upload for {asset} ({details}). "
                "A completed asset must have state='uploaded' and a positive integer size. "
                f"Inspect https://github.com/{repository}/releases/tag/{tag}; have a maintainer "
                "restore the correct tagged PDF or remove the incomplete asset before retrying "
                "exact-tag repair. No asset was deleted or overwritten."
            )
    tag_exists = tag in git(root, "tag", "--list", tag).decode().splitlines()
    if metadata is not None and not tag_exists:
        raise ReleaseError(f"Release {tag} exists but its tag is unavailable; fetch tags before repair.")
    source = resolve_ref(root, tag if tag_exists else "HEAD")
    files = _tree_files(root, source)
    missing = {"content/VERSION", FRAMEWORK_PATH, REVIEW_PATH} - files
    if missing:
        raise ReleaseError(
            f"Cannot {'repair' if metadata is not None else 'publish'} {tag} from {source}: "
            f"source lacks required release metadata ({', '.join(sorted(missing))}). "
            "Legacy tags are never rebuilt with fabricated versions or a different checkout."
        )
    source_version = content_version.validate_version(
        git(root, "show", f"{source}:content/VERSION").decode("utf-8").strip()
    )
    if source_version != version:
        raise ReleaseError(
            f"{tag} would identify content {version}, but the selected source contains {source_version}."
        )
    framework = validate_framework_version(
        git(root, "show", f"{source}:{FRAMEWORK_PATH}").decode("utf-8").strip()
    )
    comparison, reason = (tag, "existing-tag-replay") if tag_exists else select_base(root, base, env)
    return {
        "action": "upload" if metadata is not None else "create",
        "version": version,
        "tag": tag,
        "asset": asset,
        "source_sha": source,
        "framework_version": framework,
        "comparison_base": comparison,
        "base_reason": reason,
        "tag_exists": tag_exists,
    }


class _GeneratedVersions(HTMLParser):
    def __init__(self):
        super().__init__()
        self.versions: list[str] = []
        self.metadata: dict[str, list[str]] = {}
        self.capture: tuple[str, list[str]] | None = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("name") in {"book-content-version", "gh-aw-framework-version"}:
            self.metadata.setdefault(attrs["name"], []).append(attrs.get("content", ""))
        if "version-pill" in attrs.get("class", "").split():
            match = re.match(r"Content (?:version |edition v)(\S+)", attrs.get("title", ""))
            if match:
                self.versions.append(match.group(1))
        if (tag == "a" and attrs.get("href", "").endswith("versions.html")) or (
            "book-cover-meta" in attrs.get("class", "").split()
        ):
            self.capture = (tag, [])

    def handle_data(self, data):
        if self.capture:
            self.capture[1].append(data)

    def handle_endtag(self, tag):
        if self.capture and self.capture[0] == tag:
            text = "".join(self.capture[1]).strip()
            match = re.match(r"(?:v|Version )([0-9]+(?:\.[0-9]+){1,2})(?:\s|$)", text)
            if match:
                self.versions.append(match.group(1))
            self.capture = None


def check_generated(root: Path) -> dict[str, Any]:
    """Check the edition markers already emitted by the HTML/PDF build."""
    version = content_version.read_version(root / "content" / "VERSION")
    framework = read_framework_version(root)
    pages = [root / "site" / name for name in ("index.html", "book.html", "versions.html")]
    chapters = sorted((root / "site" / "chapters").glob("*.html"))
    if not chapters:
        raise ReleaseError("The generated site has no chapter pages.")
    for page in [*pages, *chapters]:
        parser = _GeneratedVersions()
        parser.feed(page.read_text(encoding="utf-8"))
        markers = parser.metadata.get("book-content-version", [])
        if markers != [version] or any(marker != version for marker in parser.versions):
            raise ReleaseError(f"Generated content version mismatch or missing marker: {page.name}")
        if parser.metadata.get("gh-aw-framework-version", []) != [framework]:
            raise ReleaseError(f"Generated framework version mismatch or missing marker: {page.name}")
    pdf = root / "site" / "gh-aw-book.pdf"
    if not pdf.is_file() or pdf.stat().st_size < 20 * 1024:
        raise ReleaseError("The generated PDF is missing or unexpectedly small.")
    with pdf.open("rb") as handle:
        if handle.read(5) != b"%PDF-":
            raise ReleaseError("The generated PDF has an invalid header.")
    return {"status": "PASS", "version": version, "framework_version": framework,
            "html_pages": len(pages) + len(chapters), "pdf": "site/gh-aw-book.pdf"}


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Source checkout (default: this repository).")
    commands = parser.add_subparsers(dest="command", required=True)
    change_parser = commands.add_parser("changes", help="List reader-visible source changes as JSON.")
    change_parser.add_argument("--base", required=True)
    check_parser = commands.add_parser("check", help="Check edition, changelog, pin, and review evidence.")
    check_parser.add_argument("--base")
    commands.add_parser("fingerprint", help="Print the LF-normalized source SHA256.")
    commands.add_parser("framework-version", help="Print the validated exact framework tag.")
    commands.add_parser("notes", help="Print the validated current changelog entry.")
    commands.add_parser("check-generated", help="Check generated HTML version markers and PDF output.")
    plan_parser = commands.add_parser("release-plan", help="Read-only create/repair/skip source selection.")
    plan_parser.add_argument("--repo", required=True)
    plan_parser.add_argument("--base")
    review_parser = commands.add_parser("record-review", help="Record an actual editorial verdict.")
    review_parser.add_argument(
        "--report", required=True,
        help="Markdown report with exactly one standalone Verdict: ACCEPT or Verdict: REVISE line.",
    )
    review_parser.add_argument("--verdict", choices=("ACCEPT", "REVISE"), required=True)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "fingerprint":
            print(fingerprint(root))
        elif args.command == "framework-version":
            print(read_framework_version(root))
        elif args.command == "notes":
            print(release_notes(root, content_version.read_version(root / "content" / "VERSION")))
        elif args.command == "changes":
            print(_json(changes(root, args.base)), end="")
        elif args.command == "check":
            print(_json(check(root, args.base)), end="")
        elif args.command == "check-generated":
            print(_json(check_generated(root)), end="")
        elif args.command == "release-plan":
            print(_json(release_plan(root, args.repo, args.base)), end="")
        elif args.command == "record-review":
            record = _json(review_record(root, args.report, args.verdict))
            (root / REVIEW_PATH).write_text(record, encoding="utf-8", newline="\n")
            print(record, end="")
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
