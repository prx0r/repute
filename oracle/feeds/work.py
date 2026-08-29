"""Work Feed — bounties, tasks, jobs that agents can get paid for.

Sources: SuperTeam, GitHub, BountyBook, AgentHansa, Daydreams, RentAHuman
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from typing import Any


class WorkFeed:
    """Collects and normalizes work opportunities from multiple sources."""

    def __init__(self):
        from ..adapters.near_market import NEARMarketAdapter
        from ..adapters.openserv import OpenServAdapter
        self.sources = {
            "superteam": SuperTeamWork(),
            "github": GitHubWork(),
            "bountybook": BountyBookWork(),
            "agenthansa": AgentHansaWork(),
            "daydreams": DaydreamsWork(),
            "rentahuman": RentAHumanWork(),
            "near": NEARWork(NEARMarketAdapter()),
            "openserv": OpenServWork(OpenServAdapter()),
        }

    async def collect(self) -> list[dict]:
        """Collect work from all sources."""
        all_work = []
        for source_id, adapter in self.sources.items():
            try:
                items = await adapter.fetch()
                for item in items:
                    item["source"] = source_id
                    all_work.append(item)
            except Exception as e:
                print(f"  [work] {source_id} error: {e}")
        return all_work


class BaseWork:
    def _get(self, url: str) -> Any:
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "MoltworkOracle/0.1"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except Exception:
            return None


class SuperTeamWork(BaseWork):
    async def fetch(self) -> list[dict]:
        data = self._get("https://superteam.fun/api/listings?limit=100")
        if not data:
            return []
        items = data if isinstance(data, list) else data.get("listings", [])
        return [self._normalize(b) for b in items]

    def _normalize(self, b: dict) -> dict:
        reward = b.get("rewardAmount") or 0
        return {
            "id": f"superteam:{b.get('id', '')}",
            "source": "superteam",
            "source_id": str(b.get("id", "")),
            "url": f"https://superteam.fun/earn/listing/{b.get('slug', '')}",
            "title": b.get("title", ""),
            "description": (b.get("description") or "")[:500],
            "category": b.get("type", "bounty"),
            "skills": [],
            "reward": float(reward),
            "currency": b.get("token", "USDG"),
            "reward_usd": float(reward),
            "fee_pct": 0,
            "escrowed": False,
            "entries": b.get("_count", {}).get("submissions", 0) if isinstance(b.get("_count"), dict) else 0,
            "views": 0,
            "slots": 1,
            "posted_at": b.get("createdAt", ""),
            "deadline": b.get("deadline", ""),
            "last_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": None,
            "agent_allowed": b.get("agentAccess", "") != "HUMAN_ONLY",
            "submission_method": "api",
            "auth_type": "api_key",
            "network": "crypto",
            "buyer_id": b.get("sponsorId", ""),
            "buyer_reputation": None,
            "buyer_historical_spend_usd": None,
            "raw": b,
        }


class GitHubWork(BaseWork):
    def __init__(self, token: str = ""):
        self.token = token or os.environ.get("GITHUB_TOKEN", "")

    async def fetch(self) -> list[dict]:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        url = "https://api.github.com/search/issues?q=label:bounty+is:open+is:issue&per_page=100"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                return [self._normalize(i) for i in data.get("items", [])]
        except Exception:
            return []

    def _normalize(self, i: dict) -> dict:
        amount = 0
        text = f"{i.get('title', '')} {i.get('body', '')[:500]}"
        for p in [r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\b', r'Bounty:\s*\$?(\d+)']:
            m = re.search(p, text)
            if m:
                try: amount = float(m.group(1).replace(",", ""))
                except: pass
                break

        return {
            "id": f"github:{i.get('html_url', '').split('/')[-1]}",
            "source": "github",
            "source_id": str(i.get("number", "")),
            "url": i.get("html_url", ""),
            "title": i.get("title", ""),
            "description": (i.get("body") or "")[:500],
            "category": "development",
            "skills": [],
            "reward": amount,
            "currency": "USD",
            "reward_usd": amount,
            "fee_pct": 0,
            "escrowed": False,
            "entries": 0,
            "views": 0,
            "slots": 1,
            "posted_at": i.get("created_at", ""),
            "deadline": None,
            "last_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": i.get("closed_at"),
            "agent_allowed": True,
            "submission_method": "github_pr",
            "auth_type": "oauth",
            "network": "fiat",
            "buyer_id": i.get("user", {}).get("login", ""),
            "buyer_reputation": None,
            "buyer_historical_spend_usd": None,
            "raw": i,
        }


class BountyBookWork(BaseWork):
    async def fetch(self) -> list[dict]:
        data = self._get("https://api.bountybook.ai/jobs?limit=100")
        if not data:
            return []
        jobs = data.get("jobs", [])
        return [self._normalize(j) for j in jobs]

    def _normalize(self, j: dict) -> dict:
        budget = j.get("budget_usdc", 0)
        if isinstance(budget, str):
            try: budget = float(budget.replace("$", ""))
            except: budget = 0
        return {
            "id": f"bountybook:{j.get('id', '')}",
            "source": "bountybook",
            "source_id": str(j.get("id", "")),
            "url": f"https://www.bountybook.ai/job/{j.get('id', '')}",
            "title": j.get("title", ""),
            "description": (j.get("description") or "")[:500],
            "category": j.get("job_type", "general"),
            "skills": j.get("tags", []),
            "reward": budget,
            "currency": "USDC",
            "reward_usd": budget,
            "fee_pct": 4,
            "escrowed": True,
            "entries": 0,
            "views": 0,
            "slots": 1,
            "posted_at": j.get("created_at", ""),
            "deadline": j.get("deadline"),
            "last_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": None,
            "agent_allowed": True,
            "submission_method": "api",
            "auth_type": "wallet",
            "network": "base",
            "buyer_id": j.get("poster_address", ""),
            "buyer_reputation": None,
            "buyer_historical_spend_usd": None,
            "raw": j,
        }


class AgentHansaWork(BaseWork):
    async def fetch(self) -> list[dict]:
        data = self._get("https://www.agenthansa.com/api/collective/bounties/public?limit=100")
        if not data:
            return []
        bounties = data.get("bounties", [])
        return [self._normalize(b) for b in bounties]

    def _normalize(self, b: dict) -> dict:
        return {
            "id": f"agenthansa:{b.get('id', '')}",
            "source": "agenthansa",
            "source_id": str(b.get("id", "")),
            "url": f"https://www.agenthansa.com/bounty/{b.get('id', '')}",
            "title": b.get("title", ""),
            "description": (b.get("description") or "")[:500],
            "category": b.get("category", "general"),
            "skills": b.get("tags", []),
            "reward": float(b.get("reward_amount", 0)),
            "currency": b.get("currency", "points"),
            "reward_usd": float(b.get("reward_amount", 0)),
            "fee_pct": 5,
            "escrowed": False,
            "entries": b.get("participant_count", 0),
            "views": 0,
            "slots": b.get("max_participants", 1),
            "posted_at": b.get("created_at", ""),
            "deadline": b.get("deadline"),
            "last_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": b.get("completed_at"),
            "agent_allowed": True,
            "submission_method": "api",
            "auth_type": "api_key",
            "network": "base",
            "buyer_id": b.get("merchant", {}).get("id", "") if isinstance(b.get("merchant"), dict) else "",
            "buyer_reputation": None,
            "buyer_historical_spend_usd": None,
            "raw": b,
        }


class DaydreamsWork(BaseWork):
    async def fetch(self) -> list[dict]:
        data = self._get("https://taskmarket.dev/api/tasks?limit=100")
        if not data:
            return []
        tasks = data.get("tasks", [])
        return [self._normalize(t) for t in tasks]

    def _normalize(self, t: dict) -> dict:
        reward_raw = t.get("reward", 0) or 0
        if isinstance(reward_raw, str):
            try: reward_raw = float(reward_raw)
            except: reward_raw = 0
        reward_usdc = reward_raw / 1_000_000 if reward_raw > 1000 else reward_raw
        return {
            "id": f"daydreams:{str(t.get('id', ''))[:20]}",
            "source": "daydreams",
            "source_id": str(t.get("id", ""))[:20],
            "url": f"https://taskmarket.dev/task/{t.get('id', '')}",
            "title": (t.get("description") or "")[:100],
            "description": (t.get("description") or "")[:500],
            "category": t.get("tags", ["general"])[0] if t.get("tags") else "general",
            "skills": t.get("tags", []),
            "reward": round(reward_usdc, 6),
            "currency": "USDC",
            "reward_usd": round(reward_usdc, 6),
            "fee_pct": 0,
            "escrowed": True,
            "entries": t.get("submissionCount", 0),
            "views": 0,
            "slots": 1,
            "posted_at": t.get("createdAt", ""),
            "deadline": t.get("expiryTime"),
            "last_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": None,
            "agent_allowed": True,
            "submission_method": "x402",
            "auth_type": "wallet",
            "network": "base",
            "buyer_id": t.get("requester", ""),
            "buyer_reputation": None,
            "buyer_historical_spend_usd": None,
            "raw": t,
        }


class RentAHumanWork(BaseWork):
    async def fetch(self) -> list[dict]:
        data = self._get("https://rentahuman.ai/api/bounties?limit=100")
        if not data:
            return []
        bounties = data if isinstance(data, list) else data.get("bounties", [])
        return [self._normalize(b) for b in bounties]

    def _normalize(self, b: dict) -> dict:
        price = b.get("price", 0)
        if isinstance(price, str):
            try: price = float(price.replace("$", ""))
            except: price = 0
        return {
            "id": f"rentahuman:{b.get('id', '')}",
            "source": "rentahuman",
            "source_id": str(b.get("id", "")),
            "url": f"https://rentahuman.ai/bounty/{b.get('id', '')}",
            "title": b.get("title", ""),
            "description": (b.get("description") or "")[:500],
            "category": b.get("category", "general"),
            "skills": b.get("skillsNeeded", []),
            "reward": float(price) if price else 0,
            "currency": b.get("currency", "USD"),
            "reward_usd": float(price) if price else 0,
            "fee_pct": 0,
            "escrowed": False,
            "entries": b.get("applicationCount", 0),
            "views": b.get("viewCount", 0),
            "slots": b.get("spotsAvailable", 0),
            "posted_at": b.get("createdAt", ""),
            "deadline": None,
            "last_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": None,
            "agent_allowed": True,
            "submission_method": "api",
            "auth_type": "api_key",
            "network": "fiat",
            "buyer_id": b.get("requester_id", ""),
            "buyer_reputation": None,
            "buyer_historical_spend_usd": None,
            "raw": b,
        }



class NEARWork:
    """NEAR Agent Market — crypto-native work tape."""
    def __init__(self, adapter):
        self.adapter = adapter

    async def fetch(self) -> list[dict]:
        items = await self.adapter.discover()
        return [i for i in items if i.get("type") == "job"]


class OpenServWork:
    """OpenServ Ideaboard — ideas → x402 endpoints."""
    def __init__(self, adapter):
        self.adapter = adapter

    async def fetch(self) -> list[dict]:
        items = await self.adapter.discover()
        return [i for i in items if i.get("type") == "idea"]
