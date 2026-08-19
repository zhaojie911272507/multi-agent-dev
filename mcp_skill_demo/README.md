# mcp_skill_demo —— LangGraph 动态组装 MCP 与 Skill 示例

一个**完整可运行**的示例：使用 LangGraph 在运行时动态组装 **MCP 服务器（工具）** 与 **Skill（技能）**，
全部由 yaml 配置驱动，新增技能 / 新增 MCP 服务器**无需修改任何 Python 代码**。

## 1. 它演示了什么

| 概念 | 本示例中的含义 | 动态在哪 |
|---|---|---|
| **MCP** | 独立的 MCP 服务器进程（math / weather），暴露标准 MCP 工具 | 运行时按 `config/mcp_servers.yaml` 拉起进程、自动发现工具，代码里没有写死任何一个工具 |
| **Skill** | 一个 yaml 声明的能力：触发规则 + 依赖的 MCP 服务器 + 系统提示词 | 运行时读取 `config/skills/*.yaml`，一个文件 = 一个技能，增删技能零代码 |
| **LangGraph** | 路由节点 + 每个技能一个"微型 Agent 节点"组成的图 | 图的结构在运行时根据装配结果**动态生成**，配置有什么，图上就有什么 |

## 2. 架构

```
                         ┌────────────────────────────────────────┐
   config/mcp_servers.yaml  ──►  MCPManager ──► {math: [add, ...], weather: [get_weather]}
                         └────────────────────────────────────────┘
                                              │ 工具（按服务器分组）
                                              ▼
   config/skills/*.yaml  ──►  SkillLoader ──► [math, weather, greeting] 技能列表
                                              │ （按技能声明绑定工具）
                                              ▼
                                  GraphBuilder ──► 编译 LangGraph
                                              │
┌─────────────────────────────────────────────────────────────────────┐
│  START ─► router ─► skill_math    (微型 Agent：LLM ⇄ ToolNode[数学工具])  ─► END │
│            │  └──► skill_weather  (微型 Agent：LLM ⇄ ToolNode[天气工具])  ─► END │
│            └────► skill_greeting  (无工具，单轮回复 / 兜底)               ─► END │
└─────────────────────────────────────────────────────────────────────┘
```

- **路由节点**：先按关键词快筛（零成本），未命中且配置了 LLM 时让 LLM 在技能清单里做意图识别
- **技能节点**：每个技能在运行时被编译成一个独立的微型 Agent 子图（模型 ⇄ ToolNode），再作为节点挂进总图——"把图组装进图"
- **兜底**：路由失败自动落到 greeting 技能，任何输入都有回应

## 3. 目录结构

```
mcp_skill_demo/
├── README.md                        # 本文档
├── requirements.txt                 # 示例依赖
├── run_demo.py                      # 一键运行入口
├── config/                          # ★ 全部动态配置在这里
│   ├── mcp_servers.yaml             #   MCP 服务器注册表（支持 stdio / streamable_http）
│   └── skills/                      #   技能定义（一个 yaml = 一个技能）
│       ├── math_skill.yaml          #     数学计算（依赖 math 服务器）
│       ├── weather_skill.yaml       #     天气查询（依赖 weather 服务器）
│       └── greeting_skill.yaml      #     打招呼 / 兜底（不依赖任何服务器）
├── servers/                         # 演示用 MCP 服务器（标准 FastMCP，独立进程）
│   ├── math_server.py               #   四则运算工具
│   └── weather_server.py            #   天气查询工具（模拟数据）
└── assembly/                        # 动态装配核心包
    ├── config_loader.py             #   读 yaml + ${DEMO_DIR} 占位符解析
    ├── mcp_manager.py               #   动态连接 MCP、发现工具（第 1 步）
    ├── skill_loader.py              #   技能装配：按名绑定工具（第 2 步）
    ├── router.py                    #   双路由：关键词 / LLM 意图识别
    ├── graph_builder.py             #   动态构图：路由 + 技能子图（第 3 步）
    ├── models.py                    #   Skill 数据模型
    └── main.py                      #   编排与交互入口
```

## 4. 运行

```bash
cd mcp_skill_demo

# 可选：配置 LLM（不配置也能跑，自动进入无 LLM 演示模式）
# echo "DEEPSEEK_API_KEY=sk-xxxx" > .env

python run_demo.py
```

运行后会打印**装配清单**（MCP 服务器 → 工具 → 技能 → 图节点），然后进入交互模式：

```
装配清单（动态生成）
======================================================================
MCP 服务器: ['math', 'weather']
  └─ math: ['add', 'subtract', 'multiply', 'divide']
  └─ weather: ['get_weather']
技能 -> 图节点 -> 工具:
  └─ math  ->  skill:math  ->  ['add', 'subtract', 'multiply', 'divide']
  └─ weather  ->  skill:weather  ->  ['get_weather']
  └─ greeting  ->  skill:greeting  ->  []
======================================================================

你> 帮我计算 (3 + 5) × 12
助手> (3 + 5) × 12 = 8 × 12 = **96**。（先执行加法 3+5=8，再执行乘法 8×12=96。）
```

试试这几个问题：`你好呀` / `帮我计算 (3 + 5) × 12` / `北京天气怎么样？` / `你会做什么？`

## 5. 配置说明

### 5.1 MCP 服务器注册表（`config/mcp_servers.yaml`）

```yaml
servers:
  math:                                  # 服务器名（技能通过它引用）
    command: python                      # stdio：启动命令
    args: ["${DEMO_DIR}/servers/math_server.py"]   # ${DEMO_DIR} 自动替换为示例根目录
    transport: stdio
  # remote_example:                      # HTTP 远程服务器写法：
  #   url: "http://localhost:8000/mcp/"
  #   transport: "streamable_http"
```

### 5.2 技能定义（`config/skills/*.yaml`）

```yaml
name: math              # 技能名（图节点 = skill_math）
description: 数学计算   # 给 LLM 路由做意图判断
triggers: [计算, math]  # 关键词路由触发词
mcp_servers: [math]     # 依赖的服务器名 -> 自动绑定其全部工具
system_prompt: |        # 技能 Agent 的系统提示词
  你是一位数学计算助手……
```

## 6. 扩展：加一个新技能 / 新 MCP，只改配置

**加一个 MCP 服务器**（比如数据库）：写一个 FastMCP 服务端 → 在 `mcp_servers.yaml` 加一段配置。
**加一个技能**：在 `config/skills/` 放一个 yaml，声明依赖的服务器名。其他什么都不用动，重新运行即自动生效。

## 7. 两种路由模式

| 模式 | 条件 | 说明 |
|---|---|---|
| 关键词路由 | 无 API Key（默认） | `KeywordRouter` 按 `triggers` 包含匹配，零依赖零成本 |
| LLM 路由 | 配置 `DEEPSEEK_API_KEY` | 先关键词快筛，未命中时让 LLM 在技能清单中选（工具 schema 方式），更准确 |

## 8. 常见问题

- **进程起不来 / 工具为空**：确认 `mcp_servers.yaml` 中 `args` 用的是 `${DEMO_DIR}` 或绝对路径；单独运行 `python servers/math_server.py` 验证服务端本身正常。
- **想在子图里换模型**：改 `assembly/main.py` 的 `create_llm()`，其余逻辑不变。
- **流式输出**：`graph.astream(...)` 即可，装配流程不受影响。
