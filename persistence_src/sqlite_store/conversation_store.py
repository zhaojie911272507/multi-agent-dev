"""
ConversationStore: 对话记录存 SQLite。
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .schema import init_schema


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConversationStore:
    """
    将会话与消息持久化到 SQLite。
    与 LangGraph thread_id 对应，可独立于 checkpointer 使用，便于查询与导出。
    """

    def __init__(self, db_path: str | Path = "persistence.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        init_schema(self.db_path)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def ensure_session(
        self,
        thread_id: str,
        user_id: str | None = None,
        title: str | None = None,
    ) -> None:
        """创建或更新 session 记录。"""
        now = _utc_now()
        with self._conn() as c:
            c.execute(
                """
                INSERT INTO sessions (thread_id, user_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(thread_id) DO UPDATE SET
                    user_id = COALESCE(excluded.user_id, user_id),
                    title = COALESCE(excluded.title, title),
                    updated_at = excluded.updated_at
                """,
                (thread_id, user_id, title, now, now),
            )

    def append_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        extra: dict[str, Any] | None = None,
    ) -> int:
        """
        追加一条消息，返回 seq。
        extra 可包含 tool_calls, tool_call_id 等。
        """
        self.ensure_session(thread_id)
        now = _utc_now()
        extra_json = json.dumps(extra, ensure_ascii=False) if extra else None

        with self._conn() as c:
            cur = c.execute(
                "SELECT COALESCE(MAX(seq), -1) + 1 FROM messages WHERE thread_id = ?",
                (thread_id,),
            )
            seq = cur.fetchone()[0]
            c.execute(
                """
                INSERT INTO messages (thread_id, seq, role, content, extra, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (thread_id, seq, role, content, extra_json, now),
            )
            c.execute(
                "UPDATE sessions SET updated_at = ? WHERE thread_id = ?",
                (now, thread_id),
            )
        return seq

    def get_messages(
        self,
        thread_id: str,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """按 seq 升序返回消息列表。"""
        with self._conn() as c:
            c.row_factory = sqlite3.Row
            q = "SELECT seq, role, content, extra, created_at FROM messages WHERE thread_id = ? ORDER BY seq"
            params: list[Any] = [thread_id]
            if limit is not None:
                q += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            rows = c.execute(q, params).fetchall()
        out = []
        for r in rows:
            extra = json.loads(r["extra"]) if r["extra"] else None
            out.append({
                "seq": r["seq"],
                "role": r["role"],
                "content": r["content"] or "",
                "extra": extra,
                "created_at": r["created_at"],
            })
        return out

    def get_session(self, thread_id: str) -> dict[str, Any] | None:
        """获取 session 信息。"""
        with self._conn() as c:
            c.row_factory = sqlite3.Row
            row = c.execute(
                "SELECT thread_id, user_id, title, created_at, updated_at FROM sessions WHERE thread_id = ?",
                (thread_id,),
            ).fetchone()
        if row is None:
            return None
        return dict(row)
