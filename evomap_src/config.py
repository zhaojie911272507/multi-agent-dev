import os

from dotenv import load_dotenv

load_dotenv()

LLM_MODEL = os.getenv("EVOMAP_LLM_MODEL", "deepseek-chat")
LLM_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
LLM_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
LLM_TEMPERATURE = float(os.getenv("EVOMAP_LLM_TEMPERATURE", "0.3"))

CONFIDENCE_THRESHOLD = float(os.getenv("EVOMAP_CONFIDENCE_THRESHOLD", "0.6"))

MAX_SEARCH_RESULTS = int(os.getenv("EVOMAP_MAX_SEARCH_RESULTS", "8"))

LANGFUSE_ENABLED = os.getenv("LANGFUSE_PUBLIC_KEY", "") != ""
