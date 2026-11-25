#!/usr/bin/env python3
"""Request and verify a legacy Pages build for an exact gh-pages commit."""

import argparse
import os
import re
import sys
import time

from approved_book import GitHub, GitHubError, PolicyError, SHA


def check_source(api):
    pages = api.get("pages")
    if pages.get("build_type") != "legacy" or pages.get("source") != {"branch": "gh-pages", "path": "/"}:
        raise PolicyError("Pages must use the legacy gh-pages root source.")


def request_build(api, commit, *, sleep=time.sleep, attempts=60):
    if not SHA.fullmatch(commit):
        raise PolicyError("An exact gh-pages commit SHA is required.")
    check_source(api)
    response = api.request(f"/repos/{api.repo}/pages/builds", "POST")
    url = response.get("url")
    builds_url = re.escape(f"https://api.github.com/repos/{api.repo}/pages/builds/")
    if not isinstance(url, str) or not re.fullmatch(builds_url + r"(?:latest|[0-9]+)", url):
        raise PolicyError("Pages returned an unexpected build URL.")
    # The gh-pages push queues its own build, which the requested one can supersede
    # (leaving it errored), so `latest` may show another build. Wait for any build of
    # the exact commit to succeed; builds of other commits never count.
    newest = None
    for attempt in range(attempts):
        builds = api.get("pages/builds?per_page=100")
        if not isinstance(builds, list):
            raise PolicyError("Pages returned an unexpected build list.")
        exact = [build for build in builds if isinstance(build, dict) and build.get("commit") == commit]
        for build in exact:
            if build.get("status") == "built":
                return build
        newest = exact[0] if exact else newest
        if attempt + 1 < attempts:
            sleep(10)
    status = (newest or {}).get("status")
    if status in {"errored", "failed", "cancelled"}:
        raise PolicyError(f"Pages build failed: {(newest.get('error') or {}).get('message')}")
    raise PolicyError(f"Pages build did not complete before the timeout (last status: {status or 'not seen'}).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("check", "build"))
    parser.add_argument("--commit")
    args = parser.parse_args()
    try:
        api = GitHub(os.environ["GITHUB_REPOSITORY"], os.environ["GH_TOKEN"])
        if args.action == "check":
            check_source(api)
            print("Legacy Pages source verified.")
        else:
            build = request_build(api, args.commit or "")
            print(f"Pages built commit {build['commit']}.")
    except (KeyError, PolicyError, GitHubError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
