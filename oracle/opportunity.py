"""OpportunitySpec — universal contract for all opportunity types.

Every opportunity (bounty, competition, service, emission, resource)
is represented as an economic contract + execution protocol.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any


# === The Universal Opportunity Spec ===

@dataclass
class OpportunitySpec:
    """Universal representation of any economically rewarded opportunity."""

    # Identity
    id: str
    source: str
    source_id: str
    url: str

    # Classification
    kind: str  # bounty, competition, service, emission, resource
    title: str
    description: str

    # What's needed
    capabilities: list[str]
    deliverables: list[str]
    hardware: dict  # gpu, ram, etc.
    credentials: list[str]
    evaluation: dict  # benchmark, scoring mechanism

    # Economics
    reward_model: str  # fixed, winner_take_all, ranked, proportional, per_call, emission
    reward_asset: str  # USDC, TAO, USD, etc.
    reward_nominal: float
    reward_pool_usd: float
    entry_fee_usd: float
    gas_estimate_usd: float
    capital_required_usd: float
    capital_at_risk_usd: float
    capital_lock_hours: float

    # Competition
    entries: int
    active_workers: int
    slots: int
    incumbent_score: float
    score_distribution: dict

    # Execution
    estimated_compute_usd: float
    estimated_api_usd: float
    estimated_wall_hours: float
    estimated_human_minutes: float
    automation_level: str  # H0, H1, H2, H3, H4
    submission_method: str  # rest, cli, sdk, onchain, service

    # Prediction
    p_entry: float
    p_award: float
    p_accept: float
    expected_payout_usd: float
    expected_net_usd: float
    confidence: float

    # Raw data
    raw: dict

    def to_dict(self) -> dict:
        return asdict(self)

    def ev(self) -> float:
        """Calculate expected value."""
        return self.expected_payout_usd - (
            self.entry_fee_usd + self.gas_estimate_usd +
            self.estimated_compute_usd + self.estimated_api_usd
        )


# === Standard Lifecycle Interface ===

class OpportunityAdapter:
    """Every platform adapter implements this conceptual interface."""

    async def discover(self) -> list[dict]:
        """Find available opportunities."""
        return []

    async def hydrate(self, id: str) -> dict:
        """Get full details for an opportunity."""
        return {}

    async def preflight(self, id: str, worker: dict) -> dict:
        """Check if worker can execute this opportunity."""
        return {"feasible": True, "reasons": []}

    async def enter(self, id: str, strategy: dict) -> dict:
        """Enter/claim/register for an opportunity."""
        return {"receipt": "", "status": "entered"}

    async def submit(self, id: str, artifact: dict) -> dict:
        """Submit work/artifact."""
        return {"receipt": "", "status": "submitted"}

    async def status(self, id: str) -> dict:
        """Check current status."""
        return {"status": "unknown"}

    async def outcome(self, id: str) -> dict:
        """Get final outcome (accepted/rejected/payout)."""
        return {"outcome": "unknown", "payout": 0}

    async def settlement(self, id: str) -> dict:
        """Get payment/settlement details."""
        return {"settled": False, "amount": 0}


# === Human Intervention Levels ===

HUMAN_LEVELS = {
    "H0": "Fully autonomous after secrets provisioned",
    "H1": "One-time human setup; thereafter autonomous",
    "H2": "Human approval required per opportunity",
    "H3": "Human contributes materially to deliverable",
    "H4": "Fundamentally human-only",
}


# === EV Calculation ===

def calculate_ev(spec: dict) -> dict:
    """Calculate expected value for an opportunity."""
    # Gross expected payout
    p_award = spec.get("p_award", 0)
    p_accept = spec.get("p_accept", 1)
    payout = spec.get("expected_payout_usd", 0)
    gross = p_award * p_accept * payout

    # Costs
    costs = (
        spec.get("entry_fee_usd", 0) +
        spec.get("gas_estimate_usd", 0) +
        spec.get("estimated_compute_usd", 0) +
        spec.get("estimated_api_usd", 0) +
        spec.get("capital_at_risk_usd", 0) * 0.01  # 1% capital risk
    )

    net = gross - costs

    return {
        "gross_payout": round(gross, 2),
        "total_costs": round(costs, 2),
        "net_ev": round(net, 2),
        "p_get_paid": round(p_award * p_accept, 4),
    }
