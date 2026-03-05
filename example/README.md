# 示例启动脚本

本目录包含 README 中各类运行示例的统一启动入口，可从项目根目录执行：

```bash
# LangGraph 基础示例
python example/run_langgraph_demo.py

# 分层 Agent 团队（文档写作）
python example/run_document_writing_team.py

# 分层 Agent 团队（研究团队）
python example/run_research_team.py

# 监督者模式多智能体
python example/run_agent_supervisor.py

# Reporter Agent
python example/run_reporter_agent.py

# EvoMap 知识演化图谱
python example/run_evomap.py

# MCP Agent（需先启动 MCP 服务器）
python example/run_mcp_agent.py

# CrewAI 示例
python example/run_crewai.py

# LlamaIndex 示例（百炼 Qwen，需 DASHSCOPE_API_KEY）
python example/run_llama_index_demo.py

# Tool Orchestrator（MCP + Skills 编排，需 DEEPSEEK_API_KEY）
python -m persistence_src.tool_orchestrator.example_run
```

或从 `example` 目录执行：

```bash
cd example
python run_langgraph_demo.py
# ...
```
