"""
示例：SQLite 对话存储 + 短期/长期记忆。

运行：python -m persistence_src.sqlite_store.example_usage
"""
from pathlib import Path

# 使用项目根目录下的 persistence.db 和 memory/
ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "persistence.db"
MEMORY_DIR = ROOT / "memory"


def main():
    from persistence_src.sqlite_store import (
        ConversationStore,
        ShortTermMemoryStore,
        LongTermMemoryStore,
    )

    # 1. 对话存储
    conv = ConversationStore(DB_PATH)
    conv.ensure_session("thread-1", user_id="user_123", title="示例会话")
    conv.append_message("thread-1", "user", "你好，请介绍一下自己")
    conv.append_message("thread-1", "assistant", "我是 AI 助手，很高兴为您服务。")
    msgs = conv.get_messages("thread-1")
    print("Messages:", [m["role"] + ": " + m["content"][:30] + "..." for m in msgs])

    # 2. 短期记忆
    stm = ShortTermMemoryStore(DB_PATH)
    stm.put("thread-1", "user_123", "recent_summary", "用户询问了自我介绍")
    rows = stm.get(thread_id="thread-1", limit=3)
    print("Short-term:", [r["content"] for r in rows])

    # 3. 长期记忆（MD 文件）
    ltm = LongTermMemoryStore(MEMORY_DIR)
    ltm.put("user_123", "preferences.md", "用户偏好意大利菜，不喜辣。", {"topic": "饮食"})
    entry = ltm.get("user_123", "preferences.md")
    print("Long-term:", entry["content"][:50] + "..." if entry else "N/A")


if __name__ == "__main__":
    main()
