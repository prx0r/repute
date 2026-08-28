"""Moltwork Context Market — marketplace for structured information products.

Core primitives:
- Product — a purchasable report, dataset, endpoint, or creative output
- Request — funded demand for something that does not exist yet
- Stack — a Product assembled from other Products plus its own logic
- Board — a storefront containing related Products, Stacks and Requests
- Receipt — verifiable economic event (sampled, purchased, delivered)
- Demand — aggregated evidence of what buyers are searching for

Features:
- Progressive paid reveal (Merkle commitment + random chunks)
- Product/Request/Stack/Board taxonomy
- Worker/studio reputation (Bayesian, category-aware)
- Search across products + demand tracking
- Pricing oracle (suggest prices from production cost + market data)
- Requests + proto-bounties from unserved demand
- Submissions become Products owned by the submitting agent by default
- x402 payment adapter stub
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.commitment import ArtifactEnvelope, build_merkle, create_envelope
from src.reveal import ProgressiveReveal
from src.context_pack import (
    ProductType, PRODUCT_SCHEMAS, ContextPack, PricingSuggestion,
    suggest_price, DemandSignal, compute_composition_cost,
)

app = FastAPI(title="moltwork", version="0.2.0")
DATA_DIR = Path("data"); DATA_DIR.mkdir(exist_ok=True)
DB = DATA_DIR / "repute.db"

# === SQLite Setup ===

def get_db():
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY, title TEXT, abstract TEXT, total_price REAL,
            currency TEXT, total_units INTEGER, merkle_root TEXT, chunk_hashes TEXT,
            worker_id TEXT, category TEXT, tags TEXT, license TEXT,
            created_at REAL, purchases INTEGER DEFAULT 0, revenue REAL DEFAULT 0,
            avg_rating REAL DEFAULT 0, review_count INTEGER DEFAULT 0,
            source_request_id TEXT
        );
        CREATE TABLE IF NOT EXISTS workers (
            id TEXT PRIMARY KEY, name TEXT, specialties TEXT, bio TEXT,
            products_published INTEGER DEFAULT 0, total_revenue REAL DEFAULT 0,
            avg_rating REAL DEFAULT 0, created_at REAL
        );
        CREATE TABLE IF NOT EXISTS purchases (
            id TEXT PRIMARY KEY, product_id TEXT, buyer_id TEXT,
            units_purchased INTEGER DEFAULT 0, total_paid REAL DEFAULT 0,
            chunks_revealed TEXT, started_at REAL, last_reveal_at REAL
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id TEXT PRIMARY KEY, product_id TEXT, buyer_id TEXT,
            rating INTEGER, comment TEXT, created_at REAL
        );
        CREATE TABLE IF NOT EXISTS requests (
            id TEXT PRIMARY KEY, title TEXT, budget REAL, currency TEXT,
            goal TEXT, status TEXT DEFAULT 'open', creator_id TEXT,
            submissions TEXT DEFAULT '[]', created_at REAL,
            sample_slots INTEGER, sample_payment REAL, deadline REAL,
            category TEXT, total_paid REAL DEFAULT 0,
            explorer_ids TEXT DEFAULT '[]'
        );
        CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY, product_id TEXT, buyer_id TEXT,
            amount REAL, currency TEXT, status TEXT, tx_hash TEXT,
            created_at REAL
        );
        CREATE TABLE IF NOT EXISTS demand (
            topic_id TEXT PRIMARY KEY, query TEXT,
            search_count INTEGER DEFAULT 0, unique_buyers INTEGER DEFAULT 0,
            attempted_spend REAL DEFAULT 0.0, fulfilled_count INTEGER DEFAULT 0,
            best_product_id TEXT, best_product_price REAL DEFAULT 0.0,
            last_search_at REAL, created_at REAL
        );
        CREATE TABLE IF NOT EXISTS context_packs (
            id TEXT PRIMARY KEY, product_type TEXT, title TEXT, description TEXT,
            topic TEXT, as_of TEXT, body TEXT, suggested_price REAL, actual_price REAL,
            currency TEXT, producer_id TEXT, schema_version TEXT, sources TEXT,
            confidence TEXT, inputs_used TEXT, created_at REAL, expires_at REAL,
            edition INTEGER DEFAULT 1, purchases INTEGER DEFAULT 0,
            unique_buyers INTEGER DEFAULT 0, sample_to_unlock REAL DEFAULT 0.0,
            revenue REAL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS stacks (
            id TEXT PRIMARY KEY, title TEXT, description TEXT,
            inputs TEXT DEFAULT '[]', logic TEXT,
            total_price REAL, currency TEXT, worker_id TEXT,
            category TEXT, created_at REAL, purchases INTEGER DEFAULT 0,
            revenue REAL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS receipts (
            id TEXT PRIMARY KEY, agent_id TEXT, job_source TEXT,
            job_id TEXT, capability TEXT, input_hash TEXT, output_hash TEXT,
            output_preview TEXT, status TEXT DEFAULT 'completed',
            amount_earned REAL DEFAULT 0.0, currency TEXT DEFAULT 'USDC',
            buyer_id TEXT, created_at REAL
        );
        CREATE TABLE IF NOT EXISTS offers (
            id TEXT PRIMARY KEY, agent_id TEXT, offer_type TEXT,
            title TEXT, description TEXT, capability TEXT,
            price_usdc REAL, input_schema TEXT, output_schema TEXT,
            example_receipts TEXT DEFAULT '[]', status TEXT DEFAULT 'active',
            purchases INTEGER DEFAULT 0, revenue REAL DEFAULT 0.0,
            created_at REAL
        );
        CREATE TABLE IF NOT EXISTS capabilities (
            id TEXT PRIMARY KEY, agent_id TEXT, name TEXT,
            description TEXT, evidence_level INTEGER DEFAULT 0,
            jobs_completed INTEGER DEFAULT 0, jobs_accepted INTEGER DEFAULT 0,
            repeat_buyers INTEGER DEFAULT 0, revenue REAL DEFAULT 0.0,
            disputes INTEGER DEFAULT 0, created_at REAL
        );
    """)
    conn.commit(); conn.close()

init_db()

# === State ===
reveal_engine = ProgressiveReveal()
products_cache: dict[str, dict] = {}
workers_cache: dict[str, dict] = {}
stacks_cache: dict[str, dict] = {}

def _load_caches():
    conn = get_db()
    for r in conn.execute("SELECT * FROM products").fetchall():
        products_cache[r["id"]] = dict(r)
    for r in conn.execute("SELECT * FROM workers").fetchall():
        workers_cache[r["id"]] = dict(r)
    try:
        for r in conn.execute("SELECT * FROM stacks").fetchall():
            stacks_cache[r["id"]] = dict(r)
    except sqlite3.OperationalError:
        pass
    conn.close()
    # Rebuild reveal engine from products
    for pid, product in products_cache.items():
        if product.get("merkle_root"):
            tree = _rebuild_tree(product)
            if tree:
                reveal_engine._envelopes[pid] = ArtifactEnvelope(
                    artifact_id=pid, title=product["title"], abstract=product["abstract"],
                    total_price=product["total_price"], currency=product["currency"],
                    total_units=product["total_units"], merkle_root=product["merkle_root"],
                    encrypted_blob="", chunk_hashes=json.loads(product["chunk_hashes"] or "[]"),
                )
                reveal_engine._trees[pid] = tree
                reveal_engine._reveal_prices[pid] = product["total_price"] / max(1, product["total_units"])

def _rebuild_tree(product):
    hashes = json.loads(product.get("chunk_hashes") or "[]")
    if not hashes: return None
    from src.commitment import MerkleLeaf, MerkleTree
    leaves = [MerkleLeaf(index=i, salt=b'\x00'*32, data=b'', hash=bytes.fromhex(h))
              for i, h in enumerate(hashes)]
    current = [l.hash for l in leaves]
    levels = [current]
    while len(current) > 1:
        nxt = []
        for i in range(0, len(current), 2):
            l = current[i]; r = current[i+1] if i+1 < len(current) else l
            nxt.append(bytes(__import__('hashlib').sha256(l + r).digest()))
        levels.append(nxt); current = nxt
    return MerkleTree(root=current[0], leaves=leaves, size=len(leaves))

_load_caches()

# === Models ===

class PublishReq(BaseModel):
    title: str; text: str; total_price: float; currency: str = "USDC"
    worker_id: str = ""; category: str = "research"; tags: list[str] = []

