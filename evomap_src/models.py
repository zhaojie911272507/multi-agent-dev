from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langgraph.graph import add_messages
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Pydantic 实体模型
# ---------------------------------------------------------------------------

class KnowledgeFragment(BaseModel):
    """知识片段 - 从外部搜索采集的原始知识条目"""
    content: str = Field(description="知识片段内容")
    source: str = Field(default="web", description="来源标识")
    timestamp: str = Field(default="", description="时间标记")
    relevance: float = Field(default=0.0, ge=0, le=1, description="相关度 0-1")


class KnowledgeEntity(BaseModel):
    """知识实体 - 从知识片段中提取的结构化实体"""
    id: str = Field(description="唯一标识")
    name: str = Field(description="实体名称")
    category: str = Field(
        description="分类：technology / theory / tool / methodology"
    )
    description: str = Field(description="简要描述")
    first_appeared: str = Field(default="unknown", description="首次出现时间/年份")
    status: str = Field(
        default="active",
        description="状态：active / deprecated / emerging",
    )


class EntityRelation(BaseModel):
    """实体关系 - 两个知识实体之间的演化关系"""
    source_id: str = Field(description="源实体 ID")
    target_id: str = Field(description="目标实体 ID")
    relation_type: str = Field(
        description="关系类型：inherits / derives / replaces / merges / influences"
    )
    strength: float = Field(default=0.5, ge=0, le=1, description="关系强度 0-1")
    description: str = Field(default="", description="关系说明")


class TrendPrediction(BaseModel):
    """趋势预测 - 对单个实体的发展趋势判断"""
    entity_id: str = Field(description="对应实体 ID")
    entity_name: str = Field(default="", description="实体名称（冗余，便于展示）")
    trend: str = Field(description="趋势：rising / stable / declining")
    confidence: float = Field(ge=0, le=1, description="置信度 0-1")
    reasoning: str = Field(description="推理依据")
    time_horizon: str = Field(default="1-3 years", description="预测时间范围")


# ---------------------------------------------------------------------------
# LLM Structured Output 用容器
# ---------------------------------------------------------------------------

class AnalysisResult(BaseModel):
    """知识分析节点的结构化输出"""
    entities: list[KnowledgeEntity] = Field(default_factory=list)
    relations: list[EntityRelation] = Field(default_factory=list)


class TrendResult(BaseModel):
    """趋势预测节点的结构化输出"""
    predictions: list[TrendPrediction] = Field(default_factory=list)
    overall_confidence: float = Field(
        default=0.0, ge=0, le=1, description="整体置信度"
    )


# ---------------------------------------------------------------------------
# LangGraph State
# ---------------------------------------------------------------------------

class EvoMapState(TypedDict):
    """EvoMap 工作流状态"""
    query: str
    knowledge_fragments: Annotated[list[KnowledgeFragment], operator.add]
    entities: list[KnowledgeEntity]
    relations: list[EntityRelation]
    evolution_graph: dict
    trend_predictions: list[TrendPrediction]
    confidence_score: float
    report: str
    messages: Annotated[list, add_messages]
