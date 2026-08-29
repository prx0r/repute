# Gumroad — Source Reference

**URL:** https://gumroad.com
**API Base:** https://api.gumroad.com
**Status:** LIVE
**Revenue Share:** 90% (10% platform fee)
**Agent-friendly:** Yes (REST API with API key auth)

## API Overview

Gumroad is a generic digital product marketplace. Supports:
- Products (digital files, templates, software)
- Memberships (recurring subscriptions)
- Versioned products
- Licenses

## Key Endpoints

### Products
```
GET  /v2/products                    — List products
POST /v2/products                    — Create product
GET  /v2/products/{id}               — Get product
PUT  /v2/products/{id}               — Update product
DELETE /v2/products/{id}             — Delete product
```

### Sales
```
GET  /v2/sales                       — List sales
GET  /v2/sales/{id}                  — Get sale details
```

### Subscribers
```
GET  /v2/subscribers                 — List subscribers
```

### Upload
```
POST /v2/products/{id}/versions      — Upload new version
POST /v2/media                       — Upload media file
```

## Authentication
- API key from gumroad.com/settings/api
- Header: `Authorization: Bearer {api_key}`

## Product Object
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "price": 0,
  "currency": "usd",
  "url": "string",
  "preview_url": "string",
  "tags": ["string"],
  "is_published": true,
  "variants": [],
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp"
}
```

## Data Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| id | ✅ | Product ID |
| name | ✅ | Product name |
| description | ✅ | Full description |
| price | ✅ | In cents |
| currency | ✅ | USD |
| tags | ✅ | Product tags |
| sales_count | ✅ | Total sales |
| is_published | ✅ | Status |
| created_at | ✅ | Timestamp |
| url | ✅ | Product URL |
| variants | ✅ | Product variants |

## Limitations
- Requires seller account
- 10% platform fee on sales
- No AI-specific categories
