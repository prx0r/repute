# x402engine

- **URL**: https://x402engine.app
- **Status**: LIVE
- **Category**: x402 / Multi-API Gateway
- **API Base URL**: https://x402engine.app
- **Auth Method**: x402 v2 micropayments (USDC on Base/Solana, USDm on MegaETH)
- **Agent-Friendliness Score**: 10/10
- **Priority for Moltwork**: HIGH

## Available Endpoints

### Discovery (Free)
- `GET /.well-known/x402.json` — Full discovery document
- `GET /api/services` — List all services
- `GET /api/services/:id` — Service details
- `GET /.well-known/agent-card.json` — A2A agent card
- `GET /openapi.json` — OpenAPI 3.1 spec
- `GET /health` — Health check

### Crypto & Blockchain
- `GET /api/crypto/price` — $0.001 (CoinGecko prices)
- `GET /api/crypto/markets` — $0.002 (market rankings)
- `GET /api/crypto/history` — $0.003 (historical data)
- `GET /api/crypto/trending` — $0.001 (trending coins)
- `GET /api/crypto/search` — $0.001 (coin search)
- `POST /api/wallet/balances` — $0.005 (token balances, 20+ chains)
- `POST /api/wallet/transactions` — $0.005 (tx history)
- `POST /api/wallet/pnl` — $0.01 (realized/unrealized PnL)
- `POST /api/token/prices` — $0.005 (DEX token prices)
- `GET /api/token/metadata` — $0.002 (token metadata)
- `GET /api/ens/resolve` — $0.001 (ENS → address)
- `GET /api/ens/reverse` — $0.001 (address → ENS)

### Compute
- `POST /api/image/fast` — $0.015 (FLUX Schnell)
- `POST /api/image/quality` — $0.05 (FLUX.2 Pro)
- `POST /api/image/text` — $0.12 (Ideogram v3)
- `POST /api/image/face-swap` — $0.08 (FLUX PuLID)
- `POST /api/image/nano-banana` — $0.10 (Google Nano Banana 2)
- `POST /api/video/fast` — $0.55 (Kling V3 Standard)
- `POST /api/video/quality` — $0.70 (Kling V3 Pro)
- `POST /api/video/hailuo` — $0.65 (MiniMax Hailuo 2.3 Pro)
- `POST /api/video/animate` — $0.70 (image to video)
- `POST /api/code/run` — $0.005 (Python/JS/Bash/R sandbox)
- `POST /api/transcribe` — $0.10 (Deepgram Nova-3)

### LLM & AI (72 models)
- `POST /api/llm/{model}` — $0.002-$0.30 per call
- Models: GPT-4o, Claude Opus/Sonnet/Haiku, Gemini, DeepSeek, Llama, Grok, Qwen, Mistral, Perplexity, Kimi, MiniMax, GLM, Cohere, and more

### Storage
- `POST /api/ipfs/pin` — $0.01 (Pinata)
- `GET /api/ipfs/get` — $0.001 (retrieve from IPFS)

### Web
- Web scrape, screenshot, search, content fetch endpoints

## MCP Server
- `claude mcp add x402 -- npx -y x402engine-mcp`

## Payment Networks
- Base (eip155:8453) — USDC, Permit2 gasless
- Solana — USDC via CDP facilitator
- MegaETH (eip155:4326) — USDm, ~10ms confirmations

## What Oracle Can Extract
- Full service catalog with pricing across 108 APIs
- Crypto market data (prices, volumes, PnL)
- Token metadata and balances
- Image/video generation capabilities
- LLM model availability and pricing
- IPFS storage metrics

## Rate Limits
- Free endpoints: /health, /.well-known/*, /api/discover, /api/services
- Paid: per-request x402 micropayments


## Real API Response Samples (Crawled 2026-08-28)

### API Root
```
FETCH ERROR: <urlopen error [SSL: TLSV1_UNRECOGNIZED_NAME] tlsv1 unrecognized name (_ssl.c:1081)>
```

