# Define a fixed prompt string or list of messages:
# 定义固定的提示字符串或消息列表：

import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from getweather import get_weather

load_dotenv()
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")

agent = create_react_agent(
    model="deepseek-chat",
    tools=[get_weather],
    # A static prompt that never changes
    prompt="Never answer questions about the weather."
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)

print(result.get("messages")[-1].content)