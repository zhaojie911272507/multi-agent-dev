import getpass
import os

from dotenv import load_dotenv

load_dotenv()
#
# def _set_if_undefined(var: str):
#     if not os.environ.get(var):
#         os.environ[var] = getpass.getpass(f"Please provide your {var}")

# def _set_if_undefined(var: str):
#     if not os.getenv(var):
#         os.environ[var] = getpass.getpass(f"Please provide your {var}")
# # _set_if_undefined("OPENAI_API_KEY")
# _set_if_undefined("TAVILY_API_KEY")

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

from typing import Annotated, List

from langchain_community.document_loaders import WebBaseLoader
from langchain_tavily import TavilySearch
from langchain_core.tools import tool

tavily_tool = TavilySearch(max_results=5)


@tool
def scrape_webpages(urls: List[str]) -> str:
    """Use requests and bs4 to scrape the provided web pages for detailed information."""
    loader = WebBaseLoader(urls)
    docs = loader.load()
    return "\n\n".join(
        [
            f'<Document name="{doc.metadata.get("title", "")}">\n{doc.page_content}\n</Document>'
            for doc in docs
        ]
    )