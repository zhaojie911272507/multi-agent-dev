"""
Database MCP Server - 生产级私有数据库 MCP

- list_tables: 列出所有表（排除系统表）
- describe_table: 获取表结构（字段、主键、索引）
- get_schema: 自省整个 Schema（表、字段、外键）
- execute_query: 执行参数化 SQL 查询（只读/可选写，行数/大小限制）
"""

from __future__ import annotations

import json
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .config import load_config
from .db import DatabaseManager

# 全局单例（MCP 常驻进程）
_db: Optional[DatabaseManager] = None


def _get_db() -> DatabaseManager:
    global _db
    if _db is None:
        _db = DatabaseManager(load_config())
    return _db


mcp = FastMCP("Database")


@mcp.tool(
    description="List all tables in the database. System tables (e.g. pg_*, information_schema) are excluded by default. "
    "Use this to discover available tables before building queries.",
)
def list_tables(exclude_system: bool = True) -> list[str]:
    """List all table names in the database, optionally excluding system tables."""
    return _get_db().list_tables(exclude_system=exclude_system)


@mcp.tool(
    description="Get the structure of a specific table: column names, types, nullable, primary key, and indexes. "
    "Use this to understand how to build JOIN queries and which columns to select.",
)
def describe_table(table_name: str) -> dict[str, Any]:
    """Get column names, types, primary key, and indexes for a table."""
    return _get_db().describe_table(table_name)


@mcp.tool(
    description="Introspect the entire database schema: all tables, their columns, types, primary keys, and foreign keys. "
    "Use this to explore table relationships and build correct queries. "
    "Excludes system tables by default.",
)
def get_schema(
    schema_name: Optional[str] = None,
    exclude_system: bool = True,
) -> dict[str, Any]:
    """Get full schema information for all tables (columns, PKs, FKs)."""
    return _get_db().get_schema(schema_name=schema_name, exclude_system=exclude_system)


@mcp.tool(
    description="Execute a read-only SQL query (SELECT or WITH). Uses parameterized execution to prevent SQL injection. "
    "Pass parameters as a JSON object for values, e.g. params='{\"user_id\": 123}'. "
    "Results are truncated to MAX_ROWS (default 1000) and 1MB. "
    "Dates and BigInt are serialized safely. Only SELECT allowed unless ALLOW_WRITE_OPERATIONS=true.",
)
def execute_query(
    query: str,
    params: Optional[str] = None,
) -> str:
    """
    Execute a parameterized SQL query.
    - query: SQL string with :param_name placeholders (or %(param_name)s for some drivers)
    - params: Optional JSON string of parameters, e.g. '{"id": 1, "name": "foo"}'
    """
    db = _get_db()
    parsed_params: Optional[dict[str, Any]] = None
    if params:
        try:
            parsed_params = json.loads(params)
        except json.JSONDecodeError:
            return json.dumps({
                "error": "Invalid params JSON. Use e.g. '{\"id\": 1}'",
                "rows": [],
                "truncated": False,
            })

    result = db.execute_query(query, params=parsed_params)
    return json.dumps(result, default=str, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")
