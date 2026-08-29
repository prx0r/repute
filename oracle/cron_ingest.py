#!/usr/bin/env python3
"""Continuous ingestion daemon — runs every 5 minutes.

Usage:
  python3 oracle/cron_ingest.py              # one-shot
  python3 oracle/cron_ingest.py --loop       # continuous
  python3 oracle/cron_ingest.py --interval 300  # custom interval
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


def _record_observation(conn, entity_id, source, metric, previous, current):
    conn.execute("""
        INSERT INTO observations
        (opportunity_id, source, metric, previous_value, current_value, change_value,
         observed_at, interval_after, interval_before, adapter_version, raw_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (entity_id, source, metric, json.dumps(previous), json.dumps(current), None,
          time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
          time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
          time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "0.1.0", ""))


def run_once():
    """Run one ingestion cycle."""
    print(f"[{time.strftime('%H:%M:%S')}] Starting ingestion...")

    # Work Feed
    work_feed = WorkFeed()
    work_items = asyncio.run(work_feed.collect())
    conn = get_db()
    count = 0
    for item in work_items:
        try:
            item_id = item.get("id", "")
            if not item_id: continue
            existing = conn.execute("SELECT * FROM opportunities WHERE id=?", (item_id,)).fetchone()
            conn.execute("""INSERT OR REPLACE INTO opportunities
                (id,source,source_id,title,description,url,type,category,skills,
                 reward_advertised,reward_currency,reward_usd,buyer_id,status,
                 posted_at,first_seen_at,last_seen_at,extra)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (item_id, item["source"], item["source_id"], item["title"],
                 item["description"], item["url"], "work", item.get("category",""),
                 json.dumps(item.get("skills",[])), item.get("reward_usd",0),
                 item.get("currency","USD"), item.get("reward_usd",0),
                 item.get("buyer_id",""), "closed" if item.get("closed_at") else "open",
                 item.get("posted_at",""), item.get("last_seen_at",time.strftime("%Y-%m-%dT%H:%M:%SZ")),
                 item.get("last_seen_at",time.strftime("%Y-%m-%dT%H:%M:%SZ")),
                 json.dumps({"entries":item.get("entries",0),"network":item.get("network","")})
            ))
            # Record observations
            if existing:
                if existing["status"] != ("closed" if item.get("closed_at") else "open"):
                    _record_observation(conn, item_id, item["source"], "status", existing["status"], "open")
            else:
                _record_observation(conn, item_id, item["source"], "status", None, "open")
                _record_observation(conn, item_id, item["source"], "reward_usd", None, item.get("reward_usd",0))
            count += 1
        except: pass
    conn.commit()
    conn.close()
    print(f"  Work: {count} items")

    # Service Feed
    service_feed = ServiceFeed()
    service_items = asyncio.run(service_feed.collect())
    conn = get_db()
    count = 0
    for item in service_items:
        try:
            sid = item.get("id","")
            if not sid: continue
            conn.execute("""INSERT OR REPLACE INTO service_listings
                (id,source,source_service_id,title,description,url,category,
                 price_usdc,price_per_call,provider_id,provider_reputation,
                 total_calls,status,capabilities,first_seen_at,last_seen_at,extra)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (sid, item["source"], item["source_id"], item.get("name",""),
                 item.get("description",""), item.get("url",""), item.get("category",""),
                 item.get("price_per_call",0), item.get("price_per_call",0),
                 item.get("provider_id",""), item.get("provider_reputation",0),
                 item.get("total_runs",item.get("total_calls",0)), "active",
                 json.dumps(item.get("capabilities",[])),
                 item.get("last_used_at",time.strftime("%Y-%m-%dT%H:%M:%SZ")),
                 time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                 json.dumps({"rating":item.get("rating",0),"reviews":item.get("reviews",0)})
            ))
            count += 1
        except: pass
    conn.commit()
    conn.close()
    print(f"  Services: {count} items")

    # Summary
    conn = get_db()
    opps = conn.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
    services = conn.execute("SELECT COUNT(*) FROM service_listings").fetchone()[0]
    obs = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    conn.close()
    print(f"  Total: {opps} work + {services} services + {obs} observations")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--interval", type=int, default=300)
    args = parser.parse_args()

    if args.loop:
        while True:
            run_once()
            time.sleep(args.interval)
    else:
        run_once()


if __name__ == "__main__":
    main()
