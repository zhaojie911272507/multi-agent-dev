# SQLite 记忆存储 Schema

## 设计概览

| 存储类型 | 介质 | 用途 |
|----------|------|------|
| 对话记录 | SQLite | 完整会话消息，支持按 thread 查询、分页 |
| 短期记忆 | SQLite | 最近 N 轮摘要、工作上下文、可设置 TTL |
| 长期记忆 | `memory/` 目录下 MD 文件 | 用户事实、偏好、重要结论，便于人工阅读与版本管理 |

---

## SQLite 表结构

### 1. sessions（会话表）

一个会话对应一个 LangGraph `thread_id`。

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | 自增主键 |
| thread_id | TEXT | UNIQUE NOT NULL | LangGraph thread_id |
| user_id | TEXT | | 用户标识，可选 |
| title | TEXT | | 会话标题，可自动生成 |
| created_at | TEXT | NOT NULL | ISO8601 时间戳 |
| updated_at | TEXT | NOT NULL | 最后更新时间 |

### 2. messages（消息表）

存储每条对话消息，与 sessions 通过 thread_id 关联。

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | 自增主键 |
| thread_id | TEXT | NOT NULL, INDEX | 会话标识 |
| seq | INTEGER | NOT NULL | 会话内顺序（从 0 递增） |
| role | TEXT | NOT NULL | user / assistant / system |
| content | TEXT | | 消息正文 |
| extra | TEXT | | JSON：tool_calls, tool_call_id 等 |
| created_at | TEXT | NOT NULL | ISO8601 时间戳 |

### 3. short_term_memory（短期记忆表）

近期摘要、工作上下文，支持按时间或 TTL 清理。

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | 自增主键 |
| thread_id | TEXT | INDEX | 所属会话 |
| user_id | TEXT | INDEX | 用户标识 |
| memory_type | TEXT | NOT NULL | recent_summary / working_context / tool_result_cache |
| content | TEXT | NOT NULL | 记忆内容 |
| created_at | TEXT | NOT NULL | 创建时间 |
| expires_at | TEXT | | 过期时间（ISO8601），为空表示不过期 |

---

## 长期记忆（Markdown）

目录：`memory/`（可配置，默认项目根下 `memory/`）

### 文件结构建议

```
memory/
  {user_id}/                    # 按用户分目录
    preferences.md              # 用户偏好
    facts.md                    # 用户相关事实
    {YYYY-MM-DD}_{topic}.md     # 按日期+主题的片段
```

### 单文件格式（可选 frontmatter）

```markdown
---
user_id: "user_123"
topic: "饮食偏好"
updated_at: "2025-03-05T10:00:00Z"
---

# 饮食偏好

用户偏好意大利菜，不喜辣。
```

无 frontmatter 时，文件名与目录即可表达语义。
