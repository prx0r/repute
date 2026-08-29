# QDW Integration — Reference for Other Agent

## What QDW Forge Gives Moltwork

### Asset Model (qdw-forge/models.py)

Already built:
- `CapabilityAsset` — the universal asset schema
- `FactoryCapsule` — worker/recipe with workflow template
- `CapabilityLease` — calls_total, max_spend, allowed_operations
- `InvocationRecord` — cost, verification, timestamps
- `AssetProfile` — empirical reputation (alpha, beta, sample_count)

Asset kinds:
```python
FACTORY, AGENT, TOOL, SKILL, DATA, HUMAN, VERIFIER, SERVICE
```

Transport kinds:
```python
HTTP, MCP, A2A, ESTATE, VANA
```

### What Moltwork Gets From QDW

| QDW Concept | Moltwork Equivalent |
|-------------|---------------------|
| CapabilityAsset | Asset |
| FactoryCapsule | Worker / Recipe |
| CapabilityLease | Lease |
| InvocationRecord | UsageEvent |
| AssetProfile | ReputationProfile |
| BountyEngine | WorkOpportunity |
| HumanOracle | HumanQueue |
| DataRightsBackend | DataRights |

### What NOT To Copy

- `BountyResolver.evaluate_options()` — placeholder values, needs real economics
- UI wholesale — use backend/node concepts, not desktop app
- QDW Estate layer — too specific to QDW's use case

### Key Files to Read

1. `qdw-forge/src/qdw_forge/models.py` — canonical schemas
2. `qdw-forge/src/qdw_forge/leases.py` — leasing mechanics
3. `qdw-forge/src/qdw_forge/invocation.py` — usage tracking
4. `qdw-forge/src/qdw_forge/mcp_server.py` — agent-native access
5. `qdw-sandbox/bounty/` — job/bounty primitives
6. `qdw/core/` — economic router, costs, learning

### Architecture Diagram

```
ORACLE
  ↓ opportunities
QDW SANDBOX (jobs/bounties)
  ↓
QDW CORE (economics/routing)
  ↓
WORKERKIT/HERMES
  ↓ creates useful process
QDW FORGE (assets/skills/leases)
  ↓
MOLTWORK MARKETPLACE
```

## What This Means for WorkerKit

WorkerKit should:
1. Use QDW Forge's `CapabilityAsset` schema for assets
2. Use QDW Forge's `CapabilityLease` for resource allocation
3. Use QDW Forge's `InvocationRecord` for usage tracking
4. Use QDW Core's economic router for cost optimization
5. Use QDW Sandbox's bounty primitives for job normalization

Do NOT rebuild these from scratch.
