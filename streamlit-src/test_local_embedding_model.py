import streamlit as st
import numpy as np
from pathlib import Path

# 页面设置
st.set_page_config(
    page_title="本地Embedding模型",
    page_icon="📁",
    layout="wide"
)

st.title("📁 使用本地Embedding模型")


# 函数：加载本地模型
@st.cache_resource
def load_local_model(model_path):
    try:
        from sentence_transformers import SentenceTransformer
        # 检查模型路径是否存在
        if not Path(model_path).exists():
            st.error(f"模型路径不存在: {model_path}")
            return None
        return SentenceTransformer(model_path)
    except ImportError:
        st.error("请安装sentence-transformers库: `pip install sentence-transformers`")
        return None
    except Exception as e:
        st.error(f"加载模型时出错: {str(e)}")
        return None


# 侧边栏 - 模型选择
st.sidebar.header("模型配置")

model_option = st.sidebar.radio(
    "选择模型来源",
    ["默认Hugging Face模型", "本地模型路径"]
)

if model_option == "默认Hugging Face模型":
    model_name = st.sidebar.selectbox(
        "选择预训练模型",
        ["all-MiniLM-L6-v2", "paraphrase-multilingual-MiniLM-L12-v2", "all-mpnet-base-v2"]
    )
else:
    model_path = st.sidebar.text_input(
        "本地模型路径",
        placeholder=r"/Users/model/all-mpnet-base-v2",
        help="请输入本地模型文件夹的完整路径"
    )
    model_name = model_path

# 输入文本
text_input = st.text_area(
    "输入文本",
    "这是一个示例文本，用于测试本地embedding模型。",
    height=100
)

if st.button("生成嵌入向量"):
    if not text_input.strip():
        st.warning("请输入文本")
    else:
        with st.spinner("加载模型并生成嵌入..."):
            model = load_local_model(model_name)

            if model:
                # 生成嵌入
                embeddings = model.encode([text_input])

                st.success("嵌入生成成功！")

                # 显示模型信息
                st.subheader("模型信息")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("向量维度", len(embeddings[0]))
                with col2:
                    st.metric("模型名称", getattr(model, 'model_name', '本地模型'))
                with col3:
                    st.metric("模型路径", model_name if model_option == "本地模型路径" else "Hugging Face")

                # 显示部分向量值
                st.subheader("嵌入向量（前20个维度）")
                st.write(embeddings[0][:20])

                # 可视化
                st.subheader("向量可视化")
                st.line_chart(embeddings[0][:50])

                # 显示模型详细信息
                with st.expander("查看模型详细信息"):
                    st.json({
                        "max_seq_length": model.max_seq_length,
                        "embedding_dimension": model.get_sentence_embedding_dimension(),
                        "model_path": model_name
                    })

# 批量处理示例
st.divider()
st.subheader("批量文本处理")

batch_texts = st.text_area(
    "批量文本（每行一个文本）",
    "这是第一个文本。\n这是第二个文本，稍长一些。\n第三个文本用于测试。",
    height=150,
    help="每行输入一个文本，将批量生成嵌入向量"
)

if st.button("批量生成嵌入"):
    texts = [text.strip() for text in batch_texts.split('\n') if text.strip()]

    if not texts:
        st.warning("请输入至少一个文本")
    else:
        with st.spinner(f"处理 {len(texts)} 个文本..."):
            model = load_local_model(model_name)
            if model:
                embeddings = model.encode(texts)

                st.success(f"成功处理 {len(texts)} 个文本")

                # 显示每个文本的嵌入摘要
                for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                    with st.expander(f"文本 {i + 1}: {text[:50]}..."):
                        st.metric("向量维度", len(embedding))
                        st.write("前10个维度值:", embedding[:10].round(6))

# 模型管理部分
st.sidebar.divider()
st.sidebar.header("模型管理")

if st.sidebar.button("清除模型缓存"):
    load_local_model.clear()
    st.sidebar.success("模型缓存已清除")

# 使用说明
with st.sidebar.expander("使用说明"):
    st.markdown("""
    ### 如何使用本地模型：
    1. 下载或训练SentenceTransformer模型
    2. 将模型保存到本地目录
    3. 在侧边栏选择"本地模型路径"
    4. 输入模型的完整路径

    ### 保存本地模型示例：
    ```python
    from sentence_transformers import SentenceTransformer

    # 下载模型
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # 保存到本地
    model.save('/path/to/your/local/model')
    ```

    ### 支持的本地格式：
    - SentenceTransformers保存的模型文件夹
    - HuggingFace Transformers模型
    - 自定义训练的SentenceTransformer模型
    """)