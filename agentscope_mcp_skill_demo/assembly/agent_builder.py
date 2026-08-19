# -*- coding: utf-8 -*-
"""Agent 组装器：把 MCP 工具、技能、模型动态组装成可对话的 Agent。

这是“动态组装”的收口环节：所有资源（MCP 客户端、技能目录、
模型）在此汇入一个 :class:`Toolkit`，再交给 :class:`Agent`。
"""

import os

from agentscope.agent import Agent
from agentscope.credential import DeepSeekCredential
from agentscope.model import DeepSeekChatModel
from agentscope.mcp import MCPClient
from agentscope.permission import (
    PermissionBehavior,
    PermissionMode,
    PermissionRule,
)
from agentscope.state import AgentState
from agentscope.tool import Toolkit


def create_model() -> DeepSeekChatModel:
    """创建 DeepSeek 对话模型（读取仓库根目录 .env 中的 DEEPSEEK_API_KEY）。

    AgentScope 2.x 不再提供 init_chat_model 快捷函数，
    需要按厂商直接实例化对应的模型类（如 DeepSeekChatModel）。
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "缺少 DEEPSEEK_API_KEY，请确保仓库根目录 .env 已配置",
        )

    # DeepSeekChatModel 需要 credential（API Key）和模型名；
    # parameters 控制生成参数（max_tokens 等）
    return DeepSeekChatModel(
        credential=DeepSeekCredential(api_key=api_key),
        model="deepseek-chat",
        parameters=DeepSeekChatModel.Parameters(max_tokens=2048),
    )


async def build_agent(
    *,
    name: str,
    system_prompt: str,
    mcps: list[MCPClient],
    skills_dir: str,
    auto_confirm_tools: bool = True,
) -> Agent:
    """动态组装 Agent。

    Args:
        name: 智能体名称
        system_prompt: 系统提示词
        mcps: 已连接好的 MCPClient 列表（由 MCPManager 产出）
        skills_dir: 技能目录路径（框架会自动用 LocalSkillLoader 加载）
        auto_confirm_tools: 为 True 时：
            1. 权限模式设为 DONT_ASK（不逐次询问用户）；
            2. 为组装进来的每个 MCP 工具注册 allow 规则——
               MCP 工具默认权限是 ASK（必须人工确认），无人确认时
               会被拒绝，因此需要显式放行（见下方注释）。
            False 则每次工具调用都等待用户确认。

    Returns:
        组装完成的 Agent 实例
    """
    # ------------------------------------------------------------------
    # 1) 组装 Toolkit：本示例的全部能力都汇聚在这里
    # ------------------------------------------------------------------
    toolkit = Toolkit(
        # mcps：直接注册 MCP 客户端，其工具会自动暴露给智能体，
        #       工具名格式为 mcp__{客户端名}__{工具名}
        mcps=mcps,
        # skills_or_loaders：技能目录字符串 / Skill / SkillLoaderBase 均可
        #       框架内部会自动创建 LocalSkillLoader 扫描目录下的 SKILL.md
        skills_or_loaders=[skills_dir],
    )

    # ------------------------------------------------------------------
    # 2) 组装 Agent：toolkit 是工具/技能的唯一来源
    # ------------------------------------------------------------------
    state = AgentState()  # 智能体状态（记忆、上下文、权限上下文都在这里）
    if auto_confirm_tools:
        # 默认权限模式 DEFAULT 下，每次工具调用都会向用户确认；
        # 演示场景改为 DONT_ASK，让流程自动跑完
        state.permission_context.mode = PermissionMode.DONT_ASK

        # 关键：MCP 工具的默认权限是 ASK（要求人工确认），DONT_ASK
        # 模式下无人确认会直接拒绝调用。因此对每个 MCP 工具动态注册
        # 一条 allow 规则（rule_content=None 表示匹配该工具的所有调用）。
        # 规则是从「实际组装好的工具」推导出来的，天然保持动态一致。
        for client in mcps:
            for tool in await client.list_tools():
                state.permission_context.allow_rules[tool.name] = [
                    PermissionRule(
                        tool_name=tool.name,
                        rule_content=None,  # None = 匹配所有调用
                        behavior=PermissionBehavior.ALLOW,
                        source="dynamic-demo",
                    ),
                ]

    agent = Agent(
        name=name,
        system_prompt=system_prompt,
        model=create_model(),
        toolkit=toolkit,
        state=state,
    )
    return agent
