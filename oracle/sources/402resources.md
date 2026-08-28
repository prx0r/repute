# x402 Intelligence Stack — Complete Source Reference

## Data Categories

```text
DISCOVERY           What services exist?
TELEMETRY           Who is actually getting paid?
QUALITY             Does the endpoint work?
DEMAND              Are independent buyers returning?
COMPETITION         How crowded is this category?
PRICING             What do successful providers charge?
TRUST               Is volume organic / suspicious?
CHANGE               What's rising/falling/changing?
```

## Sources (Priority Order)

### P0 — Primary Intelligence

| Source | Best Signal | API | MCP |
|--------|------------|-----|-----|
| **x402watch / PrintMoneyLab** | wash-filtered demand, real-vs-fake traffic | Yes/data exports | Yes |
| **x402 List** | buyer counts, volume, uptime, pricing history | **Excellent** | **Yes** |
| **402radar** | execution quality, price, alternatives | **Excellent** | No |
| **x402scan / Merit** | transactions, buyers, merchants, facilitators | Yes | Yes |
| **Coinbase Bazaar** | canonical discovery + quality ranking | **Excellent** | **Yes** |
| **TOLL·402** | massive catalog + verification/provenance | **Excellent** | **Yes** |

### P1 — Derived Intelligence

| Source | Best Signal | API | MCP |
|--------|------------|-----|-----|
| **Valoria** | market/revenue/category intelligence | Yes | Yes |
| **Signal402** | curated ecosystem + categories | Limited | Yes |
| **402 Index** | cross-rail L402/x402/MPP catalog | Yes | Yes |

### P2 — Operational

| Source | Best Signal | API | MCP |
|--------|------------|-----|-----|
| **x402.watch** | facilitator/seller uptime and latency | Unclear | UI/docs |

### Research Seed

| Source | Best Signal | Notes |
|--------|------------|-------|
| **402Pilot** | routing methodology | Dataset/code, not live API |
| **x402-trust** | change monitoring | MCP for ongoing monitoring |

---

## 1. x402watch / PrintMoneyLab

**URL:** https://x402.printmoneylab.com
**Methodology:** https://x402.printmoneylab.com/docs/methodology

Classifies buyer/seller activity:
- organic_user, ai_agent, exchange_user, analytics_bot, verifier
- developer, self_test, suspected_wash, owner_test

Excludes non-demand traffic from "real volume."

Category pages expose:
```text
services in category, 24h volume, 24h transactions, real volume %,
price, 30d transactions, real %
```

Ingest:
```text
service_id, seller, category, price, tx_24h, tx_30d, volume_24h,
real_volume_pct, buyer_label_distribution, seller_flags, network, timestamp
```

**Primary "organic demand" source.**

---

## 2. x402 List

**URL:** https://x402-list.com
**API:** https://x402-list.com/api
**OpenAPI:** https://x402-list.com/openapi.json
**MCP:** https://mcp.x402-list.com/mcp (or `npx -y x402-list-mcp`)

MCP tools:
```text
x402_search_services, x402_get_service, x402_find_best_service,
x402_check_health, x402_facilitator_volumes, x402_change_events,
x402_assess_services
```

Per-service telemetry:
```text
/api/v1/services/{slug}/price
/api/v1/services/{slug}/scores
/api/v1/services/{slug}/volume
/api/v1/services/{slug}/buyers
```

Traction record:
```text
30d volume, distinct buyers, buyer concentration,
first settlement, all-time volume, median settlement,
max settlement, facilitators used
```

---

## 3. 402radar

**URL:** https://402radar.io
**API:** https://api.402radar.io

Endpoints:
```text
GET /v1/radar/services
GET /v1/radar/services/:id
GET /v1/radar/categories
GET /v1/radar/compare
GET /v1/radar/alternatives
```

Result includes:
```text
score, scoreConfidence, latencyP95Ms, uptimePct,
medianPriceCredits, sampleCount, syntheticCount
```

Score combines: uptime, success rate, latency, price, freshness.
Confidence tracked separately.

---

## 4. x402scan / Merit

**URL:** https://www.x402scan.com
**API:** https://merit.systems/developers
**GitHub:** https://github.com/Merit-Systems/x402scan

Tracks: resources, transactions, buyers, merchants, facilitators, Base, Solana

