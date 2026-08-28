"""Tests for core Moltwork flows.

Tests cover:
1. Context Pack schema + pricing
2. Chunking (especially short texts)
3. Progressive reveal
4. Demand tracking
5. x402 adapter
6. MCP client
"""
from __future__ import annotations

import json
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.commitment import chunk_text, create_envelope, build_merkle, derive_reveal_order
from src.reveal import ProgressiveReveal
from src.context_pack import (
    ContextPack, ProductType, PRODUCT_SCHEMAS, DemandSignal,
    suggest_price, compute_composition_cost, composition_chain,
)
from src.x402 import X402Adapter, PaymentRequest
from src.mcp import MoltworkClient, MOLTWORK_TOOLS

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


# === 1. Chunking ===
print("\n=== Chunking ===")

# Short text — should still produce meaningful chunks
short = "This is a short text."
chunks = chunk_text(short, target_chunks=5)
test("short text returns at least 1 chunk", len(chunks) >= 1)
test("short text content preserved", chunks[0] == short)

# Medium text — should split into sentences
medium = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence. Sixth sentence."
chunks = chunk_text(medium, target_chunks=3)
test("medium text produces multiple chunks", len(chunks) >= 2, f"got {len(chunks)}")
all_text = " ".join(chunks)
test("medium text preserves all content", "First sentence" in all_text and "Sixth sentence" in all_text)

# Long text — should produce target_chunks
long_text = ". ".join([f"Sentence number {i} with some content to make it longer." for i in range(50)])
chunks = chunk_text(long_text, target_chunks=10)
test("long text produces multiple chunks", len(chunks) >= 5, f"got {len(chunks)}")

# Very short — single character
tiny = "x"
chunks = chunk_text(tiny)
test("tiny text returns single chunk", len(chunks) == 1)
test("tiny text content preserved", chunks[0] == "x")

# Empty text
empty = ""
chunks = chunk_text(empty)
test("empty text returns single chunk", len(chunks) == 1)


# === 2. Context Packs ===
print("\n=== Context Packs ===")

# Schema validation
test("oracle schema has required fields", "value" in PRODUCT_SCHEMAS["oracle"]["required"])
test("context_pack schema has required fields", "topic" in PRODUCT_SCHEMAS["context_pack"]["required"])
test("dataset schema has required fields", "entities" in PRODUCT_SCHEMAS["dataset"]["required"])

# Create a context pack
pack = ContextPack(
    id="cp-test-001",
    product_type="oracle",
    title="LLM Pricing Oracle",
    description="Current inference prices across providers",
    topic="llm-pricing",
    as_of="2026-08-28",
    body={"value": 0.003, "unit": "USD/1k tokens", "source": "openrouter"},
    suggested_price=0.005,
    actual_price=0.005,
    producer_id="w-test",
)
test("context pack created", pack.id == "cp-test-001")
test("context pack content hash is deterministic", pack.content_hash() == pack.content_hash())
test("context pack to_dict works", "content_hash" in pack.to_dict())

# Pricing oracle
suggestion = suggest_price(
    product_type="oracle",
    production_cost=0.009,
    comparable_prices=[0.004, 0.005, 0.01, 0.012],
    expected_sales=20,
)
test("pricing suggestion has positive price", suggestion.suggested_price > 0)
test("pricing suggestion has comparables", suggestion.comparable_low > 0)
test("pricing suggestion reasoning exists", len(suggestion.reasoning) > 0)

# No comparables — should still produce a price
suggestion2 = suggest_price(
    product_type="context_pack",
    production_cost=0.05,
    comparable_prices=[],
    expected_sales=10,
)
test("pricing without comparables still suggests", suggestion2.suggested_price > 0)

# Composition cost
inputs = [
    {"product": "reddit-daily", "cost": 0.005},
    {"product": "pricing-oracle", "cost": 0.003},
    {"product": "benchmarks", "cost": 0.007},
]
total_cost = compute_composition_cost(inputs)
test("composition cost sums correctly", abs(total_cost - 0.015) < 0.0001)
chain = composition_chain(inputs)
test("composition chain lists upstream", len(chain) == 3)


# === 3. Demand Signal ===
print("\n=== Demand Signals ===")

signal = DemandSignal(
    topic_id="abc123",
    query="x402 reliability failures",
    search_count=311,
    unique_buyers=47,
    attempted_spend=1.27,
    fulfilled_count=3,
)
test("demand signal created", signal.search_count == 311)
test("unfulfilled rate computed", abs(signal.unfulfilled_rate - (1 - 3/311)) < 0.001)
test("topic hash is deterministic", signal.topic_hash == signal.topic_hash)


