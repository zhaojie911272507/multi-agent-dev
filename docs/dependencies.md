# 项目依赖说明

本文档说明 `requirements.txt` 中各依赖包的分类与用途，便于理解项目所需的运行环境。

## 依赖分类表

| 类别 | 包 | 用途说明 |
|------|-----|----------|
| **LangGraph & LangChain** | langgraph | 多智能体工作流编排 |
| | langchain | LangChain 核心 |
| | langchain-openai | OpenAI 模型集成 |
| | langchain-community | 社区工具与集成（SQL、Ollama、文档加载等） |
| | langchain-core | LangChain 核心抽象 |
| | langchain-experimental | 实验性功能（如 PythonREPL） |
| | langchain-text-splitters | 文本分割 |
| | langchain-tavily | Tavily 搜索工具 |
| | langchain-mcp-adapters | MCP 协议适配 |
| | langgraph-swarm | 多智能体 Swarm 架构 |
| | langgraph-supervisor | 监督者模式多智能体 |
| **CrewAI** | crewai[tools] | CrewAI 多智能体框架及工具 |
| | crewai-tools | CrewAI 工具集（如 SerperDevTool） |
| **LLM & API** | openai | OpenAI API 客户端 |
| **可观测性** | langfuse | LLM 调用追踪与评估 |
| **MCP** | mcp | Model Context Protocol 服务端 |
| **Web 框架** | fastapi | Web API 框架 |
| | streamlit | 快速构建数据/对话应用界面 |
| | uvicorn | ASGI 服务器 |
| **数据 & 向量** | pandas | 数据分析 |
| | numpy | 数值计算 |
| | transformers | Hugging Face  transformers |
| | sentence-transformers | 句子向量模型 |
| | huggingface-hub | 模型与数据集下载 |
| | dashscope | 阿里云 DashScope 嵌入模型（AgenticRAG） |
| **数据库** | sqlalchemy | 数据库 ORM 与 SQL 工具 |
| **工具类** | python-dotenv | 环境变量加载 |
| | pydantic | 数据校验与配置 |
| | httpx | 异步 HTTP 客户端 |
| | requests | HTTP 请求 |
| | duckduckgo-search | DuckDuckGo 搜索 |
| **图片转 PDF** | Pillow | 图片处理 |
| | img2pdf | 图片转 PDF |

## 可选依赖

| 包 | 用途 |
|-----|------|
| langchain-ollama | 使用 Ollama 本地模型（可选） |

## 安装方式

```bash
pip install -r requirements.txt
```

## 说明

- **按需精简**：若仅运行部分模块，可按上表删除未使用的依赖
- **版本约束**：`crewai` 限定 `<1.0.0` 以保持与当前代码兼容
