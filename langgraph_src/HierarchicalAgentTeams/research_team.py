import os
from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from create_tools_for_research_team import tavily_tool, scrape_webpages
import sys
from pathlib import Path
from langgraph_src.HierarchicalAgentTeams.helper_utilities import State, make_supervisor_node


root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# llm = ChatOpenAI(model="deepseek-chat", temperature=0)
llm = init_chat_model("deepseek-chat")

search_agent = create_react_agent(llm, tools=[tavily_tool])


def search_node(state: State) -> Command[Literal["supervisor"]]:
    result = search_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="search")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )


web_scraper_agent = create_react_agent(llm, tools=[scrape_webpages])


def web_scraper_node(state: State) -> Command[Literal["supervisor"]]:
    result = web_scraper_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="web_scraper")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )

research_supervisor_node = make_supervisor_node(llm, ["search", "web_scraper"])

print(research_supervisor_node)




research_builder = StateGraph(State)
research_builder.add_node("supervisor", research_supervisor_node)
research_builder.add_node("search", search_node)
research_builder.add_node("web_scraper", web_scraper_node)

research_builder.add_edge(START, "supervisor")

research_graph = research_builder.compile()


if __name__ == "__main__":
    for chunk in research_graph.stream(
        {"messages": [("user", "when is Taylor Swift's next tour?？请用中文回答")]},
        {"recursion_limit": 100},
    ):
        print(chunk)
        print("---")

# from IPython.display import Image, display
#
# try:
#     # display(Image(graph.get_graph().draw_mermaid_png()))
#     # 获取 PNG 数据
#     png_data = research_graph.get_graph().draw_mermaid_png()
#     filename = "research_team.png"
#     # 保存到本地
#     with open(filename, "wb") as f:
#         f.write(png_data)
#
#     # 显示图像（确保路径正确）
#     display(Image(filename=filename))
#
# except Exception:
#     # This requires some extra dependencies and is optional
#     pass



# {'supervisor': {'next': 'search'}}
# ---
# {'search': {'messages': [HumanMessage(content='1. 今天是农历2025年闰六月廿一（公历2025年8月14日）。\n2. 2023年的中秋节是农历八月十五，公历2023年9月29日。', additional_kwargs={}, response_metadata={}, name='search', id='d941ac51-39cd-47ce-a501-56b8a6baf9c6')]}}
# ---
# {'supervisor': {'next': '__end__'}}
# ---


#
# test2
#
# options: ['FINISH', 'search', 'web_scraper']
# <function make_supervisor_node.<locals>.supervisor_node at 0x10b20fd80>
# {'supervisor': {'next': 'search'}}
# ---
# {'search': {'messages': [HumanMessage(content='目前没有找到关于泰勒·斯威夫特（Taylor Swift）下一次巡演的具体信息。建议您关注她的官方网站或社交媒体以获取最新动态。', additional_kwargs={}, response_metadata={}, name='search', id='5e12a167-01dd-4cc5-b1d2-24b36d6f6466')]}}
# ---
# {'supervisor': {'next': '__end__'}}
# ---