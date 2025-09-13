from huggingface_hub import snapshot_download

# 下载模型到指定目录
model_path = snapshot_download(
    repo_id="moka-ai/m3e-large",  # 模型名称
    local_dir="../../model_files/embeddingmodel/m3e-large",                   # 本地保存路径
    local_dir_use_symlinks=False,                      # 避免符号链接（适合Windows）
    revision="main"                                    # 默认分支
)
print(f"模型已下载到：{model_path}")


# from sentence_transformers import SentenceTransformer
#
# # 下载模型
# model = SentenceTransformer('all-MiniLM-L6-v2')
#
# # 保存到本地
# model.save('/path/to/your/local/model')
# 当你调用 model.save('/path/to/your/local/model') 时，模型会保存到你指定的路径，但缓存目录（.cache/huggingface/hub）中的副本不会被删除。