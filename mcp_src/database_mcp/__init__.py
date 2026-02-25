"""
Database MCP Server - 生产级私有数据库 MCP

支持 PostgreSQL、MySQL，具备：
- 参数化查询防注入
- 连接池
- 结果截断（行数/大小）
- Schema 自省
- 错误模糊化
"""

from .config import DatabaseConfig, load_config
from .db import DatabaseManager
from .server import mcp

__all__ = ["mcp", "DatabaseManager", "DatabaseConfig", "load_config"]
