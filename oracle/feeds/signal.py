"""Market Signal Feed — demand/supply metrics from multiple sources.

Sources: Apify, x402, Smithery, MCP Registry, npm, PyPI, OpenRouter, HuggingFace
"""
from __future__ import annotations

import json
import time
import urllib.request
from typing import Any


class MarketFeed:
    """Collects market signals from multiple sources."""

    def __init__(self):
        from ..adapters.bittensor import BittensorAdapter
        from ..adapters.virtuals import VirtualsACPAdapter
        self.sources = {
            "smithery": SmitherySignal(),
            "mcp_registry": MCPRegistrySignal(),
            "openrouter": OpenRouterSignal(),
            "npm": NPMSignal(),
            "hf": HuggingFaceSignal(),
            "agenteconomy": AgentEconomySignal(),
            "bittensor": BittensorSignal(BittensorAdapter()),
            "virtuals": VirtualsSignal(VirtualsACPAdapter()),
        }

    async def collect(self) -> list[dict]:
        all_signals = []
        for source_id, adapter in self.sources.items():
            try:
                items = await adapter.fetch()
                for item in items:
                    item["source"] = source_id
                    all_signals.append(item)
            except Exception as e:
                print(f"  [signal] {source_id} error: {e}")
        return all_signals


class BaseSignal:
    def _get(self, url: str) -> Any:
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "MoltworkOracle/0.1"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except Exception:
            return None


class SmitherySignal(BaseSignal):
    async def fetch(self) -> list[dict]:
        data = self._get("https://api.smithery.ai/servers?limit=100")
        if not data:
            return []
        servers = data if isinstance(data, list) else data.get("servers", data.get("data", []))
        return [self._normalize(s) for s in servers]

    def _normalize(self, s: dict) -> dict:
        return {
            "id": f"smithery:{s.get('qualifiedName', s.get('id', ''))}",
            "source": "smithery",
            "source_id": s.get("qualifiedName", s.get("id", "")),
            "url": s.get("url", ""),
            "name": s.get("qualifiedName", s.get("name", "")),
            "description": (s.get("description") or "")[:500],
            "category": s.get("category", ""),
            "use_count": s.get("useCount", 0),
            "verified": s.get("verified", False),
            "deployed": s.get("deployed", False),
            "created_at": s.get("createdAt", ""),
            "raw": s,
        }


class MCPRegistrySignal(BaseSignal):
    async def fetch(self) -> list[dict]:
        data = self._get("https://registry.modelcontextprotocol.io/v0.1/servers?limit=100")
        if not data:
            return []
        servers = data.get("servers", [])
        return [self._normalize(s) for s in servers]

    def _normalize(self, s: dict) -> dict:
        return {
            "id": f"mcp_registry:{s.get('name', '')}",
            "source": "mcp_registry",
            "source_id": s.get("name", ""),
            "url": s.get("repository", s.get("homepage", "")),
            "name": s.get("name", ""),
            "description": (s.get("description") or "")[:500],
            "category": s.get("category", ""),
            "version": s.get("version", ""),
            "created_at": s.get("published_at", s.get("createdAt", "")),
            "raw": s,
        }


class OpenRouterSignal(BaseSignal):
    async def fetch(self) -> list[dict]:
        data = self._get("https://openrouter.ai/api/v1/models?limit=50")
        if not data:
            return []
        models = data.get("data", [])
        return [self._normalize(m) for m in models]

    def _normalize(self, m: dict) -> dict:
        pricing = m.get("pricing", {})
        return {
            "id": f"openrouter:{m.get('id', '')}",
            "source": "openrouter",
            "source_id": m.get("id", ""),
            "url": m.get("url", ""),
            "name": m.get("name", ""),
            "description": (m.get("description") or "")[:500],
            "category": "llm",
            "pricing": pricing,
            "context_length": m.get("context_length", 0),
            "raw": m,
        }


class NPMSignal(BaseSignal):
    PACKAGES = [
        "@modelcontextprotocol/sdk",
        "langchain",
        "crewai",
        "autogen",
        "bittensor",
        "openai",
        "anthropic",
    ]

    async def fetch(self) -> list[dict]:
        items = []
        for pkg in self.PACKAGES:
            data = self._get(f"https://api.npmjs.org/downloads/point/last-week/{pkg}")
            if data:
                items.append(self._normalize(pkg, data))
        return items

    def _normalize(self, pkg: str, data: dict) -> dict:
        return {
            "id": f"npm:{pkg}",
            "source": "npm",
            "source_id": pkg,
            "url": f"https://www.npmjs.com/package/{pkg}",
            "name": pkg,
            "description": f"npm package: {pkg}",
            "category": "package",
            "downloads_week": data.get("downloads", 0),
            "raw": data,
        }


class HuggingFaceSignal(BaseSignal):
    async def fetch(self) -> list[dict]:
        data = self._get("https://huggingface.co/api/models?limit=20&sort=downloads&direction=-1")
        if not data:
            return []
        return [self._normalize(m) for m in data]

    def _normalize(self, m: dict) -> dict:
        return {
            "id": f"hf:{m.get('id', '')}",
            "source": "hf",
            "source_id": m.get("id", ""),
            "url": f"https://huggingface.co/{m.get('id', '')}",
            "name": m.get("id", ""),
            "description": (m.get("description") or "")[:500],
            "category": m.get("pipeline_tag", ""),
            "downloads": m.get("downloads", 0),
            "likes": m.get("likes", 0),
            "tags": m.get("tags", []),
            "raw": m,
        }


class AgentEconomySignal(BaseSignal):
    async def fetch(self) -> list[dict]:
        data = self._get("https://agenteconomy.to/data.json")
        if not data:
            return []
        # Extract key metrics
        items = []
        for key, value in data.items():
            if isinstance(value, dict) and "daily" in str(value):
                items.append({
                    "id": f"agenteconomy:{key}",
                    "source": "agenteconomy",
                    "source_id": key,
                    "url": "https://agenteconomy.to",
                    "name": key,
                    "description": f"Agent economy metric: {key}",
                    "category": "macro",
                    "metrics": value,
                    "raw": value,
                })
        return items[:20]  # Limit to 20 key metrics


class BittensorSignal:
    """Bittensor subnet incentives — 129 subnets of machine work."""
    def __init__(self, adapter):
        self.adapter = adapter

    async def fetch(self) -> list[dict]:
        items = await self.adapter.discover()
        return items


class VirtualsSignal:
    """Virtuals ACP — agent-to-agent commerce telemetry."""
    def __init__(self, adapter):
        self.adapter = adapter

    async def fetch(self) -> list[dict]:
        items = await self.adapter.discover()
        # Only keep agents with data
        return [i for i in items if i.get("type") == "agent" and i.get("data", {}).get("successful_job_count", 0) > 0]
