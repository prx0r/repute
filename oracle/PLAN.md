# Oracle Implementation Plan

## Phase 1: Source Research (do first)
For each source, crawl the site, document API details, data fields available, and create a reference page.

Sources to research:
1. MoltJobs
2. ClawGig
3. Taskforce
4. SuperTeam
5. GitHub (bounties/issues)
6. Algora
7. BountyBook
8. x402-bazaar
9. 8004scan
10. Immunefi (security bounties)

## Phase 2: Build Oracle Core

### 2.1 Schema (`oracle/schema.py`)
- Opportunity model with confidence tracking
- Observation (point-in-time sighting)
- Event (state transition: posted, claimed, completed, paid, disappeared)
- Provenance fields: value, evidence, confidence, observation_method

### 2.2 Storage (`oracle/store.py`)
- SQLite: append-only `observations` table
- SQLite: `events` table (state transitions)
- Materialized views: demand_by_skill, supply_by_agent_type, market_activity, timeseries

### 2.3 Ingest Pipeline (`oracle/ingest.py`)
- SourceAdapter protocol: discover(), normalize(), refresh()
- Deduplication: compare raw_hash to skip unchanged listings
- Event diffing: detect state changes between observations

### 2.4 Source Adapters (`oracle/adapters/`)
- One file per source
- Mock adapter for testing
- Registry for pluggable sources

### 2.5 API (`oracle/api.py`)
- /v1/markets — list sources with activity stats
- /v1/opportunities — filter by skill, status, source, type
- /v1/opportunities/{id} — full history
- /v1/demand — demand by skill/agent_type
- /v1/demand/gaps — supply/demand imbalance (killer endpoint)
- /v1/skills — all skills with counts + trending
- /v1/skills/trending — fastest-growing skills
- /v1/agent-types — agent types with economics
- /v1/sources — source adapters + health
- /v1/timeseries — time-bucketed metrics

### 2.6 Aggregations (`oracle/aggregations.py`)
- Demand by skill (GROUP BY + time window)
- Supply/demand gaps (demand_usd / qualified_agents)
- Trending skills (rolling 30d growth)
- Market liquidity (posted vs completed vs paid)
- Completion rates per category/source/time

### 2.7 Integration with server.py
- Mount oracle router: app.include_router(oracle_router, prefix="/v1")
- WorkRun endpoint auto-emits oracle events on job completion

## Phase 3: Tests + Polish
- Unit tests for schema, ingest, dedup, aggregations
- Integration tests for API endpoints
- Mock data from all 10 sources

## Phase 4: Real Adapters
- Implement real adapters for each source
- Deploy + verify data flows
