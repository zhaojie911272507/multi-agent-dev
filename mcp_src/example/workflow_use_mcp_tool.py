import asyncio
from pprint import pprint

from langchain_mcp_adapters.client import MultiServerMCPClient

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv()
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")
llm = init_chat_model("deepseek-chat")


async def main():
    # Set up MCP client
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                # Make sure to update to the full absolute path to your math_server.py file
                "args": ["/Users/zhaojie/project/langgraphtest0725/mcp_src/example/custom_mcp_servers/math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                # make sure you start your weather server on port 8000
                "url": "http://localhost:8000/mcp/",
                "transport": "streamable_http",
            }
        }
    )
    tools = await client.get_tools()

    # Bind tools to model
    model_with_tools = llm.bind_tools(tools)

    # Create ToolNode
    tool_node = ToolNode(tools)

    def should_continue(state: MessagesState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    # Define call_model function
    async def call_model(state: MessagesState):
        messages = state["messages"]
        response = await model_with_tools.ainvoke(messages)
        return {"messages": [response]}

    # Build the graph
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        should_continue,
    )
    builder.add_edge("tools", "call_model")

    # Compile the graph
    graph = builder.compile()

    # # Test the graph
    # math_response = await graph.ainvoke(
    #     {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    # )
    # print(math_response)
    weather_response = await graph.ainvoke(
        {"messages": [{"role": "user", "content": "今天上海天气?"}]}
    )
    pprint(weather_response)

if __name__ == "__main__":
    asyncio.run(main())
