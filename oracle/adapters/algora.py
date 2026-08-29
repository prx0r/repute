"""Algora bounties adapter.

Public API, no auth required. Richest OSS bounty data.
"""
from __future__ import annotations

import json
import urllib.request
from typing import Any


class AlgoraAdapter:
    """Algora open-source bounties adapter."""

    id = "algora"
    name = "Algora"
    base_url = "https://algora.io/api"

    def __init__(self):
        pass

    def _get(self, url: str) -> Any:
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except Exception as e:
            print(f"  [algora] error fetching {url}: {e}")
            return None

    async def discover(self) -> list[dict]:
        """Fetch open bounties from Algora public API."""
        results = []

        # Try the bounties endpoint
        data = self._get(f"{self.base_url}/bounties?status=open&limit=100")
        if data and isinstance(data, list):
            results.extend(data)
        elif data and isinstance(data, dict) and "bounties" in data:
            results.extend(data["bounties"])

        # Also try org-based discovery for known orgs
        for org in ["cal", "supabase", "turso", "prettier"]:
            org_data = self._get(f"{self.base_url}/bounties?org={org}&status=open&limit=50")
            if org_data:
                items = org_data if isinstance(org_data, list) else org_data.get("bounties", [])
                for item in items:
                    if not any(r.get("id") == item.get("id") for r in results):
                        results.append(item)

        return results

    def normalize(self, raw: dict) -> dict:
        """Convert Algora bounty to canonical opportunity format."""
        amount = 0
        if isinstance(raw.get("amount"), (int, float)):
            amount = raw["amount"]
        elif isinstance(raw.get("amount"), str):
            try:
                amount = float(raw["amount"].replace("$", "").replace(",", ""))
            except ValueError:
                pass

        org = raw.get("org", {})
        repo = raw.get("repo", {})
        issue = raw.get("issue", {})

        skills = []
        lang = repo.get("language", "")
        if lang:
            skills.append(lang.lower())

        return {
            "id": f"algora:{raw.get('id', '')}",
            "source": "algora",
            "source_id": str(raw.get("id", "")),
            "title": raw.get("title", ""),
            "description": (raw.get("description") or "")[:2000],
            "url": raw.get("html_url", issue.get("url", "")),
            "type": "bounty",
            "category": "development",
            "skills": skills,
            "reward_advertised": amount,
            "reward_currency": "USD",
            "reward_usd": amount,
            "buyer_id": org.get("slug", ""),
            "buyer_name": org.get("name", ""),
            "status": "open" if raw.get("status") == "open" else "completed",
            "posted_at": raw.get("created_at", ""),
            "completed_at": raw.get("awarded_at") or "",
            "proposals_count": raw.get("comments_count", 0),
            "extra": {
                "org_name": org.get("name", ""),
                "org_slug": org.get("slug", ""),
                "repo_full_name": repo.get("full_name", ""),
                "repo_language": repo.get("language", ""),
                "repo_stars": repo.get("stars", 0),
                "solver": raw.get("solver", {}),
            },
        }

    def health_check(self) -> bool:
        data = self._get(f"{self.base_url}/bounties?limit=1")
        return data is not None
