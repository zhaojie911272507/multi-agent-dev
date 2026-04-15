from harness_src.weather_harness.agent_adapter import AgentRunResult, run_agent_once
from harness_src.weather_harness.evaluator import EvalCase, evaluate_case, evaluate_cases


class FakeAgent:
    def __init__(self, response):
        self.response = response

    def invoke(self, payload):
        self.payload = payload
        return self.response


def test_run_agent_once_extracts_tool_usage_and_final_answer():
    agent = FakeAgent(
        {
            "messages": [
                {"role": "assistant", "content": "", "tool_calls": [{"name": "get_weather"}]},
                {"role": "tool", "name": "get_weather", "content": "It's always sunny in sf!"},
                {"role": "assistant", "content": "The weather in SF is sunny."},
            ]
        }
    )

    result = run_agent_once(agent, "what is the weather in sf")

    assert result.final_answer == "The weather in SF is sunny."
    assert result.tool_called is True
    assert result.message_count == 3
    assert agent.payload == {"messages": [{"role": "user", "content": "what is the weather in sf"}]}


def test_evaluate_case_passes_for_expected_city_keyword_and_tool_call():
    case = EvalCase(
        case_id="sf-weather",
        input_text="what is the weather in sf",
        expected_city_aliases=("sf", "san francisco"),
        expected_keywords=("sunny",),
    )
    result = AgentRunResult(
        final_answer="The weather in San Francisco is sunny.",
        tool_called=True,
        message_count=3,
        raw_messages=[],
    )

    scored = evaluate_case(case, result)

    assert scored.passed is True
    assert scored.score == 1.0
    assert scored.notes == "ok"


def test_evaluate_case_does_not_match_city_inside_other_words():
    case = EvalCase(
        case_id="ny-weather",
        input_text="what is the weather in new york",
        expected_city_aliases=("new york", "ny", "nyc"),
        expected_keywords=("sunny",),
    )
    result = AgentRunResult(
        final_answer="The weather is sunny.",
        tool_called=True,
        message_count=2,
        raw_messages=[],
    )

    scored = evaluate_case(case, result)

    assert scored.passed is False
    assert scored.notes == "city_not_mentioned"


def test_evaluate_cases_requires_matching_lengths():
    case = EvalCase(
        case_id="sf-weather",
        input_text="what is the weather in sf",
        expected_city_aliases=("sf",),
        expected_keywords=("sunny",),
    )

    try:
        evaluate_cases([case], [])
    except ValueError as exc:
        assert "same length" in str(exc)
    else:
        raise AssertionError("expected ValueError")
