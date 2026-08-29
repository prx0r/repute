"""AgentScout — platform intelligence module.

Loads structured manifests from agentscout/platforms/*.json
and provides objective queryable data about agent marketplaces.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PLATFORMS_DIR = Path(__file__).parent / "platforms"


def _load_manifests() -> dict[str, dict]:
    """Load all platform manifests and flatten key fields."""
    manifests = {}
    if not PLATFORMS_DIR.exists():
        return manifests
    for f in PLATFORMS_DIR.glob("*.json"):
        try:
            raw = json.loads(f.read_text())
            pid = raw.get("id", f.stem)

            # Flatten nested fields for easy querying
            econ = raw.get("economics", {})
            api = raw.get("api", {})
            market = raw.get("market_signals", {})
            agent = raw.get("agent_friendliness", {})

            flat = {
                "id": pid,
                "name": raw.get("name", pid),
                "url": raw.get("url", ""),
                "type": raw.get("type", "unknown"),
                "category": raw.get("category", "unknown"),

                # Economics (flat)
                "payment_rail": econ.get("payment_rail", "unknown"),
                "chain": econ.get("chain", "unknown"),
                "currency": econ.get("currency", "unknown"),
                "platform_fee_pct": econ.get("platform_fee_percent", econ.get("platform_fee_pct", 0)),
                "escrow": econ.get("escrow", False),

                # API (flat)
                "api_type": api.get("api_type") or ("rest" if api.get("base_url") else "none"),
                "auth": api.get("auth_method", "unknown"),
                "api_base_url": api.get("base_url", ""),
                "docs_url": api.get("docs_url", ""),
                "has_mcp": bool(api.get("mcp_server") or api.get("mcp")),
                "mcp_server": api.get("mcp_server", api.get("mcp", "")),
                "has_sdk": bool(api.get("sdk")),
                "rate_limit": api.get("rate_limits", "unknown"),

                # Market signals (flat)
                "total_listings": market.get("total_listings", 0),
                "active_listings": market.get("active_listings", 0),
                "total_volume_usd": market.get("total_volume_usd", 0),
                "avg_reward_usd": market.get("avg_reward_usd", 0),

                # Agent friendliness (flat)
                "agent_welcomed": agent.get("agent_welcomed", agent.get("has_api", False)),
                "agent_api": agent.get("has_api", False),
                "agent_docs": agent.get("docs_url", ""),

                # Raw data for deep queries
                "_raw": raw,
            }
            manifests[pid] = flat
        except Exception:
            pass
    return manifests


_manifests: dict[str, dict] | None = None


def _ensure_loaded():
    global _manifests
    if _manifests is None:
        _manifests = _load_manifests()


def get_platform(platform_id: str) -> dict | None:
    """Get a single platform manifest by ID."""
    _ensure_loaded()
    return _manifests.get(platform_id)


def list_platforms(
    category: str = "",
    platform_type: str = "",
    has_api: bool | None = None,
    has_mcp: bool | None = None,
    payment_rail: str = "",
    agent_welcomed: bool | None = None,
) -> list[dict]:
    """Query platforms with filters."""
    _ensure_loaded()
    results = list(_manifests.values())

    if category:
        results = [p for p in results if category.lower() in p.get("category", "").lower()]
    if platform_type:
        results = [p for p in results if platform_type.lower() in p.get("type", "").lower()]
    if has_api is not None:
        if has_api:
            results = [p for p in results if p.get("api_type") not in ("none", None, "unknown")]
        else:
            results = [p for p in results if p.get("api_type") in ("none", None, "unknown")]
    if has_mcp is not None:
        results = [p for p in results if p.get("has_mcp") == has_mcp]
    if payment_rail:
        results = [p for p in results if payment_rail.lower() in p.get("payment_rail", "").lower()]
    if agent_welcomed is not None:
        results = [p for p in results if p.get("agent_welcomed") == agent_welcomed]

    return results


def compare_platforms(ids: list[str]) -> list[dict]:
    """Get side-by-side comparison of specific platforms."""
    _ensure_loaded()
    return [_manifests[pid] for pid in ids if pid in _manifests]


def get_market_summary() -> dict:
    """Get aggregate stats across all platforms."""
    _ensure_loaded()
    platforms = list(_manifests.values())

    total = len(platforms)
    by_type = {}
    by_chain = {}
    by_fee = {"free": 0, "low_5pct": 0, "medium_10pct": 0}

    for p in platforms:
        t = p.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

        c = p.get("chain", "unknown")
        if isinstance(c, list):
            for chain in c:
                by_chain[chain] = by_chain.get(chain, 0) + 1
        else:
            by_chain[c] = by_chain.get(c, 0) + 1

        fee = p.get("platform_fee_pct", 0) or 0
        if fee == 0:
            by_fee["free"] += 1
        elif fee <= 5:
            by_fee["low_5pct"] += 1
        else:
            by_fee["medium_10pct"] += 1

    api_count = sum(1 for p in platforms if p.get("api_type") not in ("none", None, "unknown"))
    mcp_count = sum(1 for p in platforms if p.get("has_mcp"))
    agent_welcomed = sum(1 for p in platforms if p.get("agent_welcomed"))

    return {
        "total_platforms": total,
        "by_type": by_type,
        "by_chain": by_chain,
        "by_fee": by_fee,
        "with_api": api_count,
        "with_mcp": mcp_count,
        "agent_welcomed": agent_welcomed,
    }
