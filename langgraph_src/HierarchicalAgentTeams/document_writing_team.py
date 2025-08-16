
from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from langgraph_src.HierarchicalAgentTeams.helper_utilities import State, make_supervisor_node

from langgraph_src.HierarchicalAgentTeams.python_repl import write_document, edit_document, read_document, \
    create_outline, python_repl_tool



llm = init_chat_model("deepseek-chat")
# llm = ChatOpenAI(model="deepseek-chat", openai_api_base="https://api.deepseek.com/v1/", openai_api_key=os.getenv("DEEPSEEK_API_KEY"))
# 使用ChatOpenAI 方法无法正确执行

doc_writer_agent = create_react_agent(
    llm,
    tools=[write_document, edit_document, read_document],
    prompt=(
        "You can read, write and edit documents based on note-taker's outlines. "
        "Don't ask follow-up questions."
    ),
)


def doc_writing_node(state: State) -> Command[Literal["supervisor"]]:
    result = doc_writer_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="doc_writer")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )


note_taking_agent = create_react_agent(
    llm,
    tools=[create_outline, read_document],
    prompt=(
        "You can read documents and create outlines for the document writer. "
        "Don't ask follow-up questions."
    ),
)


def note_taking_node(state: State) -> Command[Literal["supervisor"]]:
    result = note_taking_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="note_taker")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )


chart_generating_agent = create_react_agent(
    llm, tools=[read_document, python_repl_tool]
)


def chart_generating_node(state: State) -> Command[Literal["supervisor"]]:
    result = chart_generating_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=result["messages"][-1].content, name="chart_generator"
                )
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )


doc_writing_supervisor_node = make_supervisor_node(
    llm, ["doc_writer", "note_taker", "chart_generator"]
)


# Create the graph here
paper_writing_builder = StateGraph(State)
paper_writing_builder.add_node("supervisor", doc_writing_supervisor_node)
paper_writing_builder.add_node("doc_writer", doc_writing_node)
paper_writing_builder.add_node("note_taker", note_taking_node)
paper_writing_builder.add_node("chart_generator", chart_generating_node)

paper_writing_builder.add_edge(START, "supervisor")
paper_writing_graph = paper_writing_builder.compile()

if __name__ == "__main__":
    from langfuse.langchain import CallbackHandler

    langfuse_handler = CallbackHandler()
    for s in paper_writing_graph.stream(
        {
            "messages": [
                (
                    "user",
                    "Write an outline for poem about cats and then write the poem to disk.Must be output in Chinese.",
                )
            ]
        },
        {"recursion_limit": 100,"callbacks": [langfuse_handler]},
    ):
        print(s)
        print("---")
