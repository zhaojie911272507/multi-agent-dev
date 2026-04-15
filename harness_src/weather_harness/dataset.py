from __future__ import annotations

from .evaluator import EvalCase


def default_cases() -> list[EvalCase]:
    return [
        EvalCase(
            case_id="sf-weather",
            input_text="what is the weather in sf",
            expected_city_aliases=("sf", "san francisco"),
            expected_keywords=("sunny",),
        ),
        EvalCase(
            case_id="ny-weather",
            input_text="what is the weather in new york",
            expected_city_aliases=("new york", "ny", "nyc"),
            expected_keywords=("sunny",),
        ),
        EvalCase(
            case_id="tokyo-weather",
            input_text="weather in tokyo please",
            expected_city_aliases=("tokyo",),
            expected_keywords=("sunny",),
        ),
    ]

