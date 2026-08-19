# -*- coding: utf-8 -*-
"""MCP 动态连接与工具适配 —— 本示例的核心亮点。

``pi-py-agent-core``（Pi 的 Python 运行时）本身不内置 MCP 能力，
它只定义了工具契约 ``AgentTool``（name/description/parameters + execute）。
因此我们在这里实现一个桥接层：

    1. **动态连接**：按 YAML 配置逐条拉起 MCP 服务子进程（stdio 传输），
       建立 ``ClientSession`` 并保持存活，直到示例结束统一关闭。
    2. **动态发现**：连接后调用 ``session.list_tools()`` 自动发现服务
       暴露的全部工具，并按配置的 ``enable_tools`` / ``disable_tools``
       在运行时裁剪——代码里没有写死任何一个工具名。
    3. **协议适配**：把每个 MCP 工具包装成 Pi 的 ``AgentTool``
       （工具名 ``mcp__{服务名}__{工具名}``），execute 时转发为
       ``session.call_tool()``，结果文本包装成 ``AgentToolResult``。

通过这三步，任何符合 MCP 标准的服务（文件系统、数据库、浏览器……）
都能零代码接入 Pi 智能体。

**连接的生命周期设计**：mcp 的 ``stdio_client`` 是一个 async 生成器，
内部用 ``anyio.create_task_group()`` 管理子进程读写。若在同一任务里
enter / 跨任务 exit，anyio 的 cancel scope 会报
``Attempted to exit a cancel scope ...``（本示例早期踩过的坑）。
因此每个服务连接放在**独立的常驻 worker 任务**里：进入和退出都发生在
worker 任务内部，与主流程的任务隔离，关闭时序完全可控、不会误触
async 生成器的垃圾回收路径。
"""

from __future__ import annotations

import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from pi_ai import TextContent
from pi_agent_core import AgentToolResult

from .config_loader import MCPServerEntry


# ============================================================
# 工具适配：MCP 工具 → Pi 的 AgentTool
# ============================================================


class MCPTool:
    """把 MCP 服务端暴露的一个工具包装成 Pi 的 ``AgentTool`` 协议。

    Pi 通过鸭子类型识别工具（见 ``pi_agent_core/types.py`` 的 AgentTool
    Protocol），所以这里不需要继承任何基类，只要字段与 execute 签名
    匹配即可。
    """

    # ---- Pi AgentTool 协议要求的字段 ----

    #: 工具名：mcp__{服务名}__{工具名}，命名空间避免不同服务间冲突
    name: str
    #: 工具描述（直接取自 MCP 服务端的 docstring）
    description: str
    #: 参数 JSON Schema（直接取自 MCP 的 inputSchema）
    parameters: dict
    #: 展示标签（UI/日志用，非模型可见）
    label: str
    #: 执行模式（None = 跟随全局配置）
    execution_mode: None = None

    def __init__(self, server_name: str, server_tool, call_tool):
        """Args:
            server_name: 所属 MCP 服务名（来自 YAML 配置的 name）
            server_tool: mcp SDK 的 Tool 对象（list_tools() 的产物）
            call_tool: 绑定到该服务 session 的调用闭包
                       ``async (tool_name, arguments) -> str``
        """
        self.name = f"mcp__{server_name}__{server_tool.name}"
        self.description = server_tool.description or f"{server_name} 提供的工具 {server_tool.name}"
        # MCP 的 inputSchema 本身就是 JSON Schema，直接透传
        self.parameters = server_tool.inputSchema or {"type": "object", "properties": {}}
        self.label = f"mcp:{server_name}:{server_tool.name}"
        self._server_tool_name = server_tool.name  # 原始工具名（去掉前缀）
        self._call_tool = call_tool  # 闭包持有该服务长存的 session

    async def execute(self, tool_call_id, params, cancel_event=None, on_update=None):
        """Pi 循环调用工具时的入口。

        Args:
            tool_call_id: 本次工具调用的 ID（Pi 内部使用，透传即可）
            params: 模型按 parameters schema 生成的参数（dict）
            cancel_event: 取消信号（MCP 1.24 的 call_tool 不支持中途取消，
                          这里透传忽略，超时由外层 mcp 客户端处理）
            on_update: 流式进度回调（MCP 调用是整包返回，直接忽略）

        Returns:
            AgentToolResult: 结果文本（content 发给模型）

        Raises:
            任何异常都会冒泡给 Pi 循环，被编码为失败的工具结果
            （Pi 约定：execute 抛异常 = 失败）。
        """
        # 调用 MCP 服务端；参数由 mcp SDK 校验后透传给远端工具
        result = await self._call_tool(self._server_tool_name, params)
        return AgentToolResult(content=[TextContent(text=result)])


# ============================================================
# 服务会话：一条 YAML 配置 → 一个长存的 MCP 连接
# ============================================================


