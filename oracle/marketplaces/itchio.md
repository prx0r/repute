# itch.io — Source Reference

**URL:** https://itch.io
**API Base:** https://itch.io/api/1
**Status:** LIVE
**Revenue Share:** 90%+ (adjustable platform fee, 10% default)
**Agent-friendly:** Yes (REST API with API key auth)

## API Overview

itch.io supports:
- Games (HTML5, downloadable)
- Assets (sprites, sounds, UI kits)
- Tools (addons, plugins)
- Comics, music, soundtracks
- Bundles

## Key Endpoints

### Games/Assets
```
GET  /my-games                       — List my games
POST /my-games                       — Create game
GET  /my-games/{id}                  — Get game details
PUT  /my-games/{id}                  — Update game
```

### Uploads
```
POST /my-games/{id}/uploads         — Upload build/file
```

### Sales
```
GET  /my-sales                       — List sales
GET  /my-sales/{id}                  — Get sale details
```

## Authentication
- API key from itch.io/my-api-keys
- Header: `Authorization: Bearer {api_key}`

## Game Object
```json
{
  "id": "number",
  "title": "string",
  "url": "string",
  "description": "string",
  "short_description": "string",
  "price": "string",
  "currency": "string",
  "payout": "string",
  "views_count": "number",
  "downloads_count": "number",
  "created_at": "ISO timestamp",
  "published_at": "ISO timestamp"
}
```

## Data Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| id | ✅ | Game ID |
| title | ✅ | Game title |
| description | ✅ | Full description |
| price | ✅ | In cents (0 = free) |
| currency | ✅ | USD |
| views_count | ✅ | Page views |
| downloads_count | ✅ | Download count |
| published_at | ✅ | Publication date |
| url | ✅ | Game URL |

## Limitations
- Requires seller account
- Minimum price for paid items: $0
- No API for categories/tags management