Paid API endpoints:
```text
GET /api/x402/buyers
GET /api/x402/merchants
GET /api/x402/resources
GET /api/x402/resources/search
GET /api/x402/facilitators
GET /api/x402/facilitators/stats
GET /api/x402/wallets/:address/stats
GET /api/x402/merchants/:address/stats
```

Cost: ~$0.01/query, $0.02/search

---

## 5. Coinbase Bazaar

**Search API:** https://api.cdp.coinbase.com/platform/v2/x402/discovery/search
**MCP:** https://api.cdp.coinbase.com/platform/v2/x402/discovery/mcp

MCP tools: search_resources, proxy_tool_call

Returns:
```text
description, input/output schema, price/payment terms,
network, asset, payTo, resource URL, quality/relevance data
```

Per-listing fields:
```text
quality.l30DaysTotalCalls
quality.l30DaysUniquePayers
```

**Canonical raw source.**

---

## 6. TOLL·402

**URL:** https://toll402.com
**API:** https://toll402.com/api/v1/resources
**MCP:** https://toll402.com/mcp

Stats: ~98,727 resources, 3,917 providers, 21,852 live checks

MCP tools:
```text
search_services, get_resource, compare_resources,
get_connection_recipe, check_current_quote, report_listing_issue
```

Bulk datasets with: resource IDs, source provenance, quote outcomes, curation state, payment metadata.

**Huge recall-oriented catalog.**

---

## 7. Valoria

**URL:** https://valoria.net
**Market Intel:** https://x402.valoria.net
**MCP:** https://valoria.net/mcp

Free API:
```text
GET /api/stats
GET /search?q=defi
GET /api/domain/{domain}
```

Paid intelligence:
```text
POST /intelligence/pulse
POST /intelligence/analyze
POST /intelligence/opportunities
POST /intelligence/market
```

Calculates: Demand, Competition, Margin, Growth scores.

Exposes: category revenue, service revenue, payment count, competitors, price distributions, market gaps, emerging categories, concentration.

**Treat as derived intelligence, not ground truth.**

---

## 8. Signal402

**URL:** https://signal402.com
**MCP:** `npx signal402-mcp`

Monitors hundreds of curated services in categories:
```text
AI, Data, Media, Tools, Infrastructure
```

With status, price, endpoint info, confidence labels.
Refreshes every 6 hours from editorial research + Coinbase Bazaar.

Best for: human-curated descriptions, category normalization, service validation.

---

## 9. 402 Index

**API:** https://402index.io/api/v1
**MCP:** `npm install -g @402index/mcp-server`

Indexes multiple payment rails: x402, L402, MPP.

```text
GET /api/v1/services (search/filter/sort/pagination)
```

---

## 10. x402-trust MCP

**GitHub:** https://github.com/JonasFuchss/x402-trust-mcp

Tools: trust scoring, bulk endpoint scoring, similar-service lookup,
change monitoring, price-change detection, payTo change, spec regression,
liveness monitoring.

Can monitor endpoints for 30 days with append-only event stream.

---

## 11. AgentCash

**Docs:** https://agentcash.dev/docs/how-it-works
**Discovery:** https://agentcash.dev/discovery

Agent runtime for: OpenAPI discovery, x402 fallback, price inspection,
payment, retry.

Use as Oracle probe wallet:
```text
Oracle finds interesting endpoint
→ AgentCash buys one sample
→ measure output quality
→ store evidence
```

---

## Killer Oracle Metrics

| Metric | Formula | Why It Matters |
|--------|---------|----------------|
| organic_demand | unique_repeat_buyers × wash_confidence × tx_growth | Real demand vs noise |
| market_saturation | working_services / organic_category_spend | Supply vs demand |
| revenue_per_competitor | category_revenue / active_providers | What to build |
| buyer_concentration | $500 from 300 buyers vs $50K from 1 wallet | Quality of demand |
| price elasticity | price_change vs subsequent_volume | Pricing strategy |
| survival | % services alive/working/paid after 7/30/90d | Durability |
| agent_share | agent_buyer_pct from PrintMoneyLab labels | Ecosystem stat |

## Three Evidence Layers

```text
OBSERVED MARKET    — directories + chain data
MEASURED MARKET    — health / latency / prices / wash filtering
EXPERIENCED MARKET — Moltwork actually paid for it and evaluated the result
```

The third layer is the moat. No existing explorer can say:
"We bought this endpoint 417 times, it cost $3.82, succeeded 98.1%, and improved downstream acceptance by 6.4%."
