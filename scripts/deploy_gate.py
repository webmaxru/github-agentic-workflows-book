#!/usr/bin/env python3
"""Production serves only released editions: the gate in front of every Pages deploy.

  gate   decide what may be deployed and print {"mode", "tag", "sha"} as JSON
           without --ref  (push to main): HEAD may deploy only if the book content
                          (CONTENT_PATHSPECS) equals the latest published release
           with --ref     (release or rollback): the ref must be a published release tag
                          (or the commit of one); that exact commit is deployed
  smoke  fetch the live site and require it to serve the deployed edition

The content paths come from approved_book.CONTENT_PATHSPECS, so no workflow repeats them.
Releases are always read from the GitHub API on the default branch's trusted copy of this script.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from urllib.request import Request, urlopen

from approved_book import CONTENT_PATHSPECS, GitHub, GitHubError, PolicyError, SHA, TAG

VERSION_META = re.compile(
    r'<meta\s+name="book-content-version"\s+content="([^"]+)"', re.IGNORECASE)


def run_git(root, *args):
    result = subprocess.run(["git", "--no-pager", "-C", str(root), *args],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.returncode, result.stdout.strip()


def tag_key(tag):
    parts = [int(part) for part in tag.removeprefix("content-v").split(".")]
    return tuple((parts + [0, 0])[:3])


def published_tags(api):
    """Published, non-draft, non-prerelease content tags, lowest version first."""
    found = {}
    for release in api.pages("releases"):
        tag = release.get("tag_name", "")
        if release.get("draft") or release.get("prerelease") or not TAG.fullmatch(tag):
            continue
        found[tag] = tag_key(tag)
    ordered = sorted(found.items(), key=lambda item: item[1])
    if len(ordered) > 1 and ordered[-1][1] == ordered[-2][1]:
        raise PolicyError("Several published tags identify the latest edition.")
    return [tag for tag, _ in ordered]


def tag_commit(root, tag, git=run_git):
    code, sha = git(root, "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}")
    if code or not SHA.fullmatch(sha):
        raise PolicyError(f"The tag {tag} is not available locally; fetch tags (fetch-depth: 0).")
    return sha


def gate(api, root, ref=None, git=run_git, *, require_latest=False):
    published = published_tags(api)
    if not published:
        raise PolicyError("No published content release exists; nothing may be deployed.")
    if ref:
        source = released_ref(published, root, ref, git)
        if require_latest and source["tag"] != published[-1]:
            raise PolicyError(f"{source['tag']} is not the highest published stable edition "
                              f"({published[-1]}); use manual deployment for a rollback.")
        return source
    if require_latest:
        raise PolicyError("Automatic release deployment requires an explicit released ref.")
    latest = published[-1]
    release_sha = tag_commit(root, latest, git)
    code, _ = git(root, "diff", "--quiet", release_sha, "HEAD", "--", *CONTENT_PATHSPECS)
    if code == 1:
        raise PolicyError(f"The book content on main differs from the latest published release "
                          f"{latest}; production serves only released editions.")
    if code:
        raise PolicyError("Could not compare the book content with the latest published release.")
    code, head = git(root, "rev-parse", "HEAD")
    if code or not SHA.fullmatch(head):
        raise PolicyError("Could not resolve HEAD.")
    return {"mode": "main", "tag": latest, "sha": head}


def released_ref(published, root, ref, git=run_git):
    """Resolve a released tag name, or the commit of one, to the exact tag and commit."""
    if TAG.fullmatch(ref):
        tag = ref
    elif SHA.fullmatch(ref):
        matches = [t for t in published if tag_commit(root, t, git) == ref]
        if not matches:
            raise PolicyError(f"{ref} is not the commit of a published release; "
                              "only released editions can be deployed.")
        tag = matches[0]
    else:
        raise PolicyError(f"{ref!r} is not a release tag or commit; branches and other refs "
                          "are never deployed.")
    if tag not in published:
        raise PolicyError(f"{tag} is not a published release (drafts, prereleases and unknown "
                          "tags are refused).")
    sha = tag_commit(root, tag, git)
    code, _ = git(root, "cat-file", "-e", f"{sha}:content/VERSION")
    if code:
        raise PolicyError(f"{tag} predates release metadata and cannot be rebuilt or redeployed.")
    code, _ = git(root, "merge-base", "--is-ancestor", sha, "HEAD")
    if code:
        raise PolicyError(f"{tag} is not on main; refusing to deploy it.")
    return {"mode": "tag", "tag": tag, "sha": sha}


def fetch(url):
    request = Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "book-deploy-smoke"})
    with urlopen(request, timeout=30) as response:
        return response.status, response.read().decode("utf-8", errors="replace")


def smoke(url, version, attempts=30, delay=20, fetch=fetch, sleep=time.sleep):
    """Wait until the live site reports the deployed edition (Pages needs a moment to propagate)."""
    target = f"{url.rstrip('/')}/?smoke={int(time.time())}"
    seen = "no response"
    for attempt in range(attempts):
        try:
            status, body = fetch(target)
            match = VERSION_META.search(body)
            seen = f"HTTP {status}, edition {match[1] if match else 'not found'}"
            if status == 200 and match and match[1] == version:
                return {"url": url, "version": version, "attempts": attempt + 1}
        except OSError as exc:
            seen = str(exc)
        if attempt + 1 < attempts:
            sleep(delay)
    raise PolicyError(f"The live site at {url} does not serve edition {version} ({seen}).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("gate", "smoke"))
    parser.add_argument("--ref", default="")
    parser.add_argument("--require-latest", action="store_true")
    parser.add_argument("--root", default=".")
    parser.add_argument("--url")
    parser.add_argument("--version")
    args = parser.parse_args()
    try:
        if args.action == "gate":
            api = GitHub(os.environ["GITHUB_REPOSITORY"], os.environ["GH_TOKEN"])
            result = gate(api, args.root, args.ref.strip() or None, require_latest=args.require_latest)
        else:
            result = smoke(args.url, args.version)
        print(json.dumps(result))
    except (KeyError, PolicyError, GitHubError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
