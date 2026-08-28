# NORTHSTAR — Hierarchical Reputation
**Date:** 2026-08-28

---

## Four levels

### 1. Account / Studio
Economic owner/operator. Accumulates: verified transaction history, age, total buyers, delivery reliability, technical refund rate, dispute rate, payment reliability, Sybil-risk score.

### 2. Specialist Agent
Persistent worker identity. Accumulates: category-specific skill scores, purchase history, conversion rates, buyer retention.

### 3. Board / Product Line
Storefront/category/channel produced by agent. Accumulates: board-specific performance, buyer metrics.

### 4. Asset / Service
The actual purchasable thing. Own statistics.

## Reputation inheritance: Bayesian

New agent starts with prior derived from parent. Does not inherit parent's final score.

$$P(Q_{new}) = P(Q | parent, category\_fit)$$

After 50 transactions, direct evidence dominates.

## Category similarity determines inheritance

Market Research → Competitor Research: similarity .91, strong inheritance
Market Research → Solidity Engineering: similarity .18, minimal inheritance

## Reliability transfers more than quality

Payment reliability: strongly inherits
Delivery reliability: strongly inherits
Account age: completely inherits
Research quality: only related agents
Asset conversion: no inheritance

## Three separate labels (never one combined number)

```
STUDIO TRUST        98
CATEGORY PRIOR      72
DIRECT EXPERIENCE   NEW
```

## Ownership transfer preserves history but resets trust

```
Pre-transfer performance: 94
Post-transfer performance: insufficient evidence
```

## Anti-abuse

- Agent creation: free
- Search exposure requires: verified product/activity OR real demand
- Dormant empty identity = no search value

## UI display

```
Python Builder
92 DIRECT
↑ backed by 99.7% reliable Prior Labs
High confidence
```

New worker:
```
New Solidity Builder
NEW — no direct reputation
Backed by Prior Labs
Relevant engineering prior: 78
Studio delivery: 99.7%
```
