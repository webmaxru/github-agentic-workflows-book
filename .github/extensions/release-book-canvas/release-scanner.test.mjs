import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { mkdir, mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { promisify } from "node:util";
import { scanRelease } from "./release-scanner.mjs";

const exec = promisify(execFile);

async function fixture() {
    const root = await mkdtemp(join(tmpdir(), "release-canvas-"));
    const put = async (path, contents) => {
        const target = join(root, path);
        await mkdir(join(target, ".."), { recursive: true });
        await writeFile(target, contents, "utf8");
    };
    await put("content/VERSION", "2.4\n");
    await put("content/FRAMEWORK_VERSION", "v9.1.0\n");
    await put("content/chapters/intro.html", "<h1>Intro</h1>\n");
    await put("examples/demo.md", "---\nengine: copilot\n---\n");
    await put("evidence/v9.1.0/verify.json", '{"status":"PASS"}\n');
    await put("review.json", '{"verdict":"ACCEPT"}\n');
    const config = {
        schemaVersion: 1,
        repository: { name: "Fixture book" },
        publication: {
            name: "Fixture",
            promise: "Evidence before release.",
            contentVersionPath: "content/VERSION",
            frameworkVersionPath: "content/FRAMEWORK_VERSION",
            chapterPath: "content/chapters",
            examplePath: "examples",
        },
        sources: [{
            id: "manuscript",
            label: "Manuscript",
            owner: "Author",
            paths: ["content/chapters"],
            evidence: "review.json",
            why: "Reader-facing truth.",
        }],
        demos: [{
            id: "compile",
            label: "Compile",
            owner: "Verifier",
            paths: ["examples"],
            evidence: "evidence/{frameworkVersion}/verify.json",
            cue: "Show the proof.",
        }],
        gates: [
            {
                id: "compile",
                label: "Compile passed",
                kind: "json-field",
                path: "evidence/{frameworkVersion}/verify.json",
                field: "status",
                equals: "PASS",
            },
            {
                id: "review",
                label: "Review passed",
                kind: "json-field",
                path: "review.json",
                field: "verdict",
                equals: "ACCEPT",
            },
        ],
        agents: [],
        rubric: [],
    };
    await put(".book-release-canvas.json", JSON.stringify(config));
    await exec("git", ["init", "-q"], { cwd: root });
    await exec("git", ["config", "user.email", "test@example.com"], { cwd: root });
    await exec("git", ["config", "user.name", "Test"], { cwd: root });
    await exec("git", ["add", "."], { cwd: root });
    await exec("git", ["commit", "-qm", "fixture"], { cwd: root });
    return root;
}

test("clean verified fixture is ready", async () => {
    const root = await fixture();
    const snapshot = await scanRelease(root, join(root, ".book-release-canvas.json"));
    assert.equal(snapshot.decision, "ready");
    assert.equal(snapshot.readiness, 100);
    assert.equal(snapshot.publication.contentVersion, "2.4");
    assert.equal(snapshot.publication.frameworkVersion, "v9.1.0");
    assert.equal(snapshot.publication.chapterCount, 1);
    assert.equal(snapshot.publication.exampleCount, 1);
});

test("changed example queues a demo rebuild and holds release", async () => {
    const root = await fixture();
    await writeFile(join(root, "examples", "demo.md"), "changed\n", "utf8");
    const snapshot = await scanRelease(root, join(root, ".book-release-canvas.json"));
    assert.equal(snapshot.decision, "hold");
    assert.equal(snapshot.demos[0].status, "needs-refresh");
    assert.equal(snapshot.blockers[0].type, "demo");
});

test("human override is reflected without changing repository evidence", async () => {
    const root = await fixture();
    await writeFile(join(root, "examples", "demo.md"), "changed\n", "utf8");
    const snapshot = await scanRelease(root, join(root, ".book-release-canvas.json"), {
        demos: { compile: { status: "ready", note: "Recorded from the demo rehearsal." } },
    });
    assert.equal(snapshot.demos[0].status, "ready");
    assert.equal(snapshot.demos[0].automaticStatus, "needs-refresh");
    assert.equal(snapshot.demos[0].note, "Recorded from the demo rehearsal.");
});
