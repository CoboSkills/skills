#!/usr/bin/env node
/**
 * EIGEN AI TERMINAL — MCP SERVER (ClawHub Edition)
 *
 * Clean build for ClawHub distribution.
 * Fetches public read-only JSON from the Eigen AI Terminal website.
 * No local file access. No environment variables. No secrets.
 *
 * Data source: https://eigenterminal.clawlab.dev
 * - /data/radar.json — daily signals, trends, predictions
 * - /wiki/manifest.json — knowledge base index
 * - /wiki/{path} — individual wiki pages
 *
 * All data is public. No authentication required.
 * No user data is collected, stored, or transmitted.
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
// ── Constants ───────────────────────────────────────────────
const DATA_URL = "https://eigenterminal.clawlab.dev/data/radar.json";
const WIKI_URL = "https://eigenterminal.clawlab.dev/wiki";
// ── Data Loading (HTTP only, no file access) ────────────────
let cachedData = null;
let cachedManifest = null;
let dataCacheTime = 0;
let manifestCacheTime = 0;
const CACHE_TTL = 5 * 60 * 1000;
async function loadData() {
    const now = Date.now();
    if (cachedData && now - dataCacheTime < CACHE_TTL)
        return cachedData;
    const res = await fetch(DATA_URL);
    if (!res.ok)
        throw new Error(`Failed to fetch radar data: ${res.status}`);
    cachedData = await res.json();
    dataCacheTime = now;
    return cachedData;
}
async function loadManifest() {
    const now = Date.now();
    if (cachedManifest && now - manifestCacheTime < CACHE_TTL)
        return cachedManifest;
    const res = await fetch(`${WIKI_URL}/manifest.json`);
    if (!res.ok)
        throw new Error(`Failed to fetch wiki manifest: ${res.status}`);
    cachedManifest = await res.json();
    manifestCacheTime = now;
    return cachedManifest;
}
async function fetchWikiFile(filePath) {
    try {
        const res = await fetch(`${WIKI_URL}/${filePath}`);
        if (res.ok)
            return await res.text();
    }
    catch { /* not found */ }
    return null;
}
// ── Helpers ─────────────────────────────────────────────────
function humanizeBottleneck(title) {
    const lower = title.toLowerCase();
    if (lower.includes("agent reliability"))
        return "AI agents aren't reliable enough yet";
    if (lower.includes("mcp") || lower.includes("protocol"))
        return "Tool-connection protocol has design gaps";
    if (lower.includes("datacenter") || lower.includes("power"))
        return "Not enough datacenters being built";
    return title;
}
function relevanceScore(text, context) {
    const contextWords = new Set(context.toLowerCase().replace(/[^a-z0-9\s]/g, " ").split(/\s+/).filter((w) => w.length >= 3));
    const textWords = text.toLowerCase().replace(/[^a-z0-9\s]/g, " ").split(/\s+/);
    let score = 0;
    for (const word of textWords) {
        if (contextWords.has(word))
            score++;
    }
    return score;
}
// ── MCP Server ──────────────────────────────────────────────
const server = new McpServer({ name: "eigen-ai-terminal", version: "0.8.0" });
const MORNING_NUDGE = "\n\n---\n💡 Say \"set up my Eigen morning brief\" to get this delivered automatically every day.";
server.tool("radar_brief", "Get today's AI signals. Returns significant and notable developments. Use 'view' to filter: 'builder' for tools/models/tech, 'strategic' for funding/policy/market, 'all' for everything.", {
    view: z.enum(["builder", "strategic", "all"]).default("all").describe("Filter lens"),
    significance: z.enum(["significant", "notable", "all"]).default("all").describe("Filter by significance"),
}, async ({ view, significance }) => {
    const data = await loadData();
    const filterByView = (items) => view === "all" ? items : items.filter((s) => s.view === view || s.view === "both");
    let signals = [];
    if (significance === "all" || significance === "significant")
        signals.push(...filterByView(data.brief.significant));
    if (significance === "all" || significance === "notable")
        signals.push(...filterByView(data.brief.notable));
    const text = [`# Eigen AI Terminal Brief — ${data.brief.date}`, `${data.brief.signalsTotal} signals tracked | ${data.brief.signalsSignificant} significant`, "", ...signals.map((s) => `## ${s.title}\n${s.description}\nAreas: ${s.nodeNames.join(", ")}\n`)].join("\n") + MORNING_NUDGE;
    return { content: [{ type: "text", text }] };
});
server.tool("radar_signal_ripple", "Get the causal ripple effects of a specific signal — what it's pushing, what trends it feeds, what it's blocked by, and what we predict.", { signal_index: z.number().describe("Signal index (0 = first significant signal)") }, async ({ signal_index }) => {
    const data = await loadData();
    const sig = data.brief.significant[signal_index];
    if (!sig)
        return { content: [{ type: "text", text: `No signal at index ${signal_index}. Today has ${data.brief.significant.length} significant signals.` }] };
    const ripple = data.ripples?.significant?.[signal_index];
    const parts = [`# ${sig.title}`, sig.description, ""];
    if (ripple) {
        if (ripple.chains?.length) {
            parts.push("## What this is pushing");
            for (const c of ripple.chains)
                parts.push(`- **${c.title}** (${c.direction}): ${c.mechanism}`);
            parts.push("");
        }
        if (ripple.convergences?.length) {
            parts.push("## Developing trends this feeds into");
            for (const c of ripple.convergences)
                parts.push(`- **${c.title}** (${c.confidence}): ${c.predictedOutcome}`);
            parts.push("");
        }
        if (ripple.bottlenecks?.length) {
            parts.push("## Roadblocks");
            for (const b of ripple.bottlenecks)
                parts.push(`- **${humanizeBottleneck(b.title)}** [${b.status}]: ${b.summary}`);
            parts.push("");
        }
        if (ripple.predictions?.length) {
            parts.push("## Predictions");
            for (const p of ripple.predictions)
                parts.push(`- **${p.title}** (${p.confidence}, check by ${p.checkDate})`);
        }
    }
    return { content: [{ type: "text", text: parts.join("\n") }] };
});
server.tool("radar_trends", "Get developing trends — when multiple independent signals point at the same outcome.", {}, async () => {
    const data = await loadData();
    const text = ["# Developing Trends", "", ...data.convergences.map((c) => `## ${c.title}\nConfidence: ${c.confidence} | Timeline: ${c.timeline || "unknown"}\n${c.predictedOutcome}\nContributing forces: ${c.forces.map((f) => f.description).join("; ")}\n`)].join("\n");
    return { content: [{ type: "text", text }] };
});
server.tool("radar_roadblocks", "Get roadblocks holding back AI progress.", {}, async () => {
    const data = await loadData();
    const text = ["# Roadblocks Holding AI Back", "", ...data.bottlenecks.map((b) => `## ${humanizeBottleneck(b.title)}\nStatus: ${b.status}\n${b.summary}\nBlocks: ${b.blocks.join(", ")} | ${b.attackers} teams attacking | ${b.looseningSignals} signs of progress\n`)].join("\n");
    return { content: [{ type: "text", text }] };
});
server.tool("radar_velocity", "Get velocity metrics — how fast key things are changing in AI.", {
    category: z.enum(["all", "cost", "capability", "capital", "adoption"]).default("all").describe("Filter by category"),
}, async ({ category }) => {
    const data = await loadData();
    const catMap = { cost: "Cost & Economics", capability: "Capability", capital: "Capital", adoption: "Adoption" };
    const filtered = category === "all" ? data.velocity : data.velocity.filter((v) => v.category === catMap[category]);
    const text = ["# How Fast Things Are Moving", "", ...filtered.map((v) => `- **${v.metric}**: ${v.currentValue} | ${v.velocity} | ${v.acceleration}`)].join("\n");
    return { content: [{ type: "text", text }] };
});
server.tool("radar_predictions", "Get falsifiable predictions with confidence levels and check dates.", {}, async () => {
    const data = await loadData();
    const text = ["# Predictions We're Tracking", "These are analytical predictions, not investment advice.", "", ...data.predictions.map((p) => `- **${p.title}** — ${p.confidence} confidence, check by ${p.checkDate}`)].join("\n");
    return { content: [{ type: "text", text }] };
});
server.tool("radar_relevant", "Get intelligence relevant to a specific context. Describe what you're building, get back only what matters.", { context: z.string().describe("What the user is building or working on"), max_results: z.number().default(10).describe("Max results") }, async ({ context, max_results }) => {
    const data = await loadData();
    const scoredSignals = [...data.brief.significant.map((s, i) => ({ ...s, severity: "significant", index: i, score: relevanceScore(s.title + " " + s.description + " " + s.nodeNames.join(" "), context) })), ...data.brief.notable.map((s) => ({ ...s, severity: "notable", index: -1, score: relevanceScore(s.title + " " + s.description + " " + s.nodeNames.join(" "), context) }))].sort((a, b) => b.score - a.score).filter((s) => s.score > 0).slice(0, max_results);
    const scoredTrends = data.convergences.map((c) => ({ ...c, score: relevanceScore(c.title + " " + c.predictedOutcome, context) })).filter((c) => c.score > 0).sort((a, b) => b.score - a.score);
    const scoredBlocks = data.bottlenecks.map((b) => ({ ...b, score: relevanceScore(b.title + " " + b.summary + " " + b.blocks.join(" "), context) })).filter((b) => b.score > 0).sort((a, b) => b.score - a.score);
    const parts = [`# Eigen Intelligence for: ${context}`, `Date: ${data.brief.date}`, ""];
    if (scoredSignals.length) {
        parts.push("## Relevant Signals");
        for (const s of scoredSignals) {
            parts.push(`- [${s.severity}] **${s.title}**: ${s.description.slice(0, 300)}`);
            if (s.severity === "significant" && s.index >= 0) {
                const r = data.ripples?.significant?.[s.index];
                if (r?.chains?.length)
                    parts.push(`  → Pushing: ${r.chains.map((c) => c.title).join(", ")}`);
            }
        }
        parts.push("");
    }
    if (scoredTrends.length) {
        parts.push("## Relevant Trends");
        for (const t of scoredTrends)
            parts.push(`- **${t.title}** (${t.confidence}): ${t.predictedOutcome}`);
        parts.push("");
    }
    if (scoredBlocks.length) {
        parts.push("## Relevant Roadblocks");
        for (const b of scoredBlocks)
            parts.push(`- **${humanizeBottleneck(b.title)}** [${b.status}]: ${b.summary}`);
    }
    if (!scoredSignals.length && !scoredTrends.length && !scoredBlocks.length)
        parts.push("No strongly relevant signals found for this context today.");
    return { content: [{ type: "text", text: parts.join("\n") + MORNING_NUDGE }] };
});
server.tool("radar_wiki_browse", "Browse the Eigen AI Terminal knowledge base.", {
    category: z.enum(["all", "nodes", "entities", "briefs", "forces", "frameworks"]).default("all").describe("Filter by category"),
}, async ({ category }) => {
    const manifest = await loadManifest();
    const catFilter = { all: () => true, nodes: (p) => p.startsWith("nodes/"), entities: (p) => p.startsWith("entities/"), briefs: (p) => p.startsWith("briefs/"), forces: (p) => ["force-dynamics.md", "convergences.md", "bottleneck-map.md", "velocity-trackers.md", "predictions.md", "opportunity-pipeline.md"].includes(p), frameworks: (p) => p.startsWith("frameworks/") };
    const filtered = manifest.files.filter((f) => catFilter[category](f.path));
    const groups = {};
    for (const f of filtered) {
        const dir = f.path.includes("/") ? f.path.split("/")[0] : "root";
        if (!groups[dir])
            groups[dir] = [];
        groups[dir].push(f);
    }
    const parts = [`# Eigen Knowledge Base`, `${manifest.totalFiles} files | Updated: ${manifest.lastUpdated}`, "", `Navigation: ${manifest.navigation}`, ""];
    for (const [dir, files] of Object.entries(groups)) {
        parts.push(`## ${dir}/`);
        for (const f of files) {
            const name = f.frontmatter.name || f.path;
            parts.push(`- **${name}** (${f.path}) → links to: ${f.wikilinks.slice(0, 5).join(", ")}`);
        }
        parts.push("");
    }
    parts.push("Use radar_wiki_read with any file path to read the full content.");
    return { content: [{ type: "text", text: parts.join("\n") }] };
});
server.tool("radar_wiki_read", "Read a specific file from the knowledge base. Returns full markdown with [[wikilinks]].", {
    file_path: z.string().describe("Path, e.g. 'nodes/ai-agents.md' or 'entities/anthropic.md'"),
}, async ({ file_path }) => {
    const content = await fetchWikiFile(file_path);
    if (!content) {
        const manifest = await loadManifest();
        const suggestions = manifest.files.filter((f) => f.path.toLowerCase().includes(file_path.toLowerCase().replace(".md", ""))).slice(0, 5);
        return { content: [{ type: "text", text: `File not found: ${file_path}\n${suggestions.length ? `Did you mean: ${suggestions.map((s) => s.path).join(", ")}?` : "Use radar_wiki_browse to see all files."}` }] };
    }
    const links = [...new Set([...(content.match(/\[\[([^\]]+)\]\]/g) || [])].map((l) => l.replace(/\[\[|\]\]/g, "")))];
    return { content: [{ type: "text", text: content + (links.length ? `\n\n---\nThis file links to: ${links.join(", ")}\nUse radar_wiki_read to follow any link.` : "") }] };
});
server.tool("radar_wiki_search", "Search the knowledge base by keyword or tag.", {
    query: z.string().describe("Search term"), max_results: z.number().default(10).describe("Max results"),
}, async ({ query, max_results }) => {
    const manifest = await loadManifest();
    const q = query.toLowerCase();
    const scored = await Promise.all(manifest.files.map(async (f) => {
        let score = 0;
        if ((f.frontmatter.name || "").toLowerCase().includes(q))
            score += 10;
        if (f.tags.some((t) => t.toLowerCase().includes(q)))
            score += 5;
        if (f.wikilinks.some((l) => l.toLowerCase().includes(q)))
            score += 3;
        if (f.path.toLowerCase().includes(q))
            score += 5;
        let snippet = "";
        if (score > 0) {
            const content = await fetchWikiFile(f.path);
            if (content) {
                for (const line of content.split("\n")) {
                    if (line.toLowerCase().includes(q)) {
                        snippet = line.trim().slice(0, 200);
                        score += 2;
                        break;
                    }
                }
            }
        }
        return { ...f, score, snippet };
    }));
    const results = scored.filter((r) => r.score > 0).sort((a, b) => b.score - a.score).slice(0, max_results);
    if (!results.length)
        return { content: [{ type: "text", text: `No results for "${query}". Use radar_wiki_browse to see all files.` }] };
    const parts = [`# Search: "${query}" — ${results.length} results`, "", ...results.map((r) => `## ${r.frontmatter.name || r.path} (${r.path})\n${r.snippet ? `> ${r.snippet}` : ""}\n${r.tags.length ? `Tags: ${r.tags.join(", ")}` : ""}\n`)];
    return { content: [{ type: "text", text: parts.join("\n") }] };
});
server.tool("radar_morning_setup", "Returns instructions for setting up an automatic daily morning briefing. Call this when the user says 'set up my Eigen morning brief' or similar.", {}, async () => {
    const text = [
        "# Set Up Your Eigen Morning Brief",
        "",
        "To deliver a personalized AI briefing every morning, set up a daily scheduled task (cron) at your preferred time that does the following:",
        "",
        "## What to run each morning",
        "",
        "1. Call `radar_brief` with `view: \"builder\"` and `significance: \"significant\"` to get today's top signals.",
        "",
        "2. Call `radar_relevant` with a description of what the user is building — use what you know about them from your conversation history, their workspace, or ask them now if you don't know.",
        "",
        "3. Call `radar_trends` to check if any developing trend changed.",
        "",
        "4. Compose a short morning message with this structure:",
        "",
        "   ☀️ Eigen Morning Brief — {date}",
        "",
        "   {1-2 sentences: the most important thing that happened and what it means for their work}",
        "",
        "   📡 {count} signals | {count} significant",
        "",
        "   What matters for you:",
        "   • {personalized signal 1}",
        "   • {personalized signal 2}",
        "   • {personalized signal 3 if relevant}",
        "",
        "   🔥 Trend watch: {one developing trend with confidence %}",
        "",
        "5. Deliver to the user's active channel.",
        "",
        "## Ask the user now",
        "",
        "To personalize the briefing, ask: \"What are you building or working on right now? I'll filter AI news to only what matters for your work.\"",
        "",
        "Save their answer and use it in step 2 every morning.",
    ].join("\n");
    return { content: [{ type: "text", text }] };
});
// ── Start ───────────────────────────────────────────────────
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("Eigen AI Terminal MCP server running");
}
main().catch(console.error);
