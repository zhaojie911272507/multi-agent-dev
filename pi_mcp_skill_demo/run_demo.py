# -*- coding: utf-8 -*-
"""Pi 动态组装 MCP + Skill 示例 —— 运行入口。

运行方式（在示例目录下）::

    python run_demo.py

流程概览:

    1. 读取 ``config/mcp_servers.yaml``，动态拉起配置里声明的 MCP 服务
    2. 动态扫描 ``skills/`` 目录，技能摘要注入系统提示词（懒加载）
    3. 用 Pi（pi_agent_core 的 Agent + pi_ai 的 DeepSeek 模型）组装：
       MCP 工具 + read_skill 技能工具
    4. 自动演示三个场景（MCP 计算 / 技能协同报告 / 运行时增删工具），
       然后进入交互对话
    5. 结束统一关闭 MCP 连接

Pi 特有的设计：系统提示词里只有技能摘要（name+description），
模型认为任务匹配某技能时，自行调用 ``read_skill`` 工具读取全文——
元数据优先、按需懒加载，是 Pi 上游 agent 运行时对 skills 的标准做法。
"""

import asyncio
import sys
from pathlib import Path

# 允许直接运行本文件时导入 assembly 包（把示例根目录加入 sys.path）
DEMO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO_ROOT))

from pi_ai import TextDeltaEvent  # noqa: E402  底层流式增量事件（pi_ai 层）
from pi_agent_core import (  # noqa: E402  Agent 层生命周期事件
    AgentEndEvent,
    MessageUpdateEvent,
    ToolExecutionEndEvent,
    ToolExecutionStartEvent,
)

from assembly.agent_builder import build_agent, make_function_tool  # noqa: E402
from assembly.config_loader import ensure_env_loaded, load_mcp_servers  # noqa: E402
from assembly.mcp_manager import MCPManager  # noqa: E402
from assembly.skill_loader import load_skill_components  # noqa: E402

# 智能体系统提示词：角色说明 + 技能摘要块会拼在后面
SYSTEM_PROMPT = (
    "你是一个乐于助人的中文助手，可以调用 MCP 工具完成计算、天气查询等任务。"
    "当用户请求涉及数据分析/报告时，先查看系统提示词中的 <available_skills> 技能清单，"
    "若匹配请先调用 read_skill 工具读取技能全文，再按技能说明执行。"
)


# ============================================================
# 事件订阅：流式打印对话过程
# ============================================================


class _ProgressPrinter:
    """订阅 Agent 事件，把流式文本和工具调用过程打印到终端。

    Pi 的 Agent.subscribe() 会串行广播 AgentEvent；我们只关心两类：
      - MessageUpdateEvent：模型输出增量（内部携带 pi_ai 的 TextDeltaEvent）
      - ToolExecutionStart/EndEvent：工具调用的开始与结束
    """

    def __init__(self) -> None:
        self.buffer: list[str] = []  # 累积本次回复的文本，最后拼成完整回复

    async def __call__(self, event, cancel_event) -> None:
        if isinstance(event, MessageUpdateEvent):
            # 取底层流式增量事件里的文本块
            inner = event.assistant_message_event
            if isinstance(inner, TextDeltaEvent) and inner.delta:
                print(inner.delta, end="", flush=True)
                self.buffer.append(inner.delta)
        elif isinstance(event, ToolExecutionStartEvent):
            print(f"\n  [调用工具] {event.tool_name}({event.args}) ...", flush=True)
        elif isinstance(event, ToolExecutionEndEvent):
            status = "成功" if not event.is_error else "失败"
            print(f"  [工具返回] {event.tool_name} → {status}", flush=True)
        elif isinstance(event, AgentEndEvent):
            # 排查用：Pi 把模型/网络错误编码进消息的 error_message
            last = event.messages[-1] if event.messages else None
            if last is not None and getattr(last, "error_message", None):
                print(f"\n  [Agent 错误] {last.error_message}", flush=True)

    def drain(self) -> str:
        """取走缓冲的完整回复文本。"""
        text = "".join(self.buffer)
        self.buffer.clear()
        return text


# ============================================================
# 对话辅助
# ============================================================


async def ask_and_print(agent, printer: _ProgressPrinter, text: str) -> str:
    """向智能体发一条消息，边流式输出边打印工具调用过程。

    Pi 的 Agent.prompt() 会跑完整个 ReAct 循环（模型 → 工具 → 模型 → …）
    直到模型给出最终答复，期间事件经订阅者实时打印。

    Returns:
        完整回复文本（去掉流式打印的空行差异，用于报告统计）
    """
    print(f"\n{'=' * 70}\n[用户] {text}\n{'-' * 70}")
    await agent.prompt(text)  # 事件由订阅者实时打印
    final = printer.drain()
    print(f"\n{'=' * 70}")
    return final


# ============================================================
# 演示场景
# ============================================================


