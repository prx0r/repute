# GitHub Bounties — Source Reference

**URL:** https://github.com
**API Base:** https://api.github.com
**Status:** Live, production
**Agent-friendly:** Yes (issues API)
**Payment:** Varies (crypto, fiat, platform-specific)
**Fee:** N/A (platform-dependent)

## Overview

GitHub issues are the primary bounty surface for many platforms (Algora, TaskBounty, etc.). Issues labeled "bounty" or containing dollar amounts in titles are the raw data source.

## API Surface

### Authentication
- OAuth token or personal access token
- Rate limit: 5000 req/hour (authenticated)

### Key Endpoints
```
GET  /repos/{owner}/{repo}/issues              # List issues
GET  /repos/{owner}/{repo}/issues/{number}     # Get issue
GET  /search/issues?q=label:bounty+is:open     # Search bounties
GET  /repos/{owner}/{repo}/labels              # List labels
GET  /repos/{owner}/{repo}/pulls               # PRs (linked to issues)
```

### Issue Object (Relevant Fields)
```json
{
  "id": "number",
  "number": "number",
  "title": "string",
  "body": "string (markdown)",
  "state": "open | closed",
  "labels": [{"name": "string", "description": "string"}],
  "user": {"login": "string", "id": "number"},
  "assignee": {"login": "string"} | null,
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp",
  "closed_at": "ISO timestamp | null",
  "comments": "number",
  "html_url": "string"
}
```

## Bounty Detection Patterns

### Label-based
- `bounty` label
- `💎 Bounty` (Algora convention)
- `reward` label
- `$$$` or `paid` labels

### Title-based regex
- `\$\d+` — dollar amounts
- `Bounty: \$\d+` — explicit bounty
- `(\d+)k?\s*(USD|USDC|ETH|SOL)` — crypto amounts

### Body-based
- Algora bounty blocks: `/bounty $1000`
- Platform-specific patterns

## Data Fields Available for Oracle

| Field | Confidence | Notes |
|-------|-----------|-------|
| issue.id | observed | native_id |
| issue.number | observed | |
| issue.title | observed | |
| issue.body | observed | full description |
| issue.state | observed | open/closed |
| issue.labels | observed | bounty detection |
| issue.user.login | observed | poster/buyer |
| issue.created_at | observed | lifecycle.posted_at |
| issue.closed_at | observed | lifecycle.completed_at |
| issue.comments | observed | competition signal |
| issue.html_url | observed | source_url |
| bounty_amount | inferred | from labels/title |
| repo.name | observed | project context |
| repo.language | observed | skills signal |
| linked_pr | observed | completion signal |
| pr.merged | verified | true completion signal |

## Derivable Metrics
- **Bounty frequency** per repo/org
- **Average bounty size** by language/category
- **Time-to-close** (posted → closed)
- **Competition** (comments, linked PRs)
- **Completion rate** (closed with PR merged vs without)

## Source Adapter Priority: HIGH
- Richest raw data source
- Every platform references GitHub
- Public API, no special access needed
- Deep history available
- Language/repo metadata = skills signal
