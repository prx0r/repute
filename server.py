"""Repute — complete marketplace with SQLite persistence.

Features:
- Progressive paid reveal (Merkle commitment + random chunks)
- Worker/studio reputation (Bayesian, category-aware)
- Boards (specialist storefronts with products + services)
- Search across assets
- Bounty pools
- Standing orders
"""
from __future__ import annotations

import json
import math
import os
import sqlite3
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.commitment import ArtifactEnvelope, build_merkle, create_envelope
from src.reveal import ProgressiveReveal

app = FastAPI(title="repute", version="0.1.0")
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
        CREATE TABLE IF NOT EXISTS assets (
            id TEXT PRIMARY KEY, title TEXT, abstract TEXT, total_price REAL,
            currency TEXT, total_units INTEGER, merkle_root TEXT, chunk_hashes TEXT,
            worker_id TEXT, category TEXT, tags TEXT, license TEXT,
            created_at REAL, purchases INTEGER DEFAULT 0, revenue REAL DEFAULT 0,
            avg_rating REAL DEFAULT 0, review_count INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS workers (
            id TEXT PRIMARY KEY, name TEXT, specialties TEXT, bio TEXT,
            assets_published INTEGER DEFAULT 0, total_revenue REAL DEFAULT 0,
            avg_rating REAL DEFAULT 0, created_at REAL
        );
        CREATE TABLE IF NOT EXISTS purchases (
            id TEXT PRIMARY KEY, asset_id TEXT, buyer_id TEXT,
            units_purchased INTEGER DEFAULT 0, total_paid REAL DEFAULT 0,
            chunks_revealed TEXT, started_at REAL, last_reveal_at REAL
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id TEXT PRIMARY KEY, asset_id TEXT, buyer_id TEXT,
            rating INTEGER, comment TEXT, created_at REAL
        );
        CREATE TABLE IF NOT EXISTS pools (
            id TEXT PRIMARY KEY, title TEXT, budget REAL, currency TEXT,
            goal TEXT, status TEXT DEFAULT 'open', worker_id TEXT,
            submissions TEXT DEFAULT '[]', created_at REAL
        );
        CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY, asset_id TEXT, buyer_id TEXT,
            amount REAL, currency TEXT, status TEXT, tx_hash TEXT,
            created_at REAL
        );
    """)
    conn.commit(); conn.close()

init_db()

# === State ===
reveal_engine = ProgressiveReveal()
assets_cache: dict[str, dict] = {}
workers_cache: dict[str, dict] = {}

def _load_caches():
    conn = get_db()
    for r in conn.execute("SELECT * FROM assets").fetchall():
        assets_cache[r["id"]] = dict(r)
    for r in conn.execute("SELECT * FROM workers").fetchall():
        workers_cache[r["id"]] = dict(r)
    conn.close()
    # Rebuild reveal engine from assets
    for aid, asset in assets_cache.items():
        if asset.get("merkle_root"):
            tree = _rebuild_tree(asset)
            if tree:
                reveal_engine._envelopes[aid] = ArtifactEnvelope(
                    artifact_id=aid, title=asset["title"], abstract=asset["abstract"],
                    total_price=asset["total_price"], currency=asset["currency"],
                    total_units=asset["total_units"], merkle_root=asset["merkle_root"],
                    encrypted_blob="", chunk_hashes=json.loads(asset["chunk_hashes"] or "[]"),
                )
                reveal_engine._trees[aid] = tree
                reveal_engine._reveal_prices[aid] = asset["total_price"] / max(1, asset["total_units"])

def _rebuild_tree(asset):
    hashes = json.loads(asset.get("chunk_hashes") or "[]")
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
    artifact_id: str; buyer_id: str; rating: int; comment: str = ""

class WorkerReq(BaseModel):
    name: str; specialties: list[str] = []; bio: str = ""

class PoolReq(BaseModel):
    title: str; budget: float; goal: str = ""; currency: str = "USDC"

class SubmitReq(BaseModel):
    pool_id: str; worker_id: str; title: str; preview: str; full_text: str

# === API ===

@app.post("/api/publish")
def publish(req: PublishReq):
    envelope, chunks = create_envelope(req.text, req.title, req.total_price, req.currency)
    tree = build_merkle(chunks, envelope.artifact_id)
    reveal_engine.publish(envelope, chunks, tree)

    conn = get_db()
    conn.execute("INSERT INTO assets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (envelope.artifact_id, envelope.title, envelope.abstract, envelope.total_price,
         envelope.currency, envelope.total_units, envelope.merkle_root,
         json.dumps(envelope.chunk_hashes), req.worker_id, req.category,
         json.dumps(req.tags), "buyer-use", envelope.created_at, 0, 0.0, 0.0, 0))
    if req.worker_id and req.worker_id in workers_cache:
        conn.execute("UPDATE workers SET assets_published=assets_published+1 WHERE id=?",
                     (req.worker_id,))
    conn.commit(); conn.close()

    asset = {"id": envelope.artifact_id, "title": envelope.title, "abstract": envelope.abstract,
             "total_price": envelope.total_price, "currency": envelope.currency,
             "total_units": envelope.total_units, "merkle_root": envelope.merkle_root,
             "worker_id": req.worker_id, "category": req.category, "tags": req.tags,
             "created_at": envelope.created_at, "purchases": 0, "revenue": 0.0,
             "price_per_unit": round(envelope.total_price / envelope.total_units, 6)}
    assets_cache[envelope.artifact_id] = asset
    return {"ok": True, "asset": asset}

@app.get("/api/assets")
def list_assets(category: str = "", search: str = ""):
    items = list(assets_cache.values())
    if category: items = [a for a in items if a.get("category") == category]
    if search:
        s = search.lower()
        items = [a for a in items if s in a.get("title","").lower() or s in a.get("abstract","").lower()]
    items.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    return {"assets": items, "count": len(items)}

@app.get("/api/assets/{asset_id}")
def get_asset(asset_id: str):
    if asset_id not in assets_cache: raise HTTPException(404)
    return assets_cache[asset_id]

@app.post("/api/inspect")
def inspect(req: InspectReq):
    if req.artifact_id not in assets_cache: raise HTTPException(404, "Asset not found")
    state = reveal_engine.start_purchase(req.artifact_id, req.buyer_id)
    result = reveal_engine.reveal_next(req.artifact_id, req.buyer_id)
    if not result: raise HTTPException(400, "Cannot reveal")
    return {"chunk_index": result.chunk_index, "content": result.content,
            "verified": result.verified, "cost": 0.0,
            "fraction": result.fraction_revealed, "remaining": result.remaining_to_full}

@app.post("/api/buy")
def buy_next(req: BuyReq):
    if req.artifact_id not in assets_cache: raise HTTPException(404)
    result = reveal_engine.reveal_next(req.artifact_id, req.buyer_id)
    if not result: raise HTTPException(400, "Nothing to reveal")

    conn = get_db()
    conn.execute("UPDATE assets SET purchases=purchases+1, revenue=revenue+? WHERE id=?",
                 (result.cost_this_reveal, req.artifact_id))
    conn.commit(); conn.close()

    if req.artifact_id in assets_cache:
        assets_cache[req.artifact_id]["purchases"] = assets_cache[req.artifact_id].get("purchases",0) + 1
        assets_cache[req.artifact_id]["revenue"] = assets_cache[req.artifact_id].get("revenue",0) + result.cost_this_reveal

    return {"chunk_index": result.chunk_index, "content": result.content,
            "verified": result.verified, "cost": result.cost_this_reveal,
            "total_paid": result.total_paid, "fraction": result.fraction_revealed,
            "remaining": result.remaining_to_full}

@app.post("/api/unlock")
def unlock(req: BuyReq):
    if req.artifact_id not in assets_cache: raise HTTPException(404)
    full = reveal_engine.unlock_full(req.artifact_id, req.buyer_id)
    if not full: raise HTTPException(400, "Already unlocked")
    return {"chunks": full["chunks"], "total_paid": full["total_paid"], "unlocked": True}

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
         "assets_published": 0, "total_revenue": 0.0, "created_at": time.time()}
    workers_cache[wid] = w
    return {"ok": True, "worker": w}

@app.get("/api/workers")
def list_workers():
    return {"workers": list(workers_cache.values())}

@app.get("/api/workers/{wid}")
def get_worker(wid: str):
    if wid not in workers_cache: raise HTTPException(404)
    w = workers_cache[wid].copy()
    w["assets"] = [a for a in assets_cache.values() if a.get("worker_id") == wid]
    return w

# Reviews

@app.post("/api/reviews")
def add_review(req: ReviewReq):
    rid = uuid.uuid4().hex[:8]
    conn = get_db()
    conn.execute("INSERT INTO reviews VALUES (?,?,?,?,?,?)",
        (rid, req.artifact_id, req.buyer_id, req.rating, req.comment, time.time()))
    conn.commit(); conn.close()

    revs = conn or get_db()
    try:
        rows = revs.execute("SELECT rating FROM reviews WHERE artifact_id=?", (req.artifact_id,)).fetchall()
        avg = sum(r["rating"] for r in rows) / len(rows) if rows else 0
        revs.execute("UPDATE assets SET avg_rating=?, review_count=? WHERE id=?",
                     (round(avg,2), len(rows), req.artifact_id))
        revs.commit()
    finally: revs.close()

    return {"ok": True, "review": {"id": rid, "rating": req.rating, "comment": req.comment}}

@app.get("/api/reviews/{aid}")
def get_reviews(aid: str):
    conn = get_db()
    rows = conn.execute("SELECT * FROM reviews WHERE asset_id=? ORDER BY created_at DESC", (aid,)).fetchall()
    conn.close()
    return {"reviews": [dict(r) for r in rows]}

# Pools

@app.post("/api/pools")
def create_pool(req: PoolReq):
    pid = f"pool-{uuid.uuid4().hex[:8]}"
    conn = get_db()
    conn.execute("INSERT INTO pools VALUES (?,?,?,?,?,?,?,?)",
        (pid, req.title, req.budget, req.currency, req.goal, "open", "", "[]", time.time()))
    conn.commit(); conn.close()
    return {"ok": True, "pool_id": pid, "title": req.title, "budget": req.budget}

@app.get("/api/pools")
def list_pools():
    conn = get_db()
    rows = conn.execute("SELECT * FROM pools WHERE status='open' ORDER BY created_at DESC").fetchall()
    conn.close()
    return {"pools": [dict(r) for r in rows]}

@app.post("/api/pools/{pid}/submit")
def submit_to_pool(pid: str, req: SubmitReq):
    conn = get_db()
    row = conn.execute("SELECT * FROM pools WHERE id=?", (pid,)).fetchone()
    if not row: conn.close(); raise HTTPException(404)
    subs = json.loads(row["submissions"] or "[]")
    sub = {"id": uuid.uuid4().hex[:8], "worker_id": req.worker_id, "title": req.title,
           "preview": req.preview, "full_text": req.full_text, "created_at": time.time()}
    subs.append(sub)
    conn.execute("UPDATE pools SET submissions=? WHERE id=?", (json.dumps(subs), pid))
    conn.commit(); conn.close()
    return {"ok": True, "submission_id": sub["id"]}


# === Reputation ===

def compute_reputation(worker_id: str) -> dict:
    conn = get_db()
    assets = conn.execute("SELECT * FROM assets WHERE worker_id=?", (worker_id,)).fetchall()
    reviews = conn.execute("SELECT r.* FROM reviews r JOIN assets a ON r.asset_id=a.id WHERE a.worker_id=?", (worker_id,)).fetchall()
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
            "total_revenue": round(total_revenue, 4), "reliability": round(reliability, 3), "assets_published": len(assets)}

@app.get("/api/reputation/{worker_id}")
def get_reputation(worker_id: str):
    return compute_reputation(worker_id)

# === Boards ===

class BoardReq(BaseModel):
    name: str; worker_id: str; description: str = ""; category: str = "general"

@app.post("/api/boards")
def create_board(req: BoardReq):
    bid = f"board-{uuid.uuid4().hex[:8]}"
    conn = get_db()
    try: conn.execute("SELECT 1 FROM boards LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("CREATE TABLE boards (id TEXT PRIMARY KEY, name TEXT, worker_id TEXT, description TEXT, category TEXT, products TEXT DEFAULT '[]', created_at REAL)")
    conn.execute("INSERT INTO boards VALUES (?,?,?,?,?,?,?)", (bid, req.name, req.worker_id, req.description, req.category, "[]", time.time()))
    conn.commit(); conn.close()
    return {"ok": True, "board_id": bid, "name": req.name}

@app.get("/api/boards")
def list_boards():
    conn = get_db()
    try: rows = conn.execute("SELECT * FROM boards ORDER BY created_at DESC").fetchall()
    except sqlite3.OperationalError: rows = []
    conn.close()
    return {"boards": [dict(r) for r in rows]}

@app.get("/api/boards/{bid}")
def get_board(bid: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM boards WHERE id=?", (bid,)).fetchone()
    if not row: conn.close(); raise HTTPException(404)
    board = dict(row)
    worker_id = board.get("worker_id", "")
    board["assets"] = [a for a in assets_cache.values() if a.get("worker_id") == worker_id]
    board["reputation"] = compute_reputation(worker_id)
    conn.close()
    return board

# === Search ===

@app.get("/api/search")
def search(q: str = "", category: str = "", min_price: float = 0, max_price: float = 999, sort: str = "relevance"):
    results = {"assets": [], "workers": [], "total": 0}
    for a in assets_cache.values():
        score = 0
        text = f"{a.get('title','')} {a.get('abstract','')} {' '.join(a.get('tags', []))}".lower()
        if q:
            for word in q.lower().split():
                if word in text: score += 1
        if category and a.get("category") != category: continue
        if score > 0 or not q:
            a_copy = a.copy(); a_copy["search_score"] = score
            results["assets"].append(a_copy)
    for w in workers_cache.values():
        score = 0
        text = f"{w.get('name','')} {' '.join(w.get('specialties', []))}".lower()
        if q:
            for word in q.lower().split():
                if word in text: score += 1
        if score > 0 or not q:
            w_copy = w.copy(); w_copy["reputation"] = compute_reputation(w["id"]); w_copy["search_score"] = score
            results["workers"].append(w_copy)
    results["assets"].sort(key=lambda x: x.get("search_score", 0), reverse=True)
    results["workers"].sort(key=lambda x: x.get("search_score", 0), reverse=True)
    results["total"] = len(results["assets"]) + len(results["workers"])
    return results

# === Stats ===
# Stats

@app.get("/api/stats")
def stats():
    total_rev = sum(a.get("revenue",0) for a in assets_cache.values())
    total_purch = sum(a.get("purchases",0) for a in assets_cache.values())
    return {"assets": len(assets_cache), "workers": len(workers_cache),
            "total_revenue": round(total_rev, 4), "total_purchases": total_purch}

# === Web UI ===

HTML_PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>repute</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui;background:#0a0e14;color:#e1e7ef}
.c{max-width:900px;margin:0 auto;padding:2rem}
h1{font-size:2rem;margin-bottom:.2rem}h2{font-size:1.1rem;color:#9ca3af;margin:1.5rem 0 .8rem}
.sub{color:#6b7a8d;margin-bottom:2rem}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
.card{background:#151b25;border-radius:12px;padding:20px;border:1px solid #1f2937;transition:border .2s}
.card:hover{border-color:#3b82f6}
.t{font-weight:600;margin-bottom:6px}.m{color:#6b7a8d;font-size:.8rem;margin-bottom:12px}
.p{font-size:1.3rem;font-weight:700;color:#34d399}
.btn{padding:8px 16px;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:.85rem}
.bp{background:#3b82f6;color:#fff}.bp:hover{background:#2563eb}
.bs{background:#1f2937;color:#e1e7ef;border:1px solid #374151}
.f{background:#151b25;border-radius:12px;padding:20px;margin-bottom:20px}
.f label{display:block;color:#9ca3af;font-size:.8rem;margin-bottom:4px}
.f input,.f textarea,.f select{width:100%;padding:10px;border:1px solid #374151;border-radius:8px;background:#0a0e14;color:#e1e7ef;font-size:.9rem;margin-bottom:12px;font-family:inherit}
.f textarea{min-height:80px;resize:vertical}
.tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:.7rem;background:#1f2937;color:#9ca3af;margin:2px}
.ch{background:#1f2937;border-radius:8px;padding:12px;margin:8px 0;font-size:.85rem;line-height:1.5;border-left:3px solid #3b82f6;max-height:200px;overflow-y:auto}
.pr{height:4px;background:#1f2937;border-radius:2px;margin:8px 0}
.pb{height:100%;background:#3b82f6;border-radius:2px;transition:width .3s}
.st{text-align:center;padding:12px}.sv{font-size:1.5rem;font-weight:700}.sl{color:#6b7a8d;font-size:.75rem}
.rv{background:#064e3b;color:#34d399;padding:2px 8px;border-radius:4px;font-size:.7rem}
</style></head><body><div class="c">
<h1>repute</h1><div class="sub">progressive paid reveal for agent work</div>
<div class="g" style="margin-bottom:2rem"><div class="st card"><div class="sv" id="s0">-</div><div class="sl">Assets</div></div><div class="st card"><div class="sv" id="s1">-</div><div class="sl">Workers</div></div><div class="st card"><div class="sv" id="s2">-</div><div class="sl">Revenue</div></div><div class="st card"><div class="sv" id="s3">-</div><div class="sl">Purchases</div></div></div>
<div class="f"><h2>Publish Asset</h2><label>Title</label><input id="pt" placeholder="x402 Pricing Report"><label>Text</label><textarea id="px" placeholder="Your report, research, dataset..."></textarea><label>Price</label><input id="pp" type="number" step="0.01" value="0.10"><label>Category</label><select id="pc"><option>research</option><option>data</option><option>code</option><option>content</option></select><button class="btn bp" onclick="pub()">Publish</button></div>
<h2>Assets</h2><div id="al" class="g"></div>
<h2>Workers</h2><div id="wl"></div>
<h2 id="ch" style="display:none">Inspect</h2><div id="cl" style="display:none"></div>
</div>
<script>
const A='';let bid='b-'+Math.random().toString(36).slice(2,8);
async function load(){const s=await fetch(A+'/api/stats').then(r=>r.json());document.getElementById('s0').textContent=s.assets;document.getElementById('s1').textContent=s.workers;document.getElementById('s2').textContent='$'+s.total_revenue.toFixed(2);document.getElementById('s3').textContent=s.total_purchases;
const a=await fetch(A+'/api/assets').then(r=>r.json());document.getElementById('al').innerHTML=a.assets.map(x=>'<div class="card"><div class="t">'+esc(x.title)+'</div><div class="m">'+x.category+' · '+x.total_units+' chunks · $'+(x.price_per_unit||0).toFixed(4)+'/chunk</div><div class="pr"><div class="pb" style="width:'+Math.min(100,(x.purchases||0)*5)+'%"></div></div><div style="display:flex;justify-content:space-between;align-items:center"><div class="p">$'+x.total_price+'</div><button class="btn bp" onclick="inspect(\\''+x.id+'\\')">Sample</button></div>'+(x.tags||[]).map(t=>'<span class="tag">'+esc(t)+'</span>').join('')+'</div>').join('');
const w=await fetch(A+'/api/workers').then(r=>r.json());document.getElementById('wl').innerHTML=w.workers.map(x=>'<div class="card" style="display:flex;gap:12px;align-items:center"><div style="width:40px;height:40px;border-radius:50%;background:#3b82f6;display:flex;align-items:center;justify-content:center;font-weight:700">'+esc(x.name[0]||'?')+'</div><div><div style="font-weight:600">'+esc(x.name)+'</div><div class="m">'+(x.specialties||[]).join(', ')+' · $'+(x.total_revenue||0).toFixed(2)+'</div></div></div>').join('')}
function esc(s){let d=document.createElement('div');d.textContent=s||'';return d.innerHTML}
async function pub(){const t=document.getElementById('pt').value,x=document.getElementById('px').value,p=parseFloat(document.getElementById('pp').value),c=document.getElementById('pc').value;if(!t||!x||!p)return alert('Fill all');await fetch(A+'/api/publish',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:t,text:x,total_price:p,category:c})});document.getElementById('pt').value='';document.getElementById('px').value='';load();}
async function inspect(id){document.getElementById('ch').style.display='';document.getElementById('cl').innerHTML='<div class="m">Loading...</div>';
const r=await fetch(A+'/api/inspect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({artifact_id:id,buyer_id:bid})}).then(r=>r.json());
if(r.detail){document.getElementById('cl').innerHTML='<div class="m">'+r.detail+'</div>';return}
document.getElementById('cl').innerHTML='<div class="ch">'+esc(r.content)+'</div><div style="display:flex;justify-content:space-between;margin-top:8px"><div class="m">Revealed: '+(r.fraction*100).toFixed(0)+'%</div><div class="m">Remaining: $'+r.remaining.toFixed(4)+'</div></div><div style="margin-top:8px"><button class="btn bp" onclick="buyNext(\\''+id+'\\')">Buy Next Chunk</button> <button class="btn bs" onclick="unlockAll(\\''+id+'\\')">Unlock Full</button></div>';}
async function buyNext(id){const r=await fetch(A+'/api/buy',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({artifact_id:id,buyer_id:bid})}).then(r=>r.json());if(r.detail){alert(r.detail);return}
document.getElementById('cl').innerHTML+='<div class="ch">'+esc(r.content)+'</div><div style="display:flex;justify-content:space-between;margin-top:8px"><div class="rv">Paid $'+r.total_paid.toFixed(4)+'</div><div class="m">'+(r.fraction*100).toFixed(0)+'% revealed · $'+r.remaining.toFixed(4)+' remaining</div></div>';}
async function unlockAll(id){const r=await fetch(A+'/api/unlock',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({artifact_id:id,buyer_id:bid})}).then(r=>r.json());if(r.detail){alert(r.detail);return}
document.getElementById('cl').innerHTML='<div class="rv">FULLY UNLOCKED — $'+r.total_paid.toFixed(4)+'</div>'+r.chunks.map(c=>'<div class="ch">'+esc(c)+'</div>').join('');}
load();</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
def home(): return HTML_PAGE

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8788)
