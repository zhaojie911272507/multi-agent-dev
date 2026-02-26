"""
Hard rules: tax compliance, blacklist filtering.
NO AI estimation — all math via decimal.Decimal.
"""
from decimal import Decimal, InvalidOperation
from typing import Any

from .models import (
    InvoiceLine,
    LineRef,
    TaxComplianceResult,
)

# Critical threshold: difference > $0.01 → CRITICAL_MISMATCH
CRITICAL_MISMATCH_THRESHOLD = Decimal("0.01")

# Default tax rates by region (configurable)
DEFAULT_TAX_RATES: dict[str, Decimal] = {
    "CN": Decimal("0.13"),   # 13% VAT
    "CN_SMALL": Decimal("0.03"),  # 3% small-scale
    "US": Decimal("0.00"),   # Varies by state; use explicit
    "DEFAULT": Decimal("0.13"),
}


class TaxComplianceSkill:
    """
    Validates invoice tax against region config.
    If delta > $0.01 → CRITICAL_MISMATCH, halt.
    """

    def __init__(
        self,
        region: str = "CN",
        tax_rates: dict[str, Decimal] | None = None,
    ) -> None:
        self.region = region
        self.tax_rates = tax_rates or DEFAULT_TAX_RATES

    def validate(
        self,
        invoice_data: dict[str, Any] | list[dict[str, Any]],
    ) -> TaxComplianceResult:
        """
        Input MUST be structured JSON.
        Returns TaxComplianceResult; raises/halts on CRITICAL_MISMATCH.
        """
        lines = self._normalize_to_lines(invoice_data)
        line_refs: list[LineRef] = []
        for line in lines:
            try:
                inv_line = InvoiceLine(
                    line_id=line.get("line_id", ""),
                    amount=Decimal(str(line.get("amount", 0))),
                    tax_rate=Decimal(str(line.get("tax_rate", 0))),
                    tax_amount=Decimal(str(line.get("tax_amount", 0))),
                    description=line.get("description", ""),
                    source_file=line.get("source_file", ""),
                )
            except (ValueError, KeyError, InvalidOperation) as e:
                return TaxComplianceResult(
                    passed=False,
                    line_refs=line_refs,
                    message=f"Invalid invoice line: {e}",
                )

            expected_tax = inv_line.amount * inv_line.tax_rate
            delta = abs(inv_line.tax_amount - expected_tax)

            if delta > CRITICAL_MISMATCH_THRESHOLD:
                return TaxComplianceResult(
                    passed=False,
                    delta=delta,
                    line_refs=[
                        *line_refs,
                        LineRef(
                            line_id=inv_line.line_id,
                            source_file=inv_line.source_file,
                            field_name="tax_amount",
                        ),
                    ],
                    message=f"CRITICAL_MISMATCH: tax delta {delta} > {CRITICAL_MISMATCH_THRESHOLD}",
                )
            line_refs.append(
                LineRef(
                    line_id=inv_line.line_id,
                    source_file=inv_line.source_file,
                )
            )

        return TaxComplianceResult(
            passed=True,
            line_refs=line_refs,
            message="Tax compliance OK",
        )

    def _normalize_to_lines(
        self,
        data: dict[str, Any] | list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if isinstance(data, list):
            return data
        if "lines" in data:
            return data["lines"]
        return [data]


# Blacklist supplier IDs (extend via config)
DEFAULT_BLACKLIST: set[str] = set()


class BlacklistSupplierFilter:
    """Filter out blacklisted suppliers — hard rule."""

    def __init__(self, blacklist: set[str] | None = None) -> None:
        self.blacklist = blacklist or DEFAULT_BLACKLIST

    def is_blocked(self, supplier_id: str) -> bool:
        return supplier_id.strip() in self.blacklist

    def filter_lines(
        self,
        lines: list[dict[str, Any]],
        supplier_field: str = "supplier_id",
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Returns (allowed, blocked)."""
        allowed, blocked = [], []
        for line in lines:
            sid = str(line.get(supplier_field, "")).strip()
            if self.is_blocked(sid):
                blocked.append(line)
            else:
                allowed.append(line)
        return allowed, blocked
