"""
Data models for financial audit — immutable, typed, traceable.
"""
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class AuditConclusion(str, Enum):
    PASS = "PASS"
    CRITICAL_MISMATCH = "CRITICAL_MISMATCH"
    PENDING_HUMAN_REVIEW = "PENDING_HUMAN_REVIEW"


class LineRef(BaseModel):
    """Reference to original data for traceability."""
    line_id: str
    source_file: str
    field_name: str | None = None


class InvoiceLine(BaseModel):
    """Structured invoice line — must use Decimal for precision."""
    line_id: str
    amount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    description: str = ""
    source_file: str = ""

    @field_validator("amount", "tax_rate", "tax_amount", mode="before")
    @classmethod
    def ensure_decimal(cls, v: Any) -> Decimal:
        if isinstance(v, Decimal):
            return v
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        raise ValueError("Must be numeric")


class TaxComplianceResult(BaseModel):
    passed: bool
    delta: Decimal | None = None
    line_refs: list[LineRef] = Field(default_factory=list)
    message: str = ""


class ContractConsistencyResult(BaseModel):
    confidence: int = Field(ge=0, le=100)
    requires_human_review: bool = False
    reasoning: str = ""
    line_refs: list[LineRef] = Field(default_factory=list)


class AuditTrail(BaseModel):
    """Audit decision chain — immutable, for compliance."""
    audit_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = ""  # ISO8601
    source_files: list[str] = Field(default_factory=list)
    line_refs: list[LineRef] = Field(default_factory=list)
    reasoning_path: list[str] = Field(default_factory=list)
    conclusion: AuditConclusion = AuditConclusion.PASS
    details: dict[str, Any] = Field(default_factory=dict)
