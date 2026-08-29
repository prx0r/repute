"""Olas Network adapter — comprehensive data extraction.

Endpoints called:
  /api/services               — Mech Marketplace services
  /api/services/:id           — individual service details
  /api/stats                  — platform stats
  /api/emissions              — OLAS emission data

Data extracted:
  - Agent-to-agent service listings
  - Service detail with pricing and operator data
  - OLAS emission tracking
  - Cross-chain activity (Ethereum, Gnosis, Polygon, Solana)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_service_listing, store_platform_stat


class OlasAdapter:
    id = "olas"
    name = "Olas/Mech Marketplace"
    base_url = "https://marketplace.olas.network"

    def __init__(self):
        self.client = get_client("olas", base_url=self.base_url)

    async def discover(self) -> list[dict]:
        items = []

        # 1. Services
        services = self.client.get("/api/services", params={"limit": 100})
        if services:
            s_list = services if isinstance(services, list) else services.get("services", [])
            for s in s_list:
                items.append({"type": "service", "data": s})
                store_service_listing({
                    "id": f"olas:{s.get('id', s.get('service_id', ''))}",
                    "source": "olas",
                    "source_service_id": str(s.get("id", s.get("service_id", ""))),
                    "title": s.get("name", s.get("description", "")[:80]),
                    "description": s.get("description", "")[:2000],
                    "url": f"https://marketplace.olas.network/ethereum/ai-agents/{s.get('id', '')}",
                    "category": "ai-agent",
                    "price_usdc": s.get("price", 0),
                    "price_per_call": s.get("price", 0),
                    "provider_id": s.get("creator", ""),
                    "provider_reputation": 0,
                    "total_calls": s.get("request_count", 0),
                    "status": "active" if s.get("registered", True) else "inactive",
                    "capabilities": s.get("tags", []),
                    "extra": {
                        "chain": s.get("chain", "ethereum"),
                        "agent_address": s.get("agent_address", ""),
                        "operator_count": s.get("operator_count", 0),
                        "staked_olas": s.get("staked_olas", 0),
                    },
                })

        # 2. Emissions
        emissions = self.client.get("/api/emissions")
        if emissions:
            items.append({"type": "emissions", "data": emissions})

        # 3. Stats
        stats = self.client.get("/api/stats")
        if stats:
            items.append({"type": "platform_stats", "data": stats})

        return items

    def normalize(self, raw: dict) -> dict:
        item_type = raw.get("type", "service")
        data = raw.get("data", raw)

        if item_type == "service":
            return self._normalize_service(data)
        elif item_type == "emissions":
            return self._normalize_emissions(data)
        elif item_type == "platform_stats":
            return self._normalize_stats(data)
        return self._normalize_service(data)

    def _normalize_service(self, data: dict) -> dict:
        return {
            "id": f"olas:{data.get('id', data.get('service_id', ''))}",
            "source": "olas",
            "source_id": str(data.get("id", data.get("service_id", ""))),
            "title": data.get("name", data.get("description", "")[:80]),
            "description": data.get("description", "")[:2000],
            "url": f"https://marketplace.olas.network/ethereum/ai-agents/{data.get('id', '')}",
            "type": "service",
            "category": "ai-agent",
            "skills": data.get("tags", []),
            "reward_advertised": data.get("price", 0),
            "reward_currency": "OLAS",
            "reward_usd": 0,
            "buyer_id": data.get("creator", ""),
            "status": "active" if data.get("registered", True) else "inactive",
            "extra": {
                "chain": data.get("chain", "ethereum"),
                "agent_address": data.get("agent_address", ""),
                "service_id": data.get("service_id", ""),
                "operator_count": data.get("operator_count", 0),
                "staked_olas": data.get("staked_olas", 0),
            },
        }

    def _normalize_emissions(self, data: dict) -> dict:
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (int, float, str)):
                    store_platform_stat("olas", f"emission:{key}", str(value))
        return {"type": "emissions", "source": "olas", "data": data}

    def _normalize_stats(self, data: dict) -> dict:
        for key, value in data.items():
            if isinstance(value, (int, float, str)):
                store_platform_stat("olas", key, str(value))
        return {"type": "platform_stats", "source": "olas", "data": data}

    def health_check(self) -> bool:
        r = self.client.get("/api/services", params={"limit": 1})
        return r is not None
