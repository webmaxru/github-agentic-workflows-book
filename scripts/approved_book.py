#!/usr/bin/env python3
"""Verify exact-head approval and content-only scope using the GitHub API."""

import argparse
import base64
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

OWNER = "webmaxru"
SHA = re.compile(r"[0-9a-f]{40}\Z")
COMMAND = re.compile(r"/release-book ([0-9a-f]{40})\Z")


class PolicyError(ValueError):
    pass


class GitHubError(RuntimeError):
    pass


def allowed_path(path):
    if path in {"content/VERSION", "content/FRAMEWORK_VERSION", "content/CHANGELOG.md",
                "content/release-review.json", "content/toc.yml", "content/outline.md",
                "content/playbook-brief.md"}:
        return True
    if path.startswith(("content/chapters/", "content/research/", "examples/")):
        return True
    if path in {"site/index.html", "site/book.html", "site/versions.html", "site/404.html",
                "site/llms.txt", "site/llms-full.txt", "site/sitemap.xml",
                "site/robots.txt", "site/site.webmanifest"}:
        return True
    return bool(re.fullmatch(r"site/chapters/[^/]+\.html", path))


def approved(pr, reviews, comments):
    head = pr["head"]["sha"]
    if pr["user"]["login"].lower() == OWNER:
        commands = [c for c in comments
                    if c.get("user", {}).get("login", "").lower() == OWNER
                    and COMMAND.fullmatch(c.get("body", "").strip())]
        if not commands:
            return False
        latest = max(commands, key=lambda c: (c.get("updated_at") or c.get("created_at") or "", c["id"]))
        return COMMAND.fullmatch(latest["body"].strip())[1] == head
    own = [r for r in reviews if r.get("user", {}).get("login", "").lower() == OWNER]
    if not own:
        return False
    latest = max(own, key=lambda r: (r.get("submitted_at") or "", r.get("id", 0)))
    return latest.get("state") == "APPROVED" and latest.get("commit_id") == head


def eligibility(pr, files, reviews, comments, repository, merged=False):
    head = pr.get("head", {}).get("sha", "")
    base = pr.get("base", {})
    expected_state = "closed" if merged else "open"
    head_repo = pr.get("head", {}).get("repo") or {}
    if (pr.get("state") != expected_state or pr.get("draft") or base.get("ref") != "main"
            or head_repo.get("full_name", "").lower() != repository.lower()
            or not SHA.fullmatch(head) or (merged and not pr.get("merged"))):
        raise PolicyError("PR must be a non-draft same-repository content PR targeting main.")
    if len(files) != pr.get("changed_files") or not files:
        raise PolicyError("Changed file list is incomplete or empty.")
    paths = []
    for file in files:
        paths.append(file["filename"])
        if file.get("previous_filename"):
            paths.append(file["previous_filename"])
    if not all(allowed_path(path) for path in paths):
        raise PolicyError("PR contains paths outside the content-only allowlist.")
    if not any(path.startswith("content/chapters/") or path == "content/toc.yml" for path in paths):
        raise PolicyError("PR does not change a chapter or TOC.")
    if not approved(pr, reviews, comments):
        raise PolicyError("Owner approval for the current head is missing.")
    return {"number": pr["number"], "head": head, "base": base["sha"]}


def checks_pass(checks, statuses, require_preflight=True):
    latest = {}
    for check in checks:
        name = check.get("name")
        app = check.get("app") or {}
        key = (name, app.get("id") or app.get("slug"))
        if key not in latest or check.get("id", 0) > latest[key].get("id", 0):
            latest[key] = check
    preflights = [check for (name, _), check in latest.items()
                  if name == "Book release preflight"
                  and (check.get("app") or {}).get("slug") == "github-actions"]
    preflight = max(preflights, key=lambda check: check.get("id", 0)) if preflights else None
    if require_preflight and (
        not preflight or preflight.get("status") != "completed"
        or preflight.get("conclusion") != "success"
    ):
        raise PolicyError("Book release preflight has not succeeded on the PR head.")
    if any(c.get("status") != "completed" or c.get("conclusion") not in {"success", "neutral", "skipped"}
           for c in latest.values()):
        raise PolicyError("A check on the PR head is pending or unsuccessful.")
    latest_status = {}
    for status in statuses:
        latest_status.setdefault(status["context"], status)
    if any(s.get("state") != "success" for s in latest_status.values()):
        raise PolicyError("A commit status on the PR head is pending or unsuccessful.")


