# NORTHSTAR — Honeycomb Integration + Pool Mechanics
**Date:** 2026-08-28

---

## Key insight from Honeycomb

ETHGlobal NYC 2026 project. Not mature marketplace but excellent architecture:
- Encrypted submissions (ERC-8183)
- Private grading/confidential evaluation
- ERC-8004 identity binding
- Winner re-encryption
- Human + agent dual interfaces
- x402 facilitator
- Contest lifecycle
- 1→many mapped back to ERC-8183 via BountyEscrow

## Reuse from Honeycomb
- ERC-8183 settlement compatibility
- encrypted submission model
- ERC-8004 identity binding
- winner re-encryption concept
- human + agent dual interfaces
- x402 facilitator work
- contest lifecycle

## Two funding modes

### Guaranteed Bounty
escrowed = guaranteed distribution. Creator cannot recover once qualifying submissions exist.

### Procurement / Request
"BUDGET UP TO $10,000" + "GUARANTEED INSPECTION $100". Buyer may stop early. Only guaranteed amount is committed.

## Two internal pots
- Discovery/inspection reserve (10-40%)
- Final award reserve (60-90%)

Presets: BEST SOLUTION, DIVERSE IDEAS, BUY USEFUL WORK, NEW TALENT DISCOVERY

## Anti-Sybil: same sample sequence for every buyer
Artifact sample order is fixed after publication using future randomness. New buyer gets sample #1, then #2, then #3. Creating another wallet doesn't produce different cheap info.

## PoolEscrow for bounties
Standard x402 batch-settlement is one payer → one provider. Bounties need one escrow → many providers. Solution: PoolEscrow contract with x402 reveal authorization.

## Human UX
Session-based: authorize $5 max spend for 1 hour, then smooth reveals. Large actions require explicit confirmation.
