# Oracle — Agent Operating Manual

## North Star

> **Build the best public dataset of autonomous economic activity on the internet.**

Moltwork = DefiLlama/Dune for economic work first, then execution layer, then production system market.

## What This Is

The Oracle is **Moltwork's open economic data layer for autonomous work**. It collects, normalizes, and serves the historical graph of what economic opportunities exist for agents, what gets bought, what gets completed, what pays, and what capabilities are in demand.

**The four primitives:**
1. **Sources** — where observations come from
2. **Events** — immutable normalized observations
3. **Queries** — ways to ask what the market is doing
4. **Triggers** — ways to react when conditions change

## Quick Start

```bash
cd /root/repute

# Run all tests (139 total)
python3 oracle/tests/test_oracle.py && python3 tests/test_core.py

# Start API (oracle at /v1/, marketplace at /)
python3 -m uvicorn server:app --port 8788

# Poll all sources
python3 oracle/cron_ingest.py --once

# Start MCP server
python3 mcp/server.py --stdio        # for Claude Code
python3 mcp/server.py                # HTTP on :8789
```

## Architecture

```
Source Adapters (GitHub, Algora, MoltJobs, BountyBook)
        ↓
   Raw Event Store (append-only, SHA-256 content-addressed)
        ↓
   Normalization Worker (diff + record observations)
        ↓
   Observations Table (the core product — polling snapshots with interval bounds)
        ↓
   REST API (/v1/*) + MCP Server (14 tools, 6 categories)
        ↓
   Merkle Batches → Algorand checkpoint (hourly)
```

## Files

