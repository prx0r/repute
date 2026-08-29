"""NEAR Agent Market adapter — 66 endpoints, real work tape.

API: https://market.near.ai/api-docs/
Data: jobs, bids, agents, services, escrow, disputes, payments
"""
from __future__ import annotations

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_agent_profile, store_platform_stat


class NEARMarketAdapter:
    id = "near_market"
    name = "NEAR Agent Market"
    base_url = "https://market.near.ai"

    def __init__(self):
        self.client = get_client("near_market", base_url=self.base_url, requests_per_minute=10)

    async def discover(self) -> list[dict]:
        items = []

        # Jobs — the main work feed
        jobs = self.client.get("/api/v1/jobs", params={"limit": 100, "filter": "hot"})
        if jobs:
            job_list = jobs if isinstance(jobs, list) else jobs.get("jobs", [])
            for j in job_list:
                items.append({"type": "job", "data": j})

        # Agents — directory
        agents = self.client.get("/api/v1/agents", params={"limit": 100})
        if agents:
            a_list = agents if isinstance(agents, list) else agents.get("agents", [])
            for a in a_list:
                items.append({"type": "agent", "data": a})
                store_agent_profile({
                    "id": f"near:{a.get('id', a.get('handle', ''))}",
                    "source": "near_market",
                    "source_agent_id": str(a.get("id", a.get("handle", ""))),
                    "name": a.get("name", a.get("handle", "")),
                    "description": a.get("description", "")[:500],
                    "url": f"https://market.near.ai/agents/{a.get('handle', a.get('id', ''))}",
                    "tier": a.get("tier", ""),
                    "reputation_score": a.get("reputation", 0),
                    "jobs_completed": a.get("jobs_completed", 0),
                    "total_earned_usd": a.get("earned", 0),
                    "success_rate": a.get("success_rate", 0),
                    "capabilities": a.get("skills", []),
                    "wallet_address": a.get("address", ""),
                    "chain": "near",
                    "extra": {"bids": a.get("bids", 0)},
                })

        # Services
        services = self.client.get("/api/v1/services", params={"limit": 100})
        if services:
            s_list = services if isinstance(services, list) else services.get("services", [])
            for s in s_list:
                items.append({"type": "service", "data": s})

        return items

    def normalize(self, raw: dict) -> dict:
        data = raw.get("data", raw) if isinstance(raw, dict) else raw
        item_type = raw.get("type", "job")

        if item_type == "job":
            return self._normalize_job(data)
        elif item_type == "agent":
            return self._normalize_agent(data)
        elif item_type == "service":
            return self._normalize_service(data)
        return self._normalize_job(data)

    def _normalize_job(self, data: dict) -> dict:
        reward = data.get("reward", data.get("budget", 0)) or 0
        if isinstance(reward, str):
            try: reward = float(reward.replace(",", ""))
            except: reward = 0
        return {
            "id": f"near:{data.get('id', '')}",
            "source": "near_market",
            "source_id": str(data.get("id", "")),
            "url": f"https://market.near.ai/jobs/{data.get('id', '')}",
            "title": data.get("title", ""),
            "description": (data.get("description") or "")[:500],
            "category": data.get("category", "general"),
            "skills": data.get("tags", []),
            "reward": float(reward),
            "currency": data.get("currency", "NEAR"),
            "reward_usd": float(reward),
            "fee_pct": 2.5,
            "escrowed": True,
            "entries": data.get("bids_count", 0),
            "views": 0,
            "slots": 1,
            "posted_at": data.get("created_at", ""),
            "deadline": data.get("deadline"),
            "last_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": None,
            "agent_allowed": True,
            "submission_method": "api",
            "auth_type": "wallet",
            "network": "near",
            "buyer_id": data.get("creator", data.get("poster", "")),
            "buyer_reputation": None,
            "buyer_historical_spend_usd": None,
            "raw": data,
        }

    def _normalize_agent(self, data: dict) -> dict:
        return {
            "id": f"near:{data.get('id', data.get('handle', ''))}",
            "source": "near_market",
            "source_id": str(data.get("id", data.get("handle", ""))),
            "url": f"https://market.near.ai/agents/{data.get('handle', data.get('id', ''))}",
            "title": data.get("name", data.get("handle", "")),
            "description": (data.get("description") or "")[:500],
            "category": "agent",
            "skills": data.get("skills", []),
            "reward": 0,
            "currency": "NEAR",
            "reward_usd": data.get("earned", 0),
            "fee_pct": 0,
            "escrowed": False,
            "entries": data.get("jobs_completed", 0),
            "views": 0,
            "slots": 0,
            "posted_at": data.get("joined_at", ""),
            "deadline": None,
            "last_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": None,
            "agent_allowed": True,
            "submission_method": "api",
            "auth_type": "wallet",
            "network": "near",
            "buyer_id": "",
            "buyer_reputation": None,
            "buyer_historical_spend_usd": None,
            "raw": data,
        }

    def _normalize_service(self, data: dict) -> dict:
        price = data.get("price", data.get("price_per_call", 0)) or 0
        return {
            "id": f"near:svc:{data.get('id', '')}",
            "source": "near_market",
            "source_id": str(data.get("id", "")),
            "url": f"https://market.near.ai/services/{data.get('id', '')}",
            "title": data.get("name", ""),
            "description": (data.get("description") or "")[:500],
            "category": data.get("category", "general"),
            "skills": data.get("capabilities", []),
            "reward": float(price),
            "currency": "USDC",
            "reward_usd": float(price),
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
            "submission_method": "api",
            "auth_type": "wallet",
            "network": "near",
            "buyer_id": "",
            "buyer_reputation": None,
            "buyer_historical_spend_usd": None,
            "raw": data,
        }

    def health_check(self) -> bool:
        r = self.client.get("/api/v1/jobs", params={"limit": 1})
        return r is not None
