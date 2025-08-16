print("来咯")
import os

from dotenv import load_dotenv

load_dotenv()

# Get keys for your project from the project settings page: https://cloud.langfuse.com
os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC_KEY")
os.environ["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET_KEY")
os.environ["LANGFUSE_HOST"] = os.getenv("LANGFUSE_HOST")  # 🇪🇺 EU region
# os.environ["LANGFUSE_HOST"] = "https://us.cloud.langfuse.com" # 🇺🇸 US region

# Your DeepSeek API key (get it from https://platform.deepseek.com/api_keys)
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")  # Replace with your DeepSeek API key
