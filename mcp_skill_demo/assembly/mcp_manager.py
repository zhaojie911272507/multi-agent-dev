"""
mcp_manager.py —— MCP 服务器动态连接器（动态装配的第 1 步）

职责：
    1. 接收 mcp_servers.yaml 解析出的注册表 dict
    2. 为每个服务器创建一个独立的 MultiServerMCPClient 并连接
    3. 自动发现每个服务器暴露的工具，按服务器名分组返回

核心点：
    - 这里没有任何"写死的工具"——工具列表完全来自 MCP 服务器的动态发现
    - 新增一个 MCP 服务器只需改 yaml，本文件一行都不用动
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_mcp_adapters.client import MultiServerMCPClient

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool


class MCPManager:
    """管理一组 MCP 服务器的连接与工具发现。"""

    def __init__(self, servers_config: dict):
        """
        Args:
            servers_config: mcp_servers.yaml 的 servers 节点，
                形如 {"math": {"command": "python", "args": [...], "transport": "stdio"}}
        """
        self._servers_config = servers_config
        self._clients: dict[str, MultiServerMCPClient] = {}  # 服务器名 -> 客户端
        self._tools: dict[str, list["BaseTool"]] = {}        # 服务器名 -> 工具列表

    # ------------------------------------------------------------------
    # 动态连接 & 工具发现
    # ------------------------------------------------------------------
    async def connect(self) -> dict[str, list["BaseTool"]]:
        """
        连接注册表中所有 MCP 服务器，并自动发现各自的工具。

        Returns:
            {"math": [add, subtract, ...], "weather": [get_weather], ...}
        """
        for server_name, server_cfg in self._servers_config.items():
            # 每个服务器一个独立的客户端，保证工具能按服务器名清晰分组；
            # 若需要"一个客户端连多个服务器"，直接传整个 dict 给
            # MultiServerMCPClient 即可，其余代码不变。
            client = MultiServerMCPClient({server_name: server_cfg})
            self._clients[server_name] = client
            # get_tools() 会启动进程 / 建立连接，并发现全部 @mcp.tool() 工具
            self._tools[server_name] = await client.get_tools()
        return self._tools

    # ------------------------------------------------------------------
    # 查询 & 清理
    # ------------------------------------------------------------------
    def get_tools_by_server(self) -> dict[str, list["BaseTool"]]:
        """返回 {服务器名: 工具列表}，供技能装配阶段使用。"""
        return self._tools

    async def close(self) -> None:
        """
        释放 MCP 连接（资源清理钩子）。

        注意：langchain-mcp-adapters 0.2.x 中，每个工具调用都会自动创建
        并关闭独立的 MCP 会话（子进程也随之结束），因此不存在需要手动
        关闭的长期连接 —— 0.2.x 已移除 Context Manager（__aexit__ 会直接
        抛 NotImplementedError）。保留此空实现是为了给调用方一个清晰的
        资源管理语义，未来版本若提供显式关闭 API 只需在此补充。
        """
        self._clients.clear()
