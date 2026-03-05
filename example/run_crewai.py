"""启动 CrewAI 示例"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    subprocess.run(
        [sys.executable, str(ROOT / "crewai_src" / "crewsrc" / "crewaidemo" / "src" / "crewaidemo" / "main.py")],
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
