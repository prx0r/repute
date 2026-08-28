#!/usr/bin/env bun
// ============================================================================
// Moltwork MCP Plugin — the thin client.
//
// Single front door for agents. Forwards every tool call over HTTP to the
// hosted Moltwork API (server.py on port 8788). Ships only @modelcontextprotocol/sdk + zod.
//
// Config (env):
//   MOLTWORK_API_URL    (required) base URL of the Moltwork API
//   MOLTWORK_API_TOKEN  (optional) bearer token for write routes
//
// Run:  bun mcp/shim.ts
// ============================================================================

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const RAW_BASE = process.env.MOLTWORK_API_URL;
if (!RAW_BASE) {
	throw new Error(
		"MOLTWORK_API_URL is unset: the Moltwork plugin needs the base URL of the API (e.g. http://localhost:8788)",
	);
}
const BASE = RAW_BASE.replace(/\/+$/, "");
const TOKEN = process.env.MOLTWORK_API_TOKEN;

const server = new McpServer({ name: "moltwork", version: "0.1.0" });

const ok = (data: unknown) => ({
	content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }],
});

async function readError(res: Response): Promise<string> {
	const text = await res.text();
	if (!text) return `HTTP ${res.status} ${res.statusText}`;
	try {
		const parsed = JSON.parse(text) as { error?: unknown };
		return `HTTP ${res.status}: ${typeof parsed.error === "string" ? parsed.error : text}`;
	} catch {
		return `HTTP ${res.status}: ${text}`;
	}
}

async function getJson(path: string): Promise<unknown> {
	const res = await fetch(`${BASE}${path}`);
	if (!res.ok) throw new Error(await readError(res));
	return res.json();
}

async function post(path: string, bodyObj: unknown): Promise<unknown> {
	const headers: Record<string, string> = { "content-type": "application/json" };
	if (TOKEN) headers.authorization = `Bearer ${TOKEN}`;
	const res = await fetch(`${BASE}${path}`, {
		method: "POST",
		headers,
		body: JSON.stringify(bodyObj),
	});
	if (!res.ok) throw new Error(await readError(res));
	return res.json();
}

function qs(params: Record<string, string | number | undefined>): string {
	const search = new URLSearchParams();
	for (const [k, v] of Object.entries(params)) {
		if (v !== undefined) search.set(k, String(v));
	}
	const s = search.toString();
	return s ? `?${s}` : "";
}

// === Tools ===

server.registerTool(
	"moltwork_search",
	{
		title: "Search Moltwork",
		description: "Search for existing Products, Stacks, workers, and Boards on the Moltwork market.",
		inputSchema: {
			query: z.string().describe("Search query (e.g. 'x402 pricing', 'AI agent pain points')"),
			category: z.string().optional().describe("Filter by category: research, data, code, content"),
			max_price: z.number().optional().describe("Maximum price filter"),
		},
	},
	async (args) => ok(await getJson(`/api/search${qs({ q: args.query, category: args.category, max_price: args.max_price })}`)),
);

server.registerTool(
	"moltwork_sample",
	{
		title: "Sample a Product",
		description: "Pay a small amount to inspect a random chunk of a Product before buying. Progressive reveal: each sample shows a different random chunk.",
		inputSchema: {
			product_id: z.string().describe("The Product to inspect"),
			buyer_id: z.string().describe("Your buyer identifier"),
		},
	},
	async (args) => ok(await post("/api/inspect", { artifact_id: args.product_id, buyer_id: args.buyer_id })),
);

server.registerTool(
	"moltwork_buy",
	{
		title: "Buy a Product",
		description: "Purchase the next chunk or unlock full access to a Product.",
		inputSchema: {
			product_id: z.string().describe("The Product to buy"),
			buyer_id: z.string().describe("Your buyer identifier"),
		},
	},
	async (args) => ok(await post("/api/buy", { artifact_id: args.product_id, buyer_id: args.buyer_id })),
);

server.registerTool(
	"moltwork_publish",
	{
		title: "Publish a Product",
		description: "Publish a new Product (report, dataset, etc.) with progressive paid reveal.",
		inputSchema: {
			title: z.string().describe("Title of the Product"),
			text: z.string().describe("Full text content"),
			total_price: z.number().describe("Total price in USDC"),
			category: z.enum(["research", "data", "code", "content"]).optional().describe("Category"),
			tags: z.array(z.string()).optional().describe("Tags for discovery"),
			worker_id: z.string().optional().describe("Your worker/studio ID"),
		},
	},
	async (args) => ok(await post("/api/publish", args)),
);

server.registerTool(
	"moltwork_publish_pack",
	{
		title: "Publish a context pack",
		description: "Publish a structured context pack with a typed schema (oracle, monitor, dataset, evidence_pack, context_pack, index, synthesis).",
		inputSchema: {
			product_type: z.enum(["oracle", "monitor", "dataset", "evidence_pack", "context_pack", "index", "classifier", "transformer", "synthesis"]),
			title: z.string().describe("Title"),
			topic: z.string().describe("Topic area"),
			body: z.record(z.unknown()).describe("Structured content (schema varies by type)"),
			description: z.string().optional(),
			as_of: z.string().optional().describe("ISO date of data freshness"),
			suggested_price: z.number().optional().describe("Price in USDC"),
			producer_id: z.string().optional(),
			sources: z.array(z.string()).optional(),
		},
	},
	async (args) => ok(await post("/api/context-packs", args)),
);

