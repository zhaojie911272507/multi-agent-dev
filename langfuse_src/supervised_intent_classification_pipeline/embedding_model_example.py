import pathlib
import warnings
warnings.filterwarnings("ignore")

print(pathlib.Path(__file__).absolute())
# Select embedding model
from sentence_transformers import SentenceTransformer
embedding_model = SentenceTransformer("/Users/zhaojie/project/langgraphtest0725/model_files/embeddingmodel/models--sentence-transformers--all-MiniLM-L6-v2")
print(embedding_model.encode("你好哇 先生"))





