"""TOLL402 adapter — bulk discovery source.

API: https://toll402.com/api/resources?pageSize=N
Status: ✅ Working
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_service_listing, store_platform_stat


class Toll402Adapter:
    id = "toll402"
    name = "TOLL·402"
    base_url = "https://toll402.com"

    def __init__(self):
        self.client = get_client("toll402", base_url=self.base_url, requests_per_minute=10)

    async def discover(self) -> list[dict]:
        items = []
        data = self.client.get("/api/resources", params={"pageSize": 100})
        if data:
            providers = data.get("items", []) if isinstance(data, dict) else data
            for p in providers:
                items.append({"type": "provider", "data": p})
                desc = p.get("description") or ""
                store_service_listing({
                    "id": f"toll402:{p.get('id', p.get('hostname', ''))}",
                    "source": "toll402",
                    "source_service_id": str(p.get("id", p.get("hostname", ""))),
                    "title": p.get("name", p.get("hostname", "")),
                    "description": desc[:2000],
                    "url": p.get("resourceUrl", p.get("hostname", "")),
                    "category": p.get("tags", [""])[0] if p.get("tags") else "",
                    "price_usdc": 0,
                    "price_per_call": 0,
                    "provider_id": p.get("providerName", ""),
                    "provider_reputation": 0,
                    "total_calls": p.get("resourceCount", 0),
                    "status": "active",
                    "capabilities": p.get("tags", []),
                    "extra": {
                        "hostname": p.get("hostname", ""),
                        "resource_count": p.get("resourceCount", 0),
                        "curated": p.get("isCurated", False),
                        "networks": p.get("networks", []),
                    },
                })
        return items

    def normalize(self, raw: dict) -> dict:
        data = raw.get("data", raw) if isinstance(raw, dict) else raw
        desc = data.get("description") or ""
        return {
            "id": f"toll402:{data.get('id', data.get('hostname', ''))}",
            "source": "toll402",
            "source_id": str(data.get("id", data.get("hostname", ""))),
            "title": data.get("name", data.get("hostname", "")),
            "description": desc[:2000],
            "url": data.get("resourceUrl", data.get("hostname", "")),
            "type": "provider",
            "category": data.get("tags", [""])[0] if data.get("tags") else "",
            "skills": data.get("tags", []),
            "reward_advertised": 0,
            "reward_currency": "USDC",
            "reward_usd": 0,
            "buyer_id": data.get("providerName", ""),
            "status": "active",
            "extra": {
                "resource_count": data.get("resourceCount", 0),
                "curated": data.get("isCurated", False),
                "networks": data.get("networks", []),
            },
        }

    def health_check(self) -> bool:
        r = self.client.get("/api/resources", params={"pageSize": 1})
        return r is not None
