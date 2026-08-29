"""Bittensor adapter — 129 subnets, incentive competitions.

Uses Taostats API for subnet data.
API: https://api.taostats.io
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_subnet_data, store_platform_stat


# Tracked subnets from imbroke research
TRACKED_SUBNETS = {
    118: {"name": "Ditto", "description": "Agent-memory harness", "fit": "memory/context", "status": "active"},
    11: {"name": "TrajectoryRL", "description": "Open skill factory", "fit": "skill factory", "status": "active"},
    62: {"name": "Ridges", "description": "Autonomous SWE agent", "fit": "autonomous coding", "status": "active"},
    61: {"name": "RedTeam", "description": "Security challenges", "fit": "security research", "status": "active"},
    15: {"name": "ORO", "description": "Shopping agent eval", "fit": "agent evolution", "status": "monitor"},
    60: {"name": "BitSec", "description": "Vulnerability-finding benchmark", "fit": "security research", "status": "active"},
    34: {"name": "BitMind/GAS", "description": "AI-generated-content detection", "fit": "model research", "status": "active"},
}


class BittensorAdapter:
    id = "bittensor"
    name = "Bittensor"
    base_url = "https://api.taostats.io"

    def __init__(self):
        self.client = get_client("bittensor", base_url="https://api.metagraph.sh/api/v1", requests_per_minute=20)
        self.price_client = get_client("bittensor", base_url="https://coins.llama.fi", requests_per_minute=10)

    async def discover(self) -> list[dict]:
        items = []

        # 1. TAO price
        price_data = self.price_client.get("prices/current/coingecko:bittensor")
        tao_price = 0
        if price_data:
            coins = price_data.get("coins", {})
            tao_price = coins.get("coingecko:bittensor", {}).get("price", 0)
            store_platform_stat("bittensor", "tao_price_usd", str(tao_price))

        # 2. Subnets from metagraph
        data = self.client.get("/subnets")
        if data:
            subnets = data.get("data", {}).get("subnets", []) if isinstance(data, dict) else []
            for s in subnets:
                netuid = s.get("netuid", s.get("id", 0))
                tracked = TRACKED_SUBNETS.get(netuid, {})
                emission = s.get("emission_pct", s.get("emission", 0))

                store_subnet_data({
                    "id": f"bittensor:sn{netuid}",
                    "netuid": netuid,
                    "name": tracked.get("name", s.get("name", f"SN{netuid}")),
                    "description": tracked.get("description", s.get("description", "")),
                    "emission_pct": emission,
                    "miner_count": s.get("miner_count", 0),
                    "validator_count": s.get("validator_count", 0),
                    "daily_emissions_tao": round(float(emission) * 3600, 2) if emission else 0,
                    "tao_price_usd": tao_price,
                    "gpu_required": s.get("gpu_required", False),
                    "miner_reward": tracked.get("miner_reward", ""),
                    "github": tracked.get("github", ""),
                    "status": tracked.get("status", "active"),
                    "extra": {"emission_pct": emission},
                })

                items.append({
                    "type": "subnet",
                    "data": {
                        "netuid": netuid,
                        "name": tracked.get("name", s.get("name", f"SN{netuid}")),
                        "description": tracked.get("description", s.get("description", "")),
                        "emission_pct": emission,
                        "tao_price_usd": tao_price,
                        "status": tracked.get("status", "active"),
                        "fit": tracked.get("fit", ""),
                        "github": tracked.get("github", ""),
                    }
                })

        return items

    def normalize(self, raw: dict) -> dict:
        data = raw.get("data", raw) if isinstance(raw, dict) else raw
        netuid = data.get("netuid", 0)
        tracked = TRACKED_SUBNETS.get(netuid, {})
        emission = data.get("emission_pct", 0)
        tao_price = data.get("tao_price_usd", 0)

        return {
            "id": f"bittensor:sn{netuid}",
            "source": "bittensor",
            "source_id": f"sn{netuid}",
            "url": f"https://taostats.io/subnets/{netuid}",
            "title": tracked.get("name", data.get("name", f"SN{netuid}")),
            "description": tracked.get("description", data.get("description", "")),
            "category": "incentive_market",
            "skills": [tracked.get("fit", "")] if tracked.get("fit") else [],
            "reward": round(float(emission) * 3600 * tao_price, 2) if emission else 0,
            "currency": "TAO",
            "reward_usd": round(float(emission) * 3600 * tao_price, 2) if emission else 0,
            "fee_pct": 0,
            "escrowed": False,
            "entries": 0,
            "views": 0,
            "slots": 0,
            "posted_at": "",
            "deadline": None,
            "last_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": None,
            "agent_allowed": True,
            "submission_method": "sdk",
            "auth_type": "wallet",
            "network": "bittensor",
            "buyer_id": "",
            "buyer_reputation": None,
            "buyer_historical_spend_usd": None,
            "raw": data,
        }

    def health_check(self) -> bool:
        r = self.client.get("/subnets")
        return r is not None
