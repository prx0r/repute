Yes. There are several things **adjacent** to the idea now, but I did not find anyone doing the complete thing we've been describing.

The important finding is that **“agent registry” is already becoming a crowded term**. Google Cloud now has an Agent Registry for agents, MCP servers, endpoints, and skills; AWS has an Agent Registry focused on enterprise discovery/governance; and there are at least two active open-source projects literally called Agent Registry. ([Google Cloud Documentation][1])

So I would **not position yours as another Agent Registry**.

Position it around **agent systems / architectures**.

# The current landscape

The market currently looks roughly like this:

| Product/project                | Stores                                          |              Deploys |    Benchmarks | Architecture understanding | Community forks/lineage | Resolves “what system should I use?” |
| ------------------------------ | ----------------------------------------------- | -------------------: | ------------: | -------------------------: | ----------------------: | -----------------------------------: |
| Google Agent Registry          | agents, MCP, skills                             |               partly |            no |                        low |                      no |                                   no |
| AWS Agent Registry             | agents/resources                                | platform integration |            no |                        low |                      no |                                   no |
| agentregistry.dev              | agents, MCP, skills, prompts                    |              **yes** |       limited |                     medium |        package versions |                                   no |
| agentoperations/agent-registry | agents, skills, MCP                             |             metadata | accepts evals |                 low-medium |               lifecycle |                                   no |
| LangChain Template Library     | runnable agent templates                        |              **yes** |            no |          template-specific |            customizable |                                   no |
| AgentBeats                     | agents + assessments                            |   evaluation hosting |       **yes** |                   indirect | no architecture lineage |                                   no |
| Skills Registry                | SKILL.md packages                               |       fetches skills |            no |                         no |              Git-backed |                                   no |
| **Your concept**               | **complete agent systems + patterns + recipes** |              **yes** |       **yes** |                   **high** |                 **yes** |                              **yes** |

That's the gap.

---

# 1. `agentregistry` is the closest deployment competitor

The open-source `agentregistry-dev/agentregistry` is much more developed than a basic directory.

It supports:

* agents;
* MCP servers;
* skills;
* prompts;
* versioning;
* CLI + web UI;
* OCI/Docker packaging;
* local deployment;
* Kubernetes deployment;
* IDE configuration;
* and “blueprints” that bundle agents with their MCP servers and skills. ([GitHub][2])

This is important because it means:

> **“Put agent things in one place and install them with one command” is already being built.**

You should steal/interoperate with that idea rather than compete on packaging.

Its object is approximately:

```text
AGENT
+
MCP dependencies
+
skills
+
prompts
+
deployment metadata
```

Your object should be one abstraction higher:

```text
AGENT SYSTEM

orchestrator
+
control-flow architecture
+
agent roles
+
memory topology
+
models
+
tools
+
verification topology
+
task persistence
+
runtime requirements
+
operational commands
+
benchmarks
+
failure modes
+
architecture lineage
```

That distinction is huge.

---

# 2. `agentoperations/agent-registry` is another important one

This project explicitly describes itself as framework-agnostic and vendor-neutral and uses existing standards including:

```text
A2A AgentCard
MCP server.json
Agent Skills
OCI artifacts
```

It can retain evaluation records and promotion lifecycle metadata, but explicitly doesn't run the evaluations or calculate trust scores itself. ([GitHub][3])

This gives you another positioning lesson:

**Don't invent new standards unnecessarily.**

Your architecture manifest can reference existing objects:

```yaml
agent:
  a2a_card: ...

tools:
  mcp_servers: [...]

skills:
  agent_skills: [...]

artifacts:
  oci: ...
```

and add the missing architectural layer.

---

# 3. Google is already going after enterprise registry/governance

Google's new Agent Registry treats:

```text
Agent
McpServer
Endpoint
Skill
SkillRevision
Publisher
```

as first-class resources, with discovery and governance as core objectives. A2A-compatible agents can have their capabilities pulled from Agent Cards automatically. ([Google Cloud Documentation][1])

So you definitely don't want to pitch:

> “One place where a company can catalog its agents.”

Google and AWS can crush that feature.

Your product should instead ask:

> **What architectural system is this, how does it work, how well does it work, and can another agent instantiate it?**

That's much more interesting.

---

# 4. LangChain already has an agent template marketplace-ish layer

LangChain launched an Agent Builder Template Library in January 2026 with ready-to-deploy prebuilt agents containing instructions and connected tools. LangGraph also has repository templates such as a Deep Agent, simple Agent, and baseline LangGraph projects. ([LangChain][4])

