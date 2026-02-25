"""知识分析节点

从采集到的知识片段中提取结构化的知识实体和实体间关系，
使用 LLM structured output 保证输出格式。
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from evomap_src.models import AnalysisResult, EvoMapState
from evomap_src.utils import get_llm

SYSTEM_PROMPT = """\
你是知识分析专家。根据提供的知识片段，提取出核心的知识实体和它们之间的关系。

### 实体提取规则
- 为每个实体分配一个简短唯一 id（英文小写 + 数字，如 "transformer_1"）
- category 从以下选择：technology / theory / tool / methodology
- status 从以下选择：active / deprecated / emerging
- first_appeared 填写年份（如 "2017"），不确定则填 "unknown"

### 关系提取规则
- source_id 和 target_id 必须引用已提取实体的 id
- relation_type 从以下选择：inherits / derives / replaces / merges / influences
- strength 为 0-1 的浮点数
- 关系方向：source → target 表示 source 演化/影响了 target

请尽量完整地提取，一个主题通常有 5-15 个核心实体和 5-20 条关系。\
"""


def knowledge_analyzer(state: EvoMapState) -> dict:
    """从知识片段中提取实体和关系"""
    query = state["query"]
    fragments = state.get("knowledge_fragments", [])

    fragment_text = "\n".join(
        f"- [{f.source}] (相关度: {f.relevance:.1f}) {f.content}"
        for f in fragments
    )

    llm = get_llm()
    llm_with_structure = llm.with_structured_output(AnalysisResult)

    result: AnalysisResult = llm_with_structure.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=f"研究主题：{query}\n\n知识片段：\n{fragment_text}"
        ),
    ])

    return {
        "entities": result.entities,
        "relations": result.relations,
        "messages": [
            HumanMessage(
                content=f"知识分析完成：提取 {len(result.entities)} 个实体，{len(result.relations)} 条关系"
            )
        ],
    }
