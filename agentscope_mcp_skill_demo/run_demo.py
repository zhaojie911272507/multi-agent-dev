# -*- coding: utf-8 -*-
"""AgentScope 动态组装 MCP + Skill 示例 —— 运行入口。

运行方式（在示例目录下）::

    python run_demo.py

流程概览:

    1. 读取 ``config/mcp_servers.yaml``，动态连接配置里声明的 MCP 服务
    2. 动态扫描 ``skills/`` 目录加载技能
    3. 用 Toolkit 把 MCP 工具 + 技能组装进 Agent（DeepSeek 模型）
    4. 自动演示两个场景（MCP 计算 / 技能报告），然后进入交互对话
    5. 结束后统一关闭 MCP 连接
"""

import asyncio
import sys
from pathlib import Path

# 允许直接运行本文件时导入 assembly 包（把示例根目录加入 sys.path）
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.event import (  # noqa: E402
    TextBlockDeltaEvent,
    ToolCallStartEvent,
    ToolResultStartEvent,
)
from agentscope.message import UserMsg  # noqa: E402
from agentscope.permission import PermissionBehavior, PermissionRule  # noqa: E402
from agentscope.tool import FunctionTool  # noqa: E402

from assembly.agent_builder import build_agent  # noqa: E402
from assembly.config_loader import ensure_env_loaded, load_mcp_servers  # noqa: E402
from assembly.mcp_manager import MCPManager  # noqa: E402
from assembly.skill_loader import list_skills  # noqa: E402

# 示例根目录（配置文件、服务器脚本、技能目录都基于它定位）
DEMO_ROOT = Path(__file__).resolve().parent

# 智能体系统提示词：说明角色，提示可以配合技能与工具
SYSTEM_PROMPT = (
    "你是一个乐于助人的中文助手，可以调用 MCP 工具完成计算、查询等任务。"
    "当用户请求涉及数据分析/报告时，先查看可用的技能并按技能说明执行。"
)


async def ask_and_print(agent, text: str) -> str:
    """向智能体发送一条消息，边流式输出边打印过程，返回完整回复文本。

    用 ``reply_stream`` 逐条消费事件（流式文本、工具调用、工具结果），
    效果比一次性 ``reply()`` 更直观。最终文本由 TextBlockDeltaEvent 拼出。
    """
    print(f"\n{'=' * 70}\n[用户] {text}\n{'-' * 70}")

    final_text: list[str] = []
    async for event in agent.reply_stream(UserMsg("user", text)):
        if isinstance(event, TextBlockDeltaEvent):
            # 流式输出的文本增量，实时打印
            print(event.delta, end="", flush=True)
            final_text.append(event.delta)
        elif isinstance(event, ToolCallStartEvent):
            # 智能体开始调用某个工具（MCP 工具名形如 mcp__math__add）
            print(f"\n  [调用工具] {event.tool_call_name} ...", flush=True)
        elif isinstance(event, ToolResultStartEvent):
            print(f"  [工具返回] {event.tool_call_name}", flush=True)

    print("\n" + "=" * 70)
    return "".join(final_text)


async def demo_dynamic_tool_add_remove(agent) -> None:
    """演示 Toolkit 的运行时动态增删工具（on-the-fly）。

    除了启动时组装，Toolkit 还支持运行中动态注册/移除工具，
    例如根据用户诉求临时挂载一个新能力。
    """
    print(f"\n{'#' * 70}\n# 演示：运行时动态增删工具\n{'#' * 70}")

    # 1) 动态注册一个普通 Python 函数为工具
    def get_server_time(timezone: str) -> str:
        """获取指定时区的当前时间（演示用，返回固定字符串）。

        Args:
            timezone: 时区名，例如 Asia/Shanghai
        """
        return f"{timezone} 的当前时间是 12:00:00（模拟数据）"

    tool = FunctionTool(
        func=get_server_time,
        name="get_server_time",
        description="获取指定时区的当前时间",
    )

    toolkit = agent.toolkit  # Agent 持有组装好的 Toolkit
    await toolkit.add_tool(tool)  # 动态加入工具（默认加入 basic 组）

    # 权限同样要同步：DONT_ASK 模式下，没有 allow 规则的工具会被拒绝，
    # 因此运行时新增工具时需一并注册权限规则（与组装时保持一致）
    agent.state.permission_context.allow_rules[tool.name] = [
        PermissionRule(
            tool_name=tool.name,
            rule_content=None,  # None = 匹配该工具的所有调用
            behavior=PermissionBehavior.ALLOW,
            source="dynamic-demo",
        ),
    ]
    print(f"  [动态注册] 已添加工具 '{tool.name}'（含权限规则）")

    # 让智能体实际调用一次新工具，验证生效
    await ask_and_print(agent, "现在是几点？帮我查一下 Asia/Shanghai 的时间")

    # 2) 动态移除该工具
    await toolkit.remove_tool("get_server_time")
    print(f"  [动态移除] 已移除工具 '{tool.name}'，后续调用会失败")


