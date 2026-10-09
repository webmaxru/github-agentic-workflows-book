import { createHash } from "node:crypto";
import { execFile } from "node:child_process";
import { homedir } from "node:os";
import { basename, dirname, join, normalize, relative, resolve, sep } from "node:path";
import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const STATUS_ORDER = { blocked: 0, "needs-refresh": 1, ready: 2 };

async function readText(path, fallback = "") {
    try {
        return (await readFile(path, "utf8")).trim();
    } catch (error) {
        if (error?.code === "ENOENT") {
            return fallback;
        }
        throw error;
    }
}

async function readJson(path, fallback = null) {
    const text = await readText(path);
    if (!text) {
        return fallback;
    }
    return JSON.parse(text);
}

async function exists(path) {
    try {
        await stat(path);
        return true;
    } catch (error) {
        if (error?.code === "ENOENT") {
            return false;
        }
        throw error;
    }
}

function safeResolve(root, repoPath) {
    const target = resolve(root, repoPath);
    const rootPrefix = normalize(root + sep);
    if (target !== normalize(root) && !normalize(target).startsWith(rootPrefix)) {
        throw new Error(`Configured path escapes the repository: ${repoPath}`);
    }
    return target;
}

function interpolate(value, variables) {
    return String(value).replace(/\{(\w+)\}/g, (_, name) => variables[name] ?? `{${name}}`);
}

function getField(value, field) {
    return field.split(".").reduce((current, key) => current?.[key], value);
}

