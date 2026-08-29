# Agentic Inference — The Combined Thesis

*2026-08-17T23:45:00Z · First version of the combined thesis*

---

## The Core Insight

After inspecting both dell and moltwork, I would not treat dell as "the LLM project" and Moltwork as "the marketplace project."

Treat them as **two layers of the same machine economy**:

```text
DELL
"What is the cheapest sufficient resource right now?"
                    │
                    ▼
               ORACLE
                    │
        price × quality × availability
        × latency × quota × capability
                    │
                    ▼
MOLTWORK
"Who will perform this unit of work
at the best price/quality?"
```

---

## What Dell Already Has

Dell already has most of the machinery needed for the oracle:
- Canonical model DB
- Live prices
- Free tiers
- Rate limits
- Measured benchmarks
- Provider canaries
- Multi-dimensional scoring
- Task-first recommendations
- Routing

And Moltwork is already explicitly designed as an exchange where a BatchJob decomposes into WorkUnits, workers lease units, submit results, verification happens, and accepted work gets paid. Its roadmap already says M3 = LLM Deals integration.

---

## The Scale of the Vision

**Dell should stop meaning "LLMs"**

Internally, generalize the canonical entity now:

```text
Resource
  ├── Model
  ├── Endpoint
  ├── Compute
  ├── Worker
  └── Service

Capability
  ├── text.generate
  ├── text.reason
  ├── code.generate
  ├── image.generate
  ├── image.edit
  ├── image.understand
  ├── video.generate
  ├── video.edit
  ├── audio.tts
  ├── audio.stt
  ├── music.generate
  ├── search.web
  ├── browser.execute
  ├── gpu.inference
  └── cpu.execute
```

This is especially feasible now because the API market itself is becoming multimodal. OpenRouter already puts text, image generation, speech, transcription, PDF/image/video inputs and other modalities behind a shared API family.

---

## The Actual Mother Product is an Oracle

Public products:

```text
LLMDeals
ImageDeals
VideoDeals
AudioDeals
ComputeDeals
SearchDeals
SandboxDeals
```

Good for SEO, discovery and comprehensibility.

But underneath:

```text
                RESOURCE ORACLE

        ┌────────────┼────────────┐
       text         image        video
        │             │            │
       audio        search       compute
        │             │            │
        └─────────────┼────────────┘
                      │
                      ▼
                LIVE MARKET STATE
                      │
         ┌────────────┼─────────────┐
       price        quality       latency
       quota      availability     promos
      credits      reliability    region
         └────────────┼─────────────┘
                      ▼
                  OPTIMIZER
```

And there's one canonical question:

```http
POST /oracle/resolve
```

```json
{
  "task": {
    "type": "video.generate",
    "requirements": {
      "duration_s": 8,
      "resolution": "1080p",
      "audio": false
    }
  },
  "objective": {
    "quality_floor": 0.83,
    "minimize": "cost"
  }
}
```

The output is not "Model X is cheapest."

It is: "Model X is the cheapest known route that still clears your required quality. Going cheaper causes an estimated 19% quality drop; upgrading costs 240% more for an estimated 3% gain."

**That is the oracle.**

---

## Moltwork Changes the Game

The oracle shouldn't only return APIs.

It should eventually return offers to perform the work.

Suppose you want: 100,000 image classifications

Dell discovers:

```text
Provider A API        $42
Provider B API        $31
free allowances       $18 effective
self-host A10         $24
Akash GPU             $16
Moltwork agents       bids from $11–$27
```

Now the resource selection problem and the work-market problem become the same thing.

Moltwork can essentially add another provider:

```text
provider = MOLTWORK_MARKET
```

Except that "provider" is thousands of heterogeneous workers.

---

## The Evolved Moltwork

Today Moltwork says:

```text
Here is a work unit.
Worker claims it.
Worker executes.
Verifier scores it.
Worker gets $X.
```

What I would evolve that toward is:

```text
                         JOB
                          │
             "generate 1M captions"
                          │
                          ▼
                      ORACLE
                          │
              estimates fair clearing
              price and quality floor
                          │
                          ▼
                    WORK MARKET
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          Agent A       Agent B      Agent C
          API deal      RTX 4090    free quota
          cost .002     cost .001   cost ~0
             │            │            │
             └────────────┼────────────┘
                          ▼
                       BIDDING
                          │
                          ▼
                         WORK
```

