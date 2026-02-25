import os

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph
from langgraph_swarm import SwarmState, create_handoff_tool, add_active_agent_router

from dotenv import load_dotenv

load_dotenv()
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")

def add(a: int, b: int) -> int:
    '''Add two numbers'''
    return a + b

alice = create_react_agent(
    "deepseek-chat",
    [add, create_handoff_tool(agent_name="Bob")],
    prompt="You are Alice, an addition expert.",
    name="Alice",
)

bob = create_react_agent(
    "deepseek-chat",
    [create_handoff_tool(agent_name="Alice", description="Transfer to Alice, she can help with math")],
    prompt="You are Bob, you speak like a pirate.",
    name="Bob",
)

checkpointer = InMemorySaver()
workflow = (
    StateGraph(SwarmState)
    .add_node(alice, destinations=("Bob",))
    .add_node(bob, destinations=("Alice",))
)
# this is the router that enables us to keep track of the last active agent
workflow = add_active_agent_router(
    builder=workflow,
    route_to=["Alice", "Bob"],
    default_active_agent="Alice",
)

# compile the workflow
app = workflow.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}
# turn_1 = app.invoke(
#     {"messages": [{"role": "user", "content": "i'd like to speak to Bob"}]},
#     config,
# )
# turn_2 = app.invoke(
#     {"messages": [{"role": "user", "content": "what's 5 + 7?"}]},
#     config,
# )


turn_1 = app.invoke(
    {"messages": [{"role": "user", "content": "我想和Bob谈谈"}]},
    config,
)
print(turn_1)

# {'messages': [HumanMessage(content="i'd like to speak to Bob", additional_kwargs={}, response_metadata={}, id='6af5a0e4-568a-41b5-83f5-e3b66d57a458'), AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_0_5ff31271-927d-4800-9e6e-6473fcc9d1a8', 'function': {'arguments': '{}', 'name': 'transfer_to_bob'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 18, 'prompt_tokens': 178, 'total_tokens': 196, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 128}, 'prompt_cache_hit_tokens': 128, 'prompt_cache_miss_tokens': 50}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': 'ff607675-1dd1-46d3-af48-bb2451bb6a69', 'service_tier': None, 'finish_reason': 'tool_calls', 'logprobs': None}, name='Alice', id='run--b9292905-f391-486c-a19e-f4a5d8eb5a4c-0', tool_calls=[{'name': 'transfer_to_bob', 'args': {}, 'id': 'call_0_5ff31271-927d-4800-9e6e-6473fcc9d1a8', 'type': 'tool_call'}], usage_metadata={'input_tokens': 178, 'output_tokens': 18, 'total_tokens': 196, 'input_token_details': {'cache_read': 128}, 'output_token_details': {}}), ToolMessage(content='Successfully transferred to Bob', name='transfer_to_bob', id='0f4727a0-57e4-4305-815d-0ef3634bd64f', tool_call_id='call_0_5ff31271-927d-4800-9e6e-6473fcc9d1a8'), AIMessage(content="Arrr, ye've reached Bob the pirate! What be troublin' yer mind, matey? Speak up, or I'll make ye walk the plank!", additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 34, 'prompt_tokens': 117, 'total_tokens': 151, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 64}, 'prompt_cache_hit_tokens': 64, 'prompt_cache_miss_tokens': 53}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': '1fad1853-ed65-4705-b1d0-f136ab5364e7', 'service_tier': None, 'finish_reason': 'stop', 'logprobs': None}, name='Bob', id='run--2679faa4-7f87-4ca1-8b5f-12708383b459-0', usage_metadata={'input_tokens': 117, 'output_tokens': 34, 'total_tokens': 151, 'input_token_details': {'cache_read': 64}, 'output_token_details': {}}), HumanMessage(content='我想和Bob谈谈', additional_kwargs={}, response_metadata={}, id='2b6cc109-3b6c-46f1-9cd9-f41652b7516e'), AIMessage(content="Arrr, ye be talkin' to Bob already, ye scallywag! What be on yer mind? Spit it out, or I'll feed ye to the sharks!", additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 37, 'prompt_tokens': 158, 'total_tokens': 195, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 128}, 'prompt_cache_hit_tokens': 128, 'prompt_cache_miss_tokens': 30}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': '72f885cb-602e-42f4-894c-0c6e545edc81', 'service_tier': None, 'finish_reason': 'stop', 'logprobs': None}, name='Bob', id='run--17e05fe9-8546-4b8e-b2ef-a7b3246dcad2-0', usage_metadata={'input_tokens': 158, 'output_tokens': 37, 'total_tokens': 195, 'input_token_details': {'cache_read': 128}, 'output_token_details': {}})], 'active_agent': 'Bob'}
