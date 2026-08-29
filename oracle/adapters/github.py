"""GitHub adapter — comprehensive data extraction.

Endpoints called:
  /repos/{owner}/{repo}/issues      — repo-specific issues
  /search/issues?q=label:bounty     — global bounty search

Data extracted:
  - Bounty issues with amounts, labels, assignees
  - Time-to-close analytics
  - Repo-level bounty frequency
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_platform_stat


class GitHubAdapter:
    id = "github"
    name = "GitHub"
    base_url = "https://api.github.com"

    BOUNTY_LABELS = {"bounty", "💎 bounty", "reward", "$$$", "paid", "bug-bounty", "security-bounty", "oss-bounty"}
    BOUNTY_PATTERNS = [
        re.compile(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\b'),
        re.compile(r'Bounty:\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', re.IGNORECASE),
    ]

    def __init__(self, token: str = ""):
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.client = get_client("github", base_url=self.base_url,
                                 requests_per_minute=30, requests_per_hour=5000)

    def _get(self, url: str) -> dict | None:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except Exception:
            return None

    async def discover(self) -> list[dict]:
        items = []

        # 1. Global bounty search
        query = "label:bounty+is:open+is:issue"
        data = self._get(f"{self.base_url}/search/issues?q={query}&per_page=100&sort=created&order=desc")
        if data and "items" in data:
            for issue in data["items"]:
                if self._is_bounty(issue):
                    items.append({"type": "bounty", "data": issue})

                    # 2. Linked PRs (completion signal) — skip to avoid rate limiting
                    # PR data is a bonus, not required for ingestion

        return items

    def _is_bounty(self, issue: dict) -> bool:
        labels = {l.get("name", "").lower() for l in issue.get("labels", [])}
        if labels & self.BOUNTY_LABELS:
            return True
        title = issue.get("title", "").lower()
        if any(p in title for p in ["bounty", "reward", "paid"]):
            return True
        text = f"{issue.get('title', '')} {issue.get('body', '')[:500]}"
        for pattern in self.BOUNTY_PATTERNS:
            if pattern.search(text):
                return True
        return False

    def _extract_amount(self, issue: dict) -> float:
        text = f"{issue.get('title', '')} {issue.get('body', '')[:500]}"
        for pattern in self.BOUNTY_PATTERNS:
            match = pattern.search(text)
            if match:
                try:
                    return float(match.group(1).replace(",", ""))
                except ValueError:
                    continue
        return 0.0

    def normalize(self, raw: dict) -> dict:
        import json as _json
        item_type = raw.get("type", "bounty")
        data = raw.get("data", raw)

        if item_type == "bounty":
            return self._normalize_issue(data)
        elif item_type == "linked_prs":
            return self._normalize_linked_prs(data)
        return self._normalize_issue(data)

    def _normalize_issue(self, data: dict) -> dict:
        repo_url = data.get("repository_url", data.get("html_url", ""))
        repo_name = "/".join(repo_url.rstrip("/").split("/")[-2:]) if "/" in repo_url else ""

        return {
            "id": f"github:{repo_name}#{data.get('number', '')}",
            "source": "github",
            "source_id": f"{repo_name}#{data.get('number', '')}",
            "title": data.get("title", ""),
            "description": (data.get("body") or "")[:2000],
            "url": data.get("html_url", ""),
            "type": "bounty",
            "category": "development",
            "skills": [],
            "reward_advertised": self._extract_amount(data),
            "reward_currency": "USD",
            "reward_usd": self._extract_amount(data),
            "buyer_id": data.get("user", {}).get("login", ""),
            "buyer_name": data.get("user", {}).get("login", ""),
            "status": "completed" if data.get("state") == "closed" else "open",
            "posted_at": data.get("created_at", ""),
            "completed_at": data.get("closed_at") or "",
            "proposals_count": data.get("comments", 0),
            "extra": {
                "labels": [l.get("name", "") for l in data.get("labels", [])],
                "repo": repo_name,
                "assignee": data.get("assignee", {}).get("login") if data.get("assignee") else None,
                "reactions": data.get("reactions", {}).get("total_count", 0),
            },
        }

    def _normalize_linked_prs(self, data: dict) -> dict:
        merged_count = sum(1 for pr in data.get("prs", []) if pr.get("merged"))
        return {
            "id": f"github:prs:{data.get('repo', '')}#{data.get('issue', '')}",
            "source": "github",
            "source_id": f"prs:{data.get('repo', '')}#{data.get('issue', '')}",
            "title": f"PRs for {data.get('repo', '')}#{data.get('issue', '')}",
            "description": f"{len(data.get('prs', []))} PRs, {merged_count} merged",
            "url": "",
            "type": "linked_prs",
            "category": "verification",
            "skills": [],
            "reward_advertised": 0,
            "reward_currency": "USD",
            "reward_usd": 0,
            "buyer_id": "",
            "status": "completed" if merged_count > 0 else "open",
            "extra": {
                "total_prs": len(data.get("prs", [])),
                "merged_prs": merged_count,
                "prs": data.get("prs", []),
            },
        }

    def health_check(self) -> bool:
        r = self._get(f"{self.base_url}/rate_limit")
        return r is not None


def _extract_issue_numbers(pr: dict) -> list[int]:
    """Extract issue numbers referenced in a PR body."""
    body = pr.get("body", "") or ""
    numbers = re.findall(r'(?:fixes|closes|resolves)\s+#(\d+)', body, re.IGNORECASE)
    return [int(n) for n in numbers]
