# AgentScope 动态组装 MCP + Skill 示例

一个完整、可直接运行的 [AgentScope](https://github.com/agentscope-ai/agentscope) 示例，
演示如何在**不写死任何服务**的前提下，从配置动态组装出「MCP 工具 + Skill 技能 + LLM」的智能体。

## 特性

- **配置驱动**：`config/mcp_servers.yaml` 声明要连接的 MCP 服务，新增/停用服务只改配置不改代码
- **动态连接 MCP**：运行时逐条创建 `MCPClient`、建立 stdio 连接、自动暴露工具
  （工具名格式 `mcp__{客户端名}__{工具名}`），支持 `enable_tools` / `disable_tools` 动态裁剪
- **动态加载 Skill**：扫描 `skills/` 目录下的 `SKILL.md`（frontmatter 声明 `name` / `description`），
  智能体通过内置 `Skill` 查看工具读取技能说明后按流程执行
- **运行时增删工具**：演示 `Toolkit.add_tool()` / `remove_tool()` 在对话过程中动态挂载/卸载能力
- **完整生命周期**：结束时统一 `close()` 释放 MCP 服务子进程

## 目录结构

```
agentscope_mcp_skill_demo/
├── run_demo.py                 # 运行入口（组装 → 自动演示 → 交互对话）
├── requirements.txt
├── config/
│   └── mcp_servers.yaml        # MCP 服务配置（动态组装的数据源）
├── servers/
│   ├── math_server.py          # MCP 服务端：四则运算（FastMCP/stdio）
│   └── weather_server.py       # MCP 服务端：天气查询（含被裁剪的工具）
├── skills/
│   └── data_analysis_skill/
│       └── SKILL.md            # 技能定义：数字汇总与报告流程
└── assembly/                   # 动态组装核心组件
    ├── config_loader.py        # YAML 配置 → AgentScope MCP 配置对象
    ├── mcp_manager.py          # 动态连接 MCP 服务、管理生命周期
    ├── skill_loader.py         # 动态扫描 skills 目录
    └── agent_builder.py        # Toolkit + Agent 组装
```

## 运行

```bash
# 1. 安装依赖（agentscope 2.0.6 需要 mcp>=1.24,<2.0，否则会 ImportError）
pip install -r requirements.txt

# 2. 配置 API Key（仓库根目录已有 .env 含 DEEPSEEK_API_KEY，直接复用）
#    echo "DEEPSEEK_API_KEY=sk-xxx" > ../.env

# 3. 运行示例
python run_demo.py
```

运行后会依次：

1. 从 YAML 读取并连接 `math`、`weather` 两个 MCP 服务
2. 加载 `data_analysis_skill` 技能
3. 自动演示「MCP 计算」「技能 + MCP 协同报告」「运行时增删工具」三个场景
4. 进入交互模式（输入问题回车提问，`q` 退出）

## 核心概念速览

| 概念 | 说明 |
| --- | --- |
| `MCPClient` | AgentScope 的统一 MCP 客户端；stdio 连接必须 `is_stateful=True` 并显式 `connect()` |
| `StdioMCPConfig` | stdio 传输配置（command / args / env）；另有 `HttpMCPConfig` 用于 HTTP/SSE |
| `Toolkit` | 工具、MCP 客户端、技能的统一容器，是 Agent 工具能力的唯一来源 |
| `ToolGroup` | 工具分组；basic 组默认激活，其它组可用内置 `ResetTools` 元工具动态激活/停用 |
| Skill | 目录下的 `SKILL.md`（frontmatter: name/description + 正文指令）；**不是**可直接调用的工具 |
| `FunctionTool` | 把普通 Python 函数包装成工具，支持运行时 `add_tool` / `remove_tool` |

## 版本说明

- 本示例基于 **agentscope 2.0.6** 实测（2026-08）：
  - 无 `init_chat_model` 快捷函数，模型按厂商直接实例化（如 `DeepSeekChatModel`）
  - MCP 工具名为 `mcp__{客户端名}__{工具名}`
  - 默认权限模式 `DEFAULT` 会在每次工具调用前询问用户；演示用 `PermissionMode.DONT_ASK`
- **权限坑**：MCP 工具默认权限是 ASK（要求人工确认），`DONT_ASK` 模式下无人确认会直接
  拒绝调用，必须为每个 MCP 工具注册 allow 规则（`rule_content=None` 匹配所有调用）；
  运行时用 `Toolkit.add_tool()` 动态新增的工具同样要同步注册权限规则
  （示例中这两处都已演示并注释）
- **mcp 版本坑**：agentscope 2.0.6 导入 `mcp.client.streamable_http.streamable_http_client`，
  该 API 在 mcp **1.24.0** 才引入；mcp 1.13 及以下会 ImportError，请升级

## 相关参考

- [AgentScope 文档](https://docs.agentscope.io/)
- 仓库内同主题对比示例：[mcp_skill_demo/](../mcp_skill_demo)（LangGraph 版）
