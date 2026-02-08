import chromadb
from chromadb.config import Settings
import os
import sys

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

# 获取集合
collection = chroma_client.get_collection(
    name="artifact_embeddings",
    embedding_function=None
)

print("=" * 80)
print("测试1: get() 不带任何参数（默认返回所有字段）")
print("=" * 80)
result1 = collection.get()
print(f"返回的键: {result1.keys()}")
print(f"ids数量: {len(result1.get('ids', []))}")
print(f"documents数量: {len(result1.get('documents', []))}")
print(f"metadatas数量: {len(result1.get('metadatas', []))}")
print(f"embeddings类型: {type(result1.get('embeddings'))}")
print(f"embeddings值: {result1.get('embeddings')}")
print()

print("=" * 80)
print("测试2: get(include=['documents']) 只获取documents")
print("=" * 80)
result2 = collection.get(include=["documents"])
print(f"返回的键: {result2.keys()}")
print(f"ids数量: {len(result2.get('ids', []))}")
print(f"documents数量: {len(result2.get('documents', []))}")
print(f"metadatas数量: {len(result2.get('metadatas', []))}")
print(f"embeddings类型: {type(result2.get('embeddings'))}")
print(f"embeddings值: {result2.get('embeddings')}")
print()

print("=" * 80)
print("测试3: get(include=['ids', 'documents']) 只获取ids和documents")
print("=" * 80)
result3 = collection.get(include=["ids", "documents"])
print(f"返回的键: {result3.keys()}")
print(f"ids数量: {len(result3.get('ids', []))}")
print(f"documents数量: {len(result3.get('documents', []))}")
print(f"metadatas数量: {len(result3.get('metadatas', []))}")
print(f"embeddings类型: {type(result3.get('embeddings'))}")
print(f"embeddings值: {result3.get('embeddings')}")
print()

print("=" * 80)
print("测试4: get(include=['documents', 'metadatas']) 获取documents和metadatas")
print("=" * 80)
result4 = collection.get(include=["documents", "metadatas"])
print(f"返回的键: {result4.keys()}")
print(f"ids数量: {len(result4.get('ids', []))}")
print(f"documents数量: {len(result4.get('documents', []))}")
print(f"metadatas数量: {len(result4.get('metadatas', []))}")
print(f"embeddings类型: {type(result4.get('embeddings'))}")
print(f"embeddings值: {result4.get('embeddings')}")
print()

print("=" * 80)
print("测试5: get(include=['embeddings']) 只获取embeddings（测试用）")
print("=" * 80)
result5 = collection.get(include=["embeddings"])
print(f"返回的键: {result5.keys()}")
print(f"ids数量: {len(result5.get('ids', []))}")
print(f"documents数量: {len(result5.get('documents', []))}")
print(f"metadatas数量: {len(result5.get('metadatas', []))}")
print(f"embeddings类型: {type(result5.get('embeddings'))}")
if result5.get('embeddings'):
    print(f"embeddings数量: {len(result5.get('embeddings'))}")
    print(f"第一个embedding的维度: {len(result5['embeddings'][0])}")
    print(f"第一个embedding的前5个值: {result5['embeddings'][0][:5]}")
print()

print("=" * 80)
print("测试6: get(include=['ids']) 只获取ids")
print("=" * 80)
result6 = collection.get(include=["ids"])
print(f"返回的键: {result6.keys()}")
print(f"ids数量: {len(result6.get('ids', []))}")
print(f"documents数量: {len(result6.get('documents', []))}")
print(f"metadatas数量: {len(result6.get('metadatas', []))}")
print(f"embeddings类型: {type(result6.get('embeddings'))}")
print(f"embeddings值: {result6.get('embeddings')}")
print()

print("=" * 80)
print("结论:")
print("=" * 80)
print("1. get() 不带参数会返回所有字段（包括embeddings）")
print("2. get(include=['documents']) 只返回documents和ids（ids总是返回）")
print("3. get(include=['ids', 'documents']) 只返回ids和documents")
print("4. get(include=['documents', 'metadatas']) 只返回ids、documents和metadatas")
print("5. get(include=['embeddings']) 只返回ids和embeddings")
print("6. get(include=['ids']) 只返回ids")
print()
print("建议: 为了避免输出大量向量数据，应该使用:")
print("  - get(include=['documents']) 只获取文档数量")
print("  - get(include=['documents', 'metadatas']) 获取文档和元数据")
print("  - get(include=['ids']) 只获取ID列表")
