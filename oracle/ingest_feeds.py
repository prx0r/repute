"""Three-feed ingestion — collects Work + Service data.

Run: python3 oracle/ingest_feeds.py
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from oracle.feeds import WorkFeed, ServiceFeed, MarketFeed
from oracle.store import get_db


def _record_observation(conn, entity_id: str, source: str, metric: str, previous, current):
    """Record a single observation."""
    conn.execute("""
        INSERT INTO observations
        (opportunity_id, source, metric, previous_value, current_value, change_value,
         observed_at, interval_after, interval_before, adapter_version, raw_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entity_id, source, metric,
        json.dumps(previous) if previous is not None else None,
        json.dumps(current) if current is not None else None,
        None,
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "0.1.0",
        "",
    ))


def store_work(items: list[dict]) -> int:
    """Store work opportunities in the opportunities table."""
    conn = get_db()
    count = 0
    for item in items:
        try:
            item_id = item.get("id", "")
            if not item_id:
                continue

            # Check if we've seen this before
            existing = conn.execute("SELECT * FROM opportunities WHERE id=?", (item_id,)).fetchone()
            conn.execute("""
                INSERT OR REPLACE INTO opportunities
                (id, source, source_id, title, description, url, type, category,
                 skills, reward_advertised, reward_currency, reward_usd,
                 buyer_id, status, posted_at, first_seen_at, last_seen_at, extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["id"], item["source"], item["source_id"],
                item["title"], item["description"], item["url"],
                "work", item.get("category", ""),
                json.dumps(item.get("skills", [])),
                item.get("reward_usd", 0), item.get("currency", "USD"),
                item.get("reward_usd", 0),
                item.get("buyer_id", ""),
                "open" if not item.get("closed_at") else "closed",
                item.get("posted_at", ""),
                item.get("last_seen_at", time.strftime("%Y-%m-%dT%H:%M:%SZ")),
                item.get("last_seen_at", time.strftime("%Y-%m-%dT%H:%M:%SZ")),
                json.dumps({
                    "fee_pct": item.get("fee_pct", 0),
                    "escrowed": item.get("escrowed", False),
                    "entries": item.get("entries", 0),
                    "views": item.get("views", 0),
                    "slots": item.get("slots", 1),
                    "agent_allowed": item.get("agent_allowed", False),
                    "submission_method": item.get("submission_method", ""),
                    "auth_type": item.get("auth_type", ""),
                    "network": item.get("network", ""),
                    "buyer_reputation": item.get("buyer_reputation"),
                    "buyer_historical_spend_usd": item.get("buyer_historical_spend_usd"),
                }),
            ))

            # Record observation for state tracking
            if existing:
                old_status = existing["status"]
                new_status = "closed" if item.get("closed_at") else "open"
                if old_status != new_status:
                    _record_observation(conn, item_id, item["source"], "status", old_status, new_status)
                old_entries = json.loads(existing["extra"] or "{}").get("entries", 0)
                new_entries = item.get("entries", 0)
                if old_entries != new_entries:
                    _record_observation(conn, item_id, item["source"], "entries", old_entries, new_entries)
            else:
                _record_observation(conn, item_id, item["source"], "status", None, "open")
                _record_observation(conn, item_id, item["source"], "entries", None, item.get("entries", 0))
                _record_observation(conn, item_id, item["source"], "reward_usd", None, item.get("reward_usd", 0))

            count += 1
        except Exception as e:
            pass
    conn.commit()
    conn.close()
    return count


def store_services(items: list[dict]) -> int:
    """Store services in the service_listings table."""
    conn = get_db()
    count = 0
    for item in items:
        try:
            conn.execute("""
                INSERT OR REPLACE INTO service_listings
                (id, source, source_service_id, title, description, url, category,
                 price_usdc, price_per_call, provider_id, provider_reputation,
                 total_calls, status, capabilities, first_seen_at, last_seen_at, extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["id"], item["source"], item["source_id"],
                item.get("name", ""), item.get("description", ""), item.get("url", ""),
                item.get("category", ""),
                item.get("price_per_call", 0), item.get("price_per_call", 0),
                item.get("provider_id", ""), item.get("provider_reputation", 0),
                item.get("total_runs", 0), "active",
                json.dumps(item.get("capabilities", [])),
                item.get("last_used_at", time.strftime("%Y-%m-%dT%H:%M:%SZ")),
                time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                json.dumps({
                    "rating": item.get("rating", 0),
                    "reviews": item.get("reviews", 0),
                    "verified": item.get("verified", False),
                    "total_users": item.get("total_users", 0),
                    "users_30d": item.get("users_30d", 0),
                    "users_7d": item.get("users_7d", 0),
                    "pricing_model": item.get("pricing_model", ""),
                    "provider_network": item.get("provider_network", ""),
                }),
            ))
            count += 1
        except Exception as e:
            pass
    conn.commit()
    conn.close()
    return count


def store_signals(items: list[dict]) -> int:
    """Store market signals in the service_listings table (as capability supply signals)."""
    conn = get_db()
    count = 0
    for item in items:
        try:
            conn.execute("""
                INSERT OR REPLACE INTO service_listings
                (id, source, source_service_id, title, description, url, category,
                 price_usdc, price_per_call, provider_id, provider_reputation,
                 total_calls, status, capabilities, first_seen_at, last_seen_at, extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["id"], item["source"], item["source_id"],
                item.get("name", ""), item.get("description", ""), item.get("url", ""),
                item.get("category", ""),
                0, 0,
                "", 0,
                item.get("use_count", item.get("downloads", item.get("downloads_week", 0))),
                "active",
                json.dumps(item.get("tags", [])),
                item.get("created_at", time.strftime("%Y-%m-%dT%H:%M:%SZ")),
                time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                json.dumps({
                    "use_count": item.get("use_count", 0),
                    "verified": item.get("verified", False),
                    "deployed": item.get("deployed", False),
                    "downloads": item.get("downloads", 0),
                    "downloads_week": item.get("downloads_week", 0),
                    "likes": item.get("likes", 0),
                    "metrics": item.get("metrics", {}),
                }),
            ))
            count += 1
        except Exception as e:
            pass
    conn.commit()
    conn.close()
    return count


def main():
    print("=== Three-Feed Ingestion ===")

    # Work Feed
    print("\n[WORK FEED]")
    work_feed = WorkFeed()
    work_items = asyncio.run(work_feed.collect())
    work_count = store_work(work_items)
    print(f"  {work_count} work items stored")

    # Service Feed
    print("\n[SERVICE FEED]")
    service_feed = ServiceFeed()
    service_items = asyncio.run(service_feed.collect())
    service_count = store_services(service_items)
    print(f"  {service_count} services stored")

    # Signal Feed
    print("\n[SIGNAL FEED]")
    signal_feed = MarketFeed()
    signal_items = asyncio.run(signal_feed.collect())
    signal_count = store_signals(signal_items)
    print(f"  {signal_count} signals stored")

    # Summary
    conn = get_db()
    opps = conn.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
    services = conn.execute("SELECT COUNT(*) FROM service_listings").fetchone()[0]
    work_usd = conn.execute("SELECT SUM(reward_usd) FROM opportunities WHERE reward_usd > 0").fetchone()[0] or 0
    conn.close()

    print(f"\n=== Summary ===")
    print(f"Work: {work_count} items, ${work_usd:,.0f} total")
    print(f"Services: {service_count} items")
    print(f"Signals: {signal_count} items")
    print(f"Total in DB: {opps} work + {services} services/signals")


if __name__ == "__main__":
    main()
