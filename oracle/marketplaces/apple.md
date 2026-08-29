# Apple App Store — Source Reference

**URL:** https://developer.apple.com/app-store-connect
**API Base:** https://api.appstoreconnect.apple.com
**Status:** LIVE
**Revenue Share:** 70% (15% for small businesses)
**Agent-friendly:** Yes (full REST API, 10/10 automation)

## Key Endpoints

### Apps
```
GET  /v1/apps                         — List apps
GET  /v1/apps/{id}                    — Get app details
```

### Versions
```
GET  /v1/apps/{id}/appStoreVersions   — List versions
POST /v1/apps/{id}/appStoreVersions   — Create version
```

### Submissions
```
POST /v1/submissions                  — Submit for review
```

### TestFlight
```
GET  /v1/builds                       — List builds
POST /v1/betaGroups/{id}/builds       — Add build to group
```

### Sales/Analytics
```
GET  /v1/salesReports                 — Sales reports
GET  /v1/analyticsReports             — Analytics reports
```

## Authentication
- JWT (App Store Connect API key)

## Data Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| app.id | ✅ | App ID |
| app.name | ✅ | App name |
| app.primaryLocale | ✅ | Language |
| app.sellerVisible | ✅ | Visibility |
| version.versionString | ✅ | Version |
| sales.units | ✅ | Downloads |
| sales.proceeds | ✅ | Revenue |
