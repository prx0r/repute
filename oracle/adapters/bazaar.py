"""Coinbase Bazaar adapter — canonical discovery + quality.

API: https://api.cdp.coinbase.com/platform/v2/x402/discovery/search
Price in accepts[0].amount (USDC atomics, /1_000_000 for USD)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_service_listing, store_platform_stat


class CoinbaseBazaarAdapter:
    id = "bazaar"
    name = "Coinbase Bazaar"
    base_url = "https://api.cdp.coinbase.com/platform/v2/x402/discovery"

    def __init__(self):
        self.client = get_client("bazaar", base_url=self.base_url, requests_per_minute=10)

    async def discover(self) -> list[dict]:
        items = []
        data = self.client.get("/search", params={"q": "all", "limit": 100})
        if data:
            resources = data.get("resources", []) if isinstance(data, dict) else data
            for r in resources:
                items.append({"type": "resource", "data": r})
                # Extract price from accepts array
                price_usd = 0
                accepts = r.get("accepts", [])
                if accepts and isinstance(accepts, list):
                    amount = accepts[0].get("amount", "0")
                    try:
                        price_usd = int(amount) / 1_000_000
                    except (ValueError, TypeError):
                        pass

                store_service_listing({
                    "id": f"bazaar:{r.get('resource', '')}",
                    "source": "bazaar", "source_service_id": r.get("resource", ""),
                    "title": r.get("description", "")[:100],
                    "description": r(r.get("description") or "")[:2000],
                    "url": r.get("resource", ""),
                    "category": r.get("type", ""),
                    "price_usdc": price_usd, "price_per_call": price_usd,
                    "provider_id": accepts[0].get("payTo", "") if accepts else "",
                    "provider_reputation": 0, "total_calls": 0,
                    "status": "active", "capabilities": [],
                    "extra": {
                        "protocol": r.get("type", ""),
                        "networks": [a.get("network", "") for a in accepts if isinstance(a, dict)],
                        "quality": r.get("quality", {}),
                        "x402_version": r.get("x402Version", ""),
                    },
                })
        return items

    def normalize(self, raw: dict) -> dict:
        data = raw.get("data", raw) if isinstance(raw, dict) else raw
        price_usd = 0
        accepts = data.get("accepts", [])
        if accepts and isinstance(accepts, list):
            amount = accepts[0].get("amount", "0")
            try:
                price_usd = int(amount) / 1_000_000
            except (ValueError, TypeError):
                pass

        return {
            "id": f"bazaar:{data.get('resource', '')}",
            "source": "bazaar", "source_id": data.get("resource", ""),
            "title": data.get("description", "")[:100],
            "description": data(r.get("description") or "")[:2000],
            "url": data.get("resource", ""),
            "type": "api", "category": data.get("type", ""),
            "skills": [],
            "reward_advertised": price_usd, "reward_currency": "USDC",
            "reward_usd": price_usd,
            "buyer_id": accepts[0].get("payTo", "") if accepts else "",
            "status": "active",
            "extra": {"networks": [a.get("network", "") for a in accepts if isinstance(a, dict)]},
        }

    def health_check(self) -> bool:
        r = self.client.get("/search", params={"q": "test", "limit": 1})
        return r is not None
