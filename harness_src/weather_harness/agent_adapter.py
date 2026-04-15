from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentRunResult:
    """Normalized result from a single agent invocation."""

    final_answer: str
    tool_called: bool
    message_count: int
    raw_messages: list[Any]


def _message_content(message: Any) -> str:
    if isinstance(message, dict):
        content = message.get("content", "")
    else:
        content = getattr(message, "content", "")
    if content is None:
        return ""
    return str(content)


def _message_tool_calls(message: Any) -> Any:
    if isinstance(message, dict):
        return message.get("tool_calls")
    return getattr(message, "tool_calls", None)


def _message_name(message: Any) -> str:
    if isinstance(message, dict):
        return str(message.get("name", ""))
    return str(getattr(message, "name", ""))


def _extract_messages(payload: Any) -> list[Any]:
    if isinstance(payload, dict):
        messages = payload.get("messages", [])
    else:
        messages = getattr(payload, "messages", [])

    if messages is None:
        return []
    return list(messages)


def run_agent_once(agent: Any, prompt: str) -> AgentRunResult:
    """Invoke an agent once and normalize the output for evaluation."""

    response = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    messages = _extract_messages(response)
    if not messages:
        return AgentRunResult(final_answer="", tool_called=False, message_count=0, raw_messages=[])

    final_answer = _message_content(messages[-1]).strip()
    tool_called = any(_message_tool_calls(message) for message in messages)
    tool_called = tool_called or any(_message_name(message) == "get_weather" for message in messages)

    return AgentRunResult(
        final_answer=final_answer,
        tool_called=tool_called,
        message_count=len(messages),
        raw_messages=messages,
    )

