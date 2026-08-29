"""Merkle tree + batch checkpointing for on-chain anchoring.

Every hour: raw hashes → Merkle root → chain checkpoint.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field

from .store import get_db


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class MerkleLeaf:
    index: int
    hash: bytes

    def __post_init__(self):
        if isinstance(self.hash, str):
            self.hash = bytes.fromhex(self.hash)


@dataclass
class MerkleTree:
    root: bytes
    leaves: list[MerkleLeaf]
    size: int

    def get_proof(self, index: int) -> list[tuple[str, bool]]:
        """Get Merkle proof path. Returns list of (hash_hex, is_right)."""
        if index < 0 or index >= self.size:
            return []

        levels = [[leaf.hash for leaf in self.leaves]]
        current = levels[0]
        while len(current) > 1:
            nxt = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                nxt.append(_sha256(left + right))
            levels.append(nxt)
            current = nxt

        proof = []
        idx = index
        for level in levels[:-1]:
            if idx % 2 == 0:
                sibling = level[idx + 1] if idx + 1 < len(level) else level[idx]
                proof.append((sibling.hex(), True))
            else:
                sibling = level[idx - 1]
                proof.append((sibling.hex(), False))
            idx //= 2
        return proof

    def verify_proof(self, leaf_hash: bytes, proof: list[tuple[str, bool]]) -> bool:
        current = leaf_hash
        for hash_hex, is_right in proof:
            sibling = bytes.fromhex(hash_hex)
            if is_right:
                current = _sha256(current + sibling)
            else:
                current = _sha256(sibling + current)
        return current == self.root


def build_merkle_from_hashes(hash_hexes: list[str]) -> MerkleTree:
    """Build Merkle tree from hex-encoded hashes."""
    leaves = [MerkleLeaf(index=i, hash=bytes.fromhex(h)) for i, h in enumerate(hash_hexes)]
    current = [leaf.hash for leaf in leaves]
    while len(current) > 1:
        nxt = []
        for i in range(0, len(current), 2):
            left = current[i]
            right = current[i + 1] if i + 1 < len(current) else left
            nxt.append(_sha256(left + right))
        current = nxt
    return MerkleTree(root=current[0] if current else b'\x00' * 32, leaves=leaves, size=len(leaves))


def create_batch_checkpoint(event_hashes: list[str], chain: str = "") -> dict:
    """Create a Merkle batch checkpoint from event content hashes.

    Returns batch manifest with Merkle root and proof data.
    """
    if not event_hashes:
        return {"error": "no events to batch"}

    tree = build_merkle_from_hashes(event_hashes)
    batch_id = f"batch_{int(time.time())}"

    manifest = {
        "batch_id": batch_id,
        "event_count": len(event_hashes),
        "first_event_hash": event_hashes[0],
        "last_event_hash": event_hashes[-1],
        "merkle_root": tree.root.hex(),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "chain": chain,
    }

    # Store in DB
    conn = get_db()
    conn.execute(
        "INSERT INTO merkle_batches (batch_id, event_count, first_event_id, last_event_id, merkle_root, created_at, chain) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (batch_id, len(event_hashes), event_hashes[0], event_hashes[-1],
         tree.root.hex(), time.time(), chain)
    )
    conn.commit()
    conn.close()

    return manifest


def get_recent_batches(limit: int = 10) -> list[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM merkle_batches ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_checkpoint_for_event(content_hash: str) -> dict | None:
    """Find the batch checkpoint that includes this event."""
    conn = get_db()
    # We can't do range queries on hex strings reliably.
    # Instead, check all batches and verify membership via hash comparison.
    batches = conn.execute(
        "SELECT * FROM merkle_batches ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    for batch in batches:
        first = batch["first_event_id"]
        last = batch["last_event_id"]
        # Exact match on boundaries
        if content_hash == first or content_hash == last:
            return dict(batch)
        # For interior check, compare as integers
        try:
            h = int(content_hash, 16)
            f = int(first, 16)
            l = int(last, 16)
            if f <= h <= l:
                return dict(batch)
        except (ValueError, TypeError):
            pass

    return None
