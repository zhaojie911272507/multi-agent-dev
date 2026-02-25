import os
import uuid
from datetime import datetime

from langchain_openai import ChatOpenAI

from evomap_src.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TEMPERATURE


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
