"""RentAHuman adapter — physical-world tasks for agents.

API: https://rentahuman.ai/api/bounties
Status: ✅ Working
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_agent_profile, store_platform_stat


class RentAHumanAdapter:
    id = "rentahuman"
    name = "RentAHuman"
    base_url = "https://rentahuman.ai"

    def __init__(self):
        self.client = get_client("rentahuman", base_url=self.base_url, requests_per_minute=10)

    async def discover(self) -> list[dict]:
        items = []
        # API is at /api/bounties (not /api/v1/bounties)
        bounties = self.client.get("/api/bounties", params={"limit": 100})
        if bounties:
            b_list = bounties if isinstance(bounties, list) else bounties.get("bounties", [])
            for b in b_list:
                items.append({"type": "bounty", "data": b})

        services = self.client.get("/api/services", params={"limit": 100})
        if services:
            s_list = services if isinstance(services, list) else services.get("services", [])
            for s in s_list:
                items.append({"type": "service", "data": s})

        return items

    def normalize(self, raw: dict) -> dict:
        data = raw.get("data", raw) if isinstance(raw, dict) else raw
        price = data.get("price", 0)
        if isinstance(price, str):
            try: price = float(price.replace("$", ""))
            except: price = 0

        return {
            "id": f"rentahuman:{data.get('id', '')}",
            "source": "rentahuman",
            "source_id": str(data.get("id", "")),
            "title": data.get("title", ""),
            "description": data.get("description", "")[:2000],
            "url": f"https://rentahuman.ai/bounty/{data.get('id', '')}",
            "type": "physical_task",
            "category": data.get("category", "general"),
            "skills": data.get("skillsNeeded", []),
            "reward_advertised": float(price) if price else 0,
            "reward_currency": data.get("currency", "USD"),
            "reward_usd": float(price) if price else 0,
            "buyer_id": data.get("requester_id", ""),
            "status": data.get("status", "open"),
            "posted_at": data.get("createdAt", ""),
            "extra": {
                "location": data.get("location", ""),
                "estimated_hours": data.get("estimatedHours", 0),
                "spots_available": data.get("spotsAvailable", 0),
                "application_count": data.get("applicationCount", 0),
            },
        }

    def health_check(self) -> bool:
        r = self.client.get("/api/bounties", params={"limit": 1})
        return r is not None
