"""Oracle storage layer — raw JSONL + SQLite for normalized events."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
import zlib
from pathlib import Path
from typing import Any

from .schema import EventEnvelope, Confidence


DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "oracle" / "raw"
DB_PATH = DATA_DIR / "oracle" / "oracle.db"


def _ensure_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db() -> sqlite3.Connection:
    _ensure_dirs()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            schema_version TEXT NOT NULL,
            source TEXT NOT NULL,
            source_id TEXT NOT NULL,
            observed_at TEXT NOT NULL,
            effective_at TEXT NOT NULL,
            subject_type TEXT NOT NULL,
            subject_id TEXT NOT NULL,
            payload TEXT NOT NULL,
            provenance TEXT NOT NULL,
            raw_hash TEXT,
            content_hash TEXT NOT NULL,
            created_at REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS opportunities (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            source_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            url TEXT,
            type TEXT,
            category TEXT,
            subcategory TEXT,
            skills TEXT,
            reward_advertised REAL,
            reward_currency TEXT,
            reward_usd REAL,
            buyer_id TEXT,
            buyer_name TEXT,
            status TEXT,
            posted_at TEXT,
            claimed_at TEXT,
            submitted_at TEXT,
            completed_at TEXT,
            paid_at TEXT,
            actual_payment_usd REAL,
            worker_id TEXT,
            proposals_count INTEGER,
            views_count INTEGER,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            extra TEXT,
            schema_version TEXT
        );

        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            address TEXT,
            name TEXT,
            network TEXT,
            type TEXT,
            capabilities TEXT,
            reputation_score REAL,
            reputation_verified INTEGER,
            total_earned_usd REAL,
            jobs_completed INTEGER,
            success_rate REAL,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            extra TEXT
        );

        CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            opportunity_id TEXT,
            buyer_id TEXT,
            worker_id TEXT,
            amount REAL,
            currency TEXT,
            tx_hash TEXT,
            chain TEXT,
            confidence TEXT,
            paid_at TEXT,
            observed_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS raw_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_id TEXT NOT NULL,
            raw_data TEXT NOT NULL,
            raw_hash TEXT NOT NULL,
            retrieved_at TEXT NOT NULL,
            adapter_version TEXT,
            file_path TEXT
        );

        CREATE TABLE IF NOT EXISTS merkle_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id TEXT NOT NULL,
            event_count INTEGER NOT NULL,
            first_event_id TEXT NOT NULL,
            last_event_id TEXT NOT NULL,
            merkle_root TEXT NOT NULL,
            created_at REAL NOT NULL,
            chain TEXT,
            tx_hash TEXT,
            block_height INTEGER
        );

        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id TEXT NOT NULL,
            source TEXT NOT NULL,
            metric TEXT NOT NULL,
            previous_value TEXT,
            current_value TEXT,
            change_value TEXT,
            observed_at TEXT NOT NULL,
            interval_after TEXT,
            interval_before TEXT,
            adapter_version TEXT,
            raw_hash TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_events_source ON events(source);
        CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
        CREATE INDEX IF NOT EXISTS idx_events_observed ON events(observed_at);
        CREATE INDEX IF NOT EXISTS idx_opportunities_source ON opportunities(source);
        CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(status);
        CREATE INDEX IF NOT EXISTS idx_opportunities_category ON opportunities(category);
        CREATE INDEX IF NOT EXISTS idx_payments_worker ON payments(worker_id);
    """)

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS agent_profiles (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            source_agent_id TEXT NOT NULL,
            name TEXT,
            description TEXT,
            url TEXT,
            tier TEXT,
            reputation_score REAL,
            jobs_completed INTEGER DEFAULT 0,
            total_earned_usd REAL DEFAULT 0,
            success_rate REAL,
            capabilities TEXT,
            wallet_address TEXT,
            chain TEXT,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            extra TEXT
        );

        CREATE TABLE IF NOT EXISTS platform_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            stat_name TEXT NOT NULL,
            stat_value TEXT,
            observed_at TEXT NOT NULL,
            extra TEXT
        );

        CREATE TABLE IF NOT EXISTS service_listings (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            source_service_id TEXT NOT NULL,
            title TEXT,
            description TEXT,
            url TEXT,
            category TEXT,
            price_usdc REAL,
            price_per_call REAL,
            provider_id TEXT,
            provider_reputation REAL,
            total_calls INTEGER DEFAULT 0,
            status TEXT,
            capabilities TEXT,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            extra TEXT
        );

        CREATE TABLE IF NOT EXISTS subnet_data (
            id TEXT PRIMARY KEY,
            netuid INTEGER NOT NULL,
            name TEXT,
            description TEXT,
            emission_pct REAL,
            miner_count INTEGER,
            validator_count INTEGER,
            daily_emissions_tao REAL,
            tao_price_usd REAL,
            gpu_required INTEGER,
            miner_reward TEXT,
            github TEXT,
            status TEXT,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            extra TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_agent_source ON agent_profiles(source);
        CREATE INDEX IF NOT EXISTS idx_service_source ON service_listings(source);
        CREATE INDEX IF NOT EXISTS idx_subnet_netuid ON subnet_data(netuid);
        CREATE INDEX IF NOT EXISTS idx_platform_stats_source ON platform_stats(source, stat_name);
        CREATE INDEX IF NOT EXISTS idx_raw_source ON raw_events(source, source_id);
        CREATE INDEX IF NOT EXISTS idx_obs_opp ON observations(opportunity_id);
        CREATE INDEX IF NOT EXISTS idx_obs_source ON observations(source);
        CREATE INDEX IF NOT EXISTS idx_obs_metric ON observations(metric);
        CREATE INDEX IF NOT EXISTS idx_obs_time ON observations(observed_at);

        CREATE INDEX IF NOT EXISTS idx_merkle_batch_id ON merkle_batches(batch_id);
        CREATE INDEX IF NOT EXISTS idx_merkle_created ON merkle_batches(created_at);
        CREATE INDEX IF NOT EXISTS idx_events_source_id ON events(source_id);
        CREATE INDEX IF NOT EXISTS idx_opportunities_reward ON opportunities(reward_usd);
        CREATE INDEX IF NOT EXISTS idx_agent_earned ON agent_profiles(total_earned_usd);
    """)
    conn.commit()
    conn.close()


init_db()


# === Agent Profile Storage ===

def store_agent_profile(profile: dict) -> str:
    """Store/update an agent profile."""
    pid = profile.get("id", f"profile_{profile.get('source', '')}_{profile.get('source_agent_id', '')}")
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    conn = get_db()
    existing = conn.execute("SELECT id FROM agent_profiles WHERE id=?", (pid,)).fetchone()
    if existing:
        conn.execute("""UPDATE agent_profiles SET name=?, description=?, url=?, tier=?,
            reputation_score=?, jobs_completed=?, total_earned_usd=?, success_rate=?,
            capabilities=?, wallet_address=?, chain=?, last_seen_at=?, extra=?
            WHERE id=?""", (
            profile.get("name", ""), profile.get("description", ""), profile.get("url", ""),
            profile.get("tier", ""), profile.get("reputation_score", 0),
            profile.get("jobs_completed", 0), profile.get("total_earned_usd", 0),
            profile.get("success_rate", 0), json.dumps(profile.get("capabilities", [])),
            profile.get("wallet_address", ""), profile.get("chain", ""),
            now, json.dumps(profile.get("extra", {})), pid))
    else:
        conn.execute("""INSERT INTO agent_profiles
            (id, source, source_agent_id, name, description, url, tier,
             reputation_score, jobs_completed, total_earned_usd, success_rate,
             capabilities, wallet_address, chain, first_seen_at, last_seen_at, extra)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            pid, profile.get("source", ""), profile.get("source_agent_id", ""),
            profile.get("name", ""), profile.get("description", ""), profile.get("url", ""),
            profile.get("tier", ""), profile.get("reputation_score", 0),
            profile.get("jobs_completed", 0), profile.get("total_earned_usd", 0),
            profile.get("success_rate", 0), json.dumps(profile.get("capabilities", [])),
            profile.get("wallet_address", ""), profile.get("chain", ""),
            now, now, json.dumps(profile.get("extra", {}))))
    conn.commit()
    conn.close()
    return pid


