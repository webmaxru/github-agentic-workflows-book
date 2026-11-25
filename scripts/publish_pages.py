#!/usr/bin/env python3
"""Request and verify a legacy Pages build for an exact gh-pages commit."""

import argparse
import os
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
    # The response body is deliberately ignored: its URL is never followed or trusted.
    # Verification polls only this repository's build list, so success requires a
    # `built` build of the exact commit regardless of what the request returned.
    api.request(f"/repos/{api.repo}/pages/builds", "POST")
    # The gh-pages push queues its own build, which the requested one can supersede
    # (leaving it errored), so `latest` may show another build. Wait for any build of
    # the exact commit to succeed; builds of other commits never count.
    newest = None
    last_error = None
    for attempt in range(attempts):
        builds = api.get("pages/builds?per_page=100")
        if not isinstance(builds, list):
            raise PolicyError("Pages returned an unexpected build list.")
        exact = [build for build in builds if isinstance(build, dict) and build.get("commit") == commit]
        for build in exact:
            if build.get("status") == "built":
                return build
        newest = exact[0] if exact else newest
        failed = next((build for build in exact if build.get("status") in {"errored", "failed", "cancelled"}), None)
        if failed is not None:
            error = failed.get("error")
            last_error = (error.get("message") if isinstance(error, dict) else None) or f"build {failed['status']}"
        if attempt + 1 < attempts:
            sleep(10)
    status = (newest or {}).get("status")
    detail = f"last status: {status or 'not seen'}"
    if last_error is not None:
        detail += f"; last error: {last_error}"
    raise PolicyError(f"Pages build did not complete before the timeout ({detail}).")


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
