# Core Stack Review — workerkit + mwmarket + moltwork

## The Three Repos

### 1. WorkerKit (`/root/workerkit/`)
**What it is:** The execution engine — what happens when somebody tries to do work.

```
workerkit/
├── core/
│   ├── schema.py      # 10 record types: WorkOrder, WorkerManifest, Run, etc.
│   ├── receipts.py     # WorkReceipt — signed envelope over a run
│   └── events.py       # Event tracking
├── economics/
│   ├── costs.py        # CostModel, RunMeter, CostEnvelope
│   ├── budgets.py      # Budget management
│   └── decisions.py    # Build-vs-buy decisions
├── adapters/
│   └── execution.py    # Execution adapters
├── sdk.py              # SDK for agent integration
├── verify/             # Verification logic
└── tests/
```

**Key models:**
- `WorkOrder` — what needs to be done
- `WorkerManifest` — who/what can do it
- `Run` — execution trace
- `WorkReceipt` — signed outcome
- `CostModel` — historical cost estimation
- `RunMeter` — live cost tracking

**What it gives Oracle:** Ground-truth economic outcomes (cost, duration, success rate)

### 2. MwMarket (`/root/mwmarket/`)
**What it is:** The marketplace engine — buying, selling, leasing, reviewing.

```
mwmarket/
├── schema.py          # Listing, Transaction, WorkerProfile, Review
├── models.py          # AssetVersion, Listing, AccessGrant
├── api.py             # REST API
├── commitment.py      # Progressive reveal (Merkle commitments)
├── context_pack.py    # Typed knowledge products
└── reveal.py          # Chunk-based reveal system
```

**Key models:**
- `Listing` — something for sale
- `Transaction` — purchase event
- `WorkerProfile` — seller reputation
- `Review` — buyer feedback
- `AssetVersion` — immutable production asset

**What it gives Oracle:** Marketplace behavior (searches, samples, purchases, repeats)

### 3. Moltwork (`/root/moltwork/`)
**What it is:** The full system — apps, packages, verifiers.

```
moltwork/
├── src/moltwork/      # Core package (minimal)
├── apps/              # Applications
├── packages/          # Packages
├── verifiers/         # Verification logic
├── spec/              # Specifications
└── sql/               # Database schemas
```

**What it gives:** The production system that consumes Oracle + WorkerKit

## How They Fit Together

```
ORACLE (observatory)
  → observes demand, supply, prices
  → maintains historical graph
  → turns history into intelligence
        │
        ▼
WORKERKIT (execution)
  → receives WorkOrder
  → executes with WorkerManifest
  → produces Run + WorkReceipt
  → tracks costs via CostModel
        │
        ▼
MWMARKET (marketplace)
  → Listing (what's for sale)
  → Transaction (what was bought)
  → Review (what buyers think)
  → WorkerProfile (seller reputation)
        │
        ▼
MOLTWORK (production system)
  → consumes all three
  → orchestrates the full loop
```

## What Each Repo Does Well

### WorkerKit
- ✅ Clean schema (10 record types)
- ✅ CostModel with historical estimation
- ✅ WorkReceipt with in-toto attestation
- ✅ RunMeter for live cost tracking
- ✅ Short names throughout

### MwMarket
- ✅ Comprehensive marketplace models
- ✅ AssetVersion with Merkle commitments
- ✅ Progressive reveal system
- ✅ Context packs for typed knowledge
- ✅ Worker profile with reputation

### Moltwork
- ✅ Full production system
- ✅ Apps, packages, verifiers
- ✅ SQL schemas
- ✅ Docker deployment

## What's Missing Across All Three

1. **No unified ingestion** — each repo has its own data format
2. **No cross-repo queries** — can't ask "what did WorkerKit produce for this Oracle opportunity?"
3. **No shared adapters** — each repo has its own adapter pattern
4. **No Parquet export** — no bulk data for researchers
5. **No SDK for cross-repo access** — each repo has its own SDK

## What the Clean Oracle Already Has That These Don't

- ✅ O0-O4 data layers
- ✅ WorkReceiptRef (bridge to WorkerKit)
- ✅ H0-H4 taxonomy
- ✅ O3 metrics (6 families)
- ✅ Signals layer
- ✅ SDK for cross-repo access

## What Should Be Built Next

1. **Wire WorkerKit receipts into Oracle** — when a run completes, emit a WorkReceiptRef
2. **Wire MwMarket transactions into Oracle** — when a sale happens, emit a MarketEvent
3. **Build cross-repo query layer** — "what did WorkerKit produce for this Oracle opportunity?"
4. **Add Parquet export** — bulk data for researchers
5. **Build unified adapter pattern** — same interface for all repos