# === Platform Stats Storage ===

def store_platform_stat(source: str, stat_name: str, stat_value: str, extra: dict | None = None):
    """Record a platform-level statistic."""
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    conn = get_db()
    conn.execute("INSERT INTO platform_stats (source, stat_name, stat_value, observed_at, extra) VALUES (?,?,?,?,?)",
        (source, stat_name, str(stat_value), now, json.dumps(extra or {})))
    conn.commit()
    conn.close()


# === Service Listing Storage ===

def store_service_listing(service: dict) -> str:
    """Store/update a service listing."""
    sid = service.get("id", f"svc_{service.get('source', '')}_{service.get('source_service_id', '')}")
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    conn = get_db()
    existing = conn.execute("SELECT id FROM service_listings WHERE id=?", (sid,)).fetchone()
    if existing:
        conn.execute("""UPDATE service_listings SET title=?, description=?, url=?, category=?,
            price_usdc=?, price_per_call=?, provider_id=?, provider_reputation=?,
            total_calls=?, status=?, capabilities=?, last_seen_at=?, extra=?
            WHERE id=?""", (
            service.get("title", ""), service.get("description", ""), service.get("url", ""),
            service.get("category", ""), service.get("price_usdc", 0),
            service.get("price_per_call", 0), service.get("provider_id", ""),
            service.get("provider_reputation", 0), service.get("total_calls", 0),
            service.get("status", ""), json.dumps(service.get("capabilities", [])),
            now, json.dumps(service.get("extra", {})), sid))
    else:
        conn.execute("""INSERT INTO service_listings
            (id, source, source_service_id, title, description, url, category,
             price_usdc, price_per_call, provider_id, provider_reputation,
             total_calls, status, capabilities, first_seen_at, last_seen_at, extra)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            sid, service.get("source", ""), service.get("source_service_id", ""),
            service.get("title", ""), service.get("description", ""), service.get("url", ""),
            service.get("category", ""), service.get("price_usdc", 0),
            service.get("price_per_call", 0), service.get("provider_id", ""),
            service.get("provider_reputation", 0), service.get("total_calls", 0),
            service.get("status", ""), json.dumps(service.get("capabilities", [])),
            now, now, json.dumps(service.get("extra", {}))))
    conn.commit()
    conn.close()
    return sid


# === Subnet Data Storage ===

def store_subnet_data(subnet: dict) -> str:
    """Store/update Bittensor subnet data."""
    sid = subnet.get("id", f"sn{subnet.get('netuid', 0)}")
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    conn = get_db()
    existing = conn.execute("SELECT id FROM subnet_data WHERE id=?", (sid,)).fetchone()
    if existing:
        conn.execute("""UPDATE subnet_data SET name=?, description=?, emission_pct=?,
            miner_count=?, validator_count=?, daily_emissions_tao=?, tao_price_usd=?,
            gpu_required=?, miner_reward=?, github=?, status=?, last_seen_at=?, extra=?
            WHERE id=?""", (
            subnet.get("name", ""), subnet.get("description", ""),
            subnet.get("emission_pct", 0), subnet.get("miner_count", 0),
            subnet.get("validator_count", 0), subnet.get("daily_emissions_tao", 0),
            subnet.get("tao_price_usd", 0), 1 if subnet.get("gpu_required") else 0,
            subnet.get("miner_reward", ""), subnet.get("github", ""),
            subnet.get("status", "active"), now,
            json.dumps(subnet.get("extra", {})), sid))
    else:
        conn.execute("""INSERT INTO subnet_data
            (id, netuid, name, description, emission_pct, miner_count, validator_count,
             daily_emissions_tao, tao_price_usd, gpu_required, miner_reward, github,
             status, first_seen_at, last_seen_at, extra)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            sid, subnet.get("netuid", 0), subnet.get("name", ""),
            subnet.get("description", ""), subnet.get("emission_pct", 0),
            subnet.get("miner_count", 0), subnet.get("validator_count", 0),
            subnet.get("daily_emissions_tao", 0), subnet.get("tao_price_usd", 0),
            1 if subnet.get("gpu_required") else 0, subnet.get("miner_reward", ""),
            subnet.get("github", ""), subnet.get("status", "active"),
            now, now, json.dumps(subnet.get("extra", {}))))
    conn.commit()
    conn.close()
    return sid


