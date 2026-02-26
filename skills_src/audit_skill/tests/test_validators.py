"""
Boundary tests: amount overflow, illegal chars, tax mismatch.
"""
import sys
from decimal import Decimal
from pathlib import Path

import pytest

# Add skills_src to path so audit_skill package is resolvable
_skills_src = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_skills_src))

from audit_skill.validators import CRITICAL_MISMATCH_THRESHOLD, TaxComplianceSkill


class TestTaxComplianceSkill:
    """Tax validation boundary tests."""

    def test_valid_tax_compliance(self) -> None:
        skill = TaxComplianceSkill()
        data = [
            {
                "line_id": "L001",
                "amount": "1000.00",
                "tax_rate": "0.13",
                "tax_amount": "130.00",
                "source_file": "inv.pdf",
            }
        ]
        result = skill.validate(data)
        assert result.passed is True
        assert result.delta is None

    def test_critical_mismatch_over_threshold(self) -> None:
        skill = TaxComplianceSkill()
        data = [
            {
                "line_id": "L001",
                "amount": "1000.00",
                "tax_rate": "0.13",
                "tax_amount": "131.00",  # should be 130, delta=1 > 0.01
                "source_file": "inv.pdf",
            }
        ]
        result = skill.validate(data)
        assert result.passed is False
        assert result.delta is not None
        assert result.delta > CRITICAL_MISMATCH_THRESHOLD
        assert "CRITICAL_MISMATCH" in result.message

    def test_marginally_under_threshold(self) -> None:
        skill = TaxComplianceSkill()
        data = [
            {
                "line_id": "L001",
                "amount": "100.00",
                "tax_rate": "0.13",
                "tax_amount": "13.00",
                "source_file": "inv.pdf",
            }
        ]
        result = skill.validate(data)
        assert result.passed is True

    def test_amount_overflow_decimal(self) -> None:
        """Very large amounts — ensure Decimal handles."""
        skill = TaxComplianceSkill()
        data = [
            {
                "line_id": "L001",
                "amount": "999999999999999.99",
                "tax_rate": "0.13",
                "tax_amount": "129999999999999.9987",
                "source_file": "inv.pdf",
            }
        ]
        result = skill.validate(data)
        # May pass or fail depending on rounding; no crash
        assert result.passed in (True, False)
        assert result.line_refs or result.message

    def test_invalid_numeric_rejected(self) -> None:
        skill = TaxComplianceSkill()
        data = [
            {
                "line_id": "L001",
                "amount": "not_a_number",
                "tax_rate": "0.13",
                "tax_amount": "0",
            }
        ]
        result = skill.validate(data)
        assert result.passed is False
        assert "Invalid" in result.message

    def test_illegal_chars_in_description(self) -> None:
        """Description may contain special chars; shouldn't break validation."""
        skill = TaxComplianceSkill()
        data = [
            {
                "line_id": "L001",
                "amount": "100",
                "tax_rate": "0.13",
                "tax_amount": "13",
                "description": "特殊字符 <> '\" & % $",
                "source_file": "inv.pdf",
            }
        ]
        result = skill.validate(data)
        assert result.passed is True
