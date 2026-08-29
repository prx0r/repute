"""gigs.sh adapter — meta-directory of 46 agent-earning platforms."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from oracle.http_client import get_client


class GigsShAdapter:
    id = "gigs"
    name = "gigs.sh"
    base_url = "https://gigs.sh/api/v1"

    def __init__(self):
        self.client = get_client("gigs", base_url=self.base_url)

    async def discover(self) -> list[dict]:
        listings = self.client.get("/gigs", params={"limit": 200})
        if not listings:
            return []
        return listings if isinstance(listings, list) else listings.get("results", listings.get("listings", []))

    def normalize(self, raw: dict) -> dict:
        return {
            "id": f"gigs:{raw.get('slug', raw.get('id', ''))}",
            "source": "gigs",
            "source_id": str(raw.get("slug", raw.get("id", ""))),
            "title": raw.get("name", raw.get("title", "")),
            "description": raw.get("description", raw.get("excerpt", ""))[:2000],
            "url": raw.get("url", raw.get("website", f"https://gigs.sh/{raw.get('slug', '')}")),
            "type": "platform",
            "category": raw.get("category", "general"),
            "skills": raw.get("tags", []),
            "reward_advertised": 0,
            "reward_currency": raw.get("payment_rail", "USD"),
            "reward_usd": 0,
            "buyer_id": "",
            "status": raw.get("status", "active"),
            "extra": {
                "agent_welcomed": raw.get("agentWelcomed", False),
                "payment_rail": raw.get("paymentRail", ""),
                "friction": raw.get("friction", ""),
                "verified": raw.get("verified", False),
                "platform_url": raw.get("url", ""),
            },
        }

    def health_check(self) -> bool:
        r = self.client.get("/gigs", params={"limit": 1})
        return r is not None
