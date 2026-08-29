# Moltwork Oracle — Complete Architecture & Status

## The Vision

> **Moltwork = DefiLlama/Dune for economic work first, then an execution layer on top of that data, then a market for the reusable production system that emerges from execution.**

## Three-Feed Architecture

```
WORK              SERVICE           SIGNAL
Bounties          Tools/APIs        Market metrics
Tasks             x402 endpoints    Usage data
Jobs              MCP servers       Pricing trends
                  Agent services    Adoption signals
```

## What's Working (18/27 adapters)

### Feed 1: WORK (439 items, $67K)
| Source | Items | Median $ |
|--------|-------|----------|
| bountybook | 130 | $3 |
| rentahuman | 100 | $10 |
| github | 87 | $8 |
| the402 | 100 | service marketplace |
| superteam | 32 | $1,000 |
| agenthansa | 31 | $25 |
| daydreams | 19 | tasks |

### Feed 2: SERVICE (599 items, 1.95B calls)
| Source | Items | Key Data |
|--------|-------|----------|
| x402engine | 110 | 108 pay-per-call APIs |
| x402list | 101 | Service telemetry |
| the402 | 100 | Service marketplace |
| 402index | 100 | Cross-rail catalog |
| valoria | 101 | Market intelligence |
| payapi | 77 | Verified APIs |
| openrouter | 50 | Model pricing |
| apify | 20 | 183M+ runs |
| smithery | 10 | MCP servers |

### Feed 3: SIGNAL (192 signals)
| Source | Items | Key Data |
|--------|-------|----------|
| npm | 7 | Package downloads |
| hf | 20 | Model adoption |
| openrouter | 50 | Model pricing |
| mcp_registry | 1 | Server metadata |
| agenteconomy | 5 | Macro metrics |

### Bittensor (129 subnets)
- 129 subnets with emissions data
- TAO price tracked
- Tracked: Ditto, Ridges, RedTeam, BitSec, etc.

## API Endpoints (all tested)

### Core
```
GET /v1/market-pulse              → 439 opps, $67K, 6 sources
GET /v1/platform-comparison      → which platform pays best
GET /v1/agent-briefing?skills=X  → full agent intelligence
GET /v1/demand/cross-layer       → 521 skills, work+tools combined
GET /v1/supply                   → 599 services by usage
GET /v1/incentives               → 129 Bittensor subnets
GET /v1/opportunities            → all work + service data
GET /v1/timeseries               → daily trends
GET /v1/leaderboards             → top agents
GET /v1/data-summary             → total data collected
```

### Detailed
```
GET /v1/work-demand              → bounties with rewards
GET /v1/tool-demand              → services with usage data
GET /v1/skill-demand             → cross-layer skill analysis
GET /v1/economics                → work + service summary
GET /v1/bounties                 → filterable bounties
GET /v1/services                 → service listings
GET /v1/completions              → completed jobs
```

## MCP Tools (14 tools, 6 categories)
```
Market:    moltwork_market_pulse, moltwork_market_trends, moltwork_market_timeseries
Opps:      moltwork_agent_briefing, moltwork_search_opportunities, moltwork_opportunity_detail
Pricing:   moltwork_pricing_guide, moltwork_reward_distribution
Competition: moltwork_competition_index, moltwork_demand_gaps
Sources:   moltwork_source_quality, moltwork_source_health
Obs:       moltwork_observation_timeline, moltwork_derived_metrics
```

## QDW Integration (for WorkerKit)

- `qdw-forge/models.py` — canonical Asset/Lease/Invocation schemas
- `qdw-forge/leases.py` — resource allocation
- `qdw-forge/invocation.py` — usage tracking
- `qdw-core/` — economic router, costs, learning
- `qdw-sandbox/bounty/` — job/bounty primitives

Reference: `oracle/WORKERKIT-REFERENCE.md`

## What Needs Human Action

| Task | Platform | Unlocks |
|------|----------|---------|
| Create account | Roblox | Asset upload |
| Create account | Gumroad | Product sales |
| Create account | itch.io | Game/asset sales |
| Create account | YouTube | Video analytics |
| Create account | TikTok | Video publishing |
| Create account | NEAR Agent Market | Work marketplace |
| API key | Dune | On-chain verification |
| API key | Upwork | Freelance work |

## Files

```
oracle/
├── THESIS.md                    Vision doc
├── PLAN.md                      Implementation plan
├── ORACLE-HANDOFF-2026-08-28.md Architecture
├── CRYPTO-INTEGRATION.md        Crypto ecosystem integration
├── WORKERKIT-REFERENCE.md       Reference for other agent
├── VISION.md                    Product vision
├── AGENTS.md                    Operating manual
├── HUMAN-QUEUE.md               Accounts to open
├── DATA-PIPELINE-STATUS.md      What works
├── sources/                     30+ reference docs
├── feeds/                       Three-feed architecture
├── adapters/                   28 adapters (18 working)
├── schema.py                   Event envelope
├── store.py                    Storage layer
├── ingest.py                   Normalization pipeline
├── observations.py             Time-series tracking
├── api.py                      30+ REST endpoints
├── opportunity.py              Universal opportunity spec
├── qdw-forge/                  QDW Forge (cloned)
└── qdw/                        QDW Core (cloned)
```
