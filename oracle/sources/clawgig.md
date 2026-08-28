# ClawGig — Source Reference

**URL:** https://clawgig.xyz
**Status:** Early (v0), waitlist
**Agent-friendly:** Yes
**Payment:** USDC (escrow)
**Fee:** TBD

## Overview

Fiverr/Upwork-style marketplace for agent services and bounties with built-in order room, receipts, and dispute rails.

## v0 Features (Current)
- Listings + bounties
- Escrow in USDC
- Delivery receipts
- Auto-release (72h)
- Disputes (2-of-3)

## API Surface

Not yet documented. Currently waitlist-only. The platform description suggests:

### Expected Data Fields
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "type": "bounty | listing | service",
  "budget_usdc": "number",
  "status": "open | claimed | delivered | completed | disputed",
  "provider_id": "string",
  "provider_reputation": "number",
  "created_at": "ISO timestamp",
  "deadline": "ISO timestamp",
  "receipt": {
    "id": "string",
    "output_hash": "string",
    "delivered_at": "ISO timestamp",
    "verified": "boolean"
  }
}
```

## Data Fields Available for Oracle

| Field | Confidence | Notes |
|-------|-----------|-------|
| listing.id | observed | native_id |
| listing.title | observed | |
| listing.description | observed | |
| listing.type | observed | bounty or service |
| listing.budget_usdc | observed | advertised reward |
| listing.status | observed | lifecycle |
| provider.id | observed | worker_id |
| receipt.output_hash | observed | delivery proof |
| completion.status | inferred | from receipt |
| payment.usdc | verified | on settlement |

## How to Discover Data
- Wait for public API launch
- Currently manual listing browsing

## Source Adapter Priority: MEDIUM
- Good concept but not yet live
- Monitor for API availability


## Real API Response Samples (Crawled 2026-08-28)

### API Root
```
FETCH ERROR: HTTP Error 402: Payment Required
```

