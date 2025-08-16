# 到目前为止，各个代理依赖于解读完整的消息历史记录来确定其任务。另一种方法是要求主管明确地制定任务 。我们可以通过在 handoff_tool 函数中添加 task_description 参数来实现。
from typing import Annotated

from langchain_core.tools import tool
from langgraph.constants import START
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import InjectedState, create_react_agent
from langgraph.types import Send, Command

from langgraph_src.AgentSupervisor.createWorkerAgent.mathAgent import math_agent
from langgraph_src.AgentSupervisor.createWorkerAgent.agentSupervisorD import research_agent,pretty_print_messages

def create_task_description_handoff_tool(
    *, agent_name: str, description: str | None = None
):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        # this is populated by the supervisor LLM
        task_description: Annotated[
            str,
            "Description of what the next agent should do, including all of the relevant context.",
        ],
        # these parameters are ignored by the LLM
        state: Annotated[MessagesState, InjectedState],
    ) -> Command:
        task_description_message = {"role": "user", "content": task_description}
        agent_input = {**state, "messages": [task_description_message]}
        return Command(
            goto=[Send(agent_name, agent_input)],
            graph=Command.PARENT,
        )

    return handoff_tool


assign_to_research_agent_with_description = create_task_description_handoff_tool(
    agent_name="research_agent",
    description="Assign task to a researcher agent.",
)

assign_to_math_agent_with_description = create_task_description_handoff_tool(
    agent_name="math_agent",
    description="Assign task to a math agent.",
)

supervisor_agent_with_description = create_react_agent(
    model="openai:gpt-4.1",
    tools=[
        assign_to_research_agent_with_description,
        assign_to_math_agent_with_description,
    ],
    prompt=(
        "You are a supervisor managing two agents:\n"
        "- a research agent. Assign research-related tasks to this assistant\n"
        "- a math agent. Assign math-related tasks to this assistant\n"
        "Assign work to one agent at a time, do not call agents in parallel.\n"
        "Do not do any work yourself."
    ),
    name="supervisor",
)

supervisor_with_description = (
    StateGraph(MessagesState)
    .add_node(
        supervisor_agent_with_description, destinations=("research_agent", "math_agent")
    )
    .add_node(research_agent)
    .add_node(math_agent)
    .add_edge(START, "supervisor")
    .add_edge("research_agent", "supervisor")
    .add_edge("math_agent", "supervisor")
    .compile()
)

if  __name__ == "__main__":
    from IPython.display import Image, display

    try:
        # display(Image(supervisor_with_description.get_graph().draw_mermaid_png()))
        # 获取 PNG 数据
        png_data = supervisor_with_description.get_graph().draw_mermaid_png()
        filename = "supervisor.png"
        # 保存到本地
        with open(filename, "wb") as f:
            f.write(png_data)
    except Exception as e:
        print(e)


