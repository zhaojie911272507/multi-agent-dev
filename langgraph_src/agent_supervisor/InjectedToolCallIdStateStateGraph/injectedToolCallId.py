# 通过切换工具实现切换，并将这些工具交给主管代理：当主管调用这些工具时，它将把控制权交给工作代理，并将完整的消息历史记录传递给该代理。
from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState, create_react_agent
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.types import Command

from langgraph_src.AgentSupervisor.createWorkerAgent.mathAgent import math_agent
from langgraph_src.AgentSupervisor.createWorkerAgent.agentSupervisorD import research_agent,pretty_print_messages

def create_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        state: Annotated[MessagesState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            goto=agent_name,
            update={**state, "messages": state["messages"] + [tool_message]},
            graph=Command.PARENT,
        )

    return handoff_tool


# Handoffs
assign_to_research_agent = create_handoff_tool(
    agent_name="research_agent",
    description="Assign task to a researcher agent.",
)

assign_to_math_agent = create_handoff_tool(
    agent_name="math_agent",
    description="Assign task to a math agent.",
)

# 创建主管代理
supervisor_agent = create_react_agent(
    model="deepseek-chat",
    tools=[assign_to_research_agent, assign_to_math_agent],
    prompt=(
        "You are a supervisor managing two agents:\n"
        "- a research agent. Assign research-related tasks to this agent\n"
        "- a math agent. Assign math-related tasks to this agent\n"
        "Assign work to one agent at a time, do not call agents in parallel.\n"
        "Do not do any work yourself."
    ),
    name="supervisor",
)


if __name__ == "__main__":
    # 创建多代理图  Create multi-agent graph
    from langgraph.graph import END

    # Define the multi-agent supervisor graph
    supervisor = (
        StateGraph(MessagesState)
        # NOTE: `destinations` is only needed for visualization and doesn't affect runtime behavior
        .add_node(supervisor_agent, destinations=("research_agent", "math_agent", END))
        .add_node(research_agent)
        .add_node(math_agent)
        .add_edge(START, "supervisor")
        # always return back to the supervisor
        .add_edge("research_agent", "supervisor")
        .add_edge("math_agent", "supervisor")
        .compile()
    )


    from IPython.display import Image, display

    try:
        # display(Image(graph.get_graph().draw_mermaid_png()))
        # 获取 PNG 数据
        png_data = supervisor.get_graph().draw_mermaid_png()
        filename = "supervisor.png"
        # 保存到本地
        with open(filename, "wb") as f:
            f.write(png_data)

        # 显示图像（确保路径正确）
        display(Image(filename=filename))

    except Exception:
        # This requires some extra dependencies and is optional
        pass



    for chunk in supervisor.stream(
        {
            "messages": [
                {
                    "role": "user",
                    # "content": "find US and New York state GDP in 2024. what % of US GDP was New York state?",
                    "content": "查找 2024 年江苏和无锡的GDP。无锡占江苏 GDP 的百分比是多少？",
                }
            ]
        },
    ):
        pretty_print_messages(chunk, last_message=True)

    final_message_history = chunk["supervisor"]["messages"]

    print(final_message_history)







