"""Superteam Earn adapter — Solana ecosystem, 211K members, bounties + projects."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client


class SuperteamAdapter:
    id = "superteam"
    name = "Superteam Earn"
    base_url = "https://superteam.fun"

    def __init__(self):
        self.client = get_client("superteam", base_url=self.base_url)

    async def discover(self) -> list[dict]:
        listings = self.client.get("/api/listings", params={"limit": 100, "status": "open"})
        if not listings:
            return []
        return listings if isinstance(listings, list) else listings.get("listings", [])

    def normalize(self, raw: dict) -> dict:
        # SuperTeam uses camelCase: rewardAmount, not reward_amount
        reward = raw.get("rewardAmount", raw.get("reward_amount", raw.get("reward", 0)))
        if isinstance(reward, str):
            try: reward = float(reward.replace(",", ""))
            except: reward = 0
        token = raw.get("token", "USDC")

        return {
            "id": f"superteam:{raw.get('id', raw.get('listing_id', ''))}",
            "source": "superteam",
            "source_id": str(raw.get("id", raw.get("listing_id", ""))),
            "title": raw.get("title", raw.get("name", "")),
            "description": raw.get("description", "")[:2000],
            "url": f"https://superteam.fun/earn/listing/{raw.get('slug', raw.get('id', ''))}",
            "type": raw.get("type", "bounty"),
            "category": raw.get("track", raw.get("category", "general")),
            "skills": raw.get("skills", []),
            "reward_advertised": float(reward) if reward else 0,
            "reward_currency": token,
            "reward_usd": float(reward) if reward else 0,
            "buyer_id": raw.get("sponsorId", raw.get("sponsor_id", "")),
            "buyer_name": raw.get("sponsorName", raw.get("sponsor_name", "")),
            "status": raw.get("status", "OPEN"),
            "posted_at": raw.get("createdAt", raw.get("created_at", "")),
            "extra": {
                "sponsor_name": raw.get("sponsorName", raw.get("sponsor_name", "")),
                "submissions_count": raw.get("_count", {}).get("submissions", 0) if isinstance(raw.get("_count"), dict) else 0,
                "agent_eligible": raw.get("agentAccess", "") != "HUMAN_ONLY",
                "compensation_type": raw.get("compensationType", "fixed"),
                "deadline": raw.get("deadline", ""),
                "is_featured": raw.get("isFeatured", False),
            },
        }

    def health_check(self) -> bool:
        r = self.client.get("/api/listings", params={"limit": 1})
        return r is not None
