"""Agent402 adapter — uses free discovery endpoints.

Free endpoints (no payment needed):
  /api/find?q={task}    — resolve task to tool (free)
  /api/pricing           — full pricing catalog (free)
  /api/stats             — platform stats (free)
  /openapi.json          — OpenAPI spec (free)

Paid endpoints (x402 or proof-of-work):
  500+ tools, 222 free via PoW
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_service_listing, store_platform_stat


class Agent402Adapter:
    id = "agent402"
    name = "Agent402"
    base_url = "https://agent402.tools"

    def __init__(self):
        self.client = get_client("agent402", base_url=self.base_url)

    async def discover(self) -> list[dict]:
        items = []

        # 1. Pricing catalog (free) — has all 500+ tools with prices
        pricing = self.client.get("/api/pricing")
        if pricing:
            # Response can be a dict with nested tools or a list
            if isinstance(pricing, dict):
                # Extract tools from various possible keys
                tools = pricing.get("tools", pricing.get("catalog", []))
                if not tools and isinstance(pricing.get("humanProducts"), list):
                    tools = pricing["humanProducts"]
                # If still no tools, treat the dict itself as a single entry
                if not tools:
                    tools = [pricing]
            else:
                tools = pricing if isinstance(pricing, list) else []

            for t in tools:
                items.append({"type": "tool", "data": t})
                store_service_listing({
                    "id": f"agent402:{t.get('slug', t.get('id', ''))}",
                    "source": "agent402",
                    "source_service_id": str(t.get("slug", t.get("id", ""))),
                    "title": t.get("name", t.get("slug", "")),
                    "description": t.get("description", "")[:2000],
                    "url": f"https://agent402.tools/tools/{t.get('slug', '')}",
                    "category": t.get("category", ""),
                    "price_usdc": t.get("price", 0),
                    "price_per_call": t.get("price", 0),
                    "provider_id": "",
                    "provider_reputation": 0,
                    "total_calls": 0,
                    "status": "active",
                    "capabilities": t.get("tags", []),
                    "extra": {"free_via_pow": t.get("free_via_pow", False)},
                })

        # 2. Stats (free)
        stats = self.client.get("/api/stats")
        if stats:
            items.append({"type": "platform_stats", "data": stats})

        return items

    def normalize(self, raw: dict) -> dict:
        item_type = raw.get("type", "tool")
        data = raw.get("data", raw)

        if item_type == "platform_stats":
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (int, float, str)):
                        store_platform_stat("agent402", key, str(value))
            return {"type": "platform_stats", "source": "agent402"}

        price = data.get("price", 0)
        if isinstance(price, str):
            try:
                price = float(price.replace("$", ""))
            except ValueError:
                price = 0

        return {
            "id": f"agent402:{data.get('slug', data.get('id', ''))}",
            "source": "agent402",
            "source_id": str(data.get("slug", data.get("id", ""))),
            "title": data.get("name", data.get("slug", "")),
            "description": data.get("description", "")[:2000],
            "url": f"https://agent402.tools/tools/{data.get('slug', '')}",
            "type": "tool",
            "category": data.get("category", "general"),
            "skills": data.get("tags", []),
            "reward_advertised": float(price) if price else 0,
            "reward_currency": "USDC",
            "reward_usd": float(price) if price else 0,
            "buyer_id": "",
            "status": "open",
            "extra": {
                "free_via_pow": data.get("free_via_pow", False),
                "category": data.get("category", ""),
            },
        }

    def health_check(self) -> bool:
        r = self.client.get("/api/pricing")
        return r is not None
