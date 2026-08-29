"""TaskForce adapter — 0% fee, milestone escrow, AI dispute resolution."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client


class TaskForceAdapter:
    id = "taskforce"
    name = "TaskForce"
    base_url = "https://taskforce.app/api"

    def __init__(self):
        self.client = get_client("taskforce", base_url=self.base_url)

    async def discover(self) -> list[dict]:
        tasks = self.client.get("/tasks", params={"limit": 100, "status": "open"})
        if not tasks:
            return []
        return tasks if isinstance(tasks, list) else tasks.get("tasks", [])

    def normalize(self, raw: dict) -> dict:
        budget = raw.get("budget_usdc", raw.get("budget", 0))
        milestones = raw.get("milestones", [])
        return {
            "id": f"taskforce:{raw.get('id', raw.get('task_id', ''))}",
            "source": "taskforce",
            "source_id": str(raw.get("id", raw.get("task_id", ""))),
            "title": raw.get("title", raw.get("name", "")),
            "description": raw.get("description", raw.get("goal", ""))[:2000],
            "url": f"https://task-force.app/task/{raw.get('id', '')}",
            "type": "task",
            "category": raw.get("category", "development"),
            "skills": raw.get("skills_required", raw.get("skills", [])),
            "reward_advertised": float(budget) if budget else 0,
            "reward_currency": "USDC",
            "reward_usd": float(budget) if budget else 0,
            "buyer_id": raw.get("poster_id", raw.get("client_id", "")),
            "status": raw.get("status", "open"),
            "posted_at": raw.get("created_at", ""),
            "extra": {
                "milestones_count": len(milestones),
                "dispute_resolution": "3-model AI (Gemini, Claude, DeepSeek)",
                "chain": raw.get("chain", "solana"),
            },
        }

    def health_check(self) -> bool:
        r = self.client.get("/tasks", params={"limit": 1})
        return r is not None
