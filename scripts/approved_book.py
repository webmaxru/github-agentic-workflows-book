#!/usr/bin/env python3
"""Verify exact-head approval and content-only scope, merge, dispatch, and verify provenance.

Subcommands (all read the GitHub API; only ``merge`` and ``dispatch`` write):
  select          pick the first eligible open PR (or the one given by --number)
  merge           squash-merge the approved head, conditional on its exact SHA
  dispatch        start release.yml for a merged PR (merges by GITHUB_TOKEN start no workflows)
  verify-merged   prove a merge commit is the approved head and derive the release inputs
"""

import argparse
import base64
import json
import os
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

OWNER = "webmaxru"
SHA = re.compile(r"[0-9a-f]{40}\Z")
COMMAND = re.compile(r"/release-book ([0-9a-f]{40})\Z")
EDITION = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)(?:\.(0|[1-9]\d*))?\Z")
TAG = re.compile(r"content-v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*))?\Z")
RELEASE_WORKFLOW = "release.yml"
# The one definition of "book content" for release gating. Every workflow asks a script
# instead of repeating these paths.
CONTENT_PATHSPECS = ("content", "examples")
OWNER_FILES = {"content/VERSION", "content/FRAMEWORK_VERSION", "content/CHANGELOG.md",
               "content/release-review.json", "content/toc.yml", "content/outline.md",
               "content/playbook-brief.md"}
OWNER_PREFIXES = ("content/chapters/", "content/research/", "examples/")
SITE_FILES = {"site/index.html", "site/book.html", "site/versions.html", "site/404.html",
              "site/llms.txt", "site/llms-full.txt", "site/sitemap.xml",
              "site/robots.txt", "site/site.webmanifest"}


class PolicyError(ValueError):
    pass


class GitHubError(RuntimeError):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


def allowed_path(path):
    if path in OWNER_FILES:
        return True
    if path.startswith(OWNER_PREFIXES):
        return True
    if path in SITE_FILES:
        return True
    return bool(re.fullmatch(r"site/chapters/[^/]+\.html", path))


def _login(item):
    return ((item or {}).get("user") or {}).get("login", "").lower()


def barrier(reviews, timeline):
    """Latest moment a review asked for changes or any review was dismissed (empty if never)."""
    moments = [r.get("submitted_at") or "" for r in reviews
               if r.get("state") in {"CHANGES_REQUESTED", "DISMISSED"}]
    moments += [e.get("created_at") or "" for e in timeline if e.get("event") == "review_dismissed"]
    return max(moments, default="")


def approved(pr, reviews, comments, timeline=()):
    head = pr["head"]["sha"]
    if _login(pr) == OWNER:
        commands = [c for c in comments
                    if _login(c) == OWNER and c.get("body", "").strip().startswith("/release-book")]
        if not commands:
            return False
        latest = max(commands, key=lambda c: (c.get("created_at") or "", c["id"]))
        match = COMMAND.fullmatch(latest["body"].strip())
        # An edited command is never trusted: the owner must post a fresh one for this head.
        edited = (latest.get("updated_at") or latest.get("created_at")) != latest.get("created_at")
        newer = (latest.get("created_at") or "") > barrier(reviews, timeline)
        return bool(match) and match[1] == head and not edited and newer
    own = [r for r in reviews if _login(r) == OWNER]
    if not own:
        return False
    # Any later owner review, even a plain comment, replaces the approval.
    latest = max(own, key=lambda r: (r.get("submitted_at") or "", r.get("id", 0)))
    return (latest.get("state") == "APPROVED" and latest.get("commit_id") == head
            and (latest.get("submitted_at") or "") > barrier(reviews, timeline))


