# Unity Asset Store — Source Reference

**URL:** https://assetstore.unity.com
**Publisher Portal:** https://publisher.unity.com
**Status:** LIVE
**Revenue Share:** 70%
**Agent-friendly:** Partial (Publisher Portal API, unofficial)

## API Overview

Unity Asset Store uses:
- **Publisher Portal** — web-based publishing (manual upload via Unity Editor)
- **Asset Store Publishing Tools** — Unity Editor package for upload
- **Unofficial API** — community wrapper for Publisher Portal endpoints

## Key Endpoints (Unofficial)

### Packages
```
GET  /packages                         — List packages
POST /packages                         — Create package
GET  /packages/{id}                    — Get package
PUT  /packages/{id}                    — Update package
```

### Submissions
```
POST /packages/{id}/submit            — Submit for review
GET  /packages/{id}/status            — Check review status
```

### Sales
```
GET  /sales                            — List sales
GET  /sales/{id}                       — Get sale details
```

## Authentication
- Unity Account login
- Session-based auth (cookie)

## Package Requirements
- Must be a Unity package (.unitypackage or UPM)
- Must follow Submission Guidelines
- AI-generated content must add "meaningful professional value"
- Must support URP or HDRP (Unity 5+)

## Data Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| id | ✅ | Package ID |
| name | ✅ | Package name |
| description | ✅ | Full description |
| price | ✅ | In USD |
| category | ✅ | 3D, 2D, Tools, etc. |
| downloads | ✅ | Download count |
| rating | ✅ | User rating |
| created_at | ✅ | Publication date |
| unity_version | ✅ | Required Unity version |

## Limitations
- Requires Publisher account + Unity ID
- Manual upload via Unity Editor or Publishing Tools
- 70% revenue share
- AI content must be disclosed and add professional value
