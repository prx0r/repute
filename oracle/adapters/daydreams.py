"""Daydreams TaskMarket adapter — 5 task modes, on-chain escrow, ERC-8004."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client


class DaydreamsAdapter:
    id = "daydreams"
    name = "Daydreams TaskMarket"
    base_url = "https://taskmarket.dev"

    def __init__(self):
        self.client = get_client("daydreams", base_url=self.base_url)

    async def discover(self) -> list[dict]:
        tasks = self.client.get("/api/tasks", params={"limit": 100, "status": "open"})
        if not tasks:
            return []
        return tasks if isinstance(tasks, list) else tasks.get("tasks", [])

    def normalize(self, raw: dict) -> dict:
        # Daydreams reward is in chain smallest unit (6 decimals for USDC on Base)
        reward_raw = raw.get("reward", 0)
        if isinstance(reward_raw, str):
            try: reward_raw = float(reward_raw)
            except: reward_raw = 0
        # Convert from smallest unit to USDC (6 decimals)
        reward_usdc = reward_raw / 1_000_000 if reward_raw > 1000 else reward_raw

        net_reward = raw.get("netReward", 0)
        if isinstance(net_reward, str):
            try: net_reward = float(net_reward)
            except: net_reward = 0
        net_usdc = net_reward / 1_000_000 if net_reward > 1000 else net_reward

        return {
            "id": f"daydreams:{raw.get('id', raw.get('task_id', ''))}",
            "source": "daydreams",
            "source_id": str(raw.get("id", raw.get("task_id", ""))),
            "title": raw.get("description", "")[:100] or raw.get("title", ""),
            "description": raw.get("description", "")[:2000],
            "url": f"https://taskmarket.dev/task/{raw.get('id', '')}",
            "type": raw.get("mode", "bounty"),
            "category": raw.get("tags", ["general"])[0] if raw.get("tags") else "general",
            "skills": raw.get("tags", []),
            "reward_advertised": round(reward_usdc, 6),
            "reward_currency": "USDC",
            "reward_usd": round(reward_usdc, 6),
            "buyer_id": raw.get("requester", ""),
            "status": raw.get("status", "open").lower(),
            "posted_at": raw.get("createdAt", ""),
            "extra": {
                "mode": raw.get("mode", "bounty"),
                "chain": raw.get("chain", "base"),
                "escrow_tx": raw.get("escrowTxHash", ""),
                "net_reward_usdc": round(net_usdc, 6),
                "submission_count": raw.get("submissionCount", 0),
                "award_count": raw.get("awardCount", 0),
            },
        }

    def health_check(self) -> bool:
        r = self.client.get("/api/tasks", params={"limit": 1})
        return r is not None