class GitHub:
    def __init__(self, repository, token):
        self.repo = repository
        self.token = token

    def request(self, path, method="GET", data=None):
        body = json.dumps(data).encode() if data is not None else None
        request = Request("https://api.github.com" + path, data=body, method=method, headers={
            "Authorization": "Bearer " + self.token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        })
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except (HTTPError, URLError) as exc:
            raise GitHubError(f"GitHub API {method} {path} failed: {exc}") from exc

    def get(self, suffix):
        return self.request(f"/repos/{self.repo}/{suffix}")

    def pages(self, suffix, key=None):
        result = []
        for page in range(1, 101):
            separator = "&" if "?" in suffix else "?"
            response = self.get(f"{suffix}{separator}{urlencode({'per_page': 100, 'page': page})}")
            items = response[key] if key else response
            result.extend(items)
            if len(items) < 100:
                return result
        raise GitHubError(f"Pagination limit exceeded for {suffix}.")

    def inspect(self, number, merged=False):
        pr = self.get(f"pulls/{number}")
        result = eligibility(pr, self.pages(f"pulls/{number}/files"),
                             self.pages(f"pulls/{number}/reviews"),
                             self.pages(f"issues/{number}/comments"), self.repo, merged)
        checks_pass(self.pages(f"commits/{result['head']}/check-runs", "check_runs"),
                    self.pages(f"commits/{result['head']}/statuses"))
        if not merged:
            merge_ref = pr.get("merge_commit_sha")
            if not merge_ref or not SHA.fullmatch(merge_ref):
                raise PolicyError("GitHub has not produced a PR merge commit.")
            parents = [parent["sha"] for parent in self.get(f"commits/{merge_ref}").get("parents", [])]
            if parents != [result["base"], result["head"]]:
                raise PolicyError("PR test merge does not match the current base and head.")
            checks_pass(self.pages(f"commits/{merge_ref}/check-runs", "check_runs"),
                        self.pages(f"commits/{merge_ref}/statuses"), require_preflight=False)
        if merged:
            result["merge_sha"] = pr["merge_commit_sha"]
        return result

    def previous_edition(self, head, merged=False):
        blob = self.get(f"contents/content/VERSION?ref={head}")
        if blob.get("encoding") != "base64":
            raise PolicyError("Unable to read the proposed content edition.")
        try:
            version = base64.b64decode(blob["content"], validate=False).decode("utf-8").strip()
        except (ValueError, UnicodeError) as exc:
            raise PolicyError("Invalid content edition response.") from exc
        pattern = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)(?:\.(0|[1-9]\d*))?\Z")
        match = pattern.fullmatch(version)
        if not match:
            raise PolicyError("Invalid content edition.")
        key = tuple(int(part or 0) for part in match.groups())
        editions = []
        drafts = []
        for release in self.pages("releases"):
            tag = release.get("tag_name", "")
            old = pattern.fullmatch(tag.removeprefix("content-v")) if tag.startswith("content-v") else None
            if old and not release.get("prerelease"):
                item = (tuple(int(part or 0) for part in old.groups()), tag)
                (drafts if release.get("draft") else editions).append(item)
        if not merged and any(old >= key for old, _ in editions):
            raise PolicyError("Proposed edition is not newer than the latest published edition.")
        if merged and any(old > key for old, _ in editions) and (key, f"content-v{version}") not in editions + drafts:
            raise PolicyError("Cannot create an older edition after a newer publication.")
        previous = sorted((old, tag) for old, tag in editions if old < key)
        if not previous:
            raise PolicyError("No previous published content edition is available.")
        if len(previous) > 1 and previous[-1][0] == previous[-2][0]:
            raise PolicyError("Ambiguous previous published content edition.")
        return previous[-1][1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("select", "merge", "verify-merged"))
    parser.add_argument("--number", type=int)
    parser.add_argument("--head")
    parser.add_argument("--base")
    parser.add_argument("--comparison")
    parser.add_argument("--merge-sha")
    args = parser.parse_args()
    try:
        api = GitHub(os.environ["GITHUB_REPOSITORY"], os.environ["GH_TOKEN"])
        if args.action == "select":
            numbers = [args.number] if args.number else [
                pr["number"] for pr in api.pages("pulls?state=open&base=main")
            ]
            selected = None
            for number in numbers:
                try:
                    pr = api.get(f"pulls/{number}")
                    if args.number and pr.get("merged"):
                        selected = api.inspect(number, merged=True)
                        parents = api.get(f"commits/{selected['merge_sha']}").get("parents", [])
                        if len(parents) != 2 or parents[1].get("sha") != selected["head"]:
                            raise PolicyError("Recovery requires a merge commit containing the approved head.")
                        selected["base"] = parents[0]["sha"]
                    else:
                        selected = api.inspect(number)
                    selected["comparison"] = api.previous_edition(selected["head"], bool(selected.get("merge_sha")))
                    break
                except PolicyError as exc:
                    if args.number:
                        raise
                    print(f"PR #{number}: {exc}", file=sys.stderr)
            print(json.dumps(selected or {}))
        elif args.action == "merge":
            if (not args.number or not SHA.fullmatch(args.head or "") or not SHA.fullmatch(args.base or "")
                    or not args.comparison):
                raise PolicyError("Merge requires PR number, exact head, base and edition baseline.")
            current = api.inspect(args.number)
            if current["head"] != args.head or current["base"] != args.base:
                raise PolicyError("PR head or base changed after preflight.")
            if api.previous_edition(current["head"]) != args.comparison:
                raise PolicyError("Published edition baseline changed after preflight.")
            response = api.request(f"/repos/{api.repo}/pulls/{args.number}/merge", "PUT",
                                   {"sha": args.head, "merge_method": "merge"})
            if response.get("merged") is not True or not SHA.fullmatch(response.get("sha", "")):
                raise PolicyError("GitHub did not confirm the merge.")
            commit = api.get(f"commits/{response['sha']}")
            if not commit.get("parents") or commit["parents"][0].get("sha") != args.base:
                raise PolicyError("Merge base changed concurrently; refusing publication.")
            print(json.dumps({"merge_sha": response["sha"], **current}))
        else:
            current = api.inspect(args.number, merged=True)
            if current["merge_sha"] != args.merge_sha or not SHA.fullmatch(args.merge_sha or ""):
                raise PolicyError("PR merge commit does not match the requested source.")
            if not SHA.fullmatch(args.base or ""):
                raise PolicyError("Expected merge base is required.")
            commit = api.get(f"commits/{args.merge_sha}")
            parents = [parent["sha"] for parent in commit.get("parents", [])]
            if parents != [args.base, current["head"]]:
                raise PolicyError("Merge parents do not match the approved head and base.")
            print(json.dumps(current))
    except (KeyError, PolicyError, GitHubError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
