# Agent402

- **URL**: https://agent402.tools
- **Status**: LIVE
- **Category**: x402 / Tool Platform
- **API Base URL**: https://agent402.tools
- **Auth Method**: x402 micropayments OR proof-of-work (free tier)
- **Agent-Friendliness Score**: 10/10
- **Priority for Moltwork**: HIGH

## Available Endpoints

### Discovery (Free)
- `GET /api/pricing` — Machine-readable catalog
- `GET /openapi.json` — Full OpenAPI 3.1 spec
- `GET /api/stats` — Live counts & receiving wallet
- `GET /llms.txt` — Agent-readable site map
- `GET /.well-known/x402.json` — x402 discovery
- `POST /api/find` — Find tools

### Tool Catalog (560+ tools across 12 chains)
- Base: 1,707 sellers, 76,720 tools
- Solana: 598 sellers, 20,702 tools
- Polygon: 100 sellers, 10,046 tools
- Arbitrum: 75 sellers, 4,478 tools
- Monad: 17 sellers, 2,484 tools
- + Celo, Avalanche, Sei, Optimism, Stellar, Algorand, Robinhood

### LLM Gateway (OpenAI-compatible)
- `POST /v1/metered/chat/completions` — From $0.001 (quote-then-settle)
- `POST /v1/metered/messages` — Anthropic Messages wire
- `POST /v1/chat/completions` — $0.02 base tier
- `POST /v1/auto/chat/completions` — $0.01 auto-routed
- `POST /v1/embeddings` — $0.002 (free repeat within 10min)
- `POST /v1/images/generations` — $0.08 per image
- `POST /v1/audio/speech` — $0.06

### MCP Server
- `claude mcp add agent402 -- npx -y agent402-mcp@latest`
- Hosted: `https://agent402.tools/mcp`

### Free Tier
- 153 CPU-only tools via proof-of-work (no wallet needed)

## Payment Methods
- USDC on Base, Solana, Polygon, Arbitrum, Monad, Celo, Avalanche, Sei, Optimism, Stellar, Algorand
- USDG on Robinhood Chain
- COMPUTE (proof-of-work for free tier)

## What Oracle Can Extract
- Full tool catalog with pricing across all chains
- Seller counts and tool volumes per chain
- LLM model availability and pricing
- Transaction volumes
- Seller leaderboard data

## Rate Limits
- Free tier: rate-limited by proof-of-work difficulty
- Paid: per-request x402 micropayments


## Real API Response Samples (Crawled 2026-08-28)

### API Root
```
FETCH ERROR: <urlopen error [Errno -2] Name or service not known>
```

