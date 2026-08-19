# pi_mcp_skill_demo —— Pi 动态组装 MCP 与 Skill 示例

一个**完整可运行**的示例：使用 [Pi](https://pi.dev)（[`pi-py-agent-core`](https://pypi.org/project/pi-py-agent-core/)，
[`@earendil-works/pi-agent-core`](https://github.com/earendil-works/pi) 的 Python 移植版）在运行时**动态组装 MCP 服务器（工具）与 Skill（技能）**。

全部由 YAML 配置驱动：**新增 MCP 服务器 / 新增技能，无需修改任何 Python 代码**。

## 1. 它演示了什么

| 概念 | 本示例中的含义 | 动态在哪 |
| --- | --- | --- |
| **MCP** | 独立的 MCP 服务器进程（math / weather），暴露标准 MCP 工具 | 运行时按 `config/mcp_servers.yaml` 拉起进程、`list_tools()` 自动发现工具、按配置裁剪，代码里没有写死任何一个工具名 |
| **Skill** | 一个 `SKILL.md` 文件（agentskills.io 标准）：frontmatter 声明 `name` / `description`，正文是执行流程 | 运行时扫描 `skills/` 目录；**元数据优先、按需懒加载**：系统提示词只放技能摘要，模型觉得任务匹配时调用内置 `read_skill` 工具读全文 |
| **Pi 运行时** | `pi_agent_core.Agent`（ReAct 循环 + 工具协议 `AgentTool`）+ `pi_ai.Model`（DeepSeek，OpenAI-compatible） | Agent 的 `state.tools` 是普通 list，对话中 append / remove 立即生效（运行时增删工具） |

Pi 本身不内置 MCP——`assembly/mcp_manager.py` 就是桥接层：把 MCP 工具包装成 Pi 的 `AgentTool`（工具名 `mcp__{服务}__{工具}`），任何符合 MCP 标准的服务都能零代码接入。

## 2. 架构

```
 config/mcp_servers.yaml  ──►  MCPManager ──► [mcp__math__add, ..., mcp__weather__query_weather]
                                            （stdio 连接 → 工具发现 → 裁剪 → 包装成 AgentTool）
                                                        │
 skills/data_analysis_skill/SKILL.md ──► load_skill_components ──► 技能摘要（进 system prompt）
                                                        │              + read_skill 懒加载工具
                                                        ▼
                                          Agent（pi_agent_core）
                                            system_prompt = 角色 + <available_skills> 摘要
                                            tools = [MCP 工具..., read_skill]
                                            model = DeepSeek（pi_ai / openai-completions）
                                                        │
                            ReAct 循环：模型 ⇄ 工具（MCP 调用经长存 ClientSession 转发）
```

## 3. 目录结构

```
pi_mcp_skill_demo/
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
    ├── config_loader.py        # YAML 配置 → 服务配置对象
    ├── mcp_manager.py          # ★ MCP 桥接层：动态连接 / 发现 / 适配成 AgentTool
    ├── skill_loader.py         # 技能扫描 + 懒加载（摘要注入 + read_skill 工具）
    └── agent_builder.py        # Model + Agent + 普通函数动态转工具
```

## 4. 运行

```bash
# 1. 安装依赖（pi-py-agent-core 0.84 需要 python >= 3.12）
pip install -r requirements.txt

# 2. 配置 API Key（仓库根目录已有 .env 含 DEEPSEEK_API_KEY，直接复用）
#    echo "DEEPSEEK_API_KEY=sk-xxx" > ../.env

# 3. 运行示例
python run_demo.py
```

运行后会依次：

1. 从 YAML 读取并连接 `math`、`weather` 两个 MCP 服务（发现 + 裁剪工具）
2. 加载 `data_analysis_skill` 技能（摘要进提示词，全文懒加载）
3. 自动演示三个场景：
   - **MCP 计算**：`(12 + 34) * 5 / 6` → 模型调用 `mcp__math__*`
   - **技能 + MCP 协同**：销售额分析报告 → 模型先 `read_skill` 读技能全文，再按技能流程调用计算工具
   - **运行时增删工具**：对话中动态挂载 `get_server_time` 函数工具，验证后卸载
4. 进入交互模式（输入问题回车提问，`q` 退出）

## 5. 核心概念速览

| 概念 | 说明 |
| --- | --- |
| `AgentTool` | Pi 的工具契约（鸭子类型协议）：`name` / `description` / `parameters`(JSON Schema) / `async execute(...) → AgentToolResult`。MCP 工具、read_skill、普通函数工具都按它实现 |
| `AgentToolResult` | 工具返回值：`content=[TextContent(text=...)]` 发给模型 |
| 元数据优先 | 系统提示词里只有 `<available_skills>` 摘要（name+description），全文靠 `read_skill` 按需读取——Pi 上游对 skills 的标准做法，省 token |
| `get_api_key` | Agent 的钩子：Pi 循环调 LLM 前先调用它拿 API Key（从 `DEEPSEEK_API_KEY` 环境变量取） |
| 长存 session | MCP 连接用 `AsyncExitStack` 管理，从组装到 `close_all()` 一直存活，对话期间每次工具调用走同一会话 |

## 6. 已知问题与兼容兜底

**pi_ai 0.84.1 的序列化 bug**（本示例在开发中踩到并已绕开）：

`pi_ai` 的 OpenAI provider 在把 assistant 消息转成请求体时，遍历 content
块只处理 `ToolCall`，**`text_parts` 从未被填充**——文本块被完全丢弃。
后果：历史里**不带 tool_call 的纯文本 assistant 消息**（模型的最终答复等）
序列化后变成空消息，DeepSeek 等 OpenAI 兼容端点会返回
`400 Invalid assistant message: content or tool_calls must be set`，
且错误消息会留在历史里造成"一次出错、永久雪崩"。

本示例通过 Pi 的 `transform_context` 钩子（见
[assembly/agent_builder.py](assembly/agent_builder.py) 的
`_clean_messages_for_openai`）在每次 LLM 请求前剔除这类消息：
工具调用链（toolCall → toolResult）完整保留，对话推理过程不受影响。
该 bug 属库缺陷，若上游修复可移除这段兜底。

## 7. 相关

- 仓库内同类示例：[agentscope_mcp_skill_demo](../agentscope_mcp_skill_demo/)（AgentScope）、[mcp_skill_demo](../mcp_skill_demo/)（LangGraph）
- Pi 官方仓库：[earendil-works/pi](https://github.com/earendil-works/pi)（TypeScript monorepo）、[encyc/pi-py](https://github.com/encyc/pi-py)（Python 移植）
