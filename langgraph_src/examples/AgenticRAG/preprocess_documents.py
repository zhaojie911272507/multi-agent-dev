from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders.web_base import default_header_template
from sympy import print_glsl

urls = [
    "https://lilianweng.github.io/posts/2024-11-28-reward-hacking/",
    "https://lilianweng.github.io/posts/2024-07-07-hallucination/",
    "https://lilianweng.github.io/posts/2024-04-12-diffusion-video/",
]

# default_header_template.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"})
# print(default_header_template)
docs = [WebBaseLoader(url).load() for url in urls]


# print(docs[0][0].page_content.strip()[:1000])

# Split the fetched documents into smaller chunks for indexing into our vectorstore:
from langchain_text_splitters import RecursiveCharacterTextSplitter

docs_list = [item for sublist in docs for item in sublist]

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=100, chunk_overlap=50
)
doc_splits = text_splitter.split_documents(docs_list)


# print(doc_splits[0].page_content.strip())
print(1)
