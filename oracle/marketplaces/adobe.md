# Adobe Stock — Source Reference

**URL:** https://stock.adobe.com
**Contributor Portal:** https://contributor.adobe.com
**Status:** LIVE
**Revenue Share:** 33% (photos/vectors/illustrations), 35% (video)
**Agent-friendly:** Yes (Contributor API)

## API Overview

Adobe Stock has a Contributor API for uploading content:
- Photos, illustrations, vectors
- Videos
- Templates (Adobe Express)
- Generative AI content (with proper labeling)

## Key Endpoints

### Upload
```
POST /v2/assets/uploads              — Upload asset
POST /v2/assets/uploads/{id}/content — Upload content file
```

### Metadata
```
PUT  /v2/assets/uploads/{id}         — Update metadata
GET  /v2/assets/uploads/{id}         — Get upload status
```

### Search (public)
```
GET  /v1/search/registry             — Search stock content
GET  /v1/assets/{id}                 — Get asset details
```

## Authentication
- OAuth 2.0 (Adobe I/O)
- API key from Adobe I/O console

## Generative AI Requirements
- Must be labeled as generative AI
- Must not resemble third-party copyrighted work
- Must provide significant value
- Current royalties: 33% photos/vectors, 35% video

## Data Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| id | ✅ | Asset ID |
| title | ✅ | Asset title |
| description | ✅ | Full description |
| category | ✅ | Photos, Illustrations, etc. |
| keywords | ✅ | Search keywords |
| price | ✅ | Adobe sets pricing |
| downloads | ✅ | Download count |
| created_at | ✅ | Upload date |

## Limitations
- Requires Adobe I/O developer account
- OAuth 2.0 flow
- AI content must be properly labeled
- 33-35% revenue share
