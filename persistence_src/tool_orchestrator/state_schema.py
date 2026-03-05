"""
State Schema: 扩展 LangGraph 状态，支持工具调用追踪与语义记忆上下文。

在 MessagesState 基础上增加：
- tool_call_trace: 工具调用历史（用于审计、重试、复盘）
- memory_context: 从 Store 检索得到的用户偏好/上下文（注入 LLM prompt）
"""

import operator
from typing import Annotated, Any

from langgraph.graph import MessagesState


# ---------------------------------------------------------------------------
# 工具调用记录（可选，用于可观测性与回溯）
# ---------------------------------------------------------------------------


class ToolCallRecord:
    """单次工具调用的记录。"""

    def __init__(
        self,
        tool_name: str,
        args: dict[str, Any],
        result: str | None = None,
        error: str | None = None,
    ):
        self.tool_name = tool_name
        self.args = args
        self.result = result
        self.error = error


# ---------------------------------------------------------------------------
# 扩展状态（可选扩展，默认沿用 MessagesState）
# ---------------------------------------------------------------------------


def extend_messages_state():
    """
    返回扩展的 MessagesState，包含 tool_call_trace、memory_context。
    若不需要扩展，可直接使用 MessagesState。
    """

    class ExtendedState(MessagesState):
        # 工具调用追踪：每次 ToolNode 执行后追加（可选，用于审计）
        tool_call_trace: Annotated[list[dict], operator.add] = []
        # 语义记忆上下文：从 Store 检索后注入
        memory_context: str | None = None

    return ExtendedState


# 默认导出：项目内大多数场景仅需 MessagesState，扩展状态按需使用
ExtendedOrchestratorState = extend_messages_state()
