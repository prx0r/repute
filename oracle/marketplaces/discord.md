# Discord Apps — Source Reference

**URL:** https://discord.com/developers
**API Base:** https://discord.com/api
**Status:** LIVE
**Revenue Share:** Discord handles billing, creator gets revenue
**Agent-friendly:** Yes (full REST API + Gateway)

## API Overview

Discord Premium Apps support:
- Monthly user subscriptions
- Server subscriptions
- One-time durable purchases
- Consumable purchases

Discord handles checkout, fraud, and receipts.

## Key Endpoints

### SKUs (products)
```
GET  /applications/{app_id}/skus           — List SKUs
GET  /skus/{sku_id}                        — Get SKU details
```

### Entitlements (purchases)
```
GET  /applications/{app_id}/entitlements    — List entitlements
POST /applications/{app_id}/entitlements    — Create test entitlement
DELETE /applications/{app_id}/entitlements/{id} — Consume entitlement
```

### Subscriptions
```
GET  /subscriptions/{subscription_id}       — Get subscription
DELETE /applications/{app_id}/entitlements/{id} — Cancel subscription
```

### Store
```
GET  /applications/{app_id}/store            — List store products
```

## Authentication
- Bot token or OAuth2
- Scope: `applications.commands`

## Data Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| sku.id | ✅ | Product ID |
| sku.name | ✅ | Product name |
| sku.price | ✅ | Price in cents |
| sku.type | ✅ | SUBSCRIPTION, DURABLE, CONSUMABLE |
| entitlement.id | ✅ | Purchase ID |
| entitlement.user_id | ✅ | Buyer |
| subscription.status | ✅ | ACTIVE, CANCELLED |
