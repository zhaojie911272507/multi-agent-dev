"""
Agent Graph: 基于 LangGraph 构建工具编排图，集成精准工具调用与状态记忆。

流程：
  1. call_model: LLM 决策，可输出 tool_calls
  2. should_continue: 若有 tool_calls -> tools，否则 END
  3. tools: ToolNode 执行 skills + MCP 工具
  4. 循环回 call_model 直至无 tool_calls
  5. Checkpointer 按 thread_id 持久化对话状态
  6. 可选 Store 注入语义记忆
"""

from typing import Any, Literal

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# ---------------------------------------------------------------------------
# 路由逻辑：根据最后一条消息是否包含 tool_calls 决定走向
# ---------------------------------------------------------------------------


def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
    """
    若最后一条 AI 消息包含 tool_calls，则进入 tools 节点；否则结束。
    """
    messages = state["messages"]
    if not messages:
        return "__end__"

    last = messages[-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "__end__"


# ---------------------------------------------------------------------------
# 构建编排图
# ---------------------------------------------------------------------------


# 默认 system prompt：引导 LLM 在收到工具结果后直接给出最终答案，避免反复调用工具
DEFAULT_SYSTEM_PROMPT = """你是助手，可以调用工具完成任务。
重要：当你已获得工具返回结果后，请直接基于结果给出最终答复，不要再调用工具。"""


def build_orchestrator_graph(
    tools: list,
    llm: Any,
    checkpointer: Any | None = None,
    store: Any | None = None,
    memory_namespace: tuple[str, ...] | None = None,
    short_term_store: Any | None = None,
    long_term_store: Any | None = None,
    system_prompt: str | None = None,
) -> Any:
    """
    构建带工具调用与可选语义记忆的 LangGraph 图。

    Args:
        tools: LangChain 工具列表（来自 tool_registry.build_tools）
        llm: 聊天模型（如 init_chat_model("deepseek-chat")）
        checkpointer: 状态持久化器，如 MemorySaver()；为 None 则不持久化
        store: 语义记忆 Store（如 InMemoryStore）；与 sqlite 二选一
        memory_namespace: Store 检索的命名空间，如 (user_id, "memories")
        short_term_store: ShortTermMemoryStore（SQLite 短期记忆），可选
        long_term_store: LongTermMemoryStore（memory/*.md 长期记忆），可选
        system_prompt: 系统提示，默认引导模型在获工具结果后直接答复，避免反复调用

    调用时 config 需含 thread_id；若用 sqlite 记忆，建议含 user_id。
    建议 config 中设置 recursion_limit（默认 25）防止循环过深。
    """
    sys_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
    model_with_tools = llm.bind_tools(tools)
    tool_node = ToolNode(tools)

    async def call_model(state: MessagesState, config: RunnableConfig):
        messages = state["messages"]
        conf = (config or {}).get("configurable") or {}
        thread_id = conf.get("thread_id")
        user_id = conf.get("user_id", thread_id)

        mem_ctx = ""

        # 1. 语义 Store（InMemoryStore 等）
        if store and memory_namespace and messages:
            from .memory_integration import build_memory_context

            last_user = None
            for m in reversed(messages):
                if hasattr(m, "content") and isinstance(m.content, str):
                    last_user = m.content
                    break
            if last_user:
                mem_ctx = build_memory_context(store, memory_namespace, query=last_user, limit=3)

        # 2. SQLite 短期 + MD 长期
        if not mem_ctx and (short_term_store or long_term_store):
            from .memory_integration import build_memory_context_from_sqlite

            mem_ctx = build_memory_context_from_sqlite(
                short_term_store=short_term_store,
                long_term_store=long_term_store,
                thread_id=thread_id,
                user_id=user_id,
            )

        from langchain_core.messages import SystemMessage

        # 始终注入 system prompt，减少 LLM 反复调用工具
        base = [SystemMessage(content=sys_prompt)]
        if mem_ctx:
            base.append(SystemMessage(content=mem_ctx))
        enhanced = base + list(messages)
        response = await model_with_tools.ainvoke(enhanced)

        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", should_continue)
    builder.add_edge("tools", "call_model")

    return builder.compile(checkpointer=checkpointer or MemorySaver())
