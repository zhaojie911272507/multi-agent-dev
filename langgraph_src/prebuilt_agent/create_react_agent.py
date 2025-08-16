import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from openai import api_key


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

load_dotenv()
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")
agent = create_react_agent(
    model="deepseek-chat",
    tools=[get_weather],
    prompt="You are a helpful assistant"
)

# # Run the agent
# a = agent.invoke(
#     {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
# )

j = {'messages': [
        HumanMessage(content='what is the weather in sf',
                     additional_kwargs={},
                     response_metadata={},
                     id='98e4fd06-f68f-4371-85cc-ee840427a49e'),
        AIMessage(content='',
                  additional_kwargs={
                      'tool_calls': [{'id': 'call_0_a80df37d-44ff-400f-8f69-0af442af6d62',
                                      'function': {'arguments': '{"city":"sf"}', 'name': 'get_weather'},
                                      'type': 'function', 'index': 0}],
                      'refusal': None},
                  response_metadata={
                      'token_usage': {'completion_tokens': 19,
                                      'prompt_tokens': 108,
                                      'total_tokens': 127,
                                      'completion_tokens_details': None,
                                      'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 64},
                                      'prompt_cache_hit_tokens': 64, 'prompt_cache_miss_tokens': 44},
                      'model_name': 'deepseek-chat',
                      'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache',
                      'id': '8d0ba58c-732b-44e4-925e-1b45b8d6eff1',
                      'service_tier': None,
                      'finish_reason': 'tool_calls',
                      'logprobs': None},
                  id='run--aef27175-dd24-4d91-9752-9e690a8948b4-0',
                  tool_calls=[{'name': 'get_weather',
                               'args': {'city': 'sf'},
                               'id': 'call_0_a80df37d-44ff-400f-8f69-0af442af6d62',
                               'type': 'tool_call'}],
                  usage_metadata={'input_tokens': 108,
                                  'output_tokens': 19,
                                  'total_tokens': 127,
                                  'input_token_details': {'cache_read': 64},
                                  'output_token_details': {}}
                  ),
        ToolMessage(content="It's always sunny in sf!",
                    name='get_weather',
                    id='f8ed06cf-e86a-40d0-87e9-d8b91ec7124b',
                    tool_call_id='call_0_a80df37d-44ff-400f-8f69-0af442af6d62'
                    ),
        AIMessage(content='The weather in San Francisco (SF) is sunny! Enjoy the beautiful day!',
                  additional_kwargs={'refusal': None},
                  response_metadata={'token_usage':
                                         {'completion_tokens': 16,
                                          'prompt_tokens': 140,
                                          'total_tokens': 156,
                                          'completion_tokens_details': None,
                                          'prompt_tokens_details':
                                              {'audio_tokens': None,
                                               'cached_tokens': 128
                                               },
                                          'prompt_cache_hit_tokens': 128,
                                          'prompt_cache_miss_tokens': 12},
                                     'model_name': 'deepseek-chat',
                                     'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache',
                                     'id': 'e77c5bb3-4cc8-4f7d-89b0-8b9f9e9d7ad0',
                                     'service_tier': None,
                                     'finish_reason': 'stop',
                                     'logprobs': None
                                     },
                  id='run--4122b107-077c-431d-9cff-31785ea69a24-0',
                  usage_metadata={'input_tokens': 140,
                                  'output_tokens': 16,
                                  'total_tokens': 156,
                                  'input_token_details':
                                      {
                                          'cache_read': 128
                                      },
                                  'output_token_details': {}}
                  )
]
}

print(j.get('messages')[3].content)