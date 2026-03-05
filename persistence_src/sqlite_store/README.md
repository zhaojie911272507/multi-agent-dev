# SQLite 记忆存储

对话与短期记忆存 SQLite（`persistence.db`），长期记忆存 `memory/*.md`。

## 表结构

详见 [SCHEMA.md](./SCHEMA.md)。

## 快速使用

```python
from persistence_src.sqlite_store import (
    ConversationStore,
    ShortTermMemoryStore,
    LongTermMemoryStore,
)

# 对话
conv = ConversationStore("persistence.db")
conv.append_message("thread-1", "user", "你好")
conv.get_messages("thread-1")

# 短期记忆（可设 expires_at 做 TTL）
stm = ShortTermMemoryStore("persistence.db")
stm.put("thread-1", "user_1", "recent_summary", "最近讨论了天气")
stm.get(thread_id="thread-1", limit=5)

# 长期记忆（MD 文件）
ltm = LongTermMemoryStore("memory")
ltm.put("user_1", "preferences.md", "用户偏好意大利菜", {"topic": "饮食"})
ltm.get("user_1", "preferences.md")
```

运行示例：`python -m persistence_src.sqlite_store.example_usage`

## 与 Tool Orchestrator 集成

创建编排器时传入 `short_term_store`、`long_term_store`，并在 `config.configurable` 中提供 `thread_id`、`user_id`，即可将 SQLite/MD 记忆注入 agent 上下文。
