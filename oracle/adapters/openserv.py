"""OpenServ Ideaboard adapter — ideas → x402 endpoints.

API: https://api.launch.openserv.ai
Status: ✅ Working
"""
from __future__ import annotations

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_service_listing, store_platform_stat


class OpenServAdapter:
    id = "openserv"
    name = "OpenServ Ideaboard"
    base_url = "https://api.launch.openserv.ai"

    def __init__(self):
        self.client = get_client("openserv", base_url=self.base_url, requests_per_minute=10)

    async def discover(self) -> list[dict]:
        items = []

        # Ideas
        ideas = self.client.get("/ideas", params={"limit": 100})
        if ideas:
            idea_list = ideas if isinstance(ideas, list) else ideas.get("ideas", [])
            for idea in idea_list:
                items.append({"type": "idea", "data": idea})

        # Top agents
        agents = self.client.get("/ideas/top-agents", params={"limit": 50})
        if agents:
            agent_list = agents if isinstance(agents, list) else agents.get("agents", [])
            for a in agent_list:
                items.append({"type": "agent", "data": a})

        return items

    def normalize(self, raw: dict) -> dict:
        data = raw.get("data", raw) if isinstance(raw, dict) else raw
        item_type = raw.get("type", "idea")

        if item_type == "idea":
            return self._normalize_idea(data)
        elif item_type == "agent":
            return self._normalize_agent(data)
        return self._normalize_idea(data)

    def _normalize_idea(self, data: dict) -> dict:
        upvotes = data.get("upvotes", [])
        pickups = data.get("pickups", [])
        return {
            "id": f"openserv:{data.get('id', '')}",
            "source": "openserv",
            "source_id": str(data.get("id", "")),
            "url": f"https://openserv.ai/idea/{data.get('id', '')}",
            "title": data.get("title", ""),
            "description": (data.get("description") or "")[:500],
            "category": data.get("tags", ["general"])[0] if data.get("tags") else "general",
            "skills": data.get("tags", []),
            "reward": 0,
            "currency": "x402",
            "reward_usd": 0,
            "fee_pct": 0,
            "escrowed": False,
            "entries": len(pickups),
            "views": len(upvotes),
            "slots": 1,
            "posted_at": data.get("createdAt", ""),
            "deadline": None,
            "last_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": None,
            "agent_allowed": True,
            "submission_method": "x402",
            "auth_type": "wallet",
            "network": "base",
            "buyer_id": "",
            "buyer_reputation": None,
            "buyer_historical_spend_usd": None,
            "raw": data,
        }

    def _normalize_agent(self, data: dict) -> dict:
        return {
            "id": f"openserv:agent:{data.get('wallet', data.get('id', ''))}",
            "source": "openserv",
            "source_id": str(data.get("wallet", data.get("id", ""))),
            "url": f"https://openserv.ai/agent/{data.get('wallet', '')}",
            "title": data.get("name", data.get("wallet", "")[:10]),
            "description": "",
            "category": "agent",
            "skills": data.get("capabilities", []),
            "reward": 0,
            "currency": "x402",
            "reward_usd": 0,
            "fee_pct": 0,
            "escrowed": False,
            "entries": 0,
            "views": 0,
            "slots": 0,
            "posted_at": data.get("createdAt", ""),
            "deadline": None,
            "last_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": None,
            "agent_allowed": True,
            "submission_method": "x402",
            "auth_type": "wallet",
            "network": "base",
            "buyer_id": "",
            "buyer_reputation": None,
            "buyer_historical_spend_usd": None,
            "raw": data,
        }

    def health_check(self) -> bool:
        r = self.client.get("/ideas", params={"limit": 1})
        return r is not None
