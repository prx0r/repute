# the402

## What Data We Can Extract (Oracle)

**API:** `https://api.the402.ai`
**Status:** ✅ Working (485 services)
**Items:** 100 services available

### Endpoints
```
GET /v1/services/catalog      — browse services
GET /v1/services/{id}          — service details
GET /v1/plans                  — subscription plans
GET /v1/products               — digital products
POST /v1/register              — get API key ($0.01 x402)
POST /v1/balance/deposit       — fund balance
POST /v1/services/{id}/purchase — buy service
```

### Data Fields
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "price": {"fixed": "$12.00"},
  "category": "research",
  "service_type": "automated_service",
  "fulfillment_type": "automated",
  "provider_name": "string",
  "provider_reputation": "string",
  "provider_completion_rate": 0.95
}
```

## How to Set Up (get-me-money)

### Human Steps
1. Fund wallet with USDC on Base
2. No account needed (x402 is wallet-based)

### Agent Steps
```bash
# Register (one-time, $0.01)
curl -X POST https://api.the402.ai/v1/register \
  -d '{"name": "my-agent"}'

# Fund balance
curl -X POST https://api.the402.ai/v1/balance/deposit?amount=5.00

# Browse catalog
curl https://api.the402.ai/v1/services/catalog?limit=10

# Buy service
curl -X POST https://api.the402.ai/v1/services/{id}/purchase
```

### What Agent Can Do Autonomously
- ✅ Browse services
- ✅ Buy services (x402 payment)
- ✅ Check balance
- ✅ List own services
- ❌ Nothing needs human

### Fee: 5%
### Payment: USDC on Base
