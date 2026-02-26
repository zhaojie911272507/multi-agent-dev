"""
Orchestrates full audit flow: desensitize → validators → AI → circuit breaker.
No intermediate persistence; AuditTrail only.
"""
from decimal import Decimal
from typing import Any

from .ai_analyzer import ContractConsistencySkill, with_desensitized_input
from .circuit_breaker import CircuitBreaker, build_audit_trail
from .desensitizer import desensitize_dict
from .models import AuditConclusion, AuditTrail, LineRef
from .validators import TaxComplianceSkill


async def run_audit(
    invoice_data: dict[str, Any] | list[dict[str, Any]],
    contract_data: dict[str, Any] | str | None = None,
    payment_data: dict[str, Any] | str | None = None,
    llm_invoke_fn: Any | None = None,
    amount_threshold: Decimal | None = None,
) -> tuple[AuditConclusion, AuditTrail]:
    """
    Full three-way reconciliation flow.
    1. Desensitize all inputs (logic isolation)
    2. Tax compliance (hard rule)
    3. Contract consistency (soft, if contract/payment provided)
    4. Circuit breaker (amount > threshold)
    5. Build AuditTrail; do NOT persist intermediates.
    """
    source_files: list[str] = []
    line_refs: list[LineRef] = []
    reasoning_path: list[str] = []

    # 1. Desensitize
    if isinstance(invoice_data, list):
        inv_desensitized: list[dict[str, Any]] = [desensitize_dict(x) for x in invoice_data]
        for item in inv_desensitized:
            if isinstance(item, dict) and item.get("source_file"):
                source_files.append(item["source_file"])
    else:
        inv_desensitized = [desensitize_dict(invoice_data)]
        if isinstance(invoice_data, dict) and invoice_data.get("source_file"):
            source_files.append(invoice_data["source_file"])
    reasoning_path.append("Desensitized invoice data")

    # 2. Tax compliance
    tax_skill = TaxComplianceSkill()
    tax_result = tax_skill.validate(inv_desensitized)
    reasoning_path.append(f"Tax compliance: {'PASS' if tax_result.passed else 'FAIL'}")

    if not tax_result.passed:
        trail = build_audit_trail(
            AuditConclusion.CRITICAL_MISMATCH,
            source_files,
            tax_result.line_refs,
            reasoning_path,
            {"tax_result": tax_result.model_dump()},
        )
        return AuditConclusion.CRITICAL_MISMATCH, trail

    line_refs.extend(tax_result.line_refs)

    # Collect amounts for circuit breaker
    amounts: list[Decimal] = []
    lines = inv_desensitized if isinstance(inv_desensitized, list) else [inv_desensitized]
    for line in lines:
        if isinstance(line, dict):
            amt = line.get("amount")
            if amt is not None:
                try:
                    amounts.append(Decimal(str(amt)))
                except Exception:
                    pass

    # 3. Contract consistency (if provided)
    conclusion = AuditConclusion.PASS
    if contract_data is not None and payment_data is not None:
        contract_txt, payment_txt = with_desensitized_input(contract_data, payment_data)
        consistency_skill = ContractConsistencySkill(llm_invoke_fn=llm_invoke_fn)
        consistency_result = await consistency_skill.analyze_async(
            contract_txt, payment_txt, source_files=["contract", "payment"]
        )
        reasoning_path.append(
            f"Contract consistency: confidence={consistency_result.confidence}"
        )
        line_refs.extend(consistency_result.line_refs)

        if consistency_result.requires_human_review:
            conclusion = AuditConclusion.PENDING_HUMAN_REVIEW

    # 4. Circuit breaker
    breaker = CircuitBreaker(threshold=amount_threshold)
    conclusion = breaker.apply(amounts, conclusion)
    if conclusion == AuditConclusion.PENDING_HUMAN_REVIEW:
        reasoning_path.append("Circuit breaker: amount >= threshold")

    trail = build_audit_trail(
        conclusion,
        source_files,
        line_refs,
        reasoning_path,
        {},
    )
    return conclusion, trail
