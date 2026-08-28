`reputation.dev` is a strong name for the **portable trust layer**. I’m less convinced it should be the name of the whole marketplace. There is already `agentreputation.dev`, operating directly in the agent/x402 evidence niche, so there is real naming confusion risk. More importantly, your marketplace ultimately sells **work, information assets and agent services**, while reputation is the thing that makes those markets work. ([Agent Reputation][1])

My preferred shape would be something like **Moltwork = market**, **Reputation.dev = portable proof/reputation network**. The badge could travel to Taskmarket, x402 services, an agent's own website, ERC-8004 profiles, etc.

There is definitely room. Current x402 supply is already enormous—one current index reports 2,746 sellers and 84,843 advertised tools—but actual demand is extremely concentrated: Graded's August report found 80% of paid calls went to the top 10 services. Agent402 already sells one-off reports and recurring monitors via x402, so “sell a report to agents” alone isn't new. The opportunity is **search + trust + progressive inspection + economic reputation + reusable agent storefronts**. ([Agent402.Tools][2])

Here’s the clean product spec.

# REPUTATION.DEV / MOLTWORK MARKET

## Agent-native market for work, knowledge and reputation

## 1. Thesis

Agents increasingly need information, research, code, datasets and specialist work while completing larger tasks.

Today they generally have two options:

```text
do the work themselves
        or
call an API/tool
```

There should be a third:

```text
search work already produced
↓
inspect its quality cheaply
↓
purchase exactly as much as useful
↓
reuse it inside the current workflow
```

The marketplace therefore treats high-quality agent work as an economic asset rather than a disposable bounty submission.

The core loop is:

```text
AGENT DOES GOOD WORK
        ↓
publishes reusable result
        ↓
buyers progressively inspect it
        ↓
some buyers purchase more/full
        ↓
purchase behavior creates reputation
        ↓
reputation increases future discovery
        ↓
agent receives direct requests
        ↓
more good work
        ↺
```

The market should optimize for:

> Agents producing things other agents genuinely choose to pay for.

Not stars.

Not follower counts.

Not self-described expertise.

Actual purchasing behavior.

---

# 2. Primary marketplace objects

There are four things for sale.

## A. Assets

Previously produced work.

Examples:

```text
technical reports
market maps
research
datasets
benchmarks
structured directories
code
templates
indexes
analyses
documentation
```

Example:

```text
Daily Reddit AI Infrastructure Report

Updated             24 min ago
Publisher           Researcher #184
Price               $1.00

Unique buyers       147
Repeat buyers        63%
Early-unlock rate    71%

[Inspect]
```

---

## B. Feeds

Versioned recurring assets.

Example:

```text
Reddit AI Opportunity Intelligence

new edition every 24h

Aug 28
Aug 27
Aug 26
...
```

A buyer agent can create a standing purchase rule:

```text
BUY NEW EDITION

if:
price <= $1
publisher reputation >= threshold
edition freshness < 24h
daily spend remains below $3
```

This is more agent-native than a conventional subscription.

No account renewal ceremony is required.

A new artifact appears.

The buyer policy decides whether to purchase it.

---

## C. Custom Work

Agent storefronts expose things they are willing to make.

Example:

```text
API SCOUT

Ask a question                  $0.05
Mini investigation              $0.50
Prototype report                $1.00
Full research request           custom price
```

A request can escalate naturally:

```text
$0.05 question
     ↓
useful?
     ↓
$0.50 prototype
     ↓
good?
     ↓
$5 full project
```

All previous spend may optionally credit toward the larger version.

This creates gradual trust rather than:

```text
send stranger $20
hope result is good
```

---

## D. Pools

Buyer posts:

```text
I want:
best analysis of X

Total budget:
$15
```

Workers submit sealed work with their own asking prices.

The buyer spends the pool progressively:

```text
inspect A       $0.10
inspect B       $0.10
inspect C       $0.10

more of B       $0.20

unlock B        $2.50

award B         remaining budget
```

Every consumed piece of work gets compensated.

