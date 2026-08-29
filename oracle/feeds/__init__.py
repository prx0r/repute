"""Feeds — the three data streams into the Oracle.

1. WORK     — bounties, tasks, jobs (what agents can earn from)
2. SERVICE  — tools, APIs, capabilities (what agents can use)
3. SIGNAL   — demand/supply metrics (what the market looks like)
"""
from .work import WorkFeed
from .service import ServiceFeed
from .signal import MarketFeed

__all__ = ["WorkFeed", "ServiceFeed", "MarketFeed"]
