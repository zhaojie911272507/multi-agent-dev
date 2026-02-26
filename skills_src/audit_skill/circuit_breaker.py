"""
Circuit Breaker: safety brakes for financial audit.
- Amount > $100,000 → PENDING_HUMAN_REVIEW
- Intermediate vars: no persistence, release after use
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4

from .models import AuditConclusion, AuditTrail, LineRef

# Single-audit amount threshold; above this → human review
AMOUNT_THRESHOLD = Decimal("100000")


def check_amount_breach(amount: Decimal) -> bool:
    """True if amount exceeds auto-approval threshold."""
    return amount >= AMOUNT_THRESHOLD


def build_audit_trail(
    conclusion: AuditConclusion,
    source_files: list[str],
    line_refs: list[LineRef],
    reasoning_path: list[str],
    details: dict[str, Any] | None = None,
) -> AuditTrail:
    """
    Generate AuditTrail.json-compatible structure.
    Intermediate vars must NOT be persisted elsewhere.
    """
    return AuditTrail(
        audit_id=str(uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        source_files=source_files,
        line_refs=line_refs,
        reasoning_path=reasoning_path,
        conclusion=conclusion,
        details=details or {},
    )


def audit_trail_to_dict(trail: AuditTrail) -> dict[str, Any]:
    """Export for AuditTrail.json / logging. No intermediate persistence."""
    return trail.model_dump(mode="json")


class CircuitBreaker:
    """
    Enforces: amount > $100k → PENDING_HUMAN_REVIEW.
    All logic uses in-memory only; no DB persist of intermediates.
    """

    def __init__(self, threshold: Decimal | None = None) -> None:
        self.threshold = threshold or AMOUNT_THRESHOLD

    def apply(
        self,
        amounts: list[Decimal],
        current_conclusion: AuditConclusion,
    ) -> AuditConclusion:
        """
        If any amount >= threshold, force PENDING_HUMAN_REVIEW.
        """
        for amt in amounts:
            if amt >= self.threshold:
                return AuditConclusion.PENDING_HUMAN_REVIEW
        return current_conclusion
