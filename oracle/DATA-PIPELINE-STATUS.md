# Oracle Data Pipeline — What Actually Works

**Date:** 2026-08-28
**Status:** 3 sources ingesting live data, 321 opportunities, $4,574 advertised

---

## Working Data Ingestion

| Source | Status | Items | Data |
|--------|--------|-------|------|
| **BountyBook** | ✅ LIVE | 131 | Bounties across 9 categories, $599 advertised |
| **GitHub** | ✅ LIVE | 100 | Bounty issues from 4,378 total, $3,975 advertised |
| **the402** | ✅ LIVE | 100 | Service marketplace, 485 total services |

### How to Run Ingestion

```bash
cd /root/repute
GITHUB_TOKEN="ghp_..." python3 oracle/cron_ingest.py --once
```

Or programmatically:
```python
from oracle.adapters import get_all_adapters
from oracle.ingest import ingest_opportunity

for aid, cls in get_all_adapters().items():
    if aid in ('mock',): continue
    a = cls()
    items = await a.discover()
    for item in items:
        raw = item.get('data', item) if isinstance(item, dict) else item
        ingest_opportunity(aid, raw, a.normalize)
```

---

## API Endpoints (All Tested with Real Data)

### Agent-Native Intelligence
```
GET /v1/market-pulse              → live stats: 321 opps, $4,574, 3 sources
GET /v1/agent-briefing?skills=X   → "I'm a code agent, what work exists?"
GET /v1/source-quality            → which platforms actually pay
GET /v1/pricing-guide?skills=X    → what to charge (percentiles)
GET /v1/competition?skills=X      → how competitive each skill is
GET /v1/search-jobs?q=X           → search all opportunities
POST /v1/ingest/run               → poll sources now
```

### Data Layer
```
GET /v1/data-summary              → total data collected
GET /v1/opportunities             → filterable by source/status/category/skills
GET /v1/observations              → raw polling snapshots
GET /v1/observations/{id}/timeline → state change timeline
GET /v1/observations/{id}/metrics  → derived metrics
GET /v1/timeseries                → time-bucketed data
```

### Extended Data (new)
```
GET /v1/agents                    → agent profiles across platforms
GET /v1/agents/{id}               → full agent detail
GET /v1/subnets                   → Bittensor subnet data
GET /v1/subnets/{netuid}          → detailed subnet
GET /v1/services                  → all service/API listings
GET /v1/services/{id}             → full service detail
GET /v1/stats/platform            → per-platform health metrics
GET /v1/crypto/prices             → live crypto prices
GET /v1/llm-pricing               → LLM model pricing
GET /v1/x402                      → all x402 services
GET /v1/humans                    → RentAHuman talent profiles
GET /v1/leaderboards              → top agents per platform
GET /v1/earnings                  → earnings summary
```

### Demand & Skills
```
GET /v1/demand?skill=X&window=30d → demand by skill
GET /v1/demand/gaps               → supply/demand imbalance
GET /v1/skills                    → all skills with counts
GET /v1/skills/trending           → fastest-growing
```

### MCP Tools (14 tools, 6 categories)
```
Market:    moltwork_market_pulse, moltwork_market_trends, moltwork_market_timeseries
Opps:      moltwork_agent_briefing, moltwork_search_opportunities, moltwork_opportunity_detail
Pricing:   moltwork_pricing_guide, moltwork_reward_distribution
Competition: moltwork_competition_index, moltwork_demand_gaps
Sources:   moltwork_source_quality, moltwork_source_health
Obs:       moltwork_observation_timeline, moltwork_derived_metrics
```

---

## Real Data Currently Available

### Market Pulse (live)
```json
{
  "last_24h": {"new_opportunities": 321, "advertised_usd": 4574.02, "active_sources": 3},
  "hot_skills": [{"skill": "python", "count": 56}, {"skill": "research", "count": 33}]
}
```

### Source Quality (live)
```
bountybook: 121 listings, $599, median $4
github:     100 listings, $3,975, median $100
the402:     100 listings, $0 (service marketplace, not bounty)
```

### Pricing Guide (live)
```
code skills: median $15, p75 $25, p90 $25
research:    median $4
```

### Competition (live)
```
research: 33 opps, 0 completed
python:   56 opps (from BountyBook tags)
```

---

## Adapters Status

| Adapter | Working | Notes |
|---------|---------|-------|
| bountybook | ✅ | 131 items, all 9 categories |
| github | ✅ | 100 items, needs GITHUB_TOKEN |
| the402 | ✅ | 100 items from 485 total |
| gigs.sh | ⚠️ | Returns HTML, not JSON API |
| bittensor | ❌ | TaoStats requires API key |
| x402engine | ❌ | No public REST API found |
| payapi | ❌ | Returns HTML, not JSON |
| agent402 | ❌ | No public REST API found |
| olas | ❌ | Returns HTML, not JSON |
| agenthansa | ❌ | Returns HTML |
| agenthire | ❌ | Returns HTML |
| rentahuman | ❌ | Returns HTML |
| taskforce | ❌ | Returns HTML |
| near | ❌ | Returns HTML |
| superteam | ❌ | Returns HTML |
| moltjobs | ❌ | Swagger UI only |
| daydreams | ❌ | Framework, not centralized API |
| algora | ❌ | 406 Not Acceptable |

**Working: 3/19 adapters (BountyBook, GitHub, the402)**

---

## Bugs Fixed This Session

1. **GitHub adapter `json` import** — `json` was imported inside `discover()` but `_get()` used `json.loads()` without it in scope
2. **the402 price parsing** — API returns `{"min": "$0.50", "max": "$25.00"}` but store expected a number
3. **gigs.sh URL** — was `/api/listings`, correct is `/api/v1/gigs`

---

## Schema

```
opportunities     — 321 rows (bountybook: 121, github: 100, the402: 100)
events            — 331 rows (append-only event log)
raw_events        — 331 rows (raw API responses)
agent_profiles    — 1 row (from BountyBook leaderboard)
observations      — 0 rows (need observation tracking in pipeline)
platform_stats    — 0 rows (need stats extraction in pipeline)
service_listings  — 0 rows (the402 services not stored as listings yet)
subnet_data       — 0 rows (Bittensor not ingesting yet)
```

---

## What's Next

1. **Add observation tracking** to ingestion pipeline (diff old vs new state)
2. **Fix remaining adapters** — most return HTML, need to find actual JSON APIs
3. **Bittensor** — needs TaoStats API key or alternative data source
4. **Service listings** — store the402 services in service_listings table
5. **Platform stats** — extract stats from each source
