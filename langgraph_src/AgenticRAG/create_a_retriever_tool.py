import os

from dotenv import load_dotenv
# 1.Use an in-memory vector store and Qwen embeddings:
# 使用内存中的向量存储和 Qwen 嵌入：
from langchain_core.vectorstores import InMemoryVectorStore
load_dotenv()
# 设置阿里云 API Key
# dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

from langchain_community.embeddings import DashScopeEmbeddings
embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
    # other params...
)

from preprocess_documents import doc_splits

vectorstore = InMemoryVectorStore.from_documents(
    documents=doc_splits, embedding=embeddings
)

retriever = vectorstore.as_retriever()
print(retriever)

# 2.Create a retriever tool using LangChain's prebuilt create_retriever_tool:
# 使用 LangChain 的预构建组件创建一个检索工具： create_retriever_tool
from langchain.tools.retriever import create_retriever_tool

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_blog_posts",
    "Search and return information about Lilian Weng blog posts.",
)

# result = retriever_tool.invoke({"query": "types of reward hacking"})
# print(result)

