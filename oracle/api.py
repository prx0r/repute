"""Oracle REST API — /v1/* endpoints.

Free, public, queryable intelligence layer for the agent economy.
"""
from __future__ import annotations

import json
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from .store import query_opportunities, query_events, get_stats, get_db
from .schema import EventType

router = APIRouter(prefix="/v1", tags=["oracle"])


# === Markets ===

@router.get("/markets")
def list_markets():
    """List all source markets with activity stats."""
    conn = get_db()
    sources = conn.execute("""
        SELECT source,
               COUNT(*) as total_events,
               COUNT(DISTINCT source_id) as unique_items,
               MIN(observed_at) as first_seen,
               MAX(observed_at) as last_seen
        FROM events
        GROUP BY source
        ORDER BY total_events DESC
    """).fetchall()

    markets = []
    for s in sources:
        src = s["source"]
        total_usd = conn.execute(
            "SELECT SUM(reward_usd) FROM opportunities WHERE source=? AND reward_usd > 0",
            (src,)
        ).fetchone()[0]

        markets.append({
            "source": src,
            "total_events": s["total_events"],
            "unique_items": s["unique_items"],
            "first_seen": s["first_seen"],
            "last_seen": s["last_seen"],
            "total_advertised_usd": round(total_usd or 0, 2),
        })

    conn.close()
    return {"markets": markets, "count": len(markets)}


# === Opportunities ===

@router.get("/opportunities")
def list_opportunities(
    source: str = "",
    status: str = "",
    category: str = "",
    skills: str = "",
    min_reward: float = 0,
    limit: int = 50,
):
    """List opportunities with filters."""
    opps = query_opportunities(source=source, status=status, category=category,
                               skills=skills, limit=limit)

    if min_reward > 0:
        opps = [o for o in opps if o.get("reward_usd", 0) >= min_reward]

    return {
        "opportunities": opps,
        "count": len(opps),
    }


@router.get("/opportunities/{opp_id}")
def get_opportunity(opp_id: str):
    """Get full opportunity details + observation history."""
    conn = get_db()
    opp = conn.execute("SELECT * FROM opportunities WHERE id=?", (opp_id,)).fetchone()
    if not opp:
        conn.close()
        raise HTTPException(404, "Opportunity not found")

    result = dict(opp)
    result["skills"] = json.loads(result.get("skills") or "[]")
    result["extra"] = json.loads(result.get("extra") or "{}")

    # Get event history
    events = conn.execute(
        "SELECT * FROM events WHERE subject_id LIKE ? ORDER BY observed_at",
        (f"%{opp_id}%",)
    ).fetchall()
    result["history"] = [dict(e) for e in events]

    conn.close()
    return result


# === Demand ===

@router.get("/demand")
def get_demand(
    skill: str = "",
    category: str = "",
    window: str = "30d",
    limit: int = 25,
):
    """Demand by skill/agent_type with time window."""
    conn = get_db()

    # Parse window
    days = 30
    if window.endswith("d"):
        days = int(window[:-1])
    elif window.endswith("w"):
        days = int(window[:-1]) * 7

    since_ts = time.time() - (days * 86400)
    since_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(since_ts))

    query = "SELECT * FROM opportunities WHERE first_seen_at >= ?"
    params = [since_str]

    if skill:
        query += " AND skills LIKE ?"
        params.append(f"%{skill}%")
    if category:
        query += " AND category = ?"
        params.append(category)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    # Aggregate
    total = len(rows)
    total_usd = sum(r["reward_usd"] or 0 for r in rows)
    open_count = sum(1 for r in rows if r["status"] == "open")
    completed_count = sum(1 for r in rows if r["status"] in ("completed", "paid"))

    # Skill frequency
    skill_counts = {}
    for r in rows:
        skills = json.loads(r["skills"] or "[]")
        for s in skills:
            skill_counts[s] = skill_counts.get(s, 0) + 1

    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # Category breakdown
    cat_counts = {}
    for r in rows:
        cat = r["category"] or "unknown"
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    return {
        "window": window,
        "total_opportunities": total,
        "total_advertised_usd": round(total_usd, 2),
        "open": open_count,
        "completed": completed_count,
        "completion_rate": round(completed_count / max(1, total), 4),
        "top_skills": [{"skill": s, "count": c} for s, c in top_skills],
        "categories": cat_counts,
        "filter": {"skill": skill, "category": category},
    }


@router.get("/demand/gaps")
def demand_gaps():
    """Supply/demand imbalance — which agent types have unmet demand."""
    conn = get_db()

    # Get categories with demand but few completions
    categories = conn.execute("""
        SELECT category,
               COUNT(*) as total,
               SUM(CASE WHEN reward_usd > 0 THEN reward_usd ELSE 0 END) as total_usd,
               SUM(CASE WHEN status IN ('completed', 'paid') THEN 1 ELSE 0 END) as completed,
               SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_count
        FROM opportunities
        WHERE category != ''
        GROUP BY category
        HAVING total >= 3
        ORDER BY total_usd DESC
    """).fetchall()
    conn.close()

    gaps = []
    for c in categories:
        completion_rate = c["completed"] / max(1, c["total"])
        gap_score = c["open_count"] / max(1, c["completed"])
        gaps.append({
            "category": c["category"],
            "total_opportunities": c["total"],
            "total_advertised_usd": round(c["total_usd"] or 0, 2),
            "open": c["open_count"],
            "completed": c["completed"],
            "completion_rate": round(completion_rate, 4),
            "gap_score": round(gap_score, 2),
        })

    gaps.sort(key=lambda x: x["gap_score"], reverse=True)
    return {"gaps": gaps, "count": len(gaps)}


# === Skills ===

@router.get("/skills")
def list_skills(window: str = "30d", limit: int = 50):
    """All skills with counts and trending."""
    conn = get_db()
    days = 30
    if window.endswith("d"):
        days = int(window[:-1])

    since_ts = time.time() - (days * 86400)
    since_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(since_ts))

    rows = conn.execute(
        "SELECT skills, reward_usd, first_seen_at FROM opportunities WHERE first_seen_at >= ?",
        (since_str,)
    ).fetchall()
    conn.close()

    skill_stats = {}
    for r in rows:
        skills = json.loads(r["skills"] or "[]")
        for s in skills:
            if s not in skill_stats:
                skill_stats[s] = {"count": 0, "total_usd": 0, "opportunities": []}
            skill_stats[s]["count"] += 1
            skill_stats[s]["total_usd"] += r["reward_usd"] or 0

    skills_list = []
    for skill, stats in skill_stats.items():
        skills_list.append({
            "skill": skill,
            "count": stats["count"],
            "total_advertised_usd": round(stats["total_usd"], 2),
            "avg_reward": round(stats["total_usd"] / max(1, stats["count"]), 2),
        })

    skills_list.sort(key=lambda x: x["count"], reverse=True)
    return {"skills": skills_list[:limit], "count": len(skills_list)}


@router.get("/skills/trending")
def trending_skills(window_current: str = "7d", window_previous: str = "30d", limit: int = 20):
    """Fastest-growing skills (current window vs previous)."""
    conn = get_db()

    def _skill_counts(since_str: str) -> dict:
        rows = conn.execute(
            "SELECT skills FROM opportunities WHERE first_seen_at >= ?", (since_str,)
        ).fetchall()
        counts = {}
        for r in rows:
            for s in json.loads(r["skills"] or "[]"):
                counts[s] = counts.get(s, 0) + 1
        return counts

    now = time.time()
    days_current = int(window_current.rstrip("d")) if window_current.endswith("d") else 7
    days_previous = int(window_previous.rstrip("d")) if window_previous.endswith("d") else 30

    current = _skill_counts(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - days_current * 86400)))
    previous = _skill_counts(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - days_previous * 86400)))

    # Normalize to daily rates for fair comparison across different window sizes
    trending = []
    for skill, count in current.items():
        prev = previous.get(skill, 0)
        daily_current = count / max(1, days_current)
        daily_previous = prev / max(1, days_previous)
        growth = (daily_current - daily_previous) / max(0.01, daily_previous)
        trending.append({
            "skill": skill,
            "current_count": count,
            "previous_count": prev,
            "daily_rate_current": round(daily_current, 2),
            "daily_rate_previous": round(daily_previous, 2),
            "growth_rate": round(growth, 4),
        })

    trending.sort(key=lambda x: x["growth_rate"], reverse=True)
    return {"trending": trending[:limit]}


