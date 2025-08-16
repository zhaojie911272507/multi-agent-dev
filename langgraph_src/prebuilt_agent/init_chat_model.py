from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from create_react_agent import get_weather

model = init_chat_model(
    "deepseek-chat",
    temperature=0
)

agent = create_react_agent(
    model=model,
    tools=[get_weather],
)