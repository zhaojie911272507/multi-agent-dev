#!/usr/bin/env python3
"""
math_server.py —— 演示用 MCP 服务器（数学计算）

用 mcp 官方的 FastMCP 框架实现一个标准 MCP 服务器。
它没有任何 LangGraph / LangChain 依赖，是一个独立的进程，
通过 stdio（标准输入/输出）与客户端通信。

在示例中，它由 mcp_skill_demo 的 MCPManager 以子进程方式动态拉起，
客户端只"发现"这里用 @mcp.tool() 注册的工具，无需任何硬编码。

运行方式（单独测试）：
    python servers/math_server.py
"""
from mcp.server.fastmcp import FastMCP

# 创建 MCP 服务器实例，name 是服务器标识（会出现在客户端日志中）
mcp = FastMCP("Math")


@mcp.tool()
def add(a: float, b: float) -> float:
    """两个数相加。"""
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """第一个数减去第二个数。"""
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """两个数相乘。"""
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """第一个数除以第二个数。除数不能为 0。"""
    if b == 0:
        raise ValueError("除数不能为 0")
    return a / b


if __name__ == "__main__":
    # 以 stdio 方式启动，等待客户端连接
    mcp.run(transport="stdio")
