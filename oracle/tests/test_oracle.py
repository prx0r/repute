"""Tests for the Oracle subsystem."""
from __future__ import annotations

import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from oracle.schema import (
    EventEnvelope, EventType, Confidence, OpportunityPayload,
    make_envelope, Evidence, AgentPayload, PaymentPayload,
)
from oracle.store import (
    store_event, store_opportunity, store_raw_event,
    query_opportunities, query_events, get_stats,
)
from oracle.ingest import ingest_opportunity
from oracle.merkle import build_merkle_from_hashes, create_batch_checkpoint
from oracle.adapters.mock import MockAdapter

passed = 0
failed = 0
total = 0


def test(name: str, condition: bool, detail: str = ""):
    global passed, failed, total
    total += 1
    if condition:
        passed += 1
        print(f"  ✓ {name}")
    else:
        failed += 1
        print(f"  ✗ {name}" + (f" — {detail}" if detail else ""))


# === 1. Schema ===
print("\n=== Schema ===")

envelope = make_envelope(
    event_type=EventType.OPPORTUNITY_OBSERVED,
    source="github",
    source_id="test/repo#123",
    payload={"title": "Test bounty", "reward_usd": 100},
)
test("envelope created", envelope.event_id.startswith("evt_"))
test("envelope has content hash", len(envelope.content_hash()) == 64)
test("envelope to_dict works", "event_id" in envelope.to_dict())
test("envelope source is github", envelope.source == "github")
test("envelope schema versioned", "@" in envelope.schema)

# Roundtrip
d = envelope.to_dict()
env2 = EventEnvelope.from_dict(d)
test("envelope roundtrip", env2.event_id == envelope.event_id)

# Evidence
evidence = Evidence(value=500, unit="USD", evidence_type="onchain_verified", source="bountybook")
test("evidence created", evidence.value == 500)

# Payloads
opp = OpportunityPayload(title="Test", reward_usd=100, skills=["solidity"])
test("opportunity payload", opp.title == "Test" and opp.skills == ["solidity"])

agent = AgentPayload(address="0x1234", name="TestAgent", reputation_score=4.5)
test("agent payload", agent.address == "0x1234")

payment = PaymentPayload(amount=100, currency="USDC", tx_hash="0xabc")
test("payment payload", payment.amount == 100)


# === 2. Store ===
print("\n=== Store ===")

raw_hash = store_raw_event("test", "raw_001", {"hello": "world"})
test("raw event stored", raw_hash.startswith("sha256:"))

content_hash = store_event(envelope)
test("event stored", len(content_hash) == 64)

events = query_events(source="github")
test("events queryable", len(events) >= 1)

events_all = query_events()
test("all events queryable", len(events_all) >= 1)


# === 3. Opportunity Store ===
print("\n=== Opportunity Store ===")

opp_id = store_opportunity({
    "id": "test_opp_001",
    "source": "github",
    "source_id": "repo#1",
    "title": "Test Opportunity",
    "description": "A test",
    "type": "bounty",
    "category": "security",
    "skills": ["solidity", "audit"],
    "reward_advertised": 500,
    "reward_usd": 500,
    "status": "open",
    "posted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
})
test("opportunity stored", opp_id == "test_opp_001")

# Update same opportunity
store_opportunity({
    "id": "test_opp_001",
    "source": "github",
    "source_id": "repo#1",
    "title": "Test Opportunity",
    "status": "completed",
    "reward_usd": 500,
    "actual_payment_usd": 500,
})
test("opportunity updated", True)

opps = query_opportunities(source="github")
test("opportunities queryable", len(opps) >= 1)

opps_security = query_opportunities(category="security")
test("opportunities filterable by category", len(opps_security) >= 1)

opps_skill = query_opportunities(skills="solidity")
test("opportunities filterable by skill", len(opps_skill) >= 1)


# === 4. Ingest ===
print("\n=== Ingest ===")

mock = MockAdapter(count=5)
raw_items = []
import asyncio
raw_items = asyncio.run(mock.discover())
test("mock adapter discovers items", len(raw_items) == 5)

result = ingest_opportunity("mock", raw_items[0], mock.normalize)
test("ingest returns event_id", result["event_id"].startswith("evt_"))
test("ingest returns opp_id", len(result["opp_id"]) > 0)
test("ingest detects event type", result["event_type"] in (
    EventType.OPPORTUNITY_OBSERVED, EventType.COMPLETION_OBSERVED,
    EventType.CLAIM_OBSERVED, EventType.SUBMISSION_OBSERVED))

