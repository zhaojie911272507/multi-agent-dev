from __future__ import annotations

import os


def build_weather_agent():
    """Build a small weather agent that the harness can evaluate."""

    from dotenv import load_dotenv
    from langchain.chat_models import init_chat_model
    from langgraph.prebuilt import create_react_agent

    from langgraph_src.prebuilt_agent.getweather import get_weather

    load_dotenv()
    model_name = os.getenv("HARNESS_MODEL_NAME", "deepseek-chat")
    model = init_chat_model(model_name, temperature=0)
    return create_react_agent(
        model=model,
        tools=[get_weather],
        prompt="You are a helpful assistant for weather questions.",
    )