async def demo_dynamic_tool_add_remove(agent, printer: _ProgressPrinter) -> None:
    """场景三：运行时动态增删工具。

    除了启动时组装，Agent 的 state.tools 是普通 list——
    对话过程中 append / remove 会在下一次 prompt 时立即生效，
    这就是"动态组装"的最后一环：能力可以在线挂载与卸载。
    """
    print(f"\n{'#' * 70}\n# 演示：运行时动态增删工具\n{'#' * 70}")

    # 1) 动态挂载：把普通 Python 函数变成 Pi 工具
    def get_server_time(timezone: str) -> str:
        """获取指定时区的当前时间（演示用，返回固定字符串）。"""
        return f"{timezone} 的当前时间是 12:00:00（模拟数据）"

    tool = make_function_tool(get_server_time, name="get_server_time",
                              description="获取指定时区的当前时间")
    agent.state.tools.append(tool)  # 直接操作状态，下一次 prompt 生效
    print(f"  [动态注册] 已添加工具 'get_server_time'，当前共 {len(agent.state.tools)} 个工具")

    # 让模型实际调用一次新工具，验证生效
    await ask_and_print(agent, printer, "现在是几点？帮我查一下 Asia/Shanghai 的时间")

    # 2) 动态卸载：从工具列表移除
    agent.state.tools.remove(tool)
    print(f"  [动态移除] 已移除工具 'get_server_time'，当前共 {len(agent.state.tools)} 个工具")


async def main() -> None:
    """主流程：加载配置 → 连接 MCP → 加载技能 → 组装 Agent → 对话。"""

    # ------------------------------------------------------------------
    # 0) 环境准备：加载仓库根目录 .env（DEEPSEEK_API_KEY 等）
    # ------------------------------------------------------------------
    ensure_env_loaded()

    # ------------------------------------------------------------------
    # 1) 读取 MCP 服务配置（动态组装的数据源）
    # ------------------------------------------------------------------
    entries = load_mcp_servers(DEMO_ROOT / "config" / "mcp_servers.yaml", DEMO_ROOT)
    print(f"[配置] 读取到 {len(entries)} 个 MCP 服务: "
          f"{', '.join(e.name for e in entries)}")

    # ------------------------------------------------------------------
    # 2) 动态连接 MCP 服务，发现并包装工具
    #    （MCPTool 名称形如 mcp__math__add，可被 read_skill 引用）
    # ------------------------------------------------------------------
    mcp_manager = MCPManager()
    mcp_tools = await mcp_manager.connect_all(entries)
    print(f"[组装] 得到 {len(mcp_tools)} 个 MCP 工具: "
          f"{', '.join(t.name for t in mcp_tools)}")

    # ------------------------------------------------------------------
    # 3) 动态加载技能：摘要注入提示词 + read_skill 懒加载工具
    # ------------------------------------------------------------------
    skills, skill_prompt_block, read_skill_tool = load_skill_components(
        DEMO_ROOT / "skills"
    )

    # ------------------------------------------------------------------
    # 4) 组装 Agent：MCP 工具 + read_skill 工具 + DeepSeek 模型
    # ------------------------------------------------------------------
    system_prompt = SYSTEM_PROMPT + "\n\n" + skill_prompt_block  # 技能摘要拼在后面
    agent = build_agent(system_prompt, [*mcp_tools, read_skill_tool])
    printer = _ProgressPrinter()
    agent.subscribe(printer)  # 订阅事件，实时打印过程
    print("[组装] Agent 构建完成，工具列表: "
          f"{[t.name for t in agent.state.tools]}")

    # ------------------------------------------------------------------
    # 5) 场景一：直接调用 MCP 计算工具
    # ------------------------------------------------------------------
    await ask_and_print(agent, printer, "请计算 (12 + 34) * 5 / 6 的结果是多少？")

    # ------------------------------------------------------------------
    # 6) 场景二：技能 + MCP 工具协同（数据分析报告）
    #    模型应先 read_skill 读取技能全文，再按技能流程调用 mcp__math__*
    #    计算并输出报告
    # ------------------------------------------------------------------
    await ask_and_print(
        agent, printer,
        "我们三个月的销售额分别是 1200、2300、1750 万元，请写一份数据分析报告",
    )

    # ------------------------------------------------------------------
    # 7) 场景三：运行时动态增删工具
    # ------------------------------------------------------------------
    await demo_dynamic_tool_add_remove(agent, printer)

    # ------------------------------------------------------------------
    # 8) 交互模式：输入问题回车提问，输入 q 退出
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
        await ask_and_print(agent, printer, user_input)

    # ------------------------------------------------------------------
    # 9) 清理：关闭所有 MCP 连接（释放服务子进程）
    # ------------------------------------------------------------------
    await mcp_manager.close_all()
    print("\n[完成] 已关闭全部 MCP 连接，示例结束。")


if __name__ == "__main__":
    asyncio.run(main())
