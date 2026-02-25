"""
Database MCP Server - 数据库基础架构

- 连接池管理（SQLAlchemy）
- 参数化查询（防止 SQL 注入）
- 结果截断与序列化（BigInt、日期安全）
- 错误模糊化
"""

from __future__ import annotations

import json
import re
from contextlib import contextmanager
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.inspection import inspect

from .config import DatabaseConfig, load_config

# 危险 SQL 关键词（不区分大小写），用于只读模式校验
_DANGEROUS_KEYWORDS = {
    "drop", "truncate", "delete", "update", "insert", "alter",
    "create", "replace", "grant", "revoke", "exec", "execute",
    "merge", "copy", "lock", "unlock",
}


def _is_safe_read_only_query(sql: str, allow_write: bool) -> tuple[bool, Optional[str]]:
    """
    校验 SQL 是否安全。
    - allow_write=False 时，仅允许 SELECT。
    - allow_write=True 时，仍禁止部分高危操作。
    返回 (ok, error_message)。
    """
    # 去除注释和多余空白，取首个有效语句
    stripped = re.sub(r"--[^\n]*", "", sql)
    stripped = re.sub(r"/\*.*?\*/", "", stripped, flags=re.DOTALL)
    stripped = stripped.strip()

    if not stripped:
        return False, "Empty or whitespace-only query."

    first_word = stripped.split()[0].lower() if stripped.split() else ""
    if first_word != "select" and first_word != "with":
        if first_word in ("insert", "update", "delete") and allow_write:
            pass  # 允许
        elif not allow_write:
            return False, f"Write operations are disabled. Only SELECT is allowed. (Got: {first_word})"
        else:
            pass

    # 检查是否包含高危关键词（在非注释部分）
    upper_sql = stripped.upper()
    for kw in _DANGEROUS_KEYWORDS:
        if kw.upper() == "SELECT" or kw.upper() == "WITH":
            continue
        if allow_write and kw.upper() in ("INSERT", "UPDATE", "DELETE"):
            continue
        # 简单模式：作为独立词出现
        pattern = r"\b" + kw.upper() + r"\b"
        if re.search(pattern, upper_sql):
            return False, f"Query contains disallowed keyword: {kw.upper()}"

    return True, None


def _sanitize_for_json(obj: Any) -> Any:
    """将不可 JSON 序列化的类型转为字符串（如 Decimal、BigInt、datetime）"""
    if obj is None:
        return None
    if isinstance(obj, (Decimal,)):
        return str(obj)
    if isinstance(obj, (int,)) and (obj > 2**53 - 1 or obj < -(2**53)):
        return str(obj)
    if hasattr(obj, "isoformat"):  # datetime, date, time
        return obj.isoformat()
    if isinstance(obj, (bytes, bytearray)):
        return obj.hex()
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(v) for v in obj]
    return obj


def _obfuscate_error(exc: Exception) -> str:
    """向 LLM 返回时模糊化敏感错误信息"""
    msg = str(exc).lower()
    # 屏蔽可能泄露路径、内部结构的信息
    sensitive = ["/var/", "/home/", "/usr/", "traceback", "file ", "line "]
    for s in sensitive:
        if s in msg:
            return "Database error occurred. Please check your query and try again."
    # 保留逻辑错误（如 column not found、syntax error）
    if len(str(exc)) > 500:
        return str(exc)[:500] + "..."
    return str(exc)


