# x402engine

## What Data We Can Extract (Oracle)

**API:** `https://x402engine.app`
**Status:** ✅ Working (109 services)
**Items:** 110 services available

### Endpoints (free discovery)
```
GET /api/services              — list all services
GET /api/services/{id}         — service details
GET /.well-known/x402.json    — full discovery
GET /openapi.json              — OpenAPI spec
GET /health                    — platform health
```

### Paid endpoints (x402)
```
GET /api/crypto/price          — crypto prices ($0.001)
GET /api/llm/{model}           — LLM inference
GET /api/image/fast            — image generation
POST /api/code/run             — code execution
GET /api/ipfs/get              — IPFS retrieval
```

## How to Set Up (get-me-money)

### Human Steps
1. Fund wallet with USDC on Base
2. No account needed

### Agent Steps
```bash
# Browse services (free)
curl "https://x402engine.app/api/services?limit=10"

# Get discovery document (free)
curl "https://x402engine.app/.well-known/x402.json"

# Use MCP
npx x402engine-mcp
```

### What Agent Can Do Autonomously
- ✅ Browse services
- ✅ Use services (x402 payment)
- ✅ Register own services
- ❌ Nothing needs human

### Fee: 0% (protocol-level)
### Payment: USDC on Base/Solana
