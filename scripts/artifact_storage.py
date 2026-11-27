#!/usr/bin/env python3
"""Narrow, fail-closed cleanup of book previews and consumed publisher staging."""

import argparse
import base64
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from approved_book import GitHub, GitHubError, PolicyError, SHA, TAG
from publish_release import peel
from release_content import ReleaseError, published_asset

PREFIX = "book-preview-v1"
DIGEST = re.compile(r"sha256:[0-9a-f]{64}")


def positive(value):
    if not str(value).isdigit() or int(value) <= 0:
        raise PolicyError("A positive run/artifact ID and attempt are required.")
    return int(value)


def preview_name(repository, ref, run_id, attempt):
    if not ref.startswith(("refs/heads/", "refs/tags/")) or "\n" in ref:
        raise PolicyError("A full branch or tag source ref is required.")
    book = hashlib.sha256(repository.lower().encode()).hexdigest()
    encoded = base64.urlsafe_b64encode(ref.encode()).decode().rstrip("=")
    return f"{PREFIX}-{book}-{encoded}-{positive(run_id)}-{positive(attempt)}"


def preview_ref(name, repository, run_id, attempt):
    prefix = f"{PREFIX}-{hashlib.sha256(repository.lower().encode()).hexdigest()}-"
    suffix = f"-{positive(run_id)}-{positive(attempt)}"
    if not name.startswith(prefix) or not name.endswith(suffix):
        return None
    encoded = name[len(prefix):-len(suffix)]
    try:
        ref = base64.b64decode(encoded + "=" * (-len(encoded) % 4),
                              altchars=b"-_", validate=True).decode()
    except (ValueError, UnicodeError) as exc:
        raise PolicyError("Malformed preview source ref.") from exc
    if preview_name(repository, ref, run_id, attempt) != name:
        raise PolicyError("Noncanonical preview name.")
    return ref


def trusted_run(api, run, workflow):
    return (type(run.get("id")) is int and run["id"] > 0
            and type(run.get("workflow_id")) is int and run["workflow_id"] > 0
            and isinstance(run.get("head_sha"), str) and SHA.fullmatch(run["head_sha"])
            and isinstance(run.get("head_branch"), str) and bool(run["head_branch"])
            and run.get("repository", {}).get("full_name", "").lower() == api.repo.lower()
            and run.get("head_repository", {}).get("full_name", "").lower() == api.repo.lower()
            and run.get("path") == f".github/workflows/{workflow}")


def completed(run):
    return run.get("status") == "completed"


def require_step(api, run_id, attempt, step_name):
    jobs = api.pages(f"actions/runs/{run_id}/attempts/{attempt}/jobs", "jobs")
    matches = [(job, step) for job in jobs for step in job.get("steps", [])
               if step.get("name") == step_name]
    if len(matches) != 1 or any(job.get("conclusion") != "success"
                              or job.get("status") != "completed"
                              or step.get("conclusion") != "success"
                              for job, step in matches):
        raise PolicyError(f"Cannot confirm successful consumer/upload step: {step_name}")


def artifact_matches(artifact, run, name):
    producer = artifact.get("workflow_run") or {}
    return (type(artifact.get("id")) is int and artifact["id"] > 0
            and artifact.get("name") == name and artifact.get("expired") is False
            and type(artifact.get("size_in_bytes")) is int and artifact["size_in_bytes"] > 0
            and producer.get("id") == run["id"]
            and producer.get("head_sha") == run.get("head_sha")
            and producer.get("head_branch") == run.get("head_branch"))


def artifact_time(artifact):
    value = artifact.get("created_at")
    if not isinstance(value, str):
        raise PolicyError("Artifact creation time is missing.")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if result.tzinfo is None:
            raise ValueError("timezone missing")
        return result
    except ValueError as exc:
        raise PolicyError("Artifact creation time is invalid.") from exc


