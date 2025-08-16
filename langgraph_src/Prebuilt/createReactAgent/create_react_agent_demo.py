import os

from langgraph.prebuilt import create_react_agent


from dotenv import load_dotenv

load_dotenv()
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")

def check_weather(location: str) -> str:
    '''Return the weather forecast for the specified location.'''
    return f"It's always sunny in {location}"

graph = create_react_agent(
    "deepseek-chat",
    tools=[check_weather],
    prompt="You are a helpful assistant",
)
inputs = {"messages": [{"role": "user", "content": "what is the weather in shanghai today"}]}
for chunk in graph.stream(inputs, stream_mode="updates"):
    print(chunk)





'''
{'agent': {'messages': [AIMessage(content='',
                                  additional_kwargs={'tool_calls': [{'id': 'call_0_dbcb7920-2178-4931-aa88-114d0564ae08', 
                                                                     'function': {'arguments': '{"location":"Shanghai"}', 
                                                                                  'name': 'check_weather'}, 
                                                                     'type': 'function', 'index': 0}], 
                                                     'refusal': None},
                                  response_metadata={'token_usage': {'completion_tokens': 20, 
                                                                     'prompt_tokens': 113, 
                                                                     'total_tokens': 133, 
                                                                     'completion_tokens_details': None, 
                                                                     'prompt_tokens_details': {'audio_tokens': None, 
                                                                                               'cached_tokens': 0}, 
                                                                     'prompt_cache_hit_tokens': 0, 
                                                                     'prompt_cache_miss_tokens': 113}, 
                                                     'model_name': 'deepseek-chat', 
                                                     'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache',
                                                     'id': '472be214-167a-47de-b349-a55a53c8b862', 
                                                     'service_tier': None, 
                                                     'finish_reason': 'tool_calls', 
                                                     'logprobs': None},
                                  id='run--2174f6b3-4026-421e-8f93-6435444487da-0',
                                  tool_calls=[{'name': 'check_weather', 
                                               'args': {'location': 'Shanghai'}, 
                                               'id': 'call_0_dbcb7920-2178-4931-aa88-114d0564ae08', 
                                               'type': 'tool_call'}], 
                                  usage_metadata={'input_tokens': 113, 
                                                  'output_tokens': 20, 
                                                  'total_tokens': 133, 
                                                  'input_token_details': {'cache_read': 0}, 
                                                  'output_token_details': {}
                                                  }
                                  )
                        ]
           }
 }
{'tools': {'messages': [ToolMessage(content="It's always sunny in Shanghai", 
                                    name='check_weather', 
                                    id='f7bef310-a167-4567-953a-c8352f0f8cfc', 
                                    tool_call_id='call_0_dbcb7920-2178-4931-aa88-114d0564ae08')
                        ]
           }
 }
{'agent': {'messages': [AIMessage(content='The weather in Shanghai today is sunny. Enjoy the bright skies!', 
                                  additional_kwargs={'refusal': None}, 
                                  response_metadata={'token_usage': {'completion_tokens': 13,
                                                                     'prompt_tokens': 145, 
                                                                     'total_tokens': 158, 
                                                                     'completion_tokens_details': None, 
                                                                     'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 64}, 
                                                                     'prompt_cache_hit_tokens': 64, 'prompt_cache_miss_tokens': 81}, 
                                                     'model_name': 'deepseek-chat', 
                                                     'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 
                                                     'id': 'ce572c18-2ca4-4f54-9c79-4205fdd5bb2e', 
                                                     'service_tier': None, 
                                                     'finish_reason': 'stop', 'logprobs': None}, 
                                  id='run--8cffca78-a285-443f-86b3-3d99f004b3e9-0', 
                                  usage_metadata={'input_tokens': 145, 
                                                  'output_tokens': 13, 
                                                  'total_tokens': 158, 
                                                  'input_token_details': {'cache_read': 64}, 
                                                  'output_token_details': {}
                                                  }
                                  )
                        ]
           }
 }
'''