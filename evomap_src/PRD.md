# EvoMap - 知识演化图谱系统 PRD

## 1. 产品概述

**EvoMap（Evolution Map）** 是一个基于 LangGraph 的知识演化图谱系统，用于对特定领域的知识进行采集、分析、构建演化关系、预测发展趋势并生成结构化报告。

系统以 LangGraph StateGraph 为核心编排引擎，将知识处理流程拆分为多个智能节点，通过有向图实现自动化的知识演化分析。

## 2. 核心价值

| 痛点 | 解决方案 |
|------|----------|
| 知识碎片化，难以看清技术/概念的演化脉络 | 自动构建知识演化图谱，呈现概念之间的继承、派生、替代关系 |
| 手动追踪技术趋势耗时耗力 | LLM 驱动的趋势分析与预测 |
| 分析结果缺乏结构化输出 | 自动生成 Markdown 报告 + JSON 结构化数据 |

## 3. 系统架构

### 3.1 工作流总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EvoMap Workflow                             │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │  knowledge    │───>│  knowledge   │───>│   graph_builder      │  │
│  │  collector    │    │  analyzer    │    │  (演化图谱构建)        │  │
│  │  (知识采集)    │    │  (知识分析)   │    └──────────┬───────────┘  │
│  └──────────────┘    └──────────────┘               │              │
│                                                      ▼              │
│                                          ┌──────────────────────┐  │
│                                          │   trend_predictor    │  │
│                                          │   (趋势预测)          │  │
│                                          └──────────┬───────────┘  │
│                                                      │              │
│                                     ┌────────────────┤              │
│                                     ▼                ▼              │
│                          ┌─────────────┐   ┌──────────────────┐    │
│                          │   END       │   │ report_generator │    │
│                          │(置信度不足)   │   │ (报告生成)        │    │
│                          └─────────────┘   └──────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 节点说明

| 节点 | 职责 | 输入 | 输出 |
|------|------|------|------|
| `knowledge_collector` | 接收用户查询主题，通过搜索工具采集相关知识片段 | 用户主题 query | 知识片段列表 |
| `knowledge_analyzer` | 对采集到的知识进行分类、提取实体与关系 | 知识片段列表 | 结构化知识实体 + 关系 |
| `graph_builder` | 根据实体与关系构建演化图谱（继承、派生、替代、融合） | 实体 + 关系 | 演化图谱 JSON |
| `trend_predictor` | 基于演化图谱分析趋势并给出预测 | 演化图谱 | 趋势预测 + 置信度 |
| `report_generator` | 将所有分析结果整合为 Markdown 报告 | 全部中间结果 | Markdown 报告 |

### 3.3 条件分支

- `trend_predictor` → `report_generator`：置信度 ≥ 阈值（默认 0.6），进入报告生成
- `trend_predictor` → `END`：置信度 < 阈值，直接结束并返回原始分析数据

## 4. 数据模型

### 4.1 State（LangGraph 状态）

```python
class EvoMapState(TypedDict):
    query: str                                      # 用户输入的研究主题
    knowledge_fragments: list[KnowledgeFragment]     # 采集到的知识片段
    entities: list[KnowledgeEntity]                  # 提取的知识实体
    relations: list[EntityRelation]                  # 实体间关系
    evolution_graph: dict                            # 演化图谱 JSON
    trend_predictions: list[TrendPrediction]         # 趋势预测
    confidence_score: float                          # 整体置信度
    report: str                                      # 最终 Markdown 报告
    messages: Annotated[list, add_messages]           # LLM 对话消息
```

### 4.2 核心实体

