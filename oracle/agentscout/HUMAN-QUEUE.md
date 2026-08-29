# Human Queue — What Needs Doing

Ordered by: what unlocks the most agent capability.

## Priority 1: Unlocks Full Agent Autonomy

| # | Platform | Human Action | Unlocks | Time |
|---|----------|-------------|---------|------|
| 1 | **BountyBook** | Create wallet, sign message | Agent can claim/submit bounties | 5 min |
| 2 | **AgentHansa** | POST /api/agents/register | Agent can join quests | 1 min |
| 3 | **the402** | POST /v1/register (x402 $0.01) | Agent can buy services | 1 min |
| 4 | **Daydreams** | Install skill package | Agent can claim tasks | 2 min |

## Priority 2: Unlocks Publishing

| # | Platform | Human Action | Unlocks | Time |
|---|----------|-------------|---------|------|
| 5 | **Gumroad** | Create seller account, get API key | Agent can create/sell products | 10 min |
| 6 | **itch.io** | Create account, get API key | Agent can upload games/assets | 10 min |
| 7 | **Roblox** | Create account, age verify, Open Cloud API key | Agent can upload assets | 15 min |
| 8 | **YouTube** | Google Cloud project, OAuth | Agent can upload videos | 20 min |
| 9 | **TikTok** | Developer account, Content Posting API | Agent can post videos | 15 min |

## Priority 3: Unlocks Enterprise

| # | Platform | Human Action | Unlocks | Time |
|---|----------|-------------|---------|------|
| 10 | **AWS Marketplace** | AWS seller account | Agent can publish SaaS | 30 min |
| 11 | **Upwork** | Account + MCP server | Agent can find freelance work | 20 min |
| 12 | **Unity Asset Store** | Publisher account | Agent can sell Unity assets | 30 min |
| 13 | **Adobe Stock** | Contributor account, OAuth | Agent can sell stock content | 20 min |

## Priority 4: Manual Only (agent prepares, human submits)

| # | Platform | Human Action | What Agent Can Do |
|---|----------|-------------|-------------------|
| 14 | **Fab** | Create listing, upload, submit | Prepare assets only |
| 15 | **Canva** | Apply to Creators program | Prepare templates only |
| 16 | **Creative Market** | Seller account, upload | Prepare assets only |
| 17 | **Figma** | Publish plugin | Build plugin only |

## Priority 5: Not Yet Actionable

| # | Platform | Status |
|---|----------|--------|
| 18 | TaskForce | No public API |
| 19 | AgentHire | API not accessible |
| 20 | RentAHuman | API returns 404 |
| 21 | Agoragentic | API returns 404 |
| 22 | Claw Earn | API returns 404 |
| 23 | Clustly | MCP exists, REST API not live |
| 24 | Olas Mech | On-chain only |

## Quick Start (5 minutes)

```bash
# 1. BountyBook (5 min)
# Create wallet at bountybook.ai, sign message

# 2. AgentHansa (1 min)
curl -X POST https://www.agenthansa.com/api/agents/register \
  -H "Content-Type: application/json" \
  -d '{"capabilities": ["research", "code"]}'

# 3. the402 (1 min)
curl -X POST https://api.the402.ai/v1/register \
  -H "Content-Type: application/json" \
  -d '{"name": "my-agent"}'

# 4. Daydreams (2 min)
# Install: npm install @lucid-agents/taskmarket
```
