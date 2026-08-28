# Bittensor

- **URL**: https://docs.bittensor.com
- **Status**: LIVE
- **Category**: Compute / Decentralized AI Network
- **API Base URL**: Python SDK (`import bittensor`) + CLI (`btcli`)
- **Auth Method**: On-chain wallet (Subtensor)
- **Agent-Friendliness Score**: 8/10
- **Priority for Moltwork**: MEDIUM

## Available Endpoints

### SDK Primitives
- Subtensor: chain interaction
- Wallet: identity and signing
- Balance: TAO token management
- Intents: transaction declarations
- Results: query responses

### Key Operations
- `btcli tools` — List all transaction types
- `bt.intents.list_tools()` — Python API

### Machine-Readable Docs
- `/llms.txt` — Curated index
- `/llms-full.txt` — Full docs corpus
- `/catalog/intents.json` — Every transaction with JSON schema
- `/catalog/reads.json` — Every query with parameters
- `/catalog/errors.json` — Error codes with remediation
- `/code/search.json?q=...` — Search Rust source
- `/code/index.json` — List all code
- `/code/raw/<path>` — Fetch raw source

### Network Roles
- Miners: produce digital commodities
- Validators: score miners
- Subnet creators: define incentive mechanisms
- Stakers: back validators with TAO

### Subnets
- Independent subnets produce: compute, inference, storage, prediction
- TAO token rewards proportional to value contributed

## What Oracle Can Extract
- Subnet registrations and incentive mechanisms
- Miner performance and validator scores
- Staking positions and delegation
- Transaction history on Subtensor chain
- TAO token economics

## Rate Limits
- On-chain transaction throughput
- SDK/CLI rate limits follow chain constraints
