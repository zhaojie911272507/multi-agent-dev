from pydantic import BaseModel

import os

from crewai import LLM
from dotenv import load_dotenv

load_dotenv()

class dog(BaseModel):
    name: str
    age: int
    bree: str


# 定义 DeepSeek 模型实例
llm = LLM(
    model="deepseek/deepseek-chat",  # 或 "deepseek/deepseek-reasoner"
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 替换为实际 API Key
    stream=True,

)

# response = llm.call(
# "分析以下消息并返回姓名、年龄和品种。",
# "认识科纳！它今年 3 岁，是一只黑色德国牧羊犬。"
# )

response = llm.call(
    "Analyze the following messages and return the name, age, and breed. "
    "Meet Kona! She is 3 years old and is a black german shepherd."
)

print(response)

