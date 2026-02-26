"""
Circuit breaker and amount threshold tests.
"""
import sys
from decimal import Decimal
from pathlib import Path

import pytest

_skills_src = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_skills_src))

from audit_skill.circuit_breaker import (
    AMOUNT_THRESHOLD,
    CircuitBreaker,
    check_amount_breach,
)


class TestCircuitBreaker:
    def test_amount_under_threshold(self) -> None:
        assert check_amount_breach(Decimal("99999")) is False
        assert check_amount_breach(Decimal("50000")) is False

    def test_amount_at_threshold(self) -> None:
        assert check_amount_breach(AMOUNT_THRESHOLD) is True
        assert check_amount_breach(Decimal("100000")) is True

    def test_amount_over_threshold(self) -> None:
        assert check_amount_breach(Decimal("100001")) is True
        assert check_amount_breach(Decimal("1000000")) is True

    def test_breaker_force_pending_review(self) -> None:
        from audit_skill.models import AuditConclusion

        breaker = CircuitBreaker()
        result = breaker.apply(
            [Decimal("150000")],
            AuditConclusion.PASS,
        )
        assert result == AuditConclusion.PENDING_HUMAN_REVIEW

    def test_breaker_preserves_pass_when_under(self) -> None:
        from audit_skill.models import AuditConclusion

        breaker = CircuitBreaker()
        result = breaker.apply(
            [Decimal("50000"), Decimal("20000")],
            AuditConclusion.PASS,
        )
        assert result == AuditConclusion.PASS
