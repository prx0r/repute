# Roblox Creator Store — Source Reference

**URL:** https://create.roblox.com/docs
**API Base:** https://apis.roblox.com
**Status:** LIVE
**Revenue Share:** 100% net proceeds (after taxes/processing)
**Agent-friendly:** Yes (full REST API with API key auth)

## API Overview

Roblox has the most complete API of any asset marketplace:
- **Assets API** — Create, update, query assets via REST
- **Catalog API** — Search marketplace items
- **Open Cloud** — Full programmatic access

## Key Endpoints

### Asset Management (requires API key)
```
POST   /assets/v1/assets                          — Create new asset
PATCH  /assets/v1/assets/{assetId}                 — Update asset content
GET    /assets/v1/assets/{assetId}                 — Get asset details
GET    /assets/v1/assets/{assetId}/versions        — List asset versions
DELETE /assets/v1/assets/{assetId}                 — Delete asset
```

### Creator Store Search (public)
```
GET /toolbox-service/v2/assets:search              — Search Creator Store
GET /toolbox-service/v2/assets/{id}                — Get asset details
```

### Marketplace (catalog)
```
GET /v1/search/items/details                       — Search catalog items
GET /v1/catalog/items/details                      — Get item details
GET /v1/assets/{assetId}/bundles                   — Get bundles for asset
```

### Asset Types Supported
- Model (FBX, OBJ)
- Mesh (FBX)
- Decal (PNG, JPG)
- Audio (MP3, OGG)
- Video (MP4)
- Plugin (Lua)
- Animation (FBX)
- Package

## Authentication
- **API Key**: Create at create.roblox.com → Open Cloud → API Keys
- Header: `x-api-key: ${ApiKey}`
- Permissions: assets (read/write)

## Asset Upload Flow
1. Create API key with asset permissions
2. POST to /assets/v1/assets with file content
3. Asset goes through validation
4. Publish listing via Creator Dashboard (web)

## Data Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| assetId | ✅ | Unique identifier |
| name | ✅ | Display name |
| description | ✅ | Full description |
| assetType | ✅ | Model, Mesh, Decal, etc. |
| price | ✅ | In Robux |
| creator | ✅ | User/group ID |
| created | ✅ | Timestamp |
| updated | ✅ | Timestamp |
| favoritedCount | ✅ | Popularity signal |
| purchasingCount | ✅ | Sales signal |
| version | ✅ | Current version |
| moderationStatus | ✅ | Review status |

## Limitations
- Requires age-verified account (2+ days old)
- 20MB max file size per upload
- Only FBX content updates via API (metadata updates unrestricted)
- Human account required for seller identity
