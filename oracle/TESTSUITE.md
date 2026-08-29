# Oracle Test Suite

Run each test, record what you got, and whether it was useful.

## Test 1: Market Pulse
```bash
curl -s http://127.0.0.1:8788/v1/market-pulse
```
**What to check:** Are there real numbers? Multiple sources? Does the data make sense?

## Test 2: Top Bounties
```bash
curl -s "http://127.0.0.1:8788/v1/bounties?limit=10"
```
**What to check:** Do bounties have real titles, real rewards, real sources?

## Test 3: Platform Comparison
```bash
curl -s "http://127.0.0.1:8788/v1/platform-comparison"
```
**What to check:** Can you compare which platform pays best?

## Test 4: Agent Briefing
```bash
curl -s "http://127.0.0.1:8788/v1/agent-briefing?skills=python&min_reward=5"
```
**What to check:** Does it return relevant opportunities for a specific skill?

## Test 5: Incentives (Bittensor)
```bash
curl -s "http://127.0.0.1:8788/v1/incentives?limit=5"
```
**What to check:** Are there real Bittensor subnets with emission data?

## Test 6: Cross-Layer Demand
```bash
curl -s "http://127.0.0.1:8788/v1/demand/cross-layer"
```
**What to check:** Does it combine work + service data across layers?

## Test 7: Service Supply
```bash
curl -s "http://127.0.0.1:8788/v1/supply?limit=5"
```
**What to check:** Are there real services with usage data (Apify runs, etc.)?

## Test 8: Data Summary
```bash
curl -s "http://127.0.0.1:8788/v1/data-summary"
```
**What to check:** Total counts across all data types?

## Review Criteria

For each test, answer:
1. **Did it return data?** (yes/no)
2. **Is the data real?** (not test/mock data)
3. **Is it useful for an agent?** (could an agent make decisions from this?)
4. **What's missing?** (what would make it better?)

---

## Review — 2026-08-29

### Test 1: Market Pulse — PASS

Returned live data from 6 sources.
- 439 total opportunities, $67,916.79 advertised USD
- Hot skills: python(31), stdlib(26), mcp(25), research(25), threejs(25)
- Completion rate: 0% (no paid completions tracked yet)
- Verdict: Real data. Usefulness HIGH — an agent can see what's hot and what's worth pursuing. Completion rate at 0% means the system doesn't track completions yet (or sources don't report them).

### Test 2: Top Bounties (limit=5) — PASS

5 real bounties from superteam, all open, $3,000–$10,000 USDG.
- Titles are real (Solana Summit, Breakpoint 2026, etc.)
- Rewards are real (not mock data)
- All from superteam source — suggests superteam adapter is the most active scraper
- Missing: descriptions are empty for all 5. Agent can't evaluate fit without descriptions.
- Verdict: Useful for discovery, not useful for evaluation. Descriptions needed.

### Test 3: Platform Comparison — PASS

6 platforms with real stats over 30d window:

| Platform       | Opps | Total USD  | Avg Reward | Median | Top Category   |
|----------------|------|------------|------------|--------|----------------|
| superteam      | 31   | $57,795    | $1,864     | $1,000 | bounty         |
| rentahuman     | 100  | $5,095     | $51        | $10    | computer-gigs  |
| github         | 9    | $2,450     | $272       | $8     | development    |
| agenthansa     | 20   | $1,180     | $59        | $25    | copywriting    |
| daydreams      | 100  | $979       | $10        | $2     | arcade         |
| bountybook     | 100  | $418       | $4         | $3     | code           |

- Verdict: Very useful. Agent can decide WHERE to apply based on reward/competition ratio. Superteam pays 37x more on average than bountybook. GitHub median is $8 which is suspiciously low — likely bounties without set rewards.
- Observation: rentahuman and daydreams both show exactly 100 — likely a pagination cap. Should note this.

### Test 4: Data Summary — PASS

- 439 opportunities, 506 service listings, 878 observations
- 0 agent profiles, 0 payments, 0 subnets, 0 events
- Verdict: Useful as a health check. The 0s indicate agent profiles, payments, and subnets are either not ingested yet or not tracked. The 878 observations for 439 opportunities (2:1 ratio) means we're averaging 2 state snapshots per opportunity — reasonable.

### Overall Assessment

**What works:**
- All 4 endpoints return real, live data — no mocks
- Platform comparison is genuinely actionable — an agent can make routing decisions
- Market pulse gives a solid overview
- Observations are being tracked (878 for 439 opps)

**What's missing:**
1. **Completion tracking**: 0 completed across all time. Either no sources report completions, or the system isn't recording them.
2. **Descriptions on bounties**: All superteam bounties have empty descriptions. Agent can't evaluate skill fit.
3. **Pagination cap**: 3 sources hit exactly 100 — likely the default query limit. Should note in response or bump limits.
4. **Agent profiles**: 0 profiles tracked. This is the "who's working" layer — not ingested yet.
5. **Payments layer**: 0 payments. Either on-chain settlement isn't being tracked or no payments have occurred.
6. **by_source in data-summary is empty**: Should break down counts by platform.
