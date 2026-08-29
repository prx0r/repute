# Platform Interaction Guide

How agents actually interact with each marketplace.

## Interaction Models

```
MODEL A: Full API (agent does everything)
  Agent → API → marketplace
  No human needed after initial setup

MODEL B: API + Human Gate (agent prepares, human submits)
  Agent → prepares asset → Human → submits to marketplace
  Agent does the work, human does the publishing

MODEL C: MCP Native (agent uses MCP tools)
  Agent → MCP → marketplace
  No human needed after initial setup

MODEL D: Browser Automation (agent drives browser)
  Agent → Playwright/Puppeteer → marketplace
  Works but fragile, may violate ToS

MODEL E: Manual Only (human does everything)
  Human → marketplace
  Agent can only prepare deliverables
```

---

## Per-Platform Guide

### AgentHansa
**Model:** A (Full API)
**Human steps:** None after account creation
**Agent steps:**
1. `POST /api/agents/register` — register agent (one-time)
2. `GET /api/collective/bounties/public` — list quests
3. `POST /api/collective/bounties/{id}/join` — claim quest
4. `POST /api/collective/bounties/{id}/submit` — deliver work
**Authentication:** Bearer token (from registration)
**Fee:** 5%
**Payment:** USDC via FluxA on Base

### the402
**Model:** A (Full API)
**Human steps:** None
**Agent steps:**
1. `POST /v1/register` — get API key (x402 $0.01)
2. `POST /v1/balance/deposit` — fund balance (x402)
3. `GET /v1/services/catalog` — browse services
4. `POST /v1/services/{id}/purchase` — buy service (x402)
**Authentication:** x402 payments OR pre-funded balance
**Fee:** 5%
**Payment:** USDC on Base

### BountyBook
**Model:** A (Full API)
**Human steps:** None after wallet setup
**Agent steps:**
1. Generate Ethereum wallet
2. `POST /auth/nonce` → sign → `POST /auth/verify` — authenticate
3. `GET /jobs?status=open` — list bounties
4. `POST /jobs/:id/claim` — claim bounty
5. `POST /jobs/:id/submit` — deliver work (IPFS CID)
6. AI oracle verifies → USDC released
**Authentication:** Wallet signature
**Fee:** 4%
**Payment:** USDC on Base (x402)

### SuperTeam
**Model:** B (API + Human Gate for some)
**Human steps:** 
- Create Superteam account
- Complete KYC if required
- Some bounties marked HUMAN_ONLY
**Agent steps:**
1. Browse agent-eligible listings via API
2. `POST /api/agents` — register
3. Submit via agent endpoint (for AGENT_ALLOWED bounties)
**Authentication:** API key
**Fee:** Varies
**Payment:** USDC, SOL, USDG

### Daydreams (TaskMarket)
**Model:** C (MCP Native)
**Human steps:** None
**Agent steps:**
1. Install skill package: `@lucid-agents/taskmarket`
2. Browse tasks via MCP
3. Claim + submit via x402 payments
**Authentication:** x402 micropayments
**Fee:** Varies
**Payment:** USDC on Base

### Roblox Creator Store
**Model:** B (API + Human Gate)
**Human steps:**
1. Create Roblox account
2. Complete age verification
3. Enable Open Cloud API
4. Generate API key
**Agent steps:**
1. `POST /assets/v1/assets` — upload asset (FBX, model, etc.)
2. Asset goes through validation
3. Human publishes listing via Creator Dashboard
**Authentication:** API key
**Fee:** 0% (Roblox takes processing fees)
**Payment:** Robux → USD

### Unity Asset Store
**Model:** B (Manual + Tools)
**Human steps:**
1. Create Unity ID
2. Register as publisher at publisher.unity.com
3. Read Provider Agreement
4. Submit first asset for review
**Agent steps:**
1. Use Asset Store Publishing Tools (Unity Editor)
2. Package asset as .unitypackage or UPM
3. Upload via Publisher Portal
4. Human submits for review
**Authentication:** Unity account
**Fee:** 30% (Unity takes 30%)
**Payment:** USD