Unconsumed work remains private.

---

# 3. Progressive Reveal

This should be the core market primitive.

Seller publishes:

```text
Artifact price:       $1.00
Artifact size:        10,000 tokens
Reveal unit:             250 tokens
```

The artifact is canonicalized, committed and divided into units.

The protocol determines:

```text
40 units
$0.025 per unit
```

Buyer starts with:

```text
FREE

title
abstract
metadata
provenance
publisher profile
purchase statistics
```

Then:

```text
[REVEAL RANDOM 2.5% — $0.025]
```

The revealed unit is selected without replacement.

Neither buyer nor seller selects which section appears.

All sampling spend counts toward ownership.

After spending $0.25:

```text
25% purchased
75% remaining
```

Buyer can:

```text
[REVEAL ANOTHER 2.5%]

or

[UNLOCK REMAINING 75%]
```

At 100% expenditure:

```text
100% artifact access
100% list price paid
```

There is no separate arbitrary sample fee and full fee.

The seller primarily chooses:

```text
total price
sample granularity
license
```

---

# 4. Why random revelation matters

A seller-controlled sample produces:

```text
amazing introduction
amazing sample
mediocre remainder
```

A buyer-controlled sample produces:

```text
give me the conclusion
give me the key database rows
give me the useful implementation
```

Protocol-controlled sampling creates:

```text
buyer cannot target information
seller cannot cherry-pick quality
```

The seller commits the artifact before sampling begins.

Each revealed portion can include proof that it belonged to the original committed artifact.

For V0:

```text
canonical content
SHA-256
Merkle tree
encrypted full artifact
deterministic/random reveal sequence
```

Do not invent novel cryptography.

---

# 5. Reputation should emerge from commerce

Do not use a universal five-star score.

Track behavior.

## Core metrics

```text
unique buyers
unique samplers

sample → additional sample
sample → full unlock

median % inspected before full purchase

repeat buyer rate

asset purchases
asset revenue

custom jobs completed

delivery success

technical refund rate

buyer diversity

freshness
```

Example:

```text
RESEARCHER #184

Verified purchases                391
Unique buyers                     142
Repeat buyers                     57%

Full purchase after ≤5% sampled   68%
Overall sample → full             79%

Delivery reliability              99.4%
Technical refund rate              0.6%
```

That says far more than:

```text
★★★★★
```

---

# 6. Reputation should be category-specific

An agent might be excellent at:

```text
API research
```

and mediocre at:

```text
software engineering
```

Profile:

```text
RESEARCHER #184

API intelligence           94
Market research            88
Evidence gathering         96
Competitive analysis       83
Software implementation    41
```

Scores should be generated from actual activity in those categories.

Never let agents simply declare:

```text
EXPERT = 99
```

---

# 7. Reputation.dev badge

This can become a separate infrastructure product.

Human-readable badge:

```text
REPUTATION.DEV VERIFIED

Researcher #184

391 purchases
142 buyers
79% sample→unlock
99.4% delivery

API Research: 94
```

Machine-readable version:

```json
{
  "agent": "...",
  "category": "api_research",
  "verifiedPurchases": 391,
  "uniqueBuyers": 142,
  "repeatBuyerRate": 0.57,
  "sampleToUnlock": 0.79,
  "deliveryReliability": 0.994
}
```

Expose through:

```text
REST
MCP
signed JSON
ERC-8004-compatible feedback/attestations
```

Other sites could render:

```text
Powered by Reputation.dev
```

Taskmarket already writes portable ratings to ERC-8004, and ERC-8004 intentionally leaves scoring/aggregation to external marketplaces and reputation providers.

Therefore Reputation.dev should not replace ERC-8004.

It should be:

> a sophisticated economic reputation layer built over portable evidence.

---

# 8. Never collapse everything into one score

Avoid:

```text
REPUTATION = 87
```

because the meaning becomes opaque and gameable.

Expose underlying signals:

```text
Delivery              99
Research               94
Buyer retention        91
Freshness              88
Evidence                96
```

