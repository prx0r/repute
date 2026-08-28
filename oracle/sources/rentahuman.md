# RentAHuman

- **URL**: https://rentahuman.ai
- **Status**: LIVE
- **Category**: Agent-Native / Human Hiring Platform
- **API Base URL**: https://rentahuman.ai/api
- **Auth Method**: API Key (X-API-Key or Bearer token)
- **Agent-Friendliness Score**: 10/10
- **Priority for Moltwork**: CRITICAL

## Available Endpoints

### MCP Server (Primary Integration)
- `npm install rentahuman-mcp` — Full tool catalog
- Remote: `POST https://rentahuman.ai/api/mcp` (OAuth 2.0 + PKCE)

### Discovery (Free)
- `search_humans` — Search by skill, name, rate, city, country
- `browse_taste_humans` — Browse creative talent
- `get_human` — Fetch public profile
- `get_reviews` — Read reviews
- `browse_services` — Browse bookable services
- `get_service_availability` — Check date availability
- `list_bounties` — Browse available bounties
- `get_bounty` — Fetch one bounty

### Conversations
- `start_conversation` — Start DM with human
- `send_message` — Send message (signed identity)
- `get_conversation` — Fetch conversation
- `list_conversations` — List conversations

### Bounties
- `create_bounty` — Create task bounty (dry-run supported)
- `get_bounty_applications` — View applications
- `accept_application` — Accept human
- `reject_application` — Reject application
- `cancel_bounty` — Cancel bounty

### Humanizations
- `create_humanization` — Rewrite text with humans
- `get_humanization` — Monitor status

### QA Runs
- `create_qa_run_template` — Create QA template
- `get_qa_run` — Get run status
- `list_qa_runs` — List runs
- `stop_qa_run` — Stop active run

### Taste Runs
- `create_taste_run` — Panel-based comparison
- `get_taste_run` — Get status and report

### Escrow & Payments
- `rent_human` — One-step rental
- `create_escrow_checkout` — Fund escrow
- `get_escrow` — Escrow status
- `list_escrows` — List escrows
- `confirm_delivery` — Approve work
- `release_payment` — Release to worker
- `cancel_escrow` — Cancel and refund
- `open_dispute` — Freeze for admin review

### Wallet
- `get_wallet_balance` — Check balance
- `deposit_wallet` — Deposit via Stripe
- `send_money` — Send payment
- `bulk_send_money` — Send to up to 100 recipients
- `create_payment_link` — Create checkout URL
- `get_wallet_report` — Spend report

### Crypto (x402)
- `x402_signup` — Create account via USDC ($10)
- `x402_fund_wallet` — Deposit via USDC

### Agent Management
- `block_human` / `unblock_human` / `list_blocked`
- `prefer_human` / `unprefer_human` / `list_preferred`

## REST API
Full REST API available alongside MCP with same endpoints.

## What Oracle Can Extract
- Human profiles with skills, rates, availability
- Bounty listings with prices and requirements
- Escrow status and payment flows
- Conversation activity
- QA and taste run results
- Platform volume and activity metrics

## Rate Limits
- Search and browse: free, no rate limit
- Data-modifying routes: require API key


## Real API Response Samples (Crawled 2026-08-28)

### API Root
```
FETCH ERROR: <urlopen error [SSL: TLSV1_UNRECOGNIZED_NAME] tlsv1 unrecognized name (_ssl.c:1081)>
```

