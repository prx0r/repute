# Oracle Sources — Master Index

## Source Comparison Matrix

| Source | Type | API | Auth | Payment | Agent-native | Data Richness | Priority |
|--------|------|-----|------|---------|-------------|---------------|----------|
| [MoltJobs](moltjobs.md) | Job marketplace | REST | API Key | USDC/Base | Yes (28 MCP tools) | ★★★★★ | HIGH |
| [TaskForce](taskforce.md) | Task marketplace | REST | API Key | USDC/Solana+Base | Yes | ★★★★☆ | HIGH |
| [BountyBook](bountybook.md) | Bounty marketplace | REST | Wallet sig | USDC/Base (x402) | Yes | ★★★★☆ | HIGH |
| [Algora](algora.md) | OSS bounties | REST (public) | None | USD (fiat) | Yes | ★★★★☆ | HIGH |
| [GitHub](github.md) | Issue tracker | REST | OAuth | Varies | Yes | ★★★★★ | HIGH |
| [SuperTeam](superteam.md) | Solana bounties | REST | API Key | USDC/SOL | Partial | ★★★☆☆ | MEDIUM-HIGH |
| [8004scan](8004scan.md) | Agent registry | REST | None | On-chain | Yes | ★★★☆☆ | MEDIUM-HIGH |
| [ClawGig](clawgig.md) | Agent marketplace | TBD | TBD | USDC | Yes | ★★☆☆☆ | MEDIUM |
| [x402 Bazaar](x402-bazaar.md) | API marketplace | REST | None | USDC (x402) | Yes | ★★☆☆☆ | MEDIUM |
| [TryBounty](trybounty.md) | Task marketplace | REST | — | USDC (escrow) | Yes | ★★★☆☆ | MEDIUM |
| [Olas/Mech](olas.md) | Agent-to-agent bazaar | SDK | — | OLAS/USDC multi-chain | Yes | ★★★★★ | HIGH |
| [Immunefi](immunefi.md) | Security bounties | Crawl | None | USD/Crypto | Partial | ★★★☆☆ | MEDIUM |

## Data Fields Cross-Reference

### Universal Fields (available from most sources)
- `id` — native identifier
- `title` — listing title
- `description` — full text
- `status` — lifecycle state
- `reward` — advertised payment
- `created_at` — when posted
- `buyer_id` — who posted
- `worker_id` — who claimed/completed

### Skills/Categories
| Source | Skills Signal |
|--------|--------------|
| MoltJobs | `vertical`, `skills_required` |
| TaskForce | `category`, `skills_required` |
| BountyBook | `job_type`, `tags` |
| Algora | `repo.language`, `issue.labels` |
| GitHub | `labels`, `repo.language` |
| SuperTeam | `category`, `skills_required` |
| 8004scan | `capabilities`, `type` |
| Immunefi | `finding.category`, `assets` |

### Payment Verification Levels
| Source | Advertised | Escrow | On-chain | Verified |
|--------|-----------|--------|----------|----------|
| MoltJobs | ✓ | ✓ | ✓ USDC | ✓ |
| TaskForce | ✓ | ✓ | ✓ USDC | ✓ |
| BountyBook | ✓ | ✓ x402 | ✓ USDC | ✓ oracle |
| Algora | ✓ | — | — | ✓ fiat |
| GitHub | ✓ | — | — | — |
| SuperTeam | ✓ | — | — | Partial |
| 8004scan | — | — | ✓ | ✓ |
| Immunefi | ✓ | — | — | ✓ platform |

### Lifecycle Events
| Source | Posted | Claimed | Submitted | Completed | Paid |
|--------|--------|---------|-----------|-----------|------|
| MoltJobs | ✓ | ✓ | ✓ | ✓ | ✓ |
| TaskForce | ✓ | ✓ | ✓ | ✓ | ✓ |
| BountyBook | ✓ | ✓ | ✓ | ✓ oracle | ✓ |
| Algora | ✓ | — | — | ✓ awarded | ✓ |
| GitHub | ✓ | — | — | ✓ closed | — |
| SuperTeam | ✓ | — | ✓ | ✓ awarded | ✓ |
| Immunefi | ✓ | — | ✓ | ✓ resolved | ✓ |

## Adapter Implementation Priority

### Phase 1 (Build First)
1. **GitHub** — rawest data, public API, everyone references it
2. **Algora** — public API, no auth, rich OSS bounty data
3. **MoltJobs** — richest agent marketplace API
4. **BountyBook** — x402-native, oracle-verified completions
5. **Olas/Mech** — 700K+ monthly txns, agent-to-agent commerce

### Phase 2 (Build Second)
6. **TaskForce** — 0% fee marketplace, milestone tracking
7. **TryBounty** — a16z backed, oracle-verified, diverse tasks
8. **NEAR AI Agent Market** — full SDKs, SSE streaming
9. **Clustly** — single-POST registration, MCP native
10. **AgentHansa** — REST + llms-full.txt, multiple earning channels
11. **SuperTeam** — large Solana ecosystem
12. **8004scan** — agent registry/reputation data

### Phase 3 (Build Third)
13. **Daydreams TaskMarket** — 5 task modes, on-chain
14. **AgentHire** — x402 payments, 30+ capabilities
15. **Agoragentic** — trust routing, settlement
16. **the402** — 41 MCP tools, request posting
17. **RentAHuman** — physical-world tasks
18. **Claw Earn** — on-chain escrow, staking
19. **dealwork.ai** — purpose-built for agents, 3% fee

### Phase 4 (Build When Needed)
20. **Gitcoin** — DAO bounties + grants
21. **Immunefi** — security bounty economics
22. **HackerOne** — bug bounty reports
23. **Upwork** — largest freelance platform (MCP server)
24. **Dework** — DAO bounty aggregation
25. **Bittensor** — subnet mining, TAO emissions

### Phase 5 (Infrastructure)
26. **gigs.sh** — meta-directory of 46 platforms
27. **PayAPI Market** — x402 API directory
28. **Agent402** — 560+ tools index
29. **x402engine** — 108 pay-per-call endpoints

## Source Adapter Contract

```python
class SourceAdapter(Protocol):
    id: str
    name: str
    
    async def discover(self) -> list[RawOpportunity]:
        """Fetch all available opportunities from this source."""
        ...
    
    async def normalize(self, raw: RawOpportunity) -> Opportunity:
        """Convert raw data to canonical Opportunity format."""
        ...
    
    async def refresh(self, opp: Opportunity) -> Observation | None:
        """Check if an existing opportunity has changed state."""
        ...
    
    def health_check(self) -> bool:
        """Verify the source API is reachable."""
        ...
```

## Usage

```python
from oracle.sources import SourceRegistry

registry = SourceRegistry()
registry.register(MoltJobsAdapter())
registry.register(AlgoraAdapter())
registry.register(GitHubAdapter())

# Ingest from all sources
for adapter in registry.active():
    items = await adapter.discover()
    for raw in items:
        opp = await adapter.normalize(raw)
        store.append(opp)
```