# === 4. Progressive Reveal ===
print("\n=== Progressive Reveal ===")

# Create an artifact
text = "This is a test report about AI infrastructure. " * 100
envelope, chunks = create_envelope(text, "Test Report", 0.10, "USDC")
tree = build_merkle(chunks, envelope.artifact_id)

reveal = ProgressiveReveal()
reveal.publish(envelope, chunks, tree)

# Start purchase
state = reveal.start_purchase(envelope.artifact_id, "buyer-1")
test("purchase state created", state is not None)
test("reveal order has correct length", len(state.reveal_order) == len(chunks))

# Reveal a chunk
result = reveal.reveal_next(envelope.artifact_id, "buyer-1")
test("reveal returns content", result is not None)
test("reveal has content", len(result.content) > 0)
test("reveal is verified", result.verified)
test("reveal cost is positive", result.cost_this_reveal > 0)
test("reveal fraction is correct", result.fraction_revealed > 0)
test("reveal remaining is positive", result.remaining_to_full > 0)

# Reveal more
result2 = reveal.reveal_next(envelope.artifact_id, "buyer-1")
test("second reveal works", result2 is not None)
test("second reveal different chunk", result2.chunk_index != result.chunk_index)
test("second reveal higher fraction", result2.fraction_revealed > result.fraction_revealed)

# Get options
options = reveal.get_options(envelope.artifact_id, "buyer-1")
test("options show continue", options["action"] == "continue")
test("options show remaining", options["remaining_to_full"] > 0)

# Unlock full
full = reveal.unlock_full(envelope.artifact_id, "buyer-1")
test("unlock returns all chunks", full is not None)
test("unlock has all chunks", len(full["chunks"]) == len(chunks))


# === 5. x402 Adapter ===
print("\n=== x402 Adapter ===")

adapter = X402Adapter(mode="simulated")
challenge = adapter.create_challenge(0.01, "0xPayeeAddress", "test payment")
test("challenge created", challenge.amount == 0.01)
test("challenge has nonce", challenge.nonce.startswith("0x"))
test("challenge has expiry", challenge.valid_before > challenge.valid_after)

receipt = adapter.settle("0xPayerAddress", challenge)
test("receipt created", receipt.status == "settled")
test("receipt has payment_id", len(receipt.payment_id) > 0)
test("receipt has tx_hash", receipt.tx_hash.startswith("0x"))

verified = adapter.verify(receipt.payment_id)
test("receipt verifiable", verified is not None)
test("verified receipt matches", verified.payment_id == receipt.payment_id)

payer_receipts = adapter.get_receipts_for_payer("0xPayerAddress")
test("payer receipts queryable", len(payer_receipts) == 1)


# === 6. MCP Tools ===
print("\n=== MCP Tools ===")

test("MCP tools defined", len(MOLTWORK_TOOLS) >= 8)
tool_names = [t["name"] for t in MOLTWORK_TOOLS]
test("search tool exists", "moltwork_search" in tool_names)
test("sample tool exists", "moltwork_sample" in tool_names)
test("buy tool exists", "moltwork_buy" in tool_names)
test("publish tool exists", "moltwork_publish" in tool_names)
test("publish_pack tool exists", "moltwork_publish_pack" in tool_names)
test("demand tool exists", "moltwork_demand" in tool_names)
test("pricing tool exists", "moltwork_pricing" in tool_names)
test("workers tool exists", "moltwork_workers" in tool_names)

# Each tool has required fields
for tool in MOLTWORK_TOOLS:
    test(f"{tool['name']} has description", len(tool.get("description", "")) > 0)
    test(f"{tool['name']} has inputSchema", "inputSchema" in tool)


# === 7. Integration: Merkle proof verification ===
print("\n=== Merkle Proof Verification ===")

test_text = "Alpha bravo charlie delta echo foxtrot golf hotel india juliet. " * 20
env, chks = create_envelope(test_text, "Proof Test", 0.05)
tree = build_merkle(chks, env.artifact_id)

# Verify each chunk has a valid proof
for i in range(min(3, len(chks))):
    proof = tree.get_proof(i)
    leaf_hash = tree.leaves[i].hash
    verified = tree.verify_proof(leaf_hash, proof, i)
    test(f"chunk {i} proof verifies", verified)

# Tamper detection
bad_hash = b'\x00' * 32
proof = tree.get_proof(0)
tampered = tree.verify_proof(bad_hash, proof, 0)
test("tampered hash fails verification", not tampered)


# === Summary ===
print(f"\n{'='*50}")
print(f"Results: {passed}/{total} passed, {failed} failed")
if failed == 0:
    print("All tests passed!")
else:
    print(f"{failed} test(s) failed")
    sys.exit(1)
