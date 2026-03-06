import os
import re
import uuid
from datetime import datetime
from typing import TypeVar

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

from evomap_src.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TEMPERATURE

T = TypeVar("T")


def _extract_json(text: str) -> str:
    """从 LLM 输出中提取 JSON（可能被 ```json ... ``` 包裹）"""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if m:
        return m.group(1).strip()
    return text


def structured_invoke(
    llm: ChatOpenAI,
    schema: type[T],
    messages: list[BaseMessage],
) -> T:
    """调用 LLM 获取结构化输出，若 response_format 不可用则回退到 JSON 解析"""
    try:
        chain = llm.with_structured_output(schema)
        return chain.invoke(messages)
    except Exception as e:
        err_str = str(e).lower()
        if "response_format" not in err_str and "invalid_request" not in err_str:
            raise

    parser = PydanticOutputParser(pydantic_object=schema)
    format_instructions = parser.get_format_instructions()
    fallback_messages = list(messages) + [
        HumanMessage(
            content=f"请严格按以下 JSON 格式输出，不要输出其他内容：\n{format_instructions}"
        ),
    ]
    response = llm.invoke(fallback_messages)
    raw = response.content if hasattr(response, "content") else str(response)
    return parser.parse(_extract_json(raw))


def get_llm(temperature: float | None = None) -> ChatOpenAI:
    return ChatOpenAI(
        model=LLM_MODEL,
        openai_api_key=LLM_API_KEY,
        openai_api_base=LLM_BASE_URL,
        temperature=temperature if temperature is not None else LLM_TEMPERATURE,
    )


def gen_id() -> str:
    return uuid.uuid4().hex[:8]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def save_report(report: str, filename: str | None = None) -> str:
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    if filename is None:
        filename = f"evomap_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    return path
