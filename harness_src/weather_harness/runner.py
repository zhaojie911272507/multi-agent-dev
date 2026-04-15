from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .agent_adapter import AgentRunResult, run_agent_once
from .dataset import default_cases
from .evaluator import EvalResult, evaluate_cases


def _build_agent() -> Any:
    from langgraph_src.prebuilt_agent.weather_agent import build_weather_agent

    return build_weather_agent()


def run_harness(agent: Any | None = None) -> list[EvalResult]:
    resolved_agent = agent or _build_agent()
    cases = default_cases()
    run_results = [run_agent_once(resolved_agent, case.input_text) for case in cases]
    return evaluate_cases(cases, run_results)


def _print_summary(results: list[EvalResult]) -> None:
    total = len(results)
    passed = sum(1 for result in results if result.passed)
    average_score = sum(result.score for result in results) / total if total else 0.0

    print(f"cases={total} passed={passed} failed={total - passed} average_score={average_score:.2f}")
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.case_id} score={result.score:.2f} notes={result.notes}")
        print(f"  answer: {result.actual_answer}")


def _write_output(path: Path, results: list[EvalResult]) -> None:
    payload = {
        "results": [asdict(result) for result in results],
        "summary": {
            "total": len(results),
            "passed": sum(1 for result in results if result.passed),
            "failed": sum(1 for result in results if not result.passed),
            "average_score": sum(result.score for result in results) / len(results) if results else 0.0,
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the weather agent harness.")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON file for results.")
    args = parser.parse_args(argv)

    results = run_harness()
    _print_summary(results)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        _write_output(args.output, results)
        print(f"wrote={args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

