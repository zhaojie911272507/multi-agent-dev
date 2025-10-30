import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")
print("load deepseek model....")
llm = init_chat_model("deepseek-chat")
#
# from langchain_openai import ChatOpenAI
#
# llm = ChatOpenAI(model="qwen-max",
#                    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1",
#                    api_key = os.getenv("DASHSCOPE_API_KEY")
#                    )