function normalizeRepoPath(path) {
    return path.replaceAll("\\", "/").replace(/^\.\//, "");
}

function pathMatches(path, configuredPath) {
    const normalized = normalizeRepoPath(path);
    const configured = normalizeRepoPath(configuredPath).replace(/\/\*\*$/, "");
    return normalized === configured || normalized.startsWith(`${configured}/`);
}

async function git(root, args) {
    try {
        const { stdout } = await execFileAsync("git", ["-C", root, ...args], {
            windowsHide: true,
            maxBuffer: 1024 * 1024,
        });
        return stdout.replace(/\r?\n+$/, "");
    } catch {
        return "";
    }
}

async function changedFiles(root) {
    const output = await git(root, ["status", "--short", "--untracked-files=all"]);
    if (!output) {
        return [];
    }
    return output.split(/\r?\n/).map((line) => {
        const status = line.slice(0, 2).trim() || "?";
        const rawPath = line.slice(3).trim();
        const path = rawPath.includes(" -> ") ? rawPath.split(" -> ").at(-1) : rawPath;
        return { status, path: normalizeRepoPath(path) };
    });
}

async function listFiles(root, repoPath, extension) {
    const directory = safeResolve(root, repoPath);
    if (!(await exists(directory))) {
        return [];
    }
    const found = [];
    async function walk(currentDirectory, currentRepoPath) {
        for (const entry of await readdir(currentDirectory, { withFileTypes: true })) {
            const entryRepoPath = normalizeRepoPath(join(currentRepoPath, entry.name));
            const entryPath = join(currentDirectory, entry.name);
            if (entry.isDirectory()) {
                await walk(entryPath, entryRepoPath);
            } else if (entry.isFile() && (!extension || entry.name.endsWith(extension))) {
                found.push(entryRepoPath);
            }
        }
    }
    await walk(directory, repoPath);
    return found.sort();
}

function overrideStorePath(root) {
    const copilotHome = process.env.COPILOT_HOME || join(homedir(), ".copilot");
    const id = createHash("sha256").update(resolve(root)).digest("hex").slice(0, 16);
    return join(copilotHome, "extensions", "release-book-canvas", "artifacts", `${id}.json`);
}

export async function loadOverrides(root) {
    return (await readJson(overrideStorePath(root), { demos: {} })) ?? { demos: {} };
}

export async function saveDemoOverride(root, input) {
    const path = overrideStorePath(root);
    const state = await loadOverrides(root);
    state.demos ??= {};
    state.demos[input.demoId] = {
        status: input.status,
        note: input.note?.trim() || "",
        decidedAt: new Date().toISOString(),
    };
    await mkdir(dirname(path), { recursive: true });
    await writeFile(path, JSON.stringify(state, null, 2) + "\n", "utf8");
}

async function evaluateGate(root, gate, variables) {
    const repoPath = interpolate(gate.path, variables);
    const path = safeResolve(root, repoPath);
    let actual = null;
    let passed = false;
    if (gate.kind === "file-exists") {
        passed = await exists(path);
        actual = passed ? "present" : "missing";
    } else if (gate.kind === "json-field") {
        const data = await readJson(path);
        actual = data ? getField(data, gate.field) : null;
        passed = actual === gate.equals;
    } else if (gate.kind === "text-equals") {
        actual = await readText(path, null);
        passed = actual === interpolate(gate.equals, variables);
    }
    return {
        ...gate,
        path: repoPath,
        passed,
        actual,
        status: passed ? "ready" : "blocked",
    };
}

function freshnessStatus(source, evidencePresent, relevantChanges) {
    if (relevantChanges.length > 0) {
        return "needs-refresh";
    }
    if (!evidencePresent) {
        return "blocked";
    }
    return "ready";
}

export async function scanRelease(root, configPath, overrides = { demos: {} }) {
    const config = await readJson(configPath);
    if (!config || config.schemaVersion !== 1) {
        throw new Error(`Expected schemaVersion 1 in ${relative(root, configPath)}.`);
    }

    const contentVersion = await readText(safeResolve(root, config.publication.contentVersionPath), "unknown");
    const frameworkVersion = await readText(safeResolve(root, config.publication.frameworkVersionPath), "unknown");
    const variables = { contentVersion, frameworkVersion };
    const changes = await changedFiles(root);
    const head = await git(root, ["rev-parse", "--short", "HEAD"]);
    const branch = await git(root, ["branch", "--show-current"]);
    const commitDate = await git(root, ["log", "-1", "--format=%cI"]);
    const chapters = await listFiles(root, config.publication.chapterPath, ".html");
    const examples = await listFiles(root, config.publication.examplePath, ".md");

    const sources = [];
    for (const source of config.sources) {
        const paths = source.paths.map((path) => interpolate(path, variables));
        const ignoredPaths = (source.ignorePaths ?? []).map((path) => interpolate(path, variables));
        const relevantChanges = changes.filter((change) =>
            paths.some((path) => pathMatches(change.path, path))
            && !ignoredPaths.some((path) => pathMatches(change.path, path))
        );
        const evidence = source.evidence
            ? interpolate(source.evidence, variables)
            : paths[0];
        const evidencePresent = await exists(safeResolve(root, evidence));
        sources.push({
            ...source,
            paths,
            ignoredPaths,
            evidence,
            evidencePresent,
            changedFiles: relevantChanges,
            status: freshnessStatus(source, evidencePresent, relevantChanges),
        });
    }

    const gates = await Promise.all(
        config.gates.map((gate) => evaluateGate(root, gate, variables))
    );
    const demos = [];
    for (const demo of config.demos) {
        const paths = demo.paths.map((path) => interpolate(path, variables));
        const evidence = demo.evidence
            ? interpolate(demo.evidence, variables)
            : null;
        const relevantChanges = changes.filter((change) =>
            paths.some((path) => pathMatches(change.path, path))
        );
        const evidencePresent = evidence
            ? await exists(safeResolve(root, evidence))
            : (await Promise.all(paths.map((path) => exists(safeResolve(root, path))))).some(Boolean);
        const automaticStatus = relevantChanges.length > 0
            ? "needs-refresh"
            : evidencePresent
                ? "ready"
                : "blocked";
        const decision = overrides.demos?.[demo.id];
        demos.push({
            ...demo,
            paths,
            evidence,
            changedFiles: relevantChanges,
            automaticStatus,
            status: decision?.status ?? automaticStatus,
            note: decision?.note ?? "",
            decidedAt: decision?.decidedAt ?? null,
        });
    }

    const impactedChapters = chapters
        .filter((chapter) => changes.some((change) => pathMatches(change.path, chapter)))
        .map((path) => ({ path, title: basename(path, ".html").replaceAll("-", " ") }));
    const gateScore = gates.length
        ? gates.filter((gate) => gate.passed).length / gates.length
        : 1;
    const sourceScore = sources.length
        ? sources.reduce((sum, source) => sum + STATUS_ORDER[source.status], 0) / (sources.length * 2)
        : 1;
    const demoScore = demos.length
        ? demos.reduce((sum, demo) => sum + STATUS_ORDER[demo.status], 0) / (demos.length * 2)
        : 1;
    const readiness = Math.round((gateScore * 0.55 + sourceScore * 0.25 + demoScore * 0.2) * 100);
    const blockers = [
        ...gates.filter((gate) => !gate.passed).map((gate) => ({
            type: "proof",
            title: gate.label,
            detail: `${gate.path}: expected ${String(gate.equals ?? "present")}, found ${String(gate.actual)}`,
        })),
        ...sources.filter((source) => source.status !== "ready").map((source) => ({
            type: "source",
            title: source.label,
            detail: source.changedFiles.length
                ? `${source.changedFiles.length} changed file(s) require impact review.`
                : `Evidence is missing: ${source.evidence}`,
        })),
        ...demos.filter((demo) => demo.status !== "ready").map((demo) => ({
            type: "demo",
            title: demo.label,
            detail: demo.note || (demo.status === "blocked"
                ? "Required evidence is missing."
                : demo.changedFiles.length
                    ? `${demo.changedFiles.length} dependency change(s) require a rebuild.`
                    : "A human decision marked this demo for rebuild."),
        })),
    ];

    return {
        schemaVersion: 1,
        generatedAt: new Date().toISOString(),
        repository: {
            name: config.repository.name || basename(root),
            branch,
            head,
            commitDate,
            dirtyFiles: changes.length,
        },
        publication: {
            ...config.publication,
            contentVersion,
            frameworkVersion,
            chapterCount: chapters.length,
            exampleCount: examples.length,
        },
        readiness,
        decision: blockers.length === 0 ? "ready" : "hold",
        sources,
        demos,
        gates,
        blockers,
        impactedChapters,
        changes,
        agents: config.agents,
        rubric: config.rubric,
    };
}