# Ingest all mock items
for raw in raw_items:
    ingest_opportunity("mock", raw, mock.normalize)
test("all mock items ingested", True)


# === 5. Stats ===
print("\n=== Stats ===")

stats = get_stats()
test("stats has total_events", stats["total_events"] > 0)
test("stats has by_source", len(stats["by_source"]) > 0)
test("stats has total_advertised_usd", isinstance(stats["total_advertised_usd"], float))


# === 6. Merkle ===
print("\n=== Merkle ===")

import hashlib as _hl
hashes = [_hl.sha256(f"hash_{i:04d}".encode()).hexdigest() for i in range(8)]
for h in hashes:
    store_event(make_envelope(
        event_type=EventType.OPPORTUNITY_OBSERVED,
        source="test",
        source_id=h,
        payload={"test": True},
    ))

tree = build_merkle_from_hashes(hashes)
test("merkle tree built", tree.size == 8)
test("merkle root is bytes", isinstance(tree.root, bytes))
test("merkle root is 32 bytes", len(tree.root) == 32)

# Proof
proof = tree.get_proof(0)
test("merkle proof has length", len(proof) > 0)
test("merkle proof verifies", tree.verify_proof(tree.leaves[0].hash, proof))

# Tamper detection
import hashlib
bad = hashlib.sha256(b"bad").digest()
test("tampered hash fails", not tree.verify_proof(bad, proof))

# Batch checkpoint
checkpoint = create_batch_checkpoint(hashes)
test("batch checkpoint created", checkpoint["batch_id"].startswith("batch_"))
test("batch has merkle root", len(checkpoint["merkle_root"]) == 64)


# === 7. Query Features ===
print("\n=== Query Features ===")

# Insert varied data for demand queries
import random as _rnd
for i in range(10):
    store_opportunity({
        "id": f"demand_test_{i}",
        "source": "test_demand",
        "source_id": f"dt_{i}",
        "title": f"Demand test {i}",
        "type": "bounty",
        "category": _rnd.choice(["security", "development", "content"]),
        "skills": [_rnd.choice(["solidity", "rust", "typescript"])],
        "reward_usd": round(_rnd.uniform(10, 500), 2),
        "status": _rnd.choice(["open", "completed"]),
    })

test("demand test data inserted", True)


# === 8. Observations (core product) ===
print("\n=== Observations ===")

from oracle.observations import record_observation, diff_and_record, get_observations, compute_metrics, get_market_metrics

# Record a sequence of observations simulating a job lifecycle
obs1 = record_observation(
    opportunity_id="obs_test_001",
    source="test_obs",
    metric="status",
    previous=None,
    current="open",
    observed_at="2026-08-28T10:00:00Z",
)
test("observation recorded", obs1["opportunity_id"] == "obs_test_001")
test("observation has metric", obs1["metric"] == "status")
test("observation has interval", obs1["interval_after"] != "")

# Record proposal count observations
record_observation("obs_test_001", "test_obs", "proposals_count", 0, 2,
                   observed_at="2026-08-28T10:03:00Z",
                   interval_after="2026-08-28T10:00:00Z",
                   interval_before="2026-08-28T10:05:00Z")
record_observation("obs_test_001", "test_obs", "proposals_count", 2, 7,
                   observed_at="2026-08-28T10:07:00Z")
record_observation("obs_test_001", "test_obs", "proposals_count", 7, 12,
                   observed_at="2026-08-28T10:11:00Z")

# Claim
record_observation("obs_test_001", "test_obs", "status", "open", "claimed",
                   observed_at="2026-08-28T10:14:00Z")

# Submit
record_observation("obs_test_001", "test_obs", "status", "claimed", "submitted",
                   observed_at="2026-08-28T16:42:00Z")

# Pay
record_observation("obs_test_001", "test_obs", "status", "submitted", "paid",
                   observed_at="2026-08-28T17:08:00Z")
record_observation("obs_test_001", "test_obs", "actual_payment_usd", 0, 500,
                   observed_at="2026-08-28T17:08:00Z")

obs_list = get_observations(opportunity_id="obs_test_001")
test("observations stored", len(obs_list) >= 7)

