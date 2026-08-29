"""Virtuals ACP adapter — agent-to-agent commerce.

Scanner: https://app.virtuals.io/acp/scan/agents
SDK: https://github.com/Virtual-Protocol/acp-node-v2
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_service_listing, store_agent_profile, store_platform_stat


class VirtualsACPAdapter:
    id = "virtuals"
    name = "Virtuals ACP"
    base_url = "https://acp.virtuals.io"

    def __init__(self):
        self.client = get_client("virtuals", base_url=self.base_url, requests_per_minute=10)

    async def discover(self) -> list[dict]:
        items = []

        # Try scanner API
        agents = self.client.get("/api/agents", params={"limit": 100, "sort": "SUCCESSFUL_JOB_COUNT"})
        if agents:
            agent_list = agents if isinstance(agents, list) else agents.get("agents", [])
            for a in agent_list:
                items.append({"type": "agent", "data": a})
                store_agent_profile({
                    "id": f"virtuals:{a.get('wallet', a.get('id', ''))}",
                    "source": "virtuals",
                    "source_agent_id": str(a.get("wallet", a.get("id", ""))),
                    "name": a.get("name", ""),
                    "description": a.get("description", "")[:500],
                    "url": f"https://app.virtuals.io/acp/agent/{a.get('wallet', '')}",
                    "tier": a.get("tier", ""),
                    "reputation_score": a.get("success_rate", 0),
                    "jobs_completed": a.get("successful_job_count", 0),
                    "total_earned_usd": a.get("revenue", 0),
                    "success_rate": a.get("success_rate", 0),
                    "capabilities": a.get("capabilities", []),
                    "wallet_address": a.get("wallet", ""),
                    "chain": "base",
                    "extra": {
                        "unique_buyers": a.get("unique_buyer_count", 0),
                        "online": a.get("online", False),
                        "minutes_since_online": a.get("minutes_since_online", 0),
                    },
                })

        # Try offerings
        offerings = self.client.get("/api/offerings", params={"limit": 100})
        if offerings:
            off_list = offerings if isinstance(offerings, list) else offerings.get("offerings", [])
            for o in off_list:
                items.append({"type": "offering", "data": o})

        return items

    def normalize(self, raw: dict) -> dict:
        data = raw.get("data", raw) if isinstance(raw, dict) else raw
        item_type = raw.get("type", "agent")

        if item_type == "agent":
            return self._normalize_agent(data)
        elif item_type == "offering":
            return self._normalize_offering(data)
        return self._normalize_agent(data)

    def _normalize_agent(self, data: dict) -> dict:
        return {
            "id": f"virtuals:{data.get('wallet', data.get('id', ''))}",
            "source": "virtuals",
            "source_id": str(data.get("wallet", data.get("id", ""))),
            "url": f"https://app.virtuals.io/acp/agent/{data.get('wallet', '')}",
            "title": data.get("name", ""),
            "description": (data.get("description") or "")[:500],
            "category": "agent",
            "skills": data.get("capabilities", []),
            "reward": 0,
            "currency": "USDC",
            "reward_usd": data.get("revenue", 0),
            "fee_pct": 0,
            "escrowed": False,
            "entries": data.get("successful_job_count", 0),
            "views": 0,
            "slots": 0,
            "posted_at": data.get("created_at", ""),
            "deadline": None,
            "last_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": None,
            "agent_allowed": True,
            "submission_method": "sdk",
            "auth_type": "wallet",
            "network": "base",
            "buyer_id": "",
            "buyer_reputation": None,
            "buyer_historical_spend_usd": None,
            "raw": data,
        }

    def _normalize_offering(self, data: dict) -> dict:
        return {
            "id": f"virtuals:offering:{data.get('id', '')}",
            "source": "virtuals",
            "source_id": str(data.get("id", "")),
            "url": data.get("url", ""),
            "title": data.get("name", ""),
            "description": (data.get("description") or "")[:500],
            "category": data.get("category", "service"),
            "skills": data.get("capabilities", []),
            "reward": data.get("price", 0),
            "currency": "USDC",
            "reward_usd": data.get("price", 0),
            "fee_pct": 0,
            "escrowed": True,
            "entries": 0,
            "views": 0,
            "slots": 0,
            "posted_at": data.get("created_at", ""),
            "deadline": None,
            "last_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": None,
            "agent_allowed": True,
            "submission_method": "sdk",
            "auth_type": "wallet",
            "network": "base",
            "buyer_id": "",
            "buyer_reputation": None,
            "buyer_historical_spend_usd": None,
            "raw": data,
        }

    def health_check(self) -> bool:
        r = self.client.get("/api/agents", params={"limit": 1})
        return r is not None
