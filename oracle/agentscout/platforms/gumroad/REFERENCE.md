# Gumroad

## What Data We Can Extract (Oracle)

**API:** `https://api.gumroad.com`
**Status:** ❌ Needs API key
**Items:** 0 (not accessible without auth)

### Endpoints (need API key)
```
GET /v2/products           — list products
POST /v2/products          — create product
PUT /v2/products/{id}      — update product
POST /v2/media             — upload file
GET /v2/sales              — list sales
GET /v2/subscribers        — list subscribers
```

### Data Fields (when accessible)
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "price": 1000,
  "currency": "usd",
  "url": "string",
  "tags": ["string"],
  "sales_count": 42,
  "is_published": true
}
```

## How to Set Up (get-me-money)

### Human Steps (required)
1. Go to gumroad.com
2. Create seller account
3. Go to Settings → API
4. Generate API key
5. Set environment: `GUMROAD_API_KEY=...`

### Agent Steps (after human setup)
```bash
# List products
curl -H "Authorization: Bearer $GUMROAD_API_KEY" \
  https://api.gumroad.com/v2/products

# Create product
curl -X POST https://api.gumroad.com/v2/products \
  -H "Authorization: Bearer $GUMROAD_API_KEY" \
  -d 'name=My Product&price=1000&description=...'

# Upload file
curl -X POST https://api.gumroad.com/v2/media \
  -H "Authorization: Bearer $GUMROAD_API_KEY" \
  -F "file=@product.pdf"
```

### What Agent Can Do Autonomously
- ✅ Create products
- ✅ Upload files
- ✅ Update listings
- ✅ Monitor sales
- ❌ Nothing needs human after account setup

### Fee: 10%
### Payment: USD (Stripe)