# === Raw Event Storage (append-only JSONL) ===

def _raw_path(source: str, date_str: str = "") -> Path:
    if not date_str:
        date_str = time.strftime("%Y/%m/%d")
    path = RAW_DIR / source / date_str
    path.mkdir(parents=True, exist_ok=True)
    return path / "events.jsonl.zst"


def store_raw_event(source: str, source_id: str, raw_data: Any,
                    adapter_version: str = "0.1.0") -> str:
    """Store raw event data. Returns content hash."""
    raw_json = json.dumps(raw_data, sort_keys=True, default=str)
    raw_hash = "sha256:" + hashlib.sha256(raw_json.encode()).hexdigest()

    # Store in SQLite raw_events table
    conn = get_db()
    conn.execute(
        "INSERT INTO raw_events (source, source_id, raw_data, raw_hash, retrieved_at, adapter_version) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (source, source_id, raw_json, raw_hash,
         time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), adapter_version)
    )
    conn.commit()
    conn.close()

    return raw_hash


# === Event Storage ===

def store_event(envelope: EventEnvelope) -> str:
    """Store a normalized event. Returns content hash."""
    content_hash = envelope.content_hash()
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO events "
        "(event_id, event_type, schema_version, source, source_id, observed_at, effective_at, "
        "subject_type, subject_id, payload, provenance, raw_hash, content_hash, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (envelope.event_id, envelope.event_type, envelope.schema,
         envelope.source, envelope.source_id, envelope.observed_at, envelope.effective_at,
         envelope.subject.get("type", ""), envelope.subject.get("id", ""),
         json.dumps(envelope.payload, default=str),
         json.dumps(envelope.provenance, default=str),
         envelope.raw_hash, content_hash, time.time())
    )
    conn.commit()
    conn.close()
    return content_hash


