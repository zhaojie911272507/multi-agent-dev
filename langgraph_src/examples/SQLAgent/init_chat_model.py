import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")
print("load deepseek model....")
llm = init_chat_model("deepseek-chat")
