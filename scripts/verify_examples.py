#!/usr/bin/env python3
"""Strictly compile every standalone example with one exact gh-aw compiler.

Shared components are identified by the ``shared/`` directory convention, not
by parsing frontmatter: malformed standalone workflows must fail, never disappear
from the verification corpus. Each workflow is compiled in a fresh Git repository
with its chapter's original Markdown files under .github/workflows, preserving
relative imports without ever staging files in the book's live workflows directory.
The isolated repositories receive a credential-free source origin, or the public
book repository when no usable GitHub origin exists. This configures context only;
it never fetches or runs workflows. Scratch space lives under this tool checkout's
build/v, not under potentially deeply nested input directories.
Setup/cleanup errors preserve per-workflow results but fail the overall report.
The passed/failed counts describe compilation only; callers must honor status and
environment_errors even when every workflow compiled successfully.
An emitted lock must start with gh-aw metadata naming the expected compiler and
literal strict=true. Compilation uses --strict only, not repository/scanner-dependent
--validate checks.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Sequence
from urllib.parse import urlsplit

from release_content import ROOT, ReleaseError, read_framework_version, validate_framework_version

VERSION_OUTPUT_RE = re.compile(r"(?<![\w.-])v[0-9]+\.[0-9]+\.[0-9]+(?:[-+][\w.-]+)?(?![\w.-])")
SCRATCH_ROOT = ROOT / "build" / "v"
BOOK_REMOTE = "https://github.com/webmaxru/github-agentic-workflows-book.git"
LOCK_METADATA_PREFIX = "# gh-aw-metadata: "


def compiler_version(compiler: Sequence[str], root: Path) -> tuple[str, str]:
    result = subprocess.run(
        [*compiler, "version"], cwd=root, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    output = result.stdout + result.stderr
    if result.returncode:
        raise ReleaseError(f"Compiler version command failed (exit {result.returncode}):\n{output}")
    versions = set(VERSION_OUTPUT_RE.findall(output))
    if len(versions) != 1:
        raise ReleaseError(f"Cannot identify exactly one compiler version from:\n{output}")
    return versions.pop(), output


def discover_examples(root: Path) -> tuple[list[Path], list[Path]]:
    workflows, fragments = [], []
    for path in sorted((root / "examples").rglob("*")):
        if not path.is_file() or path.suffix != ".md":
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(root / "examples"):
            raise ReleaseError(f"Examples must be regular files inside examples/: {path}")
        relative = path.relative_to(root / "examples")
        (fragments if "shared" in relative.parts[:-1] else workflows).append(path)
    if not workflows:
        raise ReleaseError("No standalone example workflows were found.")
    return workflows, fragments


def _canonical_remote(value: str) -> str | None:
    """Keep only a GitHub repository identity, never credentials/query/fragment data."""
    value = value.strip()
    try:
        if "://" in value:
            parsed = urlsplit(value)
            if parsed.scheme not in {"https", "http", "ssh", "git"} or parsed.hostname != "github.com":
                return None
            path = parsed.path.strip("/")
        else:
            match = re.fullmatch(
                r"(?:[^@\s/]+@)?github\.com:([^?#\s]+)(?:[?#].*)?", value, flags=re.IGNORECASE,
            )
            if not match:
                return None
            path = match.group(1).strip("/")
    except ValueError:
        return None
    path = path.removesuffix(".git")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9][A-Za-z0-9_.-]*", path):
        return None
    return f"https://github.com/{path}.git"


def repository_context(root: Path) -> dict[str, str]:
    # Reading the raw local config avoids expanding credential-bearing insteadOf
    # rewrites. Never include the raw URL or its diagnostics in a report.
    result = subprocess.run(
        ["git", "-C", str(root), "config", "--local", "--get", "remote.origin.url"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    remote = _canonical_remote(result.stdout) if result.returncode == 0 else None
    return {
        "url": remote or BOOK_REMOTE,
        "source": "source-origin" if remote else "book-default",
    }


def _stage(root: Path, workflow: Path, repo: Path, remote: str) -> Path:
    relative = workflow.relative_to(root / "examples")
    chapter = root / "examples" / relative.parts[0] if len(relative.parts) > 1 else root / "examples"
    target = repo / ".github" / "workflows"
    target.mkdir(parents=True)
    for source in chapter.rglob("*"):
        if source.is_file() and source.suffix == ".md":
            destination = target / source.relative_to(chapter)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
    for command in (
        ["git", "init", "--quiet", str(repo)],
        ["git", "-C", str(repo), "remote", "add", "origin", remote],
    ):
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if result.returncode:
            raise ReleaseError(f"Cannot prepare isolated example repository:\n{result.stderr}")
    return target / workflow.relative_to(chapter)


def _environment_error(report: dict[str, Any], phase: str, error: Exception, path: Path) -> None:
    entry: dict[str, Any] = {
        "phase": phase, "error": str(error), "error_type": type(error).__name__, "path": str(path),
    }
    for attr in ("errno", "winerror"):
        if getattr(error, attr, None) is not None:
            entry[attr] = getattr(error, attr)
    report["environment_errors"].append(entry)
    report.setdefault("error", str(error))


def _long_path(path: Path) -> str:
    value = str(path.absolute())
    if os.name == "nt" and not value.startswith("\\\\?\\"):
        return "\\\\?\\UNC\\" + value[2:] if value.startswith("\\\\") else "\\\\?\\" + value
    return value


def _cleanup_run_directory(run: Path, scratch: Path) -> None:
    """Recover only this invocation's exact directory, including long Windows paths."""
    if run.parent != scratch or run.resolve().parent != scratch.resolve():
        raise ReleaseError("Refusing to clean a directory outside this invocation's scratch location.")
    try:
        shutil.rmtree(_long_path(run))
    except FileNotFoundError:
        pass


