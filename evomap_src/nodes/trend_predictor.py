"""趋势预测节点

基于演化图谱分析各实体的发展趋势，给出预测和置信度评分。
"""

from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from evomap_src.models import EvoMapState, TrendResult
from evomap_src.utils import get_llm, structured_invoke

SYSTEM_PROMPT = """\
你是技术趋势分析专家。根据提供的知识演化图谱，分析每个实体的发展趋势。

### 分析维度
1. 演化链中的位置（越靠后通常越活跃）
2. 入度和出度（被影响多 vs 影响他人多）
3. 状态标记（active / emerging / deprecated）
4. 关系类型分布（被替代的实体趋势下降）

### 输出要求
- 为每个实体（或至少为主要实体）给出趋势判断
- trend: rising / stable / declining
- confidence: 0-1，对该预测的置信度
- reasoning: 简要说明推理依据
- time_horizon: 预测适用的时间范围（如 "1-2 years"）
- overall_confidence: 对整体分析的置信度

请客观分析，不确定时降低置信度。\
"""


def trend_predictor(state: EvoMapState) -> dict:
    """分析趋势并输出预测"""
    evolution_graph = state.get("evolution_graph", {})

    graph_summary = json.dumps(evolution_graph, ensure_ascii=False, indent=2)
    if len(graph_summary) > 8000:
        compact = {
            "query": evolution_graph.get("query", ""),
            "summary": evolution_graph.get("summary", {}),
            "evolution_chains": evolution_graph.get("evolution_chains", []),
            "category_groups": evolution_graph.get("category_groups", {}),
        }
        graph_summary = json.dumps(compact, ensure_ascii=False, indent=2)

    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"演化图谱数据：\n{graph_summary}"),
    ]
    result: TrendResult = structured_invoke(llm, TrendResult, messages)

    return {
        "trend_predictions": result.predictions,
        "confidence_score": result.overall_confidence,
        "messages": [
            HumanMessage(
                content=(
                    f"趋势预测完成：{len(result.predictions)} 条预测，"
                    f"整体置信度 {result.overall_confidence:.2f}"
                )
            )
        ],
    }
