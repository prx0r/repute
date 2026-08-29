"""BountyBook adapter — comprehensive data extraction.

Endpoints called:
  /jobs?status=open&category={cat}  — bounties across 9 categories
  /agents/:address                  — agent profiles
  /leaderboard                      — top earners
  /stats                            — platform stats
  /jobs/:id                         — individual job details

Data extracted:
  - Bounties with difficulty, estimated time, escrow data
  - Agent profiles with tier, earnings, completion rate
  - Leaderboard (top earners)
  - Platform health metrics
  - Job queue size (demand signal)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_agent_profile, store_platform_stat


class BountyBookAdapter:
    id = "bountybook"
    name = "BountyBook"
    base_url = "https://api.bountybook.ai"
    api_url = "https://api.bountybook.ai"

    CATEGORIES = ["research", "code", "data", "content", "monitor", "workflow", "scrape", "transform", "fetch"]

    def __init__(self):
        self.client = get_client("bountybook", base_url=self.api_url)

    async def discover(self) -> list[dict]:
        items = []

        # 1. Bounties across all categories
        for cat in self.CATEGORIES:
            jobs = self.client.get("/jobs", params={"status": "open", "category": cat, "limit": 100})
            if jobs:
                job_list = jobs if isinstance(jobs, list) else jobs.get("jobs", jobs.get("matched", []))
                for job in job_list:
                    items.append({"type": "bounty", "data": job})

        # 2. Leaderboard
        leaderboard = self.client.get("/leaderboard")
        if leaderboard:
            lb_list = leaderboard if isinstance(leaderboard, list) else leaderboard.get("leaders", leaderboard.get("agents", []))
            for agent in lb_list:
                items.append({"type": "agent", "data": agent})
                # Store as agent profile
                store_agent_profile({
                    "id": f"bountybook:agent:{agent.get('address', agent.get('wallet', ''))}",
                    "source": "bountybook",
                    "source_agent_id": str(agent.get("address", agent.get("wallet", ""))),
                    "name": agent.get("name", agent.get("address", "")[:10]),
                    "description": "",
                    "url": f"https://www.bountybook.ai/agent/{agent.get('address', '')}",
                    "tier": agent.get("tier", ""),
                    "reputation_score": agent.get("score", 0),
                    "jobs_completed": agent.get("completed", agent.get("bounties_completed", 0)),
                    "total_earned_usd": agent.get("earned", agent.get("total_earned_usdc", 0)),
                    "success_rate": agent.get("success_rate", 0),
                    "capabilities": [],
                    "wallet_address": agent.get("address", agent.get("wallet", "")),
                    "chain": "base",
                    "extra": {"rank": agent.get("rank", 0)},
                })

        # 3. Platform stats
        stats = self.client.get("/stats")
        if stats:
            items.append({"type": "platform_stats", "data": stats})

        return items

    def normalize(self, raw: dict) -> dict:
        item_type = raw.get("type", "bounty")
        data = raw.get("data", raw)

        if item_type == "bounty":
            return self._normalize_bounty(data)
        elif item_type == "agent":
            return self._normalize_agent(data)
        elif item_type == "platform_stats":
            return self._normalize_stats(data)
        return self._normalize_bounty(data)

    def _normalize_bounty(self, data: dict) -> dict:
        budget = 0
        budget_raw = data.get("budget_usdc", data.get("budget", 0))
        if isinstance(budget_raw, str):
            try:
                budget = float(budget_raw.replace("$", "").replace(",", ""))
            except ValueError:
                pass
        elif isinstance(budget_raw, (int, float)):
            budget = budget_raw

        status_map = {"open": "open", "claimed": "claimed", "submitted": "submitted",
                      "verified": "completed", "failed": "failed", "expired": "expired"}
        status = status_map.get(data.get("status", ""), "open")

        return {
            "id": f"bountybook:{data.get('id', '')}",
            "source": "bountybook",
            "source_id": str(data.get("id", "")),
            "title": data.get("title", ""),
            "description": (data.get("description") or "")[:2000],
            "url": f"https://www.bountybook.ai/job/{data.get('id', '')}",
            "type": "bounty",
            "category": data.get("job_type", "general"),
            "skills": data.get("tags", []),
            "reward_advertised": budget,
            "reward_currency": "USDC",
            "reward_usd": budget,
            "buyer_id": data.get("poster_address", ""),
            "buyer_name": data.get("poster_address", "")[:10] + "...",
            "status": status,
            "posted_at": data.get("created_at", ""),
            "claimed_at": data.get("claimed_at") or "",
            "submitted_at": data.get("submitted_at") or "",
            "completed_at": data.get("verified_at") or "",
            "worker_id": data.get("executor_address", ""),
            "extra": {
                "difficulty": data.get("difficulty", ""),
                "estimated_minutes": data.get("estimated_minutes", 0),
                "escrow_tx": data.get("escrow", {}).get("tx_hash", ""),
                "platform_fee_pct": 4,
                "queue_size": data.get("queue_size", 0),
            },
        }

    def _normalize_agent(self, data: dict) -> dict:
        return {
            "id": f"bountybook:agent:{data.get('address', data.get('wallet', ''))}",
            "source": "bountybook",
            "source_id": str(data.get("address", data.get("wallet", ""))),
            "title": data.get("name", data.get("address", "")[:10]),
            "description": "",
            "url": f"https://www.bountybook.ai/agent/{data.get('address', '')}",
            "type": "agent_profile",
            "category": "worker",
            "skills": [],
            "reward_advertised": 0,
            "reward_currency": "USDC",
            "reward_usd": data.get("total_earned_usdc", 0),
            "buyer_id": "",
            "status": "active",
            "extra": {
                "tier": data.get("tier", ""),
                "completed": data.get("completed", 0),
                "success_rate": data.get("success_rate", 0),
                "rank": data.get("rank", 0),
            },
        }

    def _normalize_stats(self, data: dict) -> dict:
        for key, value in data.items():
            if isinstance(value, (int, float, str)):
                store_platform_stat("bountybook", key, str(value))
        return {"type": "platform_stats", "source": "bountybook", "data": data}

    def health_check(self) -> bool:
        r = self.client.get("/jobs", params={"limit": 1})
        return r is not None