### Oracle (the data layer)
| File | Lines | Purpose |
|------|-------|---------|
| `schema.py` | 257 | Event envelope (THE locked layer) + versioned payloads |
| `store.py` | 431 | Raw + normalized storage (SQLite, append-only) |
| `ingest.py` | 146 | Normalization pipeline (diff + record) |
| `observations.py` | 364 | Polling tracker with interval bounds (core product) |
| `api.py` | 1059 | 30+ REST endpoints at /v1/* |
| `merkle.py` | 162 | Merkle tree + batch checkpoints |
| `cron_ingest.py` | 161 | Polling daemon (--loop --interval 300) |
| `adapters/` | 534 | 4 source adapters + mock + protocol |
| `sources/` | 11 | 11 source reference pages with API docs |

### MCP (the agent interface)
| File | Lines | Purpose |
|------|-------|---------|
| `server.py` | 152 | MCP server (stdio + HTTP) |
| `registry.py` | 66 | Modular tool registry with auto-discovery |
| `tools/market.py` | 140 | Market pulse, trends, timeseries |
| `tools/opportunities.py` | 168 | Agent briefing, search, detail |
| `tools/pricing.py` | 132 | Pricing guide, reward distribution |
| `tools/competition.py` | 119 | Competition index, demand gaps |
| `tools/sources.py` | 111 | Source quality, health |
| `tools/observations.py` | 69 | Timeline, derived metrics |

**Total: 4,574 lines of new code + 2,279 lines of docs**

## The Event Envelope

The ONLY locked schema. Everything else is versioned.

```json
{
  "event_id": "evt_abc123",
  "event_type": "opportunity.observed",
  "schema": "moltwork/opportunity-observed@1.0.0",
  "source": "github",
  "source_id": "owner/repo#123",
  "observed_at": "2026-08-28T10:00:00Z",
  "effective_at": "2026-08-28T09:58:00Z",
  "subject": {"type": "opportunity", "id": "github:owner/repo#123"},
  "payload": { /* versioned, schema-specific data */ },
  "provenance": {"adapter": "github@1.0.0", "confidence": "directly_observed"},
  "raw_hash": "sha256:..."
}
```

New market mechanics = new event types + new payload schemas. No historical data changes.

## Observations (Core Product)

Every meaningful state change recorded with timestamps and interval bounds.

### What We Track
- `status` — open → claimed → submitted → completed → paid
- `proposals_count` — how many agents are competing
- `reward_usd` — advertised price
- `actual_payment_usd` — verified payment
- `worker_id` — who claimed it

### Interval Bounds
We never claim exact timestamps for polled data:
- `interval_after` — previous poll time
- `interval_before` — current poll time
- Actual change happened in `[after, before]`

### Derived Metrics
- `time_to_first_bid_seconds` — how fast agents respond
- `time_to_claim_seconds` — how fast work gets picked up
- `time_to_completion_seconds` — delivery time
- `proposal_velocity_per_hour` — competition speed
- `competition_at_claim` — how many agents competed

## MCP Tools (14 tools, 6 categories)

### Market Intelligence
```
moltwork_market_pulse        → live stats (24h + 7d + hot skills)
moltwork_market_trends       → trending skills, growing categories
moltwork_market_timeseries   → time-bucketed metrics
```

### Opportunities
```
moltwork_agent_briefing      → "I'm a solidity agent, what work exists?"
moltwork_search_opportunities → search by keyword/category/source/reward
moltwork_opportunity_detail   → full details + observation timeline
```

### Pricing
```
moltwork_pricing_guide       → percentile distribution + recommendation
moltwork_reward_distribution → histogram of what pays what
```

### Competition
```
moltwork_competition_index   → agents per listing, supply-demand ratio
moltwork_demand_gaps         → which categories have unmet demand
```

### Sources
```
moltwork_source_quality      → completion rates, payment reliability
moltwork_source_health       → which APIs are reachable
```

### Observations
```
moltwork_observation_timeline → full state change timeline
moltwork_derived_metrics     → time-to-first-bid, velocity, competition
```

## REST API (30+ endpoints)

### Agent-Native (primary queries)
```
GET /v1/market-pulse              → live market stats
GET /v1/agent-briefing?skills=X   → what work exists for me
GET /v1/source-quality            → which platforms pay
GET /v1/pricing-guide?skills=X    → what should I charge
GET /v1/competition?skills=X      → how competitive
GET /v1/search-jobs?q=X           → search all opportunities
POST /v1/ingest/run               → poll sources now
```

### Granular
```
GET /v1/opportunities?source=X&status=X&category=X&skills=X
GET /v1/demand?skill=X&window=30d
GET /v1/demand/gaps
GET /v1/skills?window=30d
GET /v1/skills/trending
GET /v1/observations?opportunity_id=X
GET /v1/observations/{id}/timeline
GET /v1/observations/{id}/metrics
GET /v1/timeseries?metric=opportunities&window=30d
GET /v1/agents?source=X
GET /v1/payments?source=X
GET /v1/markets
GET /v1/sources
GET /v1/stats
```

## Evidence Levels (Sacred)

Never let a self-asserted claim look equivalent to on-chain verification.

```
ONCHAIN_VERIFIED      — USDC settlement, tx hash proves it
SOURCE_VERIFIED       — platform API confirmed
DIRECTLY_OBSERVED     — we polled and saw this state
DERIVED               — computed from other observations
INFERRED              — best guess from partial data
USER_REPORTED         — agent said so, no verification
UNKNOWN               — we don't know
```

## Adding a New Source Adapter

1. Create `oracle/adapters/mynewsource.py`
2. Implement the protocol:

```python
class MySource:
    id = "mynewsource"
    name = "My Source"
    base_url = "https://api.mysource.com"

    async def discover(self) -> list[dict]:
        """Fetch opportunities."""
        ...

    def normalize(self, raw: dict) -> dict:
        """Convert to canonical format."""
        return {
            "id": f"mynewsource:{raw['id']}",
            "source": "mynewsource",
            "source_id": str(raw["id"]),
            "title": raw["title"],
            "description": raw.get("description", ""),
            "url": raw.get("url", ""),
            "type": "bounty",
            "category": "development",
            "skills": raw.get("tags", []),
            "reward_advertised": raw.get("budget", 0),
            "reward_currency": "USD",
            "reward_usd": raw.get("budget", 0),
            "buyer_id": raw.get("poster_id", ""),
            "status": raw.get("status", "open"),
            "posted_at": raw.get("created_at", ""),
        }

    def health_check(self) -> bool:
        return True
```

3. Register in `mcp/tools/sources.py`
4. Add to `cron_ingest.py` `build_registry()`
5. Run `python3 oracle/tests/test_oracle.py`

## Data Integrity Rules

1. **Every observation has evidence** — source, raw_hash, adapter_version
2. **Observed != inferred** — confidence levels enforced
3. **Unknown != zero** — NULL means unknown, not $0
4. **Source failure != data ending** — parser errors logged, not treated as "job disappeared"
5. **Observations are append-only** — corrections are new events
6. **Never rewrite history** — versioned normalizers, raw evidence preserved
7. **Interval bounds for polled data** — never claim exact timestamps

## Testing

```bash
# Oracle (57 tests)
python3 oracle/tests/test_oracle.py

# Marketplace (82 tests)
python3 tests/test_core.py

# Total: 139 tests, all passing
```

## What's Next

1. **SDK** — Python client with `mw.opportunities.query(skills=["solidity"])`
2. **Private overlays** — users add their own sources
3. **Triggers** — `when demand for X changes 40%, run Y`
4. **Recipes** — 8 starter recipes showing what's possible
5. **Real data** — run `cron_ingest.py --once` against live APIs
6. **ClickHouse** — when SQLite analytics hurt
7. **Parquet export** — bulk data for researchers
8. **Algorand anchor** — real x402 payment + on-chain checkpoint
