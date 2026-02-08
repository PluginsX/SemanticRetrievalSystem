import chromadb
from chromadb.config import Settings
import os

# 设置环境变量禁用telemetry和embedding模型
os.environ['CHROMA_ANONYMIZED_TELEMETRY'] = 'False'
os.environ['CHROMA_EMBEDDING_SERVICE'] = 'none'
os.environ['CHROMA_DISABLE_EMBEDDINGS'] = 'True'
os.environ['CHROMA_NO_EMBEDDINGS'] = 'True'

# 初始化ChromaDB客户端
chroma_client = chromadb.PersistentClient(
    path="./data/chroma",
    settings=Settings(anonymized_telemetry=False)
)

# 列出所有集合
collections = chroma_client.list_collections()
print("所有集合:")
for col in collections:
    print(f"  - {col.name}")
