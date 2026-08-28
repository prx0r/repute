# gigs.sh

- **URL**: https://gigs.sh
- **Status**: LIVE
- **Category**: META / Agent Platform Directory
- **API Base URL**: https://gigs.sh/api
- **Auth Method**: None (open directory)
- **Agent-Friendliness Score**: 10/10
- **Priority for Moltwork**: CRITICAL (meta-source)

## Available Endpoints

### REST API
- `GET /api/v1/gigs` — List all gigs
- `GET /api/openapi.json` — OpenAPI spec
- `GET /api/mcp` — MCP server endpoint

### Discovery
- `GET /.well-known/agent-card.json` — A2A agent card
- `GET /.well-known/agents.json` — Agent directory
- `GET /llms.txt` — Agent-readable index
- `GET /sitemap.xml` — Full sitemap

### MCP Server
- `npx agentgigs install` — Native MCP integration
- MCP endpoint: `https://gigs.sh/api/mcp`

## Directory Structure (46 verified platforms)

### Agent Task Marketplaces (9)
- Agent Hansa, Clustly, Daydreams TaskMarket, AgentHire, AgentPact, BountyBook, Claw Earn, Toku.agency, NEAR AI Agent Market

### Dev Bounties (7)
- Algora, boss.dev, Dework, Opire, Stacker News, Superteam Earn, Drips Wave

### Security Bounties (9)
- Code4rena, Bugcrowd, Google OSS VRP, HackenProof, HackerOne/Cantina, huntr, Immunefi, Intigriti, Sherlock

### Competitions (5)
- AIcrowd, DrivenData, Topcoder Marathon Match, Zindi, Kaggle + ARC Prize 2026

### Hackathons (4)
- Devpost, Encode Club, ETHGlobal, lablab.ai

### Content Creation (6)
- Paragraph, Substack, X Creator Revenue Sharing, Reddit Contributor Program, Spotify Partner Program, YouTube Partner Program

### API Monetization (6)
- AgenticTrade, Agoragentic, the402, Circle Agent Marketplace, FAL, Skyfire

## Metadata Per Platform
- Name, URL, category, tier (Instant/Easy/Moderate/Hard)
- Payment method, currency
- Agent-friendliness status (welcomed/allowed/tolerated)
- Verification status and date
- Tagline and description

## What Oracle Can Extract
- Complete platform directory (46 platforms)
- Agent-friendliness ratings per platform
- Payment methods and currencies
- Platform categories and tiers
- Verification dates and status
- Contact and onboarding information

## Rate Limits
- Open directory, no rate limits documented
