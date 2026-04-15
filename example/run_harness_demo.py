"""启动 Harness 评测示例。"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    subprocess.run(
        [sys.executable, "-m", "harness_src.weather_harness.runner"],
        cwd=ROOT,
        check=True,
    )


if __name__ == "__main__":
    main()
