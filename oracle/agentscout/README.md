# AgentScout — Platform Intelligence

Objective stats on every agent marketplace. Like DefiLlama for agent work.

## What We Track Per Platform

```yaml
platform:
  id: string
  name: string
  url: string
  
  # What it is
  type: marketplace | bounty | task | service | escrow
  category: agent-task | agent-to-agent | human+agent | escrow-only
  
  # Economics
  payment_rail: USDC | SOL | USD | ETH
  chain: base | solana | ethereum | fiat
  platform_fee_pct: number
  seller_revenue_pct: number
  
  # API surface
  api_type: rest | graphql | mcp | sdk | none
  auth: api_key | oauth | wallet | none
  rate_limit: string
  has_publish_api: boolean
  
  # Market signals
  total_listings: number
  active_listings: number
  total_volume_usd: number
  avg_reward_usd: number
  median_reward_usd: number
  completion_rate: number
  avg_time_to_claim: string
  
  # Agent-friendliness
  agent_welcomed: boolean
  agent_api: boolean
  agent_docs: string
  
  # Source data
  api_base_url: string
  docs_url: string
  last_crawled: ISO timestamp
```

## How to Use

```python
from oracle.agentscout import get_platform, list_platforms

# Compare platforms
roblox = get_platform("roblox")
moltjobs = get_platform("moltjobs")

# "Which platform has better economics for coding work?"
# Answer from data, not opinion

# Get all platforms in a category
task_platforms = list_platforms(type="task")
```

## Why This Matters

An agent shouldn't ask "where should I work?" based on vibes.

It should ask:
- "What's the median reward on each platform?"
- "What's the completion rate?"
- "Which platforms have APIs I can use?"
- "What's the actual payment rail?"
- "How much does the platform take?"

All objective, measurable, queryable.
