import json
import os
import traceback
import argparse
from openai import OpenAI

# 解析命令行参数
def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="向量数据库创建工具")
    parser.add_argument(
        "--dimension",
        type=int,
        default=1024,
        help="向量维度，默认值为1024"
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default="test.json",
        help="输入文件路径，默认值为test.json"
    )
    return parser.parse_args()

# 读取输入文件
def read_input_file(file_path):
    """读取输入文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            paragraphs = json.load(f)
        print(f"成功读取{file_path}，共包含 {len(paragraphs)} 个自然段")
        return paragraphs
    except Exception as e:
        print(f"读取{file_path}失败: {e}")
        traceback.print_exc()
        exit(1)

# 配置Embedding API
client = OpenAI(
    base_url="http://localhost:5000/v1",
    api_key="sk-ccahwXzZsrbLaXIidBQsnv8FVIbk8Y1BjgUdnFiHjFiuGSW3"
)

# 延迟导入ChromaDB，以便更好地隔离问题
def init_chroma():
    """初始化ChromaDB客户端和集合"""
    try:
        import chromadb
        from chromadb.config import Settings
        
        print("正在导入ChromaDB...")
        print(f"ChromaDB版本: {chromadb.__version__}")
        
        # 创建Chroma客户端
        chroma_client = chromadb.PersistentClient(
            path="./chroma_data",
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        print("Chroma客户端创建成功")
        
        # 创建或获取集合
        # 使用预计算的向量
        collection = chroma_client.get_or_create_collection(
            name="test_collection",
            metadata={
                "description": "测试向量集合",
                "use_precomputed_embeddings": "true"
            }
        )
        print("Chroma集合创建成功")
        
        print("ChromaDB初始化成功")
        return chroma_client, collection
    except Exception as e:
        print(f"ChromaDB初始化失败: {e}")
        traceback.print_exc()
        return None, None

# 处理向量维度
def process_embedding(embedding, target_dimension):
    """处理向量维度，确保符合目标维度"""
    current_dimension = len(embedding)
    
    if current_dimension == target_dimension:
        print(f"向量维度 {current_dimension} 符合要求")
        return embedding
    elif current_dimension > target_dimension:
        # 截断向量到目标维度
        processed_embedding = embedding[:target_dimension]
        print(f"向量维度 {current_dimension} 大于目标维度 {target_dimension}，已截断")
        return processed_embedding
    else:
        # 填充向量到目标维度（使用0填充）
        processed_embedding = embedding + [0.0] * (target_dimension - current_dimension)
        print(f"向量维度 {current_dimension} 小于目标维度 {target_dimension}，已填充")
        return processed_embedding

# 主函数
def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    target_dimension = args.dimension
    input_file = args.input_file
    
    print(f"\n=== 向量数据库创建工具 ===")
    print(f"目标向量维度: {target_dimension}")
    print(f"输入文件: {input_file}")
    
    # 读取输入文件
    paragraphs = read_input_file(input_file)
    
    # 初始化ChromaDB
    print("\n开始初始化ChromaDB...")
    chroma_client, collection = init_chroma()
    if not chroma_client or not collection:
        print("无法初始化ChromaDB，程序退出")
        exit(1)
    
    # 处理每个自然段
    print(f"\n开始处理 {len(paragraphs)} 个自然段...")
    try:
        for i, paragraph in enumerate(paragraphs):
            print(f"\n处理第 {i+1} 个自然段:")
            print(f"文本: {paragraph[:100]}..." if len(paragraph) > 100 else f"文本: {paragraph}")
            
            # 调用Embedding API获取向量
            print("正在生成向量...")
            response = client.embeddings.create(
                model="Qwen3-Embedding-4B",
                input=paragraph,
                encoding_format="float"
            )
            
            # 获取向量
            embedding = response.data[0].embedding
            print(f"原始向量维度: {len(embedding)}")
            
            # 处理向量维度
            processed_embedding = process_embedding(embedding, target_dimension)
            
            # 存储到ChromaDB
            print("正在存储到ChromaDB...")
            # 使用正确的参数顺序
            collection.add(
                ids=[f"id_{i}"],
                embeddings=[processed_embedding],
                documents=[paragraph]
            )
            
            print(f"成功存储第 {i+1} 个自然段")

        print("\nAll paragraphs processed and stored successfully!")
        
        # 验证存储结果
        print("\n正在验证存储结果...")
        count = collection.count()
        print(f"Collection contains {count} items")
        
        # 显示存储的数据
        print(f"\nStored data:")
        results = collection.get()
        for id, document in zip(results['ids'], results['documents']):
            print(f"ID: {id}")
            print(f"Document: {document[:50]}..." if len(document) > 50 else f"Document: {document}")
            print()
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()