class DatabaseManager:
    """数据库连接池与执行管理器"""

    def __init__(self, config: Optional[DatabaseConfig] = None) -> None:
        self._config = config or load_config()
        self._engine: Optional[Engine] = None

    def _get_engine(self) -> Engine:
        if self._engine is None:
            uri = self._config.connection_uri_for_pool()
            # 连接池：pool_size, max_overflow, pool_timeout
            self._engine = create_engine(
                uri,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=self._config.idle_timeout_ms // 1000,
                echo=False,
            )
        return self._engine

    @contextmanager
    def get_connection(self):
        """获取连接（上下文管理器）"""
        engine = self._get_engine()
        conn = engine.connect()
        try:
            yield conn
        finally:
            conn.close()

    def list_tables(self, exclude_system: bool = True) -> list[str]:
        """
        列出所有表名。exclude_system=True 时排除系统表。
        """
        engine = self._get_engine()
        insp = inspect(engine)
        tables = insp.get_table_names()
        if exclude_system:
            db_type = self._config.db_type
            if db_type == "postgresql":
                tables = [t for t in tables if not (t.startswith("pg_") or t == "sql_features")]
            elif db_type == "mysql":
                tables = [t for t in tables if not t.startswith("innodb_")]
        return tables

    def describe_table(self, table_name: str) -> dict[str, Any]:
        """
        获取表的字段名、类型、主键、索引。
        表名仅允许标识符，防止注入。
        """
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            return {"error": "Invalid table name. Use alphanumeric identifiers only."}

        engine = self._get_engine()
        insp = inspect(engine)
        if table_name not in insp.get_table_names():
            return {"error": f"Table '{table_name}' not found."}

        columns = insp.get_columns(table_name)
        pk = insp.get_pk_constraint(table_name)
        pk_columns = pk.get("constrained_columns", []) if pk else []
        indexes = insp.get_indexes(table_name)

        col_info = []
        for col in columns:
            col_info.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
                "primary_key": col["name"] in pk_columns,
            })

        return {
            "table": table_name,
            "columns": col_info,
            "primary_key": pk_columns,
            "indexes": [
                {"name": idx.get("name"), "columns": idx.get("column_names", [])}
                for idx in indexes
            ],
        }

    def get_schema(
        self,
        schema_name: Optional[str] = None,
        exclude_system: bool = True,
    ) -> dict[str, Any]:
        """
        自省整个 schema：表、字段、主键、外键。
        供 AI 探索表结构和关系。
        """
        tables = self.list_tables(exclude_system=exclude_system)
        schema_info = {"tables": {}, "errors": []}

        for t in tables:
            try:
                schema_info["tables"][t] = self.describe_table(t)
                if "error" in schema_info["tables"][t]:
                    schema_info["errors"].append(
                        f"Table {t}: {schema_info['tables'][t]['error']}"
                    )
            except Exception as e:
                schema_info["errors"].append(f"Table {t}: {_obfuscate_error(e)}")

        # 外键（PostgreSQL / MySQL 均可通过 insp）
        try:
            engine = self._get_engine()
            insp = inspect(engine)
            for t in tables:
                tbl_fks = insp.get_foreign_keys(t)
                if tbl_fks and t in schema_info["tables"] and "error" not in schema_info["tables"][t]:
                    schema_info["tables"][t]["foreign_keys"] = [
                        {
                            "columns": fk.get("constrained_columns", []),
                            "referred_table": fk.get("referred_table"),
                            "referred_columns": fk.get("referred_columns", []),
                        }
                        for fk in tbl_fks
                    ]
        except Exception:
            pass  # 部分数据库可能不支持

        return schema_info

    def execute_query(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        执行 SQL 查询。必须使用参数化，严禁拼接。
        - 强制行数限制、超时、结果大小限制
        - 日期/BigInt 正确序列化
        """
        ok, err = _is_safe_read_only_query(query, self._config.allow_write_operations)
        if not ok:
            return {"error": err, "rows": [], "truncated": False}

        params = params or {}
        max_rows = self._config.max_rows
        max_bytes = self._config.max_result_size_bytes
        timeout = self._config.query_timeout_sec

        with self.get_connection() as conn:
            try:
                # 设置语句超时（部分数据库/版本支持）
                try:
                    if self._config.db_type == "postgresql":
                        conn.execute(text("SET statement_timeout = :t"), {"t": timeout * 1000})
                    elif self._config.db_type == "mysql":
                        conn.execute(text("SET max_execution_time = :t"), {"t": timeout * 1000})
                except SQLAlchemyError:
                    pass  # 忽略不支持的数据库

                # 参数化执行
                stmt = text(query)
                result = conn.execute(stmt, params)
                rows = result.fetchall()
                columns = list(result.keys())
            except SQLAlchemyError as e:
                return {
                    "error": _obfuscate_error(e),
                    "rows": [],
                    "truncated": False,
                }

        # 行数截断
        truncated_rows = len(rows) > max_rows
        rows = rows[:max_rows]

        # 转为可序列化结构
        out = []
        for r in rows:
            row_dict = dict(zip(columns, r))
            out.append(_sanitize_for_json(row_dict))

        # 结果大小截断
        dumped = json.dumps(out, default=str, ensure_ascii=False)
        size_truncated = len(dumped) > max_bytes
        if size_truncated:
            # 逐行减少直到满足大小
            out_trunc = []
            size_so_far = 2  # "[]"
            for row in out:
                part = json.dumps([row], default=str, ensure_ascii=False)
                if size_so_far + len(part) - 2 > max_bytes - 200:  # 预留 warning 空间
                    break
                out_trunc.append(row)
                size_so_far += len(part) - 2
            out = out_trunc
            dumped = json.dumps(out, default=str, ensure_ascii=False)

        warning = None
        if truncated_rows:
            warning = (
                "Warning: Result truncated to MAX_ROWS. "
                "Please use LIMIT or specific filters."
            )
        if size_truncated:
            warning = (
                warning + " "
                if warning else ""
            ) + (
                "Warning: Data truncated due to size limits. "
                "Please use LIMIT or specific filters."
            )

        return {
            "rows": out,
            "columns": columns,
            "row_count": len(out),
            "truncated": truncated_rows or size_truncated,
            "warning": warning,
            "error": None,
        }

    def close(self) -> None:
        if self._engine:
            self._engine.dispose()
            self._engine = None
