# Tool Orchestrator with State Memory

精准的工具调用与状态记忆管理模块，基于 LangGraph 编排 Skills 与 MCP 工具调用。

---

## 技术选型评估

### LangGraph 是否合理？

**结论：采用 LangGraph 是合理的**，且在本项目中为推荐方案。

| 维度 | LangGraph | 替代方案 | 说明 |
|------|-----------|----------|------|
| **工具编排** | 原生 `ToolNode` 与 conditional edges，支持多轮 tool call | LangChain Agent / CrewAI | 图结构更清晰，工具调用与状态更新可精确控制 |
| **状态持久化** | 原生 `Checkpointer`（如 `InMemorySaver`）支持 `thread_id` 多轮对话 | 需自行实现 | 开箱即用，`config.configurable.thread_id` 即可恢复会话 |
| **语义记忆** | `langgraph.store.memory.InMemoryStore` 与 `Store` 协议 | 与 persistence_src 现有方案一致 | 可检索用户偏好、上下文，注入 agent |
| **MCP 集成** | `langchain_mcp_adapters.MultiServerMCPClient` 直接提供 tools | 需手动封装 | 项目已使用，无需额外工作 |
| **Skills 集成** | 将 Skill 封装为 LangChain `@tool` 即可 | 同上 | 审计 Skill 等均可作为 tool 注册 |
| **可观测性** | 与 Langfuse 等 callback 兼容 | 通用 | 项目已有实践 |
| **可扩展性** | 节点可拆分、可替换、可加 human-in-the-loop | 受限于框架 | 适合复杂流程演进 |

### 替代方案简要对比

1. **纯 LangChain Agent**：更轻量，但无内置 checkpoint、无图级控制，状态管理需自建。
2. **CrewAI**：强调多 Agent 协作，工具调用为附属能力，与本模块「单 Agent + 多工具」的目标不完全一致。
3. **自研状态机**：可控性最高，但需重复实现持久化、工具路由、消息合并等逻辑。

**推荐**：沿用 LangGraph，与 `persistence_src`（InMemoryStore）、`mcp_src`（MCP 工具）、`skills_src`（审计等 Skills）形成统一技术栈。

---

## 架构概览

```
[User Input] --> [call_model] --> [should_continue?]
                                      |
                    +-----------------+------------------+
                    |                                     |
              [tools] (ToolNode)                    [END]
                    |
                    +--> [call_model] (loop)
```

- **call_model**：LLM 决策是否调用工具，输出 `tool_calls`。
- **tools**：`ToolNode` 执行 skills + MCP 工具，将结果写回 `messages`。
- **Checkpointer**：按 `thread_id` 保存对话状态，实现多轮记忆。
- **Store（可选）**：语义记忆检索，将用户偏好等注入 system 或 context。

---

## 使用示例

```python
import asyncio
from persistence_src.tool_orchestrator import create_orchestrator

async def main():
    # 创建编排器：自动注册 skills + MCP 工具（create_orchestrator 为 async）
    orchestrator = await create_orchestrator(
        mcp_servers={"math": {"command": "python", "args": ["path/to/math_server.py"], "transport": "stdio"}},
        enable_audit_skill=True,
    )
    # 多轮对话（同一 thread_id 保持状态）
    config = {"configurable": {"thread_id": "user-123"}, "recursion_limit": 15}
    response = await orchestrator.ainvoke(
        {"messages": [{"role": "user", "content": "帮我做一次发票校验"}]},
        config,
    )

asyncio.run(main())
```

或直接运行示例：`python -m persistence_src.tool_orchestrator.example_run`

---

## 模块结构

| 文件 | 职责 |
|------|------|
| `tool_registry.py` | 注册 Skills（如 financial-audit）、MCP 工具，统一暴露为 LangChain tools |
| `state_schema.py` | 扩展状态（含 tool_call_trace、memory_context 等） |
| `agent_graph.py` | 构建 LangGraph StateGraph，集成 ToolNode、Checkpointer、可选 Store |
| `memory_integration.py` | 将 InMemoryStore 检索结果注入 agent context |
| `__init__.py` | 导出 `create_orchestrator` 等公共接口 |
| `example_run.py` | 可运行示例（`python -m persistence_src.tool_orchestrator.example_run`） |