def _read_lock_metadata(lock: Path, version: str) -> dict[str, Any]:
    with open(_long_path(lock), encoding="utf-8") as handle:
        first_line = handle.readline()
    if not first_line.startswith(LOCK_METADATA_PREFIX):
        raise ReleaseError("Missing gh-aw metadata header on the first lock line.")
    try:
        metadata = json.loads(first_line[len(LOCK_METADATA_PREFIX) :])
    except json.JSONDecodeError as exc:
        raise ReleaseError(f"Malformed gh-aw lock metadata JSON: {exc}") from exc
    if not isinstance(metadata, dict):
        raise ReleaseError("Malformed gh-aw lock metadata: expected a JSON object.")
    if metadata.get("compiler_version") != version:
        raise ReleaseError(
            f"Lock metadata compiler_version mismatch: expected {version}, "
            f"found {metadata.get('compiler_version')!r}."
        )
    if metadata.get("strict") is not True:
        raise ReleaseError(
            f"Lock metadata strict must be boolean true; found {metadata.get('strict')!r}."
        )
    return metadata


def verify_examples(
    root: Path, compiler: Sequence[str], version: str
) -> dict[str, Any]:
    version = validate_framework_version(version)
    workflows, fragments = discover_examples(root)
    report: dict[str, Any] = {
        "schema_version": 1,
        "expected_version": version,
        "compiler": list(compiler),
        "strict": True,
        "fragments": [path.relative_to(root).as_posix() for path in fragments],
        "results": [],
        "environment_errors": [],
    }
    try:
        actual, output = compiler_version(compiler, root)
        report.update(compiler_version=actual, version_output=output)
        if actual != version:
            raise ReleaseError(f"Compiler version mismatch: expected {version}, found {actual}.")
    except (OSError, ValueError) as exc:
        report["error"] = str(exc)
        report["results"] = [
            {"path": path.relative_to(root).as_posix(), "status": "FAIL", "error": str(exc)}
            for path in workflows
        ]
    else:
        scratch = SCRATCH_ROOT
        temporary = None
        run = None
        phase = "setup"
        try:
            scratch = scratch.resolve()
            report["repository_context"] = repository_context(root)
            if not scratch.is_relative_to(ROOT):
                raise ReleaseError("Example scratch space must stay inside the tool's project checkout.")
            scratch.mkdir(parents=True, exist_ok=True)
            temporary = TemporaryDirectory(prefix="", dir=scratch)
            run = Path(temporary.name)
            phase = "compilation"
            for number, workflow in enumerate(workflows):
                item: dict[str, Any] = {"path": workflow.relative_to(root).as_posix()}
                report["results"].append(item)
                try:
                    repo = run / str(number)
                    staged = _stage(root, workflow, repo, report["repository_context"]["url"])
                    relative = str(staged.relative_to(repo))
                    result = subprocess.run(
                        [*compiler, "compile", "--strict", relative], cwd=repo,
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                    )
                    item.update(
                        status="FAIL",
                        exit_code=result.returncode,
                        stdout=result.stdout,
                        stderr=result.stderr,
                        lock_emitted=False,
                    )
                    lock = Path(_long_path(staged.with_suffix(".lock.yml")))
                    emitted = lock.is_file() and lock.stat().st_size > 0
                    item["lock_emitted"] = emitted
                    if emitted:
                        try:
                            item["lock_metadata"] = _read_lock_metadata(lock, version)
                        except (OSError, ValueError) as exc:
                            item.update(error=str(exc), metadata_error=str(exc))
                        else:
                            if result.returncode == 0:
                                item["status"] = "PASS"
                    if result.returncode == 0 and not emitted:
                        item["error"] = "Compiler returned success without emitting a nonempty lock file."
                except (OSError, ValueError) as exc:
                    item.update(status="FAIL", error=str(exc))
        except Exception as exc:
            _environment_error(report, phase, exc, run or scratch)
        finally:
            if temporary is not None:
                try:
                    temporary.cleanup()
                except Exception as exc:
                    _environment_error(report, "cleanup", exc, run)
                    try:
                        _cleanup_run_directory(run, scratch)
                    except Exception as recovery:
                        _environment_error(report, "cleanup-retry", recovery, run)
                        report["cleanup_pending"] = str(run)
                    else:
                        report["cleanup_recovered"] = True
        for item in report["results"]:
            if "status" not in item:
                item.update(status="FAIL", error=report["error"])
        report["results"].extend(
            {"path": path.relative_to(root).as_posix(), "status": "FAIL", "error": report["error"]}
            for path in workflows[len(report["results"]) :]
        )
    report["passed"] = sum(item["status"] == "PASS" for item in report["results"])
    report["failed"] = len(workflows) - report["passed"]
    report["status"] = "PASS" if report["failed"] == 0 and not report["environment_errors"] else "FAIL"
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Source checkout (default: this repository).")
    parser.add_argument("--compiler", type=Path, help="Absolute path to an isolated gh-aw executable.")
    parser.add_argument("--version", help="Exact expected tag (default: content/FRAMEWORK_VERSION).")
    parser.add_argument(
        "--report", type=Path, help="Write all results and exact compiler/environment errors as JSON.",
    )
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        if args.compiler is not None:
            if not args.compiler.is_absolute() or not args.compiler.is_file():
                raise ReleaseError("--compiler must name an existing absolute executable path.")
            compiler = [str(args.compiler)]
        else:
            compiler = ["gh", "aw"]
        version = args.version if args.version is not None else read_framework_version(root)
        report = verify_examples(root, compiler, version)
        if args.report:
            try:
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(
                    json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n",
                )
            except (OSError, ValueError) as exc:
                _environment_error(report, "report-write", exc, args.report)
                report["status"] = "FAIL"
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        print(rendered, end="")
        return 0 if report["status"] == "PASS" else 1
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
