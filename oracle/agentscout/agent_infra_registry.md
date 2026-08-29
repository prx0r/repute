# Agent Infrastructure Registry & Market Intelligence

*2026-08-18T01:30:00Z · Two adjacent infrastructure products*

---

## Product 1: Agent Architecture Registry

The unit shouldn't be a prompt. It should be a **reproducible agent system**:

```text
architecture/
  manifest.yaml
  AGENTS.md
  agents/
  skills/
  mcps/
  tools/
  workflows/
  evals/
  env.example
  docker-compose.yml
  benchmarks.json
  costs.json
  README.agent.md
```

Example architectures:
- deep-research-v3
- coding-factory
- github-maintainer
- customer-support
- paper-reviewer
- dataset-curator
- security-auditor
- translation-factory
- browser-research-swarm
- cheap-coding-agent

Each gets normalized metadata:

```json
{
  "task": "deep_research",
  "architecture": "planner → parallel researchers → synthesizer → verifier",
  "models": ["replaceable"],
  "required_mcps": ["browser", "github"],
  "min_context": 64000,
  "estimated_cost": 0.42,
  "median_runtime": 310,
  "benchmark_score": 0.87,
  "clone": "...",
  "agent_install": "..."
}
```

**Differentiator: Docker Hub for complete agent architectures, with measured cost/quality rather than just stars.**

---

## Product 2: Agent Adoption Index

A continuously updated estimate assembled from many independent signals.

OpenCode example:
- Site claims 7.5M developers/month
- npm shows 2.26M weekly downloads
- GitHub repository extremely active

Normalize signals:

| Signal | What it approximates |
|---|---|
| npm downloads | installs/upgrades/activity |
| Homebrew installs | installation demand |
| GitHub stars velocity | developer interest |
| forks | experimentation/adoption |
| contributors | ecosystem health |
| issues/day | activity/support burden |
| release downloads | client distribution |
| VS Code extension installs | installed footprint |
| website traffic | interest/user activity |
| search interest | mindshare |
| Reddit/HN mentions | developer mindshare |
| job listings | organizational adoption |
| GitHub PR fingerprints | actual agent usage |
| config files in public repos | installed agent footprint |
| MCP configurations | ecosystem integration |

---

## Agent Census

Continuously estimate adoption across:
- Claude Code, OpenCode, Codex, Cursor, Copilot, Aider, Cline, OpenHands, Devin, Windsurf

Metrics:
- estimated active projects
- new projects/day
- commits/day
- PRs/day
- languages
- industries
- repository sizes
- growth rate
- retention proxy
- switching patterns

Research backing:
- 932,791 agent-authored PRs across 116,211 repos
- 97.2% F1 distinguishing five coding agents
- Multi-method census of 180M repositories

---

## Agent Tech Radar

```json
{
  "coding_agents": {
    "opencode": {
      "adoption_index": 84.2,
      "momentum_30d": 18.7,
      "npm_downloads_7d": 2259958,
      "confidence": 0.82
    }
  },
  "models": {...},
  "mcp_servers": {...},
  "agent_frameworks": {...},
  "skills": {...},
  "architectures": {...}
}
```

---

## Adjacent APIs

| API | Query answered |
|---|---|
| Agent Census API | What agents are actually gaining usage? |
| Framework Momentum API | LangGraph vs PydanticAI vs CrewAI etc. |
| MCP Adoption API | Which MCP servers are actually being adopted? |
| Architecture Registry | What complete agent design should I clone? |
| Architecture Benchmark API | Which architecture wins for task X? |
| Agent Compatibility API | Can X skill/MCP/config run on Y agent? |
| Provider Momentum API | Which inference providers are gaining/losing usage? |
| Model Migration API | What models are developers moving from/to? |
| Deprecation Radar | What infrastructure is disappearing soon? |
| Open-source Health API | Is this dependency/project dying? |
| Agent Stack Census | What combinations are actually used together? |
| Tool Popularity API | Which APIs/MCPs agents call most? |
| Agent Web Traffic API | What portion of docs traffic is machine-driven? |
| Agent Fingerprint API | Which agent probably generated this artifact? |
| Cost Trend API | How fast is intelligence getting cheaper? |
| Capability Price Index | Historical $ cost of OCR/research/coding/etc. |
| Compute Deal Index | Cheapest available compute by workload |
| Free Compute Index | Remaining useful free resources |
| Agentability Index | Which APIs are easiest for agents to consume? |

---

## MCP Intelligence

MCP Registry encourages aggregators. Provides unauthenticated REST API.

Crawl and enrich:
- usage, health, security, latency, context cost
- version velocity, GitHub activity, package downloads
- dependencies, compatibility, actual tool tests

---

## Stack Graph

Discover what technologies are used together:

```text
OpenCode ─────uses────→ OpenRouter
   │
   ├────uses────→ Playwright MCP
   │
   └────uses────→ AGENTS.md

OpenRouter ───routes──→ DeepSeek
```

APIs:
- GET /stack/opencode
- GET /commonly-used-with/opencode
- GET /migration/from/cursor
- GET /stack/trending
- GET /stack?task=research

---

## The Converging Venture

```text
                 AGENT INFRA GRAPH
                        │
       ┌────────────────┼─────────────────┐
       │                │                 │
    RESOURCES       ADOPTION        ARCHITECTURES
       │                │                 │
   models/APIs       usage           cloneable stacks
   providers         momentum        workflows
   MCP/tools         trends          skills
   compute           migrations      benchmarks
       │                │                 │
       └────────────────┼─────────────────┘
                        │
                    ORACLE API
                        │
                    HOTLOADER
                        │
             cheapest valid execution
```

Every little API enriches the same graph.

**Together they form a machine-readable dataset describing: what agent infrastructure exists, what it costs, what actually works, what people actually use, how components fit together, and which combination an agent should select.**

---

*This is the expanded thesis for Agent Infrastructure Registry & Market Intelligence.*
