"""Service Feed — tools, APIs, capabilities that agents can buy/use.

Sources: Apify, x402engine, x402list, PayAPI, the402, 402index, TOLL402
"""
from __future__ import annotations

import json
import time
import urllib.request
from typing import Any


class ServiceFeed:
    """Collects and normalizes service/tool data."""

    def __init__(self):
        self.sources = {
            "apify": ApifyService(),
            "x402engine": X402EngineService(),
            "x402list": X402ListService(),
            "payapi": PayAPIService(),
            "the402": The402Service(),
            "402index": Index402Service(),
        }

    async def collect(self) -> list[dict]:
        all_services = []
        for source_id, adapter in self.sources.items():
            try:
                items = await adapter.fetch()
                for item in items:
                    item["source"] = source_id
                    all_services.append(item)
            except Exception as e:
                print(f"  [service] {source_id} error: {e}")
        return all_services


class BaseService:
    def _get(self, url: str) -> Any:
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "MoltworkOracle/0.1"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except Exception:
            return None


class ApifyService(BaseService):
    async def fetch(self) -> list[dict]:
        items = []
        queries = ["scraper", "browser", "data", "ai", "automation", "api", "monitor"]
        seen = set()
        for q in queries:
            data = self._get(f"https://api.apify.com/v2/store?q={q}&limit=20")
            if data:
                store = data.get("data", {})
                actors = store.get("items", []) if isinstance(store, dict) else []
                for a in actors:
                    name = a.get("name", "")
                    if name and name not in seen:
                        seen.add(name)
                        items.append(self._normalize(a))
        return items

    def _normalize(self, a: dict) -> dict:
        stats = a.get("stats", {})
        return {
            "id": f"apify:{a.get('name', '')}",
            "source": "apify",
            "source_id": a.get("name", ""),
            "url": f"https://apify.com/{a.get('username', 'apify')}/{a.get('name', '')}",
            "name": a.get("title", a.get("name", "")),
            "description": (a.get("description") or "")[:500],
            "category": a.get("categories", [""])[0] if a.get("categories") else "",
            "input_schema": None,
            "output_schema": None,
            "price_per_call": 0,
            "currency": "USD",
            "pricing_model": "free_tier",
            "rating": stats.get("actorReviewRating", 0),
            "reviews": stats.get("actorReviewCount", 0),
            "verified": True,
            "total_runs": stats.get("totalRuns", 0),
            "total_users": stats.get("totalUsers", 0),
            "users_30d": stats.get("totalUsers30Days", 0),
            "users_7d": stats.get("totalUsers7Days", 0),
            "last_used_at": stats.get("lastRunStartedAt", ""),
            "provider_id": a.get("username", ""),
            "provider_reputation": 0,
            "provider_network": "cloud",
            "raw": a,
        }


class X402EngineService(BaseService):
    async def fetch(self) -> list[dict]:
        data = self._get("https://x402engine.app/api/services?limit=100")
        if not data:
            return []
        services = data if isinstance(data, list) else data.get("services", [])
        return [self._normalize(s) for s in services]

    def _normalize(self, s: dict) -> dict:
        price = s.get("price", 0)
        if isinstance(price, str):
            try: price = float(price.replace("$", ""))
            except: price = 0
        return {
            "id": f"x402engine:{s.get('id', s.get('slug', ''))}",
            "source": "x402engine",
            "source_id": str(s.get("id", s.get("slug", ""))),
            "url": s.get("url", ""),
            "name": s.get("name", ""),
            "description": (s.get("description") or "")[:500],
            "category": s.get("category", ""),
            "input_schema": None,
            "output_schema": None,
            "price_per_call": float(price) if price else 0,
            "currency": "USDC",
            "pricing_model": "per_call",
            "rating": 0,
            "reviews": 0,
            "verified": True,
            "total_runs": 0,
            "total_users": 0,
            "users_30d": 0,
            "users_7d": 0,
            "last_used_at": "",
            "provider_id": "",
            "provider_reputation": 0,
            "provider_network": "base",
            "raw": s,
        }


