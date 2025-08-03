# To allow multi-turn conversations with an agent, you need to enable persistence by providing a checkpointer when creating an agent. At runtime, you need to provide a config containing thread_id — a unique identifier for the conversation (session):
# 要允许与代理进行多轮对话，您需要在创建代理时提供 checkpointer 来启用持久性 。在运行时，您需要提供一个包含 thread_id 的配置——对话（会话）的唯一标识符：
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from getweather import get_weather
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")


checkpointer = InMemorySaver()

agent = create_react_agent(
    model='deepseek-chat',
    tools=[get_weather],
    checkpointer=checkpointer
)

# Run the agent
config = {"configurable": {"thread_id": "1"}}
sf_response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
    config
)
ny_response = agent.invoke(
    {"messages": [{"role": "user", "content": "what about new york?"}]},
    config
)
print(sf_response)
print(ny_response)

sf_response = {'messages':
                   [HumanMessage(content='what is the weather in sf', additional_kwargs={}, response_metadata={}, id='efc7f72f-eac5-4c1f-93e7-e579759bb382'),
                    AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_0_7f7678b5-41bd-4739-a4f4-a2a0aa1da237', 'function': {'arguments': '{"city":"sf"}', 'name': 'get_weather'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 19, 'prompt_tokens': 108, 'total_tokens': 127, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 64}, 'prompt_cache_hit_tokens': 64, 'prompt_cache_miss_tokens': 44}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': 'd4c95acd-fabc-4c9d-a5da-492caec7a332', 'service_tier': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run--e2f701bc-d1b1-4c27-91e7-176682878935-0', tool_calls=[{'name': 'get_weather', 'args': {'city': 'sf'}, 'id': 'call_0_7f7678b5-41bd-4739-a4f4-a2a0aa1da237', 'type': 'tool_call'}], usage_metadata={'input_tokens': 108, 'output_tokens': 19, 'total_tokens': 127, 'input_token_details': {'cache_read': 64}, 'output_token_details': {}}),
                    ToolMessage(content="It's always sunny in sf!", name='get_weather', id='f25c7728-70f5-46ff-8a1a-69fe7727fbfe', tool_call_id='call_0_7f7678b5-41bd-4739-a4f4-a2a0aa1da237'),
                    AIMessage(content='The weather in San Francisco (SF) is currently sunny! Enjoy the beautiful day!', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 17, 'prompt_tokens': 140, 'total_tokens': 157, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 128}, 'prompt_cache_hit_tokens': 128, 'prompt_cache_miss_tokens': 12}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': '4b712cc0-179c-47d2-8ef4-7b6560d6a0f7', 'service_tier': None, 'finish_reason': 'stop', 'logprobs': None}, id='run--3d072be0-a1ae-4358-b460-6c0855208f57-0', usage_metadata={'input_tokens': 140, 'output_tokens': 17, 'total_tokens': 157, 'input_token_details': {'cache_read': 128}, 'output_token_details': {}})
                   ]
}

sf_response = {'messages':
                   [HumanMessage(content='what is the weather in sf', additional_kwargs={}, response_metadata={}, id='efc7f72f-eac5-4c1f-93e7-e579759bb382'),
                    AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_0_7f7678b5-41bd-4739-a4f4-a2a0aa1da237', 'function': {'arguments': '{"city":"sf"}', 'name': 'get_weather'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 19, 'prompt_tokens': 108, 'total_tokens': 127, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 64}, 'prompt_cache_hit_tokens': 64, 'prompt_cache_miss_tokens': 44}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': 'd4c95acd-fabc-4c9d-a5da-492caec7a332', 'service_tier': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run--e2f701bc-d1b1-4c27-91e7-176682878935-0', tool_calls=[{'name': 'get_weather', 'args': {'city': 'sf'}, 'id': 'call_0_7f7678b5-41bd-4739-a4f4-a2a0aa1da237', 'type': 'tool_call'}], usage_metadata={'input_tokens': 108, 'output_tokens': 19, 'total_tokens': 127, 'input_token_details': {'cache_read': 64}, 'output_token_details': {}}),
                    ToolMessage(content="It's always sunny in sf!", name='get_weather', id='f25c7728-70f5-46ff-8a1a-69fe7727fbfe', tool_call_id='call_0_7f7678b5-41bd-4739-a4f4-a2a0aa1da237'),
                    AIMessage(content='The weather in San Francisco (SF) is currently sunny! Enjoy the beautiful day!', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 17, 'prompt_tokens': 140, 'total_tokens': 157, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 128}, 'prompt_cache_hit_tokens': 128, 'prompt_cache_miss_tokens': 12}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': '4b712cc0-179c-47d2-8ef4-7b6560d6a0f7', 'service_tier': None, 'finish_reason': 'stop', 'logprobs': None}, id='run--3d072be0-a1ae-4358-b460-6c0855208f57-0', usage_metadata={'input_tokens': 140, 'output_tokens': 17, 'total_tokens': 157, 'input_token_details': {'cache_read': 128}, 'output_token_details': {}}),
                    HumanMessage(content='what about new york?', additional_kwargs={}, response_metadata={}, id='cb670592-5f55-4ffe-8b11-6caca4f94719'),
                    AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_0_22421be8-29b8-45a5-bd7b-5618cc3f1fcb', 'function': {'arguments': '{"city":"New York"}', 'name': 'get_weather'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 20, 'prompt_tokens': 166, 'total_tokens': 186, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 128}, 'prompt_cache_hit_tokens': 128, 'prompt_cache_miss_tokens': 38}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': '396897bf-174b-41f2-a361-3db0620f45c7', 'service_tier': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run--c1a92a7c-b2ad-41ac-b08b-046b0813d945-0', tool_calls=[{'name': 'get_weather', 'args': {'city': 'New York'}, 'id': 'call_0_22421be8-29b8-45a5-bd7b-5618cc3f1fcb', 'type': 'tool_call'}], usage_metadata={'input_tokens': 166, 'output_tokens': 20, 'total_tokens': 186, 'input_token_details': {'cache_read': 128}, 'output_token_details': {}}),
                    ToolMessage(content="It's always sunny in New York!", name='get_weather', id='c65eee12-452b-4a29-a97e-73c6dd9bb5e6', tool_call_id='call_0_22421be8-29b8-45a5-bd7b-5618cc3f1fcb'),
                    AIMessage(content='The weather in New York is also sunny! Looks like a great day there too!', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 17, 'prompt_tokens': 200, 'total_tokens': 217, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 128}, 'prompt_cache_hit_tokens': 128, 'prompt_cache_miss_tokens': 72}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': 'f78b275e-a2cf-4ee5-af8a-f2629ad234aa', 'service_tier': None, 'finish_reason': 'stop', 'logprobs': None}, id='run--592a405d-c3f3-43fa-8c81-ab67cc665e51-0', usage_metadata={'input_tokens': 200, 'output_tokens': 17, 'total_tokens': 217, 'input_token_details': {'cache_read': 128}, 'output_token_details': {}})
                    ]
               }



print(sf_response.get("messages")[-1].content)
print(ny_response.get("messages")[-1].content)

