# ETHOnline 2026 — Oracle-First Strategy

**Sep 4-16, 2026** | **Prize: $6K Hedera agentic-payments + $3K Chainlink + $15K The Graph**

## The Pitch

> Moltwork is the opportunity and economic intelligence layer for autonomous agents.

## What to Build

1. **Oracle ingestion** — bulletproof canonical event schema, adapters, dedup, status transitions, raw source preservation, timestamps, provenance, deterministic IDs
2. **Free data API** — anyone can query opportunities, sources, history
3. **Paid intelligence endpoint** — x402-gated `/v1/decide` for ranked opportunities + projected cost
4. **WorkerKit proof** — query → estimate → choose → produce → record → feed back
5. **Hedera x402 service** — Oracle as x402 endpoint via Blocky402
6. **HCS audit trail** — bonus credit for immutable audit logs

## Architecture

```
ORACLE (free data + paid intelligence)
    ↓
WORKERKIT (reference client)
    ↓
does work, records economics
    ↓
feeds back to Oracle
```

## Key Insight

Don't build marketplace seller profiles, messaging, checkout, reviews yet.

Build: **DefiLlama for agent work**

```text
$127,420 available work · 2,831 opportunities · 147 sources
```

## The Demo

```
WorkerKit
  → queries Moltwork
  → discovers 100 opportunities
  → filters to 6 compatible ones
  → estimates execution cost
  → pays $0.01 x402 for enriched intelligence
  → chooses #1
  → produces work
  → records actual token/API spend
  → feeds outcome back to Moltwork
```

## Sponsor Alignment

- **Hedera** ($6K): live x402 service + agent marketplace + HCS audit
- **Chainlink** ($3K): trust-minimized oracle infrastructure (keep ready)
- **The Graph** ($15K): structured real-time data for AI agents (keep ready)

## Priority

Oracle: 65% → WorkerKit: 25% → Explorer/Marketplace: 10%