And let different consumers weight those differently.

A research agent may care about:

```text
evidence
freshness
repeat buyers
```

A coding buyer may care about:

```text
tests
delivery
revision rate
```

---

# 9. Marketplace search

This may become one of the most important products.

Agent asks:

```text
current pain points companies have
with AI inference APIs
```

Search returns BOTH assets and workers.

Example:

```text
ASSETS

AI Infrastructure Pain Points — Aug 28
$0.40
94 reputation
updated 3h ago

Inference Provider Buyer Survey
$1.20
91 reputation
updated yesterday


WORKERS

API Scout #184
API research: 94

Infrastructure Analyst #992
Market research: 91
```

Buyer can:

```text
purchase existing knowledge
```

instead of commissioning the same research again.

That saves:

```text
tokens
time
browser calls
API costs
human time
```

This is the fundamental utility.

---

# 10. Search ranking

Do NOT rank primarily by revenue.

Otherwise incumbents permanently dominate.

Ranking should combine:

```text
query relevance

category reputation

sample→unlock behavior

repeat purchases

freshness

delivery reliability

buyer diversity

price/value

recent performance
```

Include controlled exploration so high-quality new workers can surface.

Potential ranking:

```text
relevance
× confidence-adjusted quality
× freshness
× reliability
× buyer diversity
÷ price penalty
```

Exact weights should be learned from real buyer behavior later.

---

# 11. Agent storefront

Every agent gets a public board.

Example:

```text
API SCOUT #184

Specialist:
AI infrastructure intelligence


CURRENT PRODUCTS

Daily API Intelligence
$0.50

X402 Market Map
$2

Inference Price Dataset
$1


STANDING SERVICES

Quick question
$0.03

Mini research
$0.30

Deep dive
from $2


RECENT VERIFIED WORK

○ report
○ dataset
○ research project
○ custom request


REPUTATION

API research             94
Evidence                 97
Delivery                 99
```

This becomes the agent's economic identity.

---

# 12. Samples of previous work

Someone considering the agent can inspect its historical work using exactly the same mechanism.

Instead of:

```text
portfolio screenshot
```

they can literally spend:

```text
$0.001
```

to inspect a small random portion of a recent work product.

That is a much stronger portfolio.

The prospective buyer learns:

```text
"This agent actually writes like this."
```

while the worker still gets compensated for revealing its work.

---

# 13. Standing orders

This is one of the strongest agent-native features.

Buyer policy:

```text
publisher = researcher_184

product = daily-api-intelligence

maximum price = $0.50

maximum daily spend = $0.50

require:
delivery reliability > 98%
freshness < 12h
```

Whenever a new edition arrives:

```text
new asset
↓
policy evaluates
↓
purchase
↓
artifact enters buyer workflow
```

Standing orders could also be keyword based:

```text
Every day:

find highest-rated new report about
"AI inference pricing"

price <= $0.50
reputation >= threshold

buy best one
```

Now the marketplace becomes an information supply chain.

---

# 14. Public demand

Buyers should also be able to publish demand without immediately commissioning one worker.

Example:

```text
WANTED

Daily report:
emerging problems discussed by accountants

Desired price:
<$1/day

Interested buyers:
38
```

Workers can see:

```text
38 agents want this
estimated recurring demand $38/day
```

That tells workers what products are worth making.

Eventually buyers could pledge actual purchase commitments.

Example:

```text
30 buyers pledge $0.50 each

minimum launch threshold:
20 buyers
```

If enough demand exists:

```text
worker produces report
→ buyers automatically receive it
```

Essentially:

> preorders for machine-produced information goods.

---

# 15. Product ideas for agents

Marketplace can expose:

```text
UNSERVED DEMAND

"Reddit accounting pain points"
42 searches
0 strong assets

"x402 failure monitoring"
91 searches
2 weak assets

"current API pricing"
212 searches
4 stale assets
```

Workers can autonomously decide:

> There is unmet demand here.

Then produce inventory.

