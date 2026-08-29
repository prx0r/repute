# YouTube — Source Reference

**URL:** https://developers.google.com/youtube
**API Base:** https://www.googleapis.com/youtube/v3
**Status:** LIVE
**Revenue Share:** Ad revenue (varies by views/engagement)
**Agent-friendly:** Yes (full REST API)

## Key Endpoints

### Videos
```
GET  /videos                           — List videos
POST /videos                           — Upload video (resumable upload)
PUT  /videos                           — Update metadata
DELETE /videos                         — Delete video
```

### Channels
```
GET  /channels                         — List channels
GET  /channels/{id}                    — Get channel details
```

### Analytics
```
GET  /youtubeAnalytics/v2/reports      — Channel/video analytics
```

## Authentication
- OAuth 2.0 (required for upload/manage)
- API key for read-only

## Data Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| video.id | ✅ | Video ID |
| video.title | ✅ | Title |
| video.description | ✅ | Description |
| video.viewCount | ✅ | Views |
| video.likeCount | ✅ | Likes |
| video.publishedAt | ✅ | Publish date |
| video.duration | ✅ | Duration |
| channel.subscriberCount | ✅ | Subscribers |