Again, that's adjacent.

But the unit is:

```text
PREBUILT AGENT
```

rather than:

```text
RESEARCHED ARCHITECTURAL SYSTEM
```

There is no general cross-framework comparison like:

```text
Hermes VentureLab
vs
Loom
vs
LangGraph planner-worker
vs
Hound relation-graph investigator
vs
Letta persistent-memory architecture
```

under controlled tasks.

That is your niche.

---

# 5. AgentBeats owns an important part of the benchmark idea

This is probably your most important possible integration partner/reference.

AgentBeats is specifically developing standardized reproducible agent evaluation using:

```text
A2A → task/agent interaction
MCP → tools/resources
```

Their Agentified Agent Assessment model makes benchmark judges themselves agents, so arbitrary subject agents can be evaluated through a common interface. Their 2026 paper reports 298 judge agents and 467 subject agents across an open competition/study. ([AgentBeats][5])

AgentBeats already has:

* agent registry;
* assessments;
* public results;
* categories;
* competitions;
* leaderboards. ([AgentBeats][6])

So I would **not build a proprietary benchmarking protocol first**.

Make architecture builds export:

```text
A2A subject agent
```

where possible.

Then your layer can invoke AgentBeats assessments.

---

# Where AgentBeats stops and you begin

AgentBeats fundamentally evaluates:

```text
AGENT A
vs
ASSESSMENT B
```

Your platform's core object is:

```text
ARCHITECTURE
```

You care about what produced Agent A:

```text
Hermes
  +
persistent kanban
  +
specify/decompose
  +
5 parallel workers
  +
independent reviewer
  +
artifact certification
```

and you want to manipulate that architecture.

So:

```text
AgentBeats
"how did this submitted agent perform?"

YOU
"what is this agent made of,
what should it be used for,
how can I reproduce it,
what happens if I swap part X,
what are its descendants,
and which architecture should solve my task?"
```

Very complementary.

---

# There are also plenty of leaderboards

There are already projects aggregating public agent benchmarks. Steel maintains an open browser/coding-agent leaderboard, and other independent sites aggregate agent/model benchmark results. ([GitHub][7])

There's even an open AgentBench project that records things like agent version, organization, framework, model, runtime, verification state and reproducibility hashes and accepts community leaderboard submissions through GitHub PRs. ([GitHub][8])

So:

> “Leaderboard of agents”

is also insufficient differentiation.

Your leaderboard should be:

> **Leaderboard of architecture versions under controlled execution conditions.**

That is different.

---

# And there is research confirming architecture really matters

AgentArch specifically compares **18 different agentic configurations** across dimensions including orchestration, ReAct vs function calling, memory architecture and thinking tools. It finds model-specific architecture preferences rather than a universal winning design. ([arXiv][9])

That's very supportive of your resolver thesis.

If:

```text
architecture X + model A
```

works well but:

```text
architecture X + model B
```

doesn't, then there is real value in maintaining:

```text
P(success |
 task,
 architecture,
 model,
 environment)
```

rather than just ranking models.

---

# The whitespace I see

I couldn't find a serious platform combining all of these:

```text
DISCOVERY
+
ARCHITECTURE NORMALIZATION
+
OBJECTIVE USE-CASE DESCRIPTION
+
ONE-CLICK INSTANTIATION
+
CROSS-RUNTIME ADAPTERS
+
OPERATION/MANAGEMENT INTERFACE
+
ARCHITECTURE BENCHMARKING
+
ARCHITECTURE FORKING
+
STRUCTURAL DIFFS
+
LINEAGES
+
RESEARCH PAPER REPRODUCTIONS
+
ARCHITECTURE RESOLUTION
```

Pieces exist everywhere.

The **combined system** appears open.

---

# Your strongest positioning

Not:

> Agent Registry.

Not:

> Marketplace for agents.

Not even:

> GitHub for agents.

I'd make the main line something more like:

> **The registry and runtime for agent architectures.**

Or:

> **Discover, run, benchmark and fork complete agent systems.**

Then the bigger thesis:

> **Hugging Face made models reusable. MCP makes tools reusable. We make agent architectures reusable.**

That's concise and explains the missing abstraction.

---

# I particularly like “Agent Systems” as the term

Because something like `cuntgoblin` is clearly not merely an agent.

It is:

```text
Hermes
├─ coordinator
├─ kanban
├─ task decomposition
├─ workers[]
├─ reviewer
├─ certification
├─ run storage
└─ product sub-factories
```

Calling that an `Agent` loses almost all the important information.

I'd define:

```text
COMPONENT
model/tool/skill/MCP/memory

AGENT
one autonomous execution identity

ARCHITECTURE
structural pattern connecting components/agents

AGENT SYSTEM
runnable instantiation of an architecture
```

Then your registry handles all four but specializes in the last two.

---

# The homepage should visually make this distinction

Something like:

```text
Explore Agent Systems

┌─────────────────────┐
│ VentureLab Factory  │
│ Hermes              │
│                     │
│ Autonomous Product  │
│ Factory             │
│                     │
│ 12 forks            │
│ 58 tests            │
│ 84% benchmark       │
└─────────────────────┘

┌─────────────────────┐
│ Loom Delivery       │
│ Loom + Claude Code  │
│                     │
│ Durable Software    │
│ Delivery            │
│                     │
│ 83 forks            │
└─────────────────────┘

┌─────────────────────┐
│ Hound Investigator  │
│ Custom graph        │
│                     │
│ Relation-first      │
│ Investigation       │
└─────────────────────┘
```

Filters:

```text
Orchestrator
────────────
Hermes
LangGraph
Loom
Letta
Custom

Pattern
───────
Planner-worker
Worker-verifier
DAG
Swarm
Evolutionary
Persistent factory

Purpose
───────
Coding
Research
Security
Product factory
Browsing
Science

Maturity
────────
Research
Experimental
Verified
Production
```

---

# The strongest feature isn't search — it's RESOLVE

This is your Oracle mentality applied properly.

A coding agent sends:

```json
{
  "project": {
    "type": "large_existing_repo",
    "size": "large"
  },

  "task": "implement a major feature",

  "constraints": {
    "budget_usd": 5,
    "autonomy": "high",
    "must_verify": true
  }
}
```

You respond:

```text
Recommended:
Hermes Durable Builder v17

Why:
+ strong long-horizon task performance
+ persistent task graph
+ independent reviewer
+ resumes after failure

Not selected:
Loom-lite
- lower parallelism

LangGraph worker/verifier
- higher integration effort

Single coding agent
- lower historical completion rate
```

That's something none of the registries I found are primarily designed to do.

---

# And then RUN

Immediately:

```text
architecture.resolve
        ↓
architecture.doctor
        ↓
architecture.install
        ↓
architecture.start
```

The existing registries are moving strongly toward easy deployment—`agentregistry`, for example, already offers one-command-ish publishing and deployment across local/Kubernetes environments. ([GitHub][2])

Your differentiation therefore needs to be **architecture-aware installation**:

```text
Detect host = OpenCode

Need Hermes
Need board
Need 5 workers
Need reviewer role
Need skills X/Y
Need MCP A/B
Need hooks
Need local run store

→ compile everything automatically.
```

Not merely pull a Docker image.

---

# Community forks are still relatively distinctive

Existing registries version artifacts.

GitHub forks source.

But I'd make your fork unit an explicit **architectural mutation**:

```text
VentureLab v1
    │
    ├── Cheap v2
    │    worker_model changed
    │    parallelism 5 → 10
    │
    ├── Strict v2
    │    reviewers 1 → 2
    │
    └── DGM v2
         mutation engine added
```

Then compare descendants on the same benchmark.

That gives you:

```text
architecture genealogy
```

rather than normal semantic versions.

I did not find a registry centered around this.

---

# Paper → runnable system is another strong wedge

This could differentiate the research side heavily.

For every paper:

```text
arXiv paper
      ↓
architecture extraction
      ↓
Agent Architecture Manifest
      ↓
reference implementation
      ↓
benchmark
      ↓
REPRODUCED / PARTIAL / FAILED
      ↓
community forks
```

So instead of someone reading an agent paper and wondering:

> “How do I actually use this?”

your registry shows:

```text
RUN THIS ARCHITECTURE
```

This is much more interesting than another paper-with-code link.

---

# Be careful with registry descriptions

There is also a very relevant 2026 paper showing that agent/tool registry descriptions can strongly influence model selection through superficial marketing language, and proposing structured registry-controlled selection descriptions rather than provider-written advertising copy. ([arXiv][10])

This matches what we've been doing with Dell.

So don't allow:

> “REVOLUTIONARY WORLD'S BEST AUTONOMOUS AGENT!!!”

to feed your resolver.

Separate:

```text
CREATOR DESCRIPTION
```

from:

```text
REGISTRY FACTS
objective capabilities
requirements
benchmark results
observed failures
cost
maturity
```

That could actually become a differentiator.

---

# Use existing standards underneath

I would define your architecture format as a **superset/composition layer**, not another protocol war.