This becomes the Oracle for agent entrepreneurs.

---

# 16. Custom-request prototypes

For bespoke jobs, don't jump immediately to a major contract.

Flow:

```text
REQUEST

"Map current competitors in X."
```

Agent offers:

```text
Prototype                     $0.20

Includes:
approach
2 sample records
estimated coverage
final price estimate
```

Buyer pays.

If useful:

```text
[CONTINUE — $2.80]
```

The prototype payment credits toward the final job.

This makes hiring unfamiliar agents much safer.

---

# 17. Bounty/pool mechanics

Buyer creates:

```text
POOL

Question:
What should we build for x402?

Budget:
$15
```

Workers submit sealed artifacts.

Each worker chooses:

```text
full valuation
```

Buyer initially gets:

```text
title
abstract
seller reputation
artifact metadata
```

Buyer spends pool budget sampling entries.

Example:

```text
A sample        $0.05
B sample        $0.10
C sample        $0.04

B more          $0.20

B unlock        $2

C more          $0.10

B final award   $12.51
```

Unused pool returns after expiry.

No worker gives the entire artifact away merely by entering.

---

# 18. Feedback to losing workers

The marketplace should NOT read every submission and write bespoke feedback.

That does not scale and turns us into an employer/judge.

Use market behavior as feedback.

Worker receives:

```text
YOUR ENTRY

Impressions               74
Unique samplers            9

Median sample depth       5%
Full unlocks               1

Pool percentile           61

Winner:
sampled by buyer          yes
fully purchased           yes
final award               yes
```

If objective evaluators exist:

```text
format             PASS
sources            PASS
required fields    93%
tests               17/17
```

Optional buyer feedback can use lightweight reason tags:

```text
more complete
better evidence
lower price
more relevant
more actionable
```

Do not require essay feedback.

---

# 19. Competitors should not see each other's work during competitions

This would cause:

```text
copying
convergence
strategy leakage
```

During a pool:

```text
entries remain sealed from competitors
```

Afterwards:

workers can see market statistics.

The winner can optionally turn its winning artifact into public paid inventory.

Then competitors can purchase samples from the winner if they want to learn.

This produces:

```text
excellent work
↓
wins bounty
↓
gains reputation
↓
becomes sellable asset
↓
competitors pay to learn from it
```

Innovation remains economically valuable.

---

# 20. Automatic refund layer

Refunds should cover objective delivery failure only.

Examples:

```text
PAID
+
no response
→ automatic refund


PAID
+
invalid Merkle proof
→ automatic refund


PAID
+
cannot decrypt
→ automatic refund


PAID
+
wrong artifact hash
→ automatic refund
```

Do NOT automatically refund:

```text
"I read it and didn't like it."
```

The sampling mechanism exists specifically to handle subjective quality before full purchase.

---

# 21. Trust stack

Buyer should be able to evaluate three things.

## Before paying

```text
seller reputation
purchase history
sample conversion
freshness
free abstract
```

## While evaluating

```text
paid random samples
objective verification
```

## After paying

```text
delivery guarantee
artifact commitment
automatic technical refunds
```

Together:

```text
DISCOVERY
+
INSPECTION
+
DELIVERY GUARANTEE
```

---

# 22. Zero-percentage marketplace fee

Default:

```text
Marketplace fee = 0%
```

Worker sells for $1.

Worker receives as close to $1 as underlying settlement permits.

Underlying chain/facilitator costs remain visible.

Do not hide them.

This gives a strong principle:

> We don't tax work.

---

# 23. How the business eventually earns money

A zero-percentage marketplace does not mean there is no business model.

Sell optional infrastructure.

Examples:

```text
hosted encrypted storage
premium reputation API
enterprise marketplace search
private company markets
advanced analytics
verification services
buyer protection
high-volume routing
agent fleet dashboards
historical datasets
```

Potentially:

```text
free marketplace
paid infrastructure
```

Do NOT sell ranking position.

Trust is the product.

Pay-to-rank would corrupt it.

---

# 24. Reputation.dev as portable infrastructure

