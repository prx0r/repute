# Wix App Market — Source Reference

**URL:** https://dev.wix.com
**API Base:** https://www.wixapis.com
**Status:** LIVE
**Revenue Share:** 100% year 1, 80% after
**Agent-friendly:** Yes (full REST API + SDK)

## Key Endpoints

### Apps
```
GET  /apps/v1/apps                    — List apps
GET  /apps/v1/apps/{appId}            — Get app
```

### Subscriptions
```
GET  /pricing/v1/subscriptions        — List subscriptions
```

### Commerce
```
GET  /ecommerce/v1/products           — List products
POST /ecommerce/v1/products           — Create product
```

## Authentication
- OAuth 2.0 or API key

## Data Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| app.id | ✅ | App ID |
| app.name | ✅ | App name |
| app.description | ✅ | Description |
| app.installs | ✅ | Install count |
| app.rating | ✅ | Rating |
| subscription.price | ✅ | Price |
