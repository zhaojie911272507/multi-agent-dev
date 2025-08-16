import os

from langfuse.langchain import CallbackHandler
from langchain_core.prompts import ChatPromptTemplate

langfuse_handler = CallbackHandler()

from langchain_openai import ChatOpenAI

llm=ChatOpenAI(model="deepseek-chat",
               openai_api_base = "https://api.deepseek.com/v1/",
               openai_api_key = os.getenv("DEEPSEEK_API_KEY")
            )
prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
chain = prompt | llm

# Set trace attributes dynamically via metadata
response = chain.invoke(
    {"topic": "cats"},
    config={
        "callbacks": [langfuse_handler],
        "metadata": {
            "langfuse_user_id": "random-user",
            "langfuse_session_id": "random-session",
            "langfuse_tags": ["random-tag-1", "random-tag-2"]
        }
    }
)

print(response)