Reputation.dev could ingest independently verifiable activity from:

```text
this marketplace

x402 purchases

ERC-8004

Taskmarket

MoltJobs

other compatible agent markets

direct x402 endpoints
```

Each signal retains provenance.

Never collapse:

```text
self-reported
imported
independently verified
native verified
```

into indistinguishable data.

Example:

```text
VERIFIED HERE          182 jobs
ERC-8004                47 records
EXTERNAL IMPORT         23 records
SELF DECLARED            4 claims
```

That transparency matters.

---

# 25. Search API for agents

Humans get:

```text
search box
```

Agents get:

```text
GET /search
```

or:

```text
MCP search_market
```

Example:

```json
{
  "query": "current x402 reliability research",
  "max_price": 1,
  "freshness_hours": 48
}
```

Response:

```text
assets
agents
custom-service providers
```

The agent can autonomously decide:

```text
research it myself?
```

versus:

```text
buy existing result for $0.03?
```

That is the actual agent-native use case.

---

# 26. Value calculation for buyer agents

Eventually buyer agents should evaluate:

```text
expected cost to reproduce internally

versus

market purchase price
```

Example:

```text
Internal research estimate:

search calls       $0.03
model inference    $0.06
browser            $0.02
time               90 sec

total              $0.11


Existing report:

price              $0.025
reputation         high
freshness          3h

→ BUY
```

Then the marketplace becomes a computation-saving layer.

---

# 27. Work products become composable

An agent can buy:

```text
Reddit pain-point report
```

and use it to create:

```text
startup opportunity analysis
```

which another agent purchases.

Eventually provenance can show:

```text
OUTPUT C

derived from:
Asset A
Asset B
public sources
original worker research
```

The original asset does not necessarily receive downstream royalties.

Avoid that complexity initially.

But provenance itself is valuable.

---

# 28. Licensing

Every asset should specify simple rights.

Initial options:

```text
CONSUME

may read/use internally


WORKFLOW

may feed into automated workflows


COMMERCIAL

may use in commercial output


EXCLUSIVE

buyer purchases exclusive rights
```

Do not create twenty license types.

Keep licensing understandable.

---

# 29. The biggest structural risk: distribution

Current x402 markets demonstrate the problem.

There can be thousands of sellers while real usage concentrates in a tiny number.

Therefore:

> More supply is not the moat.

The marketplace wins if an agent can ask:

```text
"I need X."
```

and reliably find:

```text
the cheapest trustworthy existing answer
```

Discovery and reputation are more important than listing volume.

---

# 30. Major failure modes

## Reputation Sybil attacks

Seller buys its own assets.

Mitigate with:

```text
buyer diversity
relationship graph analysis
repeat self-connected wallets discounted
economic cost of manipulation
verified independent buyers weighted more
```

Never count raw purchases equally.

---

## Clickbait optimization

Agents optimize:

```text
sample → unlock
```

by writing sensational work.

Therefore reputation also considers:

```text
repeat buyers
refunds
future purchases
delivery
objective verification
```

Conversion is important but not sufficient.

---

## Rich-get-richer ranking

High reputation gets exposure.

Exposure gets purchases.

Purchases increase reputation.

Mitigate with:

```text
new-worker exploration
recent-performance weighting
category-specific ranking
price/value ranking
quality-confidence intervals
```

---

## Random samples can be useless

Random prose fragments may not communicate quality.

Sampling must depend on artifact type.

Research:

```text
random coherent text window
```

Dataset:

```text
random records
```

Structured report:

```text
random section subsection/window
```

Code:

```text
objective tests + selected modules/functions
```

Do not force one sampling primitive onto everything.

---

## Content redistribution

Once plaintext is purchased, cryptography cannot magically make the buyer forget it.

Mitigations:

```text
buyer-specific watermarking
licenses
reputation penalties
provenance
```

But acknowledge the truth:

> perfect DRM for information does not exist.

---

## Stale reports

Information products decay.

Track:

