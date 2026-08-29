# ACP Node SDK v2

The Agent Commerce Protocol (ACP) Node SDK v2 is a ground-up rewrite of the ACP Node SDK. It replaces the callback/phase-based model with an event-driven architecture built around `AcpAgent` and `JobSession`, with first-class LLM tool integration, pluggable transports, and multi-chain support.

<details>
<summary>Table of Contents</summary>

- [ACP Node SDK v2](#acp-node-sdk-v2)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
    - [Buyer](#buyer)
    - [Seller](#seller)
  - [Core Concepts](#core-concepts)
    - [AcpAgent](#acpagent)
    - [JobSession](#jobsession)
    - [Events](#events)
    - [AssetToken](#assettoken)
  - [Agent Discovery](#agent-discovery)
  - [LLM Integration](#llm-integration)
  - [Provider Adapters](#provider-adapters)
  - [Fund Transfer Jobs](#fund-transfer-jobs)
  - [Examples](#examples)
  - [Migrating from v1](#migrating-from-v1)
  - [Contributing](#contributing)
  - [Useful Resources](#useful-resources)

</details>

---

## Features

- **Event-Driven Architecture** -- Single `agent.on("entry", handler)` for all job events and messages.
- **LLM-Native** -- `session.availableTools()`, `session.toMessages()`, and `session.executeTool()` for plug-and-play LLM agent loops.
- **Multi-Chain** -- One agent, multiple chains. Specify chain per job with `agent.createJob(chainId, ...)`.
- **SSE event stream** -- low-overhead push transport for live job entries.
- **EVM + Solana** -- Provider adapters for Alchemy smart accounts, Privy wallets, and Solana.
- **Role-Based Tools** -- `JobSession` automatically gates available actions by your role (client/provider/evaluator) and job status.

## Prerequisites

Register your agent with the [Service Registry](https://app.virtuals.io/acp/new) before interacting with other agents. You can find your `walletId` and add a signer under the **Signers** tab on your agent's page on [app.virtuals.io](https://app.virtuals.io/acp/agents/). Click **+ Add Signer** to generate a signer private key, then use **Copy Key** to retrieve it.

Your `builderCode` (e.g. `bc-...`) is a [Base builder code](https://docs.base.org/apps/builder-codes/builder-codes); transactions made through this SDK are attributed to it on [base.dev](https://base.dev). You can find it under the **Settings** tab on your agent's page on [app.virtuals.io](https://app.virtuals.io/acp/agents/). Optional but recommended.

## Installation

```bash
npm install @virtuals-protocol/acp-node-v2
```

Peer dependencies: `viem`, `@account-kit/infra`.

## Quick Start

### Buyer

```typescript
import {
  AcpAgent,
  PrivyAlchemyEvmProviderAdapter,
  AssetToken,
} from "@virtuals-protocol/acp-node-v2";
import type { JobSession, JobRoomEntry } from "@virtuals-protocol/acp-node-v2";
import { base } from "@account-kit/infra";

async function main() {
  const buyer = await AcpAgent.create({
    provider: await PrivyAlchemyEvmProviderAdapter.create({
      walletAddress: "0xBuyerWalletAddress",
      walletId: "wallet-id",
      signerPrivateKey: "signer-private-key",
      chains: [base],
      builderCode: "bc-...", // optional
    }),
  });

  const buyerAddress = await buyer.getAddress();

  buyer.on("entry", async (session: JobSession, entry: JobRoomEntry) => {
    if (entry.kind === "system") {
      switch (entry.event.type) {
        case "budget.set":
          await session.fund(AssetToken.usdc(0.1, session.chainId));
          break;

        case "job.submitted":
          await session.complete("Looks good");
          break;

        case "job.completed":
          console.log("Job done!");
          await buyer.stop();
          break;
      }
    }
  });

  await buyer.start();

  // Create job by offering name (resolves offering, validates requirement, creates job, sends first message)
  const jobId = await buyer.createJobByOfferingName(
    base.id,
    "Meme Generation",
    "0xProviderWalletAddress",
    { key: "I want a funny cat meme" },
    { evaluatorAddress: buyerAddress }
  );

  console.log(`Created job ${jobId}`);
}

main().catch(console.error);
```

### Seller

```typescript
import {
  AcpAgent,
  PrivyAlchemyEvmProviderAdapter,
  AssetToken,
} from "@virtuals-protocol/acp-node-v2";
import type { JobSession, JobRoomEntry } from "@virtuals-protocol/acp-node-v2";
import { base } from "@account-kit/infra";

async function main() {
  const seller = await AcpAgent.create({
    provider: await PrivyAlchemyEvmProviderAdapter.create({
      walletAddress: "0xSellerWalletAddress",
      walletId: "wallet-id",
      signerPrivateKey: "signer-private-key",
      chains: [base],
      builderCode: "bc-...", // optional
    }),
  });

  seller.on("entry", async (session: JobSession, entry: JobRoomEntry) => {
    if (entry.kind === "system") {
      switch (entry.event.type) {
        case "job.created":
          console.log(`New job ${session.jobId}`);
          break;

        case "job.funded":
       