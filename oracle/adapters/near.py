"""NEAR AI Agent Market adapter — comprehensive data extraction.

Endpoints called:
  /v1/jobs                    — open jobs
  /v1/jobs/:id                — job details
  /v1/agents                  — agent registrations
  /v1/models                  — AI model catalog

Data extracted:
  - Job listings with escrow and chain data
  - Agent registrations and capabilities
  - AI model catalog and pricing (GLM, Qwen, OpenAI, Anthropic, Gemini)
  - Inference verification data (TEE)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_agent_profile, store_service_listing, store_platform_stat


class NEARAIAdapter:
    id = "near"
    name = "NEAR AI Agent Market"
    base_url = "https://market.near.ai"

    def __init__(self):
        self.client = get_client("near", base_url=self.base_url)

    async def discover(self) -> list[dict]:
        items = []

        # 1. Jobs
        jobs = self.client.get("/v1/jobs", params={"limit": 100, "status": "open"})
        if jobs:
            j_list = jobs if isinstance(jobs, list) else jobs.get("jobs", [])
            for j in j_list:
                items.append({"type": "job", "data": j})

        # 2. Agents
        agents = self.client.get("/v1/agents", params={"limit": 100})
        if agents:
            a_list = agents if isinstance(agents, list) else agents.get("agents", [])
            for a in a_list:
                items.append({"type": "agent", "data": a})
                store_agent_profile({
                    "id": f"near:agent:{a.get('id', a.get('address', ''))}",
                    "source": "near",
                    "source_agent_id": str(a.get("id", a.get("address", ""))),
                    "name": a.get("name", ""),
                    "description": a.get("description", "")[:2000],
                    "url": f"https://market.near.ai/agent/{a.get('id', '')}",
                    "tier": a.get("tier", ""),
                    "reputation_score": a.get("reputation", 0),
                    "jobs_completed": a.get("completed_jobs", 0),
                    "total_earned_usd": a.get("total_earned", 0),
                    "success_rate": a.get("success_rate", 0),
                    "capabilities": a.get("capabilities", []),
                    "wallet_address": a.get("address", ""),
                    "chain": "near",
                    "extra": {"models": a.get("models", [])},
                })

        # 3. Models
        models = self.client.get("/v1/models", params={"limit": 100})
        if models:
            m_list = models if isinstance(models, list) else models.get("models", [])
            for m in m_list:
                items.append({"type": "model", "data": m})
                store_service_listing({
                    "id": f"near:model:{m.get('id', m.get('name', ''))}",
                    "source": "near",
                    "source_service_id": str(m.get("id", m.get("name", ""))),
                    "title": m.get("name", ""),
                    "description": m.get("description", "")[:2000],
                    "url": f"https://market.near.ai/model/{m.get('id', '')}",
                    "category": "inference",
                    "price_usdc": m.get("price_per_1k_tokens", 0),
                    "price_per_call": m.get("price_per_1k_tokens", 0),
                    "provider_id": m.get("provider", ""),
                    "provider_reputation": 0,
                    "total_calls": m.get("total_calls", 0),
                    "status": "active" if m.get("active", True) else "inactive",
                    "capabilities": [m.get("provider", "")],
                    "extra": {"context_window": m.get("context_window", 0)},
                })

        # 4. Platform stats
        stats = self.client.get("/v1/stats")
        if stats:
            items.append({"type": "platform_stats", "data": stats})

        return items

    def normalize(self, raw: dict) -> dict:
        item_type = raw.get("type", "job")
        data = raw.get("data", raw)

        if item_type == "job":
            return self._normalize_job(data)
        elif item_type == "agent":
            return self._normalize_agent(data)
        elif item_type == "model":
            return self._normalize_model(data)
        elif item_type == "platform_stats":
            return self._normalize_stats(data)
        return self._normalize_job(data)

    def _normalize_job(self, data: dict) -> dict:
        return {
            "id": f"near:{data.get('id', data.get('job_id', ''))}",
            "source": "near",
            "source_id": str(data.get("id", data.get("job_id", ""))),
            "title": data.get("title", data.get("name", "")),
            "description": data.get("description", "")[:2000],
            "url": f"https://market.near.ai/job/{data.get('id', '')}",
            "type": data.get("type", "job"),
            "category": data.get("category", "general"),
            "skills": data.get("skills", data.get("requirements", [])),
            "reward_advertised": data.get("reward_usdc", data.get("budget", 0)),
            "reward_currency": "USDC",
            "reward_usd": data.get("reward_usdc", data.get("budget", 0)),
            "buyer_id": data.get("poster", data.get("client", "")),
            "status": data.get("status", "open"),
            "posted_at": data.get("created_at", ""),
            "extra": {
                "chain": "near",
                "escrow_type": data.get("escrow_type", ""),
                "instant": data.get("instant", False),
            },
        }

    def _normalize_agent(self, data: dict) -> dict:
        return {
            "id": f"near:agent:{data.get('id', data.get('address', ''))}",
            "source": "near",
            "source_id": str(data.get("id", data.get("address", ""))),
            "title": data.get("name", ""),
            "description": data.get("description", "")[:2000],
            "url": f"https://market.near.ai/agent/{data.get('id', '')}",
            "type": "agent_profile",
            "category": "worker",
            "skills": data.get("capabilities", []),
            "reward_advertised": 0,
            "reward_currency": "USDC",
            "reward_usd": data.get("total_earned", 0),
            "buyer_id": "",
            "status": "active",
            "extra": {
                "completed_jobs": data.get("completed_jobs", 0),
                "reputation": data.get("reputation", 0),
                "models": data.get("models", []),
            },
        }

    def _normalize_model(self, data: dict) -> dict:
        return {
            "id": f"near:model:{data.get('id', data.get('name', ''))}",
            "source": "near",
            "source_id": str(data.get("id", data.get("name", ""))),
            "title": data.get("name", ""),
            "description": data.get("description", "")[:2000],
            "url": f"https://market.near.ai/model/{data.get('id', '')}",
            "type": "model",
            "category": "inference",
            "skills": [data.get("provider", "")],
            "reward_advertised": data.get("price_per_1k_tokens", 0),
            "reward_currency": "USDC",
            "reward_usd": data.get("price_per_1k_tokens", 0),
            "buyer_id": "",
            "status": "active" if data.get("active", True) else "inactive",
            "extra": {
                "provider": data.get("provider", ""),
                "context_window": data.get("context_window", 0),
                "total_calls": data.get("total_calls", 0),
            },
        }

    def _normalize_stats(self, data: dict) -> dict:
        for key, value in data.items():
            if isinstance(value, (int, float, str)):
                store_platform_stat("near", key, str(value))
        return {"type": "platform_stats", "source": "near", "data": data}

    def health_check(self) -> bool:
        r = self.client.get("/v1/jobs", params={"limit": 1})
        return r is not None
