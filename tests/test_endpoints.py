"""Comprehensive endpoint test — every API endpoint exercised."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import server
from fastapi.testclient import TestClient

# Fresh DB
if os.path.exists("data/repute.db"):
    os.remove("data/repute.db")
server.init_db()
server.products_cache.clear()
server.workers_cache.clear()
server.stacks_cache.clear()
server.demand_cache.clear()
server.context_pack_cache.clear()
server._load_caches()

client = TestClient(server.app)
passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1; print(f"  \u2713 {name}")
    else:
        failed += 1; print(f"  \u2717 {name} — {detail}")

# === Workers ===
print("\n=== Workers ===")
r = client.post("/api/workers", json={"name": "ResearchGoblin", "specialties": ["x402", "AI research"], "bio": "Specialist in x402 ecosystem intelligence."})
test("POST /api/workers", r.status_code == 200 and "worker" in r.json())
wid = r.json()["worker"]["id"]

r = client.get("/api/workers")
test("GET /api/workers", r.status_code == 200 and len(r.json()["workers"]) >= 1)

r = client.get(f"/api/workers/{wid}")
test(f"GET /api/workers/{{id}}", r.status_code == 200 and r.json()["name"] == "ResearchGoblin")

# === Moltbook ===
print("\n=== Moltbook Identity ===")
r = client.post("/api/agents/verify-moltbook", json={"moltbook_token": "test-token", "agent_name": "MoltAgent"})
test("POST /api/agents/verify-moltbook", r.status_code == 200 and r.json()["moltbook"]["verified"])
wid2 = r.json()["worker"]["id"]

# === Products (publish) ===
print("\n=== Products ===")
r = client.post("/api/products", json={"title": "x402 Ecosystem Daily", "text": "The x402 ecosystem is growing. 15 new endpoints today. Search services dominate. Median price $0.01.", "total_price": 0.05, "category": "research", "tags": ["x402", "daily"], "worker_id": wid})
test("POST /api/products", r.status_code == 200 and "product" in r.json())
pid = r.json()["product"]["id"]

r = client.post("/api/publish", json={"title": "Legacy Publish", "text": "Test content for legacy endpoint. Multiple sentences here.", "total_price": 0.03, "category": "data", "worker_id": wid})
test("POST /api/publish (legacy)", r.status_code == 200)

r = client.get("/api/products")
test("GET /api/products", r.status_code == 200 and r.json()["count"] >= 2)

r = client.get(f"/api/products/{pid}")
test(f"GET /api/products/{{id}}", r.status_code == 200 and r.json()["title"] == "x402 Ecosystem Daily")

# === Import ===
print("\n=== Import (Post-Job Hook) ===")
r = client.post("/api/import", json={"title": "Taskmarket Result: AI Pain Points", "text": "Analysis of AI coding tool pain points from a completed Taskmarket job. 2,100 structured examples.", "worker_id": wid, "source": "taskmarket", "source_job_id": "tm-99999", "category": "research", "tags": ["pain-points"]})
test("POST /api/import", r.status_code == 200 and r.json()["product"]["source"] == "taskmarket")
imported_pid = r.json()["product"]["id"]

# === Convert ===
print("\n=== Convert (Submission -> Product) ===")
r = client.post("/api/requests", json={"title": "Test Request for Convert", "budget": 1.0, "sample_slots": 3, "goal": "Test"})
rid = r.json()["request_id"]
r = client.post(f"/api/requests/{rid}/submit", json={"request_id": rid, "worker_id": wid, "title": "Convertible Submission", "preview": "Preview", "full_text": "This is a detailed submission about AI tools that can be converted into a standalone Product after the Request closes."})
sub_id = r.json()["submission_id"]
r = client.post("/api/convert", json={"request_id": rid, "submission_id": sub_id, "worker_id": wid})
test("POST /api/convert", r.status_code == 200 and "product_id" in r.json())
converted_pid = r.json()["product_id"]

# === Inspect + Buy ===
print("\n=== Inspect + Buy ===")
r = client.post("/api/inspect", json={"artifact_id": pid, "buyer_id": "buyer-1"})
test("POST /api/inspect", r.status_code == 200 and "content" in r.json() and r.json()["verified"])

r = client.post("/api/buy", json={"artifact_id": pid, "buyer_id": "buyer-1"})
test("POST /api/buy", r.status_code == 200 and "content" in r.json())

r = client.post("/api/unlock", json={"artifact_id": pid, "buyer_id": "buyer-1"})
test("POST /api/unlock", r.status_code == 200 and r.json()["unlocked"])

# === Options ===
print("\n=== Options ===")
r = client.get(f"/api/options/{pid}/buyer-1")
test("GET /api/options", r.status_code == 200)

# === Refund ===
print("\n=== Refund ===")
r = client.post("/api/refund", json={"artifact_id": pid, "buyer_id": "buyer-1"})
test("POST /api/refund", r.status_code == 200)

# === Reviews ===
print("\n=== Reviews ===")
r = client.post("/api/reviews", json={"product_id": pid, "buyer_id": "buyer-1", "rating": 5, "comment": "Great research"})
test("POST /api/reviews", r.status_code == 200 and r.json()["ok"])

r = client.get(f"/api/reviews/{pid}")
test("GET /api/reviews", r.status_code == 200 and len(r.json()["reviews"]) >= 1)

# === Reputation ===
print("\n=== Reputation ===")
r = client.get(f"/api/reputation/{wid}")
test("GET /api/reputation", r.status_code == 200 and "score" in r.json())

# === Requests ===
print("\n=== Requests ===")
r = client.post("/api/requests", json={"title": "x402 Reliability Research", "budget": 2.0, "sample_slots": 5, "goal": "Find reliability failures", "category": "research"})
test("POST /api/requests (funded)", r.status_code == 200 and r.json()["budget"] == 2.0)
rid2 = r.json()["request_id"]

r = client.post("/api/requests", json={"title": "Free Request", "budget": 0, "goal": "Interest check"})
test("POST /api/requests (free)", r.status_code == 200 and r.json()["budget"] == 0)

r = client.get("/api/requests")
test("GET /api/requests", r.status_code == 200 and r.json()["count"] >= 2)

r = client.get(f"/api/requests/{rid2}")
test("GET /api/requests/{id}", r.status_code == 200)

# Submit to funded request
r = client.post(f"/api/requests/{rid2}/submit", json={"request_id": rid2, "worker_id": wid, "title": "Reliability Analysis", "preview": "Analysis...", "full_text": "x402 reliability analysis: 23% timeout rate, 15% incorrect data, 8% unresponsive. Search APIs most reliable at 92% uptime."})
test("POST /api/requests/{id}/submit", r.status_code == 200 and "product_id" in r.json())
sub2_id = r.json()["submission_id"]

# Submit second entry (different worker)
r = client.post("/api/requests/{rid2}/submit".replace("{rid2}", rid2), json={"request_id": rid2, "worker_id": wid2, "title": "Alternative Analysis", "preview": "Different angle...", "full_text": "Alternative x402 analysis focusing on geographic distribution. US endpoints 94% uptime vs 71% elsewhere."})
test("POST /api/requests/{id}/submit (2nd worker)", r.status_code == 200)
sub2_id = r.json()["submission_id"]

# Reveal from request
r = client.post(f"/api/requests/{rid2}/reveal", json={"request_id": rid2, "submission_id": sub2_id, "buyer_id": "buyer-1"})
test("POST /api/requests/{id}/reveal", r.status_code == 200 and "content" in r.json())

# Resolve
r = client.post(f"/api/requests/{rid2}/resolve", json={"buyer_id": "buyer-1"})
test("POST /api/requests/{id}/resolve", r.status_code == 200 and r.json()["status"] == "closed")

# === Boards ===
print("\n=== Boards ===")
r = client.post("/api/boards", json={"name": "x402 Intelligence", "worker_id": wid, "description": "Daily x402 ecosystem intelligence", "category": "research"})
test("POST /api/boards", r.status_code == 200 and "board_id" in r.json())
bid = r.json()["board_id"]

r = client.get("/api/boards")
test("GET /api/boards", r.status_code == 200 and r.json()["count"] >= 1)

r = client.get(f"/api/boards/{bid}")
test("GET /api/boards/{id}", r.status_code == 200)

r = client.post(f"/api/boards/{bid}/products", json={"title": "Daily Intelligence", "price": 0.03, "type": "product"})
test("POST /api/boards/{id}/products", r.status_code == 200)

r = client.get(f"/api/boards/{bid}/storefront")
test("GET /api/boards/{id}/storefront", r.status_code == 200 and "reputation" in r.json())

# === Context Packs ===
print("\n=== Context Packs ===")
r = client.post("/api/context-packs", json={"product_type": "oracle", "title": "LLM Pricing Oracle", "topic": "llm-pricing", "body": {"value": 0.003, "unit": "USD/1k tokens"}, "suggested_price": 0.005, "producer_id": wid})
test("POST /api/context-packs", r.status_code == 200 and "pack" in r.json())
cpid = r.json()["pack"]["id"]

r = client.get("/api/context-packs")
test("GET /api/context-packs", r.status_code == 200 and r.json()["count"] >= 1)

r = client.get(f"/api/context-packs/{cpid}")
test("GET /api/context-packs/{id}", r.status_code == 200)

r = client.post(f"/api/context-packs/{cpid}/buy", json={"buyer_id": "buyer-1"})
test("POST /api/context-packs/{id}/buy", r.status_code == 200 and r.json()["ok"])

# === Search ===
print("\n=== Search ===")
r = client.get("/api/search?q=x402")
test("GET /api/search?q=x402", r.status_code == 200 and r.json()["total"] >= 1)

r = client.get("/api/search?q=accounting")
test("GET /api/search (no match)", r.status_code == 200)

r = client.get("/api/search?category=research")
test("GET /api/search?category", r.status_code == 200)

# === Demand ===
print("\n=== Demand ===")
# Track some demand
client.post("/api/demand/search?q=x402+reliability&buyer_id=buyer-1")
client.post("/api/demand/search?q=x402+reliability&buyer_id=buyer-2")
client.post("/api/demand/search?q=AI+accounting&buyer_id=buyer-1")

r = client.get("/api/demand")
test("GET /api/demand", r.status_code == 200 and r.json()["total_searches"] >= 2)

r = client.get("/api/demand/trending")
test("GET /api/demand/trending", r.status_code == 200 and len(r.json()["topics"]) >= 1)

# === Pricing ===
print("\n=== Pricing ===")
r = client.get("/api/pricing/suggest?product_type=oracle&production_cost=0.009")
test("GET /api/pricing/suggest", r.status_code == 200 and r.json()["suggested_price"] > 0)

r = client.get("/api/pricing/schema/oracle")
test("GET /api/pricing/schema/{type}", r.status_code == 200 and "required" in r.json()["schema"])

r = client.get("/api/pricing/schema/nonexistent")
test("GET /api/pricing/schema (404)", r.status_code == 404)

# === Stats ===
print("\n=== Stats ===")
r = client.get("/api/stats")
s = r.json()
test("GET /api/stats", r.status_code == 200 and "products" in s and "workers" in s and "context_packs" in s)

# === HTML UI ===
print("\n=== HTML UI ===")
r = client.get("/")
test("GET / (HTML)", r.status_code == 200 and "Moltwork" in r.text)

# === Summary ===
print(f"\n{'='*50}")
print(f"Results: {passed}/{passed+failed} passed, {failed} failed")
if failed:
    sys.exit(1)
else:
    print("All endpoints verified!")
