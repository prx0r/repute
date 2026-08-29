"""Observation tracker — the core product.

Records every meaningful state change with timestamps.
This is what nobody else has: the polling observations that become
time-to-first-bid, proposal velocity, time-to-claim, competition index.

Key principle: never claim exact timestamps for polled data.
Record intervals with after/before bounds.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any

from .store import get_db


@dataclass
class Observation:
    """A single point-in-time observation of an opportunity's state.

    The interval fields are critical: we don't know exact timestamps
    for polled changes, only the window in which they occurred.
    """
    opportunity_id: str
    source: str

    # What changed
    metric: str  # e.g. "proposal_count", "status", "reward_usd"
    previous: Any = None
    current: Any = None
    change: Any = None

    # When (with uncertainty)
    observed_at: str = ""  # when we polled
    interval_after: str = ""  # previous poll time
    interval_before: str = ""  # current poll time

    # Provenance
    adapter_version: str = "0.1.0"
    raw_hash: str = ""

    def __post_init__(self):
        if not self.observed_at:
            self.observed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def to_dict(self) -> dict:
        return asdict(self)


def record_observation(
    opportunity_id: str,
    source: str,
    metric: str,
    previous: Any,
    current: Any,
    observed_at: str = "",
    interval_after: str = "",
    interval_before: str = "",
    adapter_version: str = "0.1.0",
    raw_hash: str = "",
) -> dict:
    """Record a single observation. Returns the observation dict."""
    if not observed_at:
        observed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if not interval_after:
        interval_after = observed_at
    if not interval_before:
        interval_before = observed_at

    # Compute change
    if previous is not None and current is not None:
        try:
            change = current - previous
        except (TypeError, ValueError):
            change = None
    else:
        change = None

    obs = Observation(
        opportunity_id=opportunity_id,
        source=source,
        metric=metric,
        previous=previous,
        current=current,
        change=change,
        observed_at=observed_at,
        interval_after=interval_after,
        interval_before=interval_before,
        adapter_version=adapter_version,
        raw_hash=raw_hash,
    )

    conn = get_db()
    conn.execute(
        "INSERT INTO observations "
        "(opportunity_id, source, metric, previous_value, current_value, change_value, "
        "observed_at, interval_after, interval_before, adapter_version, raw_hash) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (obs.opportunity_id, obs.source, obs.metric,
         json.dumps(obs.previous, default=str) if obs.previous is not None else None,
         json.dumps(obs.current, default=str) if obs.current is not None else None,
         json.dumps(obs.change, default=str) if obs.change is not None else None,
         obs.observed_at, obs.interval_after, obs.interval_before,
         obs.adapter_version, obs.raw_hash)
    )
    conn.commit()
    conn.close()

    return obs.to_dict()


def diff_and_record(
    opportunity_id: str,
    source: str,
    old_state: dict | None,
    new_state: dict,
    observed_at: str = "",
    interval_after: str = "",
    interval_before: str = "",
    adapter_version: str = "0.1.0",
) -> list[dict]:
    """Compare old and new state, record observations for every change.

    This is the core diffing logic. Returns list of observations recorded.
    """
    if not observed_at:
        observed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if not interval_after:
        interval_after = observed_at
    if not interval_before:
        interval_before = observed_at

    observations = []

    if old_state is None:
        # First observation — record initial state
        for key in ["status", "reward_usd", "proposals_count", "views_count",
                     "worker_id", "actual_payment_usd"]:
            if key in new_state and new_state[key] is not None:
                obs = record_observation(
                    opportunity_id=opportunity_id,
                    source=source,
                    metric=key,
                    previous=None,
                    current=new_state[key],
                    observed_at=observed_at,
                    interval_after=interval_after,
                    interval_before=interval_before,
                    adapter_version=adapter_version,
                )
                observations.append(obs)
        return observations

    # Diff each tracked metric
    tracked = ["status", "reward_usd", "proposals_count", "views_count",
               "worker_id", "actual_payment_usd"]

    for key in tracked:
        old_val = old_state.get(key)
        new_val = new_state.get(key)

        # Normalize for comparison
        if old_val == new_val:
            continue
        if old_val is None and new_val is None:
            continue

        obs = record_observation(
            opportunity_id=opportunity_id,
            source=source,
            metric=key,
            previous=old_val,
            current=new_val,
            observed_at=observed_at,
            interval_after=interval_after,
            interval_before=interval_before,
            adapter_version=adapter_version,
        )
        observations.append(obs)

    return observations


def get_observations(
    opportunity_id: str = "",
    source: str = "",
    metric: str = "",
    since: str = "",
    limit: int = 100,
) -> list[dict]:
    """Query observations with filters."""
    conn = get_db()
    query = "SELECT * FROM observations WHERE 1=1"
    params = []

    if opportunity_id:
        query += " AND opportunity_id=?"
        params.append(opportunity_id)
    if source:
        query += " AND source=?"
        params.append(source)
    if metric:
        query += " AND metric=?"
        params.append(metric)
    if since:
        query += " AND observed_at >= ?"
        params.append(since)

    query += " ORDER BY observed_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        d["previous_value"] = json.loads(d["previous_value"]) if d["previous_value"] else None
        d["current_value"] = json.loads(d["current_value"]) if d["current_value"] else None
        d["change_value"] = json.loads(d["change_value"]) if d["change_value"] else None
        results.append(d)

    return results


def compute_metrics(opportunity_id: str) -> dict:
    """Compute derived metrics for a single opportunity from its observations."""
    observations = get_observations(opportunity_id=opportunity_id, limit=1000)
    if not observations:
        return {"opportunity_id": opportunity_id, "observations": 0}

    # Sort by observed_at
    observations.sort(key=lambda o: o["observed_at"])

    metrics = {
        "opportunity_id": opportunity_id,
        "observations": len(observations),
        "first_seen": observations[0]["observed_at"],
        "last_seen": observations[-1]["observed_at"],
    }

    # Status transitions
    status_obs = [o for o in observations if o["metric"] == "status"]
    if status_obs:
        metrics["status_transitions"] = [
            {"from": o["previous_value"], "to": o["current_value"], "at": o["observed_at"]}
            for o in status_obs
        ]
        metrics["current_status"] = status_obs[-1]["current_value"]

    # Time to first bid (first proposals_count change from 0 to >0)
    proposal_obs = [o for o in observations if o["metric"] == "proposals_count"]
    if proposal_obs:
        # Find the first observation where proposals_count becomes > 0
        for po in proposal_obs:
            curr = po.get("current_value")
            if curr is not None and curr > 0:
                try:
                    from datetime import datetime
                    t_posted = datetime.fromisoformat(metrics["first_seen"].replace("Z", "+00:00"))
                    t_first = datetime.fromisoformat(po["observed_at"].replace("Z", "+00:00"))
                    metrics["time_to_first_bid_seconds"] = int((t_first - t_posted).total_seconds())
                except (ValueError, TypeError):
                    pass
                break

    # Time to claim (status change to "claimed")
    if status_obs:
        for o in status_obs:
            if o["current_value"] == "claimed":
                try:
                    from datetime import datetime
                    t_posted = datetime.fromisoformat(metrics["first_seen"].replace("Z", "+00:00"))
                    t_claimed = datetime.fromisoformat(o["observed_at"].replace("Z", "+00:00"))
                    metrics["time_to_claim_seconds"] = int((t_claimed - t_posted).total_seconds())
                except (ValueError, TypeError):
                    pass
                break

    # Time to completion
    if status_obs:
        for o in status_obs:
            if o["current_value"] in ("completed", "paid"):
                try:
                    from datetime import datetime
                    t_posted = datetime.fromisoformat(metrics["first_seen"].replace("Z", "+00:00"))
                    t_completed = datetime.fromisoformat(o["observed_at"].replace("Z", "+00:00"))
                    metrics["time_to_completion_seconds"] = int((t_completed - t_posted).total_seconds())
                except (ValueError, TypeError):
                    pass
                break

    # Proposal velocity (proposals per hour during observation window)
    if proposal_obs and len(proposal_obs) >= 2:
        try:
            from datetime import datetime
            t_start = datetime.fromisoformat(proposal_obs[0]["observed_at"].replace("Z", "+00:00"))
            t_end = datetime.fromisoformat(proposal_obs[-1]["observed_at"].replace("Z", "+00:00"))
            hours = max(0.001, (t_end - t_start).total_seconds() / 3600)
            total_proposals = proposal_obs[-1].get("current_value", 0) or 0
            metrics["proposal_velocity_per_hour"] = round(total_proposals / hours, 2)
        except (ValueError, TypeError):
            pass

    # Competition index (proposals at time of claim)
    if status_obs and proposal_obs:
        claim_time = None
        for o in status_obs:
            if o["current_value"] == "claimed":
                claim_time = o["observed_at"]
                break
        if claim_time:
            # Find the last proposals_count observation before claim
            before_claim = [o for o in proposal_obs if o["observed_at"] <= claim_time]
            if before_claim:
                last_obs = before_claim[-1]
                metrics["competition_at_claim"] = last_obs.get("current_value") or 0

    return metrics


def get_market_metrics(source: str = "", window: str = "7d") -> dict:
    """Compute market-wide metrics from observations."""
    from datetime import datetime, timedelta

    days = int(window.rstrip("d")) if window.endswith("d") else 7
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    observations = get_observations(source=source, since=since, limit=10000)

    if not observations:
        return {"source": source, "window": window, "observations": 0}

    # Aggregate
    total_changes = len(observations)
    metrics_by_type = {}
    for obs in observations:
        m = obs["metric"]
        if m not in metrics_by_type:
            metrics_by_type[m] = 0
        metrics_by_type[m] += 1

    # Opportunity count
    unique_opps = set(o["opportunity_id"] for o in observations)

    # Status distribution from latest observations per opportunity
    status_counts = {}
    for opp_id in unique_opps:
        opp_obs = [o for o in observations if o["opportunity_id"] == opp_id and o["metric"] == "status"]
        if opp_obs:
            latest = opp_obs[-1]["current_value"]
            status_counts[latest] = status_counts.get(latest, 0) + 1

    return {
        "source": source,
        "window": window,
        "total_observations": total_changes,
        "unique_opportunities": len(unique_opps),
        "metrics_by_type": metrics_by_type,
        "status_distribution": status_counts,
    }
