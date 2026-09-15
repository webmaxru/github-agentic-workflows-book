from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import release_content


class SourceTest(unittest.TestCase):
    def setUp(self):
        scratch = ROOT.parent / "build" / "tests"
        scratch.mkdir(parents=True, exist_ok=True)
        directory = TemporaryDirectory(prefix="release-", dir=scratch)
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        self.put(".gitignore", "build/\n")
        self.put("content/VERSION", "1.1\n")
        self.put("content/FRAMEWORK_VERSION", "v0.81.6\n")
        self.put("content/CHANGELOG.md", "## [1.1] - 2026-07-08\n\nExisting edition.\n")
        self.put("content/toc.yml", "title: Book\nchapters:\n  - id: one\n    slug: one\n")
        self.put("content/chapters/one.html", "<p>A chapter.\nA second line.</p>\n")
        self.put("examples/ch01/one.md", "---\non: workflow_dispatch\n---\nA workflow.\n")
        self.put("examples/ch01/shared/policy.md", "---\ntools:\n  github:\n---\nPolicy.\n")

    def put(self, name: str, text: str) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        return path

    def accept(self):
        self.put("content/research/review.md", "Verdict: ACCEPT\n\nFixture source reviewed.\n")
        record = release_content.review_record(self.root, "content/research/review.md", "ACCEPT")
        self.put("content/release-review.json", json.dumps(record))
        return record

    def cli(self, script: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(ROOT / script), "--root", str(self.root), *args],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8",
        )


class RepositoryTest(SourceTest):
    def setUp(self):
        super().setUp()
        self.git("init", "--quiet")
        self.git("config", "core.autocrlf", "false")
        self.commit()
        self.git("tag", "content-v1.1")
        self.base = self.git("rev-parse", "HEAD")

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", "-c", "core.hooksPath=disabled-hooks", "-C", str(self.root), *args],
            capture_output=True, text=True, encoding="utf-8",
        )
        if result.returncode:
            raise AssertionError(result.stderr)
        return result.stdout.strip()

    def commit(self):
        self.git("add", "--all")
        self.git(
            "-c", "user.name=Book Tests", "-c", "user.email=book-tests@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "Test fixture",
        )
