# -*- coding: utf-8 -*-
"""MCP 天气查询服务（stdio 传输，返回模拟数据）。

与 ``math_server.py`` 一样是一个标准 MCP 服务端。
本服务提供了 **两个** 工具，其中 ``get_weather_forecast`` 会在 YAML
配置里被 ``enable_tools`` 过滤掉——用来演示”动态裁剪 MCP 工具”的能力
（工具在运行时发现后按配置过滤，模型看不到被裁剪的工具）。
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-server")

# 模拟天气数据表（演示用，真实场景可对接外部 API）
_MOCK_WEATHER = {
    "北京": {"temperature": 26, "condition": "晴", "humidity": 40},
    "上海": {"temperature": 30, "condition": "多云", "humidity": 70},
    "广州": {"temperature": 33, "condition": "雷阵雨", "humidity": 85},
}


@mcp.tool()
def query_weather(city: str) -> dict:
    """查询指定城市当前的天气情况。

    Args:
        city: 城市名称，例如"北京"

    Returns:
        包含温度、天气状况、湿度的字典
    """
    if city not in _MOCK_WEATHER:
        return {"error": f"未收录城市 {city} 的天气数据"}
    return {"city": city, **_MOCK_WEATHER[city]}


@mcp.tool()
def get_weather_forecast(city: str, days: int = 3) -> list[dict]:
    """查询指定城市未来几天的天气预报。

    Args:
        city: 城市名称
        days: 预报天数（1~7）

    Returns:
        每天的天气列表
    """
    if city not in _MOCK_WEATHER:
        return []
    # 生成简单的模拟预报数据
    return [
        {"city": city, "day": f"第{i + 1}天", "condition": "晴", "temperature": 25 + i}
        for i in range(min(max(days, 1), 7))
    ]


if __name__ == "__main__":
    # stdio 方式启动，由 MCPClient 以子进程方式拉起
    mcp.run(transport="stdio")
