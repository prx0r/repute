# Platform Reality Check — 2026-08-28

## What Actually Has Working APIs

Out of 13+ agent marketplace platforms, **only 5 have public APIs that an agent can actually call**:

### ✅ WORKING (agent can call these)

| Platform | Endpoint | Items | Key Fields | Can Upload? |
|----------|----------|-------|------------|-------------|
| **AgentHansa** | `/api/collective/bounties/public` | 20 | reward_amount, status, category, tags | Unknown (need to test) |
| **Daydreams** | `/api/tasks` | 2+ | reward (smallest unit), status, tags, mode | Unknown |
| **the402** | `/v1/services/catalog` | 485 | name, price, category, provider_reputation | Yes (REST API) |
| **Superteam** | `/api/listings` | 32 | rewardAmount, status, type, agentAccess | Unknown |
| **BountyBook** | `/api/jobs` | 5+ | budget_usdc, status, tags, difficulty | Yes (REST API) |

### ❌ NOT WORKING (no public API or broken)

| Platform | Error | Reality |
|----------|-------|---------|
| TaskForce | HTTP 404 | No public API found |
| AgentHire | Connection refused | API not accessible |
| RentAHuman | HTTP 404 | Docs exist but API not live |
| Agoragentic | HTTP 404 | API not accessible |
| Claw Earn | HTTP 404 | API not accessible |
| Clustly | HTTP 404 | MCP exists but REST API not live |
| Olas Mech | HTTP 400 | On-chain only, no REST |
| TaskForce AI | HTTP 404 | Directory, not marketplace |

## What This Means

**Most "agent marketplaces" are web UIs, not APIs.** An agent cannot programmatically:
- Browse listings on TaskForce
- Submit work on RentAHuman
- List services on Agoragentic
- Claim bounties on Claw Earn

The 5 working APIs are what we can actually build on.

## What Each Working API Actually Returns

### AgentHansa (20 bounties)
```json
{
  "id": "string",
  "title": "Get AgentHansa mentioned in an AI newsletter",
  "reward_amount": 100.0,
  "status": "in_progress | open | completed",
  "category": "marketing",
  "tags": ["newsletter", "press", "marketing", "growth"]
}
```
**Can agent interact?** Yes — register via POST, join quests, submit work.

### Daydreams (2+ tasks)
```json
{
  "id": "0x...",
  "description": "# BRYAN'S HARD DATA...",
  "reward": 24200000,  // smallest unit (÷1M for USDC)
  "status": "open",
  "tags": ["dashboard", "html", "data-visualisation"],
  "mode": "bounty"
}
```
**Can agent interact?** Yes — skill package + x402 payments.

### the402 (485 services)
```json
{
  "name": "Sourced Research Brief with Checkable Citations",
  "price": {"fixed": "$12.00"},
  "category": "research",
  "provider_reputation": "...",
  "provider_completion_rate": "..."
}
```
**Can agent interact?** Yes — x402 payments, full REST API.

### Superteam (32 bounties)
```json
{
  "title": "Create Content for Breakpoint 2026",
  "rewardAmount": 8000,
  "status": "OPEN",
  "agentAccess": "HUMAN_ONLY | AGENT_ALLOWED",
  "token": "USDG"
}
```
**Can agent interact?** Partially — some bounties are HUMAN_ONLY.

### BountyBook (5+ jobs)
```json
{
  "title": "Deliver warm introduction...",
  "budget_usdc": "5.00",
  "status": "open",
  "tags": ["sasame", "hunter", "warm-intro"],
  "difficulty": "intermediate"
}
```
**Can agent interact?** Yes — wallet auth, x402 escrow, AI oracle verification.

## The Honest Assessment

**What we can actually do right now:**
1. Ingest data from 5 platforms (we're doing this)
2. Display objective stats about each platform
3. Help agents find work on platforms with APIs

**What we CANNOT do yet:**
1. Upload/publish to most platforms (need to test each one)
2. Submit work programmatically (need to test each one)
3. Track completions across platforms (no unified webhook)

**What WorkerKit should focus on:**
1. Thin adapter for each working API
2. Human-queue for platforms that need manual steps
3. Unified search across all 5 working APIs
4. Objective comparison (fee, payment rail, API quality)
