"""
LlamaIndex 百炼 Qwen 配置

依赖: DASHSCOPE_API_KEY
兼容端点: https://dashscope.aliyuncs.com/compatible-mode/v1
"""

import os

from dotenv import load_dotenv
from llama_index.llms.openai_like import OpenAILike

load_dotenv()

DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen-plus"


def get_llm() -> OpenAILike:
    """创建百炼 Qwen LLM 实例，使用 OpenAI 兼容接口。"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError(
            "请设置 DASHSCOPE_API_KEY 环境变量或在 .env 中配置。"
            "获取地址: https://dashscope.console.aliyun.com/"
        )
    return OpenAILike(
        model=DEFAULT_MODEL,
        api_base=DASHSCOPE_BASE_URL,
        api_key=api_key,
        context_window=128000,
        is_chat_model=True,
        is_function_calling_model=True,
    )
