#!/usr/bin/env python3
"""Release publication rules that are too important to live inside YAML.

  latest  decide whether publishing this edition should mark it Latest
  tag     start a new publication only if neither a tag nor a release already exists
"""

import argparse
import json
import os
import sys

from approved_book import GitHub, GitHubError, PolicyError, SHA, TAG

TAGGER = {"name": "github-actions[bot]", "email": "41898282+github-actions[bot]@users.noreply.github.com"}


def _key(tag):
    parts = [int(part) for part in tag.removeprefix("content-v").split(".")]
    return tuple((parts + [0, 0])[:3])


def latest_decision(tag, action, releases):
    """Only a new publication can become Latest. Compare published stable editions numerically."""
    if not TAG.fullmatch(tag or ""):
        raise PolicyError("A content release tag is required.")
    if action == "skip":
        return False
    if action != "create":
        raise PolicyError(f"Unknown publication action: {action}")
    mine = _key(tag)
    newer = False
    for release in releases:
        other = release.get("tag_name", "")
        if other == tag and release.get("prerelease"):
            return False
        if release.get("draft") or release.get("prerelease") or not TAG.fullmatch(other):
            continue
        if _key(other) == mine and other != tag:
            raise PolicyError(f"{other} already identifies this content edition.")
        if _key(other) > mine:
            newer = True
    return not newer


def peel(api, obj):
    """Follow annotated tag objects down to the commit they ultimately name."""
    for _ in range(10):
        if obj.get("type") == "commit":
            return obj["sha"]
        if obj.get("type") != "tag":
            break
        obj = api.get(f"git/tags/{obj['sha']}")["object"]
    raise PolicyError("The tag does not point to a commit.")


def ensure_tag(api, tag, sha):
    if not TAG.fullmatch(tag or "") or not SHA.fullmatch(sha or ""):
        raise PolicyError("An exact content tag and commit SHA are required.")
    existing = api.get(f"git/ref/tags/{tag}", missing=True)
    if existing is not None:
        if peel(api, existing["object"]) != sha:
            raise PolicyError(f"{tag} already exists at a different commit; tags are never moved.")
        raise PolicyError(f"{tag} already exists; refusing to reuse a tag from another run.")
    releases = api.pages("releases")
    if any(release.get("tag_name") == tag for release in releases):
        raise PolicyError(f"A release or draft for {tag} already exists; nothing was changed.")
    if not latest_decision(tag, "create", releases):
        raise PolicyError("Cannot create an older edition after a newer release.")
    created = api.request(f"/repos/{api.repo}/git/tags", "POST", {
        "tag": tag, "message": f"Content release {tag}", "object": sha,
        "type": "commit", "tagger": TAGGER})
    if not SHA.fullmatch(created.get("sha", "")):
        raise PolicyError("GitHub did not return the annotated tag object.")
    api.request(f"/repos/{api.repo}/git/refs", "POST",
                {"ref": f"refs/tags/{tag}", "sha": created["sha"]})
    return {"tag": tag, "sha": sha, "created": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("latest", "tag"))
    parser.add_argument("--tag", required=True)
    parser.add_argument("--plan-action", choices=("create", "skip"), default="create")
    parser.add_argument("--sha")
    args = parser.parse_args()
    try:
        api = GitHub(os.environ["GITHUB_REPOSITORY"], os.environ["GH_TOKEN"])
        if args.action == "latest":
            result = {"latest": latest_decision(args.tag, args.plan_action, api.pages("releases"))}
        else:
            result = ensure_tag(api, args.tag, args.sha)
        print(json.dumps(result))
    except (KeyError, PolicyError, GitHubError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
