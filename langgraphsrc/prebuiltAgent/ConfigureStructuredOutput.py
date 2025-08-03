# To produce structured responses conforming to a schema, use the response_format parameter. The schema can be defined with a Pydantic model or TypedDict. The result will be accessible via the structured_response field.
# 要生成符合特定模式的结构化响应，请使用 response_format 参数。该模式可以使用 Pydantic 模型或 TypedDict 定义。结果可通过 structured_response 字段访问。

from pydantic import BaseModel
from langgraph.prebuilt import create_react_agent
from getweather import get_weather

import os
from dotenv import load_dotenv

load_dotenv()
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")


class WeatherResponse(BaseModel):
    conditions: str

agent = create_react_agent(
    model="deepseek-chat",
    tools=[get_weather],
    response_format=WeatherResponse
)

response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)

print(response["structured_response"])