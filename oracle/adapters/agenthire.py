"""AgentHire adapter — x402 on Solana, 30+ capabilities, agent-to-agent."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client


class AgentHireAdapter:
    id = "agenthire"
    name = "AgentHire"
    base_url = "https://api.agenthire.app"

    def __init__(self):
        self.client = get_client("agenthire", base_url=self.base_url)

    async def discover(self) -> list[dict]:
        agents = self.client.get("/v1/agents", params={"limit": 100, "active": True})
        if not agents:
            return []
        items = agents if isinstance(agents, list) else agents.get("agents", [])
        # Also get jobs/services
        services = self.client.get("/v1/services", params={"limit": 100}) or []
        if isinstance(services, dict):
            services = services.get("services", [])
        return items + services

    def normalize(self, raw: dict) -> dict:
        return {
            "id": f"agenthire:{raw.get('id', raw.get('agent_id', raw.get('service_id', '')))}",
            "source": "agenthire",
            "source_id": str(raw.get("id", raw.get("agent_id", raw.get("service_id", "")))),
            "title": raw.get("name", raw.get("title", raw.get("service_name", ""))),
            "description": raw.get("description", raw.get("capabilities_desc", ""))[:2000],
            "url": f"https://agenthire.app/agent/{raw.get('id', '')}",
            "type": "service" if "service" in raw else "agent",
            "category": raw.get("category", "general"),
            "skills": raw.get("capabilities", raw.get("skills", [])),
            "reward_advertised": raw.get("price_usdc", raw.get("price", 0)),
            "reward_currency": "USDC",
            "reward_usd": raw.get("price_usdc", raw.get("price", 0)),
            "buyer_id": raw.get("owner", raw.get("creator", "")),
            "status": raw.get("status", "active"),
            "extra": {
                "chain": raw.get("chain", "solana"),
                "x402_enabled": raw.get("x402_enabled", False),
                "total_earned": raw.get("total_earned", 0),
                "reputation": raw.get("reputation", 0),
            },
        }

    def health_check(self) -> bool:
        r = self.client.get("/v1/agents", params={"limit": 1})
        return r is not None
