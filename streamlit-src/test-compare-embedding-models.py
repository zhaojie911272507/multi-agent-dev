import streamlit as st
import requests
import json
import numpy as np
from typing import List

# 页面设置
st.set_page_config(
    page_title="Embedding模型比较",
    page_icon="🔍",
    layout="wide"
)

# 标题和说明
st.title("🔍 Embedding模型比较工具")
st.markdown("""
这个应用演示了如何使用SentenceTransformers与百炼平台的embedding模型。
您可以选择使用Hugging Face模型或百炼平台的API来生成文本嵌入。
""")

# 创建选项卡
tab1, tab2 = st.tabs(["Hugging Face模型", "百炼平台API"])


# 函数：使用Hugging Face模型生成嵌入
@st.cache_resource
def load_hf_model(model_name):
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(model_name)
    except ImportError:
        st.error("请安装sentence-transformers库: `pip install sentence-transformers`")
        return None


def get_hf_embeddings(model, texts):
    return model.encode(texts)


# 函数：使用百炼平台API生成嵌入
def get_bailian_embeddings(texts, api_key, endpoint):
    # 这里是示例代码，实际使用时需要替换为百炼平台的实际API
    # 通常需要设置请求头、发送请求并处理响应
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 模拟API响应 - 实际使用时需要替换为真实的API调用
    st.info("这是百炼平台API的模拟调用。实际使用时需要替换为真实的API端点、参数和处理逻辑。")

    # 生成随机向量作为模拟响应
    embeddings = []
    for text in texts:
        # 模拟生成384维向量
        embedding = np.random.rand(384).tolist()
        embeddings.append(embedding)

    return embeddings


# Hugging Face模型选项卡
with tab1:
    st.header("使用Hugging Face模型")

    # 模型选择
    hf_model_name = st.selectbox(
        "选择Hugging Face模型",
        ["all-MiniLM-L6-v2", "paraphrase-multilingual-MiniLM-L12-v2", "all-mpnet-base-v2"],
        key="hf_model"
    )

    # 输入文本
    hf_text = st.text_area("输入文本", "这是一个示例文本，用于生成嵌入向量。", key="hf_text")

    if st.button("生成嵌入", key="hf_button"):
        with st.spinner("加载模型并生成嵌入..."):
            model = load_hf_model(hf_model_name)
            if model:
                embeddings = get_hf_embeddings(model, [hf_text])
                st.success("嵌入生成成功！")

                # 显示嵌入向量信息
                st.subheader("嵌入向量信息")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("向量维度", len(embeddings[0]))
                with col2:
                    st.metric("模型", hf_model_name)

                # 显示部分向量值
                st.subheader("部分向量值（前10个维度）")
                st.write(embeddings[0][:10])

                # 可视化
                st.subheader("向量可视化")
                st.line_chart(embeddings[0][:50])

# 百炼平台API选项卡
with tab2:
    st.header("使用百炼平台API")

    # API配置
    api_key = st.text_input("API密钥", type="password", key="api_key")
    endpoint = st.text_input("API端点", "https://api.bailian.platform/embedding", key="endpoint")

    # 输入文本
    bailian_text = st.text_area("输入文本", "这是一个示例文本，用于生成嵌入向量。", key="bailian_text")

    if st.button("生成嵌入", key="bailian_button"):
        if not api_key:
            st.error("请输入API密钥")
        else:
            with st.spinner("调用百炼平台API..."):
                embeddings = get_bailian_embeddings([bailian_text], api_key, endpoint)
                st.success("嵌入生成成功！")

                # 显示嵌入向量信息
                st.subheader("嵌入向量信息")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("向量维度", len(embeddings[0]))
                with col2:
                    st.metric("API端点", endpoint)

                # 显示部分向量值
                st.subheader("部分向量值（前10个维度）")
                st.write(embeddings[0][:10])

                # 可视化
                st.subheader("向量可视化")
                st.line_chart(embeddings[0][:50])

# 比较选项卡
st.divider()
st.header("模型比较")

if st.button("比较两种方法", key="compare_btn"):
    # 这里只是示例，实际比较需要确保两种方法使用相同的文本和相似的向量维度
    st.info("要准确比较两种方法，需要确保它们生成的向量具有相同的维度和标准化方式。")

    # 使用示例文本
    sample_text = "这是一个用于比较的示例文本。"

    # 获取Hugging Face嵌入
    hf_model = load_hf_model("all-MiniLM-L6-v2")
    if hf_model:
        hf_embedding = get_hf_embeddings(hf_model, [sample_text])[0]

        # 获取百炼平台嵌入（模拟）
        bailian_embedding = get_bailian_embeddings([sample_text], "demo_key", "demo_endpoint")[0]

        # 调整维度以便比较（这里只是示例，实际使用时需要确保维度匹配）
        min_len = min(len(hf_embedding), len(bailian_embedding))
        hf_embedding = hf_embedding[:min_len]
        bailian_embedding = bailian_embedding[:min_len]

        # 计算余弦相似度
        from numpy import dot
        from numpy.linalg import norm

        cosine_sim = dot(hf_embedding, bailian_embedding) / (norm(hf_embedding) * norm(bailian_embedding))

        # 显示结果
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Hugging Face模型", "all-MiniLM-L6-v2")
        with col2:
            st.metric("百炼平台API", "模拟调用")
        with col3:
            st.metric("余弦相似度", f"{cosine_sim:.4f}")

        # 显示向量对比图
        st.subheader("向量值对比（前50个维度）")
        comparison_data = {
            "Hugging Face": hf_embedding[:50],
            "百炼平台": bailian_embedding[:50]
        }
        st.line_chart(comparison_data)

# 侧边栏信息
with st.sidebar:
    st.header("关于")
    st.markdown("""
    这个应用演示了两种生成文本嵌入的方法：

    1. **Hugging Face模型**：使用sentence-transformers库
    2. **百炼平台API**：通过HTTP请求调用百炼平台的embedding服务

    要使用百炼平台API，您需要：
    - 有效的API密钥
    - API端点URL
    - 了解API的请求/响应格式
    """)

    st.divider()
    st.markdown("**注意**：此应用中的百炼平台API调用是模拟的，实际使用时需要替换为真实的API调用代码。")