def previews(api, run_id, attempt):
    run_id, attempt = positive(run_id), positive(attempt)
    replacement_run = api.get(f"actions/runs/{run_id}")
    if (replacement_run.get("id") != run_id or not trusted_run(api, replacement_run, "ci.yml")
            or replacement_run.get("event") != "workflow_dispatch"
            or not completed(replacement_run) or replacement_run.get("conclusion") != "success"
            or replacement_run.get("run_attempt") != attempt):
        raise PolicyError("Replacement producer is not a successful completed manual Book CI run.")
    artifacts = api.pages(f"actions/runs/{run_id}/artifacts", "artifacts")
    matches = [(item, preview_ref(item["name"], api.repo, run_id, attempt))
               for item in artifacts if item.get("name", "").startswith(PREFIX + "-")]
    matches = [(item, ref) for item, ref in matches if ref is not None]
    if not matches:
        jobs = api.pages(f"actions/runs/{run_id}/attempts/{attempt}/jobs", "jobs")
        uploads = [step for job in jobs for step in job.get("steps", [])
                   if step.get("name") == "Upload book preview"]
        if uploads and (len(uploads) != 1 or uploads[0].get("conclusion") != "skipped"):
            raise PolicyError("Preview upload was not skipped, but its replacement artifact is missing "
                              "or invalid; retaining all previous previews.")
        return {"deleted": [], "reason": "No preview in this run; ordinary/manual validation only."}
    if len(matches) != 1:
        raise PolicyError("Replacement preview identity is ambiguous.")
    replacement, ref = matches[0]
    if (not artifact_matches(replacement, replacement_run, replacement["name"])
            or replacement_run.get("head_branch") != ref.split("/", 2)[2]):
        raise PolicyError("Replacement artifact does not match its producer.")
    require_step(api, run_id, attempt, "Upload book preview")
    boundary = artifact_time(replacement)
    deleted = []
    # Enumerate before deleting: deletion must not shift pagination.
    for candidate in api.pages("actions/artifacts", "artifacts"):
        name = candidate.get("name", "")
        if not name.startswith(PREFIX + "-"):
            continue
        match = re.fullmatch(r"(.+)-(\d+)-(\d+)", name)
        if not match or candidate.get("id") == replacement["id"]:
            continue
        old_id, old_attempt = map(int, match.groups()[1:])
        if preview_ref(name, api.repo, old_id, old_attempt) != ref:
            continue
        # Older cleanup must never delete a later upload, even if runs finish in reverse order.
        if artifact_time(candidate) >= boundary:
            continue
        old = api.get(f"actions/runs/{old_id}")
        if (not trusted_run(api, old, "ci.yml") or old.get("workflow_id") != replacement_run.get("workflow_id")
                or old.get("event") != "workflow_dispatch" or not completed(old)
                or old.get("head_branch") != replacement_run.get("head_branch")
                or not artifact_matches(candidate, old, name)):
            continue
        # Recheck both identities and producer states immediately before every destructive request.
        current = api.get(f"actions/runs/{run_id}")
        fresh = api.get(f"actions/artifacts/{replacement['id']}")
        if (current != replacement_run or fresh.get("id") != replacement["id"]
                or not artifact_matches(fresh, current, replacement["name"])):
            raise PolicyError("Replacement producer/artifact changed; retaining all remaining previews.")
        old_artifact = api.get(f"actions/artifacts/{positive(candidate['id'])}")
        old_now = api.get(f"actions/runs/{old_id}")
        if (old_now != old or not completed(old_now)
                or old_artifact.get("id") != candidate["id"]
                or not artifact_matches(old_artifact, old_now, name)
                or artifact_time(old_artifact) >= boundary):
            continue
        api.request(f"/repos/{api.repo}/actions/artifacts/{candidate['id']}", "DELETE")
        deleted.append(candidate["id"])
    return {"deleted": deleted, "replacement": replacement["id"], "ref": ref}


