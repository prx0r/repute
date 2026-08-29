# Bazaar (x402) — Source Reference

**URL:** https://x402.org
**Discovery API:** /api/bazaar/list, /api/bazaar/search
**Status:** LIVE
**Revenue Share:** 100% (protocol-level, no platform fee)
**Agent-friendly:** Yes (designed for agents)

## Overview

The x402 Bazaar is the discovery layer for the x402 payment protocol. It indexes paid APIs and MCP tools that agents can discover and pay for per-call.

## Key Endpoints

### Discovery
```
GET /api/bazaar/list                   — List all services
GET /api/bazaar/search?q={query}      — Search services
```

### Service Details
```
GET /api/bazaar/services/{id}          — Get service details
```

## Service Object
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
  "payTo": "0x...",
  "networks": ["eip155:8453"]
}
```

## Data Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| resource | ✅ | Endpoint URL |
| description | ✅ | Service description |
| price | ✅ | Per-call price |
| protocol | ✅ | HTTP or MCP |
| payTo | ✅ | Payment address |
| networks | ✅ | Supported chains |

## Use Case for Oracle

The Bazaar tells us:
- Which APIs agents are paying for
- Price per call across the ecosystem
- Which networks are most active
- What capabilities agents need
