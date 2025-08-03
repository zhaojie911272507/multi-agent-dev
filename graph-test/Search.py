import os
from typing import Annotated, List

from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_tavily import TavilySearch
from langchain_core.tools import tool

# # Set USER_AGENT in your environment first (or define it here temporarily)
# os.environ['USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
#
# # Fetch the USER_AGENT from environment
# headers = {'User-Agent': os.environ['USER_AGENT']}

load_dotenv()
print(os.getenv("TAVILY_API_KEY"))
exit()
tavily_tool = TavilySearch(max_results=5, api_key=os.getenv("TAVILY_API_KEY"))


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

# print(scrape_webpages(["https://www.google.com", "https://www.bing.com"]))
