"""x402 Payment Adapter — stub for EIP-3009 USDC settlement.

This provides the interface for x402 payments. In V0, it simulates payment.
In production, it would use the x402 facilitator pattern from Honeycomb:

  1. Buyer signs EIP-3009 TransferWithAuthorization
  2. Facilitator broadcasts settle() on-chain
  3. USDC moves from buyer wallet to provider wallet

For now, all payments are simulated (no on-chain settlement).
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, asdict


@dataclass
class PaymentRequest:
    """An x402 payment challenge."""
    amount: float
    currency: str  # "USDC"
    payee: str  # recipient address
    memo: str
    nonce: str  # bytes32 replay nonce
    valid_after: float
    valid_before: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PaymentReceipt:
    """Proof that payment was settled."""
    payment_id: str
    amount: float
    currency: str
    payer: str
    payee: str
    tx_hash: str  # simulated or real
    settled_at: float
    status: str  # "settled" | "pending" | "failed"

    def to_dict(self) -> dict:
        return asdict(self)


class X402Adapter:
    """Payment adapter for x402 USDC settlement.

    In V0: simulated payments (no on-chain tx).
    In V1: real EIP-3009 via facilitator.
    """

    def __init__(self, mode: str = "simulated"):
        self.mode = mode  # "simulated" | "onchain"
        self._receipts: dict[str, PaymentReceipt] = {}

    def create_challenge(self, amount: float, payee: str, memo: str = "") -> PaymentRequest:
        """Create an x402 402-challenge for a payment."""
        now = time.time()
        nonce = hashlib.sha256(f"{amount}:{payee}:{now}".encode()).hexdigest()[:64]
        return PaymentRequest(
            amount=amount,
            currency="USDC",
            payee=payee,
            memo=memo,
            nonce=f"0x{nonce}",
            valid_after=now,
            valid_before=now + 3600,  # 1 hour window
        )

    def settle(self, payer: str, challenge: PaymentRequest, signature: str = "") -> PaymentReceipt:
        """Settle a payment. In simulated mode, just creates a receipt."""
        payment_id = hashlib.sha256(
            f"{payer}:{challenge.amount}:{challenge.nonce}".encode()
        ).hexdigest()[:16]

        receipt = PaymentReceipt(
            payment_id=payment_id,
            amount=challenge.amount,
            currency=challenge.currency,
            payer=payer,
            payee=challenge.payee,
            tx_hash=f"0x{'sim' + payment_id}" if self.mode == "simulated" else "",
            settled_at=time.time(),
            status="settled",
        )

        self._receipts[payment_id] = receipt
        return receipt

    def verify(self, payment_id: str) -> PaymentReceipt | None:
        """Verify a payment receipt exists."""
        return self._receipts.get(payment_id)

    def get_receipts_for_payer(self, payer: str) -> list[PaymentReceipt]:
        """Get all receipts for a payer."""
        return [r for r in self._receipts.values() if r.payer == payer]


# Global adapter instance
adapter = X402Adapter(mode="simulated")
