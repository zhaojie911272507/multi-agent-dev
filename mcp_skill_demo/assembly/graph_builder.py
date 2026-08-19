"""
graph_builder.py —— LangGraph 动态构图（动态装配的第 3 步）

把前两步装配出的零件（技能、工具、路由）组装成一个可运行的 LangGraph：

    图结构（动态生成，配置里有什么技能，图上就有多少节点）：

        START
          │
          ▼
      router ──▶ skill_math（一个微型 Agent：LLM ⇄ ToolNode[math 工具]）
       │  │      skill_weather（同上，绑定 weather 工具）
       │  │      skill_greeting（无工具，单轮回复）
       │  └──────▶ END
       └（命中哪个技能就走哪个节点）

核心点：
    - 每个技能在运行时被编译成一个独立的"微型 Agent 子图"，
      再作为节点挂进总图 —— 即"把图组装进图"
    - 只要 yaml 配置新增技能，本文件零改动，新节点自动出现
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from .models import Skill
from .router import create_router

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel

    # 技能节点名 = "skill:" + 技能名（避免与固定节点混淆）
    SkillNodeName = str


# ----------------------------------------------------------------------------
# 图的状态定义
# ----------------------------------------------------------------------------
class AgentState(TypedDict, total=False):
    """总图状态：消息历史 + 路由结果。"""
    messages: Annotated[list, add_messages]  # 消息列表，add_messages 自动合并
    next_skill: str                          # 路由节点输出的技能名


# ----------------------------------------------------------------------------
# 1. 技能子图：为单个技能编译一个"微型 Agent"
# ----------------------------------------------------------------------------
def build_skill_agent(skill: Skill, llm: "BaseChatModel | None"):
    """
    为一个技能动态编译微型 Agent 子图：
        agent(LLM+系统提示词+绑定工具) ⇄ tools(ToolNode)
    无工具的技能（如 greeting）则退化为单轮 LLM 调用。

    Args:
        skill: 已装配好工具的技能对象
        llm:   Chat 模型。为 None 时进入"无 LLM 演示模式"——
               子图无法智能回复，agent 节点直接返回一段固定文本，
               仅用于展示动态装配的链路已经跑通（无需 API Key）。

    Returns:
        编译好的子图，可直接作为总图的节点使用。
    """
    # 该技能的 Agent 子图使用标准消息状态即可
    sub_builder = StateGraph(MessagesState)

    # --- 节点 1：模型调用（系统提示词 + 技能专属工具绑定） ---
    async def call_model(state: MessagesState, config: RunnableConfig):
        # 无 LLM 演示模式：跳过模型，直接返回固定回复，
        # 证明"路由 -> 技能节点"链路已由配置动态打通
        if llm is None:
            tool_names = [t.name for t in skill.tools]
            return {"messages": [AIMessage(
                content=(
                    f"[无 LLM 演示模式] 已路由到技能「{skill.name}」，"
                    f"该技能绑定了工具: {tool_names or '无'}。\n"
                    "配置 DEEPSEEK_API_KEY 后可体验完整智能对话。"
                )
            )]}
        # 系统提示词 + 历史消息拼接后交给 LLM
        messages = [SystemMessage(skill.system_prompt), *state["messages"]]
        # 有工具则绑定工具，让模型能够发起 tool_call；没有则不绑定
        model = llm.bind_tools(skill.tools) if skill.tools else llm
        response = await model.ainvoke(messages, config)
        return {"messages": [response]}

    # --- 节点 2：工具执行（仅当技能有工具时添加） ---
    has_tools = len(skill.tools) > 0

    def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
        """上一条消息带 tool_call -> 去执行工具；否则 -> 结束。"""
        last = state["messages"][-1]
        return "tools" if getattr(last, "tool_calls", None) else END

    sub_builder.add_node("agent", call_model)
    if has_tools:
        sub_builder.add_node("tools", ToolNode(skill.tools))
        # agent 后条件分支：需要工具就去执行，执行完回 agent 继续
        sub_builder.add_conditional_edges(
            "agent",
            should_continue,
            {"tools": "tools", END: END},
        )
        sub_builder.add_edge("tools", "agent")
    else:
        # 无工具：agent 单轮输出后直接结束
        sub_builder.add_edge("agent", END)

    sub_builder.add_edge(START, "agent")
    return sub_builder.compile()


# ----------------------------------------------------------------------------
# 2. 总图：路由节点 + 动态挂载全部技能节点
# ----------------------------------------------------------------------------
def build_dynamic_graph(
    llm: "BaseChatModel | None",
    skills: list[Skill],
):
    """
    动态构建总图：
        START -> router -> (条件边) -> skill:<name> -> END

    Args:
        llm:    Chat 模型。为 None 时路由退化为关键词匹配（无需 API Key）。
        skills: skill_loader.assemble_skills() 装配好的技能列表。
    """
    if not skills:
        raise ValueError("技能列表为空，无法构图。请检查 config/skills/ 目录。")

    # 路由实现：有 LLM 用 LLM 路由，否则关键词路由
    router = create_router(llm)
    # 兜底技能：路由失败时使用（约定最后一个无工具技能，即 greeting）
    fallback_skill = skills[-1]

    # ---- 路由节点 ----
    async def router_node(state: AgentState):
        # 取最后一条人类消息作为路由输入
        last_human = next(
            (m for m in reversed(state["messages"]) if m.type == "human"),
            None,
        )
        if last_human is None:
            return {"next_skill": fallback_skill.name}

        # 先关键词快筛：命中就直接用，省一次 LLM 调用
        chosen = next((s for s in skills if s.matches(last_human.content)), None)
        # 关键词未命中且有 LLM 时才走 LLM 路由
        if chosen is None and llm is not None:
            chosen = await router.route(skills, last_human.content)
        # 都失败 -> 兜底技能
        return {"next_skill": chosen.name if chosen else fallback_skill.name}

    # ---- 构图 ----
    builder = StateGraph(AgentState)
    builder.add_node("router", router_node)

    # 为每个技能动态添加节点 + 记录条件边映射
    # 注意：LangGraph 节点名不允许包含 ':' 等保留字符，这里用下划线连接
    skill_node_map: dict[str, str] = {}
    for skill in skills:
        node_name = f"skill_{skill.name}"          # 节点名：skill_math ...
        builder.add_node(node_name, build_skill_agent(skill, llm))
        skill_node_map[skill.name] = node_name

    # 边：START -> router -> 各技能节点 -> END
    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        "router",
        # 条件函数返回"技能名"（next_skill），
        # LangGraph 会用下面的映射表把它翻译成实际节点名
        lambda state: state["next_skill"],
        skill_node_map,  # 映射表：技能名 -> 节点名
    )
    for node_name in skill_node_map.values():
        builder.add_edge(node_name, END)

    return builder.compile(), skill_node_map
