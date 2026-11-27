"""A loopback GitHub REST API backed by a real temporary git repository, for the release rehearsal.

It answers exactly what scripts/approved_book.py, publish_release.py, deploy_gate.py and
release_content.py ask, and implements the gh commands release.yml runs. Git questions (compare,
commits, trees, file contents, tags) are answered by the real repository; everything else (pull
request, reviews, checks, releases, workflow dispatches) is in-memory state the tests set up.
Unexpected requests fail loudly instead of being guessed at.
"""

import base64
import itertools
import json
import os
import re
import subprocess
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

IDENTITY = {
    "GIT_AUTHOR_NAME": "GitHub", "GIT_AUTHOR_EMAIL": "noreply@github.com",
    "GIT_COMMITTER_NAME": "GitHub", "GIT_COMMITTER_EMAIL": "noreply@github.com",
}
SHA = r"[0-9a-f]{40}"


class Missing(Exception):
    """Becomes an HTTP 404."""


class Rejected(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


class GhError(Exception):
    """Becomes a failing gh invocation."""


class FakeGitHub:
    def __init__(self, root, repository="webmaxru/github-agentic-workflows-book", workflows=None):
        self.root = Path(root)
        self.repo = repository
        self.workflows = workflows or {}
        self.pr = None
        self.reviews, self.comments, self.timeline = [], [], []
        self.checks = {}
        self.releases = []
        self.latest_tag = None
        self.dispatches = []
        self.requests = []
        self.writes = []
        self.errors = []
        self.lock = threading.RLock()
        self.ids = itertools.count(1)
        self.ticks = itertools.count(1)
        self.test_merges = {}
        self.before_merge = None
        self.server = None

    # ---------------------------------------------------------------- helpers for tests
    def now(self):
        moment = datetime(2026, 7, 9, 10, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=next(self.ticks))
        return moment.strftime("%Y-%m-%dT%H:%M:%SZ")

    def git(self, *args, check=True, stdin=None):
        # Bytes in and out: text mode would turn "\n" into "\r\n" on Windows and corrupt tag objects.
        raw = subprocess.run(
            ["git", "--no-pager", "-C", str(self.root), *args], capture_output=True,
            input=None if stdin is None else stdin.encode("utf-8"), env={**os.environ, **IDENTITY})
        result = subprocess.CompletedProcess(
            raw.args, raw.returncode, raw.stdout.decode("utf-8", "replace"), raw.stderr.decode("utf-8", "replace"))
        if check and result.returncode:
            raise Missing(result.stderr.strip() or f"git {' '.join(args)} failed")
        return result

    def rev(self, ref, missing_ok=False):
        return self.git("rev-parse", "--verify", "--quiet", ref, check=not missing_ok).stdout.strip()

    def open_pr(self, number, head, author, same_repo=True, draft=False, mergeable=True):
        self.pr = {"number": number, "head": head, "author": author, "same_repo": same_repo,
                   "draft": draft, "state": "open", "merged": False, "merge_sha": None,
                   "base": None, "mergeable": mergeable}

    def review(self, login, state, commit_id=None):
        self.reviews.append({"id": next(self.ids), "user": {"login": login}, "state": state,
                             "commit_id": commit_id or self.pr["head"], "submitted_at": self.now()})

    def comment(self, login, body):
        stamp = self.now()
        self.comments.append({"id": next(self.ids), "user": {"login": login}, "body": body,
                              "created_at": stamp, "updated_at": stamp})
        return self.comments[-1]

    def dismiss_reviews(self):
        self.timeline.append({"event": "review_dismissed", "created_at": self.now()})

    def check(self, sha, name="Book release preflight", conclusion="success", slug="github-actions"):
        self.checks.setdefault(sha, []).append({
            "id": next(self.ids), "name": name, "status": "completed", "conclusion": conclusion,
            "app": {"id": 15368, "slug": slug}})

    def publish(self, tag, assets=(), draft=False):
        release = {"id": next(self.ids), "tag_name": tag, "name": tag, "draft": draft,
                   "prerelease": False, "assets": []}
        for name in assets:
            release["assets"].append(self.asset(name, 2048))
        self.releases.append(release)
        if not draft:
            self.latest_tag = tag
        return release

    def asset(self, name, size):
        return {"id": next(self.ids), "name": name, "state": "uploaded", "size": size,
                "content_type": "application/pdf"}

    def start(self):
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def serve(self, method):
                length = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(length) or b"{}") if length else {}
                status, payload = fake.route(method, self.path, body)
                data = b"" if status == 204 else json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                self.serve("GET")

            def do_POST(self):
                self.serve("POST")

            def do_PUT(self):
                self.serve("PUT")

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return f"http://127.0.0.1:{self.server.server_port}"

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()

    # ---------------------------------------------------------------- routing
    def route(self, method, target, body):
        with self.lock:
            url = urlsplit(target)
            query = parse_qs(url.query)
            self.requests.append((method, url.path + (f"?{url.query}" if url.query else "")))
            try:
                if url.path == "/__gh":
                    return 200, self.gh(body)
                prefix = f"/repos/{self.repo}"
                if url.path == prefix:
                    return 200, {"full_name": self.repo}
                if not url.path.startswith(prefix + "/"):
                    raise Missing(url.path)
                return self.handle(method, url.path[len(prefix) + 1:], query, body)
            except Missing as exc:
                return 404, {"message": f"Not Found ({exc})"}
            except Rejected as exc:
                return exc.status, {"message": str(exc)}
            except Exception as exc:  # a fake that cannot answer must never look like success
                self.errors.append(f"{method} {target}: {exc!r}")
                return 500, {"message": repr(exc)}

    @staticmethod
    def paged(items, query):
        return items if int((query.get("page") or ["1"])[0]) == 1 else []

    def handle(self, method, rest, query, body):
        def match(pattern):
            return re.fullmatch(pattern, rest)

        if method == "GET":
            if rest == "pulls":
                open_prs = [self.pull_json()] if self.pr and self.pr["state"] == "open" else []
                return 200, self.paged(open_prs, query)
            if (found := match(r"pulls/(\d+)")):
                return 200, self.pull_json(int(found[1]))
            if (found := match(r"pulls/(\d+)/files")):
                self.pull_json(int(found[1]))
                return 200, self.paged(self.files(), query)
            if (found := match(r"pulls/(\d+)/reviews")):
                self.pull_json(int(found[1]))
                return 200, self.paged(self.reviews, query)
            if (found := match(r"issues/(\d+)/comments")):
                self.pull_json(int(found[1]))
                return 200, self.paged(self.comments, query)
            if (found := match(r"issues/(\d+)/timeline")):
                self.pull_json(int(found[1]))
                return 200, self.paged(self.timeline, query)
            if (found := match(rf"commits/({SHA})/check-runs")):
                return 200, {"check_runs": self.paged(self.checks.get(found[1], []), query)}
            if match(rf"commits/{SHA}/statuses"):
                return 200, []
            if (found := match(rf"commits/(main|{SHA})")):
                return 200, self.commit_json(found[1])
            if rest == "git/ref/heads/main":
                return 200, {"object": {"type": "commit", "sha": self.rev("refs/heads/main")}}
            if (found := match(rf"compare/({SHA})\.\.\.({SHA})")):
                return 200, {"status": self.compare(found[1], found[2])}
            if rest == "contents/content/VERSION":
                text = self.git("show", f"{query['ref'][0]}:content/VERSION").stdout
                return 200, {"encoding": "base64", "content": base64.b64encode(text.encode()).decode()}
            if (found := match(rf"git/commits/({SHA})")):
                return 200, self.commit_json(found[1], tree=True)
            if rest == "releases":
                return 200, self.paged(self.releases, query)
            if (found := match(r"releases/tags/(.+)")):
                # Like the real API, this lookup never returns a draft.
                for release in self.releases:
                    if release["tag_name"] == found[1] and not release["draft"]:
                        return 200, release
                raise Missing(found[1])
            if (found := match(r"git/ref/tags/(.+)")):
                sha = self.rev(f"refs/tags/{found[1]}", missing_ok=True)
                if not sha:
                    raise Missing(found[1])
                return 200, {"object": {"type": self.git("cat-file", "-t", sha).stdout.strip(), "sha": sha}}
            if (found := match(rf"git/tags/({SHA})")):
                text = self.git("cat-file", "-p", found[1]).stdout
                kind, target = re.search(r"^type (\w+)$", text, re.M)[1], re.search(r"^object (\w+)$", text, re.M)[1]
                return 200, {"object": {"type": kind, "sha": target}}
        if method == "PUT" and (found := match(r"pulls/(\d+)/merge")):
            return 200, self.merge(int(found[1]), body)
        if method == "POST":
            if (found := match(r"actions/workflows/([\w.-]+)/dispatches")):
                self.dispatch(found[1], body)
                return 204, {}
            if rest == "git/tags":
                text = (f"object {body['object']}\ntype commit\ntag {body['tag']}\n"
                        f"tagger {body['tagger']['name']} <{body['tagger']['email']}> 1783590000 +0000\n\n"
                        f"{body['message']}\n")
                return 201, {"sha": self.git("hash-object", "-t", "tag", "-w", "--stdin", stdin=text).stdout.strip()}
            if rest == "git/refs":
                if self.rev(body["ref"], missing_ok=True):
                    raise Rejected(422, "Reference already exists")
                self.git("update-ref", body["ref"], body["sha"])
                self.writes.append(f"create {body['ref']}")
                return 201, {"ref": body["ref"], "object": {"sha": body["sha"]}}
        raise AssertionError(f"the fake GitHub has no route for {method} {rest}")

    # ---------------------------------------------------------------- pull request
    def merge_base(self, head):
        base = self.pr["base"] or self.rev("refs/heads/main")
        return self.git("merge-base", base, head).stdout.strip()

    def files(self):
        out = self.git("diff", "--name-status", "--no-renames", self.merge_base(self.pr["head"]),
                       self.pr["head"]).stdout.splitlines()
        names = {"A": "added", "M": "modified", "D": "removed"}
        return [{"filename": line.split("\t", 1)[1], "status": names[line[0]]} for line in out]

    def test_merge(self, base, head):
        key = (base, head)
        if key not in self.test_merges:
            tree = self.git("rev-parse", f"{head}^{{tree}}").stdout.strip()
            self.test_merges[key] = self.git("commit-tree", tree, "-p", base, "-p", head,
                                             "-m", "Merge").stdout.strip()
        return self.test_merges[key]

    def pull_json(self, number=None):
        pr = self.pr
        if not pr or (number is not None and number != pr["number"]):
            raise Missing(f"pull {number}")
        if pr["merged"]:
            base, merge_sha, mergeable = pr["base"], pr["merge_sha"], None
        else:
            base = self.rev("refs/heads/main")
            merge_sha, mergeable = self.test_merge(base, pr["head"]), pr["mergeable"]
        head_repo = self.repo if pr["same_repo"] else "someone/fork"
        return {"number": pr["number"], "state": pr["state"], "draft": pr["draft"], "merged": pr["merged"],
                "mergeable": mergeable, "merge_commit_sha": merge_sha, "changed_files": len(self.files()),
                "user": {"login": pr["author"]}, "head": {"sha": pr["head"], "repo": {"full_name": head_repo}},
                "base": {"ref": "main", "sha": base}}

    def commit_json(self, ref, tree=False):
        sha = self.rev(ref if ref == "main" else f"{ref}^{{commit}}")
        if not sha:
            raise Missing(ref)
        parents = self.git("rev-list", "--parents", "-n", "1", sha).stdout.split()[1:]
        result = {"sha": sha, "parents": [{"sha": parent} for parent in parents]}
        if tree:
            result["tree"] = {"sha": self.git("rev-parse", f"{sha}^{{tree}}").stdout.strip()}
        return result

    def compare(self, a, b):
        if a == b:
            return "identical"
        if self.git("merge-base", "--is-ancestor", a, b, check=False).returncode == 0:
            return "ahead"
        if self.git("merge-base", "--is-ancestor", b, a, check=False).returncode == 0:
            return "behind"
        return "diverged"

    def merge(self, number, body):
        self.pull_json(number)
        pr = self.pr
        if self.before_merge:
            self.before_merge()  # a push that lands between the controller's last check and the merge
        if pr["merged"] or pr["state"] != "open":
            raise Rejected(405, "Pull Request is not mergeable")
        if body.get("sha") != pr["head"]:
            raise Rejected(409, "Head branch was modified. Review and try the merge again.")
        if body.get("merge_method") != "squash":
            raise Rejected(405, "Squash is the only merge method this fake accepts")
        main = self.rev("refs/heads/main")
        if self.compare(main, pr["head"]) not in {"ahead", "identical"}:
            raise Rejected(409, "The fake only squashes a head that contains main")
        tree = self.git("rev-parse", f"{pr['head']}^{{tree}}").stdout.strip()
        merge_sha = self.git("commit-tree", tree, "-p", main, "-m", f"Update the book (#{number})").stdout.strip()
        self.git("update-ref", "refs/heads/main", merge_sha, main)
        pr.update(merged=True, state="closed", merge_sha=merge_sha, base=main)
        self.writes.append(f"squash-merge #{number} at {pr['head']}")
        return {"merged": True, "sha": merge_sha, "message": "Pull Request successfully merged"}

    def dispatch(self, workflow, body):
        declared = self.workflows.get(workflow)
        if declared is None:
            raise Missing(f"workflow {workflow}")
        inputs = body.get("inputs", {})
        if set(inputs) != set(declared):
            raise Rejected(422, f"Inputs {sorted(inputs)} do not match the declared {sorted(declared)}")
        if body.get("ref") != "main":
            raise Rejected(422, "The fake only dispatches from main")
        self.dispatches.append({"workflow": workflow, **body})
        self.writes.append(f"dispatch {workflow}")

    # ---------------------------------------------------------------- gh
    def gh(self, body):
        try:
            stdout = self.run_gh(body["args"], Path(body["cwd"]))
            return {"stdout": stdout, "stderr": "", "code": 0}
        except GhError as exc:
            return {"stdout": exc.args[1] if len(exc.args) > 1 else "", "stderr": f"gh: {exc.args[0]}\n", "code": 1}

    def run_gh(self, args, cwd):
        command, rest = args[0], args[1:]
        if command == "api":
            include = "--include" in rest
            jq = rest[rest.index("--jq") + 1] if "--jq" in rest else None
            endpoint = next(item for index, item in enumerate(rest)
                            if not item.startswith("--") and (index == 0 or rest[index - 1] != "--jq"))
            status, payload = self.route("GET", "/" + endpoint.lstrip("/"), {})
            if jq:
                payload = payload[jq.lstrip(".")]
                text = payload if isinstance(payload, str) else json.dumps(payload)
                return text + "\n"
            text = json.dumps(payload)
            if include:
                text = f"HTTP/2.0 {status} Status\r\nContent-Type: application/json\r\n\r\n{text}"
            if status >= 400:
                raise GhError(f"HTTP {status}", text)
            return text
        if command == "release":
            return self.run_gh_release(rest, cwd)
        raise AssertionError(f"the fake gh does not implement: gh {' '.join(args)}")

    def run_gh_release(self, args, cwd):
        sub, tag = args[0], args[1]
        options, positional = {}, []
        tokens = iter(args[2:])
        for token in tokens:
            if token.startswith("--"):
                key, sep, value = token.partition("=")
                if not sep and key in {"--repo", "--title", "--notes-file"}:
                    value = next(tokens)
                options[key] = value if (sep or key in {"--repo", "--title", "--notes-file"}) else True
            else:
                positional.append(token)
        release = next((item for item in self.releases if item["tag_name"] == tag), None)
        if sub == "create":
            if "--verify-tag" in options and not self.rev(f"refs/tags/{tag}", missing_ok=True):
                raise GhError(f"tag {tag} does not exist in the repository")
            if release:
                raise GhError(f"a release for {tag} already exists")
            if not (cwd / options["--notes-file"]).is_file():
                raise GhError("the notes file does not exist")
            release = {"id": next(self.ids), "tag_name": tag, "name": options.get("--title", tag),
                       "draft": "--draft" in options, "prerelease": False, "assets": []}
            self.releases.append(release)
            self.writes.append(f"release create {tag} draft={release['draft']}")
            self.attach(release, positional, cwd, "--clobber" in options)
            return ""
        if release is None:
            raise GhError(f"release not found: {tag}")
        if sub == "upload":
            self.attach(release, positional, cwd, "--clobber" in options)
            return ""
        if sub == "edit":
            if options.get("--draft") == "false":
                release["draft"] = False
            if options.get("--latest") == "true":
                self.latest_tag = tag
            self.writes.append(f"release edit {tag} draft={release['draft']} latest={options.get('--latest')}")
            return ""
        raise AssertionError(f"the fake gh does not implement: gh release {sub}")

    def attach(self, release, paths, cwd, clobber):
        for entry in paths:
            path = cwd / entry.split("#", 1)[0]
            if not path.is_file():
                raise GhError(f"asset file {path.name} does not exist")
            existing = [item for item in release["assets"] if item["name"] == path.name]
            if existing and not clobber:
                raise GhError(f"asset under the same name already exists: {path.name}")
            if existing:
                self.writes.append(f"CLOBBER {path.name}")
                release["assets"].remove(existing[0])
            release["assets"].append(self.asset(path.name, path.stat().st_size))
            self.writes.append(f"upload {path.name} to {release['tag_name']}")
