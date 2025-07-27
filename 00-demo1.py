import getpass
import os


def _set_if_undefined(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please provide your {var}")


_set_if_undefined("OPENAI_API_KEY")
_set_if_undefined("TAVILY_API_KEY")



os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.environ.get("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")

