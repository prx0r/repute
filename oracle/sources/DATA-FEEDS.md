# Oracle Data Feeds — 20 Best Sources

## The Three Feeds

```
WORK              CAPABILITY SUPPLY    MARKET DEMAND
BountyBook        Apify               x402 transactions
AgentHansa        MCP Registry        Apify usage
the402            Smithery            npm/PyPI downloads
gigs.sh           Coinbase Bazaar     search volume
Dune              OpenRouter          HN/StackExchange pain
```

## Priority A+++ (Wire First)

### 1. Apify Store
- API: https://api.apify.com/v2/store
- Docs: https://docs.apify.com/api/v2
- Data: totalRuns, totalUsers, 7/30/90d users, reviews, ratings, bookmarks
- Signal: Revealed capability demand

### 2. Coinbase Bazaar
- API: https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources
- Docs: https://docs.cdp.coinbase.com/api-reference/v2/rest-api/x402-facilitator/list-x402-resources
- Data: resource, price, payee, network, l30DaysTotalCalls, l30DaysUniquePayers
- Signal: Actual x402 demand

### 3. Agent402.tools Index
- API: https://agent402.tools/api/index
- Docs: https://agent402.tools/docs
- OpenAPI: https://agent402.tools/openapi.json
- Data: seller, endpoint, price, health, settled calls, USD volume
- Signal: Actual x402 demand

### 4. Agent402 Leaderboard
- API: https://agent402.tools/api/leaderboard
- Data: callsSettled, totalUsd, uniqueBuyers by seller
- Signal: On-chain verified demand

### 5. Dune
- API: https://api.dune.com/api/v1/sql/execute
- Docs: https://docs.dune.com/api-reference/overview/getting-started
- Data: Raw x402/ERC-8004 transactions, buyers, sellers, volumes
- Signal: Ground-truth on-chain demand

### 6. the402
- API: https://api.the402.ai/v1/services/catalog
- Docs: https://the402.ai/docs/
- Data: services, prices, provider reputation, completion rates
- Signal: Direct work + service market

### 7. BountyBook
- API: https://api.bountybook.ai/jobs
- Docs: https://www.bountybook.ai/docs
- Data: bounties, rewards, claims, submissions, verification
- Signal: Direct agent work

### 8. AgentHansa
- API: https://www.agenthansa.com/api
- OpenAPI: https://www.agenthansa.com/openapi.json
- Data: quests, skills, profiles, activity, rewards, earnings
- Signal: Direct work + worker economy

## Priority A++ (Wire Second)

### 9. gigs.sh
- API: https://gigs.sh/api/v1/gigs
- Data: 46+ marketplaces, payment rails, KYC, agent policy, onboarding friction
- Signal: Marketplace discovery

### 10. Smithery MCP Registry
- API: https://api.smithery.ai/servers
- Docs: https://smithery.ai/docs/llms.txt
- Data: server metadata, useCount, verified, deployed state
- Signal: MCP demand

### 11. Official MCP Registry
- API: https://registry.modelcontextprotocol.io/v0.1/servers
- Data: server name, description, packages, versions
- Signal: Canonical capability supply

### 12. Hugging Face Hub
- API: https://huggingface.co/api/models
- OpenAPI: https://huggingface.co/.well-known/openapi.json
- Data: models, downloads, likes, tags, pipeline/task
- Signal: AI capability adoption

### 13. OpenRouter
- API: https://openrouter.ai/api/v1/models
- Data: pricing, context, tool support, provider details, popularity
- Signal: Model demand + capability cost

### 14. npm downloads
- API: https://api.npmjs.org/downloads/point/last-week/{package}
- Docs: https://github.com/npm/registry/blob/main/docs/download-counts.md
- Data: daily/weekly/monthly downloads for any package
- Signal: Developer capability adoption

### 15. GitHub REST
- API: https://api.github.com
- Docs: https://docs.github.com/en/rest
- Data: stars, forks, issues, commits, releases, download counts
- Signal: Supply + pain + adoption

### 16. x402 List
- API: https://x402-list.com/api/v1/services
- Data: service telemetry, uptime, pricing
- Signal: x402 service quality

### 17. x402engine
- API: https://x402engine.app/api/services
- Data: 108 pay-per-call APIs
- Signal: x402 capability supply

### 18. Valoria
- API: https://valoria.net/api/stats
- Data: market intelligence, derived scores
- Signal: Cross-cutting demand analysis

## Priority A+ (Wire Third)

### 19. PyPIStats
- API: https://pypistats.org/api/packages/{package}/recent
- Data: daily/weekly/monthly downloads
- Signal: Python agent-tool adoption

### 20. Hacker News
- API: https://hn.algolia.com/api/v1/search_by_date
- Data: Ask HN, Show HN, comments, points
- Signal: Emerging pain/demand

## Priority A (Wire Later)

### 21. Stack Exchange
- API: https://api.stackexchange.com/docs
- Data: questions, bounties, tag frequencies
- Signal: Persistent technical pain

### 22. DataForSEO
- API: https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live
- Docs: https://docs.dataforseo.com/v3/keywords_data-google_ads-search_volume-live/
- Data: search volume, CPC, advertiser competition
- Signal: Commercial demand

### 23. Similarweb
- API: https://api.similarweb.com/v5/website-analysis/websites/traffic-and-engagement
- Docs: https://docs.similarweb.com/api-v5/guides/available-data
- Data: visits, uniques, engagement, traffic sources
- Signal: Marketplace adoption

### 24. AgentEconomy.to
- Raw JSON: https://agenteconomy.to/data.json
- MCP: https://agenteconomy.to/api/mcp
- Data: x402, ACP, Olas, MPP daily activity
- Signal: Cross-check against own telemetry

### 25. CoinGecko
- API: https://api.coingecko.com/api/v3
- Data: token prices, market caps, volumes
- Signal: Token economics context

### 26. DefiLlama
- API: https://api.llama.fi
- Data: TVL, yields, protocol data
- Signal: DeFi context for x402/Olas

### 27. CoinCap
- API: https://api.coincap.io/v2
- Data: real-time prices, market data
- Signal: Token price feeds

### 28. Chainlink
- API: https://api.chain.link
- Data: oracle price feeds
- Signal: Price reference data

### 29. Etherscan
- API: https://api.etherscan.io/api
- Data: on-chain transactions, contracts
- Signal: Direct on-chain verification

### 30. Algorand Explorer
- API: https://api.algoexplorer.io
- Data: Algorand transactions
- Signal: Algorand x402 activity
