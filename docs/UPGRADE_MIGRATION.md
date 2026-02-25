# 依赖升级与迁移说明

## 升级概览

项目已升级至 **LangGraph 1.x** 和 **LangChain 1.x**。

## 主要变更

### 1. 已完成的脚本适配

- **`langgraph_src/sql_agent/prebuilt_agent/create_react_agent.py`**：`create_react_agent` → `create_agent`，`prompt` → `system_prompt`
- **`langgraph_src/examples/agentic_rag/create_a_retriever_tool.py`**：`langchain.tools.retriever` → `langchain_core.tools.retriever`
- **`langgraph_src/examples/agentic_rag/preprocess_documents.py`**：移除未使用的 `default_header_template`、`print_glsl` 导入

### 2. 项目结构修正（2025-02）

- `grpah_builder_api` 已重命名为 `graph_builder_api`
- `custom_wokflow` 已重命名为 `custom_workflow`
- `knowledge/ai_design_mode/` 下中文文件名已统一为英文（中文保留于代码注释）：
  - 适配器 → `adapter.py`，适配器2 → `adapter_v2.py`
  - 代理模式 → `proxy_pattern.py`，责任链 → `chain_of_responsibility.py`
  - 门面模式 → `facade_pattern.py`，策略 → `strategy.py`，装饰器 → `decorator.py`
  - 状态模式 → `state_pattern.py`，单例 → `singleton.py`
  - 管道-过滤器模式 → `pipeline_filter_pattern.py`，组合模式 → `composite_pattern.py`
  - 享元模式AI模型共享 → `flyweight_ai_model_sharing.py`
  - AI任务异步编排 → `ai_task_async_orchestration.py`
  - 几个模式的组合示例 → `combined_patterns_example.py`

### 3. 仍需迁移的脚本（使用 create_react_agent）

以下文件仍在使用已弃用的 `langgraph.prebuilt.create_react_agent`，可逐步迁移为 `langchain.agents.create_agent`：

| 文件 | 迁移要点 |
|------|----------|
| `prebuilt_examples/create_react_agent/create_react_agent_demo.py` | `prompt` → `system_prompt` |
| `prebuilt_agent/*.py` | 同上 |
| `agent_supervisor/*.py` | 同上 |
| `hierarchical_agent_teams/*.py` | 同上 |
| `prebuilt_examples/create_swarm/*.py` | 同上 |
| `mcp_src/example/agent_client.py` | 同上 |

**迁移示例：**
```python
# 旧写法（已弃用）
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(llm, tools, prompt="You are helpful")

# 新写法
from langchain.agents import create_agent
agent = create_agent(llm, tools, system_prompt="You are helpful")
```

### 4. 依赖版本变化

| 包 | 旧版本 | 新版本 |
|----|--------|--------|
| langgraph | 0.2.x - 0.6.x | >=1.0.0 |
| langchain | 0.3.x | >=1.0.0 |
| langchain-core | 0.3.x | 1.2.x |
| langchain-openai | 0.3.x | 1.1.x |
| langchain-community | 0.3.x | 0.4.x |
| langchain-mcp-adapters | 0.1.x | >=0.2.0 |
| langgraph-supervisor | - | >=0.0.20 |

### 5. 已知兼容性说明

- **langchain-deepseek**：当前与 langchain-core 1.x 有版本冲突，使用 DeepSeek 时需留意
- **langchain-milvus**：与 langchain-core 1.x 可能不兼容
- **CrewAI**：保持 `<1.0.0` 以兼容现有代码

### 6. 安装

```bash
pip install -r requirements.txt
```