# === Opportunity Storage ===

def store_opportunity(opp: dict) -> str:
    """Store/update an opportunity. Returns opportunity ID."""
    opp_id = opp.get("id", f"opp_{opp.get('source', '')}_{opp.get('source_id', '')}")
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    conn = get_db()
    existing = conn.execute("SELECT id FROM opportunities WHERE id=?", (opp_id,)).fetchone()

    if existing:
        # Merge with existing data to preserve fields not in the update
        existing_row = conn.execute("SELECT * FROM opportunities WHERE id=?", (opp_id,)).fetchone()
        existing_data = dict(existing_row) if existing_row else {}

        def _merge(key, default=""):
            """Use incoming value if present, else fall back to existing, else default."""
            if key in opp:
                return opp[key]
            return existing_data.get(key, default)

        def _merge_num(key, default=0):
            if key in opp:
                return opp[key]
            return existing_data.get(key, default)

        merged = {
            "title": _merge("title"),
            "description": _merge("description"),
            "url": _merge("url"),
            "type": _merge("type"),
            "category": _merge("category"),
            "subcategory": _merge("subcategory"),
            "skills": json.dumps(_merge("skills", []) if isinstance(_merge("skills", []), list) else json.loads(existing_data.get("skills") or "[]")),
            "reward_advertised": _merge_num("reward_advertised"),
            "reward_currency": _merge("reward_currency", "USD"),
            "reward_usd": _merge_num("reward_usd"),
            "buyer_id": _merge("buyer_id"),
            "buyer_name": _merge("buyer_name"),
            "status": _merge("status"),
            "posted_at": _merge("posted_at"),
            "claimed_at": _merge("claimed_at"),
            "submitted_at": _merge("submitted_at"),
            "completed_at": _merge("completed_at"),
            "paid_at": _merge("paid_at"),
            "actual_payment_usd": _merge_num("actual_payment_usd"),
            "worker_id": _merge("worker_id"),
            "proposals_count": _merge_num("proposals_count"),
            "views_count": _merge_num("views_count"),
            "extra": json.dumps(_merge("extra", {}) if isinstance(_merge("extra", {}), dict) else json.loads(existing_data.get("extra") or "{}")),
        }

        conn.execute("""
            UPDATE opportunities SET
                title=?, description=?, url=?, type=?, category=?, subcategory=?,
                skills=?, reward_advertised=?, reward_currency=?, reward_usd=?,
                buyer_id=?, buyer_name=?, status=?, posted_at=?, claimed_at=?,
                submitted_at=?, completed_at=?, paid_at=?, actual_payment_usd=?,
                worker_id=?, proposals_count=?, views_count=?, last_seen_at=?, extra=?
            WHERE id=?
        """, (
            merged["title"], merged["description"], merged["url"],
            merged["type"], merged["category"], merged["subcategory"],
            merged["skills"], merged["reward_advertised"], merged["reward_currency"],
            merged["reward_usd"], merged["buyer_id"], merged["buyer_name"],
            merged["status"], merged["posted_at"], merged["claimed_at"],
            merged["submitted_at"], merged["completed_at"], merged["paid_at"],
            merged["actual_payment_usd"], merged["worker_id"],
            merged["proposals_count"], merged["views_count"],
            now, merged["extra"],
            opp_id
        ))
    else:
        # Insert new
        conn.execute("""
            INSERT INTO opportunities
            (id, source, source_id, title, description, url, type, category, subcategory,
             skills, reward_advertised, reward_currency, reward_usd, buyer_id, buyer_name,
             status, posted_at, claimed_at, submitted_at, completed_at, paid_at,
             actual_payment_usd, worker_id, proposals_count, views_count,
             first_seen_at, last_seen_at, extra, schema_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            opp_id, opp.get("source", ""), opp.get("source_id", ""),
            opp.get("title", ""), opp.get("description", ""), opp.get("url", ""),
            opp.get("type", ""), opp.get("category", ""), opp.get("subcategory", ""),
            json.dumps(opp.get("skills", [])), opp.get("reward_advertised", 0),
            opp.get("reward_currency", "USD"), opp.get("reward_usd", 0),
            opp.get("buyer_id", ""), opp.get("buyer_name", ""),
            opp.get("status", ""), opp.get("posted_at", ""),
            opp.get("claimed_at", ""), opp.get("submitted_at", ""),
            opp.get("completed_at", ""), opp.get("paid_at", ""),
            opp.get("actual_payment_usd", 0), opp.get("worker_id", ""),
            opp.get("proposals_count", 0), opp.get("views_count", 0),
            now, now, json.dumps(opp.get("extra", {})),
            opp.get("schema_version", "1.0.0")
        ))

    conn.commit()
    conn.close()
    return opp_id


# === Query Helpers ===

def query_opportunities(source: str = "", status: str = "", category: str = "",
                        skills: str = "", limit: int = 50) -> list[dict]:
    conn = get_db()
    query = "SELECT * FROM opportunities WHERE 1=1"
    params = []

    if source:
        query += " AND source=?"
        params.append(source)
    if status:
        query += " AND status=?"
        params.append(status)
    if category:
        query += " AND category=?"
        params.append(category)
    if skills:
        # Simple skill filter — check if any requested skill is in the skills JSON array
        for skill in skills.split(","):
            query += " AND skills LIKE ?"
            params.append(f"%{skill.strip()}%")

    query += " ORDER BY last_seen_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        d["skills"] = json.loads(d.get("skills") or "[]")
        d["extra"] = json.loads(d.get("extra") or "{}")
        results.append(d)
    return results


def query_events(source: str = "", event_type: str = "",
                 since: str = "", limit: int = 100) -> list[dict]:
    conn = get_db()
    query = "SELECT * FROM events WHERE 1=1"
    params = []

    if source:
        query += " AND source=?"
        params.append(source)
    if event_type:
        query += " AND event_type=?"
        params.append(event_type)
    if since:
        query += " AND observed_at >= ?"
        params.append(since)

    query += " ORDER BY observed_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    conn = get_db()
    stats = {}
    stats["total_events"] = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    stats["total_opportunities"] = conn.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
    stats["total_agents"] = conn.execute("SELECT COUNT(*) FROM agents").fetchone()[0]
    stats["total_payments"] = conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
    stats["total_raw_events"] = conn.execute("SELECT COUNT(*) FROM raw_events").fetchone()[0]

    # Per-source breakdown
    sources = conn.execute(
        "SELECT source, COUNT(*) as cnt FROM events GROUP BY source ORDER BY cnt DESC"
    ).fetchall()
    stats["by_source"] = {r["source"]: r["cnt"] for r in sources}

    # Event type breakdown
    types = conn.execute(
        "SELECT event_type, COUNT(*) as cnt FROM events GROUP BY event_type ORDER BY cnt DESC"
    ).fetchall()
    stats["by_event_type"] = {r["event_type"]: r["cnt"] for r in types}

    # Status breakdown
    statuses = conn.execute(
        "SELECT status, COUNT(*) as cnt FROM opportunities GROUP BY status ORDER BY cnt DESC"
    ).fetchall()
    stats["by_status"] = {r["status"]: r["cnt"] for r in statuses}

    # Total advertised value
    total_adv = conn.execute("SELECT SUM(reward_usd) FROM opportunities WHERE reward_usd > 0").fetchone()[0]
    stats["total_advertised_usd"] = round(total_adv or 0, 2)

    # Total verified payments
    total_paid = conn.execute("SELECT SUM(amount) FROM payments WHERE currency='USD'").fetchone()[0]
    stats["total_verified_payments_usd"] = round(total_paid or 0, 2)

    conn.close()
    return stats
