"""外部 HTTP 类型 MCP 服务端（Demo 服务）

本文件模拟一个「部署在远端、通过 HTTP 暴露」的 MCP Server。
LangGraph 客户端通过 URL 调用这里暴露的工具，与调用本地工具完全隔离。

启动方式（独立进程）:
    python mcp_server.py

默认监听 http://127.0.0.1:8000/mcp （Streamable HTTP 端点）
"""

from mcp.server.fastmcp import FastMCP

# 创建一个 MCP Server 实例，name 会出现在客户端连接的 server 列表里
mcp = FastMCP(
    "weather",
    instructions="提供天气查询与汇率查询的外部 HTTP MCP 服务",
)


@mcp.tool()
def get_weather(city: str) -> str:
    """查询指定城市的当前天气。

    Args:
        city: 城市名称（中文或英文均可），例如 上海 / Beijing。
    """
    # 演示数据（确定性假数据）；生产环境替换为对真实气象 API 的调用即可
    weather_table = {
        "上海": {"weather": "晴", "temperature": 28.0, "humidity": 60},
        "北京": {"weather": "多云", "temperature": 25.0, "humidity": 45},
        "深圳": {"weather": "阵雨", "temperature": 30.0, "humidity": 80},
    }
    info = weather_table.get(city, {"weather": "未知", "temperature": 0.0, "humidity": 0})
    return (
        f"{city} 当前天气：{info['weather']}，"
        f"气温 {info['temperature']}°C，湿度 {info['humidity']}%"
    )


@mcp.tool()
def get_exchange_rate(currency: str) -> str:
    """查询人民币(CNY)兑指定外币的汇率。

    Args:
        currency: 三位货币代码，例如 USD / EUR / JPY。
    """
    # 演示数据；生产环境替换为真实汇率 API
    rate_table = {"USD": 7.12, "EUR": 7.85, "JPY": 0.049}
    rate = rate_table.get(currency.upper())
    if rate is None:
        return f"暂不支持货币: {currency}"
    return f"1 {currency.upper()} = {rate} CNY"


if __name__ == "__main__":
    # FastMCP 的传输协议：
    # - "stdio": 本地子进程
    # - "streamable-http": 通过 HTTP 暴露（本示例，mcp 1.15 的命名）
    # - "sse": Server-Sent Events
    # 启动后端点固定为 http://127.0.0.1:8000/mcp
    mcp.run(transport="streamable-http")
