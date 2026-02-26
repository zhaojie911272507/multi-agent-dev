"""
Soft logic: ContractConsistencySkill — LLM semantic alignment.
Confidence < 85 → require human review.
"""
from typing import Any

from .desensitizer import desensitize_dict, sanitize_for_llm
from .models import ContractConsistencyResult, LineRef

# Minimum confidence for auto-pass
MIN_CONFIDENCE = 85


class ContractConsistencySkill:
    """
    Uses LLM to extract payment terms from contract and compare
    with actual payment application. Semantic match: e.g. "按进度支付" vs "项目报告".
    """

    def __init__(self, llm_invoke_fn: Any | None = None) -> None:
        """
        llm_invoke_fn: optional callable(prompt: str) -> str
        If None, uses stub that returns low confidence (safe default).
        """
        self._llm = llm_invoke_fn

    async def analyze_async(
        self,
        contract_text: str,
        payment_application_text: str,
        source_files: list[str] | None = None,
    ) -> ContractConsistencyResult:
        """Async analysis; contract and payment_app must be desensitized before call."""
        contract_safe = sanitize_for_llm(contract_text)
        payment_safe = sanitize_for_llm(payment_application_text)

        if self._llm is None:
            return ContractConsistencyResult(
                confidence=0,
                requires_human_review=True,
                reasoning="LLM not configured; manual review required.",
                line_refs=[
                    LineRef(line_id="contract", source_file=sf or "contract")
                    for sf in (source_files or ["contract"])
                ],
            )

        prompt = self._build_prompt(contract_safe, payment_safe)
        raw_response = await self._call_llm(prompt)
        return self._parse_response(raw_response, source_files or [])

    def analyze_sync(
        self,
        contract_text: str,
        payment_application_text: str,
        source_files: list[str] | None = None,
    ) -> ContractConsistencyResult:
        """Sync fallback; prefer analyze_async for production."""
        contract_safe = sanitize_for_llm(contract_text)
        payment_safe = sanitize_for_llm(payment_application_text)

        if self._llm is None:
            return ContractConsistencyResult(
                confidence=0,
                requires_human_review=True,
                reasoning="LLM not configured; manual review required.",
                line_refs=[
                    LineRef(line_id="contract", source_file=sf or "contract")
                    for sf in (source_files or ["contract"])
                ],
            )

        prompt = self._build_prompt(contract_safe, payment_safe)
        raw_response = self._call_llm_sync(prompt)
        return self._parse_response(raw_response, source_files or [])

    def _build_prompt(self, contract: str, payment_app: str) -> str:
        return f"""You are a financial auditor. Compare the contract payment terms with the actual payment application.

## Contract (payment terms)
{contract[:8000]}

## Payment Application
{payment_app[:8000]}

## Task
1. Extract payment terms from the contract (e.g. "按进度支付", "milestone-based").
2. Check if the payment application aligns with those terms (e.g. submitted report matches milestone).
3. Respond in this exact format:
CONFIDENCE: <0-100 integer>
REASONING: <brief explanation>
"""

    async def _call_llm(self, prompt: str) -> str:
        if callable(self._llm):
            # Assume async if it's a coroutine
            import asyncio
            result = self._llm(prompt)
            if asyncio.iscoroutine(result):
                return await result
            return str(result)
        return ""

    def _call_llm_sync(self, prompt: str) -> str:
        if callable(self._llm):
            result = self._llm(prompt)
            return str(result)
        return ""

    def _parse_response(
        self,
        raw: str,
        source_files: list[str],
    ) -> ContractConsistencyResult:
        confidence = 0
        reasoning = raw

        for line in raw.strip().split("\n"):
            if line.upper().startswith("CONFIDENCE:"):
                try:
                    confidence = int(line.split(":", 1)[1].strip())
                    confidence = max(0, min(100, confidence))
                except (ValueError, IndexError):
                    pass
            elif line.upper().startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()

        return ContractConsistencyResult(
            confidence=confidence,
            requires_human_review=confidence < MIN_CONFIDENCE,
            reasoning=reasoning,
            line_refs=[
                LineRef(line_id=f"src_{i}", source_file=sf)
                for i, sf in enumerate(source_files)
            ],
        )


def with_desensitized_input(
    contract_data: dict[str, Any] | str,
    payment_data: dict[str, Any] | str,
) -> tuple[str, str]:
    """
    Desensitize before passing to LLM.
    Returns (contract_text, payment_text) for analyzer.
    """
    if isinstance(contract_data, dict):
        contract_text = str(desensitize_dict(contract_data))
    else:
        contract_text = str(contract_data)

    if isinstance(payment_data, dict):
        payment_text = str(desensitize_dict(payment_data))
    else:
        payment_text = str(payment_data)

    return contract_text, payment_text
