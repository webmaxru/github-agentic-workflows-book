#!/usr/bin/env python3
"""Request and verify a legacy Pages build for an exact gh-pages commit."""

import argparse
import os
import re
import sys
import time
from urllib.parse import urlsplit

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
    url = urlsplit(response.get("url", ""))
    expected_path = f"/repos/{api.repo}/pages/builds/"
    if (url.scheme != "https" or url.netloc != "api.github.com"
            or not re.fullmatch(re.escape(expected_path) + r"\d+", url.path)
            or url.query or url.fragment):
        raise PolicyError("Pages returned an unexpected build URL.")
    suffix = url.path.removeprefix(f"/repos/{api.repo}/")
    for attempt in range(attempts):
        build = api.get(suffix)
        if build.get("status") == "built":
            if build.get("commit") != commit:
                raise PolicyError("Pages built a different commit than the validated site.")
            return build
        if build.get("status") in {"errored", "failed", "cancelled"}:
            raise PolicyError(f"Pages build failed: {(build.get('error') or {}).get('message')}")
        if attempt + 1 < attempts:
            sleep(10)
    raise PolicyError("Pages build did not complete before the timeout.")


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
