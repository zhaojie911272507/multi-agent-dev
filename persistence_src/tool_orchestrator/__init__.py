"""
Tool Orchestrator: 精准工具调用与状态记忆管理模块。

基于 LangGraph 编排 Skills 与 MCP 工具，集成：
- 工具路由（ToolNode）
- 对话状态持久化（Checkpointer / thread_id）
- 可选语义记忆（Store）
"""

from .agent_graph import build_orchestrator_graph
from .tool_registry import build_tools
from .memory_integration import build_memory_context
from .state_schema import ExtendedOrchestratorState

__all__ = [
    "create_orchestrator",
    "build_orchestrator_graph",
    "build_tools",
    "build_memory_context",
    "ExtendedOrchestratorState",
]


async def create_orchestrator(
    mcp_servers: dict | None = None,
    enable_audit_skill: bool = False,
    model_id: str = "deepseek-chat",
    store=None,
    memory_namespace: tuple[str, ...] | None = None,
    short_term_store=None,
    long_term_store=None,
    checkpointer=None,
):
    """
    创建编排器：构建 tools + 编译 LangGraph 图。

    Args:
        mcp_servers: MCP 服务器配置，例如 {"math": {"command": "python", "args": [...], "transport": "stdio"}}
        enable_audit_skill: 是否启用 financial-audit Skill
        model_id: 聊天模型 ID，如 deepseek-chat
        store: 语义记忆 Store（如 InMemoryStore），可选
        memory_namespace: Store 命名空间，如 (user_id, "memories")
        short_term_store: ShortTermMemoryStore（SQLite），可选
        long_term_store: LongTermMemoryStore（memory/*.md），可选
        checkpointer: 状态持久化器，可选；默认使用 MemorySaver

    Returns:
        编译后的 graph，支持 invoke/ainvoke/stream；调用时需传入 config={"configurable": {"thread_id": "...", "user_id": "..."}}
    """
    from langchain.chat_models import init_chat_model

    tools = await build_tools(
        mcp_servers=mcp_servers or {},
        enable_audit_skill=enable_audit_skill,
    )
    llm = init_chat_model(model_id)
    return build_orchestrator_graph(
        tools=tools,
        llm=llm,
        checkpointer=checkpointer,
        store=store,
        memory_namespace=memory_namespace,
        short_term_store=short_term_store,
        long_term_store=long_term_store,
    )
