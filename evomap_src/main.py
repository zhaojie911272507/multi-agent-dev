"""EvoMap 工作流组装与入口

使用 LangGraph StateGraph 编排知识演化分析流程：
knowledge_collector → knowledge_analyzer → graph_builder → trend_predictor
    → (条件分支) → report_generator / END
"""

from __future__ import annotations

import argparse
import asyncio
import json

from langgraph.graph import END, START, StateGraph

from evomap_src.config import CONFIDENCE_THRESHOLD
from evomap_src.models import EvoMapState
from evomap_src.nodes.graph_builder import graph_builder
from evomap_src.nodes.knowledge_analyzer import knowledge_analyzer
from evomap_src.nodes.knowledge_collector import knowledge_collector
from evomap_src.nodes.report_generator import report_generator
from evomap_src.nodes.trend_predictor import trend_predictor
from evomap_src.utils import save_report


# ---------------------------------------------------------------------------
# 条件分支
# ---------------------------------------------------------------------------

def should_generate_report(state: EvoMapState) -> str:
    """置信度 >= 阈值则生成报告，否则直接结束"""
    if state.get("confidence_score", 0.0) >= CONFIDENCE_THRESHOLD:
        return "report_generator"
    return "end"


# ---------------------------------------------------------------------------
# 构建 Graph
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    workflow = StateGraph(EvoMapState)

    workflow.add_node("knowledge_collector", knowledge_collector)
    workflow.add_node("knowledge_analyzer", knowledge_analyzer)
    workflow.add_node("graph_builder", graph_builder)
    workflow.add_node("trend_predictor", trend_predictor)
    workflow.add_node("report_generator", report_generator)

    workflow.add_edge(START, "knowledge_collector")
    workflow.add_edge("knowledge_collector", "knowledge_analyzer")
    workflow.add_edge("knowledge_analyzer", "graph_builder")
    workflow.add_edge("graph_builder", "trend_predictor")

    workflow.add_conditional_edges(
        "trend_predictor",
        should_generate_report,
        {
            "report_generator": "report_generator",
            "end": END,
        },
    )

    workflow.add_edge("report_generator", END)

    return workflow


def compile_graph():
    return build_graph().compile()


# ---------------------------------------------------------------------------
# 运行入口
# ---------------------------------------------------------------------------

async def run_evomap(query: str, *, verbose: bool = False) -> dict:
    """运行 EvoMap 分析流程

    Args:
        query: 研究主题
        verbose: 是否打印中间步骤

    Returns:
        最终 state 字典
    """
    app = compile_graph()
    initial_state: EvoMapState = {
        "query": query,
        "knowledge_fragments": [],
        "entities": [],
        "relations": [],
        "evolution_graph": {},
        "trend_predictions": [],
        "confidence_score": 0.0,
        "report": "",
        "messages": [],
    }

    final_state = None
    async for step in app.astream(initial_state, stream_mode="updates"):
        node_name = next(iter(step))
        if verbose:
            print(f"\n{'='*60}")
            print(f"[节点] {node_name}")
            print(f"{'='*60}")

            node_output = step[node_name]
            if isinstance(node_output, dict):
                for key, value in node_output.items():
                    if key == "messages":
                        continue
                    if isinstance(value, list) and len(value) > 3:
                        print(f"  {key}: [{len(value)} items]")
                    elif isinstance(value, dict) and len(str(value)) > 200:
                        print(f"  {key}: {{...}} ({len(value)} keys)")
                    elif isinstance(value, str) and len(value) > 200:
                        print(f"  {key}: {value[:200]}...")
                    else:
                        print(f"  {key}: {value}")

        final_state = step.get(node_name, {})

    merged_state = initial_state.copy()
    async for step in app.astream(initial_state, stream_mode="values"):
        if isinstance(step, dict):
            merged_state.update(step)

    return merged_state


def run_sync(query: str, *, verbose: bool = False) -> dict:
    """同步方式运行"""
    app = compile_graph()
    initial_state: EvoMapState = {
        "query": query,
        "knowledge_fragments": [],
        "entities": [],
        "relations": [],
        "evolution_graph": {},
        "trend_predictions": [],
        "confidence_score": 0.0,
        "report": "",
        "messages": [],
    }

    final_state = initial_state.copy()
    for step in app.stream(initial_state, stream_mode="values"):
        if isinstance(step, dict):
            final_state.update(step)
            if verbose:
                msgs = step.get("messages", [])
                if msgs:
                    last = msgs[-1] if isinstance(msgs, list) else msgs
                    content = getattr(last, "content", str(last))
                    print(f"  > {content}")

    return final_state


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="EvoMap - 知识演化图谱系统",
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        required=True,
        help="研究主题，例如：'大语言模型的演化历程'",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="打印详细的中间步骤",
    )
    parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="保存报告到 evomap_src/output/",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="同时输出演化图谱 JSON",
    )
    args = parser.parse_args()

    print(f"\n🔍 EvoMap 知识演化分析")
    print(f"   主题: {args.query}")
    print(f"   置信度阈值: {CONFIDENCE_THRESHOLD}")
    print(f"{'─'*50}\n")

    result = run_sync(args.query, verbose=args.verbose)

    report = result.get("report", "")
    confidence = result.get("confidence_score", 0.0)

    if report:
        print(f"\n{'═'*60}")
        print(report)
        print(f"{'═'*60}")
    else:
        print(f"\n⚠️  置信度 ({confidence:.2f}) 低于阈值 ({CONFIDENCE_THRESHOLD})，未生成报告。")
        print("   可降低阈值或更换主题重试。")

    if args.json:
        graph_data = result.get("evolution_graph", {})
        print(f"\n{'─'*50}")
        print("演化图谱 JSON:")
        print(json.dumps(graph_data, ensure_ascii=False, indent=2))

    if args.save and report:
        path = save_report(report)
        print(f"\n📄 报告已保存至: {path}")

    return result


if __name__ == "__main__":
    main()
