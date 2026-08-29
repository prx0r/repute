# Canonical Templates per Factory Type

*Standardized templates for different product types*

---

## 1. API/MCP Factory

For: Knee, EndpointTruth, MCPTruth, Toolloader, FallbackGraph

```text
Template Structure:
├── app/
│   ├── __init__.py
│   ├── api.py          # FastAPI endpoints
│   ├── db.py           # Database operations
│   ├── models.py       # Data models
│   ├── schemas.py      # Pydantic schemas
│   └── mcp.py          # MCP server
├── tests/
│   ├── test_api.py
│   ├── test_db.py
│   └── test_mcp.py
├── data/
│   └── runs/           # Evidence logs
├── docs/
│   └── README.md
├── requirements.txt
├── Dockerfile
└── factory.yaml
```

### Certification Checklist
- [ ] Clean install from empty database
- [ ] Deterministic fixtures
- [ ] Schema valid
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] API contract valid
- [ ] MCP contract valid
- [ ] Content hashes computed
- [ ] Provenance tracked
- [ ] Documentation exists

---

## 2. Content Factory

For: Research reports, market analysis, documentation

```text
Template Structure:
├── content/
│   ├── index.md        # Content index
│   ├── sections/       # Content sections
│   └── assets/         # Images, diagrams
├── metadata/
│   ├── topics.json     # Topic tags
│   ├── sources.json    # Source references
│   └── evidence.json   # Evidence links
├── build/
│   └── generate.py     # Content generation
├── tests/
│   └── test_content.py
└── factory.yaml
```

### Certification Checklist
- [ ] Content structure valid
- [ ] Topics properly tagged
- [ ] Sources referenced
- [ ] Evidence linked
- [ ] No verbosity
- [ ] Merkle/verified where applicable

---

## 3. Dataset Factory

For: Market research, benchmarks, intelligence

```text
Template Structure:
├── data/
│   ├── raw/            # Raw data
│   ├── processed/      # Processed data
│   └── exports/        # Export formats
├── schema/
│   └── schema.json     # Data schema
├── pipeline/
│   ├── ingest.py       # Data ingestion
│   ├── transform.py    # Data transformation
│   └── validate.py     # Data validation
├── tests/
│   └── test_data.py
├── docs/
│   └── README.md
└── factory.yaml
```

### Certification Checklist
- [ ] Schema valid
- [ ] Data ingested
- [ ] Transformations correct
- [ ] Validation passes
- [ ] Exports work
- [ ] Documentation exists

---

## 4. MCP Server Factory

For: Tool servers, integration points

```text
Template Structure:
├── server/
│   ├── __init__.py
│   ├── server.py       # MCP server
│   ├── tools/          # Tool implementations
│   └── schemas/        # Tool schemas
├── tests/
│   ├── test_server.py
│   └── test_tools.py
├── docs/
│   └── README.md
├── package.json
└── factory.yaml
```

### Certification Checklist
- [ ] Server starts
- [ ] Tools list works
- [ ] Tool invocation works
- [ ] Schemas valid
- [ ] Error handling works
- [ ] Documentation exists

---

## Template Selection

The factory selects template based on:
- Product type (from idea)
- Target customers
- Revenue model
- Technical requirements

```python
def select_template(idea):
    if idea.type == "api":
        return "api-mcp"
    elif idea.type == "content":
        return "content"
    elif idea.type == "dataset":
        return "dataset"
    elif idea.type == "mcp":
        return "mcp-server"
    else:
        return "api-mcp"  # default
```

---

*Canonical templates v1.0*