async def main() -> None:
    """主流程：加载配置 → 连接 MCP → 加载技能 → 组装 Agent → 对话。"""

    # ------------------------------------------------------------------
    # 0) 环境准备：加载仓库根目录 .env（DEEPSEEK_API_KEY 等）
    # ------------------------------------------------------------------
    ensure_env_loaded()

    # ------------------------------------------------------------------
    # 1) 读取 MCP 服务配置（动态组装的数据源）
    # ------------------------------------------------------------------
    config_path = DEMO_ROOT / "config" / "mcp_servers.yaml"
    entries = load_mcp_servers(config_path)
    print(f"[配置] 读取到 {len(entries)} 个 MCP 服务: "
          f"{', '.join(e.name for e in entries)}")

    # ------------------------------------------------------------------
    # 2) 动态连接 MCP 服务，获取工具
    # ------------------------------------------------------------------
    mcp_manager = MCPManager()
    await mcp_manager.connect_all(entries)

    # ------------------------------------------------------------------
    # 3) 动态加载技能（仅展示清单；真正的加载由 Toolkit 内部完成）
    # ------------------------------------------------------------------
    skills = await list_skills()
    print(f"[技能] 加载到 {len(skills)} 个技能: "
          f"{', '.join(s.name for s in skills)}")

    # ------------------------------------------------------------------
    # 4) 组装 Agent：MCP 客户端 + 技能目录 + DeepSeek 模型
    # ------------------------------------------------------------------
    agent = await build_agent(
        name="assistant",
        system_prompt=SYSTEM_PROMPT,
        mcps=mcp_manager.clients,   # 动态连接好的 MCP 客户端
        skills_dir=str(DEMO_ROOT / "skills"),
        auto_confirm_tools=True,    # 跳过逐次人工确认，演示更顺畅
    )
    print("[组装] Agent 构建完成")

    # ------------------------------------------------------------------
    # 5) 自动演示：场景一 —— 直接调用 MCP 计算工具
    # ------------------------------------------------------------------
    await ask_and_print(agent, "请计算 (12 + 34) * 5 / 6 的结果是多少？")

    # ------------------------------------------------------------------
    # 6) 自动演示：场景二 —— 技能 + MCP 工具协同（数据分析报告）
    #    智能体会先通过内置 Skill 查看工具读取技能说明，
    #    再按技能流程调用 mcp__math__* 工具计算并输出报告
    # ------------------------------------------------------------------
    await ask_and_print(
        agent,
        "我们三个月的销售额分别是 1200、2300、1750 万元，"
        "请写一份数据分析报告",
    )

    # ------------------------------------------------------------------
    # 7) 演示 Toolkit 运行时动态增删工具
    # ------------------------------------------------------------------
    await demo_dynamic_tool_add_remove(agent)

    # ------------------------------------------------------------------
    # 8) 进入交互模式：输入问题回车提问，输入 q 退出
    # ------------------------------------------------------------------
    print(f"\n{'#' * 70}\n# 交互模式：直接输入问题（输入 q 退出）\n{'#' * 70}")
    while True:
        try:
            user_input = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input:
            continue
        if user_input.lower() in ("q", "quit", "exit"):
            break
        await ask_and_print(agent, user_input)

    # ------------------------------------------------------------------
    # 9) 清理：关闭所有 MCP 连接（释放服务子进程）
    # ------------------------------------------------------------------
    await mcp_manager.close_all()
    print("\n[完成] 已关闭全部 MCP 连接，示例结束。")


if __name__ == "__main__":
    asyncio.run(main())
