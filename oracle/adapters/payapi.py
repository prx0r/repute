"""PayAPI Market adapter — uses free agent discovery endpoints.

Free endpoints (no payment needed):
  /agent/search?q={query}  — search APIs (free)
  /agent/list               — list all APIs (free)
  /agent/get/{id}           — get API details (free)
  /openapi.json             — OpenAPI spec (free)
  /llms.txt                 — agent-readable index (free)
  /mcp/sse                  — MCP server (free discovery)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_service_listing, store_platform_stat


class PayAPIMarketAdapter:
    id = "payapi"
    name = "PayAPI Market"
    base_url = "https://payapi.market"

    def __init__(self):
        self.client = get_client("payapi", base_url=self.base_url)

    async def discover(self) -> list[dict]:
        items = []

        # 1. List all APIs (free)
        apis = self.client.get("/agent/list", params={"limit": 200})
        if apis:
            # Response format: {"category": null, "verified_only": true, "count": N, "apis": [...], "categories": [...]}
            api_list = apis if isinstance(apis, list) else apis.get("results", apis.get("apis", apis.get("services", [])))
            for api in api_list:
                items.append({"type": "api", "data": api})
                store_service_listing({
                    "id": f"payapi:{api.get('id', api.get('slug', ''))}",
                    "source": "payapi",
                    "source_service_id": str(api.get("id", api.get("slug", ""))),
                    "title": api.get("name", ""),
                    "description": api.get("description", "")[:2000],
                    "url": api.get("url", f"https://payapi.market/{api.get('slug', '')}"),
                    "category": api.get("category", ""),
                    "price_usdc": api.get("price_per_call", 0),
                    "price_per_call": api.get("price_per_call", 0),
                    "provider_id": "",
                    "provider_reputation": 0,
                    "total_calls": api.get("total_calls", 0),
                    "status": "active" if api.get("active", True) else "inactive",
                    "capabilities": api.get("tags", []),
                    "extra": {
                        "endpoints_count": api.get("endpoints_count", 0),
                        "verified": api.get("verified", False),
                    },
                })

        return items

    def normalize(self, raw: dict) -> dict:
        data = raw.get("data", raw) if isinstance(raw, dict) else raw

        price = data.get("price_per_call", data.get("price", 0))
        if isinstance(price, str):
            try:
                price = float(price.replace("$", ""))
            except ValueError:
                price = 0

        return {
            "id": f"payapi:{data.get('id', data.get('slug', ''))}",
            "source": "payapi",
            "source_id": str(data.get("id", data.get("slug", ""))),
            "title": data.get("name", ""),
            "description": data.get("description", "")[:2000],
            "url": data.get("url", f"https://payapi.market/{data.get('slug', '')}"),
            "type": "api",
            "category": data.get("category", "general"),
            "skills": data.get("tags", []),
            "reward_advertised": float(price) if price else 0,
            "reward_currency": "USDC",
            "reward_usd": float(price) if price else 0,
            "buyer_id": "",
            "status": "open",
            "extra": {
                "endpoints_count": data.get("endpoints_count", 0),
                "verified": data.get("verified", False),
            },
        }

    def health_check(self) -> bool:
        r = self.client.get("/agent/list", params={"limit": 1})
        return r is not None
