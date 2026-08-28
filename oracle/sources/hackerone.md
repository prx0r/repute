# HackerOne

- **URL**: https://docs.hackerone.com
- **Status**: LIVE
- **Category**: Agent-Tolerated / Security Bug Bounty
- **API Base URL**: https://api.hackerone.com (v1 REST API)
- **Auth Method**: API Token (Basic auth: username:api_token)
- **Agent-Friendliness Score**: 6/10 (AI-assisted common, API available)
- **Priority for Moltwork**: LOW

## Available Endpoints

### REST API v1
- `GET /v1/hackers` — List hackers
- `GET /v1/hackers/{handle}` — Hacker profile
- `GET /v1/programs` — List programs
- `GET /v1/programs/{handle}` — Program details
- `GET /v1/reports` — List reports
- `GET /v1/reports/{id}` — Report details
- `GET /v1/bounties` — List bounties
- `GET /v1/structured_scopes` — Program scopes

### Documentation Sections
- Welcome, Profile, Hacking, Engagements, Hai (AI), Inbox & Reports
- Payments & Taxes, Pentests, Organization, Scope & Standards
- Automations, Integrations, Analytics, Hacker Engagement
- AI Systems Testing, Code Integrations

## What Oracle Can Extract
- Active bug bounty programs and scopes
- Hacker profiles and activity
- Report submissions and statuses
- Payout amounts and timelines
- Program popularity metrics

## Rate Limits
- API rate limits documented in HackerOne API docs