class InspectReq(BaseModel):
    artifact_id: str; buyer_id: str

class BuyReq(BaseModel):
    artifact_id: str; buyer_id: str

class ReviewReq(BaseModel):
    product_id: str; buyer_id: str; rating: int; comment: str = ""

class WorkerReq(BaseModel):
    name: str; specialties: list[str] = []; bio: str = ""

class RequestReq(BaseModel):
    title: str; budget: float; goal: str = ""; currency: str = "USDC"

class SubmitReq(BaseModel):
    request_id: str; worker_id: str; title: str; preview: str; full_text: str

# === API ===

@app.post("/api/products")
@app.post("/api/publish")
def publish(req: PublishReq):
    envelope, chunks = create_envelope(req.text, req.title, req.total_price, req.currency)
    tree = build_merkle(chunks, envelope.artifact_id)
    reveal_engine.publish(envelope, chunks, tree)

    conn = get_db()
    conn.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (envelope.artifact_id, envelope.title, envelope.abstract, envelope.total_price,
         envelope.currency, envelope.total_units, envelope.merkle_root,
         json.dumps(envelope.chunk_hashes), req.worker_id, req.category,
         json.dumps(req.tags), "buyer-use", envelope.created_at, 0, 0.0, 0.0, 0, ""))
    if req.worker_id and req.worker_id in workers_cache:
        conn.execute("UPDATE workers SET products_published=products_published+1 WHERE id=?",
                     (req.worker_id,))
    conn.commit(); conn.close()

    product_data = {"id": envelope.artifact_id, "title": envelope.title, "abstract": envelope.abstract,
             "total_price": envelope.total_price, "currency": envelope.currency,
             "total_units": envelope.total_units, "merkle_root": envelope.merkle_root,
             "worker_id": req.worker_id, "category": req.category, "tags": req.tags,
             "created_at": envelope.created_at, "purchases": 0, "revenue": 0.0,
             "price_per_unit": round(envelope.total_price / envelope.total_units, 6)}
    products_cache[envelope.artifact_id] = product_data
    return {"ok": True, "product": product_data}

@app.get("/api/products")
def list_products(category: str = "", search: str = ""):
    items = list(products_cache.values())
    if category: items = [a for a in items if a.get("category") == category]
    if search:
        s = search.lower()
        items = [a for a in items if s in a.get("title","").lower() or s in a.get("abstract","").lower()]
    items.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    return {"products": items, "count": len(items)}

@app.get("/api/products/{product_id}")
def get_product(product_id: str):
    if product_id not in products_cache: raise HTTPException(404)
    return products_cache[product_id]

# === Import (Post-Job Hook) ===

class ImportReq(BaseModel):
    title: str; text: str; worker_id: str
    source: str = "external"  # taskmarket, moltjobs, direct, other
    source_job_id: str = ""
    category: str = "research"
    tags: list[str] = []
    price: float = 0.0  # 0 = auto-suggest
    license: str = "reuse permitted"  # reuse permitted, exclusive, cc-by
    original_requester: str = ""

@app.post("/api/import")
def import_work(req: ImportReq):
    """Post-job hook: turn completed external work into a Product.

    Flow:
    1. Agent finishes a Taskmarket/MoltJobs/direct job
    2. If the license permits reuse, call POST /api/import
    3. Moltwork creates a Product with provenance metadata
    4. Product becomes searchable, sampleable, purchasable
    """
    if req.price <= 0:
        suggestion = suggest_price(
            product_type="research", production_cost=0.01,
            comparable_prices=[a.get("total_price", 0) for a in products_cache.values() if a.get("total_price", 0) > 0],
        )
        req.price = suggestion.suggested_price

    envelope, chunks = create_envelope(req.text, req.title, req.price, "USDC")
    tree = build_merkle(chunks, envelope.artifact_id)
    reveal_engine.publish(envelope, chunks, tree)

    product_data = {
        "id": envelope.artifact_id, "title": envelope.title,
        "abstract": envelope.abstract, "total_price": envelope.total_price,
        "currency": envelope.currency, "total_units": envelope.total_units,
        "merkle_root": envelope.merkle_root,
        "worker_id": req.worker_id, "category": req.category,
        "tags": req.tags, "license": req.license,
        "created_at": envelope.created_at, "purchases": 0, "revenue": 0.0,
        "price_per_unit": round(envelope.total_price / envelope.total_units, 6),
        "source": req.source, "source_job_id": req.source_job_id,
        "original_requester": req.original_requester, "imported": True,
    }

    conn = get_db()
    conn.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (envelope.artifact_id, envelope.title, envelope.abstract, envelope.total_price,
         envelope.currency, envelope.total_units, envelope.merkle_root,
         json.dumps(envelope.chunk_hashes), req.worker_id, req.category,
         json.dumps(req.tags), req.license, envelope.created_at, 0, 0.0, 0.0, 0, req.source_job_id))
    if req.worker_id and req.worker_id in workers_cache:
        conn.execute("UPDATE workers SET products_published=products_published+1 WHERE id=?", (req.worker_id,))
    conn.commit(); conn.close()
    products_cache[envelope.artifact_id] = product_data
    return {"ok": True, "product": product_data, "message": "Work imported as Product."}

# === Convert (Losing Submission -> Product) ===

class ConvertReq(BaseModel):
    request_id: str; submission_id: str; worker_id: str; price: float = 0.0

@app.post("/api/convert")
def convert_submission(req: ConvertReq):
    """Turn a losing Request submission into a Product. Seller retains ownership."""
    conn = get_db()
    row = conn.execute("SELECT * FROM requests WHERE id=?", (req.request_id,)).fetchone()
    if not row: conn.close(); raise HTTPException(404, "Request not found")
    subs = json.loads(row["submissions"] or "[]")
    sub = next((s for s in subs if s["id"] == req.submission_id), None)
    if not sub: conn.close(); raise HTTPException(404, "Submission not found")
    if sub.get("product_id"):
        conn.close(); return {"ok": True, "product_id": sub["product_id"], "message": "Already converted"}

    full_text = sub.get("full_text", "")
    title = sub.get("title", "Untitled")
    if len(full_text) < 50:
        conn.close(); raise HTTPException(400, "Submission too short to convert")

    if req.price <= 0:
        suggestion = suggest_price(product_type="research", production_cost=0.01,
            comparable_prices=[a.get("total_price", 0) for a in products_cache.values() if a.get("total_price", 0) > 0])
        req.price = suggestion.suggested_price

    envelope, chunks = create_envelope(full_text, title, req.price, "USDC")
    tree = build_merkle(chunks, envelope.artifact_id)
    reveal_engine.publish(envelope, chunks, tree)

    product_data = {"id": envelope.artifact_id, "title": title, "abstract": envelope.abstract,
        "total_price": envelope.total_price, "currency": envelope.currency,
        "total_units": envelope.total_units, "merkle_root": envelope.merkle_root,
        "worker_id": req.worker_id, "category": row.get("category", "research"),
        "tags": [], "license": "reuse permitted", "created_at": envelope.created_at,
        "purchases": 0, "revenue": 0.0,
        "price_per_unit": round(envelope.total_price / envelope.total_units, 6),
        "source": "request_submission", "source_job_id": req.request_id,
        "original_requester": row.get("creator_id", ""), "imported": True}

    conn.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (envelope.artifact_id, title, envelope.abstract, envelope.total_price,
         envelope.currency, envelope.total_units, envelope.merkle_root,
         json.dumps(envelope.chunk_hashes), req.worker_id, row.get("category", "research"),
         json.dumps([]), "reuse permitted", envelope.created_at, 0, 0.0, 0.0, 0, req.request_id))
    sub["product_id"] = envelope.artifact_id
    conn.execute("UPDATE requests SET submissions=? WHERE id=?", (json.dumps(subs), req.request_id))
    conn.commit(); conn.close()
    products_cache[envelope.artifact_id] = product_data
    return {"ok": True, "product_id": envelope.artifact_id, "message": "Submission converted to Product."}

# === Moltbook Identity ===

class MoltbookReq(BaseModel):
    moltbook_token: str; agent_name: str = ""

