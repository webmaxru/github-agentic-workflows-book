import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, isAbsolute, join, relative, resolve } from "node:path";
import { CanvasError, createCanvas, joinSession } from "@github/copilot-sdk/extension";
import {
    loadOverrides,
    saveDemoOverride,
    scanRelease,
} from "./release-scanner.mjs";

const extensionDir = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(extensionDir, "..", "..", "..");
const rendererPath = join(extensionDir, "canvas.html");
const configPath = join(repositoryRoot, ".book-release-canvas.json");
const servers = new Map();
const listeners = new Map();
const instanceConfigs = new Map();

const session = await joinSession({
    canvases: [
        createCanvas({
            id: "book-release-canvas",
            displayName: "Book release canvas",
            description: "Track documentation drift, impacted chapters, demo rebuilds, proof, and human release gates.",
            inputSchema: {
                type: "object",
                properties: {
                    configPath: {
                        type: "string",
                        description: "Optional repo-relative canvas configuration path.",
                    },
                },
                additionalProperties: false,
            },
            actions: [
                {
                    name: "refresh_release",
                    description: "Rescan the repository and return current release readiness.",
                    handler: async (ctx) => scan(ctx.instanceId),
                },
                {
                    name: "get_release_snapshot",
                    description: "Return the source, demo, evidence, and release-gate snapshot shown in the canvas.",
                    handler: async (ctx) => scan(ctx.instanceId),
                },
                {
                    name: "set_demo_status",
                    description: "Record a human demo decision without changing committed repository files.",
                    inputSchema: {
                        type: "object",
                        required: ["demoId", "status"],
                        properties: {
                            demoId: { type: "string", minLength: 1 },
                            status: {
                                type: "string",
                                enum: ["ready", "needs-refresh", "blocked"],
                            },
                            note: { type: "string", maxLength: 500 },
                        },
                        additionalProperties: false,
                    },
                    handler: async (ctx) => {
                        await saveDemoOverride(repositoryRoot, ctx.input);
                        const snapshot = await scan(ctx.instanceId);
                        broadcast(snapshot);
                        return snapshot;
                    },
                },
            ],
            open: async (ctx) => {
                const requestedConfig = ctx.input?.configPath
                    ? resolve(repositoryRoot, ctx.input.configPath)
                    : configPath;
                const relativeConfig = relative(repositoryRoot, requestedConfig);
                if (relativeConfig.startsWith("..") || isAbsolute(relativeConfig)) {
                    throw new CanvasError("invalid_config_path", "The canvas configuration must be inside the repository.");
                }
                instanceConfigs.set(ctx.instanceId, requestedConfig);
                let entry = servers.get(ctx.instanceId);
                if (!entry) {
                    entry = await startServer(ctx.instanceId);
                    servers.set(ctx.instanceId, entry);
                }
                return {
                    title: "Release truth",
                    status: "Repository evidence",
                    url: entry.url,
                };
            },
            onClose: async (ctx) => {
                const entry = servers.get(ctx.instanceId);
                listeners.delete(ctx.instanceId);
                instanceConfigs.delete(ctx.instanceId);
                if (entry) {
                    servers.delete(ctx.instanceId);
                    await new Promise((resolveClose) => entry.server.close(resolveClose));
                }
            },
        }),
    ],
});

async function scan(instanceId) {
    try {
        const overrides = await loadOverrides(repositoryRoot);
        return await scanRelease(
            repositoryRoot,
            instanceConfigs.get(instanceId) ?? configPath,
            overrides
        );
    } catch (error) {
        throw new CanvasError("release_scan_failed", error instanceof Error ? error.message : String(error));
    }
}

function broadcast(snapshot) {
    const payload = `event: snapshot\ndata: ${JSON.stringify(snapshot)}\n\n`;
    for (const clients of listeners.values()) {
        for (const response of clients) {
            response.write(payload);
        }
    }
}

async function readJsonBody(request) {
    const chunks = [];
    let length = 0;
    for await (const chunk of request) {
        length += chunk.length;
        if (length > 32_768) {
            throw new Error("Request body is too large.");
        }
        chunks.push(chunk);
    }
    if (chunks.length === 0) {
        return {};
    }
    return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

function sendJson(response, status, body) {
    response.writeHead(status, {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-store",
    });
    response.end(JSON.stringify(body));
}

async function startServer(instanceId) {
    const html = await readFile(rendererPath, "utf8");
    const server = createServer(async (request, response) => {
        const url = new URL(request.url ?? "/", "http://127.0.0.1");
        try {
            if (request.method === "GET" && url.pathname === "/") {
                response.writeHead(200, {
                    "Content-Type": "text/html; charset=utf-8",
                    "Cache-Control": "no-store",
                    "Content-Security-Policy": [
                        "default-src 'self'",
                        "style-src 'self' 'unsafe-inline'",
                        "script-src 'self' 'unsafe-inline'",
                        "connect-src 'self'",
                        "img-src 'self' data:",
                        "font-src 'self' data:",
                    ].join("; "),
                });
                response.end(html);
                return;
            }
            if (request.method === "GET" && url.pathname === "/api/snapshot") {
                sendJson(response, 200, await scan(instanceId));
                return;
            }
            if (request.method === "GET" && url.pathname === "/events") {
                response.writeHead(200, {
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    Connection: "keep-alive",
                });
                const clients = listeners.get(instanceId) ?? new Set();
                clients.add(response);
                listeners.set(instanceId, clients);
                request.on("close", () => clients.delete(response));
                response.write(": connected\n\n");
                return;
            }
            if (request.method === "POST" && url.pathname === "/api/refresh") {
                const snapshot = await scan(instanceId);
                broadcast(snapshot);
                sendJson(response, 200, snapshot);
                return;
            }
            if (request.method === "POST" && url.pathname === "/api/demo-status") {
                const input = await readJsonBody(request);
                if (!input.demoId || !["ready", "needs-refresh", "blocked"].includes(input.status)) {
                    sendJson(response, 400, { error: "demoId and a valid status are required." });
                    return;
                }
                await saveDemoOverride(repositoryRoot, input);
                const snapshot = await scan(instanceId);
                broadcast(snapshot);
                sendJson(response, 200, snapshot);
                return;
            }
            sendJson(response, 404, { error: "Not found." });
        } catch (error) {
            sendJson(response, 500, {
                error: error instanceof Error ? error.message : String(error),
            });
        }
    });
    await new Promise((resolveListen) => server.listen(0, "127.0.0.1", resolveListen));
    const address = server.address();
    const port = typeof address === "object" && address ? address.port : 0;
    return { server, url: `http://127.0.0.1:${port}/` };
}

session.log("Book release canvas is ready.", { level: "info", ephemeral: true });
