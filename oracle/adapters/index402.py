"""402 Index adapter — cross-rail catalog (x402, L402, MPP).

API: https://402index.io/api/v1/services
Status: ✅ Working
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_service_listing, store_platform_stat


class Index402Adapter:
    id = "402index"
    name = "402 Index"
    base_url = "https://402index.io/api/v1"

    def __init__(self):
        self.client = get_client("402index", base_url=self.base_url, requests_per_minute=10)

    async def discover(self) -> list[dict]:
        items = []
        data = self.client.get("/services", params={"limit": 100})
        if data:
            services = data.get("services", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
            for s in services:
                items.append({"type": "service", "data": s})
                price = s.get("price_usd", s.get("price", 0))
                if isinstance(price, str):
                    try: price = float(price.replace("$", ""))
                    except: price = 0

                store_service_listing({
                    "id": f"402index:{s.get('id', s.get('name', ''))}",
                    "source": "402index",
                    "source_service_id": str(s.get("id", "")),
                    "title": s.get("name", ""),
                    "description": (s.get("description") or "")[:2000],
                    "url": s.get("url", ""),
                    "category": s.get("category", ""),
                    "price_usdc": float(price) if price else 0,
                    "price_per_call": float(price) if price else 0,
                    "provider_id": "",
                    "provider_reputation": 0,
                    "total_calls": 0,
                    "status": "active",
                    "capabilities": [],
                    "extra": {
                        "protocol": s.get("protocol", "x402"),
                        "network": s.get("payment_network", ""),
                        "asset": s.get("payment_asset", ""),
                    },
                })
        return items

    def normalize(self, raw: dict) -> dict:
        data = raw.get("data", raw) if isinstance(raw, dict) else raw
        price = data.get("price_usd", data.get("price", 0))
        if isinstance(price, str):
            try: price = float(price.replace("$", ""))
            except: price = 0

        return {
            "id": f"402index:{data.get('id', data.get('name', ''))}",
            "source": "402index",
            "source_id": str(data.get("id", "")),
            "title": data.get("name", ""),
            "description": (data.get("description") or "")[:2000],
            "url": data.get("url", ""),
            "type": "api",
            "category": data.get("category", ""),
            "skills": [],
            "reward_advertised": float(price) if price else 0,
            "reward_currency": "USDC",
            "reward_usd": float(price) if price else 0,
            "buyer_id": "",
            "status": "active",
            "extra": {
                "protocol": data.get("protocol", "x402"),
                "network": data.get("payment_network", ""),
                "asset": data.get("payment_asset", ""),
            },
        }

    def health_check(self) -> bool:
        r = self.client.get("/services", params={"limit": 1})
        return r is not None
