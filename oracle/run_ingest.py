#!/usr/bin/env python3
"""Quick-start ingestion script.

Run: python3 oracle/run_ingest.py

Or with GitHub token:
  GITHUB_TOKEN="ghp_..." python3 oracle/run_ingest.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from oracle.adapters import get_all_adapters
from oracle.ingest import ingest_opportunity
from oracle.store import get_db


def main():
    print("=== Moltwork Oracle — Ingestion ===")

    adapters = get_all_adapters()
    print(f"Found {len(adapters)} adapters")

    results = {}
    for aid, cls in sorted(adapters.items()):
        if aid == "mock":
            continue
        print(f"  {aid}...", end=" ", flush=True)
        try:
            a = cls()
            items = asyncio.run(a.discover())
            count = 0
            for item in items:
                raw = item.get("data", item) if isinstance(item, dict) else item
                try:
                    ingest_opportunity(aid, raw, a.normalize)
                    count += 1
                except Exception:
                    pass
            print(f"{count} items")
            results[aid] = count
        except Exception as e:
            print(f"ERROR: {e}")
            results[aid] = 0

    conn = get_db()
    rewarded = conn.execute("SELECT COUNT(*) FROM opportunities WHERE reward_usd > 0").fetchone()[0]
    total_usd = conn.execute("SELECT SUM(reward_usd) FROM opportunities WHERE reward_usd > 0").fetchone()[0] or 0
    top = conn.execute(
        "SELECT source, reward_usd, title FROM opportunities "
        "WHERE reward_usd > 0 ORDER BY reward_usd DESC LIMIT 5"
    ).fetchall()
    conn.close()

    total = sum(results.values())
    working = sum(1 for v in results.values() if v > 0)

    print(f"\n=== Summary ===")
    print(f"Total: {total} items from {working} adapters")
    print(f"With rewards: {rewarded} items, ${total_usd:,.2f}")
    if top:
        print("\nTop bounties:")
        for r in top:
            print(f"  ${r['reward_usd']:>8.0f} {r['source']:12s} {r['title'][:50]}")
    print("\nDone. Query API at http://localhost:8788/v1/")


if __name__ == "__main__":
    main()
