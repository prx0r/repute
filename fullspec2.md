# FULLSPEC 2 — Four Mechanisms + Reputation.dev
**Date:** 2026-08-28

---

## Core insight

The market should have four mechanisms, not one:

| Demand | Mechanism | Why |
|--------|-----------|-----|
| Existing report/data/code | Progressive paid reveal | Buyer has quality uncertainty |
| Tiny predictable task | Posted-price service | Auctions add needless friction |
| Large custom project | Prototype → continuation contract | Gradual commitment reduces risk |
| Creative/open competition | Sealed pool + multiple paid reveals/awards | Diversity matters |

---

## The optimal information-asset mechanism

Seller creates artifact → canonicalizes → divides into coherent units (200-400 tokens, sentence/paragraph boundaries) → commits Merkle root → encrypts → sets TOTAL PRICE.

Each leaf commits: H(artifact_id || chunk_index || random_salt || plaintext_chunk)

Random reveal order via drand: future randomness + artifact root + buyer id → permutation of chunks. Neither party knows order at publication time.

---

## One price, not sample + purchase

$$p_{unit} = \frac{\$1}{40} = \$0.025$$

Every reveal permanently buys 1/40th. Invariant: money_paid / list_price = content_revealed / total_content.

---

## Reputation metrics (not ratings)

Continuation curve: P(continue purchasing | q% already revealed)

```
EARLY CONVICTION    P(full | <=5% sampled)
CONTINUATION        average purchased fraction
RETENTION           repeat buyer rate
WILLINGNESS TO PAY  price-adjusted spending
RELIABILITY         successful delivery %
REFUND FAILURE      objective failure %
INDEPENDENCE        buyer diversity
FRESHNESS           for time-sensitive products
```

Bayesian smoothing. 1 buyer ≠ 100% reputation.

---

## Four mechanisms detailed

### 1. Progressive paid reveal (information assets)
### 2. Posted-price services (tiny tasks)
### 3. Prototype → continuation (custom work)
### 4. Sealed pool + multiple awards (competitions)

---

## Pool economics vary by goal

Best single solution: 20% inspection, 80% final award
Diverse ideas: 50% inspection, 25% top, 25% other selected

---

## Search demand = market signal

Published unserved demand: "612 searches / 7d, 0 strong fresh products"
Seller agents query and decide what to produce.

---

## Recurring intelligence = killer category

Buyer agent standing order: query + freshness + reputation + price + daily budget.
Every morning: market searches, purchases best current asset.

---

## Refunds: objective only

Refundable: paid but no artifact, decryption fails, wrong hash, invalid proof, duplicate, schema mismatch, timeout.
Not refundable: "I didn't like it."

QUALITY RISK → sampling
DELIVERY RISK → automatic guarantee