def eligibility(pr, files, reviews, comments, repository, merged=False, timeline=()):
    head = pr.get("head", {}).get("sha", "")
    base = pr.get("base", {})
    expected_state = "closed" if merged else "open"
    head_repo = pr.get("head", {}).get("repo") or {}
    if (pr.get("state") != expected_state or pr.get("draft") or base.get("ref") != "main"
            or head_repo.get("full_name", "").lower() != repository.lower()
            or not SHA.fullmatch(head) or (merged and not pr.get("merged"))):
        raise PolicyError("PR must be a non-draft same-repository content PR targeting main.")
    if not merged and pr.get("mergeable") is not True:
        raise PolicyError("PR is not mergeable (conflicts, or GitHub has not computed mergeability yet).")
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
    if not approved(pr, reviews, comments, timeline):
        raise PolicyError("Owner approval for the current head is missing or was revoked.")
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
    def __init__(self, repository, token, api_url=None):
        self.repo = repository
        self.token = token
        # The runner sets GITHUB_API_URL; it is how the end-to-end rehearsal reaches a loopback API.
        self.api_url = (api_url or os.environ.get("GITHUB_API_URL") or "https://api.github.com").rstrip("/")

    def request(self, path, method="GET", data=None, missing=False):
        body = json.dumps(data).encode() if data is not None else None
        request = Request(self.api_url + path, data=body, method=method, headers={
            "Authorization": "Bearer " + self.token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        })
        try:
            with urlopen(request, timeout=30) as response:
                payload = response.read()
        except HTTPError as exc:
            if missing and exc.code == 404:
                return None
            raise GitHubError(f"GitHub API {method} {path} failed: {exc}", exc.code) from exc
        except URLError as exc:
            raise GitHubError(f"GitHub API {method} {path} failed: {exc}") from exc
        try:
            return json.loads(payload) if payload.strip() else {}
        except ValueError as exc:
            raise GitHubError(f"GitHub API {method} {path} returned invalid JSON.") from exc

    def get(self, suffix, missing=False):
        path = f"/repos/{self.repo}/{suffix}"
        return self.request(path, missing=True) if missing else self.request(path)

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

    def pull(self, number, merged=False):
        pr = self.get(f"pulls/{number}")
        # GitHub computes mergeability lazily; null means "ask again shortly".
        for _ in range(3):
            if merged or pr.get("state") != "open" or pr.get("mergeable") is not None:
                break
            time.sleep(2)
            pr = self.get(f"pulls/{number}")
        return pr

    def inspect(self, number, merged=False):
        pr = self.pull(number, merged)
        result = eligibility(pr, self.pages(f"pulls/{number}/files"),
                             self.pages(f"pulls/{number}/reviews"),
                             self.pages(f"issues/{number}/comments"), self.repo, merged,
                             self.pages(f"issues/{number}/timeline"))
        checks_pass(self.pages(f"commits/{result['head']}/check-runs", "check_runs"),
                    self.pages(f"commits/{result['head']}/statuses"))
        if not merged:
            self.require_current_main(result["base"], result["head"])
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

    def require_current_main(self, base, head):
        """The head must already contain the current tip of main (never merge a stale head)."""
        main = self.get("git/ref/heads/main")["object"]["sha"]
        if main != base:
            raise PolicyError("main moved since the pull request was last evaluated; "
                              "update the branch and approve again.")
        status = self.get(f"compare/{main}...{head}?per_page=1").get("status")
        if status not in {"ahead", "identical"}:
            raise PolicyError("The head does not contain the current main; "
                              "update the branch and approve again.")

    def edition_at(self, ref):
        blob = self.get(f"contents/content/VERSION?ref={ref}")
        if blob.get("encoding") != "base64":
            raise PolicyError("Unable to read the proposed content edition.")
        try:
            version = base64.b64decode(blob["content"], validate=False).decode("utf-8").strip()
        except (ValueError, UnicodeError) as exc:
            raise PolicyError("Invalid content edition response.") from exc
        if not EDITION.fullmatch(version):
            raise PolicyError("Invalid content edition.")
        return version

    def provenance(self, merge_sha, head):
        """Prove ``merge_sha`` is a squash of exactly ``head`` and return the base it sits on."""
        commit = self.get(f"git/commits/{merge_sha}")
        source = self.get(f"git/commits/{head}")
        parents = [parent["sha"] for parent in commit.get("parents", [])]
        if len(parents) != 1 or commit["tree"]["sha"] != source["tree"]["sha"]:
            raise PolicyError("The merge is not a squash of exactly the approved head.")
        return parents[0]

    def previous_edition(self, head, merged=False):
        version = self.edition_at(head)
        pattern = EDITION
        match = pattern.fullmatch(version)
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


