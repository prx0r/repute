# Market Research Structure

*Clean, verified, meta-tagged market research*

---

## Structure

```text
market-research/
├── global/
│   ├── ai-agents-2026.json
│   ├── llm-infrastructure-2026.json
│   └── mcp-ecosystem-2026.json
├── verticals/
│   ├── agent-infrastructure/
│   ├── brainwave-technology/
│   ├── research-intelligence/
│   └── climate-intelligence/
├── topics/
│   ├── mcp.json
│   ├── llm-routing.json
│   ├── agent-tools.json
│   └── cost-optimization.json
└── evidence/
    ├── arxiv/
    ├── github/
    └── market/
```

---

## Data Format

Each research entry:

```json
{
  "id": "research_001",
  "topic": "mcp-adoption",
  "vertical": "agent-infrastructure",
  "finding": "MCP adoption accelerating in 2026",
  "evidence": [
    {
      "type": "arxiv",
      "source": "https://arxiv.org/abs/...",
      "verified": true,
      "hash": "sha256:..."
    }
  ],
  "meta_tags": ["mcp", "agents", "2026", "adoption"],
  "confidence": 0.85,
  "collected_at": "2026-08-18T14:00:00Z",
  "verified_at": "2026-08-18T14:05:00Z"
}
```

---

## Verification

Every research entry must have:
- Verified source (arxiv, github, market data)
- Content hash
- Timestamp
- Confidence score
- Meta-tags

---

## Verbosity Removal

Research should be:
- Fact-based (no opinions)
- Numbers-focused (market size, growth rate)
- Source-linked (every claim has a source)
- Concise (max 100 words per finding)

---

## Global Layer

Pool research across 4 factories:
- Agent Infrastructure
- Brainwave Technology
- Research Intelligence
- Climate Intelligence

Enable crossover labs:
- Agent + Brainwave
- Agent + Research
- Agent + Climate
- Brainwave + Research

---

*Market research structure v1.0*
