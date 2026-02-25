"""
Database MCP Server - 配置管理

从环境变量加载数据库连接配置，支持 PostgreSQL、MySQL。
敏感信息不落日志。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class DatabaseConfig:
    """数据库连接配置（只读）"""

    db_type: Literal["postgresql", "mysql"]
    host: str
    port: int
    user: str
    password: str
    database: str
    max_rows: int
    idle_timeout_ms: int
    query_timeout_sec: int
    max_result_size_bytes: int
    allow_write_operations: bool
    db_driver: str  # mysql 驱动: pymysql | mysqldb

    def connection_uri(self) -> str:
        """生成 SQLAlchemy 连接 URI"""
        if self.db_type == "postgresql":
            return (
                f"postgresql://{self.user}:{self.password}"
                f"@{self.host}:{self.port}/{self.database}"
            )
        elif self.db_type == "mysql":
            prefix = "mysql+mysqldb" if self.db_driver == "mysqldb" else "mysql+pymysql"
            return (
                f"{prefix}://{self.user}:{self.password}"
                f"@{self.host}:{self.port}/{self.database}"
            )
        raise ValueError(f"Unsupported db_type: {self.db_type}")

    def connection_uri_for_pool(self) -> str:
        """用于连接池的 URI，可附加 pool 参数"""
        base = self.connection_uri()
        # 连接池参数由 SQLAlchemy create_engine 的 pool_* 参数控制
        return base


def load_config() -> DatabaseConfig:
    """从环境变量加载配置"""
    db_type_raw = os.getenv("DB_TYPE", "postgresql").lower()
    if db_type_raw not in ("postgresql", "mysql"):
        raise ValueError(
            f"DB_TYPE must be 'postgresql' or 'mysql', got: {db_type_raw}"
        )
    db_type: Literal["postgresql", "mysql"] = db_type_raw  # type: ignore

    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", "5432" if db_type == "postgresql" else "3306"))
    user = os.getenv("DB_USER", "")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "")

    if not all([user, password, database]):
        raise ValueError(
            "DB_USER, DB_PASSWORD, DB_NAME are required. "
            "Please set them in .env or environment."
        )

    max_rows = int(os.getenv("MAX_ROWS", "1000"))
    idle_timeout_ms = int(os.getenv("IDLE_TIMEOUT_MS", "30000"))
    query_timeout_sec = int(os.getenv("QUERY_TIMEOUT_SEC", "30"))
    max_result_size_bytes = int(os.getenv("MAX_RESULT_SIZE_BYTES", "1048576"))  # 1MB
    allow_write = os.getenv("ALLOW_WRITE_OPERATIONS", "false").lower() in ("true", "1", "yes")
    db_driver = os.getenv("DB_DRIVER", "pymysql").lower()

    return DatabaseConfig(
        db_type=db_type,
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        max_rows=max(max_rows, 1),
        idle_timeout_ms=max(idle_timeout_ms, 1000),
        query_timeout_sec=max(query_timeout_sec, 1),
        max_result_size_bytes=max(max_result_size_bytes, 1024),
        allow_write_operations=allow_write,
        db_driver=db_driver if db_driver in ("pymysql", "mysqldb") else "pymysql",
    )
