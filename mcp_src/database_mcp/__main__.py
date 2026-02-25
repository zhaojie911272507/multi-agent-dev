"""允许通过 python -m mcp_src.database_mcp 启动"""

from .server import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")
