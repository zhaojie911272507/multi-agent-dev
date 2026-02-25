"""报告生成节点

整合所有分析结果，通过 LLM 生成结构化的 Markdown 报告。
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from evomap_src.models import EvoMapState
from evomap_src.utils import get_llm

SYSTEM_PROMPT = """\
你是知识分析报告撰写专家。请根据提供的分析数据，生成一份结构清晰的中文 Markdown 报告。

### 报告结构要求

1. **标题**：# 知识演化报告：{主题}
2. **概览**：实体数量、关系数量、整体置信度
3. **知识实体一览**：表格展示主要实体（名称、分类、状态、首次出现时间）
4. **演化图谱**：用文字描述核心演化路径（如 A → B → C），解释关键演化节点
5. **关系网络**：描述重要的实体关系（继承、派生、替代、融合、影响）
6. **趋势预测**：表格展示预测结果（实体、趋势、置信度、说明）
7. **总结与展望**：综合分析结论

### 写作要求
- 使用中文
- 专业但易读
- 善用表格、列表等 Markdown 格式
- 演化路径用 → 箭头连接
- 不要编造数据，基于提供的信息撰写\
"""


def _build_data_section(state: EvoMapState) -> str:
    """将 state 中的分析数据序列化为 LLM 可读的文本"""
    parts: list[str] = []

    parts.append(f"## 研究主题\n{state['query']}")

    entities = state.get("entities", [])
    if entities:
        lines = ["## 知识实体"]
        for e in entities:
            lines.append(
                f"- **{e.name}** (id={e.id}, 分类={e.category}, "
                f"状态={e.status}, 首现={e.first_appeared}): {e.description}"
            )
        parts.append("\n".join(lines))

    relations = state.get("relations", [])
    if relations:
        entity_name = {e.id: e.name for e in entities}
        lines = ["## 实体关系"]
        for r in relations:
            src = entity_name.get(r.source_id, r.source_id)
            tgt = entity_name.get(r.target_id, r.target_id)
            lines.append(
                f"- {src} --[{r.relation_type}, 强度={r.strength:.1f}]--> {tgt}: {r.description}"
            )
        parts.append("\n".join(lines))

    graph = state.get("evolution_graph", {})
    chains = graph.get("evolution_chains", [])
    if chains:
        lines = ["## 演化链"]
        for i, chain in enumerate(chains, 1):
            lines.append(f"{i}. {' → '.join(chain)}")
        parts.append("\n".join(lines))

    predictions = state.get("trend_predictions", [])
    if predictions:
        lines = ["## 趋势预测"]
        for p in predictions:
            name = p.entity_name or p.entity_id
            lines.append(
                f"- **{name}**: {p.trend} (置信度={p.confidence:.2f}) - {p.reasoning}"
            )
        parts.append("\n".join(lines))

    parts.append(f"\n## 整体置信度\n{state.get('confidence_score', 0.0):.2f}")

    return "\n\n".join(parts)


def report_generator(state: EvoMapState) -> dict:
    """生成最终 Markdown 报告"""
    data_section = _build_data_section(state)
    llm = get_llm(temperature=0.5)

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"请基于以下分析数据生成报告：\n\n{data_section}"),
    ])

    report = response.content

    return {
        "report": report,
        "messages": [HumanMessage(content="报告生成完成")],
    }