```python
class KnowledgeFragment(BaseModel):
    """知识片段"""
    content: str          # 原始内容
    source: str           # 来源
    timestamp: str        # 时间标记
    relevance: float      # 相关度 0-1

class KnowledgeEntity(BaseModel):
    """知识实体"""
    id: str               # 唯一标识
    name: str             # 实体名称
    category: str         # 分类（技术/理论/工具/方法论）
    description: str      # 描述
    first_appeared: str   # 首次出现时间
    status: str           # active / deprecated / emerging

class EntityRelation(BaseModel):
    """实体关系"""
    source_id: str        # 源实体 ID
    target_id: str        # 目标实体 ID
    relation_type: str    # inherits / derives / replaces / merges / influences
    strength: float       # 关系强度 0-1
    description: str      # 关系说明

class TrendPrediction(BaseModel):
    """趋势预测"""
    entity_id: str        # 相关实体
    trend: str            # rising / stable / declining
    confidence: float     # 置信度 0-1
    reasoning: str        # 推理依据
    time_horizon: str     # 预测时间范围
```

## 5. 实现步骤

### Step 1: 项目基础结构
- 创建 `__init__.py`
- 创建 `config.py`（模型配置、API Key、阈值参数）
- 创建 `utils.py`（通用工具函数）

### Step 2: 核心数据模型
- 创建 `models.py`，定义 State 和所有 Pydantic 模型

### Step 3: 知识采集节点
- 创建 `nodes/knowledge_collector.py`
- 使用 DuckDuckGo 搜索工具采集知识
- LLM 对搜索结果进行初步筛选

### Step 4: 知识分析节点
- 创建 `nodes/knowledge_analyzer.py`
- LLM 从知识片段中提取实体和关系
- 使用 structured output 确保输出格式

### Step 5: 演化图谱构建
- 创建 `nodes/graph_builder.py`
- 将实体和关系组装为图谱 JSON
- 识别演化路径（时间线排序、关系链追踪）

### Step 6: 趋势预测
- 创建 `nodes/trend_predictor.py`
- LLM 分析图谱中的模式与趋势
- 输出置信度评分

### Step 7: 报告生成
- 创建 `nodes/report_generator.py`
- 整合所有分析结果
- 生成结构化 Markdown 报告

### Step 8: 工作流组装
- 创建 `main.py`，组装 StateGraph
- 定义节点连接和条件分支
- 提供 CLI 入口

## 6. 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 工作流引擎 | LangGraph StateGraph | 与项目现有技术栈一致 |
| LLM | DeepSeek via ChatOpenAI | 复用项目已有配置 |
| 搜索工具 | DuckDuckGoSearchResults | 已在 requirements.txt 中 |
| 数据模型 | Pydantic v2 | 结构化输出 |
| 配置管理 | python-dotenv | 环境变量 |

## 7. 目录结构

```
evomap_src/
├── __init__.py
├── PRD.md              # 本文档
├── config.py           # 配置（模型、阈值）
├── models.py           # 数据模型
├── utils.py            # 工具函数
├── main.py             # 工作流组装 + CLI 入口
└── nodes/
    ├── __init__.py
    ├── knowledge_collector.py
    ├── knowledge_analyzer.py
    ├── graph_builder.py
    ├── trend_predictor.py
    └── report_generator.py
```

## 8. 使用方式

```bash
# 从项目根目录运行
python -m evomap_src.main --query "大语言模型的演化历程"

# 或在 Python 中调用
from evomap_src.main import run_evomap
result = await run_evomap("深度学习框架的演化")
```

## 9. 输出示例

系统会生成如下结构的报告：

```markdown
# 知识演化报告：大语言模型的演化历程

## 概览
- 分析实体数量：12
- 识别关系数量：18
- 整体置信度：0.82

## 演化图谱
### 核心演化路径
RNN → LSTM → Transformer → GPT → GPT-4
                          → BERT → RoBERTa
                          → T5 → PaLM → Gemini

## 趋势预测
| 实体 | 趋势 | 置信度 | 说明 |
|------|------|--------|------|
| Transformer | stable | 0.95 | 仍为主流架构 |
| Mamba/SSM | rising | 0.78 | 新兴替代架构 |

## 详细分析
...
```
