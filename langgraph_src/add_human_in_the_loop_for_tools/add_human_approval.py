# How to add a human-in-the-loop for tools
# 为工具添加人机交互

import json

from langchain_core.messages import AIMessage

from demo1 import *

class NotApproved(Exception):
    """Custom exception."""


def human_approval(msg: AIMessage) -> AIMessage:
    """Responsible for passing through its input or raising an exception.

    Args:
        msg: output from the chat model

    Returns:
        msg: original output from the msg
    """
    tool_strs = "\n\n".join(
        json.dumps(tool_call, indent=2) for tool_call in msg.tool_calls
    )
    input_msg = (
        f"Do you approve of the following tool invocations\n\n{tool_strs}\n\n"
        "Anything except 'Y'/'Yes' (case-insensitive) will be treated as a no.\n >>>"
    )
    resp = input(input_msg)
    if resp.lower() not in ("yes", "y"):
        raise NotApproved(f"Tool invocations not approved:\n\n{tool_strs}")
    return msg


chain = llm_with_tools | human_approval | call_tools
r = chain.invoke("how many emails did i get in the last 5 days?")
print(r)



# Do you approve of the following tool invocations
#
# {
#   "name": "count_emails",
#   "args": {
#     "last_n_days": 5
#   },
#   "id": "call_0_8d84d3c5-1ebb-44bf-8622-5ced797b482d",
#   "type": "tool_call"
# }
#
# Anything except 'Y'/'Yes' (case-insensitive) will be treated as a no.
#  >>>y
# [{'name': 'count_emails', 'args': {'last_n_days': 5}, 'id': 'call_0_8d84d3c5-1ebb-44bf-8622-5ced797b482d', 'type': 'tool_call', 'output': 10}]


