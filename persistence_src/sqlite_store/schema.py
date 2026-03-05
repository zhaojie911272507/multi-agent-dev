"""
Schema: 创建 SQLite 表结构。
"""

import sqlite3
from pathlib import Path


# 建表 SQL，保持与 SCHEMA.md 一致
SESSIONS_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT UNIQUE NOT NULL,
    user_id TEXT,
    title TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_thread_id ON sessions(thread_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
"""

MESSAGES_SQL = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT,
    extra TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(thread_id, seq)
);
CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id);
"""

SHORT_TERM_MEMORY_SQL = """
CREATE TABLE IF NOT EXISTS short_term_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT,
    user_id TEXT,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_stm_thread_id ON short_term_memory(thread_id);
CREATE INDEX IF NOT EXISTS idx_stm_user_id ON short_term_memory(user_id);
CREATE INDEX IF NOT EXISTS idx_stm_expires_at ON short_term_memory(expires_at);
"""


def init_schema(conn: sqlite3.Connection | str | Path) -> None:
    """
    初始化所有表。若传入 str/Path，则视为 sqlite 文件路径。
    """
    if isinstance(conn, (str, Path)):
        conn = sqlite3.connect(str(conn))
        close = True
    else:
        close = False

    try:
        conn.executescript(SESSIONS_SQL)
        conn.executescript(MESSAGES_SQL)
        conn.executescript(SHORT_TERM_MEMORY_SQL)
        conn.commit()
    finally:
        if close:
            conn.close()
