# LangGraph 调用外部 HTTP MCP + Skill 示例

一个完整的端到端示例：**LangGraph Agent 同时调用「外部 HTTP 类 MCP Server」和「本地 Skill」**。

## 目录结构

```
http_mcp_skill_demo/
├── mcp_server.py            # 外部 HTTP MCP 服务端（FastMCP + Streamable HTTP）
├── skills/
│   └── stock_analysis_skill/
│       ├── skill.yaml       # skill 声明：名称 / 描述 / 触发词 / 实现入口
│       └── orchestrator.py  # skill 实现（确定性估值规则）
├── langgraph_agent.py       # 主示例：LangGraph Agent 调用上面两类能力
└── README.md
```

## 运行步骤

### 1. 启动外部 HTTP MCP 服务端（独立终端）

```bash
python mcp_server.py
# 监听 http://127.0.0.1:8000/mcp
```

### 2. 运行 LangGraph Agent（另一个终端）

```bash
python langgraph_agent.py
```

Agent 会依次回答两个问题：

| 问题 | 走的链路 |
|------|----------|
| 今天上海和北京的天气怎么样？ | 外部 HTTP MCP（远程进程网络调用） |
| 帮我分析一下 AAPL 的估值，当前股价 210 | 本地 Skill（stock-analysis） |

## 原理说明

```
┌──────────────────────────── LangGraph Agent ────────────────────────────┐
│  create_react_agent(llm, tools=[MCP工具..., Skill工具...])               │
│      │                                                                   │
│      ├── MCP 工具（远程）：通过 langchain-mcp-adapters 连接外部 HTTP 服务 │
│      │     MultiServerMCPClient({"weather": {url, transport: "http"}})   │
│      │     → get_weather / get_exchange_rate                             │
│      │                                                                   │
│      └── Skill 工具（本地）：扫描 skills/*/skill.yaml，动态加载实现入口    │
│            skill.yaml(description + triggers) → 包装成 @tool              │
│            → stock_analysis                                              │
└──────────────────────────────────────────────────────────────────────────┘
```

- **MCP 是"进程间"协议**：Agent 与 MCP Server 完全解耦，Server 可以部署在任何机器上，
  只要暴露 HTTP 端点即可（本示例用 FastMCP `mcp.run(transport="http")` 暴露）。
- **Skill 是"能力包"**：`skill.yaml` 声明能力（名称/描述/触发词），Python 模块实现逻辑，
  包装成工具后由 LLM 根据 description 自主决定何时调用 —— 与 `skills_src/audit_skill` 同一模式。
- **两者对 Agent 无差别**：最终都是 `BaseTool`，ReAct 循环里 LLM 自行选择调用。

## 扩展点

- 连接多个 HTTP MCP：在 `MultiServerMCPClient` 的 dict 里加一组 `{url, transport}` 即可；
  同名工具可用 `tool_name_prefix=True` 加前缀区分。
- HTTP 鉴权：`{"url": ..., "transport": "http", "headers": {"Authorization": "Bearer xxx"}}`。
- 新增 skill：在 `skills/` 下复制一个目录，写 `skill.yaml`（声明）+ 实现模块即可，
  `langgraph_agent.py` 会自动扫描加载。