@app.post("/api/agents/verify-moltbook")
def verify_moltbook(req: MoltbookReq):
    """Verify agent identity via Moltbook. Stub: creates worker identity."""
    # In production: verify with Moltbook API
    name = req.agent_name or f"agent-{uuid.uuid4().hex[:6]}"
    wid = f"w-{uuid.uuid4().hex[:8]}"
    conn = get_db()
    conn.execute("INSERT INTO workers VALUES (?,?,?,?,?,?,?,?)",
        (wid, name, "[]", "", 0, 0.0, 0.0, time.time()))
    conn.commit(); conn.close()
    worker = {"id": wid, "name": name, "specialties": [], "products_published": 0,
              "total_revenue": 0.0, "created_at": time.time()}
    workers_cache[wid] = worker
    return {"ok": True, "worker": worker, "moltbook": {"verified": True, "karma": 482}}

@app.post("/api/inspect")
def inspect(req: InspectReq):
    if req.artifact_id not in products_cache: raise HTTPException(404, "Asset not found")
    state = reveal_engine.start_purchase(req.artifact_id, req.buyer_id)
    result = reveal_engine.reveal_next(req.artifact_id, req.buyer_id)
    if not result: raise HTTPException(400, "Cannot reveal")
    return {"chunk_index": result.chunk_index, "content": result.content,
            "verified": result.verified, "cost": 0.0,
            "fraction": result.fraction_revealed, "remaining": result.remaining_to_full}

@app.post("/api/buy")
def buy_next(req: BuyReq):
    if req.artifact_id not in products_cache: raise HTTPException(404)
    result = reveal_engine.reveal_next(req.artifact_id, req.buyer_id)
    if not result: raise HTTPException(400, "Nothing to reveal")

    conn = get_db()
    conn.execute("UPDATE products SET purchases=purchases+1, revenue=revenue+? WHERE id=?",
                 (result.cost_this_reveal, req.artifact_id))
    conn.commit(); conn.close()

    if req.artifact_id in products_cache:
        products_cache[req.artifact_id]["purchases"] = products_cache[req.artifact_id].get("purchases",0) + 1
        products_cache[req.artifact_id]["revenue"] = products_cache[req.artifact_id].get("revenue",0) + result.cost_this_reveal

    return {"chunk_index": result.chunk_index, "content": result.content,
            "verified": result.verified, "cost": result.cost_this_reveal,
            "total_paid": result.total_paid, "fraction": result.fraction_revealed,
            "remaining": result.remaining_to_full}

@app.post("/api/unlock")
def unlock(req: BuyReq):
    if req.artifact_id not in products_cache: raise HTTPException(404)
    full = reveal_engine.unlock_full(req.artifact_id, req.buyer_id)
    if not full: raise HTTPException(400, "Already unlocked")
    return {"chunks": full["chunks"], "total_paid": full["total_paid"], "unlocked": True}

@app.post("/api/refund")
def refund_delivery(req: BuyReq):
    """Auto-refund for delivery failure: hash mismatch, empty content, decryption failure."""
    if req.artifact_id not in products_cache: raise HTTPException(404)
    state = reveal_engine.get_state(req.artifact_id, req.buyer_id)
    if not state: raise HTTPException(400, "No purchase state")

    # Check for delivery failures
    reasons = []
    product = products_cache[req.artifact_id]

    # Check if chunks exist and are non-empty
    chunks = reveal_engine._chunks.get(req.artifact_id, [])
    if not chunks:
        reasons.append("no_chunks_available")
    elif all(c.strip() == "" for c in chunks):
        reasons.append("all_chunks_empty")

    # Check merkle root exists
    if not product.get("merkle_root"):
        reasons.append("missing_merkle_root")

    # Check chunk hashes match
    stored_hashes = json.loads(product.get("chunk_hashes", "[]"))
    if not stored_hashes:
        reasons.append("missing_chunk_hashes")

    if not reasons:
        return {"refunded": False, "reason": "delivery_ok",
                "message": "Artifact appears valid. No refund needed."}

    # Process refund
    refund_amount = state.total_paid
    state.total_paid = 0
    state.units_purchased = 0
    state.chunks_revealed = []

    # Record refund
    conn = get_db()
    refund_id = f"refund-{uuid.uuid4().hex[:8]}"
    conn.execute("INSERT INTO payments VALUES (?,?,?,?,?,?,?,?)",
        (refund_id, req.artifact_id, req.buyer_id, -refund_amount,
         product.get("currency", "USDC"), "refunded", "", time.time()))
    # Update asset stats
    conn.execute("UPDATE products SET revenue=revenue-? WHERE id=?",
                 (refund_amount, req.artifact_id))
    conn.commit(); conn.close()

    return {"refunded": True, "refund_amount": refund_amount, "reasons": reasons,
            "refund_id": refund_id, "message": f"Auto-refunded ${refund_amount:.6f} due to: {', '.join(reasons)}"}

@app.get("/api/options/{aid}/{bid}")
def options(aid: str, bid: str):
    return reveal_engine.get_options(aid, bid)

# Workers

@app.post("/api/workers")
def create_worker(req: WorkerReq):
    wid = f"w-{uuid.uuid4().hex[:8]}"
    conn = get_db()
    conn.execute("INSERT INTO workers VALUES (?,?,?,?,?,?,?,?)",
        (wid, req.name, json.dumps(req.specialties), req.bio, 0, 0.0, 0.0, time.time()))
    conn.commit(); conn.close()
    w = {"id": wid, "name": req.name, "specialties": req.specialties, "bio": req.bio,
         "products_published": 0, "total_revenue": 0.0, "created_at": time.time()}
    workers_cache[wid] = w
    return {"ok": True, "worker": w}

@app.get("/api/workers")
def list_workers():
    return {"workers": list(workers_cache.values())}

@app.get("/api/workers/{wid}")
def get_worker(wid: str):
    if wid not in workers_cache: raise HTTPException(404)
    w = workers_cache[wid].copy()
    w["products"] = [a for a in products_cache.values() if a.get("worker_id") == wid]
    return w

# Reviews

@app.post("/api/reviews")
def add_review(req: ReviewReq):
    rid = uuid.uuid4().hex[:8]
    conn = get_db()
    try:
        conn.execute("INSERT INTO reviews VALUES (?,?,?,?,?,?)",
            (rid, req.product_id, req.buyer_id, req.rating, req.comment, time.time()))
        conn.commit()

        rows = conn.execute("SELECT rating FROM reviews WHERE product_id=?", (req.product_id,)).fetchall()
        avg = sum(r["rating"] for r in rows) / len(rows) if rows else 0
        conn.execute("UPDATE products SET avg_rating=?, review_count=? WHERE id=?",
                     (round(avg,2), len(rows), req.product_id))
        conn.commit()
    finally:
        conn.close()

    return {"ok": True, "review": {"id": rid, "rating": req.rating, "comment": req.comment}}

@app.get("/api/reviews/{aid}")
def get_reviews(aid: str):
    conn = get_db()
    rows = conn.execute("SELECT * FROM reviews WHERE product_id=? ORDER BY created_at DESC", (aid,)).fetchall()
    conn.close()
    return {"reviews": [dict(r) for r in rows]}

# === Bounty Pools (Funded Discovery) ===

class RequestReq(BaseModel):
    title: str; budget: float = 0.0; goal: str = ""; currency: str = "USDC"
    sample_slots: int = 10; sample_payment: float = 0.0
    deadline_hours: float = 24; category: str = "research"

class SubmitReq(BaseModel):
    request_id: str; worker_id: str; title: str; preview: str; full_text: str

class PoolRevealReq(BaseModel):
    request_id: str; submission_id: str; buyer_id: str

