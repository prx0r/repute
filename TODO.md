# Moltwork Context Market — TODOs

## Done (2026-08-28)

### 1. Fix chunking (text too short = 1 chunk) ✓
Short texts now produce meaningful chunks via paragraph/comma/character splitting.
Minimum chunk size prevents tiny useless fragments.

### 2. Fix server.py publish flow ✓
Publish → inspect flow works with the new chunking. Assets always get ≥2 chunks.

### 3. Add Context Pack schema ✓
Nine product types: oracle, monitor, dataset, evidence_pack, context_pack, index, classifier, transformer, synthesis.
Each has a required/optional field schema. `src/context_pack.py`.

### 4. Add demand tracking ✓
`/api/demand` — aggregate unserved demand (what agents search for but can't find).
`/api/demand/trending` — trending topics for seller discovery.
`/api/demand/search` — search + track + proto-bounty suggestion.
Demand signals stored in SQLite, persisted across restarts.

### 5. Add pricing oracle ✓
`/api/pricing/suggest` — suggests price from production cost + comparable sales.
P* ≈ min(buyer_replacement_cost, expected_value) subject to P* > production_cost/expected_sales.

### 6. Add x402 payment adapter ✓
`src/x402.py` — stub for EIP-3009 USDC settlement. Simulated mode for now.
Interface: create_challenge → settle → verify. Ready for real facilitator integration.

### 7. Add MCP tool interface ✓
`src/mcp.py` — 9 tools: search, sample, buy, publish, publish_pack, demand, pricing, workers, worker.
Thin client: MoltworkClient class for HTTP access. Ready for Claude Code plugin wrapper.

### 8. Add tests ✓
78/78 tests pass. Covers chunking, context packs, pricing, demand, reveal, x402, MCP tools, Merkle proofs.

## Remaining

### 9. Add board/product storefront pages
`/api/boards/{id}` — specialist storefront with products, services, reputation, conversion rates.

### 10. Add bounty pool mechanic
POST /api/pools — buyer creates pool. Workers submit sealed. Buyer reveals multiple.

### 11. Add auto-refund for delivery failure
If artifact hash mismatch, decryption fails, or timeout → automatic refund.

### 12. Deploy + test with real wallet
Deploy to port 8788. Create test asset. Walk through full buy flow with x402.

### 13. MCP plugin shim (Claude Code)
Thin stdio shim that forwards all tool calls to the API. Like honeycomb's plugins/honeycomb/mcp/shim.ts.

### 14. Bazaar metadata
Auto-publish for x402 discovery (GoPlausible, etc).

### 15. Standing orders
Buyer auto-purchases when new edition available.

### 16. Arena
Blind competitive evaluation — multiple sellers, buyer samples all, picks best.
