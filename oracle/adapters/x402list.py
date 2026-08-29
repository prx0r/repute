"""x402 List adapter — free API, 2K req/day, service telemetry."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_service_listing, store_platform_stat


class X402ListAdapter:
    id = "x402list"
    name = "x402 List"
    base_url = "https://x402-list.com"

    def __init__(self):
        self.client = get_client("x402list", base_url=self.base_url, requests_per_minute=10)

    async def discover(self) -> list[dict]:
        items = []
        data = self.client.get("/api/v1/services", params={"per_page": 100})
        if data:
            services = data.get("data", []) if isinstance(data, dict) else data
            for s in services:
                items.append({"type": "service", "data": s})
                store_service_listing({
                    "id": f"x402list:{s.get('slug', s.get('id', ''))}",
                    "source": "x402list", "source_service_id": str(s.get("slug", s.get("id", ""))),
                    "title": s.get("name", ""), "description": s.get("description", "")[:2000],
                    "url": s.get("url", ""), "category": s.get("category", ""),
                    "price_usdc": s.get("min_price_usd", 0), "price_per_call": s.get("min_price_usd", 0),
                    "provider_id": "", "provider_reputation": 0,
                    "total_calls": s.get("total_checks", 0), "status": s.get("status", "unknown"),
                    "capabilities": s.get("tags", []),
                    "extra": {"uptime_24h": s.get("uptime", {}).get("24h", 0), "networks": s.get("networks", [])},
                })
        stats = self.client.get("/api/v1/stats")
        if stats:
            items.append({"type": "stats", "data": stats})
        return items

    def normalize(self, raw: dict) -> dict:
        data = raw.get("data", raw) if isinstance(raw, dict) else raw
        if raw.get("type") == "stats":
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, (int, float, str)):
                        store_platform_stat("x402list", k, str(v))
            return {"type": "stats", "source": "x402list"}
        price = data.get("min_price_usd", 0)
        if isinstance(price, str):
            try: price = float(price.replace("$", ""))
            except: price = 0
        return {
            "id": f"x402list:{data.get('slug', data.get('id', ''))}",
            "source": "x402list", "source_id": str(data.get("slug", data.get("id", ""))),
            "title": data.get("name", ""), "description": data.get("description", "")[:2000],
            "url": data.get("url", ""), "type": "api", "category": data.get("category", ""),
            "skills": data.get("tags", []),
            "reward_advertised": float(price) if price else 0, "reward_currency": "USDC",
            "reward_usd": float(price) if price else 0, "buyer_id": "", "status": data.get("status", "open"),
            "extra": {"uptime": data.get("uptime", {}), "networks": data.get("networks", []),
                      "verified": data.get("verified", False)},
        }

    def health_check(self) -> bool:
        r = self.client.get("/api/v1/services", params={"per_page": 1})
        return r is not None
