"""启动 LlamaIndex 示例（百炼 Qwen，需 DASHSCOPE_API_KEY）"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    subprocess.run(
        [sys.executable, str(ROOT / "llama_index_src" / "main.py")],
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
