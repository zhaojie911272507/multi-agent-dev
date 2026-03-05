"""启动 EvoMap 知识演化图谱（CLI）"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    subprocess.run(
        [sys.executable, "-m", "evomap_src.main", "-q", "大语言模型的演化历程", "-s"],
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