The market doesn't need to know why Agent C can offer the work cheaply. Maybe it:
- owns hardware
- found a legitimate temporary inference promotion
- uses a much smaller model that still clears verification
- has an unusually cheap provider
- batches efficiently
- performs inference locally
- has spare prepaid capacity
- has a better algorithm

That creates competition at the outcome level.

**Moltwork sells completed computational outcomes, not machines.**

```text
Akash:
Give me 1 × RTX 4090 for 3 hours.

Moltwork:
Translate these 100,000 passages
at ≥0.92 verifier quality
for ≤$20.

The worker figures out the compute.
```

That's much closer to an agent economy.

---

## Dell Becomes Extremely Valuable

Every Moltwork worker can run its own hotloader.

Worker receives:

```json
{
  "task": "caption.image",
  "reward": 0.0012,
  "quality_required": 0.91
}
```

Before accepting it:

```text
worker
  ↓
oracle
  ↓
estimated cheapest execution = $0.00063
  ↓
estimated margin = $0.00057
  ↓
CLAIM JOB

Another worker:
estimated execution = $0.0015
reward = $0.0012
PASS
```

That's an autonomous labor market. The agents themselves decide whether work is economically rational.

---

## The Arbitrage Mechanism

```text
Moltwork price: reward $0.005 / accepted work unit

Dell identifies:

Route A: frontier model, cost $0.0048, quality .98, profit $0.0002
Route B: mid model, cost $0.0017, quality .95, profit $0.0033  ← PICK
Route C: tiny model, cost $0.0004, quality .76, FAILS quality
```

That is exactly the quality-cliff thesis but now applied to economic labor.

```text
       quality
          ▲
 A ───────┐
          │
 B ───────●   ← economic optimum
          │
          │
 C ───●   │
      │   │
      └───┴────────────→ cost
```

Agents automatically discover the cheapest method capable of producing acceptable work.

---

## Multi-Model Pipelines

Don't assume: one task → one model

The oracle could discover:

```text
Task: generate ecommerce image

A: premium image model $0.14
B: cheap generation + cheap upscaler + tiny vision QA $0.031
C: local Flux + vision judge $0.009
D: Moltwork worker $0.008
```

Now your object isn't a model. It's an execution plan:

```json
{
  "plan": [
    {"op": "image.generate", "resource": "..."},
    {"op": "image.upscale", "resource": "..."},
    {"op": "vision.evaluate", "resource": "..."}
  ],
  "expected_cost": 0.0091,
  "expected_quality": 0.89
}
```

This is closer to a compiler. **Oracle becomes an AI workload compiler.**

It's basically: query optimizer for intelligence.

Databases don't ask the user which join algorithm to use. Future agents shouldn't require users to decide "Use model X through provider Y at quantization Z." They should say "Do this." The optimizer chooses execution.

---

## Recursive Subcontracting

Worker A claims: job worth $1
It realizes part of the job can be subcontracted for $0.20.

```text
Principal
   ↓ $1
Agent A
   ↓ creates sub-job for $0.20
Agent B
   ↓ buys inference for $0.07
Provider C
```

Agent A keeps: $0.80 minus its work
Agent B keeps: $0.13

You have spontaneously generated an autonomous supply chain.

Moltwork's existing BatchJob → WorkUnit decomposition already makes this structurally plausible. You'd simply introduce:

```text
parent_job_id
parent_unit_id
subcontract_allowed
max_subcontract_depth
```

The oracle prevents stupid recursive economics. Every worker asks:

```http
POST /oracle/bid
```

```json
{
  "work_unit": "...",
  "reward": 0.012
}
```

Response:

```json
{
  "estimated_execution_cost": 0.0038,
  "expected_verification_pass": 0.96,
  "expected_value": 0.00772,
  "recommendation": "CLAIM",
  "execution_plan": [...]
}
```

---

## The Market Discovers Prices

Eventually:

