from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.types import Command

from langgraph_src.HierarchicalAgentTeams.document_writing_team import paper_writing_graph
from langgraph_src.HierarchicalAgentTeams.research_team import research_graph
from langgraph_src.HierarchicalAgentTeams.helper_utilities import make_supervisor_node, State

llm = init_chat_model(model="deepseek-chat")

teams_supervisor_node = make_supervisor_node(llm, ["research_team", "writing_team"])

def call_research_team(state: State) -> Command[Literal["supervisor"]]:
    response = research_graph.invoke({"messages": state["messages"][-1]})
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response["messages"][-1].content, name="research_team"
                )
            ]
        },
        goto="supervisor",
    )


def call_paper_writing_team(state: State) -> Command[Literal["supervisor"]]:
    response = paper_writing_graph.invoke({"messages": state["messages"][-1]})
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response["messages"][-1].content, name="writing_team"
                )
            ]
        },
        goto="supervisor",
    )


# Define the graph.
super_builder = StateGraph(State)
super_builder.add_node("supervisor", teams_supervisor_node)
super_builder.add_node("research_team", call_research_team)
super_builder.add_node("writing_team", call_paper_writing_team)

super_builder.add_edge(START, "supervisor")
super_graph = super_builder.compile()

from langfuse.langchain import CallbackHandler
langfuse_handler = CallbackHandler()

for s in super_graph.stream(
    {
        "messages": [
            # ("user", "Research AI agents and write a brief report about them.Make the data part into a chart style。Must be output in Chinese.")
            ("user", "Research 特斯拉2024年的股票和年报 and write a brief report about them.Make the data part into a chart style。Must be output in Chinese.")
        ],
    },
    {"recursion_limit": 25,"callbacks": [langfuse_handler],},
):
    print(s)
    print("---")


# draw_graph_img(super_graph, rename="super_graph2")