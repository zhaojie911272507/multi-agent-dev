#!/usr/bin/env python3
"""
weather_server.py —— 演示用 MCP 服务器（天气查询，内置模拟数据）

与 math_server.py 相同，是一个独立的标准 MCP 服务器（stdio）。
这里用一份内置的模拟数据代替真实天气 API，方便离线演示；
生产环境中只需把 get_weather 内部替换为真实天气 API 调用即可。

运行方式（单独测试）：
    python servers/weather_server.py
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

# 模拟天气数据库：城市 -> (天气状况, 气温℃)
_MOCK_WEATHER = {
    "北京": ("晴", 30),
    "上海": ("小雨", 26),
    "广州": ("多云", 33),
    "深圳": ("晴", 34),
    "杭州": ("阴", 28),
    "成都": ("小雨", 24),
    "beijing": ("Sunny", 30),
    "shanghai": ("Light rain", 26),
    "guangzhou": ("Cloudy", 33),
}


@mcp.tool()
def get_weather(city: str) -> str:
    """
    查询指定城市的当前天气。
    Args:
        city: 城市名称，如 "北京" 或 "beijing"。
    """
    if city in _MOCK_WEATHER:
        condition, temp = _MOCK_WEATHER[city]
        return f"{city}：{condition}，{temp}℃"
    return f"抱歉，没有找到城市「{city}」的天气数据，可用城市：{'、'.join(list(_MOCK_WEATHER)[:6])}"


if __name__ == "__main__":
    # 以 stdio 方式启动，等待客户端连接
    mcp.run(transport="stdio")
