# TikTok — Source Reference

**URL:** https://developers.tiktok.com
**API Base:** https://open.tiktokapis.com
**Status:** LIVE
**Revenue Share:** Creator Rewards (varies)
**Agent-friendly:** Yes (Content Posting API)

## Key Endpoints

### Content Posting
```
POST /v2/post/publish/video/    — Direct post video
POST /v2/post/publish/upload/   — Upload video as draft
```

### User Info
```
GET /v2/user/info/              — Get user profile
```

### Analytics
```
GET /v2/video/list/             — List videos
GET /v2/video/query/            — Get video details
```

## Authentication
- OAuth 2.0
- Scope: `video.publish`

## Data Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| video.id | ✅ | Video ID |
| video.title | ✅ | Caption |
| video.viewCount | ✅ | Views |
| video.likeCount | ✅ | Likes |
| video.shareCount | ✅ | Shares |
| video.commentCount | ✅ | Comments |
| video.createTime | ✅ | Create time |
