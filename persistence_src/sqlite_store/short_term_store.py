"""
ShortTermMemoryStore: 短期记忆存 SQLite。

支持 memory_type 区分：recent_summary, working_context, tool_result_cache 等。
可设置 expires_at 实现 TTL。
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .schema import init_schema


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ShortTermMemoryStore:
    """
    短期记忆存储。
    """

    def __init__(self, db_path: str | Path = "persistence.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        init_schema(self.db_path)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def put(
        self,
        thread_id: str | None,
        user_id: str | None,
        memory_type: str,
        content: str,
        expires_at: str | None = None,
    ) -> int:
        """
        写入一条短期记忆。
        expires_at: ISO8601 字符串，为空则不过期。
        返回插入的 id。
        """
        now = _utc_now()
        with self._conn() as c:
            cur = c.execute(
                """
                INSERT INTO short_term_memory (thread_id, user_id, memory_type, content, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (thread_id, user_id, memory_type, content, now, expires_at),
            )
            return cur.lastrowid or 0

    def get(
        self,
        thread_id: str | None = None,
        user_id: str | None = None,
        memory_type: str | None = None,
        limit: int = 10,
        exclude_expired: bool = True,
    ) -> list[dict[str, Any]]:
        """
        按条件查询短期记忆，按 created_at 降序。
        exclude_expired=True 时自动过滤已过期记录。
        """
        conditions = []
        params: list[Any] = []
        if thread_id is not None:
            conditions.append("thread_id = ?")
            params.append(thread_id)
        if user_id is not None:
            conditions.append("user_id = ?")
            params.append(user_id)
        if memory_type is not None:
            conditions.append("memory_type = ?")
            params.append(memory_type)
        if exclude_expired:
            conditions.append("(expires_at IS NULL OR expires_at > ?)")
            params.append(_utc_now())

        where = " AND ".join(conditions) if conditions else "1=1"
        params.append(limit)

        with self._conn() as c:
            c.row_factory = sqlite3.Row
            rows = c.execute(
                f"""
                SELECT id, thread_id, user_id, memory_type, content, created_at, expires_at
                FROM short_term_memory
                WHERE {where}
                ORDER BY created_at DESC
                LIMIT ?
                """,
                params,
            ).fetchall()
        return [dict(r) for r in rows]

    def delete_expired(self) -> int:
        """删除已过期记录，返回删除行数。"""
        with self._conn() as c:
            cur = c.execute(
                "DELETE FROM short_term_memory WHERE expires_at IS NOT NULL AND expires_at < ?",
                (_utc_now(),),
            )
            return cur.rowcount or 0
