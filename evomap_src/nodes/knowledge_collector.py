"""知识采集节点

通过 DuckDuckGo 搜索工具采集与用户主题相关的知识片段，
再由 LLM 评估相关度并筛选。
"""

from __future__ import annotations

import json

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.messages import HumanMessage, SystemMessage

from evomap_src.config import MAX_SEARCH_RESULTS
from evomap_src.models import EvoMapState, KnowledgeFragment
from evomap_src.utils import get_llm, now_iso

SYSTEM_PROMPT = """\
你是知识采集助手。用户会提供一个研究主题和一批搜索结果。
请从搜索结果中筛选出与主题高度相关的条目，并为每条评估相关度（0-1）。

请严格以 JSON 数组格式输出，每个元素包含:
- content: 知识内容摘要（中文）
- source: 来源信息
- relevance: 相关度（0-1 的浮点数）

只输出 JSON 数组，不要输出其他内容。\
"""


def knowledge_collector(state: EvoMapState) -> dict:
    """采集与主题相关的知识片段"""
    query = state["query"]
    llm = get_llm()

    search_tool = DuckDuckGoSearchResults(
        max_results=MAX_SEARCH_RESULTS,
        output_format="list",
    )

    search_queries = [
        f"{query} 发展历史 演化",
        f"{query} evolution history timeline",
        f"{query} 最新进展 趋势",
    ]

    raw_results: list[str] = []
    for sq in search_queries:
        try:
            results = search_tool.invoke(sq)
            if isinstance(results, list):
                for r in results:
                    snippet = r.get("snippet", "") if isinstance(r, dict) else str(r)
                    link = r.get("link", "web") if isinstance(r, dict) else "web"
                    raw_results.append(f"[{link}] {snippet}")
            else:
                raw_results.append(str(results))
        except Exception:
            continue

    if not raw_results:
        return {
            "knowledge_fragments": [
                KnowledgeFragment(
                    content=f"未能搜索到与「{query}」相关的信息，将基于 LLM 自身知识进行分析。",
                    source="fallback",
                    timestamp=now_iso(),
                    relevance=0.5,
                )
            ],
            "messages": [HumanMessage(content=f"研究主题：{query}（搜索无结果，使用 LLM 内置知识）")],
        }

    search_text = "\n".join(f"{i+1}. {r}" for i, r in enumerate(raw_results))

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"研究主题：{query}\n\n搜索结果：\n{search_text}"),
    ])

    fragments: list[KnowledgeFragment] = []
    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]
        items = json.loads(content)
        for item in items:
            fragments.append(
                KnowledgeFragment(
                    content=item.get("content", ""),
                    source=item.get("source", "web"),
                    timestamp=now_iso(),
                    relevance=float(item.get("relevance", 0.5)),
                )
            )
    except (json.JSONDecodeError, KeyError, TypeError):
        fragments.append(
            KnowledgeFragment(
                content=response.content,
                source="llm_raw",
                timestamp=now_iso(),
                relevance=0.6,
            )
        )

    fragments = [f for f in fragments if f.relevance >= 0.3]
    if not fragments:
        fragments.append(
            KnowledgeFragment(
                content=f"关于「{query}」的综合知识（基于 LLM 分析）",
                source="llm_fallback",
                timestamp=now_iso(),
                relevance=0.5,
            )
        )

    return {
        "knowledge_fragments": fragments,
        "messages": [
            HumanMessage(content=f"研究主题：{query}"),
            HumanMessage(content=f"已采集 {len(fragments)} 条知识片段"),
        ],
    }
