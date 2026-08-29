"""AgentHansa adapter — comprehensive data extraction.

Endpoints called:
  GET /api/collective/bounties/public  — open bounties
  GET /api/agents/skills               — available skills catalog
  GET /api/arena/games                 — arena games
  GET /api/agents/me/quick-earn        — verification tasks
  GET /ledger                          — transaction history

Data extracted:
  - Bounty listings with difficulty, limits, join counts
  - Skills catalog (what's available to learn)
  - Arena game types and availability
  - Verification task inventory
  - Transaction/transfer activity
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client
from oracle.store import store_agent_profile, store_platform_stat


class AgentHansaAdapter:
    id = "agenthansa"
    name = "AgentHansa"
    base_url = "https://www.agenthansa.com"

    def __init__(self):
        self.client = get_client("agenthansa", base_url=self.base_url)

    async def discover(self) -> list[dict]:
        items = []

        # 1. Bounties
        bounties = self.client.get("/api/collective/bounties/public", params={"limit": 100})
        if bounties:
            b_list = bounties if isinstance(bounties, list) else bounties.get("bounties", [])
            for b in b_list:
                items.append({"type": "bounty", "data": b})

        # 2. Skills catalog
        skills = self.client.get("/api/agents/skills")
        if skills:
            s_list = skills if isinstance(skills, list) else skills.get("skills", [])
            for s in s_list:
                items.append({"type": "skill", "data": s})

        # 3. Arena games
        games = self.client.get("/api/arena/games")
        if games:
            g_list = games if isinstance(games, list) else games.get("games", [])
            for g in g_list:
                items.append({"type": "arena_game", "data": g})

        # 4. Quick-earn tasks
        quick_earn = self.client.get("/api/agents/me/quick-earn")
        if quick_earn:
            q_list = quick_earn if isinstance(quick_earn, list) else quick_earn.get("tasks", [])
            for q in q_list:
                items.append({"type": "verification_task", "data": q})

        # 5. Platform stats
        stats = self.client.get("/api/stats")
        if stats:
            items.append({"type": "platform_stats", "data": stats})

        return items

    def normalize(self, raw: dict) -> dict:
        item_type = raw.get("type", "bounty")
        data = raw.get("data", raw)

        if item_type == "bounty":
            return self._normalize_bounty(data)
        elif item_type == "skill":
            return self._normalize_skill(data)
        elif item_type == "arena_game":
            return self._normalize_arena(data)
        elif item_type == "verification_task":
            return self._normalize_verification(data)
        elif item_type == "platform_stats":
            return self._normalize_stats(data)
        return self._normalize_bounty(data)

    def _normalize_bounty(self, data: dict) -> dict:
        # AgentHansa uses reward_amount field
        reward = data.get("reward_amount", data.get("reward", data.get("reward_usdc", 0)))
        return {
            "id": f"agenthansa:{data.get('id', data.get('bounty_id', ''))}",
            "source": "agenthansa",
            "source_id": str(data.get("id", data.get("bounty_id", ""))),
            "title": data.get("title", data.get("name", "")),
            "description": data.get("description", data.get("task", ""))[:2000],
            "url": f"https://www.agenthansa.com/bounty/{data.get('id', '')}",
            "type": "quest",
            "category": data.get("category", data.get("type", "general")),
            "skills": data.get("tags", []),
            "reward_advertised": float(reward) if reward else 0,
            "reward_currency": data.get("currency", "points"),
            "reward_usd": float(reward) if reward else 0,
            "buyer_id": data.get("merchant", {}).get("id", "") if isinstance(data.get("merchant"), dict) else "",
            "buyer_name": data.get("merchant", {}).get("name", "") if isinstance(data.get("merchant"), dict) else "",
            "status": data.get("status", "open"),
            "posted_at": data.get("created_at", ""),
            "extra": {
                "difficulty": data.get("difficulty", ""),
                "agents_limit": data.get("max_participants", 0),
                "agents_joined": data.get("participant_count", data.get("joined", 0)),
                "deadline": data.get("deadline", ""),
                "split_method": data.get("split_method", ""),
            },
        }

    def _normalize_skill(self, data: dict) -> dict:
        """Store skills as platform stats for demand analysis."""
        skill_name = data.get("name", data.get("skill", ""))
        task_count = data.get("task_count", data.get("available_tasks", 0))
        store_platform_stat("agenthansa", f"skill:{skill_name}:tasks", str(task_count))
        return {
            "id": f"agenthansa:skill:{skill_name}",
            "source": "agenthansa",
            "source_id": f"skill:{skill_name}",
            "title": skill_name,
            "description": data.get("description", ""),
            "url": "",
            "type": "skill_listing",
            "category": data.get("category", ""),
            "skills": [skill_name],
            "reward_advertised": 0,
            "reward_currency": "USDC",
            "reward_usd": 0,
            "buyer_id": "",
            "status": "active",
            "extra": {"task_count": task_count, "difficulty": data.get("difficulty", "")},
        }

    def _normalize_arena(self, data: dict) -> dict:
        return {
            "id": f"agenthansa:arena:{data.get('key', data.get('id', ''))}",
            "source": "agenthansa",
            "source_id": str(data.get("key", data.get("id", ""))),
            "title": data.get("name", data.get("title", "")),
            "description": data.get("description", data.get("rules", ""))[:2000],
            "url": "",
            "type": "arena_game",
            "category": "gaming",
            "skills": data.get("required_skills", []),
            "reward_advertised": data.get("prize_pool", 0),
            "reward_currency": "USDC",
            "reward_usd": data.get("prize_pool", 0),
            "buyer_id": "",
            "status": data.get("status", "active"),
            "extra": {
                "game_type": data.get("game_type", ""),
                "players_count": data.get("players_count", 0),
                "matches_today": data.get("matches_today", 0),
            },
        }

    def _normalize_verification(self, data: dict) -> dict:
        return {
            "id": f"agenthansa:verify:{data.get('id', '')}",
            "source": "agenthansa",
            "source_id": str(data.get("id", "")),
            "title": data.get("name", data.get("task", "")),
            "description": data.get("description", "")[:2000],
            "url": "",
            "type": "verification_task",
            "category": "verification",
            "skills": data.get("skills", []),
            "reward_advertised": data.get("reward", 0),
            "reward_currency": "points",
            "reward_usd": 0,
            "buyer_id": "",
            "status": "active",
            "extra": {"verification_type": data.get("type", ""), "xp_reward": data.get("xp", 0)},
        }

    def _normalize_stats(self, data: dict) -> dict:
        for key, value in data.items():
            if isinstance(value, (int, float, str)):
                store_platform_stat("agenthansa", key, str(value))
        return {"type": "platform_stats", "source": "agenthansa", "data": data}

    def health_check(self) -> bool:
        r = self.client.get("/api/collective/bounties/public", params={"limit": 1})
        return r is not None
