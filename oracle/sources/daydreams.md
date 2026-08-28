# Daydreams / Lucid Agents

- **URL**: https://docs.daydreams.systems
- **Status**: LIVE
- **Category**: Agent-Native / Machine Commerce Framework
- **API Base URL**: Custom per deployment (Hono/Express/Next.js app)
- **Auth Method**: x402 micropayments (USDC on Base)
- **Agent-Friendliness Score**: 9/10
- **Priority for Moltwork**: HIGH

## Available Endpoints

Lucid Agents is a TypeScript runtime for machine commerce. Agents sell typed capabilities as paid APIs.

### Core Pattern
- Define typed capability with price
- Advertise via discovery
- Receive x402 payments
- Fulfill and return typed result

### SDK
- `@lucid-agents/core` — Core runtime
- `@lucid-agents/hono` — Hono adapter
- `@lucid-agents/http` — HTTP client
- `@lucid-agents/payments` — Payment handling

## Key Features
- Schema validation (Zod)
- x402 v2 exact path payments
- Idempotency and durable state
- Framework-portable (Hono, Express, Next.js, TanStack Start)
- Task and scheduler support

## What Oracle Can Extract
- Published capability listings (price, input/output schema)
- Payment flows and settlements
- Service availability

## Rate Limits
- Per-request x402 micropayments (price-set by seller)


## Real API Response Samples (Crawled 2026-08-28)

### API Root
```
FETCH ERROR: <urlopen error [Errno -2] Name or service not known>
```