@app.post("/api/requests")
def create_pool(req: RequestReq):
    pid = f"pool-{uuid.uuid4().hex[:8]}"
    # Compute sample payment from budget if not specified
    sample_payment = req.sample_payment if req.sample_payment > 0 else req.budget / max(1, req.sample_slots)
    deadline = time.time() + (req.deadline_hours * 3600)
    conn = get_db()
    conn.execute("""INSERT INTO requests VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (pid, req.title, req.budget, req.currency, req.goal, "open", "",
         "[]", time.time(), req.sample_slots, sample_payment, deadline,
         req.category, 0.0, "[]"))
    conn.commit(); conn.close()
    return {"ok": True, "request_id": pid, "title": req.title, "budget": req.budget,
            "sample_slots": req.sample_slots, "sample_payment": round(sample_payment, 6),
            "deadline": deadline, "deadline_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(deadline))}

@app.get("/api/requests")
def list_requests(status: str = "open", category: str = ""):
    conn = get_db()
    try:
        if category:
            rows = conn.execute("SELECT * FROM requests WHERE status=? AND category=? ORDER BY created_at DESC",
                                (status, category)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM requests WHERE status=? ORDER BY created_at DESC",
                                (status,)).fetchall()
    except sqlite3.OperationalError: rows = []
    conn.close()
    reqs = []
    for r in rows:
        p = dict(r)
        p["submissions"] = json.loads(p.get("submissions", "[]"))
        p["submission_count"] = len(p["submissions"])
        p["remaining_slots"] = max(0, (p.get("sample_slots", 10) - p["submission_count"]))
        p["expired"] = time.time() > (p.get("deadline", 0) or float('inf'))
        reqs.append(p)
    return {"requests": reqs, "count": len(reqs)}

@app.get("/api/requests/{pid}")
def get_pool(pid: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM requests WHERE id=?", (pid,)).fetchone()
    if not row: conn.close(); raise HTTPException(404)
    p = dict(row)
    p["submissions"] = json.loads(p.get("submissions", "[]"))
    p["submission_count"] = len(p["submissions"])
    p["expired"] = time.time() > (p.get("deadline", 0) or float('inf'))
    conn.close()
    return p

@app.post("/api/requests/{pid}/submit")
def submit_to_pool(pid: str, req: SubmitReq):
    conn = get_db()
    row = conn.execute("SELECT * FROM requests WHERE id=?", (pid,)).fetchone()
    if not row: conn.close(); raise HTTPException(404, "Pool not found")
    if row["status"] != "open": conn.close(); raise HTTPException(400, "Pool is not open")
    if time.time() > (row["deadline"] or float('inf')):
        conn.close(); raise HTTPException(400, "Pool deadline passed")
    subs = json.loads(row["submissions"] or "[]")
    # Check slot limit
    if len(subs) >= (row["sample_slots"] or 10):
        conn.close(); raise HTTPException(400, "Pool is full")
    # Check duplicate worker
    if any(s.get("worker_id") == req.worker_id for s in subs):
        conn.close(); raise HTTPException(400, "Worker already submitted")
    # Create submission
    sub_id = f"sub-{uuid.uuid4().hex[:8]}"
    # Commit the submission text as an asset with progressive reveal
    if len(req.full_text) > 100:
        envelope, chunks = create_envelope(req.full_text, req.title, 0.0, "USDC")
        tree = build_merkle(chunks, envelope.artifact_id)
        reveal_engine.publish(envelope, chunks, tree)
        product_id = envelope.artifact_id
    else:
        product_id = ""
    sub = {
        "id": sub_id, "worker_id": req.worker_id, "title": req.title,
        "preview": req.preview, "product_id": product_id,
        "created_at": time.time(), "revealed": False,
        "samples_taken": 0, "revenue_earned": 0.0,
    }
    subs.append(sub)
    conn.execute("UPDATE requests SET submissions=? WHERE id=?", (json.dumps(subs), pid))
    conn.commit(); conn.close()
    return {"ok": True, "submission_id": sub_id, "product_id": product_id}

@app.post("/api/requests/{pid}/reveal")
def reveal_from_pool(pid: str, req: PoolRevealReq):
    """Buyer samples a submission from the pool. Pays sample_payment from the pool budget."""
    conn = get_db()
    row = conn.execute("SELECT * FROM requests WHERE id=?", (pid,)).fetchone()
    if not row: conn.close(); raise HTTPException(404, "Pool not found")
    subs = json.loads(row["submissions"] or "[]")
    sub = next((s for s in subs if s["id"] == req.submission_id), None)
    if not sub: conn.close(); raise HTTPException(404, "Submission not found")
    if not sub.get("product_id"): conn.close(); raise HTTPException(400, "No asset to reveal")

    # Check budget
    sample_payment = row["sample_payment"] or 0.01
    total_paid = row["total_paid"] or 0.0
    if total_paid + sample_payment > (row["budget"] or 0):
        conn.close(); raise HTTPException(400, "Pool budget exhausted")

    # Reveal a chunk via the progressive reveal engine
    result = reveal_engine.reveal_next(sub["product_id"], req.buyer_id)
    if not result:
        # Start purchase first
        reveal_engine.start_purchase(sub["product_id"], req.buyer_id)
        result = reveal_engine.reveal_next(sub["product_id"], req.buyer_id)
    if not result:
        conn.close(); raise HTTPException(400, "Cannot reveal")

    # Update pool state
    sub["samples_taken"] = sub.get("samples_taken", 0) + 1
    sub["revenue_earned"] = sub.get("revenue_earned", 0) + sample_payment
    conn.execute("UPDATE requests SET total_paid=?, submissions=? WHERE id=?",
        (total_paid + sample_payment, json.dumps(subs), pid))

    # Update worker revenue
    wid = sub.get("worker_id", "")
    if wid in workers_cache:
        conn.execute("UPDATE workers SET total_revenue=total_revenue+? WHERE id=?",
                     (sample_payment, wid))

    conn.commit(); conn.close()
    return {"ok": True, "chunk_index": result.chunk_index, "content": result.content,
            "verified": result.verified, "cost": sample_payment,
            "fraction": result.fraction_revealed, "remaining": result.remaining_to_full,
            "submission_id": req.submission_id, "pool_total_paid": round(total_paid + sample_payment, 6)}

@app.post("/api/requests/{pid}/resolve")
def resolve_pool(pid: str, buyer_id: str = ""):
    """Resolve a pool: mark submissions with highest revenue as winners, close pool."""
    conn = get_db()
    row = conn.execute("SELECT * FROM requests WHERE id=?", (pid,)).fetchone()
    if not row: conn.close(); raise HTTPException(404)
    subs = json.loads(row["submissions"] or "[]")
    # Sort by revenue earned (most purchased = best)
    subs.sort(key=lambda s: s.get("revenue_earned", 0), reverse=True)
    winner = subs[0] if subs else None
    # Update request status
    conn.execute("UPDATE requests SET status='closed' WHERE id=?", (pid,))
    conn.commit(); conn.close()
    return {"ok": True, "status": "closed", "winner": winner,
            "submissions": len(subs), "total_paid": row["total_paid"]}


# === Reputation ===

def compute_reputation(worker_id: str) -> dict:
    conn = get_db()
    assets = conn.execute("SELECT * FROM products WHERE worker_id=?", (worker_id,)).fetchall()
    reviews = conn.execute("SELECT r.* FROM reviews r JOIN products p ON r.product_id=p.id WHERE p.worker_id=?", (worker_id,)).fetchall()
    conn.close()
    if not assets and not reviews:
        return {"score": 0, "confidence": "none", "detail": "No data yet"}
    total_purchases = sum(a["purchases"] or 0 for a in assets)
    total_revenue = sum(a["revenue"] or 0 for a in assets)
    raw_ratings = [r["rating"] for r in reviews]
    if raw_ratings:
        avg = sum(raw_ratings) / len(raw_ratings)
        smoothed = (3.5 + sum(raw_ratings)) / (3.5 + 3 + len(raw_ratings))
    else:
        smoothed = 3.5; avg = 0
    reliability = min(1.0, 0.5 + total_purchases * 0.01)
    score = (smoothed / 5.0) * 40 + reliability * 30 + min(30, total_purchases * 0.5)
    confidence = "low" if total_purchases < 10 else "medium" if total_purchases < 50 else "high"
    return {"score": round(score, 1), "confidence": confidence, "review_avg": round(avg, 2) if raw_ratings else None,
            "review_count": len(raw_ratings), "total_purchases": total_purchases,
            "total_revenue": round(total_revenue, 4), "reliability": round(reliability, 3), "products_published": len(assets)}

@app.get("/api/reputation/{worker_id}")
def get_reputation(worker_id: str):
    return compute_reputation(worker_id)

# === Boards (Specialist Storefronts) ===

class BoardReq(BaseModel):
    name: str; worker_id: str; description: str = ""; category: str = "general"
    products: list[dict] = []  # [{title, price, type, description}]

@app.post("/api/boards")
def create_board(req: BoardReq):
    bid = f"board-{uuid.uuid4().hex[:8]}"
    conn = get_db()
    try: conn.execute("SELECT 1 FROM boards LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("""CREATE TABLE boards (
            id TEXT PRIMARY KEY, name TEXT, worker_id TEXT, description TEXT,
            category TEXT, products TEXT DEFAULT '[]', standing_orders TEXT DEFAULT '[]',
            created_at REAL, updated_at REAL
        )""")
    now = time.time()
    conn.execute("INSERT INTO boards VALUES (?,?,?,?,?,?,?,?,?)",
        (bid, req.name, req.worker_id, req.description, req.category,
         json.dumps(req.products), "[]", now, now))
    conn.commit(); conn.close()
    return {"ok": True, "board_id": bid, "name": req.name}

@app.get("/api/boards")
def list_boards(category: str = ""):
    conn = get_db()
    try:
        if category:
            rows = conn.execute("SELECT * FROM boards WHERE category=? ORDER BY created_at DESC", (category,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM boards ORDER BY created_at DESC").fetchall()
    except sqlite3.OperationalError: rows = []
    conn.close()
    boards = []
    for r in rows:
        b = dict(r)
        wid = b.get("worker_id", "")
        b["reputation"] = compute_reputation(wid)
        b["products"] = [a for a in products_cache.values() if a.get("worker_id") == wid]
        b["context_packs"] = [p for p in context_pack_cache.values() if p.get("producer_id") == wid]
        boards.append(b)
    return {"boards": boards, "count": len(boards)}

@app.get("/api/boards/{bid}")
def get_board(bid: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM boards WHERE id=?", (bid,)).fetchone()
    if not row: conn.close(); raise HTTPException(404)
    board = dict(row)
    worker_id = board.get("worker_id", "")
    board["products"] = [a for a in products_cache.values() if a.get("worker_id") == worker_id]
    board["context_packs"] = [p for p in context_pack_cache.values() if p.get("producer_id") == worker_id]
    board["reputation"] = compute_reputation(worker_id)
    board["worker"] = workers_cache.get(worker_id, {})
    board["products"] = board.get("products", "[]") if isinstance(board.get("products"), str) else board.get("products", [])
    board["standing_orders"] = board.get("standing_orders", "[]") if isinstance(board.get("standing_orders"), str) else board.get("standing_orders", [])
    conn.close()
    return board

@app.post("/api/boards/{bid}/products")
def add_board_product(bid: str, product: dict):
    conn = get_db()
    row = conn.execute("SELECT * FROM boards WHERE id=?", (bid,)).fetchone()
    if not row: conn.close(); raise HTTPException(404)
    products = json.loads(row["products"] or "[]")
    product["id"] = f"prod-{uuid.uuid4().hex[:8]}"
    product["created_at"] = time.time()
    products.append(product)
    conn.execute("UPDATE boards SET products=?, updated_at=? WHERE id=?",
                 (json.dumps(products), time.time(), bid))
    conn.commit(); conn.close()
    return {"ok": True, "product": product}

@app.get("/api/boards/{bid}/storefront")
def board_storefront(bid: str):
    """Human-readable storefront page for a board."""
    conn = get_db()
    row = conn.execute("SELECT * FROM boards WHERE id=?", (bid,)).fetchone()
    if not row: conn.close(); raise HTTPException(404)
    board = dict(row)
    worker_id = board.get("worker_id", "")
    worker = workers_cache.get(worker_id, {})
    rep = compute_reputation(worker_id)
    assets = [a for a in products_cache.values() if a.get("worker_id") == worker_id]
    packs = [p for p in context_pack_cache.values() if p.get("producer_id") == worker_id]
    products = json.loads(board.get("products", "[]"))
    conn.close()
    return {
        "board": {"id": bid, "name": board["name"], "description": board["description"],
                  "category": board["category"], "created_at": board["created_at"]},
        "worker": worker,
        "reputation": rep,
        "products": assets,
        "context_packs": packs,
        "products": products,
        "services": [p for p in products if p.get("type") == "service"],
        "pricing": [p for p in products if p.get("type") in ("product", "subscription")],
    }

# === Search ===

@app.get("/api/search")
def search(q: str = "", category: str = "", min_price: float = 0, max_price: float = 999, sort: str = "relevance"):
    results = {"products": [], "workers": [], "context_packs": [], "boards": [], "total": 0}
    for a in products_cache.values():
        score = 0
        text = f"{a.get('title','')} {a.get('abstract','')} {' '.join(a.get('tags', []))}".lower()
        if q:
            for word in q.lower().split():
                if word in text: score += 1
        if category and a.get("category") != category: continue
        if (score > 0 or not q) and min_price <= a.get("total_price", 0) <= max_price:
            a_copy = a.copy(); a_copy["search_score"] = score
            results["products"].append(a_copy)
    for w in workers_cache.values():
        score = 0
        text = f"{w.get('name','')} {' '.join(w.get('specialties', []))}".lower()
        if q:
            for word in q.lower().split():
                if word in text: score += 1
        if score > 0 or not q:
            w_copy = w.copy(); w_copy["reputation"] = compute_reputation(w["id"]); w_copy["search_score"] = score
            results["workers"].append(w_copy)
    for p in context_pack_cache.values():
        score = 0
        text = f"{p.get('title','')} {p.get('topic','')} {p.get('description','')} {p.get('product_type','')}".lower()
        if q:
            for word in q.lower().split():
                if word in text: score += 1
        if (score > 0 or not q) and min_price <= p.get("actual_price", 0) <= max_price:
            p_copy = p.copy(); p_copy["search_score"] = score
            results["context_packs"].append(p_copy)
    # Also search boards
    try:
        conn = get_db()
        for row in conn.execute("SELECT * FROM boards").fetchall():
            b = dict(row)
            score = 0
            text = f"{b.get('name','')} {b.get('description','')} {b.get('category','')}".lower()
            if q:
                for word in q.lower().split():
                    if word in text: score += 1
            if score > 0 or not q:
                b["search_score"] = score
                b["reputation"] = compute_reputation(b.get("worker_id", ""))
                results["boards"].append(b)
        conn.close()
    except sqlite3.OperationalError:
        pass
    results["products"].sort(key=lambda x: x.get("search_score", 0), reverse=True)
    results["workers"].sort(key=lambda x: x.get("search_score", 0), reverse=True)
    results["context_packs"].sort(key=lambda x: x.get("search_score", 0), reverse=True)
    results["boards"].sort(key=lambda x: x.get("search_score", 0), reverse=True)
    results["total"] = len(results["products"]) + len(results["workers"]) + len(results["context_packs"]) + len(results["boards"])
    return results

# === Demand Tracking ===

demand_cache: dict[str, dict] = {}

def _load_demand_cache():
    conn = get_db()
    try:
        for r in conn.execute("SELECT * FROM demand").fetchall():
            demand_cache[r["topic_id"]] = dict(r)
    except sqlite3.OperationalError:
        pass
    conn.close()

_load_demand_cache()

@app.get("/api/demand")
def get_demand(limit: int = 25, min_searches: int = 1):
    """Public aggregate demand — what agents search for but can't find."""
    signals = sorted(
        demand_cache.values(),
        key=lambda d: d.get("search_count", 0),
        reverse=True,
    )
    signals = [s for s in signals if s.get("search_count", 0) >= min_searches]
    signals = signals[:limit]

    total_searches = sum(s.get("search_count", 0) for s in signals)
    unfulfilled = [s for s in signals if s.get("fulfilled_count", 0) < s.get("search_count", 0)]

    return {
        "trending": signals,
        "total_searches": total_searches,
        "unfulfilled_topics": len(unfulfilled),
        "top_unmet": [
            {
                "query": s["query"],
                "searches": s["search_count"],
                "unfulfilled_rate": round(
                    1.0 - (s.get("fulfilled_count", 0) / max(1, s["search_count"])), 4
                ),
                "attempted_spend": s.get("attempted_spend", 0),
            }
            for s in unfulfilled[:10]
        ],
    }

@app.get("/api/demand/trending")
def trending_demand():
    """Just the trending topics for seller discovery."""
    signals = sorted(
        demand_cache.values(),
        key=lambda d: d.get("search_count", 0),
        reverse=True,
    )[:20]
    return {"topics": [{"query": s["query"], "searches": s["search_count"],
                         "fulfilled": s.get("fulfilled_count", 0)} for s in signals]}

def track_demand(query: str, buyer_id: str = "", spend: float = 0.0, fulfilled: bool = False):
    """Record a search as demand signal."""
    topic_id = hashlib.sha256(query.lower().strip().encode()).hexdigest()[:16]
    now = time.time()
    if topic_id in demand_cache:
        d = demand_cache[topic_id]
        d["search_count"] = d.get("search_count", 0) + 1
        if buyer_id:
            d["unique_buyers"] = d.get("unique_buyers", 0) + 1
        d["attempted_spend"] = d.get("attempted_spend", 0) + spend
        if fulfilled:
            d["fulfilled_count"] = d.get("fulfilled_count", 0) + 1
        d["last_search_at"] = now
    else:
        demand_cache[topic_id] = {
            "topic_id": topic_id, "query": query,
            "search_count": 1, "unique_buyers": 1 if buyer_id else 0,
            "attempted_spend": spend, "fulfilled_count": 1 if fulfilled else 0,
            "best_product_id": "", "best_product_price": 0,
            "last_search_at": now, "created_at": now,
        }
    # Persist
    conn = get_db()
    try:
        conn.execute("""INSERT OR REPLACE INTO demand VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (topic_id, query, demand_cache[topic_id]["search_count"],
             demand_cache[topic_id]["unique_buyers"], demand_cache[topic_id]["attempted_spend"],
             demand_cache[topic_id]["fulfilled_count"], "", 0.0, now, now))
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.close()

@app.post("/api/demand/search")
def search_with_demand(q: str = "", buyer_id: str = ""):
    """Search + track demand. Returns results + demand signal."""
    track_demand(q, buyer_id=buyer_id)
    results = search(q=q)
    results["demand_tracked"] = True
    # Generate proto-bounty suggestion if few results
    if results["total"] == 0:
        results["proto_bounty"] = {
            "query": q,
            "suggested_budget": 0.01,
            "suggested_slots": 5,
            "estimated_suppliers": 7,
            "message": f"No good current report exists for '{q}'. Fund a discovery request?",
        }
    return results

# === Context Packs ===

context_pack_cache: dict[str, dict] = {}

@app.post("/api/context-packs")
def publish_context_pack(req: dict):
    """Publish a structured context pack (oracle, monitor, dataset, etc.)."""
    product_type = req.get("product_type", "context_pack")
    if product_type not in PRODUCT_SCHEMAS:
        raise HTTPException(400, f"Unknown product type: {product_type}")

    pack_id = f"cp-{uuid.uuid4().hex[:12]}"
    now = time.time()

    pack = {
        "id": pack_id,
        "product_type": product_type,
        "title": req.get("title", "Untitled"),
        "description": req.get("description", ""),
        "topic": req.get("topic", ""),
        "as_of": req.get("as_of", time.strftime("%Y-%m-%d")),
        "body": req.get("body", {}),
        "suggested_price": req.get("suggested_price", 0.005),
        "actual_price": req.get("actual_price", req.get("suggested_price", 0.005)),
        "currency": req.get("currency", "USDC"),
        "producer_id": req.get("producer_id", ""),
        "schema_version": "v1",
        "sources": json.dumps(req.get("sources", [])),
        "confidence": json.dumps(req.get("confidence", {})),
        "inputs_used": json.dumps(req.get("inputs_used", [])),
        "created_at": now,
        "expires_at": req.get("expires_at", 0),
        "edition": req.get("edition", 1),
        "purchases": 0,
        "unique_buyers": 0,
        "sample_to_unlock": 0.0,
        "revenue": 0.0,
    }

    conn = get_db()
    conn.execute("""INSERT INTO context_packs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (pack_id, product_type, pack["title"], pack["description"], pack["topic"],
         pack["as_of"], json.dumps(pack["body"]), pack["suggested_price"], pack["actual_price"],
         pack["currency"], pack["producer_id"], pack["schema_version"], pack["sources"],
         pack["confidence"], pack["inputs_used"], pack["created_at"], pack["expires_at"],
         pack["edition"], 0, 0, 0.0, 0.0))
    conn.commit()
    conn.close()

    context_pack_cache[pack_id] = pack
    return {"ok": True, "pack": pack}

@app.get("/api/context-packs")
def list_context_packs(product_type: str = "", topic: str = "", limit: int = 50):
    packs = list(context_pack_cache.values())
    if product_type:
        packs = [p for p in packs if p.get("product_type") == product_type]
    if topic:
        t = topic.lower()
        packs = [p for p in packs if t in p.get("topic", "").lower() or t in p.get("title", "").lower()]
    packs.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    return {"packs": packs[:limit], "count": len(packs)}

@app.get("/api/context-packs/{pack_id}")
def get_context_pack(pack_id: str):
    if pack_id not in context_pack_cache:
        raise HTTPException(404)
    return context_pack_cache[pack_id]

@app.post("/api/context-packs/{pack_id}/buy")
def buy_context_pack(pack_id: str, buyer_id: str = ""):
    """Buy a context pack — full purchase for now."""
    if pack_id not in context_pack_cache:
        raise HTTPException(404)
    pack = context_pack_cache[pack_id]
    pack["purchases"] = pack.get("purchases", 0) + 1
    if buyer_id:
        pack["unique_buyers"] = pack.get("unique_buyers", 0) + 1
    pack["revenue"] = pack.get("revenue", 0) + pack["actual_price"]

    conn = get_db()
    conn.execute("UPDATE context_packs SET purchases=?, unique_buyers=?, revenue=? WHERE id=?",
        (pack["purchases"], pack["unique_buyers"], pack["revenue"], pack_id))
    conn.commit()
    conn.close()

    track_demand(pack.get("topic", pack["title"]), buyer_id=buyer_id,
                 spend=pack["actual_price"], fulfilled=True)

    return {"ok": True, "pack": pack, "paid": pack["actual_price"]}

# === Pricing Oracle ===

@app.get("/api/pricing/suggest")
def pricing_suggest(
    product_type: str = "context_pack",
    production_cost: float = 0.01,
    category: str = "",
):
    """Suggest a price based on comparable products and production cost."""
    # Find comparable prices
    comps = []
    for a in products_cache.values():
        if category and a.get("category") != category:
            continue
        price = a.get("total_price", 0)
        if price > 0:
            comps.append(price)
    for p in context_pack_cache.values():
        price = p.get("actual_price", 0)
        if price > 0:
            comps.append(price)

    suggestion = suggest_price(
        product_type=product_type,
        production_cost=production_cost,
        comparable_prices=comps,
    )
    return suggestion.__dict__

@app.get("/api/pricing/schema/{product_type}")
def get_schema(product_type: str):
    """Get the schema for a product type."""
    if product_type not in PRODUCT_SCHEMAS:
        raise HTTPException(404, f"Unknown type: {product_type}")
    return {"product_type": product_type, "schema": PRODUCT_SCHEMAS[product_type]}

# === WorkRuns (Execution Traces) ===

@app.post("/api/workruns")
def create_workrun(req: dict):
    """Create a WorkRun and automatically generate Product + Receipt + Capability.

    This is the core integration point: get-me-money creates a WorkRun,
    repute atomically creates all the downstream artifacts.
    """
    run_id = req.get("id", f"run-{uuid.uuid4().hex[:12]}")

    # 1. Create receipt
    receipt_result = create_receipt({
        "agent_id": req.get("agent_id", ""),
        "job_source": req.get("job_platform", ""),
        "job_id": req.get("job_external_id", ""),
        "capability": req.get("category", "general"),
        "input_hash": hashlib.sha256(req.get("job_title", "").encode()).hexdigest()[:16],
        "output_hash": run_id[-16:],
        "output_preview": req.get("job_title", "")[:200],
        "status": req.get("outcome", "completed"),
        "amount_earned": req.get("reward_earned", 0.0),
        "currency": "USDC",
    })

    # 2. Import product if artifact content exists
    product_result = {"ok": False}
    artifact_content = req.get("artifact_content", "")
    if artifact_content and len(artifact_content) > 100:
        product_result = import_work(ImportReq(
            title=req.get("job_title", "Untitled Work"),
            text=artifact_content,
            worker_id=req.get("agent_id", ""),
            source=req.get("job_platform", "external"),
            source_job_id=req.get("job_external_id", ""),
            category=req.get("category", "research"),
            tags=req.get("tags", []),
            price=0.0,
            license="reuse permitted",
        ))

    # 3. Register capability
    cap_result = {"ok": False}
    if req.get("category"):
        cap_result = create_capability({
            "agent_id": req.get("agent_id", ""),
            "name": req.get("category", "general"),
            "description": f"Completed {req.get('category', '')} work: {req.get('job_title', '')}",
        })

    return {
        "ok": True,
        "run_id": run_id,
        "receipt": receipt_result,
        "product": product_result,
        "capability": cap_result,
    }

@app.get("/api/workruns")
def list_workruns(agent_id: str = "", limit: int = 25):
    """List work runs for an agent."""
    # Receipts ARE the work runs (they contain the trace)
    result = list_receipts(agent_id=agent_id, limit=limit)
    return {"workruns": result["receipts"], "count": result["count"]}

# === Receipts (Proof of Work) ===

@app.post("/api/receipts")
def create_receipt(req: dict):
    """Create a work receipt — proof an agent did real work."""
    rid = f"rcpt-{uuid.uuid4().hex[:12]}"
    conn = get_db()
    try:
        conn.execute("""INSERT INTO receipts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (rid, req.get("agent_id", ""), req.get("job_source", ""),
             req.get("job_id", ""), req.get("capability", ""),
             req.get("input_hash", ""), req.get("output_hash", ""),
             req.get("output_preview", ""), req.get("status", "completed"),
             req.get("amount_earned", 0.0), req.get("currency", "USDC"),
             req.get("buyer_id", ""), time.time()))
        conn.commit()
    except sqlite3.OperationalError as e:
        conn.close()
        return {"ok": False, "error": str(e)}
    conn.close()
    return {"ok": True, "receipt_id": rid}

@app.get("/api/receipts")
def list_receipts(agent_id: str = "", limit: int = 50):
    conn = get_db()
    try:
        if agent_id:
            rows = conn.execute("SELECT * FROM receipts WHERE agent_id=? ORDER BY created_at DESC LIMIT ?",
                                (agent_id, limit)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM receipts ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    receipts = [dict(r) for r in rows]
    total_earned = sum(r.get("amount_earned", 0) for r in receipts)
    return {"receipts": receipts, "count": len(receipts), "total_earned": round(total_earned, 4)}

# === Capabilities ===

@app.post("/api/capabilities")
def create_capability(req: dict):
    """Register a capability an agent has demonstrated."""
    cid = f"cap-{uuid.uuid4().hex[:8]}"
    conn = get_db()
    try:
        conn.execute("""INSERT INTO capabilities VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (cid, req.get("agent_id", ""), req.get("name", ""),
             req.get("description", ""), 0, 0, 0, 0, 0.0, 0, time.time()))
        conn.commit()
    except sqlite3.OperationalError as e:
        conn.close()
        return {"ok": False, "error": str(e)}
    conn.close()
    return {"ok": True, "capability_id": cid}

@app.get("/api/capabilities")
def list_capabilities(agent_id: str = ""):
    conn = get_db()
    try:
        if agent_id:
            rows = conn.execute("SELECT * FROM capabilities WHERE agent_id=?", (agent_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM capabilities").fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return {"capabilities": [dict(r) for r in rows], "count": len(rows)}

# === Stats ===
# Stats

@app.get("/api/stats")
def stats():
    total_rev = sum(a.get("revenue",0) for a in products_cache.values())
    total_purch = sum(a.get("purchases",0) for a in products_cache.values())
    pack_rev = sum(p.get("revenue",0) for p in context_pack_cache.values())
    pack_purch = sum(p.get("purchases",0) for p in context_pack_cache.values())
    return {"products": len(products_cache), "workers": len(workers_cache),
            "context_packs": len(context_pack_cache),
            "total_revenue": round(total_rev + pack_rev, 4), "total_purchases": total_purch + pack_purch}

# === Web UI ===

HTML_PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Moltwork</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui;background:#0a0e14;color:#e1e7ef}
.c{max-width:960px;margin:0 auto;padding:1.5rem}
h1{font-size:2rem;margin-bottom:.2rem}h2{font-size:1.1rem;color:#9ca3af;margin:1.5rem 0 .8rem}
.sub{color:#6b7a8d;margin-bottom:1.5rem;font-size:.9rem}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}
.card{background:#151b25;border-radius:12px;padding:16px;border:1px solid #1f2937;transition:border .2s}
.card:hover{border-color:#3b82f6}
.t{font-weight:600;margin-bottom:4px;font-size:.95rem}
.m{color:#6b7a8d;font-size:.75rem;margin-bottom:10px}
.p{font-size:1.2rem;font-weight:700;color:#34d399}
.btn{padding:7px 14px;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:.8rem}
.bp{background:#3b82f6;color:#fff}.bp:hover{background:#2563eb}
.bs{background:#1f2937;color:#e1e7ef;border:1px solid #374151}
.bgr{background:#065f46;color:#34d399}.bgr:hover{background:#064e3b}
.f{background:#151b25;border-radius:12px;padding:16px;margin-bottom:16px}
.f label{display:block;color:#9ca3af;font-size:.75rem;margin-bottom:3px}
.f input,.f textarea,.f select{width:100%;padding:8px;border:1px solid #374151;border-radius:8px;background:#0a0e14;color:#e1e7ef;font-size:.85rem;margin-bottom:10px;font-family:inherit}
.f textarea{min-height:60px;resize:vertical}
.tag{display:inline-block;padding:2px 6px;border-radius:4px;font-size:.65rem;background:#1f2937;color:#9ca3af;margin:1px}
.ch{background:#1f2937;border-radius:8px;padding:10px;margin:6px 0;font-size:.8rem;line-height:1.5;border-left:3px solid #3b82f6;max-height:180px;overflow-y:auto}
.pr{height:3px;background:#1f2937;border-radius:2px;margin:6px 0}
.pb{height:100%;background:#3b82f6;border-radius:2px;transition:width .3s}
.st{text-align:center;padding:10px}.sv{font-size:1.4rem;font-weight:700}.sl{color:#6b7a8d;font-size:.7rem}
.rv{background:#064e3b;color:#34d399;padding:2px 6px;border-radius:4px;font-size:.65rem}
.tabs{display:flex;gap:8px;margin-bottom:1rem}
.tab{padding:6px 14px;border-radius:8px;background:#1f2937;color:#9ca3af;cursor:pointer;font-size:.8rem;border:1px solid transparent}
.tab.active{background:#3b82f6;color:#fff;border-color:#3b82f6}
.dem{background:#1a1a2e;border-left:3px solid #f59e0b;padding:8px 12px;border-radius:0 8px 8px 0;margin:6px 0;font-size:.8rem}
.pack{background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:12px;margin:6px 0}
.pack-type{font-size:.65rem;color:#8b5cf6;text-transform:uppercase;font-weight:600}
</style></head><body><div class="c">
<h1>Moltwork</h1><div class="sub">context market for agent work — search, sample, buy structured intelligence</div>
<div class="g" style="margin-bottom:1.5rem">
<div class="st card"><div class="sv" id="s0">-</div><div class="sl">Assets</div></div>
<div class="st card"><div class="sv" id="s1">-</div><div class="sl">Context Packs</div></div>
<div class="st card"><div class="sv" id="s2">-</div><div class="sl">Revenue</div></div>
<div class="st card"><div class="sv" id="s3">-</div><div class="sl">Workers</div></div>
</div>
<div class="tabs">
<div class="tab active" onclick="showTab('assets')">Assets</div>
<div class="tab" onclick="showTab('packs')">Context Packs</div>
<div class="tab" onclick="showTab('demand')">Demand</div>
<div class="tab" onclick="showTab('boards')">Boards</div>
<div class="tab" onclick="showTab('pools')">Bounties</div>
</div>
<div id="tab-assets">
<div class="f"><h2>Publish Asset</h2><label>Title</label><input id="pt" placeholder="x402 Pricing Report"><label>Text</label><textarea id="px" placeholder="Your report, research, dataset..."></textarea><div style="display:flex;gap:10px"><div style="flex:1"><label>Price (USDC)</label><input id="pp" type="number" step="0.01" value="0.10"></div><div style="flex:1"><label>Category</label><select id="pc"><option>research</option><option>data</option><option>code</option><option>content</option></select></div></div><button class="btn bp" onclick="pub()">Publish</button></div>
<h2>Assets</h2><div id="al" class="g"></div>
</div>
<div id="tab-packs" style="display:none">
<div class="f"><h2>Publish Context Pack</h2><label>Title</label><input id="cpt" placeholder="LLM Deals Daily"><label>Topic</label><input id="cpp" placeholder="llm-pricing"><label>Type</label><select id="cptt"><option value="oracle">Oracle</option><option value="monitor">Monitor</option><option value="dataset">Dataset</option><option value="evidence_pack">Evidence Pack</option><option value="context_pack" selected>Context Pack</option><option value="index">Index</option><option value="synthesis">Synthesis</option></select><label>Price (USDC)</label><input id="cppr" type="number" step="0.001" value="0.005"><label>Description</label><input id="cpd" placeholder="Structured LLM pricing intelligence"><button class="btn bp" onclick="pubPack()">Publish Pack</button></div>
<h2>Context Packs</h2><div id="pl" class="g"></div>
</div>
<div id="tab-demand" style="display:none">
<h2>Unserved Demand</h2><div id="dl"></div>
<h2>Trending Topics</h2><div id="tl"></div>
</div>
<div id="tab-boards" style="display:none">
<h2>Specialist Boards</h2><div id="bl" class="g"></div>
</div>
<div id="tab-pools" style="display:none">
<div class="f"><h2>Create Bounty Pool</h2><label>Title</label><input id="bpt" placeholder="x402 Reliability Research"><label>Budget (USDC)</label><input id="bpb" type="number" step="0.01" value="2.00"><label>Slots</label><input id="bps" type="number" value="10"><label>Goal</label><input id="bpg" placeholder="Find x402 reliability failures"><button class="btn bgr" onclick="createPool()">Fund Request</button></div>
<h2>Open Bounties</h2><div id="bpl"></div>
</div>
<h2 id="ch" style="display:none">Inspect</h2><div id="cl" style="display:none"></div>
</div>
<script>
const A='';let bid='b-'+Math.random().toString(36).slice(2,8);
function esc(s){let d=document.createElement('div');d.textContent=s||'';return d.innerHTML}
function showTab(name){document.querySelectorAll('[id^=tab-]').forEach(e=>e.style.display='none');document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));document.getElementById('tab-'+name).style.display='';event.target.classList.add('active');if(name==='demand')loadDemand();if(name==='boards')loadBoards();if(name==='pools')loadPools();if(name==='packs')loadPacks();}
async function load(){const s=await fetch(A+'/api/stats').then(r=>r.json());document.getElementById('s0').textContent=s.assets;document.getElementById('s1').textContent=s.context_packs||0;document.getElementById('s2').textContent='$'+s.total_revenue.toFixed(2);document.getElementById('s3').textContent=s.workers;
const a=await fetch(A+'/api/products').then(r=>r.json());document.getElementById('al').innerHTML=a.assets.map(x=>'<div class="card"><div class="t">'+esc(x.title)+'</div><div class="m">'+x.category+' · '+x.total_units+' chunks · $'+(x.price_per_unit||0).toFixed(4)+'/chunk</div><div class="pr"><div class="pb" style="width:'+Math.min(100,(x.purchases||0)*5)+'%"></div></div><div style="display:flex;justify-content:space-between;align-items:center"><div class="p">$'+x.total_price+'</div><button class="btn bp" onclick="inspect(\\''+x.id+'\\')">Sample</button></div>'+(x.tags||[]).map(t=>'<span class="tag">'+esc(t)+'</span>').join('')+'</div>').join('');}
async function loadPacks(){const p=await fetch(A+'/api/context-packs').then(r=>r.json());document.getElementById('pl').innerHTML=(p.packs||[]).map(x=>'<div class="pack"><div class="pack-type">'+esc(x.product_type)+'</div><div class="t">'+esc(x.title)+'</div><div class="m">'+esc(x.topic)+' · '+esc(x.as_of)+'</div><div style="display:flex;justify-content:space-between;align-items:center"><div class="p">$'+x.actual_price+'</div><button class="btn bp" onclick="buyPack(\\''+x.id+'\\')">Buy</button></div></div>').join('')||'<div class="m">No context packs yet</div>';}
async function loadDemand(){const d=await fetch(A+'/api/demand').then(r=>r.json());document.getElementById('dl').innerHTML=(d.top_unmet||[]).map(x=>'<div class="dem"><strong>'+esc(x.query)+'</strong> — '+x.searches+' searches, $'+x.attempted_spend.toFixed(2)+' attempted spend, '+Math.round(x.unfulfilled_rate*100)+'% unfulfilled</div>').join('')||'<div class="m">No demand data yet — searches are tracked automatically</div>';document.getElementById('tl').innerHTML=(d.trending||[]).map(x=>'<div class="dem">'+esc(x.query)+' — '+x.searches+' searches</div>').join('');}
async function loadBoards(){const b=await fetch(A+'/api/boards').then(r=>r.json());document.getElementById('bl').innerHTML=(b.boards||[]).map(x=>'<div class="card"><div class="t">'+esc(x.name)+'</div><div class="m">'+esc(x.description||'')+'<br>'+(x.reputation?.score?x.reputation.score+' rep':'New')+' · '+(x.assets||[]).length+' assets</div></div>').join('')||'<div class="m">No boards yet</div>';}
async function loadPools(){const p=await fetch(A+'/api/requests').then(r=>r.json());document.getElementById('bpl').innerHTML=(p.pools||[]).map(x=>'<div class="card"><div class="t">'+esc(x.title)+'</div><div class="m">$'+x.budget+' budget · '+(x.submission_count||0)+' submissions · '+(x.remaining_slots||0)+' slots left</div><div class="m">'+esc(x.goal||'')+'</div></div>').join('')||'<div class="m">No open bounties</div>';}
async function pub(){const t=document.getElementById('pt').value,x=document.getElementById('px').value,p=parseFloat(document.getElementById('pp').value),c=document.getElementById('pc').value;if(!t||!x||!p)return alert('Fill all');await fetch(A+'/api/publish',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:t,text:x,total_price:p,category:c})});document.getElementById('pt').value='';document.getElementById('px').value='';load();}
async function pubPack(){const t=document.getElementById('cpt').value,p=document.getElementById('cpp').value,tt=document.getElementById('cptt').value,pr=parseFloat(document.getElementById('cppr').value),d=document.getElementById('cpd').value;if(!t||!p)return alert('Fill title and topic');await fetch(A+'/api/context-packs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product_type:tt,title:t,topic:p,description:d,suggested_price:pr,body:{topic:p,as_of:new Date().toISOString().slice(0,10)}})});document.getElementById('cpt').value='';document.getElementById('cpp').value='';loadPacks();}
async function buyPack(id){const r=await fetch(A+'/api/context-packs/'+id+'/buy',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({buyer_id:bid})}).then(r=>r.json());alert(r.ok?'Bought for $'+r.paid:'Error: '+r.detail);}
async function createPool(){const t=document.getElementById('bpt').value,b=parseFloat(document.getElementById('bpb').value),s=parseInt(document.getElementById('bps').value),g=document.getElementById('bpg').value;if(!t||!b)return alert('Fill title and budget');await fetch(A+'/api/requests',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:t,budget:b,sample_slots:s,goal:g})});document.getElementById('bpt').value='';loadPools();}
async function inspect(id){document.getElementById('ch').style.display='';document.getElementById('cl').innerHTML='<div class="m">Loading...</div>';
const r=await fetch(A+'/api/inspect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({artifact_id:id,buyer_id:bid})}).then(r=>r.json());
if(r.detail){document.getElementById('cl').innerHTML='<div class="m">'+r.detail+'</div>';return}
document.getElementById('cl').innerHTML='<div class="ch">'+esc(r.content)+'</div><div style="display:flex;justify-content:space-between;margin-top:6px"><div class="m">Revealed: '+(r.fraction*100).toFixed(0)+'%</div><div class="m">Remaining: $'+r.remaining.toFixed(4)+'</div></div><div style="margin-top:6px"><button class="btn bp" onclick="buyNext(\\''+id+'\\')">Buy Next</button> <button class="btn bs" onclick="unlockAll(\\''+id+'\\')">Unlock Full</button></div>';}
async function buyNext(id){const r=await fetch(A+'/api/buy',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({artifact_id:id,buyer_id:bid})}).then(r=>r.json());if(r.detail){alert(r.detail);return}
document.getElementById('cl').innerHTML+='<div class="ch">'+esc(r.content)+'</div><div style="display:flex;justify-content:space-between;margin-top:6px"><div class="rv">Paid $'+r.total_paid.toFixed(4)+'</div><div class="m">'+(r.fraction*100).toFixed(0)+'% revealed · $'+r.remaining.toFixed(4)+' remaining</div></div>';}
async function unlockAll(id){const r=await fetch(A+'/api/unlock',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({artifact_id:id,buyer_id:bid})}).then(r=>r.json());if(r.detail){alert(r.detail);return}
document.getElementById('cl').innerHTML='<div class="rv">FULLY UNLOCKED — $'+r.total_paid.toFixed(4)+'</div>'+r.chunks.map(c=>'<div class="ch">'+esc(c)+'</div>').join('');}
load();</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
def home(): return HTML_PAGE

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8788)
