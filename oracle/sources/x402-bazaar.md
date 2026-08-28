# x402 Bazaar — Source Reference

**URL:** https://x402bazaar.org
**Discovery API:** `/api/bazaar/list`, `/api/bazaar/search`
**Status:** Live (protocol-level)
**Agent-friendly:** Yes (designed for agents)
**Payment:** USDC on Base, Solana (x402 protocol)
**Fee:** Protocol-level, varies by merchant

## Overview

The discovery layer for x402 — a payment protocol for APIs and MCP tools. Services register on the Bazaar; agents discover and pay per-call via HTTP 402. Not a bounty platform — a paid API marketplace.

## API Surface

### Discovery Endpoints
```
GET /api/bazaar/list                # List all services
GET /api/bazaar/search?q={query}   # Search services
```

### Service Object (Bazaar Extension)
```json
{
  "resource": "https://api.example.com/endpoint",
  "description": "string",
  "price": {
    "amount": "number (USDC atomics)",
    "currency": "USDC",
    "network": "eip155:8453"
  },
  "protocol": "http | mcp",
  "extensions": {
    "bazaar": {
      "info": {
        "input": {
          "type": "http | mcp",
          "method": "GET | POST | PUT | PATCH | DELETE",
          "toolName": "string (for MCP)",
          "inputSchema": "object (for MCP)",
          "description": "string",
          "transport": "streamable-http | sse"
        }
      }
    }
  },
  "payTo": "0x...",
  "networks": ["eip155:8453", "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp"],
  "maxAmountUsd": "number"
}
```

## Data Fields Available for Oracle

| Field | Confidence | Notes |
|-------|-----------|-------|
| service.resource | observed | endpoint URL |
| service.description | observed | |
| service.price.amount | observed | cost per call |
| service.price.currency | observed | USDC |
| service.protocol | observed | http or mcp |
| service.payTo | observed | merchant address |
| service.networks | observed | chain availability |
| service.maxAmountUsd | observed | price ceiling |
| mcp.toolName | observed | for MCP tools |
| mcp.inputSchema | observed | tool parameters |

## Unique Signals
- **Price per call** — actual API pricing data
- **MCP tool discovery** — what tools agents are building
- **Network coverage** — where payments settle
- **Merchant activity** — who's selling what

## Note
This is NOT a bounty/task marketplace. It's a paid API discovery layer. Useful for:
- Understanding what agents are paying for
- Pricing intelligence for API services
- Tracking MCP tool ecosystem growth

## Source Adapter Priority: MEDIUM
- Useful for pricing data
- MCP tool ecosystem signal
- Not directly job/bounty data
- Complementary to bounty sources
