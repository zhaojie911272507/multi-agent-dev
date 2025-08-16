import getpass
import os

# need to set deepseek_api_key in environment variables
if not os.environ.get("deepseek_api_key"):
  os.environ["deepseek_api_key"] = getpass.getpass("Enter API key for Anthropic: ")

from langchain.chat_models import init_chat_model

model = init_chat_model("deepseek-chat")

a = model.invoke("Hello, world!")
print(a)
