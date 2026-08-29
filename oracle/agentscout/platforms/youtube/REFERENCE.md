# YouTube

## What Data We Can Extract (Oracle)

**API:** `https://www.googleapis.com/youtube/v3`
**Status:** ❌ Needs OAuth
**Items:** 0 (not accessible without auth)

### Endpoints (need OAuth 2.0)
```
POST /upload         — upload video (resumable)
GET /videos          — list videos
PUT /videos          — update metadata
GET /channels        — channel info
GET /youtubeAnalytics/v2/reports — analytics
```

## How to Set Up (get-me-money)

### Human Steps (required)
1. Go to console.cloud.google.com
2. Create project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials
5. Set up consent screen
6. Generate credentials.json
7. Set environment: `YOUTUBE_CREDENTIALS=...`

### Agent Steps (after human setup)
```bash
# Upload video
curl -X POST 'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status' \
  -H "Authorization: Bearer $YOUTUBE_TOKEN" \
  -d '{"snippet":{"title":"My Video","description":"..."},"status":{"privacyStatus":"public"}}'

# Get analytics
curl "https://youtubeanalytics.googleapis.com/v2/reports?ids=channel==MINE&metrics=views,estimatedMinutesWatched&startDate=2026-01-01&endDate=2026-08-28"
```

### What Agent Can Do Autonomously
- ✅ Upload videos
- ✅ Update metadata
- ✅ Pull analytics
- ❌ Nothing needs human after OAuth setup

### Fee: N/A
### Payment: Ad revenue (varies)
