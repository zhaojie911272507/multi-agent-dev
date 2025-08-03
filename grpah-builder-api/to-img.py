from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, add_messages,START, END

from langgraphsrc.customWokflow.init_chat_model import llm


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]



# Build workflow
parallel_builder = StateGraph(State)


def call_llm_1(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

def call_llm_2(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

def call_llm_3(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

def aggregator(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Add nodes
parallel_builder.add_node("call_llm_1", call_llm_1)
parallel_builder.add_node("call_llm_2", call_llm_2)
parallel_builder.add_node("call_llm_3", call_llm_3)
parallel_builder.add_node("aggregator", aggregator)

# Add edges to connect nodes
parallel_builder.add_edge(START, "call_llm_1")
parallel_builder.add_edge(START, "call_llm_2")
parallel_builder.add_edge(START, "call_llm_3")
parallel_builder.add_edge("call_llm_1", "aggregator")
parallel_builder.add_edge("call_llm_2", "aggregator")
parallel_builder.add_edge("call_llm_3", "aggregator")
parallel_builder.add_edge("aggregator", END)
parallel_workflow = parallel_builder.compile()


from IPython.display import Image, display

try:
    # display(Image(graph.get_graph().draw_mermaid_png()))
    # 获取 PNG 数据
    png_data = parallel_workflow.get_graph().draw_mermaid_png()

    # 保存到本地
    with open("graph.png", "wb") as f:
        f.write(png_data)

    # 显示图像（确保路径正确）
    display(Image(filename="graph.png"))

except Exception:
    # This requires some extra dependencies and is optional
    pass
