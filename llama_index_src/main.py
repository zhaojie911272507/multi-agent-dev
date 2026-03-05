"""
LlamaIndex 百炼 Qwen 示例入口

用法: python -m llama_index_src
或: python llama_index_src/main.py
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from llama_index_src.config import DEFAULT_MODEL, get_llm
from llama_index_src.examples import run_chat, run_completion, run_rag, run_streaming


def main() -> None:
    llm = get_llm()
    print("LlamaIndex + 百炼 Qwen")
    print(f"模型: {DEFAULT_MODEL} | API: DashScope 兼容模式")

    run_completion(llm)
    run_chat(llm)
    run_streaming(llm)
    run_rag(llm)

    print("\n完成")


if __name__ == "__main__":
    main()
