# import getpass
# import os
#
#
# def _set_if_undefined(var: str):
#     if not os.environ.get(var):
#         os.environ[var] = getpass.getpass(f"Please provide your {var}")
#
#
# # _set_if_undefined("OPENAI_API_KEY")
# _set_if_undefined("TAVILY_API_KEY")
#
#
# # os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
# # os.environ["TAVILY_API_KEY"] = os.environ.get("TAVILY_API_KEY")

import getpass
import os
from dotenv import load_dotenv  # 需要安装 python-dotenv

# 加载 .env 文件
load_dotenv()

def prompt_for_env_variable(var: str) -> None:
    """Prompt user for environment variable if not already set."""
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please enter your {var}: ")

a= prompt_for_env_variable("TAVILY_API_KEY")


print(a)