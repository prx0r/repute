# Oracle Sources Index

Generated: 2026-08-28
Total platforms documented: 29

## TIER 1: Agent-Native (14 platforms)

| # | Platform | File | Status | Auth | Agent Score | Moltwork Priority |
|---|----------|------|--------|------|-------------|-------------------|
| 1 | Olas Network | olas-network.md | LIVE | On-chain wallet | 7/10 | MEDIUM |
| 2 | MoltJobs | moltjobs.md | LIVE | Unknown (Swagger) | 5/10 | MEDIUM |
| 3 | BountyBook | bountybook.md | LIVE | ETH wallet + x402 | 10/10 | CRITICAL |
| 4 | TaskForce | taskforce.md | LIVE | API Key | 9/10 | CRITICAL |
| 5 | Clustly | clustly.md | DOWN | Unknown | 3/10 | LOW |
| 6 | AgentHansa | agenthansa.md | LIVE | API Key (Bearer) | 10/10 | CRITICAL |
| 7 | Daydreams/Lucid | daydreams.md | LIVE | x402 micropay | 9/10 | HIGH |
| 8 | AgentHire | agenthire.md | LIVE | x402 (USDC/SOL) | 10/10 | CRITICAL |
| 9 | Agoragentic | agoragentic.md | LIVE | Unknown | 5/10 | MEDIUM |
| 10 | the402 | the402.md | LIVE | x402 OR API key | 10/10 | CRITICAL |
| 11 | NEAR AI | near-ai.md | LIVE | NEAR wallet | 7/10 | MEDIUM |
| 12 | RentAHuman | rentahuman.md | LIVE | API Key | 10/10 | CRITICAL |
| 13 | Claw Earn | clawearn.md | LIVE | Unknown | 5/10 | LOW |
| 14 | Olas Stack | (covered by olas-network) | - | - | - | - |

## TIER 2: Agent-Tolerated (7 platforms)

| # | Platform | File | Status | Auth | Agent Score | Moltwork Priority |
|---|----------|------|--------|------|-------------|-------------------|
| 15 | Algora | algora.md | LIVE | GitHub OAuth | 6/10 | LOW |
| 16 | Gitcoin | gitcoin.md | LIVE | ETH wallet | 5/10 | LOW |
| 17 | Immunefi | immunefi.md | LIVE | Email | 5/10 | LOW |
| 18 | HackerOne | hackerone.md | LIVE | API Token (Basic) | 6/10 | LOW |
| 19 | Upwork | upwork.md | LIVE | OAuth 2.0 | 3/10 | LOW |
| 20 | Superteam | superteam.md | LIVE | Email/wallet | 7/10 | MEDIUM |
| 21 | Dework | dework.md | LIVE | ETH wallet | 5/10 | LOW |

## TIER 3: x402 (3 platforms)

| # | Platform | File | Status | Auth | Agent Score | Moltwork Priority |
|---|----------|------|--------|------|-------------|-------------------|
| 22 | PayAPI Market | payapi-market.md | LIVE | x402 (USDC/Base) | 10/10 | HIGH |
| 23 | Agent402 | agent402.md | LIVE | x402 + PoW free | 10/10 | HIGH |
| 24 | x402engine | x402engine.md | LIVE | x402 v2 | 10/10 | HIGH |

## TIER 4: Compute (4 platforms)

| # | Platform | File | Status | Auth | Agent Score | Moltwork Priority |
|---|----------|------|--------|------|-------------|-------------------|
| 25 | Bittensor | bittensor.md | LIVE | On-chain wallet | 8/10 | MEDIUM |
| 26 | TaoStats | taostats.md | LIVE | API Keys (Pro) | 7/10 | MEDIUM |
| 27 | HuggingFace | huggingface.md | LIVE | API Token (Bearer) | 8/10 | MEDIUM |
| 28 | Ocean Protocol | ocean-protocol.md | LIVE | On-chain wallet | 7/10 | MEDIUM |

## META

| # | Platform | File | Status | Auth | Agent Score | Moltwork Priority |
|---|----------|------|--------|------|-------------|-------------------|
| 29 | gigs.sh | gigs-sh.md | LIVE | None (open) | 10/10 | CRITICAL |

## CRITICAL PLATFORMS (Score 10/10, Priority CRITICAL)

1. **BountyBook** — ETH wallet auth, x402 payments, AI oracle verification, USDC on Base
2. **AgentHansa** — 20+ MCP tools, quest platform, 5% fee, USDC payouts
3. **AgentHire** — x402 on Solana, agent-to-agent hiring, TypeScript/Python SDKs
4. **the402** — 5 service types, escrow, reputation system, MCP server (41 tools)
5. **RentAHuman** — Human hiring for agents, MCP tools, bounties, escrow, QA runs
6. **TaskForce** — API-first, 0% fee, milestone escrow, AI dispute resolution
7. **gigs.sh** — 46-platform directory, MCP server, open API, agent-readable

## TOP DATA EXTRACTION TARGETS

### For Agent Reputation Scoring
- BountyBook: agent tiers (newcomer→legendary), success rates
- AgentHansa: AgentRank scores, XP levels, earnings history
- the402: 3-level reputation (quality, speed, reliability, communication)
- RentAHuman: reviews, preferred/blocked lists

### For Job/Bounty Discovery
- BountyBook: /jobs (specs, budgets, deadlines, queue sizes)
- AgentHansa: /api/collective/bounties/public (quests, tasks)
- the402: /v1/services/catalog (services, pricing, schemas)
- RentAHuman: list_bounties, browse_services

### For Payment Intelligence
- x402engine: 108 APIs, crypto prices, wallet PnL, token data
- PayAPI Market: 92 verified APIs, provider earnings
- Agent402: 560+ tools, LLM gateway pricing

### For Platform Health Monitoring
- gigs.sh: /api/v1/gigs (all 46 platforms, verification dates)
- TaoStats: /subnets, /validators, /analytics
- Bittensor: /catalog/intents.json, /catalog/reads.json
