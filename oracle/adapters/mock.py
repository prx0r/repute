"""Oracle adapter for Mock/test data."""
from __future__ import annotations

import time
import random
from typing import Any


class MockAdapter:
    """Test adapter that generates fake opportunity data."""

    id = "mock"
    name = "Mock (Test)"
    base_url = ""

    SAMPLE_SKILLS = [
        "solidity", "rust", "typescript", "python", "react",
        "foundry", "security", "web-scraping", "data-analysis",
        "content-writing", "design", "smart-contracts",
    ]

    SAMPLE_CATEGORIES = ["development", "security", "content", "research", "design"]

    SAMPLE_TITLES = [
        "Audit Solidity bridge contract",
        "Build Rust indexer for on-chain data",
        "Research L2 gas optimization techniques",
        "Write content for DeFi protocol docs",
        "Design landing page for token launch",
        "Fix XSS vulnerability in web app",
        "Build Telegram bot for price alerts",
        "Analyze MEV extraction patterns",
        "Create dataset of NFT sales history",
        "Implement ZK proof verifier in TypeScript",
    ]

    def __init__(self, count: int = 20):
        self.count = count

    async def discover(self) -> list[dict]:
        """Generate fake opportunities."""
        items = []
        for i in range(self.count):
            budget = round(random.uniform(5, 500), 2)
            skills = random.sample(self.SAMPLE_SKILLS, k=random.randint(1, 4))
            status = random.choice(["open", "open", "open", "claimed", "completed"])

            created = time.time() - random.uniform(0, 86400 * 7)

            item = {
                "id": f"mock_{i:04d}",
                "title": random.choice(self.SAMPLE_TITLES),
                "description": f"Test opportunity #{i}. Budget: ${budget}. Skills: {', '.join(skills)}.",
                "budget_usdc": budget,
                "category": random.choice(self.SAMPLE_CATEGORIES),
                "status": status,
                "skills": skills,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(created)),
                "proposal_count": random.randint(0, 15),
            }
            items.append(item)
        return items

    def normalize(self, raw: dict) -> dict:
        return {
            "id": f"mock:{raw.get('id', '')}",
            "source": "mock",
            "source_id": raw.get("id", ""),
            "title": raw.get("title", ""),
            "description": raw.get("description", ""),
            "url": "",
            "type": "bounty",
            "category": raw.get("category", "general"),
            "skills": raw.get("skills", []),
            "reward_advertised": raw.get("budget_usdc", 0),
            "reward_currency": "USDC",
            "reward_usd": raw.get("budget_usdc", 0),
            "buyer_id": "mock_buyer",
            "buyer_name": "Test Buyer",
            "status": raw.get("status", "open"),
            "posted_at": raw.get("created_at", ""),
            "proposals_count": raw.get("proposal_count", 0),
        }

    def health_check(self) -> bool:
        return True
