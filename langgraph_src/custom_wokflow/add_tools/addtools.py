
# 3. Define the tool
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
from langchain_tavily import TavilySearch

tool = TavilySearch(max_results=2)
tools = [tool]
tool.invoke("What's a 'node' in LangGraph?")


# 4. Define the graph
from langgraph_src.custom_wokflow.init_chat_model import llm

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

# Modification: tell the LLM which tools it can call
# highlight-next-line
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)


# 5. Create a function to run the tools¶
# 5. 创建函数来运行工具
import json

from langchain_core.messages import ToolMessage


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


tool_node = BasicToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)


# 6. Define the conditional_edges
# With the tool node added, now you can define the conditional_edges.
# 添加工具节点后，现在您可以定义 conditional_edges 。
#
# Edges route the control flow from one node to the next. Conditional edges start from a single node and usually contain "if" statements to route to different nodes depending on the current graph state. These functions receive the current graph state and return a string or list of strings indicating which node(s) to call next.
# 边将控制流从一个节点路由到下一个节点。 条件边从单个节点开始，通常包含“if”语句，根据当前图状态路由到不同的节点。这些函数接收当前图 state ，并返回一个字符串或字符串列表，指示接下来要调用哪个节点。
#
# Next, define a router function called route_tools that checks for tool_calls in the chatbot's output. Provide this function to the graph by calling add_conditional_edges, which tells the graph that whenever the chatbot node completes to check this function to see where to go next.
# 接下来，定义一个名为 route_tools 的路由器函数，用于检查聊天机器人输出中是否存在 tool_calls 。通过调用 add_conditional_edges 将此函数提供给图，这将告诉图，每当 chatbot 机器人节点完成时，都要检查此函数以确定下一步要去哪里。
#
# The condition will route to tools if tool calls are present and END if not. Because the condition can return END, you do not need to explicitly set a finish_point this time.
# 如果存在工具调用，则条件将路由至 tools ；如果不存在，则 END 。由于条件可以返回 END ，因此您这次无需明确设置 finish_point 。

def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


# The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "END" if
# it is fine directly responding. This conditional routing defines the main agent loop.
graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
    # It defaults to the identity function, but if you
    # want to use a node named something else apart from "tools",
    # You can update the value of the dictionary to something else
    # e.g., "tools": "my_tools"
    {"tools": "tools", END: END},
)

# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile()


from IPython.display import Image, display

try:
    # display(Image(graph.get_graph().draw_mermaid_png()))
    # 获取 PNG 数据
    png_data = graph.get_graph().draw_mermaid_png()

    # 保存到本地
    with open("graph.png", "wb") as f:
        f.write(png_data)

    # 显示图像（确保路径正确）
    display(Image(filename="graph.png"))

except Exception:
    # This requires some extra dependencies and is optional
    pass

