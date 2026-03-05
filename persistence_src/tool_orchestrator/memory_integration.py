"""
Memory Integration: 将记忆检索结果注入 agent 上下文。

支持两种后端：
1. LangGraph Store（如 InMemoryStore）：语义检索
2. SQLite + MD：短期记忆从 short_term_memory 表，长期从 memory/*.md
"""

from typing import Any

# Store 协议：需实现 search(namespace, query, limit) -> list of records
StoreLike = Any


def build_memory_context(
    store: StoreLike,
    namespace: tuple[str, ...],
    query: str,
    limit: int = 3,
) -> str:
    """
    从 Store 检索与 query 相关的记忆，拼接为上下文字符串。
    适用于 InMemoryStore 等实现 search 的 Store。
    """
    if store is None:
        return ""

    try:
        results = store.search(namespace, query=query, limit=limit)
    except Exception:
        return ""

    if not results:
        return ""

    parts = []
    for i, r in enumerate(results, 1):
        val = r.value if hasattr(r, "value") else r
        if isinstance(val, dict):
            text = val.get("content") or val.get("food_preference") or str(val)
        else:
            text = str(val)
        parts.append(f"[{i}] {text}")

    return "Previous context:\n" + "\n".join(parts)


def build_memory_context_from_sqlite(
    short_term_store: Any,
    long_term_store: Any,
    thread_id: str | None,
    user_id: str | None,
    limit_short: int = 5,
    limit_long: int = 3,
) -> str:
    """
    从 SQLite 短期记忆 + memory/*.md 长期记忆构建上下文。

    Args:
        short_term_store: ShortTermMemoryStore 实例
        long_term_store: LongTermMemoryStore 实例
        thread_id: 当前会话 ID
        user_id: 用户 ID
        limit_short: 短期记忆条数
        limit_long: 长期记忆文件数量（取前 N 个文件的 content）

    Returns:
        格式化后的 context 字符串
    """
    parts = []

    # 短期记忆：最近摘要、工作上下文
    if short_term_store and (thread_id or user_id):
        rows = short_term_store.get(
            thread_id=thread_id,
            user_id=user_id,
            limit=limit_short,
        )
        if rows:
            for r in rows:
                parts.append(f"[短期-{r.get('memory_type', '')}] {r.get('content', '')}")

    # 长期记忆：从 MD 文件读取
    if long_term_store and user_id:
        files = long_term_store.list_files(user_id=user_id)
        for i, f in enumerate(files[:limit_long]):
            entry = long_term_store.get(user_id, f["filename"])
            if entry and entry.get("content"):
                parts.append(f"[长期-{f['filename']}] {entry['content'][:500]}")

    if not parts:
        return ""
    return "Memory context:\n" + "\n".join(parts)
