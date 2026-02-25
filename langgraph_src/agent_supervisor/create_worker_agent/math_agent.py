import os

from dotenv import load_dotenv
from langchain_core.messages import convert_to_messages
from langgraph.prebuilt import create_react_agent


load_dotenv()
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")


def add(a: float, b: float):
    """Add two numbers."""
    return a + b


def multiply(a: float, b: float):
    """Multiply two numbers."""
    return a * b


def divide(a: float, b: float):
    """Divide two numbers."""
    return a / b


math_agent = create_react_agent(
    model="deepseek-chat",
    tools=[add, multiply, divide],
    prompt=(
        "You are a math agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with math-related tasks\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="math_agent",
)

def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)


def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        # skip parent graph updates in the printouts
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label)
        print("\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")

# res = math_agent.invoke({"messages": [{"content": "What is 2 + 2?", "role": "user"}]})
# print(res)

if __name__ == "__main__":
    for chunk in math_agent.stream(
        {"messages": [{"role": "user", "content": "2+2等于几?"}]}
    ):
        pretty_print_messages(chunk)




# Update from node agent:
#
#
# ================================== Ai Message ==================================
# Name: math_agent
# Tool Calls:
#   add (call_0_e56ffa72-804c-4e14-b491-388c44351aa8)
#  Call ID: call_0_e56ffa72-804c-4e14-b491-388c44351aa8
#   Args:
#     a: 2
#     b: 2
#
#
# Update from node tools:
#
#
# ================================= Tool Message =================================
# Name: add
#
# 4.0
#
#
# Update from node agent:
#
#
# ================================== Ai Message ==================================
# Name: math_agent
#
# 4.0






#
# {'messages': [HumanMessage(content='What is 2 + 2?',
#                            additional_kwargs={},
#                            response_metadata={},
#                            id='3dcf8dc7-980e-4918-aa11-c72acb51e805'),
#               AIMessage(content='',
#                         additional_kwargs={'tool_calls': [{'id': 'call_0_f24f8798-7218-4611-a39d-dca8719ba613', 'function': {'arguments': '{"a":2,"b":2}', 'name': 'add'}, 'type': 'function', 'index': 0}], 'refusal': None},
#                         response_metadata={'token_usage': {'completion_tokens': 21, 'prompt_tokens': 349, 'total_tokens': 370, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 0}, 'prompt_cache_hit_tokens': 0, 'prompt_cache_miss_tokens': 349}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': '92fad275-52b3-4105-86c8-194d3319ae23', 'service_tier': None, 'finish_reason': 'tool_calls', 'logprobs': None},
#                         name='math_agent',
#                         id='run--66545423-df13-4c96-a4be-db609f1f8e72-0',
#                         tool_calls=[{'name': 'add', 'args': {'a': 2, 'b': 2}, 'id': 'call_0_f24f8798-7218-4611-a39d-dca8719ba613', 'type': 'tool_call'}],
#                         usage_metadata={'input_tokens': 349, 'output_tokens': 21, 'total_tokens': 370, 'input_token_details': {'cache_read': 0}, 'output_token_details': {}}),
#               ToolMessage(content='4.0',
#                           name='add',
#                           id='74f80e53-675d-43ed-969f-c1e8636895a9',
#                           tool_call_id='call_0_f24f8798-7218-4611-a39d-dca8719ba613'),
#               AIMessage(content='4.0',
#                         additional_kwargs={'refusal': None},
#                         response_metadata={'token_usage': {'completion_tokens': 3, 'prompt_tokens': 381, 'total_tokens': 384, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 320}, 'prompt_cache_hit_tokens': 320, 'prompt_cache_miss_tokens': 61}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_8802369eaa_prod0623_fp8_kvcache', 'id': '8c60f866-8b03-4d2a-9058-c71f509a46f3', 'service_tier': None, 'finish_reason': 'stop', 'logprobs': None},
#                         name='math_agent', id='run--0fd8be13-a2a1-49fa-84b2-55e038e26700-0',
#                         usage_metadata={'input_tokens': 381,
#                                         'output_tokens': 3,
#                                         'total_tokens': 384,
#                                         'input_token_details': {'cache_read': 320},
#                                         'output_token_details': {}
#                                         }
#                         )
#               ]
#  }


