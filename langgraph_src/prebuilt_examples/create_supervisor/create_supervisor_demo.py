import os

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from langgraph_supervisor import create_supervisor

from langgraph.prebuilt import create_react_agent

from dotenv import load_dotenv

load_dotenv()
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")
#
# llm = init_chat_model("deepseek-chat")

# Create specialized agents

def add(a: float, b: float) -> float:
    '''Add two numbers.'''
    return a + b

def web_search(query: str) -> str:
    '''Search the web for information.'''
    return 'Here are the headcounts for each of the FAANG companies in 2024...'

math_agent = create_react_agent(
    model="deepseek-chat",
    tools=[add],
    name="math_expert",
)

research_agent = create_react_agent(
    model="deepseek-chat",
    tools=[web_search],
    name="research_expert",
)

# Create supervisor workflow
workflow = create_supervisor(
    [research_agent, math_agent],
    model=ChatOpenAI(model="deepseek-chat",
                     openai_api_base = "https://api.deepseek.com/v1/",
                     openai_api_key = os.getenv("DEEPSEEK_API_KEY")),
)

# Compile and run
app = workflow.compile()
result = app.invoke({
    "messages": [
        {
            "role": "user",
            "content": "what's the combined headcount of the FAANG companies in 2024?"
        }
    ]
})

print(result)









'''
{'messages': [HumanMessage(content="what's the combined headcount of the FAANG companies in 2024?",
                           additional_kwargs={},
                           response_metadata={},
                           id='0d8f78a3-ae91-4b81-ac81-72359d6568cc'),
              AIMessage(content='',
                        additional_kwargs={'tool_calls': [{'id': 'call_0_17fe698b-65e9-4960-830c-60ae9b9fc368', 
                                                           'function': {'arguments': '{}', 
                                                                        'name': 'transfer_to_research_expert'}, 
                                                           'type': 'function', 
                                                           'index': 0}], 
                                           'refusal': None},
                        response_metadata={'token_usage': {'completion_tokens': 19, 
                                                           'prompt_tokens': 162, 
                                                           'total_tokens': 181, 
                                                           'completion_tokens_details': None, 
                                                           'prompt_tokens_details': {'audio_tokens': None, 
                                                                                     'cached_tokens': 0}, 
                                                           'prompt_cache_hit_tokens': 0, 
                                                           'prompt_cache_miss_tokens': 162}, 
                                           'model_name': 'deepseek-chat', 
                                           'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 
                                           'id': '1d765d11-7470-4b05-9c3d-68557103774a', 
                                           'service_tier': None, 
                                           'finish_reason': 'tool_calls', 
                                           'logprobs': None},
                        name='supervisor',
                        id='run--aa74cc21-1bf3-4b17-8bab-152a66c2d9d8-0',
                        tool_calls=[{'name': 'transfer_to_research_expert', 
                                     'args': {}, 
                                     'id': 'call_0_17fe698b-65e9-4960-830c-60ae9b9fc368', 
                                     'type': 'tool_call'}],
                        usage_metadata={'input_tokens': 162, 
                                        'output_tokens': 19, 
                                        'total_tokens': 181, 
                                        'input_token_details': {'cache_read': 0}, 
                                        'output_token_details': {}}),
              ToolMessage(content='Successfully transferred to research_expert',
                          name='transfer_to_research_expert',
                          id='dc055c0a-3dc1-4ab0-a95c-1aa0a3e21d98',
                          tool_call_id='call_0_17fe698b-65e9-4960-830c-60ae9b9fc368'),
              AIMessage(content="It seems I couldn't retrieve the exact headcounts for the FAANG companies (Meta, Apple, Amazon, Netflix, Google) in 2024 directly. Would you like me to try a different approach or provide historical data for reference?",
                        additional_kwargs={'refusal': None},
                        response_metadata={'token_usage': {'completion_tokens': 49, 
                                                           'prompt_tokens': 422, 
                                                           'total_tokens': 471, 
                                                           'completion_tokens_details': None, 
                                                           'prompt_tokens_details': {'audio_tokens': None,
                                                                                     'cached_tokens': 192}, 
                                                           'prompt_cache_hit_tokens': 192, 
                                                           'prompt_cache_miss_tokens': 230}, 
                                           'model_name': 'deepseek-chat', 
                                           'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 
                                           'id': 'bbccda0f-1a07-4e3f-b5e4-7c450774f37e', 
                                           'service_tier': None, 
                                           'finish_reason': 'stop', 
                                           'logprobs': None}, 
                        name='research_expert',
                        id='run--24f44c37-1760-41e6-a0c6-9c6028e4d876-0',
                        usage_metadata={'input_tokens': 422, 
                                        'output_tokens': 49, 
                                        'total_tokens': 471, 
                                        'input_token_details': {'cache_read': 192}, 
                                        'output_token_details': {}}),
              AIMessage(content='Transferring back to supervisor',
                        additional_kwargs={},
                        response_metadata={'__is_handoff_back': True},
                        name='research_expert',
                        id='263e75da-f146-4dc2-99a4-80cde3230506',
                        tool_calls=[{'name': 'transfer_back_to_supervisor', 
                                     'args': {}, 
                                     'id': '8af64ad2-0cd2-4a37-a0fe-6115e6e37504', 
                                     'type': 'tool_call'}]),
              ToolMessage(content='Successfully transferred back to supervisor',
                          name='transfer_back_to_supervisor',
                          id='44806b35-3f4c-44e8-94a0-9e3e32e7f16d',
                          tool_call_id='8af64ad2-0cd2-4a37-a0fe-6115e6e37504'),
              AIMessage(content="It seems the exact headcounts for the FAANG companies (Meta, Apple, Amazon, Netflix, Google) in 2024 aren't readily available. Would you like me to provide historical data or estimate based on trends? Alternatively, I can try a different approach to find the most current information. Let me know how you'd like to proceed!",
                        additional_kwargs={'refusal': None},
                        response_metadata={'token_usage': {'completion_tokens': 71, 
                                                           'prompt_tokens': 257, 
                                                           'total_tokens': 328, 
                                                           'completion_tokens_details': None, 
                                                           'prompt_tokens_details': {'audio_tokens': None, 
                                                                                     'cached_tokens': 128}, 
                                                           'prompt_cache_hit_tokens': 128, 
                                                           'prompt_cache_miss_tokens': 129}, 
                                           'model_name': 'deepseek-chat', 
                                           'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 
                                           'id': '24a2a650-4cca-4900-9851-0d40e94e1124', 
                                           'service_tier': None, 
                                           'finish_reason': 'stop', 
                                           'logprobs': None}, 
                        name='supervisor', 
                        id='run--8e9cb744-2ecb-4645-99ee-ec95d7e1ffe0-0', 
                        usage_metadata={'input_tokens': 257, 
                                        'output_tokens': 71, 
                                        'total_tokens': 328, 
                                        'input_token_details': {'cache_read': 128}, 
                                        'output_token_details': {}
                                        }
                        )
              ]
 }

'''


