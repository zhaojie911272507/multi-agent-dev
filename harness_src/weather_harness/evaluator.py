from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from .agent_adapter import AgentRunResult


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    input_text: str
    expected_city_aliases: tuple[str, ...]
    expected_keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvalResult:
    case_id: str
    passed: bool
    score: float
    actual_answer: str
    tool_called: bool
    notes: str


def _normalize_text(value: str) -> str:
    return " ".join(value.lower().split())


def _contains_any(text: str, candidates: Iterable[str]) -> bool:
    return any(
        candidate and re.search(rf"(?<!\w){re.escape(candidate)}(?!\w)", text) is not None
        for candidate in candidates
    )


def evaluate_case(case: EvalCase, run_result: AgentRunResult) -> EvalResult:
    answer = _normalize_text(run_result.final_answer)
    city_hit = _contains_any(answer, (_normalize_text(alias) for alias in case.expected_city_aliases))
    keyword_hits = [keyword for keyword in case.expected_keywords if _normalize_text(keyword) in answer]

    score_parts = 0.0
    notes: list[str] = []

    if city_hit:
        score_parts += 0.5
    else:
        notes.append("city_not_mentioned")

    if keyword_hits:
        score_parts += 0.25 * len(keyword_hits)
    else:
        notes.append("missing_expected_keywords")

    if run_result.tool_called:
        score_parts += 0.25
    else:
        notes.append("tool_not_called")

    score = min(score_parts, 1.0)
    passed = city_hit and bool(keyword_hits) and run_result.tool_called

    return EvalResult(
        case_id=case.case_id,
        passed=passed,
        score=score,
        actual_answer=run_result.final_answer,
        tool_called=run_result.tool_called,
        notes=";".join(notes) if notes else "ok",
    )


def evaluate_cases(cases: list[EvalCase], run_results: list[AgentRunResult]) -> list[EvalResult]:
    if len(cases) != len(run_results):
        raise ValueError("cases and run_results must have the same length")
    return [evaluate_case(case, result) for case, result in zip(cases, run_results)]