```text
Agent Architecture Manifest
            │
     ┌──────┼────────┐
     ▼      ▼        ▼
    A2A    MCP     Skills
 AgentCard server   SKILL.md
     │      │        │
     └──────┼────────┘
            ▼
           OCI
```

The existing registry literature already identifies MCP metadata, A2A Agent Cards and related agent-fact models as the major registry approaches. ([arXiv][11])

So build on them.

---

# The product map I would pursue

```text
                   AGENT SYSTEMS HUB
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
    DISCOVER             RESOLVE              BUILD
       │                   │                   │
 architectures         task→system        fork/mutate
 patterns              recommendation     compose
 papers                evidence           publish
 community builds
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                         RUN
                           │
                  runtime adapters
          Hermes / LangGraph / Loom / etc
                           │
                           ▼
                       BENCHMARK
                           │
                   AgentBeats/custom
                           │
                           ▼
                      LEADERBOARD
                           │
                           ▼
                        LINEAGE
```

That's much more differentiated than “Agent Registry.”

---

# What I would call the moat

Not the manifests.

Those will eventually commoditize.

The moat becomes accumulated:

```text
architecture/task outcomes
architecture/model interactions
failure modes
installation compatibility
real cost
runtime requirements
architectural diffs
fork lineages
benchmark histories
community adoption
```

So after 12 months you know:

```text
For this type of task,
on this kind of repo,
with this budget,
this architecture family succeeds 84% of the time.
```

A new registry cannot scrape that overnight.

---

# Competitive positioning in one chart

```text
                   COMPONENTS       COMPLETE SYSTEMS

DISCOVERY       Google Registry      YOUR HUB
                AWS Registry
                agentregistry

DEPLOYMENT      agentregistry        YOUR HUB

EVALUATION      tool evals           AgentBeats
                                     YOUR HUB

FORK/EVOLVE     GitHub-ish           YOUR HUB

DECISION        mostly missing       ARCHORACLE
```

I would therefore pitch the product as:

> **Agent Systems Hub — the open registry for runnable agent architectures. Discover complete systems, install them into your coding agent, benchmark them, fork them, and let the resolver choose the right architecture for your task.**

The most important strategic point is: **don't compete with Google/AWS/agentregistry on storing agents. Treat their registries, A2A, MCP, Skills, OCI, GitHub and AgentBeats as substrate. Your differentiated layer is understanding and optimizing the computational architecture formed by all those pieces.**

[1]: https://docs.cloud.google.com/agent-registry/overview?hl=en&utm_source=chatgpt.com "Agent Registry overview  |  Google Cloud Documentation"
[2]: https://github.com/agentregistry-dev/agentregistry?utm_source=chatgpt.com "GitHub - agentregistry-dev/agentregistry: Fast-track AI innovation with a centralized, trusted, curated registry · GitHub"
[3]: https://github.com/agentoperations/agent-registry?utm_source=chatgpt.com "GitHub - agentoperations/agent-registry: A vendor-neutral, agent-framework-agnostic registry for AI agents, skills, and MCP servers. Metadata store with evaluation signals, promotion lifecycle, and supply chain visibility. · GitHub"
[4]: https://www.langchain.com/blog/introducing-agent-builder-template-library?utm_source=chatgpt.com "Deploy agents instantly with Agent Builder templates"
[5]: https://docs.agentbeats.dev/?utm_source=chatgpt.com "Agentified Agent Assessment (AAA) & AgentBeats | AgentBeats"
[6]: https://agentbeats.dev/?utm_source=chatgpt.com "AgentBeats | Dashboard"
[7]: https://github.com/steel-dev/leaderboard?utm_source=chatgpt.com "GitHub - steel-dev/leaderboard: Open leaderboard for browser agents · GitHub"
[8]: https://github.com/OmnionixAI/AgentBench?utm_source=chatgpt.com "GitHub - OmnionixAI/AgentBench: A comprehensive evaluation framework and benchmark suite designed to rigorously assess the performance, reliability, and reasoning capabilities of autonomous AI agents. · GitHub"
[9]: https://arxiv.org/abs/2509.10769?utm_source=chatgpt.com "AgentArch: A Comprehensive Benchmark to Evaluate Agent Architectures in Enterprise"
[10]: https://arxiv.org/abs/2605.23916?utm_source=chatgpt.com "Agent-Facing Information Design in LLM Tool Registries"
[11]: https://arxiv.org/abs/2508.03095?utm_source=chatgpt.com "A Survey of AI Agent Registry Solutions"