class X402ListService(BaseService):
    async def fetch(self) -> list[dict]:
        data = self._get("https://x402-list.com/api/v1/services?per_page=100")
        if not data:
            return []
        services = data.get("data", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        return [self._normalize(s) for s in services]

    def _normalize(self, s: dict) -> dict:
        price = s.get("min_price_usd", 0)
        if isinstance(price, str):
            try: price = float(price.replace("$", ""))
            except: price = 0
        return {
            "id": f"x402list:{s.get('slug', s.get('id', ''))}",
            "source": "x402list",
            "source_id": str(s.get("slug", s.get("id", ""))),
            "url": s.get("url", ""),
            "name": s.get("name", ""),
            "description": (s.get("description") or "")[:500],
            "category": s.get("category", ""),
            "input_schema": None,
            "output_schema": None,
            "price_per_call": float(price) if price else 0,
            "currency": "USDC",
            "pricing_model": "per_call",
            "rating": 0,
            "reviews": 0,
            "verified": s.get("verified", False),
            "total_runs": 0,
            "total_users": 0,
            "users_30d": 0,
            "users_7d": 0,
            "last_used_at": "",
            "provider_id": "",
            "provider_reputation": 0,
            "provider_network": s.get("networks", [""])[0] if s.get("networks") else "",
            "raw": s,
        }


class PayAPIService(BaseService):
    async def fetch(self) -> list[dict]:
        data = self._get("https://payapi.market/agent/list?limit=100")
        if not data:
            return []
        services = data.get("results", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        return [self._normalize(s) for s in services]

    def _normalize(self, s: dict) -> dict:
        price = s.get("price_min", 0)
        if isinstance(price, str):
            try: price = float(price.replace("$", ""))
            except: price = 0
        return {
            "id": f"payapi:{s.get('id', s.get('slug', ''))}",
            "source": "payapi",
            "source_id": str(s.get("id", s.get("slug", ""))),
            "url": s.get("marketplace_url", s.get("url", "")),
            "name": s.get("name", ""),
            "description": (s.get("description") or "")[:500],
            "category": s.get("category", ""),
            "input_schema": None,
            "output_schema": None,
            "price_per_call": float(price) if price else 0,
            "currency": "USDC",
            "pricing_model": "per_call",
            "rating": 0,
            "reviews": 0,
            "verified": s.get("payment_verified", False),
            "total_runs": 0,
            "total_users": 0,
            "users_30d": 0,
            "users_7d": 0,
            "last_used_at": "",
            "provider_id": "",
            "provider_reputation": 0,
            "provider_network": s.get("network", ""),
            "raw": s,
        }


class The402Service(BaseService):
    async def fetch(self) -> list[dict]:
        data = self._get("https://api.the402.ai/v1/services/catalog?limit=100")
        if not data:
            return []
        services = data.get("services", [])
        return [self._normalize(s) for s in services]

    def _normalize(self, s: dict) -> dict:
        price = s.get("price", {})
        if isinstance(price, dict):
            price_str = price.get("fixed", "0")
            try: price = float(price_str.replace("$", "").replace(",", ""))
            except: price = 0
        else:
            price = 0
        return {
            "id": f"the402:{s.get('id', '')}",
            "source": "the402",
            "source_id": str(s.get("id", "")),
            "url": s.get("endpoint", ""),
            "name": s.get("name", ""),
            "description": (s.get("description") or "")[:500],
            "category": s.get("category", ""),
            "input_schema": s.get("input_schema"),
            "output_schema": None,
            "price_per_call": float(price) if price else 0,
            "currency": "USD",
            "pricing_model": s.get("pricing_model", "fixed"),
            "rating": 0,
            "reviews": s.get("provider_completed_jobs", 0),
            "verified": s.get("provider_verification_tier") == "verified",
            "total_runs": 0,
            "total_users": 0,
            "users_30d": 0,
            "users_7d": 0,
            "last_used_at": "",
            "provider_id": s.get("provider_id", ""),
            "provider_reputation": s.get("provider_reputation", 0),
            "provider_network": "base",
            "raw": s,
        }


class Index402Service(BaseService):
    async def fetch(self) -> list[dict]:
        data = self._get("https://402index.io/api/v1/services?limit=100")
        if not data:
            return []
        services = data.get("services", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        return [self._normalize(s) for s in services]

    def _normalize(self, s: dict) -> dict:
        price = s.get("price_usd", 0)
        if isinstance(price, str):
            try: price = float(price.replace("$", ""))
            except: price = 0
        return {
            "id": f"402index:{s.get('id', s.get('name', ''))}",
            "source": "402index",
            "source_id": str(s.get("id", "")),
            "url": s.get("url", ""),
            "name": s.get("name", ""),
            "description": (s.get("description") or "")[:500],
            "category": s.get("category", ""),
            "input_schema": None,
            "output_schema": None,
            "price_per_call": float(price) if price else 0,
            "currency": "USDC",
            "pricing_model": "per_call",
            "rating": 0,
            "reviews": 0,
            "verified": True,
            "total_runs": 0,
            "total_users": 0,
            "users_30d": 0,
            "users_7d": 0,
            "last_used_at": "",
            "provider_id": "",
            "provider_reputation": 0,
            "provider_network": s.get("payment_network", ""),
            "raw": s,
        }
