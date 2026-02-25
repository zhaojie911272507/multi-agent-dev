# AI 工程化实战

**设计模式赋能 AI 场景 × LangGraph 工作流 × Langfuse 可观测性 × CrewAI 多智能体协作**

本仓库沉淀 AI 工程实践经验，涵盖经典设计模式在 AI 系统的创新应用与现代智能体框架的深度整合，助您从概念验证(POC)快速过渡到生产环境部署。

## 快速开始

### 环境要求

- Python 3.10+
- OpenAI API Key 或 DeepSeek API Key（推荐，用于国内访问）

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd langgraphtest0725

# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 环境变量

在项目根目录创建 `.env` 文件，配置所需 API Key：

```env
# 至少配置其一
OPENAI_API_KEY=sk-xxx
DEEPSEEK_API_KEY=sk-xxx

# Langfuse 可观测性（可选）
LANGFUSE_PUBLIC_KEY=pk-xxx
LANGFUSE_SECRET_KEY=sk-xxx
```

### 运行示例

```bash
# LangGraph 基础示例
python langgraph_src/demo1.py

# MCP Agent 示例（需先启动 MCP 服务器）
python mcp_src/example/agent_client.py
```

## 核心价值亮点

### 架构基石：设计模式重塑 AI 开发

- **单例模式** - 全局共享资源管理（向量数据库/LLM 客户端）
- **工厂模式** - 动态创建 AI 模型/处理器实例
- **门面模式** - 简化复杂 AI 工具链调用接口
- **策略模式** - 运行时动态切换推理逻辑
- **观察者模式** - 实时监控模型输出流

### MCP（Model Context Protocol）集成

- **多服务接入** - 支持 stdio、streamable_http 等传输方式
- **自定义工具服务器** - 数学计算、天气查询等示例
- **LangGraph 集成** - MCP 工具与 `create_react_agent` / `StateGraph` 无缝结合
- **统一接口** - 标准化模型调用，支持批量与异步

### 多智能体协作框架：CrewAI

- **角色分工** - 创建专业化智能体团队
- **任务编排** - 建立智能体间的依赖关系
- **上下文共享** - 实现跨智能体信息传递
- **自主协作** - 智能体自动协商与决策

### 状态驱动工作流：LangGraph

- **可视化编排** - 构建复杂任务状态机
- **条件路由** - 基于上下文动态切换路径
- **错误处理** - 内置失败重试与回退机制
- **并行执行** - 提高任务处理吞吐量

### 全链路可观测性：Langfuse

- **提示工程** - 跟踪提示词迭代优化路径
- **质量监控** - 分析模型输出稳定性
- **成本追踪** - 监控不同模型调用开销
- **版本对比** - AB 测试不同模型/提示效果

## 项目结构

| 模块 | 说明 |
|------|------|
| `langgraph_src/` | LangGraph 核心示例（图 API、预构建 Agent、SQL Agent、监督者模式等） |
| `crewai_src/` | CrewAI 多智能体示例 |
| `mcp_src/` | MCP 协议示例与自定义服务器 |
| `langfuse_src/` | Langfuse 可观测性集成 |
| `evomap_src/` | EvoMap 知识演化图谱系统 |
| `persistence/` | 持久化与内存存储 |
| `knowledge/` | 设计模式、异步等知识库 |
| `docs/` | 项目文档 |

详见 [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)。

## 文档索引

- [项目结构说明](docs/PROJECT_STRUCTURE.md)
- [依赖说明](docs/dependencies.md)
- [命名规范](docs/NAMING_CONVENTIONS.md)
- [升级迁移指南](docs/UPGRADE_MIGRATION.md)

## 持续演进

将持续更新前沿 AI 工程实践，涵盖：

- 生产级智能体部署优化
- 多模态系统架构设计
- LLM 微调与蒸馏策略
- 高并发场景性能优化
- 联邦学习与隐私保护

### 待探索框架（TODOLIST）

- Agno
- CAMEL (camel-ai)
- AG2 (formerly AutoGen)
- MetaGPT (GitHub: FoundationAgents/MetaGPT)

---

**欢迎贡献实践经验**！通过 Issues 提交建议或通过 Pull Request 分享实现。