class _MCPServerSession:
    """单个 MCP 服务的长存会话（worker 任务模式）。

    ``start()`` 启动一个独立的 asyncio 任务 ``_run()``，MCP 连接的
    enter / exit 全部发生在该任务内部：

        - 连接建立后通过 ``_ready`` 事件通知 start() 返回
        - 之后主流程通过 ``list_tools()`` / ``call_tool()`` 与它交互
        - ``stop()`` 只负责置位 ``_stop`` 事件并等待 worker 退出，
          连接在 worker 任务内按正常顺序优雅关闭
    """

    def __init__(self, entry: MCPServerEntry):
        self.name = entry.name
        self._entry = entry
        self._task: asyncio.Task | None = None
        self._session: ClientSession | None = None
        self._ready = asyncio.Event()   # 连接建立（或失败）后置位
        self._stop = asyncio.Event()    # 请求关闭
        self._error: BaseException | None = None

    # ---- 生命周期 ----

    async def start(self) -> None:
        """启动 worker 任务并等待连接建立（或抛错）。"""
        self._task = asyncio.create_task(self._run())
        await self._ready.wait()        # 等待 worker 完成 MCP 握手
        if self._error is not None:
            raise self._error           # 连接失败：把错误抛给组装流程

    async def stop(self) -> None:
        """请求关闭并等待 worker 退出（逆序调用无副作用）。"""
        self._stop.set()
        if self._task is not None:
            await self._task
        print(f"  [MCP 已关闭] {self.name}")

    async def _run(self) -> None:
        """worker 主循环：连接 → 握手 → 服务调用 → 收到停止信号后关闭。"""
        params = StdioServerParameters(
            command=self._entry.command,
            args=self._entry.args,
            env=self._entry.env or None,  # 与 os.environ 合并后传给子进程
        )
        try:
            # stdio_client：拉起子进程并建立双向管道（read/write 两个流）
            # 整个 async with 生命周期都在这一个 worker 任务里完成
            async with stdio_client(params) as (read, write):
                # ClientSession：面向 MCP 协议的会话壳（list_tools / call_tool）
                async with ClientSession(read, write) as session:
                    await session.initialize()  # MCP 握手：能力协商
                    self._session = session
                    print(f"  [MCP 已连接] {self.name}")
                    self._ready.set()           # 通知 start() 连接成功
                    await self._stop.wait()     # 一直服务，直到 stop()
        except BaseException as exc:  # noqa: BLE001 —— 含取消也要上报
            if isinstance(exc, asyncio.CancelledError):
                self._error = exc
            else:
                self._error = exc
            self._ready.set()                   # 通知 start() 连接失败

    # ---- 对外服务接口 ----

    async def list_tools(self):
        """动态发现远端服务暴露的工具清单（ListToolsResult.tools）。"""
        return (await self._session.list_tools()).tools

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """调用本服务的某个工具，返回纯文本结果。

        远端可能返回多种 content 块（文本/图片/资源引用），
        这里只提取文本块拼成字符串；真实场景可按需处理图片等。
        """
        call_result = await self._session.call_tool(tool_name, arguments=arguments)
        parts: list[str] = []
        for block in call_result.content:
            if getattr(block, "type", None) == "text":  # TextContent
                parts.append(block.text)
        return "\n".join(parts) if parts else f"(空结果，isError={call_result.isError})"


# ============================================================
# MCP 管理器：连接全部服务 → 发现并包装工具 → 统一关闭
# ============================================================


class MCPManager:
    """动态组装 MCP 工具的总入口。"""

    def __init__(self) -> None:
        self._sessions: dict[str, _MCPServerSession] = {}

    async def connect_all(self, entries: list[MCPServerEntry]) -> list[MCPTool]:
        """连接配置里的全部服务，返回包装好的 Pi 工具列表。

        Args:
            entries: load_mcp_servers() 的产物

        Returns:
            全部服务的可用工具（已应用 enable/disable 过滤）。
            调用方把它注册进 ``agent.state.tools`` 即完成组装。

        Raises:
            任一服务连接失败时：先关闭已建立的服务，再抛出异常。
        """
        tools: list[MCPTool] = []
        try:
            for entry in entries:
                session = _MCPServerSession(entry)
                await session.start()
                self._sessions[entry.name] = session

                # 动态发现：让远端服务自报工具清单，代码不写死任何工具名
                discovered = list(await session.list_tools())
                print(f"  [工具发现] {entry.name}: {[t.name for t in discovered]}")

                # 按配置裁剪（enable 优先；同时给出 disable 时 enable 生效）
                keep = (
                    {t.name for t in discovered if t.name in set(entry.enable_tools)}
                    if entry.enable_tools is not None
                    else {t.name for t in discovered} - set(entry.disable_tools)
                )
                dropped = [t.name for t in discovered if t.name not in keep]
                if dropped:
                    print(f"  [工具裁剪] {entry.name}: 过滤掉 {dropped}")

                # 每个保留的工具包装成 Pi AgentTool（闭包绑定本服务会话）
                tools.extend(
                    MCPTool(entry.name, t, session.call_tool)
                    for t in discovered
                    if t.name in keep
                )
        except Exception:
            # 中途失败：先关闭已建立的连接，再向上抛错
            await self.close_all()
            raise
        return tools

    async def close_all(self) -> None:
        """统一关闭所有 MCP 连接（释放服务子进程）。

        每个连接的 enter/exit 都在各自的 worker 任务里，因此关闭顺序
        没有约束（逆序关闭也安全）。worker 任务退出后子进程随之结束。
        """
        for session in reversed(list(self._sessions.values())):
            await session.stop()
        self._sessions.clear()
