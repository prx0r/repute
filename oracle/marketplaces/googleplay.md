# Google Play — Source Reference

**URL:** https://developer.android.com/google-play
**API Base:** https://androidpublisher.googleapis.com/androidpublisher
**Status:** LIVE
**Revenue Share:** 70% (85% for subscriptions)
**Agent-friendly:** Yes (full REST API, 10/10 automation)

## Key Endpoints

### Edits
```
POST /v3/applications/{package}/edits            — Create edit
POST /v3/applications/{package}/edits/{editId}/bundles — Upload AAB
PATCH /v3/applications/{package}/edits/{editId}  — Update metadata
POST /v3/applications/{package}/edits/{editId}/commit — Commit edit
```

### Subscriptions
```
GET  /v3/applications/{package}/subscriptions   — List subscriptions
POST /v3/applications/{package}/subscriptions   — Create subscription
```

### Purchases
```
GET  /v3/applications/{package}/purchases/{type} — Verify purchase
```

## Authentication
- OAuth 2.0 (Google Cloud service account)

## Data Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| edit.id | ✅ | Edit ID |
| listing.title | ✅ | App title |
| listing.description | ✅ | Full description |
| listing.language | ✅ | Locale |
| stats.installs | ✅ | Install count |
| stats.rating | ✅ | Average rating |
