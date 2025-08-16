from typing import Literal

from langchain_core.tools import tool

from langgraph_src.custom_wokflow.init_chat_model import llm


# Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide a and b.

    Args:
        a: first int
        b: second int
    """
    return a / b


# Augment the LLM with tools
tools = [add, multiply, divide]
tools_by_name = {tool.name: tool for tool in tools}
llm_with_tools = llm.bind_tools(tools)


from langgraph.graph import MessagesState, START, END, StateGraph
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage


# Nodes
def llm_call(state: MessagesState):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            llm_with_tools.invoke(
                [
                    SystemMessage(
                        content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
                    )
                ]
                + state["messages"]
            )
        ]
    }


def tool_node(state: dict):
    """Performs the tool call"""

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


# Conditional edge function to route to the tool node or end based upon whether the LLM made a tool call
def should_continue(state: MessagesState) -> Literal["environment", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]
    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "Action"
    # Otherwise, we stop (reply to the user)
    return END


# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("environment", tool_node)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        # Name returned by should_continue : Name of next node to visit
        "Action": "environment",
        END: END,
    },
)
agent_builder.add_edge("environment", "llm_call")

# Compile the agent
agent = agent_builder.compile()

# # Show the agent
# display(Image(agent.get_graph(xray=True).draw_mermaid_png()))


from IPython.display import Image, display

try:
    # display(Image(graph.get_graph().draw_mermaid_png()))
    # 获取 PNG 数据
    png_data = agent.get_graph().draw_mermaid_png()

    # 保存到本地
    with open("agent-to-graph.png", "wb") as f:
        f.write(png_data)

    # 显示图像（确保路径正确）
    display(Image(filename="agent-to-graph.png"))

except Exception:
    # This requires some extra dependencies and is optional
    pass


# Invoke
messages = [HumanMessage(content="Add 3 and 4.")]
messages = agent.invoke({"messages": messages})
for m in messages["messages"]:
    m.pretty_print()


# <IPython.core.display.Image object>
# ================================ Human Message =================================
#
# Add 3 and 4.
# ================================== Ai Message ==================================
# Tool Calls:
#   add (call_0_b932795b-9de0-4f0f-b8ca-3a269ce1f155)
#  Call ID: call_0_b932795b-9de0-4f0f-b8ca-3a269ce1f155
#   Args:
#     a: 3
#     b: 4
# ================================= Tool Message =================================
#
# 7
# ================================== Ai Message ==================================
#
# The sum of 3 and 4 is 7.


