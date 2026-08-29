# Roblox

## What Data We Can Extract (Oracle)

**API:** `https://apis.roblox.com`
**Status:** ❌ Needs API key
**Items:** 0 (not accessible without auth)

### Endpoints (need API key)
```
GET /toolbox-service/v2/assets:search  — search Creator Store
POST /assets/v1/assets                — upload asset
PATCH /assets/v1/assets/{id}          — update asset
GET /v1/catalog/items/details         — catalog search
```

### Data Fields (when accessible)
```json
{
  "id": "number",
  "name": "string",
  "assetType": "Model | Mesh | Decal | Audio | Plugin",
  "price": "number (Robux)",
  "creator": {"id": "number", "name": "string"},
  "favoritedCount": "number",
  "purchasingCount": "number"
}
```

## How to Set Up (get-me-money)

### Human Steps (required)
1. Create Roblox account at roblox.com
2. Complete age verification (2+ days old)
3. Go to create.roblox.com → Open Cloud → API Keys
4. Create API key with "assets" permission
5. Set environment: `ROBLOX_API_KEY=...`

### Agent Steps (after human setup)
```bash
# Search Creator Store (no auth needed for read)
curl "https://apis.roblox.com/toolbox-service/v2/assets:search?query=sci-fi&limit=10"

# Upload asset (needs API key)
curl -X POST https://apis.roblox.com/assets/v1/assets \
  -H "x-api-key: $ROBLOX_API_KEY" \
  -F 'request={"assetType":"Model","displayName":"My Asset"}' \
  -F 'fileContent=@model.fbx'
```

### What Agent Can Do Autonomously
- ✅ Search Creator Store (read)
- ✅ Upload assets (with API key)
- ✅ Update assets (with API key)
- ❌ Publish listing (needs Creator Dashboard)
- ❌ Set pricing (needs Creator Dashboard)

### Fee: 0% (Roblox takes processing fees)
### Payment: Robux → USD

## Unique: Roblox has two markets
- **Creator Store** — wholesale inputs (models, plugins, systems)
- **Marketplace** — retail outputs (clothing, accessories)