# <IPython.core.display.Image object>
# Update from node supervisor:
#
#
# ================================= Tool Message =================================
# Name: transfer_to_research_agent
#
# Successfully transferred to research_agent
#
#
# Update from node research_agent:
#
#
# ================================== Ai Message ==================================
# Name: research_agent
#
# 1. **US GDP in 2024**: According to the U.S. Bureau of Economic Analysis (BEA), the real GDP increased at an annual rate of 2.4% in the fourth quarter of 2024. However, the exact nominal GDP figure for 2024 is not directly provided in the search results.
#    - Source: [BEA](https://www.bea.gov/news/2025/gross-domestic-product-4th-quarter-and-year-2024-third-estimate-gdp-industry-and)
#
# 2. **New York State GDP in 2024**: New York's gross state product (GSP) in 2024 was approximately $1.8 trillion.
#    - Source: [IBISWorld](https://www.ibisworld.com/united-states/economic-profiles/new-york/)
#
# 3. **Percentage of US GDP from New York State**: To calculate this, the exact nominal US GDP for 2024 is required. Based on the available data, New York's GDP was $1.8 trillion. If the US GDP is assumed to be around $27.7 trillion (based on 2023 data from Trading Economics), New York's share would be approximately 6.5%. However, this is an estimate and not exact for 2024.
#    - Sources: [Trading Economics](https://tradingeconomics.com/united-states/gdp), [IBISWorld](https://www.ibisworld.com/united-states/economic-profiles/new-york/)
#
#
# Update from node supervisor:
#
#
# ================================= Tool Message =================================
# Name: transfer_to_math_agent
#
# Successfully transferred to math_agent
#
#
# Update from node math_agent:
#
#
# ================================== Ai Message ==================================
# Name: math_agent
#
# New York state contributed approximately 6.5% of the US GDP in 2024.
#
#
# Update from node supervisor:
#
#
# ================================== Ai Message ==================================
# Name: supervisor
#
#
# [HumanMessage(content='find US and New York state GDP in 2024. what % of US GDP was New York state?', additional_kwargs={}, response_metadata={}, id='dfb94271-75fb-4feb-baee-d49fd4663571'), AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_0_d8471389-4815-4695-80a4-656cf010b3fe', 'function': {'arguments': '{}', 'name': 'transfer_to_research_agent'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 18, 'prompt_tokens': 213, 'total_tokens': 231, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 64}, 'prompt_cache_hit_tokens': 64, 'prompt_cache_miss_tokens': 149}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': '9b39ca39-cea6-48c6-b046-b314a160cbea', 'service_tier': None, 'finish_reason': 'tool_calls', 'logprobs': None}, name='supervisor', id='run--0e987665-76b3-4d07-b641-e85fc3bb27f2-0', tool_calls=[{'name': 'transfer_to_research_agent', 'args': {}, 'id': 'call_0_d8471389-4815-4695-80a4-656cf010b3fe', 'type': 'tool_call'}], usage_metadata={'input_tokens': 213, 'output_tokens': 18, 'total_tokens': 231, 'input_token_details': {'cache_read': 64}, 'output_token_details': {}}), ToolMessage(content='Successfully transferred to research_agent', name='transfer_to_research_agent', id='a81d3618-38d2-4ec9-9913-788918e3be4d', tool_call_id='call_0_d8471389-4815-4695-80a4-656cf010b3fe'), AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_0_7833b6b3-4236-4045-af7a-aeb7a5d041d9', 'function': {'arguments': '{"query": "US GDP 2024"}', 'name': 'tavily_search'}, 'type': 'function', 'index': 0}, {'id': 'call_1_e6496ffa-5353-45a4-8ccf-124e9676ce21', 'function': {'arguments': '{"query": "New York state GDP 2024"}', 'name': 'tavily_search'}, 'type': 'function', 'index': 1}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 51, 'prompt_tokens': 2044, 'total_tokens': 2095, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 1984}, 'prompt_cache_hit_tokens': 1984, 'prompt_cache_miss_tokens': 60}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': 'dcd56a93-ebba-4f8b-800b-1ad28cc8f262', 'service_tier': None, 'finish_reason': 'tool_calls', 'logprobs': None}, name='research_agent', id='run--750bf4b8-a52d-461a-8450-3c932ac0a6bb-0', tool_calls=[{'name': 'tavily_search', 'args': {'query': 'US GDP 2024'}, 'id': 'call_0_7833b6b3-4236-4045-af7a-aeb7a5d041d9', 'type': 'tool_call'}, {'name': 'tavily_search', 'args': {'query': 'New York state GDP 2024'}, 'id': 'call_1_e6496ffa-5353-45a4-8ccf-124e9676ce21', 'type': 'tool_call'}], usage_metadata={'input_tokens': 2044, 'output_tokens': 51, 'total_tokens': 2095, 'input_token_details': {'cache_read': 1984}, 'output_token_details': {}}), ToolMessage(content='{"query": "US GDP 2024", "follow_up_questions": null, "answer": null, "images": [], "results": [{"url": "https://www.bea.gov/news/2025/gross-domestic-product-4th-quarter-and-year-2024-third-estimate-gdp-industry-and", "title": "Gross Domestic Product, 4th Quarter and Year 2024 (Third Estimate ...", "content": "Gross Domestic Product, 4th Quarter and Year 2024 (Third Estimate), GDP by Industry, and Corporate Profits | U.S. Bureau of Economic Analysis (BEA) **Real gross domestic product (GDP)** increased at an annual rate of 2.4 percent in the fourth quarter of 2024 (October, November, and December), according to the third estimate released by the U.S. Bureau of Economic Analysis. The **price index for gross domestic purchases** increased 2.2 percent in the fourth quarter, revised down 0.1 percentage point from the previous estimate. Real GDP increased at an annual rate of 2.4 percent (0.6 percent at a quarterly rate 1), an upward revision of 0.1 percentage point from the previous estimate, primarily reflecting a downward revision to imports that was partly offset by a downward revision to consumer spending.", "score": 0.9067276, "raw_content": null}, {"url": "https://tradingeconomics.com/united-states/gdp", "title": "United States GDP - Trading Economics", "content": "The Gross Domestic Product (GDP) in the United States was worth 27720.71 billion US dollars in 2023, according to official data from the World Bank. This page provides - United States GDP - actual values, historical data, forecast, chart, statistics, economic calendar and news. | GDP Growth Rate | -0.20 | 2.40 | percent | Mar 2025 | GDP GDP GDP Annual Growth Rate GDP Growth Rate Core Inflation Rate MoM Core PCE Price Index MoM Core PCE Price Index YoY Export Prices MoM GDP Price Index Inflation Rate MoM PCE Price Index MoM House Price Index MoM House Price Index YoY Economic Calendar Historical Data News Stream Earnings Releases Credit Ratings Forecasts Markets Currencies Stocks Commodities Bonds Crypto Get Started", "score": 0.4292146, "raw_content": null}, {"url": "https://en.wikipedia.org/wiki/Economy_of_the_United_States", "title": "Economy of the United States - Wikipedia", "content": "Economy of the United States - Wikipedia | Image 489Companies of the United States | | Government institutions | * Department of the Treasury * Department of Commerce * Department of Labor * Office of the United States Trade Representative * Small Business Administration * Internal Revenue Service * National Labor Relations Board * United States Trade and Development Agency * Customs and Border Protection * Office of the Comptroller of the Currency * Consumer Financial Protection Bureau * Securities and Exchange Commission * Federal Deposit Insurance Corporation * National Credit Union Administration * United States International Trade Commission * Statistics | | International development | * U.S. International Development Finance Corporation * Blue Dot Network * Partnership for Global Infrastructure and Investment * Export–Import Bank of the United States |", "score": 0.14274524, "raw_content": null}], "response_time": 0.94}', name='tavily_search', id='4fe30887-ef15-4662-8607-5ba59d233dfb', tool_call_id='call_0_7833b6b3-4236-4045-af7a-aeb7a5d041d9'), ToolMessage(content='{"query": "New York state GDP 2024", "follow_up_questions": null, "answer": null, "images": [], "results": [{"url": "https://www.ibisworld.com/united-states/economic-profiles/new-york/", "title": "New York Economic Trends, Stats & Rankings | IBISWorld", "content": "New York\'s gross state product (GSP) in 2024 reached $1.8tn, with growth of 1.3% over the 5 years to 2024. Businesses in New York employed a total of 11,671,845 people in 2024, with average annual employment growth over the past five years of 0.0%. The top three sectors by total employment are Finance and Insurance, Real Estate and Rental and Leasing, Information, while the unemployment rate across the state in 2024 was 4.2%. State GDP, or Gross State Product, is a measurement of a state\'s output, or the sum of value added from all industries in the state. It is a common indicator used to track the health of a state\'s economy.", "score": 0.9512194, "raw_content": null}, {"url": "https://usafacts.org/answers/what-is-the-gross-domestic-product-gdp/state/new-york/", "title": "What is the gross domestic product (GDP) in New York? - USAFacts", "content": "In 2024, New York’s real (that is, inflation-adjusted) GDP per person was 1st out of all 50 states. The Bureau of Economic Analysis (BEA) provides detailed GDP tables that break down the U.S. gross domestic product by geography, industry, and other variables. The Bureau of Economic Analysis (BEA) provides detailed GDP tables that break down the U.S. gross domestic product by geography, industry, and other variables. The Bureau of Economic Analysis (BEA) provides detailed GDP tables that break down the U.S. gross domestic product by geography, industry, and other variables. This dot plot displays the real gross domestic product (GDP) by industry in New York for the years 2013 and 2023, using chained 2017 dollars.", "score": 0.80625874, "raw_content": null}, {"url": "https://en.wikipedia.org/wiki/Economy_of_New_York_(state)", "title": "Economy of New York (state) - Wikipedia", "content": "Economy of New York (state) - Wikipedia Economy of New York (state) If New York State were an independent nation, it would rank as the 8th largest economy in the world by nominal GDP. Wind is the predominant generating technology.[26] In 2018, the New York State Energy Research and Development Authority awarded long-term contracts to 22 utility-scale solar farms, totaling a combined capacity of 646 MW.[27]In 2012, LIPA adopted a power purchase agreement (limited to 50 MW), which will pay $0.22/kWh for solar generation for installations ranging from 50\xa0kW to 20 MW. State of New York Retrieved from \\"https://en.wikipedia.org/w/index.php?title=Economy_of_New_York_(state)&oldid=1284867348\\" Economy of New York (state) Economy of New York (state)", "score": 0.26916826, "raw_content": null}], "response_time": 0.96}', name='tavily_search', id='1e00e11d-32e2-41d5-883e-a63e3916e822', tool_call_id='call_1_e6496ffa-5353-45a4-8ccf-124e9676ce21'), AIMessage(content="1. **US GDP in 2024**: According to the U.S. Bureau of Economic Analysis (BEA), the real GDP increased at an annual rate of 2.4% in the fourth quarter of 2024. However, the exact nominal GDP figure for 2024 is not directly provided in the search results.  \n   - Source: [BEA](https://www.bea.gov/news/2025/gross-domestic-product-4th-quarter-and-year-2024-third-estimate-gdp-industry-and)\n\n2. **New York State GDP in 2024**: New York's gross state product (GSP) in 2024 was approximately $1.8 trillion.  \n   - Source: [IBISWorld](https://www.ibisworld.com/united-states/economic-profiles/new-york/)\n\n3. **Percentage of US GDP from New York State**: To calculate this, the exact nominal US GDP for 2024 is required. Based on the available data, New York's GDP was $1.8 trillion. If the US GDP is assumed to be around $27.7 trillion (based on 2023 data from Trading Economics), New York's share would be approximately 6.5%. However, this is an estimate and not exact for 2024.  \n   - Sources: [Trading Economics](https://tradingeconomics.com/united-states/gdp), [IBISWorld](https://www.ibisworld.com/united-states/economic-profiles/new-york/)", additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 315, 'prompt_tokens': 3542, 'total_tokens': 3857, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 2368}, 'prompt_cache_hit_tokens': 2368, 'prompt_cache_miss_tokens': 1174}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': '79e34528-e556-4e7a-a7eb-83b4ed595e48', 'service_tier': None, 'finish_reason': 'stop', 'logprobs': None}, name='research_agent', id='run--8dd39674-10f5-4397-8210-eb04cdefe850-0', usage_metadata={'input_tokens': 3542, 'output_tokens': 315, 'total_tokens': 3857, 'input_token_details': {'cache_read': 2368}, 'output_token_details': {}}), AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_0_71d03eeb-7146-4644-ba61-52164755f49c', 'function': {'arguments': '{"task":"Calculate the percentage of US GDP that New York state contributed in 2024, given that New York\'s GDP was $1.8 trillion and the US GDP was $27.7 trillion."}', 'name': 'transfer_to_math_agent'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 60, 'prompt_tokens': 2058, 'total_tokens': 2118, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 192}, 'prompt_cache_hit_tokens': 192, 'prompt_cache_miss_tokens': 1866}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': 'bd2a662f-c3ce-4b55-aa33-e0c9e104dc06', 'service_tier': None, 'finish_reason': 'tool_calls', 'logprobs': None}, name='supervisor', id='run--2245899c-672e-462a-bd7a-0acf6542de32-0', tool_calls=[{'name': 'transfer_to_math_agent', 'args': {'task': "Calculate the percentage of US GDP that New York state contributed in 2024, given that New York's GDP was $1.8 trillion and the US GDP was $27.7 trillion."}, 'id': 'call_0_71d03eeb-7146-4644-ba61-52164755f49c', 'type': 'tool_call'}], usage_metadata={'input_tokens': 2058, 'output_tokens': 60, 'total_tokens': 2118, 'input_token_details': {'cache_read': 192}, 'output_token_details': {}}), ToolMessage(content='Successfully transferred to math_agent', name='transfer_to_math_agent', id='25b31dc3-121e-42ee-9cf6-3c037d3bb7d9', tool_call_id='call_0_71d03eeb-7146-4644-ba61-52164755f49c'), AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_0_783e1625-e01c-42d4-9d17-79f9c500d1f0', 'function': {'arguments': '{"a":1.8,"b":27.7}', 'name': 'divide'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 25, 'prompt_tokens': 2280, 'total_tokens': 2305, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 704}, 'prompt_cache_hit_tokens': 704, 'prompt_cache_miss_tokens': 1576}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': 'ff6d5566-4c97-483e-91f3-406fd2701d9e', 'service_tier': None, 'finish_reason': 'tool_calls', 'logprobs': None}, name='math_agent', id='run--f916b6a6-842b-4c69-a2b1-859b14a83756-0', tool_calls=[{'name': 'divide', 'args': {'a': 1.8, 'b': 27.7}, 'id': 'call_0_783e1625-e01c-42d4-9d17-79f9c500d1f0', 'type': 'tool_call'}], usage_metadata={'input_tokens': 2280, 'output_tokens': 25, 'total_tokens': 2305, 'input_token_details': {'cache_read': 704}, 'output_token_details': {}}), ToolMessage(content='0.06498194945848376', name='divide', id='f3d19a22-1b05-42bc-b14d-ef3293d8d897', tool_call_id='call_0_783e1625-e01c-42d4-9d17-79f9c500d1f0'), AIMessage(content='New York state contributed approximately 6.5% of the US GDP in 2024.', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 19, 'prompt_tokens': 2321, 'total_tokens': 2340, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 1600}, 'prompt_cache_hit_tokens': 1600, 'prompt_cache_miss_tokens': 721}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': '078e6316-121c-4ac0-b0c4-ac708775458d', 'service_tier': None, 'finish_reason': 'stop', 'logprobs': None}, name='math_agent', id='run--6e860f04-0445-4a92-8c90-2649277987ed-0', usage_metadata={'input_tokens': 2321, 'output_tokens': 19, 'total_tokens': 2340, 'input_token_details': {'cache_read': 1600}, 'output_token_details': {}}), AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 0, 'prompt_tokens': 2192, 'total_tokens': 2192, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 2048}, 'prompt_cache_hit_tokens': 2048, 'prompt_cache_miss_tokens': 144}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': '9db74eac-641e-4322-8b8b-f5a54e6bdf1c', 'service_tier': None, 'finish_reason': 'stop', 'logprobs': None}, name='supervisor', id='run--154f5fcc-cb8f-4c76-b5ca-e39834df4808-0', usage_metadata={'input_tokens': 2192, 'output_tokens': 0, 'total_tokens': 2192, 'input_token_details': {'cache_read': 2048}, 'output_token_details': {}})]