def select(api, number=None):
    """Return the first eligible PR (empty dict if none). With ``number`` a merged PR is a recovery."""
    numbers = [number] if number else [pr["number"] for pr in api.pages("pulls?state=open&base=main")]
    for candidate in numbers:
        try:
            if number and api.get(f"pulls/{candidate}").get("merged"):
                selected = api.inspect(candidate, merged=True)
                selected["base"] = api.provenance(selected["merge_sha"], selected["head"])
            else:
                selected = api.inspect(candidate)
            selected["comparison"] = api.previous_edition(selected["head"], bool(selected.get("merge_sha")))
            selected["tag"] = f"content-v{api.edition_at(selected['head'])}"
            return selected
        except PolicyError as exc:
            if number:
                raise
            print(f"PR #{candidate}: {exc}", file=sys.stderr)
    return {}


def merge(api, number, head, base, comparison):
    """Squash-merge ``head`` only if it is still the approved, current, eligible head."""
    if not number or not SHA.fullmatch(head or "") or not SHA.fullmatch(base or "") or not comparison:
        raise PolicyError("Merge requires PR number, exact head, base and edition baseline.")
    current = api.inspect(number)
    if current["head"] != head or current["base"] != base:
        raise PolicyError("PR head or base changed after preflight.")
    if api.previous_edition(current["head"]) != comparison:
        raise PolicyError("Published edition baseline changed after preflight.")
    # GitHub rejects the merge unless the head is still exactly this SHA.
    response = api.request(f"/repos/{api.repo}/pulls/{number}/merge", "PUT",
                           {"sha": head, "merge_method": "squash"})
    if response.get("merged") is not True or not SHA.fullmatch(response.get("sha", "")):
        raise PolicyError("GitHub did not confirm the merge.")
    if api.provenance(response["sha"], head) != base:
        raise PolicyError("Merge base changed concurrently; refusing publication.")
    return {**current, "merge_sha": response["sha"], "comparison": comparison,
            "tag": f"content-v{api.edition_at(head)}"}


def dispatch(api, number, head, base, merge_sha, tag):
    """Start release.yml on main. A merge made with GITHUB_TOKEN triggers no workflows."""
    if not number or not all(SHA.fullmatch(value or "") for value in (head, base, merge_sha)):
        raise PolicyError("Dispatch requires the PR number and exact head, base and merge SHAs.")
    if not TAG.fullmatch(tag or ""):
        raise PolicyError("Dispatch requires a content release tag.")
    api.request(f"/repos/{api.repo}/actions/workflows/{RELEASE_WORKFLOW}/dispatches", "POST", {
        "ref": "main",
        "inputs": {"pr": str(number), "head_sha": head, "base_sha": base,
                   "merge_sha": merge_sha, "tag": tag}})
    return {"dispatched": RELEASE_WORKFLOW, "pr": number, "tag": tag}


def verify_merged(api, number, head, base, merge_sha, tag):
    """Prove the merge commit is the approved head and return the derived release inputs."""
    if not number or not all(SHA.fullmatch(value or "") for value in (head, base, merge_sha)):
        raise PolicyError("Verification requires the PR number and exact head, base and merge SHAs.")
    current = api.inspect(number, merged=True)
    if current["head"] != head:
        raise PolicyError("The approved head is not the head of this pull request.")
    if current["merge_sha"] != merge_sha:
        raise PolicyError("PR merge commit does not match the requested source.")
    if api.provenance(merge_sha, head) != base:
        raise PolicyError("The merge base does not match the preflight base.")
    expected = f"content-v{api.edition_at(head)}"
    if tag != expected:
        raise PolicyError(f"The tag {tag} does not match the approved edition ({expected}).")
    return {**current, "base": base, "tag": expected,
            "comparison": api.previous_edition(head, merged=True)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("select", "merge", "dispatch", "verify-merged"))
    parser.add_argument("--number", type=int)
    parser.add_argument("--head")
    parser.add_argument("--base")
    parser.add_argument("--comparison")
    parser.add_argument("--merge-sha")
    parser.add_argument("--tag")
    args = parser.parse_args()
    try:
        api = GitHub(os.environ["GITHUB_REPOSITORY"], os.environ["GH_TOKEN"])
        if args.action == "select":
            result = select(api, args.number)
        elif args.action == "merge":
            result = merge(api, args.number, args.head, args.base, args.comparison)
        elif args.action == "dispatch":
            result = dispatch(api, args.number, args.head, args.base, args.merge_sha, args.tag)
        else:
            result = verify_merged(api, args.number, args.head, args.base, args.merge_sha, args.tag)
        print(json.dumps(result))
    except (KeyError, PolicyError, GitHubError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
