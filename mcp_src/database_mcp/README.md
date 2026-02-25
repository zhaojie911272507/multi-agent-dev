# Database MCP Server

生产级私有数据库 MCP Server，支持 **PostgreSQL**、**MySQL**，面向 AI 智能体的安全查询与 Schema 自省。

## 特性

| 能力 | 说明 |
| --- | --- |
| **防 SQL 注入** | 仅支持参数化查询（`text()` + `params`），严禁字符串拼接 |
| **只读保护** | 默认仅允许 `SELECT`，通过 `ALLOW_WRITE_OPERATIONS=true` 显式开启写操作 |
| **结果截断** | 行数限制（默认 1000）、结果大小限制（默认 1MB），防止上下文溢出 |
| **连接池** | SQLAlchemy 连接池，避免每请求新建连接 |
| **Schema 自省** | `get_schema` / `list_tables` / `describe_table` 供 AI 探索表结构 |
| **错误模糊化** | 屏蔽底层路径、堆栈等敏感信息，仅返回逻辑错误提示 |

## 工具列表

| 工具 | 描述 |
| --- | --- |
| `list_tables` | 列出所有表名，默认排除系统表 |
| `describe_table` | 获取表字段、类型、主键、索引 |
| `get_schema` | 自省整个 Schema（表、字段、外键） |
| `execute_query` | 执行参数化 SQL 查询 |

## 快速开始

### 1. 配置

```bash
cp mcp_src/database_mcp/.env.example .env
# 编辑 .env，填写 DB_HOST、DB_USER、DB_PASSWORD、DB_NAME 等
```

### 2. 启动 MCP Server（stdio）

```bash
python -m mcp_src.database_mcp.server
```

### 3. 在 Cursor / Claude Desktop 中配置

```json
{
  "mcpServers": {
    "database": {
      "command": "python",
      "args": ["-m", "mcp_src.database_mcp.server"],
      "cwd": "/path/to/langgraphtest0725",
      "env": {
        "DB_HOST": "127.0.0.1",
        "DB_PORT": "5432",
        "DB_USER": "readonly_user",
        "DB_PASSWORD": "your_password",
        "DB_NAME": "production_db"
      }
    }
  }
}
```

### 4. 与 LangGraph 集成

在 `MultiServerMCPClient` 中增加 database 服务器：

```python
client = MultiServerMCPClient({
    "database": {
        "command": "python",
        "args": ["-m", "mcp_src.database_mcp.server"],
        "transport": "stdio",
    },
})
```

## 环境变量

详见 `.env.example`，必填项：

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `DB_TYPE`: `postgresql` | `mysql`

可选：`MAX_ROWS`, `QUERY_TIMEOUT_SEC`, `ALLOW_WRITE_OPERATIONS` 等。

## 参数化查询示例

```sql
-- 查询
SELECT * FROM users WHERE id = :id AND status = :status
```

工具调用：

```json
{
  "query": "SELECT * FROM users WHERE id = :id",
  "params": "{\"id\": 123}"
}
```

## 依赖

- `sqlalchemy>=2.0.0`
- `psycopg2-binary`（PostgreSQL）
- `pymysql` 或 `mysqlclient`（MySQL）
- `python-dotenv`
