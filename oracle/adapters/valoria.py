"""Valoria adapter — market intelligence, derived scores."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_platform_stat


class ValoriaAdapter:
    id = "valoria"
    name = "Valoria"
    base_url = "https://valoria.net"

    def __init__(self):
        self.client = get_client("valoria", base_url=self.base_url, requests_per_minute=10)

    async def discover(self) -> list[dict]:
        items = []
        # Stats
        stats = self.client.get("/api/stats")
        if stats:
            items.append({"type": "stats", "data": stats})
            for k, v in stats.items():
                if isinstance(v, (int, float, str)):
                    store_platform_stat("valoria", k, str(v))

        # Search for services
        search = self.client.get("/search", params={"q": "all", "limit": 100})
        if search:
            services = search if isinstance(search, list) else search.get("services", search.get("results", []))
            for s in services:
                items.append({"type": "service", "data": s})

        return items

    def normalize(self, raw: dict) -> dict:
        data = raw.get("data", raw) if isinstance(raw, dict) else raw
        if raw.get("type") == "stats":
            return {"type": "stats", "source": "valoria"}
        price = data.get("price", data.get("min_price", 0))
        if isinstance(price, str):
            try: price = float(price.replace("$", ""))
            except: price = 0
        return {
            "id": f"valoria:{data.get('slug', data.get('id', data.get('domain', '')))}",
            "source": "valoria", "source_id": str(data.get("slug", data.get("id", data.get("domain", "")))),
            "title": data.get("name", data.get("domain", "")), "description": data.get("description", "")[:2000],
            "url": data.get("url", data.get("domain", "")), "type": "api", "category": data.get("category", ""),
            "skills": data.get("tags", []),
            "reward_advertised": float(price) if price else 0, "reward_currency": "USDC",
            "reward_usd": float(price) if price else 0, "buyer_id": "", "status": "active",
            "extra": {"demand_score": data.get("demand_score", 0), "competition_score": data.get("competition_score", 0),
                      "margin_score": data.get("margin_score", 0), "growth_score": data.get("growth_score", 0)},
        }

    def health_check(self) -> bool:
        r = self.client.get("/api/stats")
        return r is not None
