"""Ingestion pipeline — normalize, dedupe, append to event log."""
from __future__ import annotations

import hashlib
import json
import time
from typing import Callable

from .store import get_db, get_stats, store_raw_event, store_event, store_opportunity
from .schema import make_envelope


def _compute_raw_hash(raw_data: Any) -> str:
    raw_json = json.dumps(raw_data, sort_keys=True, default=str)
    return "sha256:" + hashlib.sha256(raw_json.encode()).hexdigest()


def _detect_event_type(opp: dict) -> str:
    """Detect event type from opportunity status."""
    status = opp.get("status", "").lower()
    if status in ("completed", "paid", "verified"):
        return "completion.observed"
    elif status in ("submitted",):
        return "submission.observed"
    elif status in ("claimed",):
        return "claim.observed"
    else:
        return "opportunity.observed"


def ingest_opportunity(
    source_id: str,
    raw: dict,
    normalize_fn: Callable,
) -> dict:
    """Ingest a single opportunity from a source adapter.

    1. Store raw event data
    2. Normalize to canonical format
    3. Detect event type
    . Create event envelope
    5. Store opportunity
    6. Store event
    7. Return stats

    Returns dict with: event_id, opp_id, event_type, source, source_id
    """
    source_id_str = str(raw.get("id", ""))

    # 1. Store raw
    raw_hash = store_raw_event(source_id, source_id_str, raw)

    # 2. Normalize
    opp = normalize_fn(raw)
    opp["source"] = source_id
    opp["source_id"] = source_id_str

    # 3. Detect event type
    event_type = _detect_event_type(opp)

    # 4. Create envelope
    envelope = make_envelope(
        event_type=event_type,
        source=source_id,
        source_id=source_id_str,
        payload=opp,
        raw_hash=raw_hash,
    )

    # 5. Store opportunity
    opp_id = store_opportunity(opp)

    # 6. Store event
    store_event(envelope)

    return {
        "event_id": envelope.event_id,
        "opp_id": opp_id,
        "event_type": event_type,
        "source": source_id,
        "source_id": source_id_str,
    }


def ingest_source(registry, source_id: str) -> dict:
    """Ingest from a single source adapter."""
    adapter_cls = registry.get(source_id)
    if not adapter_cls:
        return {"error": f"Unknown source: {source_id}"}

    adapter = adapter_cls()
    raw_items = adapter.discover() if not hasattr(adapter.discover(), '__await__') else __import__('asyncio').get_event_loop().run_until_complete(adapter.discover())
    count = 0
    errors = []

    for raw in raw_items:
        try:
            ingest_opportunity(source_id, raw, adapter.normalize)
            count += 1
        except Exception as e:
            errors.append({"id": raw.get("id", "?"), "error": str(e)})

    return {
        "source": source_id,
        "count": count,
        "total_raw": len(raw_items),
        "errors": errors,
    }
