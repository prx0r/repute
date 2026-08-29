# Oracle Handover — 2026-08-28

## The Vision (North Star)

> **Moltwork = DefiLlama/Dune for economic work first, then an execution layer on top of that data, then a market for the reusable production system that emerges from execution.**

**Build the best public dataset of autonomous economic activity on the internet.** Everything else derives from that.

## The Flywheel

```
1. OBSERVE    all economic work/demand
2. NORMALIZE  make different markets queryable together
3. ANALYZE    derive demand, competition, pricing, success signals
4. EXECUTE    give an agent a Recipe for exploiting an opportunity
5. RECORD     capture exactly how the work was produced
6. EXTRACT    turn useful pieces into Parts/Recipes/Services
7. SELL/REUSE other agents consume those productive inputs
8. LEARN      observe downstream economic outcomes
```

## What This Is

Moltwork Oracle is the **open economic data layer for autonomous work**. It collects, normalizes, and serves the historical graph of what economic opportunities exist for agents, what gets bought, what gets completed, what pays, and what capabilities are in demand.

## Architecture (4 layers)

```
SOURCE ADAPTERS (24 adapters, 11 working)
        ↓
RAW EVENT STORE (append-only, SHA-256 content-addressed)
        ↓
NORMALIZATION (diff + record observations)
        ↓
REST API (30+ endpoints) + MCP (14 tools)
```

## What's Built

### Core (`oracle/`)
| File | Lines | Purpose |
|------|-------|---------|
| `schema.py` | 257 | Event envelope (THE locked layer) + versioned payloads |
| `store.py` | 636 | Raw + normalized storage (SQLite, append-only) |
| `ingest.py` | 146 | Normalization pipeline |
| `observations.py` | 364 | Polling tracker with interval bounds |
| `cron_ingest.py` | 158 | Polling daemon |
| `http_client.py` | 120 | Rate-limited HTTP client |
| `merkle.py` | 162 | Merkle tree + batch checkpoints |
| `api.py` | 1500 | 30+ REST endpoints |

### Adapters (`oracle/adapters/`)
24 adapters, 11 working with live data:
- BountyBook (131 items), GitHub (100), the402 (100)
- x402engine (110), x402 List (101), PayAPI (75)
- Valoria (101), SuperTeam (34), AgentHansa (31)
- Daydreams (19), Agent402 (2)

### MCP (`mcp/`)
14 tools across 6 categories: market, opportunities, pricing, competition, sources, observations.

### Marketplaces (`oracle/marketplaces/`)
5 adapters: Roblox, Gumroad, itch.io, Adobe Stock, x402 Bazaar.

### Documentation
- `sources/` — 30+ reference docs
- `HUMAN-QUEUE.md` — 25 accounts to open
- `BUILD-NOTES-2026-08-28.md` — session log
- `402resources.md` — x402 intelligence stack
- `AGENTS.md` — operating manual

## How to Use

### Run Ingestion
```bash
cd /root/repute
GITHUB_TOKEN="ghp_..." python3 oracle/cron_ingest.py --once
```

### Start API
```bash
python3 -m uvicorn server:app --port 8788
```

### Run Tests
```bash
python3 oracle/tests/test_oracle.py  # 57/57
python3 tests/test_core.py          # 82/82
```

### Query Data
```bash
# What work exists?
curl http://localhost:8788/v1/bounties?limit=5

# Which platforms pay?
curl http://localhost:8788/v1/source-quality

# What should I charge?
curl http://localhost:8788/v1/pricing-guide?skills=solidity

# Market pulse
curl http://localhost:8788/v1/market-pulse

# Skill gaps
curl http://localhost:8788/v1/skills/demand-supply
```

## What's Next (Priority Order)

1. **Fix broken adapters** — Algora (406), MoltJobs (400), TOLL402, Coinbase Bazaar
2. **Add Bittensor** — install SDK, read chain data
3. **Add more GitHub repos** — search for bounties beyond current 100
4. **Wire observation tracking** — pass interval bounds from cron_ingest
5. **Add completed job data** — track outcomes across sources
6. **Build SDK** — `from moltwork import Moltwork`
7. **Add Parquet export** — bulk data for researchers
8. **Algorand anchor** — Merkle root on-chain
9. **ClickHouse** — when SQLite analytics hurt

## Key Files to Know

| File | Why It Matters |
|------|---------------|
| `oracle/schema.py` | THE locked layer — never change the envelope |
| `oracle/store.py` | All storage — append-only, merge preserves existing values |
| `oracle/observations.py` | Core product — interval bounds, diff_and_record |
| `oracle/api.py` | 30+ endpoints — test after any change |
| `oracle/adapters/__init__.py` | Auto-discovery — new adapters auto-register |
| `oracle/cron_ingest.py` | Ingestion — filters non-opportunity results |

## Gotchas

1. **GitHub needs GITHUB_TOKEN** — set via env var
2. **Daydreams reward is in smallest unit** — divide by 1,000,000
3. **SuperTeam uses camelCase** — `rewardAmount` not `reward_amount`
4. **Adapter normalize() must return opportunity format** — stats/platform returns are filtered
5. **Skills are stored as JSON arrays** — LIKE query works but returns false positives
6. **store_opportunity merge uses `_merge()`** — never use `or` for zero values
7. **init_db() runs at import** — every import creates/modifies the database
