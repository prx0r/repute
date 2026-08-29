"""Marketplace adapters — publish products to external marketplaces.

This is the distribution layer: take a canonical Moltwork product and
adapt/package it for each target marketplace.

Three adapter types:
  1. Discovery — read marketplace data (what sells, what's trending)
  2. Publish — upload products to marketplaces
  3. Sync — track sales, reviews, status

Not all adapters support all three operations.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client


class MarketAdapter:
    """Base protocol for marketplace adapters.

    Implement at minimum: discover_listings()
    Optionally: publish(), sync_sales(), sync_status()
    """

    id: str = ""
    name: str = ""
    base_url: str = ""
    revenue_share: float = 0.0  # e.g. 0.88 = 88% to seller
    has_api: bool = False
    has_publish_api: bool = False

    def __init__(self):
        self.client = get_client(self.id, base_url=self.base_url) if self.base_url else None

    async def discover_listings(self, category: str = "", limit: int = 100) -> list[dict]:
        """Discover existing listings on this marketplace.
        Returns list of normalized listing dicts.
        """
        return []

    async def publish(self, product: dict) -> dict:
        """Publish a product to this marketplace.
        Returns: {"ok": bool, "listing_id": str, "url": str, "error": str}
        """
        return {"ok": False, "error": "Not implemented"}

    async def sync_sales(self, listing_id: str) -> dict:
        """Sync sales data for a listing.
        Returns: {"sales": int, "revenue": float, "last_sale": str}
        """
        return {"sales": 0, "revenue": 0}

    def health_check(self) -> bool:
        return self.has_api


class RobloxAdapter(MarketAdapter):
    """Roblox Creator Store — full REST API."""

    id = "roblox"
    name = "Roblox Creator Store"
    base_url = "https://apis.roblox.com"
    revenue_share = 1.0  # 100% net
    has_api = True
    has_publish_api = True

    def __init__(self, api_key: str = ""):
        super().__init__()
        self.api_key = api_key
        if api_key:
            self.client = get_client("roblox", base_url=self.base_url)

    async def discover_listings(self, category: str = "", limit: int = 100) -> list[dict]:
        """Search Creator Store."""
        if not self.client:
            return []
        data = self.client.get("/toolbox-service/v2/assets:search", params={
            "query": category or "game asset",
            "limit": min(limit, 100),
        })
        if not data:
            return []
        items = data if isinstance(data, list) else data.get("assets", data.get("results", []))
        return [self._normalize_listing(item) for item in items]

    def _normalize_listing(self, item: dict) -> dict:
        return {
            "id": f"roblox:{item.get('id', '')}",
            "marketplace": "roblox",
            "marketplace_id": str(item.get("id", "")),
            "title": item.get("name", item.get("displayName", "")),
            "description": item.get("description", "")[:2000],
            "url": f"https://www.roblox.com/catalog/{item.get('id', '')}",
            "price": item.get("price", 0),
            "currency": "Robux",
            "category": item.get("assetType", item.get("category", "")),
            "sales": item.get("purchasingCount", 0),
            "favorites": item.get("favoritedCount", 0),
            "rating": item.get("averageRating", 0),
            "extra": {
                "asset_type": item.get("assetType", ""),
                "creator": item.get("creator", {}),
                "created_at": item.get("created", ""),
                "updated_at": item.get("updated", ""),
            },
        }

    async def publish(self, product: dict) -> dict:
        """Upload asset to Roblox via API."""
        if not self.api_key:
            return {"ok": False, "error": "No API key configured"}
        # Publish would use POST /assets/v1/assets
        return {"ok": False, "error": "Publish not yet implemented (requires file upload)"}

    def health_check(self) -> bool:
        return bool(self.api_key)


class GumroadAdapter(MarketAdapter):
    """Gumroad — REST API for digital products."""

    id = "gumroad"
    name = "Gumroad"
    base_url = "https://api.gumroad.com"
    revenue_share = 0.9  # 90% to seller
    has_api = True
    has_publish_api = True

    def __init__(self, api_key: str = ""):
        super().__init__()
        self.api_key = api_key
        if api_key:
            self.client = get_client("gumroad", base_url=self.base_url)

    async def discover_listings(self, category: str = "", limit: int = 100) -> list[dict]:
        if not self.client:
            return []
        data = self.client.get("/v2/products")
        if not data:
            return []
        products = data if isinstance(data, list) else data.get("products", [])
        return [self._normalize_listing(p) for p in products[:limit]]

    def _normalize_listing(self, item: dict) -> dict:
        return {
            "id": f"gumroad:{item.get('id', '')}",
            "marketplace": "gumroad",
            "marketplace_id": str(item.get("id", "")),
            "title": item.get("name", ""),
            "description": item.get("description", "")[:2000],
            "url": item.get("url", ""),
            "price": item.get("price", 0) / 100,  # cents to dollars
            "currency": item.get("currency", "usd"),
            "category": "",
            "sales": item.get("sales_count", 0),
            "rating": 0,
            "extra": {
                "tags": item.get("tags", []),
                "is_published": item.get("is_published", False),
            },
        }

    def health_check(self) -> bool:
        return bool(self.api_key)


class ItchAdapter(MarketAdapter):
    """itch.io — REST API for games and assets."""

    id = "itch"
    name = "itch.io"
    base_url = "https://itch.io/api/1"
    revenue_share = 0.9  # 90% to seller
    has_api = True
    has_publish_api = True

    def __init__(self, api_key: str = ""):
        super().__init__()
        self.api_key = api_key
        if api_key:
            self.client = get_client("itch", base_url=self.base_url)

    async def discover_listings(self, category: str = "", limit: int = 100) -> list[dict]:
        if not self.client:
            return []
        data = self.client.get("/my-games")
        if not data:
            return []
        games = data if isinstance(data, list) else data.get("games", [])
        return [self._normalize_listing(g) for g in games[:limit]]

    def _normalize_listing(self, item: dict) -> dict:
        return {
            "id": f"itch:{item.get('id', '')}",
            "marketplace": "itch",
            "marketplace_id": str(item.get("id", "")),
            "title": item.get("title", ""),
            "description": item.get("description", "")[:2000],
            "url": item.get("url", ""),
            "price": float(item.get("price", "0") or "0"),
            "currency": item.get("currency", "usd"),
            "category": "",
            "sales": item.get("downloads_count", 0),
            "rating": 0,
            "extra": {
                "views": item.get("views_count", 0),
            },
        }

    def health_check(self) -> bool:
        return bool(self.api_key)


class AdobeStockAdapter(MarketAdapter):
    """Adobe Stock — Contributor API."""

    id = "adobe"
    name = "Adobe Stock"
    base_url = "https://stock.adobe.com/Rest/Media/1/AdobeStock/2"
    revenue_share = 0.33  # 33% to contributor
    has_api = True
    has_publish_api = True

    def __init__(self, api_key: str = ""):
        super().__init__()
        self.api_key = api_key

    async def discover_listings(self, category: str = "", limit: int = 100) -> list[dict]:
        # Adobe Stock search is public
        if not self.client:
            self.client = get_client("adobe", base_url=self.base_url)
        data = self.client.get("/search", params={"search_parameters[media_id]": "1", "limit": limit})
        if not data:
            return []
        items = data if isinstance(data, list) else data.get("items", [])
        return [self._normalize_listing(item) for item in items[:limit]]

    def _normalize_listing(self, item: dict) -> dict:
        return {
            "id": f"adobe:{item.get('id', '')}",
            "marketplace": "adobe",
            "marketplace_id": str(item.get("id", "")),
            "title": item.get("title", ""),
            "description": item.get("description", "")[:2000],
            "url": item.get("url", ""),
            "price": 0,  # Adobe sets pricing
            "currency": "USD",
            "category": item.get("category", ""),
            "sales": item.get("downloads_count", 0),
            "rating": item.get("rating", 0),
            "extra": {
                "keywords": item.get("keywords", []),
                "creator": item.get("creator_name", ""),
            },
        }

    def health_check(self) -> bool:
        return True  # Search is public


class X402BazaarAdapter(MarketAdapter):
    """x402 Bazaar — discovery layer for paid APIs."""

    id = "x402bazaar"
    name = "x402 Bazaar"
    base_url = "https://x402.org"
    revenue_share = 1.0
    has_api = True
    has_publish_api = False  # Discovery only

    def __init__(self):
        super().__init__()
        self.client = get_client("x402bazaar", base_url=self.base_url)

    async def discover_listings(self, category: str = "", limit: int = 100) -> list[dict]:
        data = self.client.get("/api/bazaar/list", params={"limit": limit})
        if not data:
            return []
        items = data if isinstance(data, list) else data.get("services", [])
        return [self._normalize_listing(item) for item in items[:limit]]

    def _normalize_listing(self, item: dict) -> dict:
        price = item.get("price", {})
        amount = price.get("amount", 0) if isinstance(price, dict) else 0
        return {
            "id": f"x402bazaar:{item.get('resource', '')}",
            "marketplace": "x402bazaar",
            "marketplace_id": item.get("resource", ""),
            "title": item.get("description", "")[:100],
            "description": item.get("description", ""),
            "url": item.get("resource", ""),
            "price": amount / 1_000_000 if amount else 0,  # USDC atomics to dollars
            "currency": "USDC",
            "category": item.get("category", ""),
            "sales": 0,
            "rating": 0,
            "extra": {
                "protocol": item.get("protocol", ""),
                "payTo": item.get("payTo", ""),
                "networks": item.get("networks", []),
            },
        }

    def health_check(self) -> bool:
        r = self.client.get("/api/bazaar/list", params={"limit": 1})
        return r is not None
