"""
main.py —— 示例入口：编排完整的"动态组装 + 运行"流程

流程一览（三步组装 + 交互运行）：
    Step 1  读配置        config_loader  ->  MCP 注册表 + 技能定义
    Step 2  动态连接 MCP  MCPManager     ->  {服务器名: [工具]}
    Step 3  动态构图      GraphBuilder   ->  编译好的 LangGraph
    Step 4  交互运行      循环读取用户输入并调用图

运行：cd mcp_skill_demo && python run_demo.py
      （run_demo.py 只是薄封装，真正逻辑都在这里）
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from .config_loader import load_mcp_config, load_skill_defs
from .graph_builder import build_dynamic_graph
from .mcp_manager import MCPManager
from .skill_loader import assemble_skills

if TYPE_CHECKING:  # 仅用于类型标注
    from langchain_core.language_models.chat_models import BaseChatModel

# 演示用示例问题：用于演示如何触发各个技能
SAMPLE_QUESTIONS = [
    "你好呀",
    "帮我计算 (3 + 5) × 12",
    "北京天气怎么样？",
    "你会做什么？",
]


def create_llm() -> "BaseChatModel | None":
    """
    创建 LLM 实例；未配置 DEEPSEEK_API_KEY 时返回 None。

    返回 None 时示例自动进入"无 LLM 演示模式"：
        - 路由：关键词匹配（KeywordRouter）
        - 技能 Agent 节点：返回固定文本，展示装配链路已跑通
     这样没有 API Key 也能完整演示动态组装流程。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("⚠ 未检测到 DEEPSEEK_API_KEY：将以「纯关键词路由 + 无 LLM」模式运行")
        print("  配置 .env 中的 DEEPSEEK_API_KEY 后即可使用 LLM 路由与智能回复\n")
        return None
    # 与仓库内其他示例保持一致：DeepSeek chat 模型
    return init_chat_model("deepseek-chat", api_key=api_key)


def print_assembly_report(skills, tools_by_server, skill_node_map) -> None:
    """打印装配清单：动态组装了什么、绑定了哪些工具。"""
    print("=" * 70)
    print("装配清单（动态生成）")
    print("=" * 70)
    print(f"MCP 服务器: {list(tools_by_server.keys())}")
    for name, tools in tools_by_server.items():
        print(f"  └─ {name}: {[t.name for t in tools]}")
    print(f"\n技能 -> 图节点 -> 工具:")
    for skill in skills:
        print(f"  └─ {skill.name}  ->  {skill_node_map[skill.name]}  ->  {[t.name for t in skill.tools]}")
    print("=" * 70)


async def main() -> None:
    """完整示例：动态组装 MCP + Skill，并进入交互式运行。"""
    load_dotenv()  # 读取 .env（若存在 DEEPSEEK_API_KEY 等配置）

    # =====================================================================
    # Step 1：读配置（全部来自 yaml，无硬编码）
    # =====================================================================
    mcp_servers_cfg = load_mcp_config()          # MCP 服务器注册表
    skill_defs = load_skill_defs()               # 技能定义列表
    print(f"[1/4] 读取配置：MCP 服务器 {len(mcp_servers_cfg)} 个，"
          f"技能定义 {len(skill_defs)} 个")

    # =====================================================================
    # Step 2：动态连接 MCP 并发现工具（langchain-mcp-adapters）
    # =====================================================================
    mcp_manager = MCPManager(mcp_servers_cfg)
    tools_by_server = await mcp_manager.connect()
    print(f"[2/4] 动态连接 MCP，发现工具: "
          f"{ {k: [t.name for t in v] for k, v in tools_by_server.items()} }")

    # =====================================================================
    # Step 3：装配技能（按名把工具绑定给技能）
    # =====================================================================
    skills = assemble_skills(skill_defs, tools_by_server)
    print(f"[3/4] 装配技能: {[s.name for s in skills]}")

    # =====================================================================
    # Step 4：动态构图（路由 + 每个技能一个 Agent 节点）
    # =====================================================================
    llm = create_llm()
    graph, skill_node_map = build_dynamic_graph(llm, skills)
    print("[4/4] 动态构图完成 ✓")
    print_assembly_report(skills, tools_by_server, skill_node_map)

    # =====================================================================
    # 交互式运行
    # =====================================================================
    print("\n交互模式：输入你想问的问题（示例见下），输入 exit / quit 退出")
    for q in SAMPLE_QUESTIONS:
        print(f"  示例问题: {q}")

    try:
        while True:
            user_input = input("\n你> ").strip()
            if not user_input:
                continue
            if user_input.lower() in {"exit", "quit", "q"}:
                break

            # 调用图：注入消息，图会自动完成 路由 -> 技能 Agent -> 回复
            result = await graph.ainvoke({"messages": [{"role": "user", "content": user_input}]})
            # 打印最后的 AI 消息（技能 Agent 的最终回复）
            for message in result["messages"]:
                if getattr(message, "type", "") == "ai" and not getattr(message, "tool_calls", None):
                    print(f"助手> {message.content}")
    finally:
        # 关闭所有 MCP 连接，释放子进程
        await mcp_manager.close()
        print("\n已关闭 MCP 连接，示例结束。")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
