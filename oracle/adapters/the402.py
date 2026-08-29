"""the402 adapter — comprehensive data extraction.

Endpoints called:
  GET /v1/services/catalog     — full service catalog (free discovery)
  GET /v1/services/:id         — individual service details
  GET /v1/subscriptions/plans  — subscription plans
  GET /v1/products             — digital products
  GET /v1/reputation/:wallet   — 3-level, 4-dimension reputation
  GET /v1/threads              — negotiation threads
  GET /v1/balance/history      — transaction history

Data extracted:
  - Service catalog with reputation levels
  - Provider reputation (quality, speed, reliability, communication)
  - Subscription plans and pricing
  - Digital product catalog
  - Thread/negotiation activity
  - Transaction volume signals
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_service_listing, store_agent_profile, store_platform_stat


class The402Adapter:
    id = "the402"
    name = "the402"
    base_url = "https://api.the402.ai"

    def __init__(self):
        self.client = get_client("the402", base_url=self.base_url)

    async def discover(self) -> list[dict]:
        """Fetch service catalog from the402."""
        items = []

        # Service catalog (the main data)
        catalog = self.client.get("/v1/services/catalog", params={"limit": 200, "sort": "reputation"})
        if catalog:
            services = catalog if isinstance(catalog, list) else catalog.get("services", [])
            for svc in services:
                items.append({"type": "service", "data": svc})

        return items

    def normalize(self, raw: dict) -> dict:
        """Normalize any the402 data item."""
        item_type = raw.get("type", "service")
        data = raw.get("data", raw)

        if item_type == "service":
            return self._normalize_service(data)
        elif item_type == "service_detail":
            return self._normalize_service_detail(data)
        elif item_type == "reputation":
            return self._normalize_reputation(data)
        elif item_type == "subscription":
            return self._normalize_subscription(data)
        elif item_type == "product":
            return self._normalize_product(data)
        elif item_type == "thread":
            return self._normalize_thread(data)
        elif item_type == "platform_stats":
            return self._normalize_stats(data)
        return self._normalize_service(data)

    def _normalize_service(self, data: dict) -> dict:
        # Price can be a dict with min/max or a string like "$12.00"
        price = data.get("price", data.get("price_usdc", 0))
        if isinstance(price, dict):
            # Extract max price as the advertised price
            max_price = price.get("max", price.get("min", "0"))
            if isinstance(max_price, str):
                price = float(max_price.replace("$", "").replace(",", ""))
            else:
                price = float(max_price) if max_price else 0
        elif isinstance(price, str):
            price = float(price.replace("$", "").replace(",", "")) if price else 0

        return {
            "id": f"the402:{data.get('id', '')}",
            "source": "the402",
            "source_id": str(data.get("id", "")),
            "title": data.get("name", data.get("title", "")),
            "description": data.get("description", "")[:2000],
            "url": data.get("url", f"https://the402.ai/service/{data.get('id', '')}"),
            "type": "service",
            "category": data.get("category", data.get("service_type", "general")),
            "skills": data.get("tags", []),
            "reward_advertised": float(price) if price else 0,
            "reward_currency": "USDC",
            "reward_usd": float(price) if price else 0,
            "buyer_id": data.get("provider_id", data.get("provider_wallet", "")),
            "buyer_name": data.get("provider_name", ""),
            "status": "open",
            "extra": {
                "service_type": data.get("service_type", ""),
                "fulfillment_type": data.get("fulfillment_type", ""),
                "pricing_model": data.get("pricing_model", ""),
                "verification_tier": data.get("provider_verification_tier", ""),
            },
        }

    def _normalize_service_detail(self, data: dict) -> dict:
        """Store as service listing with full detail."""
        service = {
            "id": f"the402:{data.get('id', '')}",
            "source": "the402",
            "source_service_id": str(data.get("id", "")),
            "title": data.get("name", ""),
            "description": data.get("description", "")[:2000],
            "url": data.get("url", ""),
            "category": data.get("category", ""),
            "price_usdc": data.get("price_usdc", 0),
            "price_per_call": data.get("price_per_call", 0),
            "provider_id": data.get("provider_wallet", ""),
            "provider_reputation": data.get("reputation_score", 0),
            "total_calls": data.get("total_calls", 0),
            "status": "active" if data.get("active", True) else "inactive",
            "capabilities": data.get("tags", []),
            "extra": {
                "deliverable_schema": data.get("deliverable_schema", {}),
                "input_schema": data.get("input_schema", {}),
                "output_schema": data.get("output_schema", {}),
                "service_type": data.get("service_type", ""),
            },
        }
        store_service_listing(service)
        return service

    def _normalize_reputation(self, data: dict) -> dict:
        """Store as agent profile with reputation detail."""
        profile = {
            "id": f"the402:rep:{data.get('wallet', '')}",
            "source": "the402",
            "source_agent_id": data.get("wallet", ""),
            "name": data.get("name", data.get("wallet", "")[:10]),
            "description": "",
            "url": f"https://the402.ai/reputation/{data.get('wallet', '')}",
            "tier": data.get("reputation_level", ""),
            "reputation_score": data.get("score", 0),
            "jobs_completed": data.get("total_jobs", 0),
            "total_earned_usd": data.get("total_earned", 0),
            "success_rate": data.get("success_rate", 0),
            "capabilities": [],
            "wallet_address": data.get("wallet", ""),
            "chain": "base",
            "extra": {
                "quality": data.get("quality", 0),
                "speed": data.get("speed", 0),
                "reliability": data.get("reliability", 0),
                "communication": data.get("communication", 0),
                "reputation_level": data.get("reputation_level", ""),
            },
        }
        store_agent_profile(profile)
        return profile

    def _normalize_subscription(self, data: dict) -> dict:
        return {
            "id": f"the402:sub:{data.get('id', '')}",
            "source": "the402",
            "source_id": str(data.get("id", "")),
            "title": data.get("name", ""),
            "description": data.get("description", ""),
            "url": "",
            "type": "subscription",
            "category": data.get("category", ""),
            "skills": [],
            "reward_advertised": data.get("price_usdc", 0),
            "reward_currency": "USDC",
            "reward_usd": data.get("price_usdc", 0),
            "buyer_id": "",
            "status": "active",
            "extra": {"interval": data.get("interval", ""), "features": data.get("features", [])},
        }

    def _normalize_product(self, data: dict) -> dict:
        return {
            "id": f"the402:prod:{data.get('id', '')}",
            "source": "the402",
            "source_id": str(data.get("id", "")),
            "title": data.get("name", ""),
            "description": data.get("description", "")[:2000],
            "url": f"https://the402.ai/product/{data.get('id', '')}",
            "type": "product",
            "category": data.get("category", ""),
            "skills": data.get("tags", []),
            "reward_advertised": data.get("price_usdc", 0),
            "reward_currency": "USDC",
            "reward_usd": data.get("price_usdc", 0),
            "buyer_id": data.get("provider_wallet", ""),
            "status": "active",
            "extra": {"file_type": data.get("file_type", ""), "size_bytes": data.get("size_bytes", 0)},
        }

    def _normalize_thread(self, data: dict) -> dict:
        return {
            "id": f"the402:thread:{data.get('id', '')}",
            "source": "the402",
            "source_id": str(data.get("id", "")),
            "title": data.get("subject", f"Thread {data.get('id', '')}"),
            "description": data.get("last_message", "")[:2000],
            "url": "",
            "type": "thread",
            "category": "",
            "skills": [],
            "reward_advertised": data.get("proposed_price", 0),
            "reward_currency": "USDC",
            "reward_usd": data.get("proposed_price", 0),
            "buyer_id": data.get("buyer_wallet", ""),
            "status": data.get("status", "open"),
            "extra": {
                "message_count": data.get("message_count", 0),
                "provider_wallet": data.get("provider_wallet", ""),
            },
        }

    def _normalize_stats(self, data: dict) -> dict:
        """Store platform stats."""
        for key, value in data.items():
            if isinstance(value, (int, float, str)):
                store_platform_stat("the402", key, str(value))
        return {"type": "platform_stats", "source": "the402", "data": data}

    def health_check(self) -> bool:
        r = self.client.get("/v1/services/catalog", params={"limit": 1})
        return r is not None