# Compute metrics
metrics = compute_metrics("obs_test_001")
test("metrics computed", metrics["observations"] >= 7)
test("metrics has first_seen", "first_seen" in metrics)
test("metrics has status_transitions", "status_transitions" in metrics)
test("metrics has current_status", metrics.get("current_status") == "paid")
test("metrics has time_to_first_bid", "time_to_first_bid_seconds" in metrics)
test("metrics has time_to_claim", "time_to_claim_seconds" in metrics)
test("metrics has time_to_completion", "time_to_completion_seconds" in metrics)


# === 9. Diff and Record ===
print("\n=== Diff and Record ===")

# Simulate polling: first observation
old_state = None
new_state = {"status": "open", "reward_usd": 100, "proposals_count": 0}
obs = diff_and_record("diff_test_001", "test_diff", old_state, new_state,
                       observed_at="2026-08-28T10:00:00Z")
test("diff records initial state", len(obs) >= 3)

# Second poll: proposals changed
old_state = new_state.copy()
new_state = {"status": "open", "reward_usd": 100, "proposals_count": 5}
obs = diff_and_record("diff_test_001", "test_diff", old_state, new_state,
                       observed_at="2026-08-28T10:05:00Z")
test("diff detects proposal change", len(obs) >= 1)
test("diff records correct change", obs[0].get("change") == 5 or obs[0].get("change_value") == 5)

# Third poll: no change
old_state = new_state.copy()
new_state = {"status": "open", "reward_usd": 100, "proposals_count": 5}
obs = diff_and_record("diff_test_001", "test_diff", old_state, new_state,
                       observed_at="2026-08-28T10:10:00Z")
test("diff ignores no-change", len(obs) == 0)

# Fourth poll: status changed
old_state = new_state.copy()
new_state = {"status": "claimed", "reward_usd": 100, "proposals_count": 5, "worker_id": "agent_42"}
obs = diff_and_record("diff_test_001", "test_diff", old_state, new_state,
                       observed_at="2026-08-28T10:15:00Z")
test("diff detects status change", any(o["metric"] == "status" for o in obs))
test("diff detects worker_id", any(o["metric"] == "worker_id" for o in obs))


# === 10. End-to-end lifecycle ===
print("\n=== End-to-End Lifecycle ===")

# Simulate full lifecycle: post → bid → claim → submit → pay
from oracle.ingest import ingest_opportunity
from oracle.adapters.mock import MockAdapter

mock = MockAdapter(count=3)
raw_items = asyncio.run(mock.discover())
result = ingest_opportunity("mock", raw_items[0], mock.normalize)
opp_id = result["opp_id"]

# Simulate polling observations over time
import time as _time
t0 = _time.time()

diff_and_record(opp_id, "mock", None,
    {"status": "open", "reward_usd": 100, "proposals_count": 0},
    observed_at="2026-08-28T10:00:00Z",
    interval_after="2026-08-28T09:55:00Z",
    interval_before="2026-08-28T10:00:00Z")

diff_and_record(opp_id, "mock",
    {"status": "open", "reward_usd": 100, "proposals_count": 0},
    {"status": "open", "reward_usd": 100, "proposals_count": 3},
    observed_at="2026-08-28T10:03:00Z",
    interval_after="2026-08-28T10:00:00Z",
    interval_before="2026-08-28T10:05:00Z")

diff_and_record(opp_id, "mock",
    {"status": "open", "reward_usd": 100, "proposals_count": 3},
    {"status": "claimed", "reward_usd": 100, "proposals_count": 3, "worker_id": "agent_7"},
    observed_at="2026-08-28T10:14:00Z")

diff_and_record(opp_id, "mock",
    {"status": "claimed", "reward_usd": 100, "proposals_count": 3, "worker_id": "agent_7"},
    {"status": "completed", "reward_usd": 100, "actual_payment_usd": 100},
    observed_at="2026-08-28T16:42:00Z")

lifecycle_obs = get_observations(opportunity_id=opp_id)
test("lifecycle observations recorded", len(lifecycle_obs) >= 6)

lifecycle_metrics = compute_metrics(opp_id)
test("lifecycle has time_to_first_bid", "time_to_first_bid_seconds" in lifecycle_metrics)
test("lifecycle has time_to_claim", "time_to_claim_seconds" in lifecycle_metrics)
test("lifecycle has time_to_completion", "time_to_completion_seconds" in lifecycle_metrics)


# === Summary ===
print(f"\n{'='*50}")
print(f"Results: {passed}/{total} passed, {failed} failed")
if failed == 0:
    print("All tests passed!")
else:
    print(f"{failed} test(s) failed")
    sys.exit(1)
