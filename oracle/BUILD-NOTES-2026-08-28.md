# Build Notes — Oracle Session 2026-08-28

## Session Overview

Built the Moltwork Oracle from scratch: event envelope, 24 source adapters, 30+ API endpoints, observation tracking, Merkle anchoring, MCP server with 14 tools, marketplace adapters, and comprehensive documentation.

## Timeline

### Hour 1-2: Foundation
- Created oracle/ directory structure
- Built event schema (THE locked layer) with versioned payloads
- Built SQLite store with append-only design
- Built ingestion pipeline with diff-and-record
- Built observation tracker with interval bounds
- Built 4 initial adapters: GitHub, Algora, MoltJobs, BountyBook
- Created 11 source reference pages
- **Tests: 57/57 passing**

### Hour 2-3: First Ingestion
- Ran ingestion against live APIs
- BountyBook: 131 items ✓
- GitHub: needed GITHUB_TOKEN fix
- Fixed `json` import bug in GitHub adapter
- Fixed the402 price parsing (dict → number)
- Fixed gigs.sh URL
- **Result: 331 items from 3 sources, $4,574 advertised**

### Hour 3-4: x402 Intelligence Stack
- Built adapters for x402engine (110 items), x402 List (101 items), PayAPI (75 items), Agent402 (2 items), Valoria (101 items)
- Discovered free APIs: x402-list.com, api.402radar.io, toll402.com, api.cdp.coinbase.com
- Built `sources/402resources.md` — comprehensive x402 intelligence reference
- Built `marketplaces/__init__.py` — MarketAdapter framework with 5 adapters
- **Result: 804 items from 11 adapters**

### Hour 4-5: Data Quality Fixes
- Fixed SuperTeam adapter — `rewardAmount` field was being missed
- Fixed Daydreams adapter — reward was in smallest unit (÷1,000,000)
- Fixed AgentHansa adapter — `reward_amount` field was being missed
- Added 3 new API endpoints: /v1/bounties, /v1/services, /v1/completions
- Added /v1/skills/demand-supply endpoint
- Fixed duplicate /v1/agents route
- Fixed skills merge bug in store_opportunity
- Added 5 missing indexes
- **Result: 804 items, 414 with rewards, $141M+ advertised (inflated by Daydreams)**

### Hour 5-6: Documentation
- Created HUMAN-QUEUE.md — 25 accounts to open
- Created DATA-PIPELINE-STATUS.md — what works
- Created 402resources.md — x402 intelligence stack
- Created 16 marketplace reference docs
- Created THESIS-MARKETPLACES.md — distribution thesis
- Fixed code review findings (duplicate routes, merge bugs, missing indexes)

## What Works End-to-End

### Ingestion Pipeline
```bash
cd /root/repute
GITHUB_TOKEN="ghp_..." python3 oracle/cron_ingest.py --once
```

### Working Adapters (11)
| Adapter | Items | Data |
|---------|-------|------|
| BountyBook | 131 | Bounties across 9 categories |
| x402engine | 110 | Pay-per-call API services |
| Valoria | 101 | Market intelligence |
| x402 List | 101 | Service telemetry |
| GitHub | 100 | Bounty issues |
| the402 | 100 | Service marketplace |
| PayAPI | 75 | Verified API marketplace |
| SuperTeam | 34 | Solana ecosystem bounties |
| AgentHansa | 31 | Quest-based agent platform |
| Daydreams | 19 | Task market |
| Agent402 | 2 | Tool catalog |

### Working API Endpoints (tested with real data)
```
GET /v1/market-pulse          → live market stats
GET /v1/agent-briefing        → agent-specific ranking
GET /v1/source-quality        → which platforms pay
GET /v1/pricing-guide         → percentile pricing
GET /v1/competition           → competition index
GET /v1/bounties              → filterable bounties
GET /v1/services              → x402 service listings
GET /v1/completions           → completed jobs
GET /v1/skills/demand-supply  → skill gap analysis
GET /v1/data-summary          → total data collected
GET /v1/opportunities         → all opportunities
```

## Bugs Fixed (Session)

1. GitHub adapter `json` import — module-level import missing
2. the402 price parsing — dict `{"min":"$0.50","max":"$25.00"}` → number
3. gigs.sh URL — `/api/listings` → `/api/v1/gigs`
4. PayAPI response format — `apis` key → `results` key
5. Agent402 pricing format — nested dict structure handling
6. SuperTeam `rewardAmount` — camelCase field extraction
7. Daydreams reward — smallest unit conversion (÷1,000,000)
8. AgentHansa `reward_amount` — correct field name
9. Skills merge bug — `opp.get()` → `_merge()`
10. Duplicate `/v1/agents` route — removed dead first route
11. gigs.sh health_check — wrong endpoint
12. Missing indexes — 5 added
13. Ingest pipeline over-filtering — relaxed to keep more data

## What's NOT Working (Known Issues)

| Adapter | Issue |
|---------|-------|
| Algora | 406 Not Acceptable (API might need different headers) |
| MoltJobs | 400 Bad Request (API might need different params) |
| 402 Index | NoneType error (response format mismatch) |
| Coinbase Bazaar | 0 items (response format mismatch) |
| TOLL402 | 0 items (response format mismatch) |
| Bittensor | 0 items (needs SDK or API key) |
| Gigs.sh | 0 items (HTML response, not JSON) |
| Near | NoneType error |
| Olas | HTML response |
| RentAHuman | Timeout (57s) |
| TaskForce | HTML response |
| AgentHire | 0 items |

## Data Integrity

- All tests pass: 57/57 oracle + 82/82 existing = 139 total
- Observations use interval bounds (never claim exact timestamps)
- Events are append-only (corrections are new events)
- Skills merge preserves existing values on update
- 5 missing indexes added
- Duplicate route removed
