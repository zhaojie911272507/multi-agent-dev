"""
LlamaIndex 示例：Completion、Chat、Streaming、RAG
"""

from llama_index.core import Document, Settings, SummaryIndex
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai_like import OpenAILike


def run_completion(llm: OpenAILike) -> None:
    """Completion 风格调用"""
    print("\n" + "-" * 50)
    print("Completion")
    print("-" * 50)
    resp = llm.complete("用一句话介绍 Python 语言。")
    print(resp.text)


def run_chat(llm: OpenAILike) -> None:
    """Chat 风格调用"""
    print("\n" + "-" * 50)
    print("Chat")
    print("-" * 50)
    messages = [
        ChatMessage(role="system", content="你是一个简洁的技术助手。"),
        ChatMessage(role="user", content="什么是 RESTful API？用 2 句话说明。"),
    ]
    resp = llm.chat(messages)
    print(resp.message.content)


def run_streaming(llm: OpenAILike) -> None:
    """流式 Completion"""
    print("\n" + "-" * 50)
    print("Streaming")
    print("-" * 50)
    resp = llm.stream_complete("数到 5：")
    for r in resp:
        print(r.delta, end="", flush=True)
    print()


def run_rag(llm: OpenAILike) -> None:
    """简单 RAG：SummaryIndex 无需 embedding"""
    print("\n" + "-" * 50)
    print("RAG")
    print("-" * 50)
    Settings.llm = llm

    doc = Document(
        text="""LlamaIndex 是一个数据框架，用于构建 LLM 应用。
它支持多种数据源、检索增强生成（RAG）和结构化输出。
核心概念包括：Index、Query Engine、Retriever、Response Synthesizer。"""
    )

    index = SummaryIndex.from_documents([doc])
    query_engine = index.as_query_engine()
    response = query_engine.query("LlamaIndex 的核心概念有哪些？")
    print(response.response)


if __name__ == "__main__":
    from config import get_llm

    llm = get_llm()
    run_completion(llm)
    run_chat(llm)
    run_streaming(llm)
    run_rag(llm)
