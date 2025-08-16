import os

from crewai import LLM
from dotenv import load_dotenv

load_dotenv()
# 定义 DeepSeek 模型实例
LLM_DS = LLM(
    model="deepseek/deepseek-chat",  # 或 "deepseek/deepseek-reasoner"
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 替换为实际 API Key
    stream=True,
)