### Gumroad
**Model:** A (Full API)
**Human steps:** Create seller account
**Agent steps:**
1. `POST /v2/products` — create product
2. `POST /v2/media` — upload files
3. `PUT /v2/products/{id}` — update listing
4. Monitor sales via `GET /v2/sales`
**Authentication:** API key
**Fee:** 10%
**Payment:** USD (Stripe)

### itch.io
**Model:** A (Full API + Butler CLI)
**Human steps:** Create account
**Agent steps:**
1. Use `butler` CLI for automated uploads
2. `butler upload <dir> <user>/<game>` — publish
3. `butler push <dir> <user>/<game>:<channel>` — update
4. Monitor sales via API
**Authentication:** API key
**Fee:** Adjustable (default 10%)
**Payment:** USD, PayPal

### Fab (Epic Games)
**Model:** E (Manual Only)
**Human steps:**
1. Create Epic Games account
2. Create Fab publisher profile
3. Build listing via web UI
4. Upload assets
5. Submit for review
6. Wait for approval
**Agent steps:** None (agent can prepare assets)
**Authentication:** Epic Games account
**Fee:** 12% (88% to creator)
**Payment:** USD

### Adobe Stock
**Model:** B (API + Review)
**Human steps:**
1. Create Adobe I/O account
2. Register as contributor
3. Set up OAuth 2.0
**Agent steps:**
1. `POST /v2/assets/uploads` — upload asset
2. `PUT /v2/assets/uploads/{id}` — add metadata
3. Submit for review
**Authentication:** OAuth 2.0
**Fee:** 65-67% (Adobe takes 33-35%)
**Payment:** USD

### Canva Creators
**Model:** E (Manual Only)
**Human steps:**
1. Apply to Creators program
2. Get accepted
3. Create content
4. Submit via Creator Portal
**Agent steps:** None (agent can prepare templates)
**Authentication:** Canva account
**Fee:** Royalty-based
**Payment:** USD (royalties)

### Figma Community
**Model:** B (Limited API)
**Human steps:**
1. Create Figma account
2. Publish plugin/widget/template
**Agent steps:**
1. Build plugin via Figma API
2. Publish to Community
**Authentication:** OAuth 2.0
**Fee:** N/A (free to publish)
**Payment:** Varies

### Creative Market
**Model:** E (Manual Only)
**Human steps:**
1. Create seller account
2. Upload assets via web UI
3. Disclose AI usage if applicable
4. Wait for review
**Agent steps:** None (agent can prepare assets)
**Authentication:** Email account
**Fee:** 40% (60% to creator)
**Payment:** USD (PayPal)

### AWS Marketplace
**Model:** B (API + Approval)
**Human steps:**
1. Create AWS seller account
2. Get approved as seller
3. List product in catalog
**Agent steps:**
1. Use Catalog API to create/update products
2. Submit for AWS review
**Authentication:** AWS IAM
**Fee:** 0% for SaaS (AWS takes no cut)
**Payment:** USD via AWS billing

### Upwork
**Model:** D (Browser Automation) or B (MCP)
**Human steps:**
1. Create Upwork account
2. Complete profile
3. Get verified
**Agent steps:**
1. Use MCP server (new, Aug 2026)
2. Browse jobs, submit proposals
**Authentication:** OAuth 2.0
**Fee:** 20% (service fee)
**Payment:** USD (PayPal, wire)

### TikTok
**Model:** B (API + OAuth)
**Human steps:**
1. Create TikTok developer account
2. Get Content Posting API access
3. Complete OAuth flow
**Agent steps:**
1. `POST /v2/post/publish/video/` — post video
**Authentication:** OAuth 2.0
**Fee:** N/A
**Payment:** Creator Rewards (varies)

### YouTube
**Model:** B (API + OAuth)
**Human steps:**
1. Create Google Cloud project
2. Enable YouTube Data API
3. Complete OAuth consent screen
**Agent steps:**
1. Upload via resumable upload API
2. Manage via Data API
3. Pull analytics via Analytics API
**Authentication:** OAuth 2.0
**Fee:** N/A
**Payment:** Ad revenue (varies)
