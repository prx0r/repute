# Crypto-Agent Ecosystems — Architecture & Integration Plan

## Core Insight

> **Every Moltwork opportunity = economic contract + execution protocol**

## Five Machine-Work Markets

```
1. WORK          Bounties, jobs, tasks
                 NEAR, Virtuals, OpenServ, BountyBook, AgentHansa

2. SERVICE       Capability → paid per use
                 Olas Mechs, Virtuals ACP, x402, Nevermined

3. INCENTIVE     Best implementation → earn emissions
                 Bittensor (129 subnets), Allora, FLock

4. RESOURCE      Compute/infrastructure → paid
                 Akash, Nosana, Morpheus, Phala

5. TRUST         Identity + reputation graph
                 ERC-8004, Phala attestations
```

## Universal OpportunitySpec

```json
{
  "id": "...",
  "source": "...",
  "kind": "bounty|competition|service|emission|resource",

  "requirements": {
    "capabilities": [],
    "deliverables": [],
    "hardware": {},
    "credentials": [],
    "evaluation": {}
  },

  "economics": {
    "reward_model": "fixed|winner_take_all|ranked|proportional|per_call|emission",
    "reward_asset": "...",
    "reward_nominal": null,
    "reward_pool_usd": null,
    "entry_fee_usd": 0,
    "gas_estimate_usd": 0
  },

  "competition": {
    "entries": null,
    "active_workers": null,
    "slots": null,
    "incumbent_score": null
  },

  "execution": {
    "estimated_compute_usd": null,
    "estimated_wall_hours": null,
    "automation_level": "H0|H1|H2|H3|H4",
    "submission_method": "rest|cli|sdk|onchain|service"
  },

  "prediction": {
    "p_entry": null,
    "p_award": null,
    "expected_payout_usd": null,
    "expected_net_usd": null,
    "confidence": null
  }
}
```

## EV Calculation

```
Expected Gross Payout
= Σ P(outcome_i) × payout_i

Expected Net Value
= expected_gross_payout
  - entry_fee
  - gas
  - compute
  - API_cost
  - infrastructure
  - expected_rework_cost
  - capital_risk_cost
  - human_intervention_cost
```

## Human Intervention Taxonomy

| Level | Meaning |
|-------|---------|
| H0 | Fully autonomous after secrets provisioned |
| H1 | One-time human setup; thereafter autonomous |
| H2 | Human approval required per opportunity |
| H3 | Human contributes materially to deliverable |
| H4 | Fundamentally human-only |

## Top 5 Platforms to Integrate

### 1. Bittensor (Incentive Market)
- 129 subnets, each an incentive mechanism
- Ditto SN118: agent memory competition
- SDK: `pip install bittensor`
- Metagraph API: https://api.metagraph.sh
- Taostats: https://api.taostats.io
- **H1** (needs wallet provisioning)

### 2. NEAR Agent Market (Work Market)
- Jobs, bids, agents, reputation, earnings
- API: https://market.near.ai/api-docs/
- OpenAPI: https://market.near.ai/openapi.json
- Real bid → award → delivery → payment data
- **H0** (once wallet exists)

### 3. Virtuals ACP (Service Market)
- Agent-to-agent commerce
- CLI: `acp browse --json`
- SDK: https://github.com/Virtual-Protocol/acp-node-v2
- Sorting: SUCCESSFUL_JOB_COUNT, SUCCESS_RATE, UNIQUE_BUYER_COUNT
- **H1** (signer provisioning)

### 4. Olas Mech (Service Market)
- x402-like services with history
- Client: `pip install mech-client`
- Subgraph: on-chain queries
- **H1** (wallet + funding)

### 5. OpenServ Ideaboard (Demand Signal)
- Ideas → x402 endpoints
- API: https://api.launch.openserv.ai
- No auth for reads
- **H0** (once wallet exists)

## Execution Rails (NOT opportunities)

| Platform | What It Is | Use For |
|----------|-----------|---------|
| Bankr | x402 Cloud hosting | Deploy capabilities |
| Phala | Confidential compute | TEE execution |
| Akash | Decentralized compute | GPU/CPU supply |
| Nosana | GPU marketplace | Inference supply |

## The Full Loop

```
ORACLE discovers opportunity
        ↓
OpportunitySpec
        ↓
  ┌─────┼─────┐
  ▼     ▼     ▼
feasible? EV? strategic?
  └─────┼─────┘
        ↓
     SELECT
        ↓
    PREFLIGHT
        ↓
   BUILD VARIANTS
        ↓
     JUDGE
        ↓
    OUTCOME
        ↓
   EXPERIENCE
```