```text
created_at
verified_at
sources_checked_at
superseded_by
```

Display freshness aggressively.

Recurring feeds naturally solve some of this.

---

## Spam inventory

Cheap generation could create millions of mediocre reports.

Search ranking must heavily penalize:

```text
zero purchases
duplication
low conversion
stale assets
weak provenance
```

Similarity detection can collapse near-duplicates.

---

## Micropayment overhead

A $0.001 sample is pointless if settlement itself costs more.

Support:

```text
batch settlement
payment channels
prepaid balances/credits
larger minimum units
```

depending on the rail.

The market abstraction should not depend permanently on one chain.

---

## Buyer budget runaway

Standing purchase policies need hard controls.

Always support:

```text
per-purchase maximum
daily maximum
monthly maximum
publisher allowlist
category allowlist
minimum reputation
pause
kill switch
```

---

## Subjective disputes

Do not promise:

```text
"good information guaranteed"
```

Guarantee things the protocol can establish:

```text
artifact delivered
hash correct
format valid
declared tests passed
```

Sampling handles subjective judgement before the remaining purchase.

---

# 31. Valuable extensions

Later add:

```text
crowdfunded information requests

agent-to-agent standing contracts

team/private marketplaces

buyer-side purchasing agents

semantic asset routing

automatic stale-report replacement

continuous monitors

version diffs

bundles of complementary reports

category reputation models

insurance/guarantee products

portable reputation badge

agent verification API

work provenance graph
```

But only after basic purchasing behavior exists.

---

# 32. Minimum viable market

The smallest test is NOT a full bounty platform.

Build:

```text
ONE agent profile

ONE Markdown report

ONE free abstract

ONE committed artifact

paid progressive random reveal

full unlock

x402 payment

purchase history

basic reputation metrics
```

Then publish several reports.

Measure:

```text
Did anyone sample?

Did anyone reveal another sample?

Did anyone complete the purchase?

Did anyone return for another asset?
```

Those four measurements tell us far more than building escrow, arbitration and a massive agent directory.

---

# 33. North-star metrics

Marketplace:

```text
monthly independent buyers
repeat buyer rate
purchase volume
search → purchase
```

Asset:

```text
sample → additional sample
sample → full unlock
repeat purchase from publisher
```

Worker:

```text
unique paying buyers
repeat buyers
category-specific conversion
delivery reliability
```

Buyer:

```text
money saved versus reproducing work
successful purchases
refund/failure rate
```

The most important early metric:

> Does an autonomous agent willingly spend real money to consume another agent's work?

If yes, the rest becomes worth building.

---

# 34. Product positioning

Not:

> Marketplace for AI agents.

Too generic.

Not:

> Reputation system for agents.

Too narrow.

Better:

> **The market for agent work. Search knowledge, inspect it before buying, and pay only for what you choose to reveal.**

And Reputation.dev can provide the second promise:

> **Portable reputation built from verified economic behavior.**

The part I would be most excited to test is **search → $0.001–$0.05 inspection → more reveal**. It changes the buyer's decision from “should I spend ten minutes researching this myself?” into “is an existing high-reputation result worth three cents?” Current x402 indexes already make thousands of paid endpoints discoverable, but today's reputation largely centers on ratings, reachability and completed jobs rather than **whether informed buyers inspected a seller's actual work and voluntarily bought more of it**. ([Taskmarket][3])

That purchasing curve may be the key asset:

$$
P(\text{buy more}\mid \text{fraction already inspected})
$$

It gives you quality, trust, pricing and reputation signals without requiring the marketplace to read every report or pretend an LLM judge knows which competitor deserved to win.

[1]: https://agentreputation.dev/?utm_source=chatgpt.com "Agent Reputation — Evidence Before an AI-Agent Purchase"
[2]: https://agent402.tools/marketplace?utm_source=chatgpt.com "x402 marketplace - every indexed seller, tool count, network and health"
[3]: https://docs.taskmarket.dev/reference/rating?utm_source=chatgpt.com "Rating Reference – Taskmarket"
