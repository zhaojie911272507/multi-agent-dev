# 项目结构说明

命名规范详见 [docs/NAMING_CONVENTIONS.md](NAMING_CONVENTIONS.md)。

## 目录概览

```
langgraphtest0725/
├── langgraph_src/           # LangGraph 核心示例与脚本
│   ├── graph_api/           # 图 API 示例（StateGraph、Command、条件分支等）
│   ├── prebuilt_examples/   # 预构建 Agent（React、Swarm、Supervisor）
│   ├── prebuilt_agent/      # 预构建 Agent 进阶（内存、结构化输出等）
│   ├── custom_workflow/     # 自定义工作流（原 custom_wokflow，已修正拼写）
│   ├── sql_agent/           # SQL 数据库 Agent
│   ├── examples/            # 示例（agentic_rag）
│   ├── agent_supervisor/    # 监督者模式多智能体
│   ├── hierarchical_agent_teams/   # 分层 Agent 团队
│   ├── reporter_agent/      # Reporter Agent
│   └── add_human_in_the_loop_for_tools/  # 人工审核示例
├── graph_builder_api/       # 图可视化（原 grpah_builder_api，已修正拼写）
├── crewai_src/              # CrewAI 多智能体示例
├── mcp_src/                 # MCP（Model Context Protocol）示例
├── langfuse_src/            # Langfuse 可观测性
├── persistence/             # 持久化与内存存储
├── knowledge/               # 设计模式、异步等知识库
├── streamlit_src/           # Streamlit 演示（原 streamlit-src）
├── llama_index/             # LlamaIndex 示例（原 LlamaIndex）
├── evomap_src/              # EvoMap 知识演化图谱系统
│   ├── nodes/               # 工作流节点
│   │   ├── knowledge_collector.py   # 知识采集
│   │   ├── knowledge_analyzer.py    # 知识分析（实体/关系提取）
│   │   ├── graph_builder.py         # 演化图谱构建
│   │   ├── trend_predictor.py       # 趋势预测
│   │   └── report_generator.py      # 报告生成
│   ├── config.py            # 配置（模型、阈值）
│   ├── models.py            # 数据模型（State、实体、关系）
│   ├── utils.py             # 工具函数
│   ├── main.py              # 工作流组装 + CLI 入口
│   └── PRD.md               # 产品需求文档
├── smalltoolscripts/        # 小工具脚本
├── test/                    # 测试与示例脚本
└── docs/                    # 文档
```

## 命名修正记录

| 原名称 | 修正后 | 说明 |
|--------|--------|------|
| `grpah_builder_api` | `graph_builder_api` | 拼写错误 |
| `custom_wokflow` | `custom_workflow` | 拼写错误 |
| `GraphAPI` | `graph_api` | PEP 8：包名 snake_case |
| `Prebuilt` | `prebuilt_examples` | PEP 8：避免与 prebuilt_agent 冲突 |
| `SQLAgent` | `sql_agent` | PEP 8：包名 snake_case |
| `AgenticRAG` | `agentic_rag` | PEP 8：包名 snake_case |
| `HierarchicalAgentTeams` | `hierarchical_agent_teams` | PEP 8：包名 snake_case |
| `ReporterAgent` | `reporter_agent` | PEP 8：包名 snake_case |
| `add-a-human-in-the-loop-for-tools` | `add_human_in_the_loop_for_tools` | PEP 8：包名禁用连字符 |
| `streamlit-src` | `streamlit_src` | PEP 8：包名禁用连字符 |
| `LlamaIndex` | `llama_index` | PEP 8：包名 snake_case |
| `CrewAI-LangGraph` | `crewai_langgraph` | PEP 8：包名 snake_case + 禁用连字符 |
| `createDeletgationTasks` | `create_delegation_tasks` | PEP 8 + 拼写修正 |
| `createWorkerAgent` | `create_worker_agent` | PEP 8 |
| `客服流程.py` | `customer_service_flow.py` | PEP 8：模块名 snake_case |
| `信号量.md` | `semaphore.md` | 中文→英文（asyncio_module） |
| `贝叶斯.md` | `bayesian.md` | 中文→英文（知识库） |
| `ConditionalBranchingRouteToMultipleNode_validate渲染.png` | `conditional_branching_route_to_multiple_node_validate_render.png` | 中文→英文 + snake_case |

## 已移除的冗余文件

### 全局
- `graph_builder_api/uuid_test.py`：trivial 测试，无保留价值

### langgraph_src 模块
- `langgraph_src/examples/SQLAgent/`：整个目录已删除，功能已合并至主 `sql_agent/`
- `langgraph_src/graph_api/exampleSend.py`：空文件
- `langgraph_src/graph_api/test_astream_message.py`：未实现的 stub 测试
- `langgraph_src/prebuilt_agent/add_a_custom_prompt/getweather.py`：与 `prebuilt_agent/getweather.py` 重复，已统一
