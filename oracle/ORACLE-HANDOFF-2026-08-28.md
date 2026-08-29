# Oracle Architecture Handoff — 2026-08-28

## Core Architecture

```text
Internet work markets
        ↓
collect every observable state/event
        ↓
IMMUTABLE RAW EVENT LOG
        ↓
versioned normalization
        ↓
analytics warehouse
        ↓
free API + SQL + Parquet
        ↓
agents / researchers / dashboards

Meanwhile:

immutable event batches
        ↓
Merkle tree
        ↓
Merkle root anchored on-chain
```

## The Event Envelope (lock only this)

```json
{
  "event_id": "01J...",
  "event_type": "opportunity.observed",
  "schema": "moltwork/opportunity-observed@1.2.0",

  "source": "clawgig",
  "source_id": "gig_8127",

  "observed_at": "2026-08-28T08:04:13Z",
  "effective_at": "2026-08-28T08:03:51Z",

  "subject": {
    "type": "opportunity",
    "id": "clawgig:gig_8127"
  },

  "payload": {},

  "provenance": {},
  "raw_hash": "sha256:..."
}
```

Everything interesting lives in the versioned `payload`.

Future schemas:
```
moltwork/opportunity-observed@1.3
moltwork/bid-observed@1.0
moltwork/x402-call@1.0
moltwork/auction-bid@1.0
moltwork/agent-service-sale@1.0
```

## Three Data Layers (Bronze/Silver/Gold)

### 1. Raw — immutable truth
```
raw/
  clawgig/
    2026/08/28/events.jsonl.zst
  moltjobs/
  superteam/
  x402/
```

Every blob gets: SHA-256, source, retrieval timestamp, HTTP metadata, adapter version.

### 2. Normalized — structured events
```
opportunity.created / observed / updated / closed
bid.observed / proposal.observed / claim.observed / award.observed
submission.observed / completion.observed
payment.observed
agent.observed / service.observed / service.call_observed
buyer.observed / seller.observed
```

Columnar storage (Parquet).

### 3. Analytics — mutable interpretations (ClickHouse)
```
market_daily / skill_demand_daily / agent_type_demand
source_liquidity / buyer_activity / reward_distribution
time_to_first_response / time_to_claim / time_to_completion
payment_realization / competition_index
```

## Never Rewrite History

Store raw events + versioned normalizers:
```
RAW EVENT → normalizer-v1 → old interpretation
RAW EVENT → normalizer-v7 → new interpretation
```

Entire database can be rebuilt with newest intelligence.

## Never Update or Delete Observations

Corrections are new events:
```
event A: "reward = $500"
event B: "type=correction, event=A, reward actually 500 USDC, USD conversion was $499.94"
```

## Observation Value (polling data = the product)

Record every meaningful state change with timestamps:
```
10:00 $500 Solidity audit, 0 proposals, OPEN
10:03 $500 Solidity audit, 2 proposals, OPEN
10:07 $500 Solidity audit, 7 proposals, OPEN
10:11 $500 Solidity audit, 12 proposals, OPEN
10:14 CLAIMED
16:42 SUBMITTED
17:08 PAID $500
```

Derivable metrics per job:
- time to first competitor
- proposal velocity
- time to claim
- number responses before claim
- time to completion
- advertised reward vs realized payment

## Inferred Timestamps (be careful)

Never claim exact timestamps for polled data:
```json
{
  "metric": "proposal_count",
  "previous": 3,
  "current": 5,
  "change": 2,
  "interval": {
    "after": "10:00",
    "before": "10:05"
  }
}
```

## Evidence/Provenance (first-class)

```json
{
  "value": 500,
  "unit": "USD",
  "evidence": {
    "type": "source_api",
    "source": "clawgig",
    "raw_hash": "sha256:...",
    "observed_at": "...",
    "adapter": "clawgig@0.4.1"
  },
  "confidence": "observed"
}
```

Evidence classes:
```
ONCHAIN_VERIFIED / SOURCE_VERIFIED / DIRECTLY_OBSERVED
DERIVED / INFERRED / USER_REPORTED / UNKNOWN
```

## Blockchain as Audit/Notarization Layer

NOT per-observation. Instead:
```
10,000 observations → hash each → Merkle tree → root → one chain transaction
```

Publish manifest:
```json
{
  "batch": "2026-08-28T16",
  "events": 10832,
  "merkle_root": "0x83ac...",
  "chain_transaction": "..."
}
```

Chain-agnostic anchors:
```json
{
  "algorithm": "sha256",
  "merkle_root": "...",
  "anchors": [
    {"chain": "algorand", "tx": "..."},
    {"chain": "base", "tx": "..."}
  ]
}
```

## Algorand First

- Global x402 Challenge: $100K + 500K ALGO prizes
- Requires paid API on Algorand MainNet, real x402 payments via GoPlausible facilitator
- Moltwork Intelligence = paid x402 endpoint for expensive analytics
- Core dataset stays free

## Eventually Also Anchor to Base

```
                 MOLTWORK
                    │
          canonical data hashes
                    │
            Merkle checkpoints
             /             \
       Algorand            Base
```

## Verification CLI

```bash
molt verify evt_123
```

Returns:
```
✓ raw observation hash valid
✓ included in batch 9812
✓ Merkle proof valid
✓ batch root anchored on Algorand
✓ checkpoint finalized
✓ event existed no later than Aug 28 2026 16:05 UTC
```

## Three Interfaces

### REST (for agents)
```
GET /v1/opportunities
GET /v1/demand?skill=solidity
GET /v1/markets/clawgig
GET /v1/metrics/time-to-first-bid
```

### SQL (for analysts — ClickHouse)
```sql
SELECT source, median(time_to_first_response_seconds), count(*)
FROM opportunities
WHERE first_seen_at > now() - INTERVAL 30 DAY
GROUP BY source;
```

### Bulk data (for researchers)
```
https://data.moltwork.com/events/2026/08/*.parquet
https://data.moltwork.com/opportunities/latest.parquet
```

DuckDB can query directly:
```sql
SELECT * FROM read_parquet('https://data.moltwork.com/opportunities/*.parquet');
```

## MVP Architecture

```text
                    adapters
                       │
                       ▼
              RAW JSON EVENT STORE
                       │
                 SHA256 each event
                       │
                       ▼
               NORMALIZATION WORKER
                       │
                  PostgreSQL
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
          REST API          Parquet export
             │
             ▼
         ClickHouse (later)

Every hour:
raw hashes → Merkle root → Algorand checkpoint
```

## Dashboard Vision (Dune for agent labor)

```
AGENT ECONOMY — LAST 24H
New work posted             18,491
Advertised demand           $2.84M
Verified completed volume   $412k
Active buyers               3,482
Active workers              7,814

Median time → first bid     2m 41s
Median time → claim         19m 08s
Median completion           4h 12m

HOTTEST CAPABILITIES
Solidity security     +83%
Browser automation    +51%
Rust                   +39%
Research               +12%
Generic writing        -18%

SITE LIQUIDITY
              Listings   Paid%   Time→claim   Competition
MoltJobs        832       72%      11m            medium
ClawGig       1,291       48%       7m            high
Site X        4,021        3%      91h            low
```
