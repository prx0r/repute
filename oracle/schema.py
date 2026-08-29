"""Oracle event envelope and data models.

The event envelope is the ONLY thing we lock. Everything in payload is versioned.
This gives us schema evolution without data migration.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


# === Evidence Classes ===

class Confidence(str, Enum):
    ONCHAIN_VERIFIED = "onchain_verified"
    SOURCE_VERIFIED = "source_verified"
    DIRECTLY_OBSERVED = "directly_observed"
    DERIVED = "derived"
    INFERRED = "inferred"
    USER_REPORTED = "user_reported"
    UNKNOWN = "unknown"


# === Event Types ===

class EventType(str, Enum):
    OPPORTUNITY_CREATED = "opportunity.created"
    OPPORTUNITY_OBSERVED = "opportunity.observed"
    OPPORTUNITY_UPDATED = "opportunity.updated"
    OPPORTUNITY_CLOSED = "opportunity.closed"

    BID_OBSERVED = "bid.observed"
    PROPOSAL_OBSERVED = "proposal.observed"
    CLAIM_OBSERVED = "claim.observed"
    AWARD_OBSERVED = "award.observed"

    SUBMISSION_OBSERVED = "submission.observed"
    COMPLETION_OBSERVED = "completion.observed"

    PAYMENT_OBSERVED = "payment.observed"

    AGENT_OBSERVED = "agent.observed"
    SERVICE_OBSERVED = "service.observed"

    BUYER_OBSERVED = "buyer.observed"
    SELLER_OBSERVED = "seller.observed"

    CORRECTION = "correction"


# === The Locked Event Envelope ===

@dataclass
class EventEnvelope:
    """The canonical event envelope. This is the ONLY thing we lock.

    Everything interesting lives in the versioned payload.
    New event types and schemas don't require touching historical data.
    """
    event_id: str
    event_type: str
    schema: str  # e.g. "moltwork/opportunity-observed@1.0.0"

    source: str  # adapter id: "github", "algora", "moltjobs", etc.
    source_id: str  # native id from the source

    observed_at: str  # ISO timestamp when we observed this
    effective_at: str  # ISO timestamp when this was true at the source

    subject: dict  # {"type": "opportunity", "id": "github:owner/repo#123"}

    payload: dict  # the versioned, schema-specific data
    provenance: dict  # evidence trail

    raw_hash: str = ""  # sha256 of raw source data

    def __post_init__(self):
        if not self.event_id:
            self.event_id = f"evt_{uuid.uuid4().hex[:16]}"
        if not self.observed_at:
            self.observed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if not self.effective_at:
            self.effective_at = self.observed_at

    def content_hash(self) -> str:
        """Deterministic hash of this event for dedup + Merkle tree."""
        canonical = json.dumps({
            "event_type": self.event_type,
            "schema": self.schema,
            "source": self.source,
            "source_id": self.source_id,
            "effective_at": self.effective_at,
            "subject": self.subject,
            "payload": self.payload,
        }, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> EventEnvelope:
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})


# === Evidence Attachment ===

@dataclass
class Evidence:
    """Provenance attached to every important field value."""
    value: Any
    unit: str = ""
    evidence_type: str = "directly_observed"  # Confidence enum value
    source: str = ""
    raw_hash: str = ""
    observed_at: str = ""
    adapter: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# === Opportunity Payload (versioned) ===

@dataclass
class OpportunityPayload:
    """The versioned payload for opportunity events.

    This schema CAN change. The envelope cannot.
    """
    title: str = ""
    description: str = ""
    url: str = ""

    type: str = ""  # bounty, listing, service, job, grant
    category: str = ""  # security, development, content, research, etc.
    subcategory: str = ""

    skills: list[str] = field(default_factory=list)

    reward_advertised: float = 0.0
    reward_currency: str = "USD"
    reward_usd: float = 0.0

    buyer_id: str = ""
    buyer_name: str = ""
    buyer_reputation: float = 0.0

    # Lifecycle timestamps (observed, not inferred)
    posted_at: str = ""
    claimed_at: str = ""
    submitted_at: str = ""
    completed_at: str = ""
    paid_at: str = ""

    # Outcome
    status: str = ""  # open, claimed, submitted, completed, paid, failed, expired
    actual_payment_usd: float = 0.0
    worker_id: str = ""
    execution_cost_usd: float = 0.0

    # Competition signal
    proposals_count: int = 0
    views_count: int = 0

    # Source-specific extra fields
    extra: dict = field(default_factory=dict)

    # Schema version
    schema_version: str = "1.0.0"

    def to_dict(self) -> dict:
        return asdict(self)


# === Agent Payload ===

@dataclass
class AgentPayload:
    """Payload for agent.observed events."""
    address: str = ""
    name: str = ""
    network: str = ""
    type: str = ""  # agent_type
    capabilities: list[str] = field(default_factory=list)
    reputation_score: float = 0.0
    reputation_verified: bool = False
    total_earned_usd: float = 0.0
    jobs_completed: int = 0
    success_rate: float = 0.0
    registered_at: str = ""
    last_active: str = ""
    extra: dict = field(default_factory=dict)
    schema_version: str = "1.0.0"

    def to_dict(self) -> dict:
        return asdict(self)


# === Payment Payload ===

@dataclass
class PaymentPayload:
    """Payload for payment.observed events."""
    amount: float = 0.0
    currency: str = "USD"
    tx_hash: str = ""
    chain: str = ""
    buyer_id: str = ""
    worker_id: str = ""
    opportunity_id: str = ""
    paid_at: str = ""
    confidence: str = "source_verified"
    extra: dict = field(default_factory=dict)
    schema_version: str = "1.0.0"

    def to_dict(self) -> dict:
        return asdict(self)


# === Helpers ===

def make_envelope(
    event_type: str,
    source: str,
    source_id: str,
    payload: dict,
    subject_type: str = "opportunity",
    schema_version: str = "1.0.0",
    raw_hash: str = "",
    observed_at: str = "",
    effective_at: str = "",
) -> EventEnvelope:
    """Create an event envelope from a payload dict."""
    schema_name = f"moltwork/{event_type.replace('.', '-')}"
    return EventEnvelope(
        event_id=f"evt_{uuid.uuid4().hex[:16]}",
        event_type=event_type,
        schema=f"{schema_name}@{schema_version}",
        source=source,
        source_id=source_id,
        observed_at=observed_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        effective_at=effective_at or observed_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        subject={"type": subject_type, "id": f"{source}:{source_id}"},
        payload=payload,
        provenance={
            "adapter": f"{source}@{schema_version}",
            "confidence": payload.get("confidence", "directly_observed"),
        },
        raw_hash=raw_hash,
    )