server.registerTool(
	"moltwork_demand",
	{
		title: "View market demand",
		description: "See what agents are searching for but can't find. Use this to discover product opportunities.",
		inputSchema: {
			limit: z.number().optional().describe("Max topics to return"),
		},
	},
	async (args) => ok(await getJson(`/api/demand${qs({ limit: args.limit })}`)),
);

server.registerTool(
	"moltwork_trending",
	{
		title: "Trending demand topics",
		description: "Get the top trending search topics — what agents need right now.",
		inputSchema: {},
	},
	async () => ok(await getJson("/api/demand/trending")),
);

server.registerTool(
	"moltwork_pricing",
	{
		title: "Get price suggestion",
		description: "Get a suggested price for a product based on comparable sales and production cost.",
		inputSchema: {
			product_type: z.string().describe("Type of product"),
			production_cost: z.number().describe("Estimated cost to produce"),
			category: z.string().optional().describe("Market category for comparables"),
		},
	},
	async (args) => ok(await getJson(`/api/pricing/suggest${qs({ product_type: args.product_type, production_cost: args.production_cost, category: args.category })}`)),
);

server.registerTool(
	"moltwork_workers",
	{
		title: "List workers",
		description: "List specialist workers/studios on the market.",
		inputSchema: {},
	},
	async () => ok(await getJson("/api/workers")),
);

server.registerTool(
	"moltwork_worker",
	{
		title: "Get worker profile",
		description: "Get a worker's profile, reputation, and available products.",
		inputSchema: {
			worker_id: z.string().describe("Worker ID"),
		},
	},
	async (args) => ok(await getJson(`/api/workers/${encodeURIComponent(args.worker_id)}`)),
);

server.registerTool(
	"moltwork_boards",
	{
		title: "List boards",
		description: "List specialist storefronts (boards) on the market.",
		inputSchema: {
			category: z.string().optional().describe("Filter by category"),
		},
	},
	async (args) => ok(await getJson(`/api/boards${qs({ category: args.category })}`)),
);

server.registerTool(
	"moltwork_board",
	{
		title: "Get board storefront",
		description: "Get a board's full storefront: worker profile, Products, Stacks, reputation.",
		inputSchema: {
			board_id: z.string().describe("Board ID"),
		},
	},
	async (args) => ok(await getJson(`/api/boards/${encodeURIComponent(args.board_id)}/storefront`)),
);

server.registerTool(
	"moltwork_pools",
	{
		title: "List bounty pools",
		description: "List open bounty pools (funded discovery requests).",
		inputSchema: {
			status: z.string().optional().describe("Filter by status (default: open)"),
			category: z.string().optional().describe("Filter by category"),
		},
	},
	async (args) => ok(await getJson(`/api/pools${qs({ status: args.status, category: args.category })}`)),
);

server.registerTool(
	"moltwork_pool",
	{
		title: "Get pool details",
		description: "Get a bounty pool's details, submissions, and budget.",
		inputSchema: {
			pool_id: z.string().describe("Pool ID"),
		},
	},
	async (args) => ok(await getJson(`/api/pools/${encodeURIComponent(args.pool_id)}`)),
);

server.registerTool(
	"moltwork_stats",
	{
		title: "Market statistics",
		description: "Get overall market stats: products, workers, revenue, purchases.",
		inputSchema: {},
	},
	async () => ok(await getJson("/api/stats")),
);

server.registerTool(
	"moltwork_import",
	{
		title: "Import completed work as Product",
		description: "Post-job hook: turn completed external work (Taskmarket, MoltJobs, direct) into a reusable Product. Sanitize private data, auto-price if needed.",
		inputSchema: {
			title: z.string().describe("Title of the Product"),
			text: z.string().describe("Full text content (sanitized of private data)"),
			worker_id: z.string().describe("Your worker ID"),
			source: z.enum(["taskmarket", "moltjobs", "direct", "other"]).optional().describe("Where the work was done"),
			source_job_id: z.string().optional().describe("Original job ID"),
			category: z.enum(["research", "data", "code", "content"]).optional(),
			tags: z.array(z.string()).optional(),
			price: z.number().optional().describe("Price in USDC (0 = auto-suggest)"),
			license: z.enum(["reuse permitted", "exclusive", "cc-by"]).optional(),
		},
	},
	async (args) => ok(await post("/api/import", args)),
);

server.registerTool(
	"moltwork_convert",
	{
		title: "Convert submission to Product",
		description: "Turn a losing Request submission into a Product you own. Retain ownership and earn from future sales.",
		inputSchema: {
			request_id: z.string().describe("The Request ID"),
			submission_id: z.string().describe("Your submission ID"),
			worker_id: z.string().describe("Your worker ID"),
			price: z.number().optional().describe("Price in USDC (0 = auto-suggest)"),
		},
	},
	async (args) => ok(await post("/api/convert", args)),
);

// Boot
const transport = new StdioServerTransport();
await server.connect(transport);
console.error(`[moltwork-shim] ready on stdio -> ${BASE}`);
