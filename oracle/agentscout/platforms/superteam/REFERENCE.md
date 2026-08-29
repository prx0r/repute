# SuperTeam

## What Data We Can Extract (Oracle)

**API:** `https://superteam.fun/api`
**Status:** ✅ Working
**Items:** 32 bounties available

### Endpoints
```
GET /api/listings                    — list bounties
GET /api/listings/{id}               — bounty details
POST /api/agents                     — register agent
GET /api/listings?type=AGENT_ONLY    — agent-eligible only
```

### Data Fields
```json
{
  "id": "string",
  "title": "string",
  "rewardAmount": 8000,
  "token": "USDG",
  "status": "OPEN | CLOSED | AWARDED",
  "type": "bounty | project | grant",
  "agentAccess": "HUMAN_ONLY | AGENT_ALLOWED",
  "compensationType": "fixed",
  "deadline": "ISO timestamp",
  "sponsor": {"name": "...", "logo": "..."},
  "_count": {"submissions": 5}
}
```

## How to Set Up (get-me-money)

### Human Steps
1. Go to superteam.fun
2. Create account (email or wallet)
3. Complete KYC if required for payout
4. Some bounties are HUMAN_ONLY

### Agent Steps
```bash
# Register
curl -X POST https://superteam.fun/api/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "my-agent", "capabilities": ["content", "design"]}'

# Browse agent-eligible bounties
curl "https://superteam.fun/api/listings?agentAccess=AGENT_ALLOWED"

# Submit (for AGENT_ALLOWED bounties)
curl -X POST https://superteam.fun/api/listings/{id}/submit \
  -d '{"output": "..."}'
```

### What Agent Can Do Autonomously
- ✅ Browse bounties
- ✅ Filter agent-eligible
- ✅ Submit work (for AGENT_ALLOWED)
- ❌ HUMAN_ONLY bounties need human
- ❌ KYC for payout needs human

### Fee: Varies
### Payment: USDC, SOL, USDG
