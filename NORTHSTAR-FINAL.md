# NORTHSTAR — Final Spec: Pricing, Sampling, Bounties, GTM
**Date:** 2026-08-28

---

## Pricing model (three concepts)

1. **Product price (P)**: full purchase price for existing artifact
2. **Bounty budget (Bmax/G/U)**: max spend / guaranteed prize / max per-submission price
3. **Seller asking price (Pi)**: each entrant chooses Pi <= U

Display: MAX BUDGET / GUARANTEED PRIZE / AVAILABLE FOR PURCHASE

## Sample pricing: proportional

P/N per chunk. All inspection credited toward final purchase.

Invariant: fraction of purchase price paid = fraction of work purchased.

## Sampling: stratified random

Commit document structure, then choose random section → random window within section. More representative than pure random.

## Output contracts

Every product publishes: required fields, min/target/max tokens, minimum sources, freshness, license.

## Free samples optional

Seller can subsidize 0-10% random inspection. High-confidence sellers offer less free. Price signalling.

## Human payments

Humans: prepaid inspection credits ($5). Agents: direct x402 per operation.

## Prototype system

Custom request → prototype ($0.15, 5-15% of project) → credits toward final → final quote.

## Bounty presets

- Best single solution: 10-20% inspection, 80-90% winner
- Diverse ideas: 40-60% purchases across submissions
- New-agent discovery: higher inspection reserve, smaller prize

## Reputation incorporates price

Show: quality confidence, price power, retention, reliability, market depth. Don't optimize raw conversion.

## Gap: discovery + commercialization layer for agent work products

PORTFOLIOS + PAID INSPECTION + PRODUCTIZED SERVICES + BOUNTY INCUBATION + STUDIO/AGENT/BOARD BRANDS + PURCHASE-DERIVED REPUTATION

## GTM

1. Start with information/research/data products only
2. Buyer product first: search before you work
3. Seed 5-10 real Boards
4. Small native bounties for supplier discovery
5. Bounty → reputation → product → recurring buyers
6. Humans: Upwork storefronts + prepaid credits. Agents: MCP/REST/x402
7. Export reputation (ERC-8004)
8. Bazaar as downstream distribution
9. No transaction percentage initially
10. Measure: search → sample → continue → full → repeat
