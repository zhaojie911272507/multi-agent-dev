import streamlit as st
import requests
import json
import numpy as np
from typing import List
import os

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
您可以选择使用Hugging Face模型、本地模型或百炼平台的API来生成文本嵌入。
""")

# 创建选项卡
tab1, tab2, tab3 = st.tabs(["Hugging Face/本地模型", "百炼平台API", "M3E-Large模型"])


# 函数：使用Hugging Face模型生成嵌入
@st.cache_resource
def load_hf_model(model_name, model_path=None):
    try:
        from sentence_transformers import SentenceTransformer
        if model_path and os.path.exists(model_path):
            return SentenceTransformer(model_path)
        else:
            return SentenceTransformer(model_name)
    except ImportError:
        st.error("请安装sentence-transformers库: `pip install sentence-transformers`")
        return None
    except Exception as e:
        st.error(f"加载模型时出错: {str(e)}")
        return None


def get_hf_embeddings(model, texts):
    return model.encode(texts)


# 函数：使用百炼平台API生成嵌入
def get_bailian_embeddings(texts, api_key, endpoint):
    # 这里是示例代码，实际使用时需要替换为百炼平台的实际API
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


# 函数：使用M3E-Large模型生成嵌入
def get_m3e_embeddings(texts, use_local=False, model_path=None):
    try:
        from sentence_transformers import SentenceTransformer

        if use_local and model_path:
            if not os.path.exists(model_path):
                st.error(f"本地模型路径不存在: {model_path}")
                return None
            model = SentenceTransformer(model_path)
        else:
            # 使用在线M3E-Large模型
            model = SentenceTransformer("moka-ai/m3e-large")

        return model.encode(texts)
    except Exception as e:
        st.error(f"M3E模型加载失败: {str(e)}")
        return None


# Hugging Face/本地模型选项卡
with tab1:
    st.header("使用Hugging Face模型或本地模型")

    # 模型选择方式
    model_source = st.radio(
        "选择模型来源",
        ["Hugging Face Hub", "本地模型"],
        key="model_source"
    )

    if model_source == "Hugging Face Hub":
        # Hugging Face模型选择
        hf_model_name = st.selectbox(
            "选择Hugging Face模型",
            ["all-MiniLM-L6-v2", "paraphrase-multilingual-MiniLM-L12-v2", "all-mpnet-base-v2"],
            key="hf_model"
        )
        model_path = None
    else:
        # 本地模型路径输入
        model_path = st.text_input(
            "输入本地模型路径",
            placeholder="例如: /path/to/your/model",
            key="local_model_path"
        )
        hf_model_name = "local-model"

    # 输入文本
    hf_text = st.text_area("输入文本", "这是一个示例文本，用于生成嵌入向量。", key="hf_text")

    if st.button("生成嵌入", key="hf_button"):
        if model_source == "本地模型" and not model_path:
            st.error("请输入本地模型路径")
        else:
            with st.spinner("加载模型并生成嵌入..."):
                model = load_hf_model(hf_model_name, model_path)
                if model:
                    embeddings = get_hf_embeddings(model, [hf_text])
                    st.success("嵌入生成成功！")

                    # 显示嵌入向量信息
                    st.subheader("嵌入向量信息")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("向量维度", len(embeddings[0]))
                    with col2:
                        st.metric("模型名称", hf_model_name if model_source == "Hugging Face Hub" else "本地模型")
                    with col3:
                        st.metric("模型路径", model_path if model_path else "Hugging Face Hub")

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

# M3E-Large模型选项卡
with tab3:
    st.header("M3E-Large模型")

    # M3E模型选择方式
    m3e_source = st.radio(
        "选择M3E模型来源",
        ["在线模型", "本地模型"],
        key="m3e_source"
    )

    m3e_model_path = None
    if m3e_source == "本地模型":
        m3e_model_path = st.text_input(
            "输入M3E本地模型路径",
            placeholder="例如: /path/to/m3e-large",
            key="m3e_local_path"
        )

    # 输入文本
    m3e_text = st.text_area("输入文本", "这是一个示例文本，用于生成嵌入向量。", key="m3e_text")

    if st.button("生成嵌入", key="m3e_button"):
        if m3e_source == "本地模型" and not m3e_model_path:
            st.error("请输入M3E本地模型路径")
        else:
            with st.spinner("加载M3E模型并生成嵌入..."):
                use_local = m3e_source == "本地模型"
                embeddings = get_m3e_embeddings([m3e_text], use_local, m3e_model_path)

                if embeddings is not None:
                    st.success("M3E嵌入生成成功！")

                    # 显示嵌入向量信息
                    st.subheader("嵌入向量信息")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("向量维度", len(embeddings[0]))
                    with col2:
                        st.metric("模型名称", "M3E-Large")
                    with col3:
                        source_type = "本地模型" if use_local else "在线模型"
                        st.metric("模型来源", source_type)

                    # 显示部分向量值
                    st.subheader("部分向量值（前10个维度）")
                    st.write(embeddings[0][:10])

                    # 可视化
                    st.subheader("向量可视化")
                    st.line_chart(embeddings[0][:50])

# 比较选项卡
st.divider()
st.header("模型比较")

compare_text = st.text_area("输入比较文本", "这是一个用于比较不同模型的示例文本。", key="compare_text")

if st.button("比较所有方法", key="compare_btn"):
    if not compare_text:
        st.error("请输入比较文本")
    else:
        with st.spinner("正在比较所有模型..."):
            results = {}

            # 获取Hugging Face/本地模型嵌入
            if 'hf_model' in st.session_state and 'model_source' in st.session_state:
                model_source = st.session_state.model_source
                if model_source == "Hugging Face Hub":
                    model = load_hf_model(st.session_state.hf_model)
                else:
                    model_path = st.session_state.get('local_model_path', '')
                    if model_path and os.path.exists(model_path):
                        model = load_hf_model("local-model", model_path)
                    else:
                        model = None

                if model:
                    hf_embedding = get_hf_embeddings(model, [compare_text])[0]
                    results["Hugging Face/本地模型"] = hf_embedding

            # 获取百炼平台嵌入（模拟）
            bailian_embedding = get_bailian_embeddings([compare_text], "demo_key", "demo_endpoint")[0]
            results["百炼平台API"] = bailian_embedding

            # 获取M3E嵌入
            m3e_source = st.session_state.get('m3e_source', '在线模型')
            m3e_path = st.session_state.get('m3e_local_path', '')
            use_local = m3e_source == "本地模型"

            m3e_embeddings = get_m3e_embeddings([compare_text], use_local, m3e_path if use_local else None)
            if m3e_embeddings is not None:
                results["M3E-Large"] = m3e_embeddings[0]

            if len(results) < 2:
                st.warning("至少需要两种模型才能进行比较")
            else:
                # 计算相似度矩阵
                from numpy import dot
                from numpy.linalg import norm

                model_names = list(results.keys())
                embeddings_list = list(results.values())

                # 创建相似度矩阵
                similarity_matrix = np.zeros((len(model_names), len(model_names)))

                for i in range(len(model_names)):
                    for j in range(len(model_names)):
                        if i == j:
                            similarity_matrix[i][j] = 1.0
                        else:
                            # 调整到相同长度
                            min_len = min(len(embeddings_list[i]), len(embeddings_list[j]))
                            vec1 = embeddings_list[i][:min_len]
                            vec2 = embeddings_list[j][:min_len]
                            cosine_sim = dot(vec1, vec2) / (norm(vec1) * norm(vec2))
                            similarity_matrix[i][j] = cosine_sim

                # 显示相似度矩阵
                st.subheader("模型间余弦相似度矩阵")
                similarity_df = pd.DataFrame(
                    similarity_matrix,
                    index=model_names,
                    columns=model_names
                )
                st.dataframe(similarity_df.style.format("{:.4f}").background_gradient(cmap="Blues"))

                # 显示向量对比图
                st.subheader("向量值对比（前50个维度）")
                comparison_data = {}
                for name, embedding in results.items():
                    comparison_data[name] = embedding[:50]
                st.line_chart(comparison_data)

# 侧边栏信息
with st.sidebar:
    st.header("关于")
    st.markdown("""
    这个应用演示了三种生成文本嵌入的方法：

    1. **Hugging Face/本地模型**：使用sentence-transformers库
    2. **百炼平台API**：通过HTTP请求调用百炼平台的embedding服务
    3. **M3E-Large模型**：支持本地部署和在线版本

    M3E-Large模型信息：
    - 支持中文文本嵌入
    - 向量维度：1024
    - 在中文文本任务上表现优异
    """)

    st.divider()
    st.markdown("**注意**：")
    st.markdown("- 百炼平台API调用是模拟的")
    st.markdown("- 使用本地模型需要先下载模型到本地")
    st.markdown("- M3E在线模型需要网络连接")