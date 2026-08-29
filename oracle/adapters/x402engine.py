"""x402engine adapter — uses free discovery endpoints + MCP.

Free endpoints (no payment needed):
  /.well-known/x402.json   — full service discovery
  /api/services             — list all services
  /api/services/:id         — service details
  /api/discover             — discovery endpoint
  /health                   — platform health

Paid endpoints (x402):
  /api/crypto/price, /api/llm, /api/image, etc.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_service_listing, store_platform_stat


class X402EngineAdapter:
    id = "x402engine"
    name = "x402engine"
    base_url = "https://x402engine.app"

    def __init__(self):
        self.client = get_client("x402engine", base_url=self.base_url)

    async def discover(self) -> list[dict]:
        items = []

        # 1. Service catalog (free)
        services = self.client.get("/api/services", params={"limit": 200})
        if services:
            s_list = services if isinstance(services, list) else services.get("services", [])
            for s in s_list:
                items.append({"type": "service", "data": s})
                store_service_listing({
                    "id": f"x402engine:{s.get('id', s.get('slug', ''))}",
                    "source": "x402engine",
                    "source_service_id": str(s.get("id", s.get("slug", ""))),
                    "title": s.get("name", ""),
                    "description": s.get("description", "")[:2000],
                    "url": s.get("url", f"https://x402engine.app{ s.get('endpoint', '')}"),
                    "category": s.get("category", ""),
                    "price_usdc": s.get("price", 0),
                    "price_per_call": s.get("price", 0),
                    "provider_id": "",
                    "provider_reputation": 0,
                    "total_calls": s.get("total_calls", 0),
                    "status": "active",
                    "capabilities": s.get("tags", []),
                    "extra": {"networks": s.get("networks", [])},
                })

        # 2. Discovery document (free)
        discovery = self.client.get("/.well-known/x402.json")
        if discovery:
            items.append({"type": "discovery", "data": discovery})

        return items

    def normalize(self, raw: dict) -> dict:
        item_type = raw.get("type", "service")
        data = raw.get("data", raw)

        if item_type == "discovery":
            # Store discovery metadata as platform stats
            if isinstance(data, dict):
                for key in ["total_services", "total_endpoints", "networks"]:
                    if key in data:
                        store_platform_stat("x402engine", key, str(data[key]))
            return {"type": "discovery", "source": "x402engine"}

        price = data.get("price", 0)
        if isinstance(price, str):
            try:
                price = float(price.replace("$", ""))
            except ValueError:
                price = 0

        return {
            "id": f"x402engine:{data.get('id', data.get('slug', ''))}",
            "source": "x402engine",
            "source_id": str(data.get("id", data.get("slug", ""))),
            "title": data.get("name", ""),
            "description": data.get("description", "")[:2000],
            "url": data.get("url", f"https://x402engine.app{data.get('endpoint', '')}"),
            "type": "api",
            "category": data.get("category", "general"),
            "skills": data.get("tags", []),
            "reward_advertised": float(price) if price else 0,
            "reward_currency": "USDC",
            "reward_usd": float(price) if price else 0,
            "buyer_id": "",
            "status": "open",
            "extra": {
                "category": data.get("category", ""),
                "networks": data.get("networks", []),
                "total_calls": data.get("total_calls", 0),
            },
        }

    def health_check(self) -> bool:
        r = self.client.get("/api/services", params={"limit": 1})
        return r is not None