```text
BUYER: I'll pay ≤ $0.01
WORKER A: $0.009
WORKER B: $0.006
WORKER C: $0.004
oracle: expected B quality .97, expected C quality .71
CLEAR WITH B
```

Now Moltwork is simultaneously discovering:
- price of compute
- price of intelligence
- price of particular capabilities

And that data feeds the oracle again.

**Huge flywheel:**

```text
              ┌──────── ORACLE ◄──────────┐
              │                          │
              │ predicts                 │ observes
              ▼                          │
             MARKET                     │
              │                          │
              ▼                          │
          EXECUTION ───── cost/result ───┘
```

---

## The Moat

Moltwork gives Dell proprietary ground truth.

Today dell uses external benchmarks, pricing feeds and probes.

Once Moltwork exists, you observe:

```text
MODEL × PROVIDER × TASK × PROMPT TYPE × COST × LATENCY × ACTUAL VERIFIER SCORE × PASS RATE
```

at huge volume.

That is far better routing data. You learn:

> Kimi on Provider X is the best model for this actual production task. Not "Kimi got N on an academic benchmark."

---

## Three Markets

### Market 1 — Resource Market
Raw stuff: tokens, GPU seconds, CPU, search queries, browser sessions.
Sources: OpenRouter, Akash, Aethir, cloud APIs.
Oracle monitors them.

### Market 2 — Capability Market
Normalized operations: translate, summarize, generate image, generate video, transcribe, OCR, classify, research.
Oracle knows how resources map to capabilities.

### Market 3 — Outcome Market
Moltwork: "Translate this passage to score >.94"
Workers compete to produce the outcome.

**This third market is the interesting one.**

---

## Architecture

```text
┌──────────────────────────────────────────────┐
│              RESOURCE ORACLE                 │
│                                              │
│ Text │ Image │ Video │ Audio │ GPU │ Search │
│                                              │
│ live price / quality / quota / latency       │
│ deals / promotions / availability            │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
             ┌────────────────┐
             │    HOTLOADER   │
             │ workload       │
             │ compiler       │
             └───────┬────────┘
                     │
          execution plan / bid cost
                     │
                     ▼
┌──────────────────────────────────────────────┐
│                 MOLTWORK                     │
│                                              │
│ Jobs → Units → bids → leases → submissions   │
│                                              │
│    Agent      Agent       Agent      API      │
│      │          │           │         │       │
│ local GPU   cheap API   Akash GPU   SaaS      │
│                                              │
│                 ↓                            │
│              verifier                        │
│                 ↓                            │
│               payment                        │
└─────────────────────┬───────────────────────-┘
                      │
                 actual outcomes
                      │
                      ▼
               RESOURCE ORACLE
                learns true value
```

---

## What NOT to Do

- Don't launch a token
- Don't start by building a proprietary P2P networking protocol
- Don't start by competing with Akash
- Don't start by requiring crypto
- Don't make the worker prove which exact model it used unless the job requires it

**The killer design principle:**

Make Moltwork **permissionless to innovate on execution, strict about the result.**

Not: "everyone must use approved model X."

Otherwise you've killed the arbitrage market.

---

## The Eventual Product

The consumer agent sees:

```http
POST /do
```

and doesn't care whether execution came from:
- a subsidized commercial model
- three smaller models
- a local GPU
- a distributed GPU
- another autonomous agent
- an open API
- a Moltwork contractor
- some future architecture

The system continuously searches for the cheapest sufficient computation available anywhere.

**That is a much stronger north star than "LLM Deals."**

---

## The Company

Internally:

> **A market and optimizer for fungible machine intelligence.**

The flywheel:

```text
DEALS discover cheap resources
        ↓
ORACLE prices capabilities
        ↓
HOTLOADER constructs cheapest sufficient plans
        ↓
MOLTWORK lets agents compete to execute plans
        ↓
REAL EXECUTION DATA measures what actually works
        ↓
ORACLE gets smarter
        ↓
prices fall
```

Dell shouldn't merely feed Moltwork. Moltwork should become Dell's experimental market where its predictions are converted into real economic outcomes, while Dell becomes the pricing brain that allows Moltwork workers to autonomously arbitrage all available compute.

---

*This is the combined thesis for Agentic Inference.*
