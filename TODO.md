# Repute TODOs — Live Product

## 1. Fix chunking (text too short = 1 chunk)
Make chunking work with shorter texts. Split at sentence/paragraph level, target 5-20 chunks per asset.

## 2. Fix server.py publish flow
The publish endpoint works but the inspect flow breaks because assets only get 1 chunk. Fix the chunking integration.

## 3. Add x402 payment endpoint
POST /api/pay/{asset_id} — buyer pays USDC via x402 batch settlement. Track payments in ledger.

## 4. Add reputation tracking
Track: sample→unlock conversion, repeat buyers, refund rate, buyer diversity. Compute Bayesian score per worker.

## 5. Add worker storefront pages
GET /workers/{id} — profile with: specialties, assets, revenue, conversion rates, reputation badges.

## 6. Add search + discovery
GET /api/search?q=x402 — text search across assets. GET /api/demand — unserved demand signals.

## 7. Add bounty pool mechanic
POST /api/pools — buyer creates $15 pool. Workers submit sealed. Buyer reveals multiple.

## 8. Add auto-refund for delivery failure
If artifact hash mismatch, decryption fails, or timeout → automatic refund.

## 9. Add SQLite persistence
Replace in-memory dicts with SQLite. Survive restarts.

## 10. Deploy + test with real wallet
Deploy to port 8788 on VPS. Create test asset. Walk through full buy flow.