def verify(api, tag, sha=None, digest=None, asset_file=None):
    if not TAG.fullmatch(tag or "") or (sha is not None and not SHA.fullmatch(sha)):
        raise PolicyError("An exact content tag and optional source SHA are required.")
    metadata = api.get(f"releases/tags/{tag}")
    asset = published_asset(metadata, tag, f"gh-aw-book-v{tag.removeprefix('content-v')}.pdf")
    remote_digest = asset.get("digest", "")
    if not isinstance(remote_digest, str) or not DIGEST.fullmatch(remote_digest):
        raise PolicyError("Published asset has no valid SHA-256 integrity digest; retain staging.")
    if asset_file:
        path = Path(asset_file)
        digest = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        if path.stat().st_size != asset["size"]:
            raise PolicyError("Published asset size differs from the validated PDF.")
    if digest is not None and (not DIGEST.fullmatch(digest) or remote_digest != digest):
        raise PolicyError("Published asset digest differs from the validated PDF.")
    ref = api.get(f"git/ref/tags/{tag}")
    source = peel(api, ref["object"])
    if not SHA.fullmatch(source):
        raise PolicyError("Published tag has no valid commit identity.")
    if sha is not None and source != sha:
        raise PolicyError("Published tag points at a different source.")
    return {"digest": remote_digest, "sha": source}


def staging(api, run_id, kind, tag, sha=None, digest=None):
    run_id = positive(run_id)
    if run_id != positive(os.environ["GITHUB_RUN_ID"]):
        raise PolicyError("Staging cleanup is confined to the current workflow run.")
    workflow = "release.yml" if kind == "release" else "deploy-pages.yml"
    run = api.get(f"actions/runs/{run_id}")
    # Pages can also be called by release.yml in the same producing run.
    paths = [workflow] if kind == "release" else [workflow, "release.yml"]
    if (run.get("id") != run_id or not any(trusted_run(api, run, path) for path in paths)
            or run.get("head_branch") != "main" or run.get("event") not in {"push", "workflow_dispatch"}):
        raise PolicyError("Staging cleanup requires a trusted main publisher run.")
    attempt = positive(run.get("run_attempt"))
    if kind == "release" and (not sha or not digest):
        raise PolicyError("Release cleanup requires the validated source and publication digest.")
    verify(api, tag, sha, digest)
    require_step(api, run_id, attempt, "Verify published PDF integrity" if kind == "release"
                 else "Smoke test the live site")
    name = f"validated-{kind}"
    artifacts = api.pages(f"actions/runs/{run_id}/artifacts", "artifacts")
    matches = [item for item in artifacts if item.get("name") == name]
    if len(matches) != 1 or not artifact_matches(matches[0], run, name):
        raise PolicyError("Consumed staging artifact identity is missing or ambiguous.")
    item = api.get(f"actions/artifacts/{matches[0]['id']}")
    if item.get("id") != matches[0]["id"] or not artifact_matches(item, run, name):
        raise PolicyError("Staging artifact identity changed.")
    api.request(f"/repos/{api.repo}/actions/artifacts/{item['id']}", "DELETE")
    return {"deleted": [item["id"]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("name", "previews", "verify", "staging"))
    parser.add_argument("--run-id")
    parser.add_argument("--attempt")
    parser.add_argument("--kind", choices=("release", "pages"))
    parser.add_argument("--tag")
    parser.add_argument("--sha")
    parser.add_argument("--digest")
    parser.add_argument("--asset-file")
    args = parser.parse_args()
    try:
        repo = os.environ["GITHUB_REPOSITORY"]
        if args.action == "name":
            print("name=" + preview_name(repo, os.environ["GITHUB_REF"],
                                         os.environ["GITHUB_RUN_ID"], os.environ["GITHUB_RUN_ATTEMPT"]))
            return 0
        api = GitHub(repo, os.environ["GH_TOKEN"])
        if args.action == "previews":
            result = previews(api, args.run_id, args.attempt)
        elif args.action == "verify":
            result = verify(api, args.tag, args.sha, asset_file=args.asset_file)
            print("digest=" + result["digest"])
            return 0
        else:
            if not args.kind:
                raise PolicyError("Staging kind is required.")
            result = staging(api, args.run_id, args.kind, args.tag, args.sha, args.digest)
        print(json.dumps(result))
    except (KeyError, ValueError, OSError, PolicyError, GitHubError, ReleaseError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
