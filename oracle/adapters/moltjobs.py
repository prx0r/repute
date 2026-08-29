"""MoltJobs adapter — richest agent marketplace API.

API: https://api.moltjobs.io/v1/jobs
Field: budgetUsdc (not budget_usdc)
"""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Any


class MoltJobsAdapter:
    id = "moltjobs"
    name = "MoltJobs"
    base_url = "https://api.moltjobs.io/v1"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.environ.get("MOLTJOBS_API_KEY", "")

    def _get(self, url: str) -> Any:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-Api-Key"] = self.api_key
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except Exception as e:
            print(f"  [moltjobs] error: {e}")
            return None

    async def discover(self) -> list[dict]:
        data = self._get(f"{self.base_url}/jobs?limit=100")
        if not data:
            return []
        jobs = data if isinstance(data, list) else data.get("data", data.get("jobs", []))
        return [{"type": "job", "data": j} for j in jobs]

    def normalize(self, raw: dict) -> dict:
        data = raw.get("data", raw) if isinstance(raw, dict) else raw
        budget = data.get("budgetUsdc", data.get("budget", 0))
        if isinstance(budget, str):
            try: budget = float(budget.replace("$", ""))
            except: budget = 0

        return {
            "id": f"moltjobs:{data.get('id', '')}",
            "source": "moltjobs",
            "source_id": str(data.get("id", "")),
            "title": data.get("title", ""),
            "description": (data.get("inputData", "") or data.get("description", ""))[:2000],
            "url": f"https://moltjobs.io/jobs/{data.get('id', '')}",
            "type": "job",
            "category": data.get("vertical", data.get("templateId", "general")),
            "skills": [],
            "reward_advertised": float(budget) if budget else 0,
            "reward_currency": "USDC",
            "reward_usd": float(budget) if budget else 0,
            "buyer_id": data.get("posterId", ""),
            "status": data.get("status", "OPEN"),
            "posted_at": data.get("createdAt", data.get("deadlineAt", "")),
            "extra": {
                "template_id": data.get("templateId", ""),
                "auto_approved": data.get("autoApproved", False),
                "escrow_tx": data.get("escrowTxHash", ""),
            },
        }

    def health_check(self) -> bool:
        data = self._get(f"{self.base_url}/jobs?limit=1")
        return data is not None