# === Sources ===

@router.get("/sources")
def list_sources():
    """List source adapters and their health."""
    from .adapters import SourceRegistry
    registry = SourceRegistry()

    # Import and register known adapters
    try:
        from .adapters.github import GitHubAdapter
        registry.register(GitHubAdapter())
    except: pass
    try:
        from .adapters.algora import AlgoraAdapter
        registry.register(AlgoraAdapter())
    except: pass
    try:
        from .adapters.moltjobs import MoltJobsAdapter
        registry.register(MoltJobsAdapter())
    except: pass
    try:
        from .adapters.bountybook import BountyBookAdapter
        registry.register(BountyBookAdapter())
    except: pass

    sources = []
    for adapter in registry.active():
        health = False
        try:
            health = adapter.health_check()
        except: pass

        sources.append({
            "id": adapter.id,
            "name": adapter.name,
            "base_url": adapter.base_url if hasattr(adapter, "base_url") else "",
            "healthy": health,
        })

    return {"sources": sources, "count": len(sources)}


# === Timeseries ===

@router.get("/timeseries")
def timeseries(
    metric: str = "opportunities",
    interval: str = "day",
    window: str = "30d",
):
    """Time-bucketed metrics."""
    conn = get_db()
    days = 30
    if window.endswith("d"):
        days = int(window[:-1])

    since_ts = time.time() - (days * 86400)
    since_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(since_ts))

    if metric == "opportunities":
        rows = conn.execute("""
            SELECT DATE(first_seen_at) as day, COUNT(*) as count,
                   SUM(reward_usd) as total_usd
            FROM opportunities
            WHERE first_seen_at >= ?
            GROUP BY day ORDER BY day
        """, (since_str,)).fetchall()
    elif metric == "payments":
        rows = conn.execute("""
            SELECT DATE(paid_at) as day, COUNT(*) as count,
                   SUM(amount) as total_usd
            FROM payments
            WHERE paid_at >= ?
            GROUP BY day ORDER BY day
        """, (since_str,)).fetchall()
    else:
        rows = []

    conn.close()
    return {
        "metric": metric,
        "interval": interval,
        "data": [{"date": r["day"], "count": r["count"], "total_usd": round(r["total_usd"] or 0, 2)} for r in rows],
    }


# === Stats ===

@router.get("/stats")
def stats():
    """Global oracle statistics."""
    return get_stats()


# === Agents (defined later at line ~1065, queries agent_profiles table) ===

    return {"agents": agents, "count": len(agents)}


# === Payments ===

@router.get("/payments")
def list_payments(source: str = "", limit: int = 50):
    """List verified payments."""
    conn = get_db()
    query = "SELECT * FROM payments WHERE 1=1"
    params = []
    if source:
        query += " AND source=?"
        params.append(source)
    query += " ORDER BY observed_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return {"payments": [dict(r) for r in rows], "count": len(rows)}


# === Observations (the core product) ===

@router.get("/observations")
def list_observations(
    opportunity_id: str = "",
    source: str = "",
    metric: str = "",
    since: str = "",
    limit: int = 100,
):
    """Query polling observations — the raw time-series data."""
    from .observations import get_observations
    obs = get_observations(
        opportunity_id=opportunity_id, source=source,
        metric=metric, since=since, limit=limit,
    )
    return {"observations": obs, "count": len(obs)}


@router.get("/observations/{opp_id}/timeline")
def opportunity_timeline(opp_id: str):
    """Full observation timeline for a single opportunity.

    Shows every state change with interval bounds.
    This is the dataset that produces time-to-first-bid,
    proposal velocity, time-to-claim, etc.
    """
    from .observations import get_observations
    obs = get_observations(opportunity_id=opp_id, limit=1000)
    obs.sort(key=lambda o: o["observed_at"])
    return {"opportunity_id": opp_id, "timeline": obs, "count": len(obs)}


@router.get("/observations/{opp_id}/metrics")
def opportunity_metrics(opp_id: str):
    """Derived metrics for a single opportunity.

    Computes: time_to_first_bid, time_to_claim, time_to_completion,
    proposal_velocity, competition_at_claim.
    """
    from .observations import compute_metrics
    metrics = compute_metrics(opp_id)
    return metrics


@router.get("/metrics/market")
def market_metrics(source: str = "", window: str = "7d"):
    """Market-wide metrics computed from observations."""
    from .observations import get_market_metrics
    return get_market_metrics(source=source, window=window)


