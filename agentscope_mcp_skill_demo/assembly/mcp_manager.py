# -*- coding: utf-8 -*-
"""MCP 管理器：动态连接 MCP 服务，统一管理客户端生命周期。

这是“动态组装 MCP”的核心组件：

1. 接收上一步 config_loader 产出的配置条目列表；
2. 为每个条目创建一个 ``MCPClient``（AgentScope 的统一 MCP 客户端）；
3. 逐个 ``connect()`` 建立连接（stdio 连接必须显式 connect，且为有状态）；
4. 把连接好的客户端交给 Toolkit 使用，工具名形如 ``mcp__{name}__{tool}``；
5. 结束时统一 ``close()`` 释放子进程资源。
"""

import asyncio

from agentscope.mcp import MCPClient
from agentscope.tool import ToolBase

from .config_loader import MCPServerEntry


class MCPManager:
    """管理一组动态连接的 MCP 客户端。"""

    def __init__(self) -> None:
        self._clients: dict[str, MCPClient] = {}
        """已连接的客户端，key 为客户端名称"""

    @property
    def clients(self) -> list[MCPClient]:
        """当前已连接的所有 MCPClient（供 Toolkit 组装使用）。"""
        return list(self._clients.values())

    async def connect_all(self, entries: list[MCPServerEntry]) -> None:
        """根据配置逐条建立 MCP 连接。

        Args:
            entries: config_loader 产出的配置条目列表

        Raises:
            RuntimeError: 已有同名客户端已连接
        """
        for entry in entries:
            if entry.name in self._clients:
                raise RuntimeError(f"MCP 客户端 {entry.name} 已存在，请勿重复连接")

            # 构造 MCPClient：
            # - is_stateful=True：stdio 连接必须是有状态的（持有一个长会话）
            # - enable/disable_tools：动态裁剪该服务暴露的工具
            client = MCPClient(
                name=entry.name,
                is_stateful=True,
                mcp_config=entry.mcp_config,
                enable_tools=entry.enable_tools,
                disable_tools=entry.disable_tools,
            )

            # stdio 有状态连接需要显式 connect()：拉起子进程并握手
            await client.connect()
            self._clients[entry.name] = client

            # 列出该服务实际暴露的工具（包装为 ToolBase 对象）
            tools = await client.list_tools()
            names = [t.name for t in tools]
            print(
                f"  [MCP] 已连接 '{entry.name}': "
                f"{len(names)} 个工具 -> {', '.join(names)}",
            )

    async def list_all_tools(self) -> list[ToolBase]:
        """汇总所有已连接服务的工具（包装后的 ToolBase 对象）。

        如果不想把 MCPClient 直接交给 Toolkit，也可以手动把
        这些工具对象传进 ``Toolkit(tools=[...])``。
        """
        tasks = [client.list_tools() for client in self._clients.values()]
        results = await asyncio.gather(*tasks)
        return [tool for group in results for tool in group]

    async def close_all(self) -> None:
        """关闭全部连接，清理子进程资源。"""
        for client in self._clients.values():
            try:
                await client.close()
            except Exception as e:  # 清理阶段出错只告警，不阻断后续
                print(f"  [MCP] 关闭 '{client.name}' 失败: {e}")
            except BaseException as e:
                # stdio 子进程退出时的任务组清理会抛 CancelledError
                # （BaseException 子类，agentscope 2.0.6 未捕获），
                # 此时连接实际已关闭，仅提示即可
                print(f"  [MCP] 关闭 '{client.name}' 的清理异常(可忽略): {e}")
        self._clients.clear()
