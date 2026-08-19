# -*- coding: utf-8 -*-
"""MCP 计算器服务（stdio 传输）。

本文件是一个标准的 MCP **服务端**（Server），基于官方 ``mcp`` 包里的
FastMCP 快速实现。它会被示例里的 ``MCPManager`` 以子进程方式拉起，
通过 stdio 与智能体通信。

用途：作为”Pi 动态组装”示例中的外部工具来源之一。
整个示例不需要安装任何独立服务，直接运行 ``run_demo.py`` 即可。

运行方式（由 MCPManager 自动拉起，无需手动执行）::

    python servers/math_server.py
"""

from mcp.server.fastmcp import FastMCP

# 创建一个 FastMCP 服务实例，name 仅用于日志/调试标识
mcp = FastMCP("math-server")


@mcp.tool()
def add(a: float, b: float) -> float:
    """计算两个数的和。

    Args:
        a: 第一个加数
        b: 第二个加数

    Returns:
        a + b 的结果
    """
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """计算两个数的差（a - b）。

    Args:
        a: 被减数
        b: 减数

    Returns:
        a - b 的结果
    """
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """计算两个数的乘积。

    Args:
        a: 第一个乘数
        b: 第二个乘数

    Returns:
        a * b 的结果
    """
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """计算两个数的商（a / b）。

    Args:
        a: 被除数
        b: 除数（不能为 0）

    Returns:
        a / b 的结果

    Raises:
        ValueError: 当 b 为 0 时
    """
    if b == 0:
        raise ValueError("除数不能为 0")
    return a / b


if __name__ == "__main__":
    # 以 stdio 方式启动服务：MCPClient 会通过标准输入/输出与它通信。
    # 合法传输方式还有 "sse" / "streamable-http"（注意不是 "http"）。
    mcp.run(transport="stdio")