@router.get("/metrics/time-to-first-bid")
def time_to_first_bid(source: str = "", window: str = "7d", limit: int = 50):
    """Median time to first bid across opportunities."""
    from .observations import get_observations
    from datetime import datetime

    days = int(window.rstrip("d")) if window.endswith("d") else 7
    import time as _time
    since = _time.strftime("%Y-%m-%dT%H:%M:%SZ",
                           _time.gmtime(_time.time() - days * 86400))

    # Get all proposal_count observations
    obs = get_observations(source=source, metric="proposals_count", since=since, limit=10000)

    # Group by opportunity
    by_opp = {}
    for o in obs:
        oid = o["opportunity_id"]
        if oid not in by_opp:
            by_opp[oid] = []
        by_opp[oid].append(o)

    # Compute time to first bid for each
    times = []
    for oid, opp_obs in by_opp.items():
        opp_obs.sort(key=lambda o: o["observed_at"])
        if opp_obs and opp_obs[0].get("previous_value") == 0:
            # First observation had 0 proposals, now has more
            try:
                t1 = datetime.fromisoformat(opp_obs[0]["interval_after"].replace("Z", "+00:00"))
                t2 = datetime.fromisoformat(opp_obs[0]["observed_at"].replace("Z", "+00:00"))
                times.append(int((t2 - t1).total_seconds()))
            except (ValueError, TypeError):
                pass

    times.sort()
    median = times[len(times) // 2] if times else 0
    p25 = times[len(times) // 4] if times else 0
    p75 = times[3 * len(times) // 4] if times else 0

    return {
        "window": window,
        "source": source,
        "sample_size": len(times),
        "median_seconds": median,
        "p25_seconds": p25,
        "p75_seconds": p75,
        "all_times": times[:limit],
    }


@router.get("/metrics/site-liquidity")
def site_liquidity(window: str = "30d"):
    """Per-source liquidity: listings, paid %, time-to-claim, competition."""
    from .observations import get_observations
    from .store import get_db
    from datetime import datetime
    import time as _time

    days = int(window.rstrip("d")) if window.endswith("d") else 30
    since = _time.strftime("%Y-%m-%dT%H:%M:%SZ",
                           _time.gmtime(_time.time() - days * 86400))

    conn = get_db()
    sources = conn.execute(
        "SELECT DISTINCT source FROM opportunities"
    ).fetchall()
    conn.close()

    results = []
    for row in sources:
        src = row["source"]

        # Get opportunities for this source
        conn = get_db()
        opps = conn.execute(
            "SELECT id, status, reward_usd FROM opportunities WHERE source=? AND first_seen_at >= ?",
            (src, since)
        ).fetchall()
        conn.close()

        if not opps:
            continue

        total = len(opps)
        completed = sum(1 for o in opps if o["status"] in ("completed", "paid"))
        paid_pct = round(completed / max(1, total), 4)

        # Average reward
        rewards = [o["reward_usd"] for o in opps if o["reward_usd"] and o["reward_usd"] > 0]
        avg_reward = round(sum(rewards) / max(1, len(rewards)), 2)

        results.append({
            "source": src,
            "total_listings": total,
            "completed": completed,
            "paid_pct": paid_pct,
            "avg_reward_usd": avg_reward,
        })

    results.sort(key=lambda x: x["paid_pct"], reverse=True)
    return {"sites": results, "window": window}


# === Agent-Native Intelligence Endpoints ===
# These are the "Dune queries" — pre-built answers to common agent questions.

@router.get("/agent-briefing")
def agent_briefing(skills: str = "", window: str = "30d", limit: int = 20):
    """I am an agent with these skills. What work exists for me?

    Returns ranked opportunities, demand trends, pricing data, and competition.
    This is the primary endpoint agents query before deciding what to work on.
    """
    from .store import get_db
    import time as _time

    days = int(window.rstrip("d")) if window.endswith("d") else 30
    since = _time.strftime("%Y-%m-%dT%H:%M:%SZ",
                           _time.gmtime(_time.time() - days * 86400))

    conn = get_db()
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]

    # Build query
    query = "SELECT * FROM opportunities WHERE first_seen_at >= ? AND status IN ('open', 'claimed')"
    params = [since]

    if skill_list:
        skill_filters = " OR ".join(["skills LIKE ?" for _ in skill_list])
        query += f" AND ({skill_filters})"
        params.extend([f"%{s}%" for s in skill_list])

    query += " ORDER BY reward_usd DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()

    # Also get historical data for pricing/competition
    hist_query = "SELECT * FROM opportunities WHERE first_seen_at >= ?"
    hist_params = [since]
    if skill_list:
        skill_filters = " OR ".join(["skills LIKE ?" for _ in skill_list])
        hist_query += f" AND ({skill_filters})"
        hist_params.extend([f"%{s}%" for s in skill_list])

    hist_rows = conn.execute(hist_query, hist_params).fetchall()
    conn.close()

    # Compute briefing
    open_opps = []
    for r in rows:
        d = dict(r)
        d["skills"] = json.loads(d.get("skills") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        open_opps.append(d)

    total = len(hist_rows)
    total_usd = sum(r["reward_usd"] or 0 for r in hist_rows)
    completed = sum(1 for r in hist_rows if r["status"] in ("completed", "paid"))
    open_count = sum(1 for r in hist_rows if r["status"] == "open")

    # Pricing stats
    rewards = [r["reward_usd"] for r in hist_rows if r["reward_usd"] and r["reward_usd"] > 0]
    rewards.sort()
    median_reward = rewards[len(rewards) // 2] if rewards else 0
    p75_reward = rewards[3 * len(rewards) // 4] if rewards else 0
    p90_reward = rewards[int(len(rewards) * 0.9)] if rewards else 0

    # Per-source breakdown
    source_stats = {}
    for r in hist_rows:
        src = r["source"]
        if src not in source_stats:
            source_stats[src] = {"total": 0, "completed": 0, "total_usd": 0, "rewards": []}
        source_stats[src]["total"] += 1
        if r["status"] in ("completed", "paid"):
            source_stats[src]["completed"] += 1
        source_stats[src]["total_usd"] += r["reward_usd"] or 0
        if r["reward_usd"] and r["reward_usd"] > 0:
            source_stats[src]["rewards"].append(r["reward_usd"])

    for src, stats in source_stats.items():
        stats["paid_pct"] = round(stats["completed"] / max(1, stats["total"]), 4)
        stats["median_reward"] = sorted(stats["rewards"])[len(stats["rewards"]) // 2] if stats["rewards"] else 0
        stats["total_usd"] = round(stats["total_usd"], 2)
        del stats["rewards"]

    # Category breakdown
    cat_counts = {}
    for r in hist_rows:
        cat = r["category"] or "unknown"
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    return {
        "skills": skill_list,
        "window": window,
        "summary": {
            "total_opportunities": total,
            "open": open_count,
            "completed": completed,
            "completion_rate": round(completed / max(1, total), 4),
            "total_advertised_usd": round(total_usd, 2),
            "median_reward_usd": round(median_reward, 2),
            "p75_reward_usd": round(p75_reward, 2),
            "p90_reward_usd": round(p90_reward, 2),
        },
        "top_opportunities": open_opps[:10],
        "by_source": source_stats,
        "by_category": cat_counts,
    }


@router.get("/source-quality")
def source_quality(window: str = "30d"):
    """Which platforms actually pay? Completion rates, payment reliability.

    Answers: "Should I spend my time on Site A or Site B?"
    """
    from .store import get_db
    import time as _time

    days = int(window.rstrip("d")) if window.endswith("d") else 30
    since = _time.strftime("%Y-%m-%dT%H:%M:%SZ",
                           _time.gmtime(_time.time() - days * 86400))

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM opportunities WHERE first_seen_at >= ?", (since,)
    ).fetchall()
    conn.close()

    # Aggregate by source
    sources = {}
    for r in rows:
        src = r["source"]
        if src not in sources:
            sources[src] = {
                "total": 0, "open": 0, "claimed": 0, "submitted": 0,
                "completed": 0, "paid": 0, "failed": 0, "expired": 0,
                "total_usd": 0, "paid_usd": 0, "rewards": [],
            }
        s = sources[src]
        s["total"] += 1
        status = r["status"] or "open"
        if status in s:
            s[status] += 1
        s["total_usd"] += r["reward_usd"] or 0
        if r["actual_payment_usd"] and r["actual_payment_usd"] > 0:
            s["paid_usd"] += r["actual_payment_usd"]
        if r["reward_usd"] and r["reward_usd"] > 0:
            s["rewards"].append(r["reward_usd"])

    results = []
    for src, s in sources.items():
        completion_rate = s["completed"] / max(1, s["total"])
        payment_rate = s["paid"] / max(1, s["completed"]) if s["completed"] > 0 else 0
        realized_pct = s["paid_usd"] / max(1, s["total_usd"]) if s["total_usd"] > 0 else 0

        results.append({
            "source": src,
            "total_listings": s["total"],
            "status_breakdown": {
                "open": s["open"], "claimed": s["claimed"],
                "submitted": s["submitted"], "completed": s["completed"],
                "paid": s["paid"], "failed": s["failed"], "expired": s["expired"],
            },
            "completion_rate": round(completion_rate, 4),
            "payment_rate": round(payment_rate, 4),
            "total_advertised_usd": round(s["total_usd"], 2),
            "total_verified_paid_usd": round(s["paid_usd"], 2),
            "realized_payment_pct": round(realized_pct, 4),
            "median_reward": round(sorted(s["rewards"])[len(s["rewards"]) // 2], 2) if s["rewards"] else 0,
        })

    results.sort(key=lambda x: x["completion_rate"], reverse=True)
    return {"window": window, "sources": results}


@router.get("/pricing-guide")
def pricing_guide(skills: str = "", category: str = "", window: str = "90d"):
    """What should I charge for these skills? Based on real market data.

    Returns percentile distribution, per-source pricing, and trend.
    """
    from .store import get_db
    import time as _time

    days = int(window.rstrip("d")) if window.endswith("d") else 90
    since = _time.strftime("%Y-%m-%dT%H:%M:%SZ",
                           _time.gmtime(_time.time() - days * 86400))

    conn = get_db()
    query = "SELECT * FROM opportunities WHERE first_seen_at >= ? AND reward_usd > 0"
    params = [since]

    if skills:
        for skill in skills.split(","):
            query += " AND skills LIKE ?"
            params.append(f"%{skill.strip()}%")
    if category:
        query += " AND category = ?"
        params.append(category)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    rewards = sorted([r["reward_usd"] for r in rows if r["reward_usd"]])
    if not rewards:
        return {"skills": skills, "category": category, "window": window,
                "message": "No pricing data found for these filters"}

    total = len(rewards)
    p10 = rewards[int(total * 0.1)]
    p25 = rewards[int(total * 0.25)]
    p50 = rewards[int(total * 0.5)]
    p75 = rewards[int(total * 0.75)]
    p90 = rewards[int(total * 0.9)]
    avg = sum(rewards) / total

    # Per-source pricing
    source_pricing = {}
    for r in rows:
        src = r["source"]
        if src not in source_pricing:
            source_pricing[src] = []
        source_pricing[src].append(r["reward_usd"])

    source_stats = {}
    for src, sr in source_pricing.items():
        sr.sort()
        source_stats[src] = {
            "count": len(sr),
            "median": round(sr[len(sr) // 2], 2),
            "p75": round(sr[int(len(sr) * 0.75)], 2) if len(sr) > 3 else round(sr[-1], 2),
        }

    return {
        "skills": skills,
        "category": category,
        "window": window,
        "sample_size": total,
        "distribution": {
            "p10": round(p10, 2), "p25": round(p25, 2),
            "median": round(p50, 2), "p75": round(p75, 2),
            "p90": round(p90, 2), "avg": round(avg, 2),
        },
        "by_source": source_stats,
        "recommendation": {
            "minimum": round(p25, 2),
            "competitive": round(p50, 2),
            "premium": round(p75, 2),
        },
    }


@router.get("/competition")
def competition_index(skills: str = "", window: str = "30d"):
    """How competitive is each skill? Agents per listing, time-to-claim.

    Answers: "Am I too late for Rust jobs? Should I pivot to WASM?"
    """
    from .store import get_db
    import time as _time

    days = int(window.rstrip("d")) if window.endswith("d") else 30
    since = _time.strftime("%Y-%m-%dT%H:%M:%SZ",
                           _time.gmtime(_time.time() - days * 86400))

    conn = get_db()
    rows = conn.execute(
        "SELECT skills, status, reward_usd, proposals_count FROM opportunities WHERE first_seen_at >= ?",
        (since,)
    ).fetchall()
    conn.close()

    # Build per-skill stats
    skill_stats = {}
    for r in rows:
        skill_list = json.loads(r["skills"] or "[]")
        for skill in skill_list:
            if skill not in skill_stats:
                skill_stats[skill] = {
                    "total": 0, "open": 0, "completed": 0,
                    "rewards": [], "proposals": [],
                }
            s = skill_stats[skill]
            s["total"] += 1
            if r["status"] == "open":
                s["open"] += 1
            elif r["status"] in ("completed", "paid"):
                s["completed"] += 1
            if r["reward_usd"] and r["reward_usd"] > 0:
                s["rewards"].append(r["reward_usd"])
            if r["proposals_count"] and r["proposals_count"] > 0:
                s["proposals"].append(r["proposals_count"])

    results = []
    for skill, s in skill_stats.items():
        avg_proposals = sum(s["proposals"]) / max(1, len(s["proposals"]))
        competition_score = avg_proposals / max(1, s["total"])
        supply_demand = s["open"] / max(1, s["total"] - s["open"])

        results.append({
            "skill": skill,
            "total_opportunities": s["total"],
            "open": s["open"],
            "completed": s["completed"],
            "avg_proposals": round(avg_proposals, 1),
            "competition_score": round(competition_score, 2),
            "supply_demand_ratio": round(supply_demand, 2),
            "median_reward": round(sorted(s["rewards"])[len(s["rewards"]) // 2], 2) if s["rewards"] else 0,
        })

    results.sort(key=lambda x: x["competition_score"], reverse=True)
    return {"window": window, "skills": results}


@router.get("/market-pulse")
def market_pulse():
    """Live market pulse — what Dune shows on its homepage.

    The single endpoint agents hit to understand the current state.
    """
    from .store import get_db
    import time as _time

    conn = get_db()

    # Last 24h
    since_24h = _time.strftime("%Y-%m-%dT%H:%M:%SZ",
                               _time.gmtime(_time.time() - 86400))
    # Last 7d
    since_7d = _time.strftime("%Y-%m-%dT%H:%M:%SZ",
                              _time.gmtime(_time.time() - 7 * 86400))

    # 24h stats
    row_24h = conn.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN reward_usd > 0 THEN reward_usd ELSE 0 END) as total_usd,
               SUM(CASE WHEN status IN ('completed', 'paid') THEN 1 ELSE 0 END) as completed,
               COUNT(DISTINCT source) as sources
        FROM opportunities WHERE first_seen_at >= ?
    """, (since_24h,)).fetchone()

    # 7d stats
    row_7d = conn.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN reward_usd > 0 THEN reward_usd ELSE 0 END) as total_usd,
               SUM(CASE WHEN status IN ('completed', 'paid') THEN 1 ELSE 0 END) as completed,
               SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_count,
               COUNT(DISTINCT source) as sources
        FROM opportunities WHERE first_seen_at >= ?
    """, (since_7d,)).fetchone()

    # All time
    all_time = conn.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN reward_usd > 0 THEN reward_usd ELSE 0 END) as total_usd,
               SUM(CASE WHEN status IN ('completed', 'paid') THEN 1 ELSE 0 END) as completed
        FROM opportunities
    """).fetchone()

    # Top skills this week
    top_skills = conn.execute("""
        SELECT skills FROM opportunities WHERE first_seen_at >= ?
    """, (since_7d,)).fetchall()
    skill_counts = {}
    for r in top_skills:
        for s in json.loads(r["skills"] or "[]"):
            skill_counts[s] = skill_counts.get(s, 0) + 1
    top_skills_sorted = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    conn.close()

    return {
        "last_24h": {
            "new_opportunities": row_24h["total"],
            "advertised_usd": round(row_24h["total_usd"] or 0, 2),
            "completed": row_24h["completed"],
            "active_sources": row_24h["sources"],
        },
        "last_7d": {
            "total_opportunities": row_7d["total"],
            "advertised_usd": round(row_7d["total_usd"] or 0, 2),
            "completed": row_7d["completed"],
            "open": row_7d["open_count"],
            "completion_rate": round((row_7d["completed"] or 0) / max(1, row_7d["total"]), 4),
            "active_sources": row_7d["sources"],
        },
        "all_time": {
            "total_opportunities": all_time["total"],
            "advertised_usd": round(all_time["total_usd"] or 0, 2),
            "completed": all_time["completed"],
        },
        "hot_skills": [{"skill": s, "count": c} for s, c in top_skills_sorted],
    }


@router.get("/search-jobs")
def search_jobs(q: str = "", min_reward: float = 0, category: str = "",
                source: str = "", status: str = "open", limit: int = 20):
    """Free-text search across all opportunities.

    Agents use this to find specific work matching their capabilities.
    """
    from .store import get_db

    conn = get_db()
    query = "SELECT * FROM opportunities WHERE 1=1"
    params = []

    if q:
        # Simple text search across title, description, skills
        for word in q.lower().split():
            query += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ? OR skills LIKE ?)"
            params.extend([f"%{word}%", f"%{word}%", f"%{word}%"])

    if min_reward > 0:
        query += " AND reward_usd >= ?"
        params.append(min_reward)
    if category:
        query += " AND category = ?"
        params.append(category)
    if source:
        query += " AND source = ?"
        params.append(source)
    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY reward_usd DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        d["skills"] = json.loads(d.get("skills") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        results.append(d)

    return {"query": q, "results": results, "count": len(results)}


@router.post("/ingest/run")
def trigger_ingest(source: str = ""):
    """Trigger a manual ingestion cycle.

    Use this to force-poll all sources or a specific one.
    """
    from .cron_ingest import build_registry, run_once

    registry = build_registry()
    if source:
        adapter = registry.get(source)
        if not adapter:
            raise HTTPException(404, f"Unknown source: {source}")
        # Run single source
        from oracle.ingest import ingest_source
        result = asyncio.run(ingest_source(registry, source))
    else:
        result = run_once(registry)

    return result


# Need asyncio for trigger_ingest
import asyncio


# === Extended Data Endpoints ===
# These expose the richer data from comprehensive adapters.

@router.get("/agents")
def list_all_agents(source: str = "", tier: str = "", limit: int = 50):
    """All agent profiles across all platforms.
    
    Returns agent identity, reputation, earnings, capabilities per platform.
    """
    conn = get_db()
    query = "SELECT * FROM agent_profiles WHERE 1=1"
    params = []
    if source:
        query += " AND source=?"; params.append(source)
    if tier:
        query += " AND tier=?"; params.append(tier)
    query += " ORDER BY total_earned_usd DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    agents = []
    for r in rows:
        d = dict(r)
        d["capabilities"] = json.loads(d.get("capabilities") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        agents.append(d)

    return {"agents": agents, "count": len(agents)}


@router.get("/agents/{agent_id}")
def get_agent_detail(agent_id: str):
    """Full agent profile with cross-platform data."""
    conn = get_db()
    row = conn.execute("SELECT * FROM agent_profiles WHERE id=?", (agent_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Agent not found")

    result = dict(row)
    result["capabilities"] = json.loads(result.get("capabilities") or "[]")
    result["extra"] = json.loads(result.get("extra") or "{}")

    # Get observations for this agent
    obs = conn.execute(
        "SELECT * FROM observations WHERE opportunity_id LIKE ? ORDER BY observed_at DESC LIMIT 50",
        (f"%{agent_id}%",)
    ).fetchall()
    result["recent_observations"] = [dict(o) for o in obs]
    conn.close()

    return result


@router.get("/subnets")
def list_subnets(netuid: int = 0, status: str = "", limit: int = 100):
    """Bittensor subnet data — emissions, miners, validators, economics."""
    conn = get_db()
    query = "SELECT * FROM subnet_data WHERE 1=1"
    params = []
    if netuid:
        query += " AND netuid=?"; params.append(netuid)
    if status:
        query += " AND status=?"; params.append(status)
    query += " ORDER BY emission_pct DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    subnets = []
    for r in rows:
        d = dict(r)
        d["extra"] = json.loads(d.get("extra") or "{}")
        subnets.append(d)

    return {"subnets": subnets, "count": len(subnets)}


@router.get("/subnets/{netuid}")
def get_subnet_detail(netuid: int):
    """Detailed subnet data with observation history."""
    conn = get_db()
    row = conn.execute("SELECT * FROM subnet_data WHERE netuid=?", (netuid,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Subnet not found")

    result = dict(row)
    result["extra"] = json.loads(result.get("extra") or "{}")

    # Get platform stats for this subnet
    stats = conn.execute(
        "SELECT * FROM platform_stats WHERE stat_name LIKE ? ORDER BY observed_at DESC LIMIT 20",
        (f"%sn{netuid}%",)
    ).fetchall()
    result["stats_history"] = [dict(s) for s in stats]
    conn.close()

    return result


@router.get("/services")
def list_services(source: str = "", category: str = "", min_price: float = 0,
                  max_price: float = 999999, limit: int = 50):
    """All service/API listings across x402 platforms."""
    conn = get_db()
    query = "SELECT * FROM service_listings WHERE 1=1"
    params = []
    if source:
        query += " AND source=?"; params.append(source)
    if category:
        query += " AND category=?"; params.append(category)
    if min_price > 0:
        query += " AND price_usdc>=?"; params.append(min_price)
    if max_price < 999999:
        query += " AND price_usdc<=?"; params.append(max_price)
    query += " ORDER BY total_calls DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    services = []
    for r in rows:
        d = dict(r)
        d["capabilities"] = json.loads(d.get("capabilities") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        services.append(d)

    return {"services": services, "count": len(services)}


@router.get("/services/{service_id}")
def get_service_detail(service_id: str):
    """Full service listing with provider reputation."""
    conn = get_db()
    row = conn.execute("SELECT * FROM service_listings WHERE id=?", (service_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Service not found")

    result = dict(row)
    result["capabilities"] = json.loads(result.get("capabilities") or "[]")
    result["extra"] = json.loads(result.get("extra") or "{}")
    conn.close()

    return result


@router.get("/stats/platform")
def platform_stats_detail(source: str = "", stat_name: str = "", limit: int = 100):
    """Per-platform health metrics — time-series data."""
    conn = get_db()
    query = "SELECT * FROM platform_stats WHERE 1=1"
    params = []
    if source:
        query += " AND source=?"; params.append(source)
    if stat_name:
        query += " AND stat_name LIKE ?"; params.append(f"%{stat_name}%")
    query += " ORDER BY observed_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    stats = []
    for r in rows:
        d = dict(r)
        d["extra"] = json.loads(d.get("extra") or "{}")
        stats.append(d)

    return {"stats": stats, "count": len(stats)}


@router.get("/crypto/prices")
def crypto_prices():
    """Live crypto prices from x402engine."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM platform_stats WHERE source='x402engine' AND stat_name LIKE 'crypto_prices:%' ORDER BY observed_at DESC LIMIT 20"
    ).fetchall()
    conn.close()

    prices = {}
    for r in rows:
        name = r["stat_name"].replace("crypto_prices:", "")
        try:
            prices[name] = float(r["stat_value"])
        except ValueError:
            prices[name] = r["stat_value"]

    return {"prices": prices, "source": "x402engine"}


@router.get("/llm-pricing")
def llm_pricing():
    """LLM model pricing across providers from agent402/x402engine."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM platform_stats WHERE (source='agent402' AND stat_name LIKE 'pricing:%') OR (source='x402engine' AND stat_name LIKE '%llm%') ORDER BY observed_at DESC LIMIT 50"
    ).fetchall()
    conn.close()

    pricing = {}
    for r in rows:
        pricing[r["stat_name"]] = r["stat_value"]

    return {"pricing": pricing, "sources": ["agent402", "x402engine"]}


@router.get("/x402")
def x402_services(category: str = "", max_price: float = 0.10, limit: int = 50):
    """All x402 pay-per-call services sorted by usage."""
    conn = get_db()
    query = """SELECT * FROM service_listings 
               WHERE source IN ('payapi', 'agent402', 'x402engine', 'the402')"""
    params = []

    if category:
        query += " AND category=?"; params.append(category)
    if max_price > 0:
        query += " AND price_per_call<=?"; params.append(max_price)

    query += " ORDER BY total_calls DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    services = []
    for r in rows:
        d = dict(r)
        d["capabilities"] = json.loads(d.get("capabilities") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        services.append(d)

    return {"services": services, "count": len(services)}


@router.get("/humans")
def list_humans(skill: str = "", city: str = "", limit: int = 50):
    """RentAHuman talent profiles — skills, rates, locations."""
    conn = get_db()
    query = "SELECT * FROM agent_profiles WHERE source='rentahuman'"
    params = []

    if skill:
        query += " AND capabilities LIKE ?"; params.append(f"%{skill}%")
    if city:
        query += " AND extra LIKE ?"; params.append(f'%"{city}"%')

    query += " ORDER BY total_earned_usd DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    humans = []
    for r in rows:
        d = dict(r)
        d["capabilities"] = json.loads(d.get("capabilities") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        humans.append(d)

    return {"humans": humans, "count": len(humans)}


@router.get("/leaderboards")
def leaderboards(source: str = "", limit: int = 20):
    """Top agents per platform by earnings."""
    conn = get_db()
    query = "SELECT * FROM agent_profiles WHERE total_earned_usd > 0"
    params = []
    if source:
        query += " AND source=?"; params.append(source)
    query += " ORDER BY total_earned_usd DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    leaders = []
    for r in rows:
        d = dict(r)
        d["capabilities"] = json.loads(d.get("capabilities") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        leaders.append(d)

    return {"leaders": leaders, "count": len(leaders)}


@router.get("/earnings")
def earnings_summary(source: str = "", window: str = "30d"):
    """Agent earnings summary across platforms."""
    conn = get_db()

    # Total earnings per source
    rows = conn.execute("""
        SELECT source, COUNT(*) as agent_count,
               SUM(total_earned_usd) as total_earned,
               AVG(total_earned_usd) as avg_earned,
               MAX(total_earned_usd) as top_earned
        FROM agent_profiles
        WHERE total_earned_usd > 0
        GROUP BY source
        ORDER BY total_earned DESC
    """).fetchall()
    conn.close()

    sources = []
    for r in rows:
        sources.append({
            "source": r["source"],
            "agent_count": r["agent_count"],
            "total_earned_usd": round(r["total_earned"] or 0, 2),
            "avg_earned_usd": round(r["avg_earned"] or 0, 2),
            "top_earned_usd": round(r["top_earned"] or 0, 2),
        })

    total = sum(s["total_earned_usd"] for s in sources)
    return {"sources": sources, "total_earned_usd": round(total, 2)}


@router.get("/data-summary")
def data_summary():
    """Summary of all data collected across all sources."""
    conn = get_db()

    opps = conn.execute("SELECT COUNT(*) as c FROM opportunities").fetchone()["c"]
    agents = conn.execute("SELECT COUNT(*) as c FROM agent_profiles").fetchone()["c"]
    services = conn.execute("SELECT COUNT(*) as c FROM service_listings").fetchone()["c"]
    subnets = conn.execute("SELECT COUNT(*) as c FROM subnet_data").fetchone()["c"]
    observations = conn.execute("SELECT COUNT(*) as c FROM observations").fetchone()["c"]
    events = conn.execute("SELECT COUNT(*) as c FROM events").fetchone()["c"]
    stats = conn.execute("SELECT COUNT(*) as c FROM platform_stats").fetchone()["c"]
    payments = conn.execute("SELECT COUNT(*) as c FROM payments").fetchone()["c"]
    raw = conn.execute("SELECT COUNT(*) as c FROM raw_events").fetchone()["c"]

    # Per-source breakdown
    sources = conn.execute("""
        SELECT source, COUNT(*) as c FROM events GROUP BY source ORDER BY c DESC
    """).fetchall()

    # Total advertised value
    total_usd = conn.execute("SELECT SUM(reward_usd) FROM opportunities WHERE reward_usd > 0").fetchone()[0]

    conn.close()

    return {
        "totals": {
            "opportunities": opps,
            "agent_profiles": agents,
            "service_listings": services,
            "subnets": subnets,
            "observations": observations,
            "events": events,
            "platform_stats": stats,
            "payments": payments,
            "raw_events": raw,
        },
        "total_advertised_usd": round(total_usd or 0, 2),
        "by_source": {r["source"]: r["c"] for r in sources},
    }


# === Bounties Endpoint ===

@router.get("/bounties")
def list_bounties(
    source: str = "",
    category: str = "",
    min_reward: float = 0,
    max_reward: float = 999999,
    status: str = "",
    skill: str = "",
    limit: int = 50,
    sort: str = "reward",
):
    """Query bounties with reward filters, source, status, skills."""
    conn = get_db()
    query = "SELECT * FROM opportunities WHERE reward_usd > 0"
    params = []

    if source:
        query += " AND source=?"; params.append(source)
    if category:
        query += " AND category=?"; params.append(category)
    if status:
        query += " AND status=?"; params.append(status)
    if min_reward > 0:
        query += " AND reward_usd>=?"; params.append(min_reward)
    if max_reward < 999999:
        query += " AND reward_usd<=?"; params.append(max_reward)
    if skill:
        query += " AND skills LIKE ?"; params.append(f"%{skill}%")

    if sort == "reward":
        query += " ORDER BY reward_usd DESC"
    elif sort == "recent":
        query += " ORDER BY posted_at DESC"

    query += " LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    bounties = []
    for r in rows:
        d = dict(r)
        d["skills"] = json.loads(d.get("skills") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        bounties.append(d)

    return {"bounties": bounties, "count": len(bounties)}


# === Services Endpoint (x402 API marketplace) ===

@router.get("/services")
def list_services(
    source: str = "",
    category: str = "",
    min_price: float = 0,
    max_price: float = 999999,
    limit: int = 50,
    sort: str = "calls",
):
    """Query x402 service listings with pricing."""
    conn = get_db()
    query = "SELECT * FROM service_listings WHERE 1=1"
    params = []

    if source:
        query += " AND source=?"; params.append(source)
    if category:
        query += " AND category=?"; params.append(category)
    if min_price > 0:
        query += " AND price_per_call>=?"; params.append(min_price)
    if max_price < 999999:
        query += " AND price_per_call<=?"; params.append(max_price)

    if sort == "calls":
        query += " ORDER BY total_calls DESC"
    elif sort == "price":
        query += " ORDER BY price_per_call ASC"

    query += " LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    services = []
    for r in rows:
        d = dict(r)
        d["capabilities"] = json.loads(d.get("capabilities") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        services.append(d)

    return {"services": services, "count": len(services)}


# === Completions Endpoint ===

@router.get("/completions")
def list_completions(source: str = "", limit: int = 50):
    """Track completed jobs across sources."""
    conn = get_db()
    query = "SELECT * FROM opportunities WHERE status IN ('completed', 'paid')"
    params = []

    if source:
        query += " AND source=?"; params.append(source)

    query += " ORDER BY completed_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    completions = []
    for r in rows:
        d = dict(r)
        d["skills"] = json.loads(d.get("skills") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        completions.append(d)

    return {"completions": completions, "count": len(completions)}


# === Skill Demand with Supply Analysis ===

@router.get("/skills/demand-supply")
def skill_demand_supply(window: str = "30d"):
    """Which skills have unmet demand vs supply."""
    conn = get_db()

    days = int(window.rstrip("d")) if window.endswith("d") else 30
    import time as _time
    since = _time.strftime("%Y-%m-%dT%H:%M:%SZ",
                           _time.gmtime(_time.time() - days * 86400))

    # Get all opportunities in window
    rows = conn.execute(
        "SELECT skills, reward_usd, status FROM opportunities WHERE first_seen_at>=?",
        (since,)
    ).fetchall()
    conn.close()

    # Aggregate by skill
    skill_stats = {}
    for r in rows:
        for s in json.loads(r["skills"] or "[]"):
            if s not in skill_stats:
                skill_stats[s] = {"total": 0, "open": 0, "completed": 0, "total_usd": 0}
            skill_stats[s]["total"] += 1
            if r["status"] == "open":
                skill_stats[s]["open"] += 1
            elif r["status"] in ("completed", "paid"):
                skill_stats[s]["completed"] += 1
            skill_stats[s]["total_usd"] += r["reward_usd"] or 0

    # Compute gap scores
    gaps = []
    for skill, stats in skill_stats.items():
        completion_rate = stats["completed"] / max(1, stats["total"])
        gap_score = stats["open"] / max(1, stats["completed"])
        gaps.append({
            "skill": skill,
            "total": stats["total"],
            "open": stats["open"],
            "completed": stats["completed"],
            "total_usd": round(stats["total_usd"], 2),
            "completion_rate": round(completion_rate, 4),
            "gap_score": round(gap_score, 2),
        })

    gaps.sort(key=lambda x: x["gap_score"], reverse=True)
    return {"window": window, "skills": gaps}


# === Layered Data Architecture ===

@router.get("/tool-demand")
def tool_demand(source: str = "", category: str = "", limit: int = 50):
    """Tool demand layer — what APIs/tools agents are paying for.
    
    Sources: Apify (usage data), x402engine, x402list, PayAPI, the402
    Shows: runs, users, pricing, category popularity
    """
    conn = get_db()

    # Get tool/service listings from x402 sources
    tool_sources = ("apify", "x402engine", "x402list", "payapi", "the402", "402index")
    query = f"SELECT * FROM service_listings WHERE source IN ({','.join('?'*len(tool_sources))})"
    params = list(tool_sources)

    if source:
        query += " AND source=?"; params.append(source)
    if category:
        query += " AND category=?"; params.append(category)

    query += " ORDER BY total_calls DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    services = []
    for r in rows:
        d = dict(r)
        d["capabilities"] = json.loads(d.get("capabilities") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        services.append(d)

    # Aggregate by source
    by_source = {}
    for s in services:
        src = s["source"]
        if src not in by_source:
            by_source[src] = {"count": 0, "total_calls": 0, "avg_price": 0, "prices": []}
        by_source[src]["count"] += 1
        by_source[src]["total_calls"] += s.get("total_calls", 0)
        if s.get("price_per_call", 0) > 0:
            by_source[src]["prices"].append(s["price_per_call"])

    for src, stats in by_source.items():
        if stats["prices"]:
            stats["avg_price"] = round(sum(stats["prices"]) / len(stats["prices"]), 6)
            stats["median_price"] = round(sorted(stats["prices"])[len(stats["prices"])//2], 6)
        del stats["prices"]

    return {
        "services": services,
        "count": len(services),
        "by_source": by_source,
        "total_tools": sum(s.get("total_calls", 0) for s in services),
    }


@router.get("/work-demand")
def work_demand(source: str = "", category: str = "", min_reward: float = 0, limit: int = 50):
    """Work demand layer — what jobs/bounties agents can do.
    
    Sources: SuperTeam, GitHub, BountyBook, AgentHansa, Daydreams, RentAHuman
    Shows: rewards, completion rates, platform comparison
    """
    conn = get_db()

    # Get bounties/work from non-x402 sources
    work_sources = ("superteam", "github", "bountybook", "agenthansa", "daydreams", "rentahuman")
    query = f"SELECT * FROM opportunities WHERE source IN ({','.join('?'*len(work_sources))}) AND reward_usd > 0"
    params = list(work_sources)

    if source:
        query += " AND source=?"; params.append(source)
    if category:
        query += " AND category=?"; params.append(category)
    if min_reward > 0:
        query += " AND reward_usd>=?"; params.append(min_reward)

    query += " ORDER BY reward_usd DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    bounties = []
    for r in rows:
        d = dict(r)
        d["skills"] = json.loads(d.get("skills") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        bounties.append(d)

    # Aggregate by source
    by_source = {}
    for b in bounties:
        src = b["source"]
        if src not in by_source:
            by_source[src] = {"count": 0, "total_usd": 0, "rewards": []}
        by_source[src]["count"] += 1
        by_source[src]["total_usd"] += b.get("reward_usd", 0)
        by_source[src]["rewards"].append(b.get("reward_usd", 0))

    for src, stats in by_source.items():
        if stats["rewards"]:
            stats["median_reward"] = round(sorted(stats["rewards"])[len(stats["rewards"])//2], 2)
            stats["avg_reward"] = round(sum(stats["rewards"]) / len(stats["rewards"]), 2)
        stats["total_usd"] = round(stats["total_usd"], 2)
        del stats["rewards"]

    return {
        "bounties": bounties,
        "count": len(bounties),
        "by_source": by_source,
        "total_usd": round(sum(b.get("reward_usd", 0) for b in bounties), 2),
    }


@router.get("/skill-demand")
def skill_demand(window: str = "30d", limit: int = 30):
    """Skill demand layer — cross-cutting analysis across tools and work.
    
    Combines: tool categories + work skills + pricing + competition
    """
    conn = get_db()

    days = int(window.rstrip("d")) if window.endswith("d") else 30
    import time as _time
    since = _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime(_time.time() - days * 86400))

    # Work demand by skill
    work_rows = conn.execute(
        "SELECT skills, reward_usd, source, status FROM opportunities WHERE first_seen_at>=? AND reward_usd>0",
        (since,)
    ).fetchall()

    # Tool demand by category
    tool_rows = conn.execute(
        "SELECT category, source, total_calls, price_per_call FROM service_listings WHERE total_calls>0"
    ).fetchall()

    conn.close()

    # Aggregate work skills
    skill_stats = {}
    for r in work_rows:
        for s in json.loads(r["skills"] or "[]"):
            if s not in skill_stats:
                skill_stats[s] = {"work_count": 0, "work_usd": 0, "work_sources": set(), "tool_count": 0, "tool_usd": 0}
            skill_stats[s]["work_count"] += 1
            skill_stats[s]["work_usd"] += r["reward_usd"] or 0
            skill_stats[s]["work_sources"].add(r["source"])

    # Aggregate tool categories
    for r in tool_rows:
        cat = r["category"]
        if cat not in skill_stats:
            skill_stats[cat] = {"work_count": 0, "work_usd": 0, "work_sources": set(), "tool_count": 0, "tool_usd": 0}
        skill_stats[cat]["tool_count"] += 1
        skill_stats[cat]["tool_usd"] += r["total_calls"] or 0

    # Build results
    results = []
    for skill, stats in skill_stats.items():
        work_count = stats["work_count"]
        tool_count = stats["tool_count"]
        results.append({
            "skill": skill,
            "work_opportunities": work_count,
            "work_total_usd": round(stats["work_usd"], 2),
            "work_sources": list(stats["work_sources"]),
            "tool_services": tool_count,
            "tool_total_calls": tool_count,
            "cross_layer_score": min(work_count, tool_count) + (work_count * tool_count / 100),
        })

    results.sort(key=lambda x: x["cross_layer_score"], reverse=True)
    return {"window": window, "skills": results[:limit]}


@router.get("/economics")
def economics():
    """What can agents actually earn? Summary economics across all layers."""
    conn = get_db()

    # Work layer
    work = conn.execute("""
        SELECT source, COUNT(*) as c, SUM(reward_usd) as usd,
               AVG(reward_usd) as avg_reward
        FROM opportunities WHERE reward_usd > 0
        GROUP BY source ORDER BY usd DESC
    """).fetchall()

    # Tool layer
    tools = conn.execute("""
        SELECT source, COUNT(*) as c, SUM(total_calls) as calls
        FROM service_listings WHERE total_calls > 0
        GROUP BY source ORDER BY calls DESC
    """).fetchall()

    # Total
    total_work_usd = conn.execute("SELECT SUM(reward_usd) FROM opportunities WHERE reward_usd > 0").fetchone()[0] or 0
    total_tools = conn.execute("SELECT SUM(total_calls) FROM service_listings").fetchone()[0] or 0
    total_opps = conn.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
    total_services = conn.execute("SELECT COUNT(*) FROM service_listings").fetchone()[0]

    conn.close()

    return {
        "work_layer": {
            "total_bounties": sum(r["c"] for r in work),
            "total_usd": round(total_work_usd, 2),
            "by_source": [{"source": r["source"], "count": r["c"], "usd": round(r["usd"] or 0, 2), "avg_reward": round(r["avg_reward"] or 0, 2)} for r in work],
        },
        "tool_layer": {
            "total_services": sum(r["c"] for r in tools),
            "total_calls": round(total_tools),
            "by_source": [{"source": r["source"], "count": r["c"], "calls": round(r["calls"] or 0)} for r in tools],
        },
        "summary": {
            "total_opportunities": total_opps,
            "total_services": total_services,
            "total_work_usd": round(total_work_usd, 2),
            "total_tool_calls": round(total_tools),
        },
    }


# === Incentive Markets (Bittensor, Allora, FLock) ===

@router.get("/incentives")
def list_incentives(netuid: int = 0, status: str = "", limit: int = 50):
    """Bittensor subnets and other incentive markets."""
    conn = get_db()
    query = "SELECT * FROM subnet_data WHERE 1=1"
    params = []
    if netuid:
        query += " AND netuid=?"; params.append(netuid)
    if status:
        query += " AND status=?"; params.append(status)
    query += " ORDER BY emission_pct DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    subnets = []
    for r in rows:
        d = dict(r)
        d["extra"] = json.loads(d.get("extra") or "{}")
        subnets.append(d)

    return {"subnets": subnets, "count": len(subnets)}


@router.get("/incentives/{netuid}")
def get_incentive_detail(netuid: int):
    """Detailed Bittensor subnet data."""
    conn = get_db()
    row = conn.execute("SELECT * FROM subnet_data WHERE netuid=?", (netuid,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Subnet not found")

    result = dict(row)
    result["extra"] = json.loads(result.get("extra") or "{}")
    conn.close()
    return result


@router.get("/demand/cross-layer")
def demand_cross_layer(window: str = "30d"):
    """Cross-layer demand analysis — work + service + signal combined."""
    conn = get_db()

    days = int(window.rstrip("d")) if window.endswith("d") else 30
    import time as _time
    since = _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime(_time.time() - days * 86400))

    # Work demand by skill
    work_rows = conn.execute(
        "SELECT skills, reward_usd, source FROM opportunities WHERE first_seen_at>=? AND reward_usd>0",
        (since,)
    ).fetchall()

    # Service supply by category
    service_rows = conn.execute(
        "SELECT category, source, total_calls FROM service_listings WHERE total_calls>0"
    ).fetchall()

    conn.close()

    # Aggregate work skills
    skill_work = {}
    for r in work_rows:
        for s in json.loads(r["skills"] or "[]"):
            if s not in skill_work:
                skill_work[s] = {"count": 0, "usd": 0, "sources": set()}
            skill_work[s]["count"] += 1
            skill_work[s]["usd"] += r["reward_usd"] or 0
            skill_work[s]["sources"].add(r["source"])

    # Aggregate service categories
    skill_supply = {}
    for r in service_rows:
        cat = r["category"]
        if cat not in skill_supply:
            skill_supply[cat] = {"count": 0, "calls": 0}
        skill_supply[cat]["count"] += 1
        skill_supply[cat]["calls"] += r["total_calls"] or 0

    # Cross-layer analysis
    all_skills = set(list(skill_work.keys()) + list(skill_supply.keys()))
    results = []
    for skill in all_skills:
        work = skill_work.get(skill, {"count": 0, "usd": 0, "sources": set()})
        supply = skill_supply.get(skill, {"count": 0, "calls": 0})
        results.append({
            "skill": skill,
            "work_opportunities": work["count"],
            "work_usd": round(work["usd"], 2),
            "work_sources": list(work["sources"]),
            "service_count": supply["count"],
            "service_calls": supply["calls"],
            "cross_layer_score": work["count"] + supply["count"],
        })

    results.sort(key=lambda x: x["cross_layer_score"], reverse=True)
    return {"window": window, "skills": results}


@router.get("/supply")
def list_supply(category: str = "", source: str = "", limit: int = 50):
    """All service/tool supply — what capabilities exist."""
    conn = get_db()
    query = "SELECT * FROM service_listings WHERE 1=1"
    params = []
    if source:
        query += " AND source=?"; params.append(source)
    if category:
        query += " AND category=?"; params.append(category)
    query += " ORDER BY total_calls DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    services = []
    for r in rows:
        d = dict(r)
        d["capabilities"] = json.loads(d.get("capabilities") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        services.append(d)

    return {"services": services, "count": len(services)}


@router.get("/opportunities")
def list_opportunities(source: str = "", status: str = "", category: str = "",
                      skills: str = "", min_reward: float = 0, limit: int = 50):
    """All opportunities — work, service, signal combined."""
    conn = get_db()
    query = "SELECT * FROM opportunities WHERE 1=1"
    params = []
    if source:
        query += " AND source=?"; params.append(source)
    if status:
        query += " AND status=?"; params.append(status)
    if category:
        query += " AND category=?"; params.append(category)
    if skills:
        for s in skills.split(","):
            query += " AND skills LIKE ?"; params.append(f"%{s.strip()}%")
    if min_reward > 0:
        query += " AND reward_usd>=?"; params.append(min_reward)
    query += " ORDER BY reward_usd DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    opps = []
    for r in rows:
        d = dict(r)
        d["skills"] = json.loads(d.get("skills") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        opps.append(d)

    return {"opportunities": opps, "count": len(opps)}


# === Platform Comparison ===

@router.get("/platform-comparison")
def platform_comparison(window: str = "30d"):
    """Which platform pays best for which skills?"""
    conn = get_db()
    days = int(window.rstrip("d")) if window.endswith("d") else 30
    import time as _time
    since = _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime(_time.time() - days * 86400))

    rows = conn.execute(
        "SELECT source, reward_usd, status, category FROM opportunities WHERE first_seen_at>=? AND reward_usd>0",
        (since,)
    ).fetchall()
    conn.close()

    sources = {}
    for r in rows:
        src = r["source"]
        if src not in sources:
            sources[src] = {"count": 0, "total_usd": 0, "rewards": [], "categories": {}}
        sources[src]["count"] += 1
        sources[src]["total_usd"] += r["reward_usd"] or 0
        sources[src]["rewards"].append(r["reward_usd"] or 0)
        cat = r["category"] or "general"
        sources[src]["categories"][cat] = sources[src]["categories"].get(cat, 0) + 1

    results = []
    for src, s in sources.items():
        rewards = s["rewards"]
        results.append({
            "source": src,
            "total_opportunities": s["count"],
            "total_usd": round(s["total_usd"], 2),
            "median_reward": round(sorted(rewards)[len(rewards)//2], 2) if rewards else 0,
            "avg_reward": round(sum(rewards)/len(rewards), 2) if rewards else 0,
            "top_category": max(s["categories"].items(), key=lambda x: x[1])[0] if s["categories"] else "",
        })

    results.sort(key=lambda x: x["median_reward"], reverse=True)
    return {"window": window, "platforms": results}


# === Timeseries ===

@router.get("/timeseries")
def timeseries(metric: str = "opportunities", window: str = "30d"):
    """Time-bucketed metrics."""
    conn = get_db()
    days = int(window.rstrip("d")) if window.endswith("d") else 30
    import time as _time
    since = _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime(_time.time() - days * 86400))

    rows = conn.execute("""
        SELECT DATE(first_seen_at) as day, COUNT(*) as count,
               SUM(reward_usd) as total_usd
        FROM opportunities WHERE first_seen_at>=?
        GROUP BY day ORDER BY day
    """, (since,)).fetchall()
    conn.close()

    return {
        "metric": metric,
        "data": [{"date": r["day"], "count": r["count"], "usd": round(r["total_usd"] or 0, 2)} for r in rows],
    }


# === Agent Briefing ===

@router.get("/agent-briefing")
def agent_briefing(skills: str = "", min_reward: float = 0, window: str = "30d"):
    """Full intelligence briefing for an agent with these skills."""
    conn = get_db()
    days = int(window.rstrip("d")) if window.endswith("d") else 30
    import time as _time
    since = _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime(_time.time() - days * 86400))

    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    query = "SELECT * FROM opportunities WHERE first_seen_at>=?"
    params = [since]

    if skill_list:
        for s in skill_list:
            query += " AND skills LIKE ?"; params.append(f"%{s}%")
    if min_reward > 0:
        query += " AND reward_usd>=?"; params.append(min_reward)

    query += " ORDER BY reward_usd DESC LIMIT 50"
    rows = conn.execute(query, params).fetchall()
    conn.close()

    opps = []
    for r in rows:
        d = dict(r)
        d["skills"] = json.loads(d.get("skills") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        opps.append(d)

    total_usd = sum(o.get("reward_usd", 0) for o in opps)
    rewards = sorted([o.get("reward_usd", 0) for o in opps if o.get("reward_usd", 0) > 0])

    return {
        "skills": skill_list,
        "window": window,
        "summary": {
            "total": len(opps),
            "total_usd": round(total_usd, 2),
            "median_reward": round(rewards[len(rewards)//2], 2) if rewards else 0,
            "p75_reward": round(rewards[int(len(rewards)*0.75)], 2) if rewards else 0,
        },
        "top_opportunities": opps[:10],
    }


# === Market Pulse ===

@router.get("/market-pulse")
def market_pulse():
    """Live market stats — what's happening right now."""
    conn = get_db()
    import time as _time

    opps = conn.execute("SELECT COUNT(*) as c FROM opportunities").fetchone()["c"]
    services = conn.execute("SELECT COUNT(*) as c FROM service_listings").fetchone()["c"]
    subnets = conn.execute("SELECT COUNT(*) as c FROM subnet_data").fetchone()["c"]
    total_usd = conn.execute("SELECT SUM(reward_usd) FROM opportunities WHERE reward_usd>0").fetchone()[0] or 0
    total_calls = conn.execute("SELECT SUM(total_calls) FROM service_listings").fetchone()[0] or 0

    by_source = conn.execute(
        "SELECT source, COUNT(*) as c FROM opportunities GROUP BY source ORDER BY c DESC"
    ).fetchall()

    conn.close()

    return {
        "opportunities": opps,
        "services": services,
        "subnets": subnets,
        "total_usd": round(total_usd, 2),
        "total_tool_calls": round(total_calls),
        "by_source": {r["source"]: r["c"] for r in by_source},
    }


# === Leaderboards ===

@router.get("/leaderboards")
def leaderboards(source: str = "", limit: int = 20):
    """Top agents per platform by earnings."""
    conn = get_db()
    query = "SELECT * FROM agent_profiles WHERE total_earned_usd > 0"
    params = []
    if source:
        query += " AND source=?"; params.append(source)
    query += " ORDER BY total_earned_usd DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    leaders = []
    for r in rows:
        d = dict(r)
        d["capabilities"] = json.loads(d.get("capabilities") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        leaders.append(d)

    return {"leaders": leaders, "count": len(leaders)}
