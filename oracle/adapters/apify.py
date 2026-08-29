"""Apify adapter — 51K+ tools with real usage data.

Economic intelligence: what agents are actually using and paying for.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_service_listing, store_platform_stat


class ApifyAdapter:
    id = "apify"
    name = "Apify"
    base_url = "https://api.apify.com/v2"

    def __init__(self):
        self.client = get_client("apify", base_url=self.base_url, requests_per_minute=10)

    async def discover(self) -> list[dict]:
        items = []

        # Search for popular actors across categories
        queries = ["scraper", "browser", "data", "ai", "automation", "api", "monitor"]
        seen = set()

        for q in queries:
            data = self.client.get("/store", params={"q": q, "limit": 20, "sort": "popularity"})
            if data:
                store = data.get("data", {}) if isinstance(data, dict) else data
                actors = store.get("items", []) if isinstance(store, dict) else []
                for actor in actors:
                    name = actor.get("name", "")
                    if name and name not in seen:
                        seen.add(name)
                        items.append({"type": "actor", "data": actor})

                        # Store as service listing
                        stats = actor.get("stats", {})
                        store_service_listing({
                            "id": f"apify:{name}",
                            "source": "apify",
                            "source_service_id": name,
                            "title": actor.get("title", name),
                            "description": actor.get("description", "")[:2000],
                            "url": f"https://apify.com/{actor.get('username', 'apify')}/{name}",
                            "category": actor.get("categories", [""])[0] if actor.get("categories") else "",
                            "price_usdc": 0,
                            "price_per_call": 0,
                            "provider_id": actor.get("username", ""),
                            "provider_reputation": stats.get("actorReviewRating", 0),
                            "total_calls": stats.get("totalRuns", 0),
                            "status": "active",
                            "capabilities": actor.get("categories", []),
                            "extra": {
                                "total_users": stats.get("totalUsers", 0),
                                "total_users_30d": stats.get("totalUsers30Days", 0),
                                "total_users_7d": stats.get("totalUsers7Days", 0),
                                "reviews": stats.get("actorReviewCount", 0),
                                "rating": stats.get("actorReviewRating", 0),
                                "bookmarks": stats.get("bookmarkCount", 0),
                                "last_run": stats.get("lastRunStartedAt", ""),
                            },
                        })

        return items

    def normalize(self, raw: dict) -> dict:
        data = raw.get("data", raw) if isinstance(raw, dict) else raw
        stats = data.get("stats", {})

        return {
            "id": f"apify:{data.get('name', '')}",
            "source": "apify",
            "source_id": data.get("name", ""),
            "title": data.get("title", data.get("name", "")),
            "description": data.get("description", "")[:500],
            "url": f"https://apify.com/{data.get('username', 'apify')}/{data.get('name', '')}",
            "type": "tool",
            "category": data.get("categories", [""])[0] if data.get("categories") else "",
            "skills": data.get("categories", []),
            "reward_advertised": 0,
            "reward_currency": "USD",
            "reward_usd": 0,
            "buyer_id": data.get("username", ""),
            "status": "active",
            "extra": {
                "total_runs": stats.get("totalRuns", 0),
                "total_users": stats.get("totalUsers", 0),
                "total_users_30d": stats.get("totalUsers30Days", 0),
                "reviews": stats.get("actorReviewCount", 0),
                "rating": stats.get("actorReviewRating", 0),
                "bookmarks": stats.get("bookmarkCount", 0),
            },
        }

    def health_check(self) -> bool:
        r = self.client.get("/store", params={"q": "test", "limit": 1})
        return r is not None
